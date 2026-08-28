# -*- coding: utf-8 -*-
"""
Шаг 7б. Отбор финального ядра.

Две задачи:

1. Схлопнуть перестановки слов. Вордстат считает «ремонт квартир под ключ»
   и «под ключ ремонт квартир» одной фразой: фразовая частотность у них
   совпадает, различается только точная. Оставляем вариант с наибольшей
   точной — это естественный порядок слов, остальное дубли.

2. Отобрать в ядро по московской фразовой, с лимитом на итоговый объём.
"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')

LIMIT_KOM = int(os.environ.get('LIMIT_KOM', '1500'))
LIMIT_BLOG = int(os.environ.get('LIMIT_BLOG', '500'))
MIN_QUOTED = int(os.environ.get('MIN_QUOTED', '3'))


# Окончания режем от длинных к коротким, иначе «квартирами» станет «квартирам»
ENDINGS = tuple(sorted({
    'иями', 'ыми', 'ими', 'ями', 'ами', 'ого', 'его', 'ому', 'ему',
    'ых', 'их', 'ая', 'яя', 'ое', 'ее', 'ые', 'ие', 'ей', 'ой', 'ый', 'ий',
    'ов', 'ев', 'ах', 'ях', 'ам', 'ям', 'ом', 'ем', 'ую', 'юю',
    'ия', 'ию', 'ии', 'ье', 'ья', 'ью', 'ех', 'ух',
    'а', 'я', 'ы', 'и', 'е', 'о', 'у', 'ю', 'ь', 'й',
}, key=len, reverse=True))

# Ценовой интент — коммерция, даже если запрос выглядит вопросом
CENA = re.compile(r'сколько\s+стоит|\bцен[аыу]?\b|\bцены\b|стоимост|\bпрайс|'
                  r'расц[ен]|\bсмет[аыу]?\b|за\s+м2|за\s+кв\w*\s*м|под\s+ключ\s+цен', re.I)

STOP = {'и', 'в', 'на', 'под', 'для', 'с', 'от', 'по', 'к', 'у', 'о', 'из'}


def stem(w):
    if len(w) <= 4:
        return w
    for e in ENDINGS:
        if w.endswith(e) and len(w) - len(e) >= 4:
            return w[:-len(e)]
    return w


def key_of(phrase):
    """Ключ перестановки: мультимножество основ слов без стоп-слов.

    Вордстат в кавычках не различает ни порядок слов, ни словоформу:
    «ремонт квартир», «ремонт квартиры» и «ремонты квартир» — одна фраза
    с одной и той же фразовой частотностью. Группируем по основам.
    """
    words = re.findall(r'[а-яёa-z0-9]+', phrase.lower())
    words = [stem(w) for w in words if w not in STOP]
    return tuple(sorted(words))


def collapse(ws, meta):
    """Схлопывает перестановки, возвращает {фраза: данные} и число схлопнутых."""
    groups = collections.defaultdict(list)
    for phrase, v in ws.items():
        if v.get('quoted', 0) < MIN_QUOTED:
            continue
        groups[key_of(phrase)].append(phrase)

    out, dropped = {}, 0
    for k, variants in groups.items():
        if len(variants) == 1:
            best = variants[0]
        else:
            best = max(variants, key=lambda p: (ws[p].get('overal', 0), -len(p)))
            dropped += len(variants) - 1
        out[best] = dict(ws[best])
        m = meta.get(best, {})
        out[best]['napravlenie'] = m.get('napravlenie', '')
        out[best]['src'] = m.get('src', [])
        out[best]['varianty'] = [v for v in variants if v != best][:5]
    return out, dropped


def main():
    prof = json.load(open(os.path.join(MAT, 'ядро_профиль.json'), encoding='utf-8'))

    # частотность снята двумя проходами; объединяем, чтобы перекладывание фраз
    # между коммерцией и блогом не требовало новых запросов к API
    ALL = {}
    for f in ('частотность_kom_wordstat.json', 'частотность_blog_wordstat.json'):
        p = os.path.join(MAT, f)
        if os.path.exists(p):
            ALL.update(json.load(open(p, encoding='utf-8')))
    print('частотность есть по %d фразам' % len(ALL))

    ws_kom = {w: ALL[w] for w in prof if w in ALL}
    kom, dropped = collapse(ws_kom, prof)
    print('коммерческие: снято %d, после схлопывания перестановок и словоформ %d '
          '(убрано дублей %d)' % (len(ws_kom), len(kom), dropped))

    info_path = os.path.join(MAT, 'ядро_инфо_профиль.json')
    blog = {}
    if os.path.exists(info_path):
        info = json.load(open(info_path, encoding='utf-8'))
        ws_blog = {w: ALL[w] for w in info if w in ALL}
        blog, dropped_b = collapse(ws_blog, info)
        print('блог: с частотностью %d, после схлопывания %d (убрано дублей %d)'
              % (len(ws_blog), len(blog), dropped_b))

        # ценовые запросы возвращаем в коммерцию: «сколько стоит ремонт» —
        # это выбор подрядчика, а не чтение статьи
        moved = 0
        for w in list(blog):
            if CENA.search(w):
                v = blog.pop(w)
                v['napravlenie'] = v.get('napravlenie') or 'Ремонт квартир'
                kom.setdefault(w, v)
                moved += 1
        print('перенесено из блога в коммерцию по ценовому интенту: %d' % moved)
    else:
        print('блог: частотность ещё не снята')

    top_kom = dict(sorted(kom.items(), key=lambda kv: -kv[1]['quoted'])[:LIMIT_KOM])
    print('\nв коммерческое ядро берём: %d (лимит %d)' % (len(top_kom), LIMIT_KOM))

    blog = {w: v for w, v in blog.items() if w not in top_kom}
    top_blog = dict(sorted(blog.items(), key=lambda kv: -kv[1]['quoted'])[:LIMIT_BLOG])
    if top_blog:
        print('в блог берём: %d (лимит %d)' % (len(top_blog), LIMIT_BLOG))

    json.dump(top_kom, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(top_blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('\nИТОГО в ядре: %d коммерческих + %d в блоге = %d (лимит проекта 2000)'
          % (len(top_kom), len(top_blog), len(top_kom) + len(top_blog)))

    by_dir = collections.Counter(v.get('napravlenie', '—') for v in top_kom.values())
    print('\n=== коммерческое ядро по направлениям ===')
    for d, n in by_dir.most_common():
        s = sum(v['quoted'] for v in top_kom.values() if v.get('napravlenie') == d)
        print('  %-20s фраз %-5d суммарная фразовая %d' % (d, n, s))

    print('\n=== топ-25 коммерческих ===')
    for w, v in sorted(top_kom.items(), key=lambda kv: -kv[1]['quoted'])[:25]:
        print('  %-52s "Ч"=%-6d %s' % (w[:52], v['quoted'], v.get('napravlenie', '')))

    if top_blog:
        print('\n=== топ-15 в блог ===')
        for w, v in sorted(top_blog.items(), key=lambda kv: -kv[1]['quoted'])[:15]:
            print('  %-58s "Ч"=%d' % (w[:58], v['quoted']))


main()

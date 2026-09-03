# -*- coding: utf-8 -*-
"""
Шаг 17. Семантика под новые услуги из замечаний клиента.

Клиент предложил добавить кондиционирование, вентиляцию, умный дом,
отопление и декоративную штукатурку, а также перегруппировать услуги
в инженерные системы, отделочные и черновые работы.

Спрос по всем направлениям проверен прямым запросом к Вордстату
и подтверждён коммерциализацией. Здесь собираются сами фразы.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin  # noqa: E402
arsenkin.OUT_DIR = os.path.join(MAT, 'арсенкин')
MOSCOW = 213

NOVYE = {
    'Декоративная штукатурка': (
        r'декоративн\w*\s+штукатурк|штукатурк\w*\s+декоративн|венецианск\w*\s+штукатурк|'
        r'фактурн\w*\s+штукатурк|микроцемент',
        ['декоративная штукатурка', 'декоративная штукатурка стен',
         'нанесение декоративной штукатурки', 'декоративная штукатурка цена за м2',
         'венецианская штукатурка', 'фактурная штукатурка стен',
         'декоративная штукатурка под бетон', 'декоративная штукатурка в квартире']),
    'Установка кондиционеров': (
        r'кондиционер|сплит[\s-]?систем',
        ['установка кондиционера', 'монтаж кондиционера', 'установка кондиционера в квартире',
         'установка сплит системы', 'монтаж сплит системы', 'установка кондиционера цена',
         'установка кондиционера под ключ']),
    'Вентиляция': (
        r'вентиляц|приточн\w*\s+установк|рекуператор',
        ['монтаж вентиляции', 'установка вентиляции в квартире', 'вентиляция в квартире',
         'приточная вентиляция в квартире', 'монтаж приточной вентиляции',
         'вентиляция под ключ']),
    'Умный дом': (
        r'умн\w*\s+дом|умн\w*\s+квартир',
        ['умный дом', 'установка умного дома', 'монтаж умного дома', 'умный дом под ключ',
         'система умный дом', 'умный дом в квартире цена', 'монтаж системы умный дом']),
    'Отопление': (
        r'отоплен|радиатор|батаре\w*\s+отоплен|т[её]пл\w*\s+пол\w*\s+водян',
        ['монтаж отопления', 'замена радиаторов отопления', 'установка радиаторов',
         'система отопления в квартире', 'монтаж системы отопления',
         'замена батарей отопления', 'установка батарей в квартире']),
    'Инженерные системы': (
        r'инженерн\w*\s+систем|инженерн\w*\s+сет|инженерн\w*\s+коммуникац',
        ['инженерные системы', 'монтаж инженерных систем',
         'инженерные системы в квартире', 'монтаж инженерных сетей',
         'инженерные коммуникации в квартире']),
}


def main():
    raw = json.load(open(os.path.join(MAT, 'ядро_сырое.json'), encoding='utf-8'))
    ws = json.load(open(os.path.join(MAT, 'частотность_kom_wordstat.json'), encoding='utf-8'))
    core = json.load(open(os.path.join(MAT, 'ядро_финал.json'), encoding='utf-8'))
    blog = json.load(open(os.path.join(MAT, 'ядро_финал_блог.json'), encoding='utf-8'))

    to_check = {}
    for page, (pat, manual) in NOVYE.items():
        rx = re.compile(pat, re.I)
        found = sorted((w for w in raw if rx.search(w)),
                       key=lambda w: -raw[w].get('wsk', 0))
        cand = [w for w in found[:80] if w not in ws]
        for w in cand + [m for m in manual if m not in ws]:
            to_check[w] = page
        print('%-28s в пуле %-4d на съём %d' % (page, len(found), len(cand) + len(manual)))

    todo = sorted(to_check)
    print('\nна съём частотности: %d' % len(todo))
    for i in range(0, len(todo), 250):
        chunk = todo[i:i + 250]
        print('  волна %d — %d фраз' % (i // 250 + 1, len(chunk)), flush=True)
        res = arsenkin.run('wordstat', {'queries': chunk, 'regions': [MOSCOW], 'type': 1,
                                        'ws': ['base', 'quoted', 'overal', 'exact']},
                           timeout=3600)
        data = res.get('result', {}).get('data', {}).get('result', {})
        for q, byreg in (data.items() if isinstance(data, dict) else []):
            v = byreg.get(str(MOSCOW), {}) if isinstance(byreg, dict) else {}
            ws[q] = {'base': v.get('base', 0), 'quoted': v.get('quoted', 0),
                     'overal': v.get('overal', 0), 'exact': v.get('exact', 0)}
        json.dump(ws, open(os.path.join(MAT, 'частотность_kom_wordstat.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)

    print('\n' + '=' * 70)
    added = 0
    for page in NOVYE:
        cands = [w for w, p in to_check.items() if p == page]
        live = sorted(((ws[w]['quoted'], w) for w in cands
                       if ws.get(w, {}).get('quoted', 0) >= 3 and w not in core), reverse=True)
        print('\n%s: живых фраз %d, спрос %d' % (page, len(live), sum(q for q, _ in live)))
        for q, w in live[:8]:
            print('    %-52s "Ч"=%d' % (w[:52], q))
        for q, w in live:
            v = dict(ws[w])
            v['napravlenie'] = 'Новые услуги'
            v['src'] = ['замечания клиента']
            v['varianty'] = []
            core[w] = v
            blog.pop(w, None)
            added += 1

    json.dump(core, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nдобавлено фраз: %d' % added)
    print('стало: коммерческих %d, блог %d' % (len(core), len(blog)))


main()

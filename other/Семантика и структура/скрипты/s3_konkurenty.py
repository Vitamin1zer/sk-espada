# -*- coding: utf-8 -*-
"""
Шаг 3. Кто реальные конкуренты sk-espada.ru.

Снимаем топ-10 Яндекса по Москве по 30 маркерам всех направлений,
считаем частоту попадания доменов и долю агрегаторов.
Списку конкурентов из брифа не верим — проверяем выдачей.
"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin
arsenkin.OUT_DIR = os.path.join(PROJ, 'материалы', 'арсенкин')

MARKERS = [
    # ремонт — пиллар и кластеры
    "ремонт квартир под ключ",
    "ремонт квартир москва",
    "ремонт квартиры в новостройке под ключ",
    "ремонт вторички",
    "капитальный ремонт квартиры",
    "косметический ремонт квартиры",
    "дизайнерский ремонт квартир",
    "ремонт однокомнатной квартиры",
    "ремонт двухкомнатной квартиры",
    "ремонт трехкомнатной квартиры",
    "ремонт квартиры студии",
    "ремонт квартир цена за м2",
    # дизайн
    "дизайн интерьера квартиры",
    "дизайн проект квартиры",
    "дизайн интерьера офиса",
    "дизайн проект дома",
    "дизайн интерьера коммерческих помещений",
    # приёмка
    "приемка квартиры в новостройке",
    "приемка квартиры без отделки",
    "приемка квартиры с отделкой",
    "приемщик квартир",
    # отдельные услуги
    "комплектация квартиры материалами",
    "перепланировка квартиры",
    "механизированная штукатурка",
    "отделка квартир под ключ",
    # доверие и прочее
    "ремонт квартир отзывы",
    "портфолио ремонта квартир",
    "строительная компания ремонт квартир москва",
    "ремонт квартир в жк",
    "сколько стоит ремонт квартиры",
]

# Агрегаторы ниши услуг — определено на шаге 0, по факту выдачи пополним
AGGREGATORS = {
    'avito.ru', 'profi.ru', 'uslugi.yandex.ru', 'youdo.com', 'yandex.ru',
    '2gis.ru', 'zoon.ru', 'yell.ru', 'blizko.ru', 'tiu.ru', 'flamp.ru',
    'otzovik.com', 'irecommend.ru', 'vk.com', 'ok.ru', 'dzen.ru', 'ya.ru',
    'ozon.ru', 'wildberries.ru', 'leroymerlin.ru', 'petrovich.ru',
    'ivan-remont.ru',  # уточним по факту
    'domclick.ru', 'cian.ru', 'm2.ru', 'novostroy-m.ru', 'realty.ya.ru',
    'youtube.com', 'rutube.ru', 'pikabu.ru', 'forumhouse.ru', 'mastergrad.com',
}


def domain_of(url):
    m = re.match(r'https?://([^/]+)', url or '')
    if not m:
        return ''
    d = m.group(1).lower()
    return d[4:] if d.startswith('www.') else d


def main():
    cache = os.path.join(arsenkin.OUT_DIR, 's3_top10.json')
    if os.path.exists(cache):
        print('беру из кэша: s3_top10.json')
        res = json.load(open(cache, encoding='utf-8'))
    else:
        print('снимаем топ-10 по %d маркерам, Яндекс, Москва' % len(MARKERS))
        res = arsenkin.run('check-top', {
            'queries': MARKERS,
            'se': [{'type': 1, 'region': 213}],
            'depth': 10,
            'is_snippet': 0,
            'noreask': 1,
        }, name='s3_top10', timeout=3600)

    # разбор результата: collect — список по запросам, внутри [[url, url, ...]]
    block = res['result']['result']
    queries = res['result']['request']['queries']
    collect = block['collect']

    def flatten(x):
        if isinstance(x, str):
            return [x]
        out = []
        for i in (x or []):
            out.extend(flatten(i))
        return out

    hits = collections.Counter()
    top3 = collections.Counter()
    agg_share = {}
    per_query = {}

    for qi, q in enumerate(queries):
        urls = flatten(collect[qi]) if qi < len(collect) else []
        doms = []
        for i, u in enumerate(urls[:10]):
            d = domain_of(u)
            if not d:
                continue
            doms.append(d)
            hits[d] += 1
            if i < 3:
                top3[d] += 1
        per_query[q] = doms
        if doms:
            agg_share[q] = sum(1 for d in doms if d in AGGREGATORS) / len(doms)

    json.dump({'per_query': per_query, 'hits': dict(hits), 'top3': dict(top3),
               'agg_share': agg_share},
              open(os.path.join(arsenkin.OUT_DIR, 's3_razbor.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('\nразобрано запросов: %d' % len(per_query))
    if not per_query:
        print('!! не удалось разобрать структуру, сырой ответ:')
        print(raw[:2000])
        return

    print('\n=== ТОП ДОМЕНОВ ПО ЧАСТОТЕ В ВЫДАЧЕ ===')
    print('%-34s %-8s %-8s %s' % ('домен', 'в топ-10', 'в топ-3', 'агрегатор'))
    for d, n in hits.most_common(30):
        print('%-34s %-8d %-8d %s' % (d, n, top3.get(d, 0), 'да' if d in AGGREGATORS else ''))

    vals = list(agg_share.values())
    print('\nсредняя доля агрегаторов в выдаче: %.0f%%' % (100 * sum(vals) / len(vals)))
    print('запросов, где агрегаторы держат половину и больше: %d из %d'
          % (sum(1 for v in vals if v >= 0.5), len(vals)))

    print('\nsk-espada.ru встречается в топ-10: %d раз' % hits.get('sk-espada.ru', 0))


main()

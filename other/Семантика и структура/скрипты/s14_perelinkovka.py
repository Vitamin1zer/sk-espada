# -*- coding: utf-8 -*-
"""
Шаг 14. План перелинковки.

Строит пары «откуда — куда — анкор». Анкором берётся маркер целевой страницы,
то есть самый частотный коммерческий запрос, по которому она обязана
ранжироваться. Ссылка с осмысленным анкором передаёт релевантность,
ссылка «подробнее» не передаёт ничего.

Типы связей:
  * пиллар в кластер и обратно — вертикаль раздела;
  * между соседними кластерами — горизонталь, по два ближайших по спросу;
  * блог в коммерцию — статья ведёт на страницу услуги, ради которой писалась;
  * коммерция в блог — страница услуги ведёт в свою рубрику блога;
  * услуги и страницы доверия в пиллар — сбор веса на главных страницах.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, HERE)
import ploskie_url as P  # noqa: E402

PILLARY = {'Ремонт квартир': '/remont-kvartir/',
           'Дизайн': '/design/',
           'Приёмка': '/priemka/'}


def build(meta, stat, marker, blog_rubrics, skip=None, adres=None):
    """meta: URL -> (название, раздел, старый URL, ...)
    stat: URL -> {'q': спрос, ...}
    marker: URL -> {'marker': фраза}
    blog_rubrics: папка блога -> (кластер, URL коммерческой страницы, спрос)
    """
    rows = []
    seen = set()
    skip = skip or set()
    # адреса берём из таблицы заказчика, у нас они только внутренние
    adres = adres or {}

    def A(u):
        return adres.get(u) or P.flat_url(u)

    def add(src, dst, anchor, kind, prio):
        # страницы, которые решено не создавать, из перелинковки исключаем
        if src in skip or dst in skip:
            return
        if not src or not dst or src == dst:
            return
        key = (src, dst)
        if key in seen:
            return
        seen.add(key)
        rows.append([A(src), A(dst), anchor, kind, prio])

    def anchor_of(url):
        m = (marker.get(url) or {}).get('marker')
        return m if m else (meta[url][0] if url in meta else url)

    # раздел -> дочерние страницы
    kids = collections.defaultdict(list)
    for url in meta:
        par = P.parent_nested(url)
        if par and par in meta:
            kids[par].append(url)

    # 1 и 2. Пиллар в кластер и обратно
    for pill in PILLARY.values():
        if pill not in meta:
            continue
        children = sorted(kids.get(pill, []),
                          key=lambda u: -stat.get(u, {}).get('q', 0))
        for ch in children:
            add(pill, ch, anchor_of(ch), 'Пиллар в кластер', 1)
            add(ch, pill, anchor_of(pill), 'Кластер в пиллар', 1)

    # 3. Между соседними кластерами: по два ближайших по спросу
    for pill, children in kids.items():
        ordered = sorted(children, key=lambda u: -stat.get(u, {}).get('q', 0))
        for i, ch in enumerate(ordered):
            for nb in ordered[i + 1:i + 3]:
                add(ch, nb, anchor_of(nb), 'Между соседями', 2)
                add(nb, ch, anchor_of(ch), 'Между соседями', 2)

    # 4 и 5. Блог и коммерция
    for papka, (klaster, com_url, q) in sorted(blog_rubrics.items(),
                                               key=lambda kv: -kv[1][2]):
        if not com_url or com_url not in meta or com_url in skip:
            continue
        rows.append([papka, A(com_url), anchor_of(com_url),
                     'Блог в коммерцию', 1])
        rows.append([A(com_url), papka,
                     'Статьи о том, %s' % klaster.lower(), 'Коммерция в блог', 3])

    # 6. Отдельные услуги в пиллар ремонта
    pill = '/remont-kvartir/'
    for url, m in meta.items():
        if m[1] == 'Услуги' and url in stat:
            add(url, pill, anchor_of(pill), 'Услуга в пиллар', 2)

    # 7. Портфолио и отзывы в пиллары, пиллары в портфолио
    for url in ('/portfolio/', '/otzyvy/'):
        if url not in meta:
            continue
        for pill in PILLARY.values():
            if pill in meta:
                add(url, pill, anchor_of(pill), 'Доверие в пиллар', 3)
                add(pill, url, meta[url][0], 'Пиллар в доверие', 3)

    return rows

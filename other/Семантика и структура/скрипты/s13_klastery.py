# -*- coding: utf-8 -*-
"""
Шаг 13. Разбор кластеризации и приёмка структуры.

Кластеризация снята по всему ядру, отдельно по коммерции и отдельно по блогу,
тип hard, порог 3, глубина топ-10 по Москве.

Приёмка: маркеры двух разных страниц не должны попасть в один кластер.
Если попали — выдача эти страницы не различает, и их придётся склеивать.
Это единственная объективная проверка того, что структура развязана.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, HERE)


def parse(path):
    """Возвращает {фраза: имя кластера} и {имя кластера: [фразы]}."""
    raw = json.load(open(path, encoding='utf-8'))
    cl = raw['result']['clustering']
    by_phrase, by_cluster = {}, {}
    for head, block in (cl.get('clustered') or {}).items():
        words = list((block.get('words') or {}).keys())
        by_cluster[head] = words
        for w in words:
            by_phrase[w] = head
    # «single» — фразы, не собравшиеся ни в один кластер. Это не корзина
    # остатков: каждая такая фраза сама по себе, и для приёмки структуры
    # это хороший признак — выдача различает её от всех прочих.
    lone = list((cl.get('single') or {}).keys())
    for w in lone:
        by_phrase[w] = ''
    return by_phrase, by_cluster, len(lone)


def main():
    out = {}
    for tag, label in [('kom', 'коммерция'), ('blog', 'блог')]:
        p = os.path.join(MAT, 'арсенкин', 's8_clusters_%s.json' % tag)
        if not os.path.exists(p):
            print('нет файла %s' % p)
            continue
        by_phrase, by_cluster, n_lone = parse(p)
        out[tag] = {'by_phrase': by_phrase, 'by_cluster': by_cluster}
        sizes = sorted((len(v) for v in by_cluster.values()), reverse=True)
        print('### %s: фраз %d, кластеров %d, некластеризовано %d'
              % (label, len(by_phrase), len(by_cluster), n_lone))
        if sizes:
            print('    крупнейшие кластеры: %s' % ', '.join(str(x) for x in sizes[:8]))
        print()

    json.dump(out, open(os.path.join(MAT, 'кластеры.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    # ---------- приёмка структуры ----------
    core = json.load(open(os.path.join(MAT, 'ядро_разложено.json'), encoding='utf-8'))
    comm_path = os.path.join(MAT, 'коммерциализация.json')
    comm = json.load(open(comm_path, encoding='utf-8')) if os.path.exists(comm_path) else {}

    # маркер страницы — самая частотная коммерческая фраза
    marker = {}
    for w, v in core.items():
        url = v.get('url')
        c = comm.get(w)
        if not (isinstance(c, (int, float)) and c >= 30):
            continue
        if url not in marker or v['quoted'] > marker[url][0]:
            marker[url] = (v['quoted'], w)
    for w, v in core.items():
        url = v.get('url')
        if url not in marker:
            marker[url] = (v['quoted'], w)

    by_phrase = out.get('kom', {}).get('by_phrase', {})
    kl_to_pages = collections.defaultdict(list)
    for url, (q, w) in marker.items():
        k = by_phrase.get(w, '')
        if k:
            kl_to_pages[k].append((url, w))

    collisions = {k: v for k, v in kl_to_pages.items() if len(v) > 1}
    total = len(marker)
    alone = sum(1 for url, (q, w) in marker.items() if not by_phrase.get(w))

    print('=' * 92)
    print('ПРИЁМКА СТРУКТУРЫ')
    print('=' * 92)
    print('страниц с маркером: %d' % total)
    print('маркеров, которые вообще не кластеризовались: %d — это хорошо, '
          'страница различима' % alone)
    print('кластеров, куда попало больше одного маркера: %d' % len(collisions))
    if collisions:
        print('\nСТРАНИЦЫ, КОТОРЫЕ ВЫДАЧА НЕ РАЗЛИЧАЕТ:')
        for k, pages in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
            print('\n  кластер «%s»' % k[:70])
            for url, w in pages:
                print('     %-40s маркер: %s' % (url, w[:44]))
    else:
        print('\nСтолкновений нет: маркеры всех страниц лежат в разных кластерах.')

    json.dump({k: v for k, v in collisions.items()},
              open(os.path.join(MAT, 'приёмка_столкновения.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump({u: {'marker': w, 'quoted': q, 'cluster': by_phrase.get(w, '')}
               for u, (q, w) in marker.items()},
              open(os.path.join(MAT, 'маркеры.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nсохранено: материалы/кластеры.json, маркеры.json, приёмка_столкновения.json')


main()

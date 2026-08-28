# -*- coding: utf-8 -*-
"""
Шаг 7г. Перенос низкокоммерческих запросов в блог.

Коммерциализация ниже 40 % означает, что в московской выдаче по фразе стоят
статьи и галереи, а не подрядчики. Продающая страница по такой фразе
проигрывает интенту, поэтому фраза уходит в блог и позже связывается
с коммерческой страницей перелинковкой.

Порог задан заказчиком. Фразы без данных о коммерциализации остаются
в коммерческом ядре: отсутствие проверки не повод их выбрасывать.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')

PORE = int(os.environ.get('PORE_KOM', '40'))


def main():
    kom = json.load(open(os.path.join(MAT, 'ядро_финал.json'), encoding='utf-8'))
    blog = json.load(open(os.path.join(MAT, 'ядро_финал_блог.json'), encoding='utf-8'))
    comm = json.load(open(os.path.join(MAT, 'коммерциализация.json'), encoding='utf-8'))

    print('на входе: коммерческих %d, в блоге %d' % (len(kom), len(blog)))
    have = sum(1 for w in kom if isinstance(comm.get(w), (int, float)))
    print('из коммерческих проверено на коммерциализацию: %d' % have)

    moved, no_data = 0, 0
    by_dir = collections.Counter()
    for w in list(kom):
        c = comm.get(w)
        if not isinstance(c, (int, float)):
            no_data += 1
            continue
        if c < PORE:
            v = kom.pop(w)
            v['iz_kommercii'] = True
            v['kommercializaciya'] = c
            blog[w] = v
            moved += 1
            by_dir[v.get('napravlenie', '—')] += 1

    print('\nперенесено в блог (коммерциализация ниже %d): %d' % (PORE, moved))
    print('осталось без данных о коммерциализации: %d — остаются в коммерции' % no_data)
    print('\n=== откуда ушли фразы ===')
    for d, n in by_dir.most_common():
        print('  %-24s %d' % (d, n))

    # подгонка под лимит проекта: коммерческое ядро не режем, режем хвост блога
    LIMIT = int(os.environ.get('LIMIT_VSEGO', '2000'))
    room = max(0, LIMIT - len(kom))
    if len(blog) > room:
        cut = len(blog) - room
        blog = dict(sorted(blog.items(), key=lambda kv: -kv[1].get('quoted', 0))[:room])
        print('\nблог урезан по лимиту проекта: убрано %d самых низкочастотных' % cut)

    json.dump(kom, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('\nстало: коммерческих %d, в блоге %d, всего %d (лимит %d)'
          % (len(kom), len(blog), len(kom) + len(blog), LIMIT))


main()

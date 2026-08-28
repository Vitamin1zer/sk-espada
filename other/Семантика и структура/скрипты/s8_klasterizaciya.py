# -*- coding: utf-8 -*-
"""
Шаг 8. Кластеризация по живой выдаче.

Кластеризуем ТОЛЬКО очищенное ядро с подтверждённой московской частотностью.
Кластеризация до чистки — прямая грабля: мусорные фразы образуют мусорные
кластеры и утягивают за собой решения по страницам.

Тип hard, порог 3: страницы должны быть развязаны жёстко, иначе поисковик
не различит их между собой.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin
arsenkin.OUT_DIR = os.path.join(PROJ, 'материалы', 'арсенкин')
MAT = os.path.join(PROJ, 'материалы')

MOSCOW = 213
GROUP = os.environ.get('GROUP', 'hard')
COUNT = int(os.environ.get('COUNT', '3'))
DEPTH = int(os.environ.get('DEPTH', '10'))
NAME = os.environ.get('NAME', 's8_clusters')
SRC = os.environ.get('SRC', 'ядро_финал.json')


def main():
    core = json.load(open(os.path.join(MAT, SRC), encoding='utf-8'))
    queries = list(core.keys())
    print('фраз на кластеризацию: %d (group=%s, count=%d, depth=%d)'
          % (len(queries), GROUP, COUNT, DEPTH))

    cached = arsenkin.load(NAME)
    if cached:
        print('беру из кэша: %s' % NAME)
        res = cached
    else:
        res = arsenkin.run('clustering', {
            'queries': queries,
            'group': GROUP, 'count': COUNT, 'main': True,
            'ws': ['base', 'quoted'],
            'se': 1, 'region': MOSCOW, 'depth': DEPTH,
        }, name=NAME, timeout=7200)

    r = res.get('result', {})
    print('ключи результата:', list(r.keys()) if isinstance(r, dict) else type(r))
    js = json.dumps(r, ensure_ascii=False)
    print('размер:', len(js))
    print(js[:1500])

    json.dump(r, open(os.path.join(MAT, 'кластеры_сырое_%s.json' % NAME), 'w',
                      encoding='utf-8'), ensure_ascii=False)


main()

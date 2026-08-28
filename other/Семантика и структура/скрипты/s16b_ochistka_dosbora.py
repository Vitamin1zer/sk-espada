# -*- coding: utf-8 -*-
"""
Шаг 16б. Приведение досбора к общим правилам ядра.

Досбор добавлял фразы напрямую, минуя схлопывание словоформ и порог
коммерциализации. Здесь они проходят те же проверки, что и остальное ядро,
иначе в коммерческой части окажутся перестановки вида «комната гардеробная»
и информационные запросы вида «размеры гардеробной».
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin  # noqa: E402
arsenkin.OUT_DIR = os.path.join(MAT, 'арсенкин')

MOSCOW = 213
PORE = int(os.environ.get('PORE_KOM', '30'))
LIMIT = int(os.environ.get('LIMIT_VSEGO', '2000'))


def load_collapse():
    src = open(os.path.join(HERE, 's7b_otbor.py'), encoding='utf-8').read()
    src = src.replace('\nmain()\n', '\n')
    ns = {'__file__': os.path.join(HERE, 's7b_otbor.py')}
    exec(compile(src, 's7b', 'exec'), ns)
    return ns['key_of']


def main():
    key_of = load_collapse()
    core = json.load(open(os.path.join(MAT, 'ядро_финал.json'), encoding='utf-8'))
    blog = json.load(open(os.path.join(MAT, 'ядро_финал_блог.json'), encoding='utf-8'))
    comm_path = os.path.join(MAT, 'коммерциализация.json')
    comm = json.load(open(comm_path, encoding='utf-8')) if os.path.exists(comm_path) else {}
    print('на входе: коммерческих %d, блог %d' % (len(core), len(blog)))

    # 1. схлопываем словоформы и перестановки внутри коммерческого ядра
    groups = collections.defaultdict(list)
    for w in core:
        groups[key_of(w)].append(w)
    dropped = 0
    for k, variants in groups.items():
        if len(variants) == 1:
            continue
        best = max(variants, key=lambda p: (core[p].get('overal', 0), -len(p)))
        for w in variants:
            if w != best:
                core.pop(w, None)
                dropped += 1
    print('схлопнуто дублей в коммерческом ядре: %d' % dropped)

    # 2. коммерциализация для фраз, которых ещё не проверяли
    todo = [w for w in core if not isinstance(comm.get(w), (int, float))]
    print('без данных о коммерциализации: %d' % len(todo))
    for i in range(0, len(todo), 200):
        chunk = todo[i:i + 200]
        print('  волна %d — %d фраз' % (i // 200 + 1, len(chunk)), flush=True)
        res = arsenkin.run('commerce', {'queries': chunk, 'se': 1, 'region': MOSCOW},
                           timeout=5400)
        stack = [res.get('result', {})]
        found = 0
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                q = cur.get('query') or cur.get('word') or cur.get('phrase')
                if q and isinstance(q, str):
                    for k in ('commerce', 'commercial', 'value', 'percent', 'com'):
                        if k in cur:
                            comm[q] = cur[k]
                            found += 1
                            break
                for v in cur.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                for v in cur:
                    if isinstance(v, (dict, list)):
                        stack.append(v)
        json.dump(comm, open(comm_path, 'w', encoding='utf-8'), ensure_ascii=False)
        print('   распознано %d, всего %d' % (found, len(comm)), flush=True)

    # 3. порог коммерциализации
    moved = 0
    for w in list(core):
        c = comm.get(w)
        if isinstance(c, (int, float)) and c < PORE:
            v = core.pop(w)
            v['iz_kommercii'] = True
            v['kommercializaciya'] = c
            blog[w] = v
            moved += 1
    print('\nперенесено в блог по порогу %d: %d' % (PORE, moved))

    # 4. лимит проекта
    room = max(0, LIMIT - len(core))
    if len(blog) > room:
        cut = len(blog) - room
        blog = dict(sorted(blog.items(), key=lambda kv: -kv[1].get('quoted', 0))[:room])
        print('из блога убрано по лимиту: %d' % cut)

    json.dump(core, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nстало: коммерческих %d, блог %d, всего %d'
          % (len(core), len(blog), len(core) + len(blog)))


main()

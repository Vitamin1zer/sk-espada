# -*- coding: utf-8 -*-
"""
Шаг 7в. Коммерциализация.

Проверяем, коммерческая ли выдача по фразе. Порог для услуг — 50 %,
принят на шаге 0. Приоритет страницы считается как сумма фразовой
частотности только по коммерческим фразам.
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin
arsenkin.OUT_DIR = os.path.join(PROJ, 'материалы', 'арсенкин')
MAT = os.path.join(PROJ, 'материалы')

MOSCOW = 213
CHUNK = int(os.environ.get('CHUNK', '200'))
SRC = os.environ.get('SRC', 'ядро_финал.json')
CACHE = os.path.join(MAT, 'коммерциализация.json')


def main():
    core = json.load(open(os.path.join(MAT, SRC), encoding='utf-8'))
    done = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    todo = [w for w in core if w not in done]
    print('фраз: %d, уже проверено: %d, осталось: %d' % (len(core), len(done), len(todo)))

    total = math.ceil(len(todo) / CHUNK)
    for i, chunk in enumerate(arsenkin.chunked(todo, CHUNK), 1):
        print('  волна %d/%d — %d фраз' % (i, total, len(chunk)), flush=True)
        try:
            res = arsenkin.run('commerce',
                               {'queries': chunk, 'se': 1, 'region': MOSCOW},
                               timeout=5400)
        except Exception as e:
            print('   !! волна %d упала: %s' % (i, e))
            break
        r = res.get('result', {})
        found = 0
        stack = [r]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                # ищем узлы, где есть и фраза, и число
                q = cur.get('query') or cur.get('word') or cur.get('phrase')
                if q and isinstance(q, str):
                    val = None
                    for k in ('commerce', 'commercial', 'value', 'percent',
                              'com', 'commerce_percent'):
                        if k in cur:
                            val = cur[k]
                            break
                    if val is not None:
                        done[q] = val
                        found += 1
                for v in cur.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                for v in cur:
                    if isinstance(v, (dict, list)):
                        stack.append(v)
        if not found:
            print('   структура ответа не распознана, сохраняю сырое для разбора')
            arsenkin.save(res, 'commerce_raw_wave%d' % i)
            break
        json.dump(done, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
        print('   распознано в волне: %d, всего: %d' % (found, len(done)), flush=True)

    print('\nпроверено фраз: %d' % len(done))
    if done:
        vals = [v for v in done.values() if isinstance(v, (int, float))]
        if vals:
            vals.sort()
            print('медиана коммерциализации: %s' % vals[len(vals) // 2])
            print('коммерческих (>=50): %d из %d'
                  % (sum(1 for v in vals if v >= 50), len(vals)))


main()

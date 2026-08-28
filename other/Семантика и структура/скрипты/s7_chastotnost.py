# -*- coding: utf-8 -*-
"""
Шаг 7. Частотность по Москве и коммерциализация.

Частотность из semantics — общероссийская, решения по ней принимать нельзя.
Здесь снимаем базовую и фразовую по региону 213 и проверяем коммерциализацию.

Порядок: предфильтр по общероссийской (чтобы не жечь лимиты на заведомо
пустых фразах) -> wordstat по Москве -> отсев по московской фразовой ->
commerce по выжившим.

Запускается волнами, результат каждой пачки сохраняется на диск.
"""
import os, sys, json, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin
arsenkin.OUT_DIR = os.path.join(PROJ, 'материалы', 'арсенкин')

MAT = os.path.join(PROJ, 'материалы')
MOSCOW = 213

WS_PREFILTER = int(os.environ.get('WS_PREFILTER', '80'))   # общероссийская wsk
MAX_CANDIDATES = int(os.environ.get('MAX_CANDIDATES', '3200'))
CHUNK = int(os.environ.get('CHUNK', '250'))
SOURCE = os.environ.get('SOURCE', 'ядро_коммерч.json')
TAG = os.environ.get('TAG', 'kom')


def cache_path(kind):
    return os.path.join(MAT, 'частотность_%s_%s.json' % (TAG, kind))


def load_cache(kind):
    p = cache_path(kind)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def save_cache(kind, obj):
    json.dump(obj, open(cache_path(kind), 'w', encoding='utf-8'), ensure_ascii=False)


def main():
    src = json.load(open(os.path.join(MAT, SOURCE), encoding='utf-8'))
    print('кандидатов на входе: %d' % len(src))

    ranked = sorted(src.items(), key=lambda kv: -kv[1].get('wsk', 0))
    pre = [(w, p) for w, p in ranked if p.get('wsk', 0) >= WS_PREFILTER][:MAX_CANDIDATES]
    print('после предфильтра (общероссийская wsk >= %d): %d, берём не более %d'
          % (WS_PREFILTER, sum(1 for _, p in ranked if p.get('wsk', 0) >= WS_PREFILTER),
             MAX_CANDIDATES))
    print('к съёму по Москве: %d' % len(pre))

    ws = load_cache('wordstat')
    todo = [w for w, _ in pre if w not in ws]
    print('уже в кэше: %d, осталось снять: %d' % (len(ws), len(todo)))

    for i, chunk in enumerate(arsenkin.chunked(todo, CHUNK), 1):
        total = math.ceil(len(todo) / CHUNK)
        print('  волна %d/%d — %d фраз' % (i, total, len(chunk)), flush=True)
        try:
            res = arsenkin.run('wordstat', {
                'queries': chunk, 'regions': [MOSCOW], 'type': 1,
                'ws': ['base', 'quoted', 'overal', 'exact'],
            }, timeout=3600)
        except Exception as e:
            print('   !! волна %d упала: %s' % (i, e))
            break
        data = res.get('result', {}).get('data', {}).get('result', {})
        for q, byreg in (data.items() if isinstance(data, dict) else []):
            v = byreg.get(str(MOSCOW), {}) if isinstance(byreg, dict) else {}
            # base = Ч, quoted = "Ч" (фразовая), overal = "!Ч" (точная)
            ws[q] = {'base': v.get('base', 0), 'quoted': v.get('quoted', 0),
                     'overal': v.get('overal', 0), 'exact': v.get('exact', 0)}
        save_cache('wordstat', ws)
        print('   снято всего: %d' % len(ws), flush=True)

    live = {w: v for w, v in ws.items() if v.get('quoted', 0) > 0}
    print('\nснято фраз: %d, с ненулевой московской фразовой: %d' % (len(ws), len(live)))
    if live:
        qs = sorted(v['quoted'] for v in live.values())
        print('медиана фразовой по Москве: %d' % qs[len(qs) // 2])

    json.dump(ws, open(os.path.join(MAT, 'частотность_москва_%s.json' % TAG), 'w',
                       encoding='utf-8'), ensure_ascii=False)
    print('сохранено: материалы/частотность_москва_%s.json' % TAG)


main()

# -*- coding: utf-8 -*-
"""
Шаг 5. Сбор ядра.

Доноры — реальные конкуренты, подтверждённые съёмом топ-10 на шаге 3,
а не список из брифа. Плюс поисковые подсказки по маркерам.

Частотность, которую отдаёт semantics, общероссийская. Здесь она нужна
только чтобы упорядочить кандидатов; решения принимаются позже,
по московской фразовой из wordstat.
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin
arsenkin.OUT_DIR = os.path.join(PROJ, 'материалы', 'арсенкин')

# домен -> сколько раз попал в топ-10 по 30 маркерам (шаг 3)
DONORS = [
    ('remo-nt.ru', 11),
    ('remony.ru', 10),
    ('domeo.ru', 10),
    ('titanremont.ru', 8),
    ('stroyremdizayn.ru', 7),
    ('only-remontkvartir.ru', 6),
    ('point-remont.ru', 5),
    ('centr-otdelka.ru', 5),
    ('vproekte.com', 5),          # дизайн
    ('mrnadzor.ru', 4),           # приёмка
    ('avalremont.ru', 4),
    ('eremont.ru', 4),            # Вира Артстрой, из брифа клиента
]

SUGGEST_MARKERS = [
    "ремонт квартир под ключ", "ремонт квартиры в новостройке",
    "ремонт вторички", "капитальный ремонт квартиры",
    "косметический ремонт квартиры", "дизайнерский ремонт квартиры",
    "ремонт однокомнатной квартиры", "ремонт двухкомнатной квартиры",
    "ремонт трехкомнатной квартиры", "ремонт квартиры студии",
    "дизайн интерьера квартиры", "дизайн проект квартиры",
    "дизайн интерьера офиса", "дизайн интерьера дома",
    "приемка квартиры в новостройке", "приемка квартиры с отделкой",
    "комплектация квартиры", "перепланировка квартиры",
    "механизированная штукатурка", "отделка квартир под ключ",
    "сколько стоит ремонт квартиры", "ремонт квартир цена",
]


def collect_domain(dom):
    name = 's5_dom_' + dom.replace('.', '_')
    cached = arsenkin.load(name)
    if cached:
        return cached, True
    res = arsenkin.run('semantics',
                       {'mode': 'domain', 'queries': [dom], 'region': 'msk'},
                       name=name, timeout=3600)
    return res, False


def collect_suggest():
    name = 's5_suggest'
    cached = arsenkin.load(name)
    if cached:
        return cached, True
    res = arsenkin.run('suggest', {
        'queries': SUGGEST_MARKERS,
        'se': 1, 'region': 213,
        'check': ['nrm', 'spc', 'lat', 'cyr', 'dig', 'loc', 'sho', 'quo'],
        'depth': 2,
    }, name=name, timeout=3600)
    return res, False


def main():
    phrases = {}   # фраза -> {'ws','wsk','isquest','src':set,'urls':set}

    def add(word, ws=0, wsk=0, isquest=0, src='', url=''):
        w = (word or '').strip().lower()
        if not w or len(w) < 3:
            return
        p = phrases.setdefault(w, {'ws': 0, 'wsk': 0, 'isquest': 0,
                                   'src': set(), 'urls': set()})
        p['ws'] = max(p['ws'], int(ws or 0))
        p['wsk'] = max(p['wsk'], int(wsk or 0))
        p['isquest'] = max(p['isquest'], int(isquest or 0))
        p['src'].add(src)
        if url:
            p['urls'].add(url)

    for dom, hits in DONORS:
        try:
            res, from_cache = collect_domain(dom)
        except Exception as e:
            print('  !! %s: %s' % (dom, e))
            continue
        r = res.get('result', {})
        items = r.get('result', {})
        n = 0
        for v in (items.values() if isinstance(items, dict) else items):
            add(v.get('word'), v.get('ws'), v.get('wsk'), v.get('isquest'),
                src=dom, url=v.get('url', ''))
            n += 1
        print('%-24s топ-10: %-3d фраз: %-6d %s'
              % (dom, hits, n, '(из кэша)' if from_cache else ''))

    try:
        res, from_cache = collect_suggest()
        r = res.get('result', {})
        cnt = 0
        stack = [r]
        seen_id = set()
        while stack:
            cur = stack.pop()
            if id(cur) in seen_id:
                continue
            seen_id.add(id(cur))
            if isinstance(cur, dict):
                for k, v in cur.items():
                    if isinstance(v, str) and len(v) > 3 and ' ' in v:
                        add(v, src='suggest'); cnt += 1
                    else:
                        stack.append(v)
            elif isinstance(cur, list):
                for v in cur:
                    if isinstance(v, str) and len(v) > 3 and ' ' in v:
                        add(v, src='suggest'); cnt += 1
                    else:
                        stack.append(v)
        print('%-24s подсказок: %-6d %s'
              % ('suggest', cnt, '(из кэша)' if from_cache else ''))
    except Exception as e:
        print('  !! suggest: %s' % e)

    out = os.path.join(PROJ, 'материалы', 'ядро_сырое.json')
    dump = {w: {'ws': p['ws'], 'wsk': p['wsk'], 'isquest': p['isquest'],
                'src': sorted(p['src']), 'urls': sorted(p['urls'])[:3]}
            for w, p in phrases.items()}
    json.dump(dump, open(out, 'w', encoding='utf-8'), ensure_ascii=False)

    print('\nуникальных фраз собрано: %d' % len(phrases))
    print('вопросительных (кандидаты в блог): %d'
          % sum(1 for p in phrases.values() if p['isquest']))
    print('сохранено: материалы/ядро_сырое.json')


main()

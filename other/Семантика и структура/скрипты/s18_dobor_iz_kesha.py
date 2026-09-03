# -*- coding: utf-8 -*-
"""
Шаг 18. Добор фраз новых направлений из кэша частотности.

Шаги 16 и 17 брали кандидатов только среди фраз, которые сами же и снимали.
При повторном запуске на прогретом кэше они не находят ничего, и страницы
новых услуг остаются без семантики. Здесь кандидаты берутся из всего кэша
по шаблонам направлений — независимо от того, когда фразу сняли.

Существующие фразы ядра не трогаются: скрипт только добавляет.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')

PORE = int(os.environ.get('PORE_KOM', '30'))

NAPRAVLENIYA = {
    'Установка кондиционеров': r'кондиционер|сплит[\s-]?систем',
    'Вентиляция': r'вентиляц|приточн\w*\s+установк|рекуператор',
    'Умный дом': r'умн\w*\s+дом|умн\w*\s+квартир',
    'Отопление и радиаторы': r'отоплен|радиатор|батаре\w*\s+отоплен',
    'Декоративная штукатурка': r'декоративн\w*\s+штукатурк|штукатурк\w*\s+декоративн|'
                               r'венецианск\w*\s+штукатурк|фактурн\w*\s+штукатурк|микроцемент',
    'Инженерные системы': r'инженерн\w*\s+(?:систем|сет|коммуникац)',
    'Отделочные работы': r'отделочн\w*\s+работ',
    'Ремонт гардеробной': r'гардеробн',
    'Ремонт коммерческих помещений': r'(?:ремонт|отделк)\w*[\w\s]{0,20}'
                                     r'(?:коммерческ|офис|магазин|салон|кафе|ресторан)',
    'Приёмка квартиры с отделкой': r'при[её]м\w*[\w\s]{0,25}'
                                   r'(?:с\s+отделк|чистов|предчистов|white\s*box)',
}


def main():
    ws = json.load(open(os.path.join(MAT, 'частотность_kom_wordstat.json'), encoding='utf-8'))
    core = json.load(open(os.path.join(MAT, 'ядро_финал.json'), encoding='utf-8'))
    blog = json.load(open(os.path.join(MAT, 'ядро_финал_блог.json'), encoding='utf-8'))
    cp = os.path.join(MAT, 'коммерциализация.json')
    comm = json.load(open(cp, encoding='utf-8')) if os.path.exists(cp) else {}

    print('на входе: коммерческих %d, блог %d' % (len(core), len(blog)))
    added_total = 0
    for page, pat in NAPRAVLENIYA.items():
        rx = re.compile(pat, re.I)
        cands = [w for w in ws
                 if rx.search(w) and ws[w].get('quoted', 0) >= 3 and w not in core]
        # интент проверяем тем же порогом, что и по всему ядру
        take = []
        for w in cands:
            c = comm.get(w)
            if isinstance(c, (int, float)) and c < PORE:
                continue
            take.append(w)
        take.sort(key=lambda w: -ws[w]['quoted'])
        if not take:
            print('%-32s добавить нечего' % page)
            continue
        print('%-32s +%-4d фраз, спрос %d' % (page, len(take),
                                              sum(ws[w]['quoted'] for w in take)))
        for w in take[:5]:
            print('      %-50s "Ч"=%d' % (w[:50], ws[w]['quoted']))
        for w in take:
            v = dict(ws[w])
            v['napravlenie'] = 'Новые услуги'
            v['src'] = ['добор по замечаниям клиента']
            v['varianty'] = []
            core[w] = v
            blog.pop(w, None)
            added_total += 1

    json.dump(core, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nдобавлено: %d' % added_total)
    print('стало: коммерческих %d, блог %d, всего %d'
          % (len(core), len(blog), len(core) + len(blog)))


main()

# -*- coding: utf-8 -*-
"""
Шаг 16. Досбор семантики под страницы, оставшиеся без фраз.

Заказчик утвердил структуру, в которой пять страниц не имеют ни одной фразы
в ядре. Такая страница не ранжируется вовсе, поэтому ядро под неё нужно
дособрать: сначала из уже собранного сырого пула, затем прямой проверкой
Вордстата по формулировкам, которых в пуле не оказалось.

Прямая проверка обязательна: отсутствие фразы у конкурентов-доноров ещё
не значит отсутствие спроса, донор мог просто не иметь такой страницы.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, r'C:\Users\User\.claude\skills\leoseo-structure\scripts')
import arsenkin  # noqa: E402
arsenkin.OUT_DIR = os.path.join(MAT, 'арсенкин')

MOSCOW = 213

# страница -> (регулярка для поиска в сыром пуле, список формулировок на проверку)
DOSBOR = {
    'Ремонт гардеробной': (
        r'гардеробн',
        ['ремонт гардеробной', 'отделка гардеробной', 'ремонт гардеробной комнаты',
         'гардеробная под ключ', 'гардеробная комната под ключ',
         'обустройство гардеробной', 'сделать гардеробную', 'гардеробная из кладовки']),
    'Ремонт коммерческих помещений': (
        r'(?:ремонт|отделк)\w*[\w\s]{0,20}(?:коммерческ|офис|магазин|салон|кафе|ресторан)',
        ['ремонт коммерческих помещений', 'отделка коммерческих помещений',
         'ремонт офиса под ключ', 'отделка офиса под ключ', 'ремонт офисных помещений',
         'ремонт магазина под ключ', 'отделка магазина', 'ремонт кафе под ключ',
         'ремонт помещения под ключ', 'ремонт нежилого помещения']),
    'Дизайн прихожей и коридора': (
        r'дизайн\w*[\w\s]{0,20}(?:прихож|коридор)|(?:прихож|коридор)\w*[\w\s]{0,12}дизайн',
        ['дизайн прихожей', 'дизайн коридора', 'дизайн проект прихожей',
         'дизайн интерьера прихожей', 'дизайн прихожей в квартире',
         'дизайн проект коридора', 'дизайн узкой прихожей']),
    'Приёмка квартиры с отделкой': (
        r'при[её]м\w*[\w\s]{0,25}(?:с\s+отделк|чистов|предчистов|white\s*box|с\s+ремонт)',
        ['приемка квартиры с отделкой', 'приёмка квартиры с отделкой',
         'приемка квартиры с чистовой отделкой', 'приемка квартиры от застройщика с отделкой',
         'приемка квартиры с предчистовой отделкой', 'приемка квартиры вайт бокс',
         'приемка квартиры с ремонтом от застройщика']),
    'Приёмка в ЖК (шаблон)': (
        r'при[её]м\w*[\w\s]{0,25}\bжк\b|\bжк\b[\w\s]{0,25}при[её]м',
        ['приемка квартиры в жк', 'приёмка квартиры в жк', 'приемка в жк',
         'приемщик квартир в жк', 'приемка новостройки в жк']),
}


def main():
    raw = json.load(open(os.path.join(MAT, 'ядро_сырое.json'), encoding='utf-8'))
    ws_cache = json.load(open(os.path.join(MAT, 'частотность_kom_wordstat.json'),
                              encoding='utf-8'))
    core = json.load(open(os.path.join(MAT, 'ядро_финал.json'), encoding='utf-8'))
    blog = json.load(open(os.path.join(MAT, 'ядро_финал_блог.json'), encoding='utf-8'))

    # 1. что находится в сыром пуле и ещё не снято по Москве
    to_check = {}
    for page, (pat, manual) in DOSBOR.items():
        rx = re.compile(pat, re.I)
        found = [w for w in raw if rx.search(w)]
        found.sort(key=lambda w: -raw[w].get('wsk', 0))
        cand = [w for w in found[:60] if w not in ws_cache]
        for w in cand:
            to_check[w] = page
        for w in manual:
            if w not in ws_cache:
                to_check[w] = page
        print('%-34s в пуле %-4d на съём %d' % (page, len(found), len(cand) + len(manual)))

    todo = sorted(to_check)
    print('\nвсего фраз на съём частотности: %d' % len(todo))

    if todo:
        for i in range(0, len(todo), 250):
            chunk = todo[i:i + 250]
            print('  волна %d — %d фраз' % (i // 250 + 1, len(chunk)), flush=True)
            res = arsenkin.run('wordstat', {
                'queries': chunk, 'regions': [MOSCOW], 'type': 1,
                'ws': ['base', 'quoted', 'overal', 'exact']}, timeout=3600)
            data = res.get('result', {}).get('data', {}).get('result', {})
            for q, byreg in (data.items() if isinstance(data, dict) else []):
                v = byreg.get(str(MOSCOW), {}) if isinstance(byreg, dict) else {}
                ws_cache[q] = {'base': v.get('base', 0), 'quoted': v.get('quoted', 0),
                               'overal': v.get('overal', 0), 'exact': v.get('exact', 0)}
            json.dump(ws_cache, open(os.path.join(MAT, 'частотность_kom_wordstat.json'),
                                     'w', encoding='utf-8'), ensure_ascii=False)

    # 2. отбираем живые и кладём в коммерческое ядро
    print('\n' + '=' * 78)
    added_total = 0
    for page, (pat, manual) in DOSBOR.items():
        cands = [w for w, p in to_check.items() if p == page]
        live = [(ws_cache[w]['quoted'], w) for w in cands
                if ws_cache.get(w, {}).get('quoted', 0) >= 3 and w not in core]
        live.sort(reverse=True)
        print('\n%s: живых фраз %d' % (page, len(live)))
        for q, w in live[:12]:
            print('    %-56s "Ч"=%d' % (w[:56], q))
        for q, w in live:
            v = dict(ws_cache[w])
            v['napravlenie'] = 'Досбор'
            v['src'] = ['досбор под утверждённую структуру']
            v['varianty'] = []
            core[w] = v
            blog.pop(w, None)
            added_total += 1

    # держим общий лимит: режем хвост блога
    LIM = int(os.environ.get('LIMIT_VSEGO', '2000'))
    room = max(0, LIM - len(core))
    if len(blog) > room:
        cut = len(blog) - room
        blog = dict(sorted(blog.items(), key=lambda kv: -kv[1].get('quoted', 0))[:room])
        print('\nиз блога убрано по лимиту: %d' % cut)

    json.dump(core, open(os.path.join(MAT, 'ядро_финал.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(blog, open(os.path.join(MAT, 'ядро_финал_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nдобавлено в коммерческое ядро: %d' % added_total)
    print('стало: коммерческих %d, блог %d, всего %d'
          % (len(core), len(blog), len(core) + len(blog)))


main()

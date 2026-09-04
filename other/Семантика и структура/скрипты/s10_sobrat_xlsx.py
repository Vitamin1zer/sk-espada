# -*- coding: utf-8 -*-
"""
Шаг 10. Сборка итоговых таблиц.

Собирает два файла в эталонном формате SEO VICTORY:
  * СЕМАНТИЧЕСКОЕ ЯДРО — листы «СЕМАНТИКА», «СЕМАНТИКА Блог», «СВОДКА»
  * СТРУКТУРА САЙТА   — листы «Структура сайта», «Структура меню», «Мета-теги»

Оформление снято с эталонов: шапка чёрной заливкой, шрифт Inter 10,
закреплённая первая строка, автофильтр по данным.
"""
import os, re, sys, json, shutil, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Темы блога. Порядок важен: узкие раньше широких.
BLOG_TEMY = [
    ('Стили интерьера', r'\bстил|лофт|сканди|прованс|джапанди|минимализм|хай[\s-]?тек|'
                        r'неоклассик|классическ|модерн|бохо|контемпорари|эклектик|ар[\s-]деко|фьюжн'),
    ('Цвет в интерьере', r'\bцвет|оттен|палитр|сочетани\w+\s+цвет|колер'),
    ('Бюджет и смета', r'сколько\s+стоит|бюджет|смет|сэконом|дешев|дорог[оа]|расход\w*\s+материал'),
    ('Этапы и сроки ремонта', r'с\s+чего\s+нач|этап|последовательн|сроки|порядок\s+работ|'
                              r'сколько\s+(?:длит|идёт|идет|занимает)'),
    ('Материалы и отделка', r'\bобо[ий]|плитк|ламинат|краск|штукатурк|шпакл|гипсокартон|'
                            r'смес|потолк|напольн|линолеум|паркет|керамогранит|затирк|грунтовк'),
    ('Инженерные системы', r'электрик|проводк|розетк|сантехник|труб|вентиляц|отоплен|'
                           r'т[её]плый\s+пол|кондиционер|канализац|водоснабжен'),
    ('Планировка и зонирование', r'планировк|зонирован|перепланировк|метраж|квадратн|'
                                 r'перегородк|ниш[аи]\b|студи'),
    ('Выбор подрядчика', r'как\s+выбрать\s+(?:бригад|подрядчик|компан)|договор|гарант|'
                         r'при[её]мк\w*\s+работ|обман|развод|контролир'),
    ('Мебель и хранение', r'мебел|шкаф|гардероб|гарнитур|систем\w*\s+хранен|комод|стеллаж'),
    ('Освещение', r'освещен|свет|светильник|люстр|подсветк|лампа'),
]
BLOG_RX = [(n, re.compile(p, re.I)) for n, p in BLOG_TEMY]


BLOG_SLUG = {
    'Стили интерьера': 'stili-interera',
    'Цвет в интерьере': 'cvet-v-interere',
    'Бюджет и смета': 'byudzhet-remonta',
    'Этапы и сроки ремонта': 'etapy-remonta',
    'Материалы и отделка': 'materialy',
    'Инженерные системы': 'inzhenernye-sistemy',
    'Планировка и зонирование': 'planirovka',
    'Выбор подрядчика': 'vybor-podryadchika',
    'Мебель и хранение': 'mebel-i-hranenie',
    'Освещение': 'osveshchenie',
    'Блог — хаб': '',
}


def blog_klaster(phrase):
    for name, pat in BLOG_RX:
        if pat.search(phrase):
            return name
    return 'Блог — хаб'


# Папка запроса — путь вложенности до страницы, русскими названиями.
# Показываем папку, в которой лежит кластер, а не саму страницу:
# «Инженерные системы» лежат в услугах, значит их папка /Услуги/,
# а электромонтаж лежит уже внутри инженерных систем —
# /Услуги/Инженерные системы/.
#
# Корневая папка — раздел меню. Там, где головной страницей раздела
# служит сама страница верхнего уровня (ремонт квартир, дизайн, приёмка),
# раздел и голову не дублируем: это один узел дерева.
RAZDEL = {
    '/remont-kvartir/':                   'Ремонт квартир',
    '/design/':                           'Дизайн интерьера',
    '/uslugi/':                           'Услуги',
}

_NAMES = None


def _names():
    """Название страницы по служебному вложенному адресу."""
    global _NAMES
    if _NAMES is None:
        _NAMES = {p[0]: p[1] for p in _load_s8b()['PAGES']}
    return _NAMES


def papka_ru(url):
    """Папка, в которой лежит кластер: путь вложенности без самой страницы."""
    import ploskie_url as PU
    if not url or url == '/':
        return '/Главная/'
    parts = []
    cur = PU.parent_nested(url)
    while cur:
        nm = _names().get(cur)
        if nm:
            parts.insert(0, nm)
        cur = PU.parent_nested(cur)
    top = '/%s/' % url.strip('/').split('/')[0]
    root = RAZDEL.get(top, 'Услуги')
    # раздел и его головная страница — один узел, второй раз не пишем
    if parts and parts[0] == _names().get(top):
        parts.pop(0)
    return '/%s/' % '/'.join([root] + parts)


def blog_papka(phrase):
    """Папка рубрики блога. Хаб живёт в корне раздела."""
    slug = BLOG_SLUG.get(blog_klaster(phrase), '')
    return '/blog/%s/' % slug if slug else '/blog/'


# Фразы, пришедшие в блог из коммерции, кладём в рубрику по их же странице.
# Так сразу видно, с какой коммерческой страницей связывать статью
# перелинковкой, а хаб не превращается в свалку.
_S8B = None


def _load_s8b():
    global _S8B
    if _S8B is None:
        src = open(os.path.join(HERE, 's8b_stranicy.py'), encoding='utf-8').read()
        src = src.replace('\nmain()\n', '\n')
        ns = {'__file__': os.path.join(HERE, 's8b_stranicy.py')}
        exec(compile(src, 's8b', 'exec'), ns)
        _S8B = ns
    return _S8B


def _load_assign():
    return _load_s8b()['assign']


_KLIENT = None


def _klient_slugs():
    """Слаги, утверждённые заказчиком: название страницы -> слаг."""
    global _KLIENT
    if _KLIENT is None:
        p = os.path.join(MAT, 'slagi_klienta.json')
        _KLIENT = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    return _KLIENT


def blog_rubrika(phrase, v):
    """(папка, кластер) статьи блога.

    Сначала пробуем привязать статью к коммерческой странице — тогда сразу
    видно, куда вести перелинковку. Пиллар в расчёт не берём: он ловит всё
    подряд как правило по умолчанию, и привязка к нему ничего не значит.
    Что не привязалось, раскладываем по тематическим рубрикам.

    Папка рубрики строится на слаге коммерческой страницы из таблицы
    заказчика, чтобы адреса блога и сайта не разъезжались.
    """
    import ploskie_url as PU
    url, name, sect = _load_assign()(phrase)
    if url != '/remont-kvartir/':
        slug = (_klient_slugs().get(name) or {}).get('slug') or PU.slug(url)
        return '/blog/%s/' % slug.strip('/'), name
    return blog_papka(phrase), blog_klaster(phrase)

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')
sys.path.insert(0, HERE)

HDR_FILL = PatternFill('solid', fgColor='FF000000')
HDR_FONT = Font(name='Inter', size=10, bold=True, color='FFFFFFFF')
BODY_FONT = Font(name='Inter', size=10)


def sheet(wb, title, headers, widths, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    for i, h in enumerate(headers, 1):
        c = ws.cell(1, i, h)
        c.fill = HDR_FILL
        c.font = HDR_FONT
        c.alignment = Alignment(horizontal='left', vertical='center')
    for i, w in enumerate(widths, 1):
        if w:
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'
    return ws


def put(ws, rows):
    for r, row in enumerate(rows, 2):
        for i, v in enumerate(row, 1):
            c = ws.cell(r, i, v)
            c.font = BODY_FONT
    if rows:
        ws.auto_filter.ref = 'A1:%s%d' % (get_column_letter(len(rows[0])), len(rows) + 1)


def build_semantics(out_path):
    core = json.load(open(os.path.join(MAT, 'ядро_разложено.json'), encoding='utf-8'))
    blog = {}
    p = os.path.join(MAT, 'ядро_финал_блог.json')
    if os.path.exists(p):
        blog = json.load(open(p, encoding='utf-8'))
    comm = {}
    p = os.path.join(MAT, 'коммерциализация.json')
    if os.path.exists(p):
        comm = json.load(open(p, encoding='utf-8'))

    # Фразы по страницам не перекладываем: низкая коммерциализация — это не повод
    # унести маркер страницы в блог, а повод пересмотреть роль самой страницы.
    # Сигнал уходит в вердикт на листе «Спрос по страницам» файла структуры.
    low = sum(1 for w in core if isinstance(comm.get(w), (int, float)) and comm[w] < 25)
    print('фраз с информационной выдачей (коммерциализация ниже 25 %%): %d из %d'
          % (low, len(core)))

    wb = Workbook()

    ws = sheet(wb, 'СЕМАНТИКА',
               ['Запрос', 'Ч', '"Ч"', '"!Ч"', 'Папка', 'КЛАСТЕР', 'Коммерциализация'],
               [77.6, 7.6, 6.5, 7.1, 30, 32, 19.9], first=True)
    # адрес страницы берём из таблицы заказчика: его слаги — источник истины
    import ploskie_url as PU

    def adres(v):
        nm = v.get('stranica', '')
        if nm == 'Главная':
            return '/'
        sl = (_klient_slugs().get(nm) or {}).get('slug')
        if sl:
            return '/%s/' % sl.strip('/')
        return PU.flat_url(v.get('url', ''))

    rows = []
    for w, v in sorted(core.items(),
                       key=lambda kv: (papka_ru(kv[1].get('url', '')),
                                       kv[1].get('stranica', ''),
                                       -kv[1]['quoted'])):
        rows.append([w, v.get('base', 0), v.get('quoted', 0), v.get('overal', 0),
                     papka_ru(v.get('url', '')), v.get('stranica', ''), comm.get(w, '')])
    put(ws, rows)

    ws2 = sheet(wb, 'СЕМАНТИКА Блог',
                ['Запрос', 'Ч', '"Ч"', '"!Ч"', 'Папка', 'КЛАСТЕР'],
                [77.6, 7.6, 6.5, 7.1, 30, 32])
    brows = []
    brubr = {w: blog_rubrika(w, v) for w, v in blog.items()}

    def botdel(phrase):
        # рубрика блога наследует отдел коммерческой страницы, к которой
        # привязана; что привязано к пиллару, живёт в собственных рубриках
        url, _, _ = _load_assign()(phrase)
        if url == '/remont-kvartir/':
            return '/Блог/'
        return '/Блог%s' % papka_ru(url)

    bo = {w: botdel(w) for w in blog}
    for w, v in sorted(blog.items(),
                       key=lambda kv: (bo[kv[0]], brubr[kv[0]][1],
                                       -kv[1].get('quoted', 0))):
        brows.append([w, v.get('base', 0), v.get('quoted', 0), v.get('overal', 0),
                      bo[w], brubr[w][1]])
    put(ws2, brows)

    ws3 = sheet(wb, 'СВОДКА', ['КЛАСТЕР', 'Сумма "Ч"'], [32, 14])
    agg = collections.Counter()
    for v in core.values():
        agg[v.get('stranica', '—')] += v.get('quoted', 0)
    srows = [[k, n] for k, n in agg.most_common()]
    bagg = collections.Counter()
    for w, v in blog.items():
        bagg['Блог · ' + brubr[w][1]] += v.get('quoted', 0)
    srows += [[k, n] for k, n in bagg.most_common()]
    put(ws3, srows)

    # ---- кластеры живой выдачи, отдельными листами ----
    kl_path = os.path.join(MAT, 'кластеры.json')
    if os.path.exists(kl_path):
        KL = json.load(open(kl_path, encoding='utf-8'))
        # для блога вместо коммерческой страницы показываем рубрику
        page_of = {'kom': lambda w: core.get(w, {}).get('stranica', ''),
                   'blog': lambda w: brubr.get(w, ('', ''))[1]}
        for tag, title, src in [('kom', 'Кластеры коммерция', core),
                                ('blog', 'Кластеры блог', blog)]:
            data = KL.get(tag, {})
            byc = data.get('by_cluster', {})
            byp = data.get('by_phrase', {})
            wsk = sheet(wb, title,
                        ['Кластер', 'Фраз', 'Суммарная "Ч"',
                         'Страница' if tag == 'kom' else 'Рубрика блога', 'Запросы'],
                        [46, 8, 15, 34, 120])
            krows = []
            for head, words in byc.items():
                q = sum(src.get(w, {}).get('quoted', 0) for w in words)
                pages = collections.Counter(page_of[tag](w) for w in words
                                            if page_of[tag](w))
                page = pages.most_common(1)[0][0] if pages else ''
                krows.append([head, len(words), q, page,
                              '; '.join(sorted(words, key=lambda w: -src.get(w, {}).get('quoted', 0))[:40])])
            singles = [w for w, k in byp.items() if not k]
            for w in sorted(singles, key=lambda w: -src.get(w, {}).get('quoted', 0)):
                krows.append([w, 1, src.get(w, {}).get('quoted', 0),
                              page_of[tag](w), w])
            krows.sort(key=lambda r: -r[2])
            put(wsk, krows)

    wb.save(out_path)
    # отдаём разложенное ядро дальше, в сборку структуры
    json.dump(core, open(os.path.join(MAT, 'ядро_итог_коммерч.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump({w: dict(v, papka=brubr[w][0], klaster=brubr[w][1]) for w, v in blog.items()},
              open(os.path.join(MAT, 'ядро_итог_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    return len(rows), len(brows), len(srows)


def build_structure(out_path, pages_rows, menu_cols, meta_rows):
    wb = Workbook()
    ws = sheet(wb, 'Структура сайта',
               ['Статус', 'Новый URL', 'Адрес на сайте', 'Название',
                'Родительская категория', '1 уровень', '2 уровень',
                '3 уровень', '4 уровень', 'Текст',
                'Статус SEO текста', 'Дата внедрения'],
               [23.1, 36.6, 22, 46, 34, 34, 34, 34, 30, 14, 18.6, 16],
               first=True)
    put(ws, pages_rows)

    ws2 = sheet(wb, 'Структура меню', list(menu_cols.keys()),
                [25.8] * len(menu_cols))
    depth = max(len(v) for v in menu_cols.values()) if menu_cols else 0
    mrows = []
    for i in range(depth):
        mrows.append([(v[i] if i < len(v) else '') for v in menu_cols.values()])
    put(ws2, mrows)
    ws2.freeze_panes = 'A2'

    ws3 = sheet(wb, 'Мета-теги',
                ['Название', 'Title', 'Длина', 'Description', 'Длина', 'H1', 'Длина'],
                [42.5, 59.0, 7.6, 99.8, 7.6, 43.1, 7.6])
    put(ws3, meta_rows)

    wb.save(out_path)
    return len(pages_rows), len(meta_rows)


if __name__ == '__main__':
    out = os.path.join(PROJ, 'СЕМАНТИЧЕСКОЕ ЯДРО _ СК ЭСПАДА _ SEO VICTORY.xlsx')
    if os.path.exists(out):
        bak = out.replace('.xlsx', ' (шаблон).xlsx')
        if not os.path.exists(bak):
            shutil.copyfile(out, bak)
    n1, n2, n3 = build_semantics(out)
    print('СЕМАНТИЧЕСКОЕ ЯДРО собрано: %d коммерческих, %d в блоге, %d кластеров в сводке'
          % (n1, n2, n3))

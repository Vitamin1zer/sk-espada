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


def blog_klaster(phrase):
    for name, pat in BLOG_RX:
        if pat.search(phrase):
            return name
    return 'Блог — хаб'

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
    rows = []
    for w, v in sorted(core.items(), key=lambda kv: (kv[1].get('url', ''), -kv[1]['quoted'])):
        rows.append([w, v.get('base', 0), v.get('quoted', 0), v.get('overal', 0),
                     v.get('url', ''), v.get('stranica', ''), comm.get(w, '')])
    put(ws, rows)

    ws2 = sheet(wb, 'СЕМАНТИКА Блог',
                ['Запрос', 'Ч', '"Ч"', '"!Ч"', 'Папка', 'КЛАСТЕР'],
                [77.6, 7.6, 6.5, 7.1, 18.0, 23.4])
    brows = []
    for w, v in sorted(blog.items(), key=lambda kv: (blog_klaster(w), -kv[1]['quoted'])):
        brows.append([w, v.get('base', 0), v.get('quoted', 0), v.get('overal', 0),
                      '/blog/', blog_klaster(w)])
    put(ws2, brows)

    ws3 = sheet(wb, 'СВОДКА', ['КЛАСТЕР', 'Сумма "Ч"'], [32, 14])
    agg = collections.Counter()
    for v in core.values():
        agg[v.get('stranica', '—')] += v.get('quoted', 0)
    srows = [[k, n] for k, n in agg.most_common()]
    bagg = collections.Counter()
    for w, v in blog.items():
        bagg[blog_klaster(w)] += v.get('quoted', 0)
    srows += [[k, n] for k, n in bagg.most_common()]
    put(ws3, srows)

    wb.save(out_path)
    # отдаём разложенное ядро дальше, в сборку структуры
    json.dump(core, open(os.path.join(MAT, 'ядро_итог_коммерч.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump({w: dict(v, klaster=blog_klaster(w)) for w, v in blog.items()},
              open(os.path.join(MAT, 'ядро_итог_блог.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    return len(rows), len(brows), len(srows)


def build_structure(out_path, pages_rows, menu_cols, meta_rows):
    wb = Workbook()
    ws = sheet(wb, 'Структура сайта',
               ['Статус', 'Новый URL', 'адрес в шаблоне', 'Название', 'Текст',
                'Статус SEO текста', 'Дата внедрения'],
               [23.1, 36.6, 30, 54.1, 14, 18.6, 16], first=True)
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

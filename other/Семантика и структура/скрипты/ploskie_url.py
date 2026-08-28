# -*- coding: utf-8 -*-
"""
Плоские адреса при сохранённой иерархии в админке.

Решение заказчика: у всех страниц сайта уникальный слаг и плоский адрес,
`/design-kvartir/` вместо `/design/kvartir/`. При этом в админке WordPress
через Nested Pages сохраняется вложенность: все страницы, включая блог,
лежат в одном разделе «Страницы» деревом.

Поэтому вложенный путь остаётся внутренним представлением — он несёт
иерархию, — а наружу выдаётся плоский адрес. Родитель для админки
вычисляется из того же вложенного пути.

Блог по решению заказчика остаётся под своим префиксом: `/blog/design-vannoy/`,
без дальнейшего дробления на категории.
"""


def segments(nested):
    return [s for s in nested.strip('/').split('/') if s]


def flat_url(nested):
    """Вложенный путь -> плоский адрес страницы."""
    seg = segments(nested)
    if not seg:
        return '/'
    return '/' + '-'.join(seg) + '/'


def slug(nested):
    """Слаг страницы: то, что уходит в post_name."""
    seg = segments(nested)
    # у главной своего сегмента нет, но post_name в WordPress ей всё равно нужен
    return '-'.join(seg) if seg else 'glavnaya'


def parent_nested(nested):
    """Вложенный путь родителя, либо пусто для верхнего уровня."""
    seg = segments(nested)
    if len(seg) <= 1:
        return ''
    return '/' + '/'.join(seg[:-1]) + '/'


def parent_slug(nested):
    """Слаг родителя для колонки parent_page_slug в pages.csv."""
    p = parent_nested(nested)
    return slug(p) if p else ''


def level(nested):
    return len(segments(nested))


def blog_flat(nested_rubric):
    """Рубрика блога -> плоский адрес под /blog/.

    На вход приходит путь вида /blog/design/vannoy/, на выходе
    /blog/design-vannoy/ — без дробления на категории.
    """
    seg = segments(nested_rubric)
    if not seg or seg == ['blog']:
        return '/blog/'
    tail = '-'.join(seg[1:])
    return '/blog/%s/' % tail


def check_unique(nested_list):
    """Проверяет, что после уплощения слаги не столкнулись."""
    seen = {}
    dupes = []
    for n in nested_list:
        s = slug(n)
        if s in seen:
            dupes.append((s, seen[s], n))
        else:
            seen[s] = n
    return dupes

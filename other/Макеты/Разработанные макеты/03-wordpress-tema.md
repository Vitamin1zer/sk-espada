# 03. Тема WordPress

## 1. Базовые решения

| Вопрос | Решение | Почему |
|---|---|---|
| Тип темы | Классическая, PHP-шаблоны | Дизайн фиксированный, редактор блоков здесь только мешал бы: контент-менеджер должен заполнять поля, а не собирать вёрстку |
| Поля | ACF Pro | Гибкие группы, повторители, условная логика по шаблону |
| Разделы услуг | Обычные страницы (`page`) с деревом | Нужна вложенность в админке для крошек и мега-меню; CPT здесь ничего не даёт |
| Портфолио | CPT `project` | Своя таксономия фильтров, отдельная архивная страница |
| Блог | Штатные `post` + рубрики | Не изобретать |
| Отзывы | CPT `review` | Выводятся на нескольких страницах, нужна фильтрация по услуге |
| Меню | Штатные `nav_menu` (три локации) | Мега-меню строится из дерева страниц, а не из ручного меню — см. §5 |
| Формы | Свой обработчик на `admin-post.php` + REST | CF7 и WPForms навязывают свою разметку и стили; дизайн формы слишком специфичный |
| Мультиязычность | Не нужна | — |

Плагины: **ACF Pro** (обязательно), **Yoast SEO** или **Rank Math** (мета-теги и sitemap), **WebP Express** или конвертация на сборке. Больше ничего.

## 2. Структура темы

```
wp-content/themes/espada/
├── style.css                  только заголовок темы, стили не здесь
├── functions.php              подключение модулей из inc/
├── screenshot.png
│
├── inc/
│   ├── setup.php              theme_support, размеры изображений, меню
│   ├── assets.php             wp_enqueue_style / script, версионирование
│   ├── cpt.php                CPT project, review
│   ├── taxonomies.php         таксономии фильтров портфолио
│   ├── acf-fields.php         регистрация групп кодом (см. §4)
│   ├── acf-blocks.php         пусто, если блоки не используем
│   ├── breadcrumbs.php        построение крошек по post_parent
│   ├── megamenu.php           сборка дерева и упаковка групп в карточки
│   ├── forms.php              обработчик заявок, валидация, письма
│   ├── quiz.php               REST-эндпоинт квиза
│   ├── seo.php                JSON-LD: Organization, BreadcrumbList, FAQPage, Article
│   └── helpers.php            espada_phone_link(), espada_svg_icon(), espada_price()
│
├── template-parts/
│   ├── layout/
│   │   ├── header-util.php        утилитарная строка
│   │   ├── header-main.php        основная строка
│   │   ├── megamenu.php           панель мега-меню
│   │   ├── mobile-menu.php        мобильное меню с аккордеоном
│   │   └── breadcrumbs.php
│   ├── section/
│   │   ├── hero.php               обложка с формой
│   │   ├── hero-page.php          обложка внутренней без изображения
│   │   ├── lead.php               вводный текст + цифры
│   │   ├── clusters.php           плитка кластеров ссылок
│   │   ├── tariffs.php            тарифы с табами
│   │   ├── rates-table.php        таблица цены и сроков
│   │   ├── includes.php           «что входит» тремя блоками
│   │   ├── steps.php              этапы работ
│   │   ├── works.php              примеры работ
│   │   ├── quiz.php               квиз-калькулятор
│   │   ├── seo-text.php           SEO-блок с раскрытием
│   │   ├── faq.php                аккордеон вопросов
│   │   ├── reviews.php            отзывы
│   │   ├── siblings.php           чипы соседних кластеров
│   │   ├── partners.php           логотипы поставщиков
│   │   ├── cta.php                блок перед подвалом
│   │   └── contacts.php           контакты с картой
│   ├── card/
│   │   ├── work.php  tariff.php  review.php  post.php  direction.php
│   └── form/
│       ├── inline.php  modal.php  footer.php  partner.php
│       └── fields.php             общие поля: имя, телефон, согласие
│
├── page-templates/
│   ├── tpl-pillar.php         пиллар услуги
│   ├── tpl-category.php       категория услуги
│   ├── tpl-home.php           главная
│   ├── tpl-portfolio.php      портфолио (архив через страницу)
│   ├── tpl-reviews.php        отзывы
│   ├── tpl-about.php          о компании
│   ├── tpl-contacts.php       контакты
│   ├── tpl-faq.php            вопросы и ответы
│   ├── tpl-zhk.php            страница ЖК
│   ├── tpl-legal.php          юридический документ
│   ├── tpl-thanks.php         спасибо
│   └── tpl-partners.php       партнёрам
│
├── single-project.php         карточка кейса
├── single.php                 статья блога
├── archive.php  index.php  404.php  search.php
├── header.php  footer.php
│
├── assets/
│   ├── scss/                  ← из этого пакета
│   ├── js/
│   │   ├── main.js            точка входа
│   │   └── modules/           header.js quiz.js filters.js forms.js accordion.js
│   ├── fonts/                 TildaSans-*.woff2
│   ├── img/                   brand/ icons/ (SVG-спрайт)
│   └── dist/                  сборка: main.css, main.js
└── package.json  vite.config.js  .stylelintrc.json
```

## 3. Custom Post Types и таксономии

```php
// inc/cpt.php

register_post_type('project', [
  'label'         => 'Проекты',
  'public'        => true,
  'has_archive'   => false,          // архив — через страницу /portfolio/
  'rewrite'       => ['slug' => 'portfolio', 'with_front' => false],
  'supports'      => ['title', 'thumbnail', 'editor', 'excerpt'],
  'menu_icon'     => 'dashicons-portfolio',
  'show_in_rest'  => true,
]);

register_post_type('review', [
  'label'        => 'Отзывы',
  'public'       => false,           // своей страницы у отзыва нет
  'show_ui'      => true,
  'supports'     => ['title'],
  'menu_icon'    => 'dashicons-format-quote',
]);
```

Таксономии для фильтров портфолио — по одной на фильтр, чтобы фильтрация шла через `tax_query`, а не через сравнение метаполей:

```php
// inc/taxonomies.php
$taxes = [
  'obj_type'  => 'Тип объекта',   // Новостройка, Вторичка, Студия, Дом
  'rooms'     => 'Комнаты',       // Студия, 1, 2, 3 и больше
  'work_type' => 'Тип работ',     // Косметический, Чистовой, Черновой, Под ключ, Капитальный, Дизайнерский
  'zhk'       => 'ЖК',            // список от заказчика
];
```

Площадь — числовое метаполе `area_m2`, фильтруется диапазонами через `meta_query`. Диапазоны фиксированные: до 40, 40–70, 70–100, больше 100 м².

## 4. ACF: группы полей

Регистрировать **кодом** через `acf_add_local_field_group()` в `inc/acf-fields.php`, не через админку. Причина: поля попадают в git, разворачиваются на любом окружении одной командой, и Claude Code может их читать и править.

### Группа: Обложка (`espada_hero`)
Условие: шаблоны пиллара, категории, главной, ЖК.

| Поле | Тип | Заметка |
|---|---|---|
| `hero_h1` | text | Если пусто — берётся заголовок страницы |
| `hero_price` | text | «8 850». Пусто — блок цены скрывается (приёмка) |
| `hero_price_note` | text | По умолчанию «Цена „от“ указана за квадратный метр по полу» |
| `hero_bullets` | repeater → text | 3–4 пункта с тире |
| `hero_image` | image | Первый экран, `loading="eager"` |
| `hero_cta_primary` | select | Значения из таблицы CTA (04-tokeny.md §8) |
| `hero_cta_secondary` | select | Пусто — вторая кнопка скрывается |
| `hero_form_title` | text | Заголовок формы на обложке |
| `hero_form_text` | textarea | Пояснение под заголовком |

### Группа: Вводный блок (`espada_lead`)
| Поле | Тип |
|---|---|
| `lead_title` | text |
| `lead_text` | textarea |
| `lead_facts` | repeater: `value` (text), `label` (text), 3–4 строки |

### Группа: Кластеры ссылок (`espada_clusters`)
Условие: шаблон пиллара.

| Поле | Тип | Заметка |
|---|---|---|
| `clusters_title` | text | |
| `clusters_note` | textarea | |
| `clusters_source` | radio | `auto` — собрать из дочерних страниц по полю группы; `manual` — задать вручную |
| `clusters_groups` | repeater: `title` (text), `items` (relationship → page) | Только при `manual` |

При `auto` PHP собирает дочерние страницы текущей и группирует по их полю `page_cluster_group` (см. группу «Служебные»). Упаковка групп в карточки — §5.

### Группа: Тарифы (`espada_tariffs`)
| Поле | Тип |
|---|---|
| `tariffs_title` | text |
| `tariffs_tabs_enabled` | true_false |
| `tariffs_tabs` | repeater: `tab_label` (text), `tab_items` (repeater: `title`, `price`, `image`, `features` (repeater → text)) |

### Группа: Таблица цены и сроков (`espada_rates`)
Условие: шаблон категории.

| Поле | Тип |
|---|---|
| `rates_label` | text | «Тариф» / «Пакет» / «Услуга» |
| `rates_rows` | repeater: `title`, `price`, `term` |
| `rates_note` | textarea |

### Группа: Что входит (`espada_includes`)
`includes_title` (text) + `includes_groups` (repeater: `title`, `items` (repeater → text)). Ровно три группы по дизайну.

### Группа: Этапы (`espada_steps`)
`steps_title` (text) + `steps_items` (repeater: `title`, `text`). Нумерация автоматическая, в поля не вводится.

### Группа: Квиз (`espada_quiz`)
| Поле | Тип |
|---|---|
| `quiz_enabled` | true_false |
| `quiz_kind` | radio: `remont` / `design` |
| `quiz_title` | text |

Сами шаги квиза — не в ACF, а в PHP-конфиге `inc/quiz.php`: они одинаковые на всех страницах, менять их через админку не нужно и опасно (сломается расчёт).

### Группа: SEO-текст (`espada_seo_text`)
`seo_text_title` (text) + `seo_text_body` (wysiwyg). Выводится в `.espada-prose`, сворачивается на высоте ~150 px с кнопкой «Читать полностью».

### Группа: FAQ (`espada_faq`)
`faq_items` (repeater: `question` (text), `answer` (wysiwyg)). Из этого же поля генерируется JSON-LD `FAQPage`.

### Группа: Проект портфолио (`espada_project`)
Условие: CPT `project`.

| Поле | Тип |
|---|---|
| `area_m2` | number | Для фильтра по площади |
| `term_months` | number | |
| `params` | repeater: `key`, `value` | Таблица параметров объекта |
| `story` | repeater → textarea | Задача и решение |
| `gallery` | gallery | Галерея с миниатюрами |
| `before_after` | repeater: `label`, `image`, `note` | Два элемента |
| `scope` | repeater: `title`, `items` (repeater → text) | Состав работ |
| `review_ref` | post_object → review | Отзыв клиента по объекту |
| `related_services` | relationship → page | Услуги из проекта |

### Группа: Отзыв (`espada_review`)
| Поле | Тип |
|---|---|
| `author_name` | text |
| `author_avatar` | image |
| `rating` | number, 1–5 |
| `source` | select: Яндекс.Карты / 2ГИС / Отзовик |
| `source_url` | url | Ссылка на оригинал — обязательна |
| `date_published` | date_picker |
| `service` | select | Для фильтра по услуге |
| `text` | textarea |
| `photo` | image | Фото объекта, опционально |

### Группа: Страница ЖК (`espada_zhk`)
`developer`, `year_built`, `house_type`, `ceiling_height`, `builder_finish` (text) + `defects` (repeater → text) + `projects` (relationship → project).

### Группа: Служебные (`espada_page_meta`)
Условие: все страницы.

| Поле | Тип | Заметка |
|---|---|---|
| `page_cluster_group` | text | В какую группу мега-меню и кластеров попадает страница: «По виду ремонта», «По помещениям» и т.д. |
| `page_menu_label` | text | Короткая подпись для меню: «Новостройка» вместо «Ремонт квартиры в новостройке» |
| `page_menu_order` | number | Порядок внутри группы |
| `page_hide_sections` | checkbox | Какие секции скрыть на этой странице |

Поле `page_menu_label` — ключевое. Заказчик отдельно требовал убрать переспам во вложенных пунктах меню: в шапке раздел называется «Ремонт квартир», а дочерние — «Новостройка», «Вторичка», «Однокомнатная», без повтора слова «ремонт». Полное название живёт в `post_title` и в `h1`, короткое — в меню и чипах.

## 5. Мега-меню: сборка и упаковка

Меню строится **из дерева страниц**, не из `nav_menu`. Причина: 25 дочерних страниц раздела ремонта нужно группировать, и держать это руками в двух местах — гарантированное расхождение.

```php
// inc/megamenu.php, упрощённо

function espada_megamenu_groups(int $parent_id): array {
    $children = get_pages([
        'child_of'    => $parent_id,
        'parent'      => $parent_id,
        'sort_column' => 'menu_order,post_title',
    ]);

    $groups = [];
    foreach ($children as $page) {
        $group = get_field('page_cluster_group', $page->ID) ?: '';
        $groups[$group][] = [
            'label' => get_field('page_menu_label', $page->ID) ?: $page->post_title,
            'url'   => get_permalink($page),
        ];
    }
    return $groups;
}

/**
 * Упаковка групп в карточки.
 * Группа от 8 ссылок занимает карточку целиком, мелкие складываются
 * вместе до 8 ссылок. Так карточки в ряду получаются близкой высоты,
 * и внутри нет пустот — заказчик правил этот дефект отдельно.
 */
function espada_pack_cards(array $groups, int $limit = 8): array {
    $cards = [];
    $current = null;

    foreach ($groups as $title => $items) {
        if (count($items) >= $limit) {
            $cards[] = [['title' => $title, 'items' => $items]];
            $current = null;
            continue;
        }
        $size = $current ? array_sum(array_map(fn($g) => count($g['items']), $current)) : 0;
        if ($current !== null && $size + count($items) <= $limit) {
            $current[] = ['title' => $title, 'items' => $items];
            $cards[count($cards) - 1] = $current;
            continue;
        }
        $current = [['title' => $title, 'items' => $items]];
        $cards[] = $current;
    }
    return $cards;
}
```

Результат кешировать в транзиент с инвалидацией на `save_post`:

```php
add_action('save_post_page', fn() => delete_transient('espada_megamenu'));
```

Промо-карточка справа — отдельная ACF-группа на странице-родителе: `megamenu_promo_title`, `_text`, `_cta`, `_link`.

## 6. Хлебные крошки

Строятся по `post_parent`, **не по URL**. Адреса плоские (`/design-kvartir/`), вложенность существует только в дереве админки.

```php
// inc/breadcrumbs.php
function espada_breadcrumbs(): array {
    $items = [['label' => 'Главная', 'url' => home_url('/')]];

    if (is_singular('project')) {
        $items[] = ['label' => 'Портфолио', 'url' => get_permalink(get_page_by_path('portfolio'))];
        $items[] = ['label' => get_the_title(), 'url' => null];
        return $items;
    }

    if (is_singular('post')) {
        $items[] = ['label' => 'Блог', 'url' => get_permalink(get_page_by_path('blog'))];
        $items[] = ['label' => get_the_title(), 'url' => null];
        return $items;
    }

    if (is_page()) {
        $ancestors = array_reverse(get_post_ancestors(get_the_ID()));
        foreach ($ancestors as $id) {
            $items[] = ['label' => get_the_title($id), 'url' => get_permalink($id)];
        }
        $items[] = ['label' => get_the_title(), 'url' => null];
    }

    return $items;
}
```

Последний элемент — без ссылки. Из того же массива генерируется JSON-LD `BreadcrumbList`.

## 7. Перенос контента

**Дерево страниц** создаётся импортом `pages.csv`. Колонки:

```
post_title, post_name, post_parent (slug родителя), page_template,
menu_order, page_menu_label, page_cluster_group, meta_title, meta_description, hero_h1
```

Порядок работ:

1. Сначала родители (`/remont-kvartir/`, `/design/`, `/priemka/`, `/uslugi/`), потом дочерние — иначе `post_parent` не разрешится.
2. Слаги — из `other/Семантика и структура/скрипты/s11_struktura.py`. Не переизобретать: под них уже собрана семантика и будут настроены редиректы.
3. `page_menu_label` заполнять обязательно — иначе в меню попадут длинные названия с переспамом.
4. Мета-теги — из отдельной выгрузки SEO-специалиста, не генерировать из заголовка.
5. Контент существующих пяти страниц (главная, дизайн, комплектация, приёмка, партнёрам) переносится из `other/Выгрузка сайта с Тильды/stranicy/*/content.md` — тексты финальные, переписывать не нужно.
6. Изображения: пережать в WebP, загрузить в медиабиблиотеку, привязать через ACF. `alt` брать из макетов — они заполнены осмысленно.

Если подключен скилл `wp-migration` — он описывает формат CSV и связку с ACF подробнее, использовать его.

**Редиректы.** Список 301 со старых адресов Tilda готовит SEO-специалист. Ставить до открытия индексации.

## 8. Формы: обработка

Свой обработчик, без плагинов форм.

```php
// inc/forms.php
add_action('wp_ajax_espada_lead',        'espada_handle_lead');
add_action('wp_ajax_nopriv_espada_lead', 'espada_handle_lead');
```

Требования:

- **Nonce** обязателен. Плюс honeypot-поле и проверка времени заполнения (меньше 2 секунд — бот).
- **Серверная валидация** дублирует клиентскую: телефон — 10 цифр после `+7`, согласие — обязательно, кроме формы подвала.
- **Заявки сохраняются в БД** (CPT `lead`, `public => false`), а не только уходят письмом. Письма теряются, заявки — деньги.
- В заявку писать: источник (URL страницы), тип формы, UTM из сессии, и **сводку ответов квиза**, если заявка пришла из него.
- Ответ JSON: `{ success, message, redirect }`. При успехе фронт показывает экран подтверждения и уводит на `/spasibo/` — цель в Метрике считается по переходу на этот адрес, а не по нажатию кнопки.
- Ошибки возвращать полями: `{ errors: { phone: 'Введите номер полностью — 10 цифр после +7' } }`, чтобы фронт подсветил конкретное поле.

## 9. Квиз: расчёт на сервере

Ставки не хранить в JS — их видно в исходнике и легко подделать запрос. Конфиг в PHP:

```php
// inc/quiz.php
const ESPADA_RATES = [
  'remont' => [
    'Косметический' => 7200, 'Чистовой' => 8850, 'Черновой' => 9890,
    'Под ключ' => 13050, 'Дизайнерский' => 15290,
  ],
  'design' => [
    'Технический' => 1790, 'Стандартный' => 2400,
    'Полный' => 3500, 'Авторский' => 4800,
  ],
];
```

Вилка: `ставка × площадь` и `× 1.25`, округление до тысяч. Приписка про ориентир и «точная смета после замера» — обязательна, это не украшение, а защита от претензий.

REST-эндпоинт `/wp-json/espada/v1/quiz/estimate` принимает выбор и площадь, возвращает вилку. Фронт может считать локально для отзывчивости, но в заявку уходит серверное значение.

## 10. Производительность

- Мега-меню, список ЖК, логотипы партнёров — в транзиенты с инвалидацией на `save_post`.
- Изображения: `add_image_size()` под реальные размеры из макетов (карточка работы 4:3, миниатюра галереи 104×74, аватар отзыва 42×42). Не полагаться на `large`/`medium`.
- `loading="lazy"` на всё, кроме первого экрана; `fetchpriority="high"` на изображение обложки.
- Шрифты: `preload` двух начертаний (ExtraBold и Regular), `font-display: swap`.
- Скрипты — `defer`. Квиз и фильтры грузить только на страницах, где они есть, через условный `wp_enqueue_script`.
- Цель по Core Web Vitals: LCP первого экрана до 2,5 с на 4G.

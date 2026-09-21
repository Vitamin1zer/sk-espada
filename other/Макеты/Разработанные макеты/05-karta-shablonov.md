# 05. Карта шаблонов

## 1. Как читать таблицу

Многие макеты содержат несколько страниц в одном файле — они переключаются свойством `page` в панели твиков справа. Столбец «Вариант» указывает, какое значение выбрать, чтобы увидеть нужную страницу.

Столбец «Приоритет» — порядок вёрстки. Внутри одного номера порядок неважен.

## 2. Сквозные элементы

| Макет | Вариант | Шаблон темы | ACF | Приоритет |
|---|---|---|---|---|
| `Сквозные элементы.dc.html` | блоки 1a–1d | `template-parts/layout/header-*.php` | Дерево страниц + `page_menu_label`, `page_cluster_group` | **1** |
| — | блок 1b–1c | `template-parts/layout/megamenu.php` | `megamenu_promo_*` на родителе | **1** |
| — | блок 1g | `template-parts/layout/mobile-menu.php` | то же дерево | **1** |
| — | блок 1e | `template-parts/layout/breadcrumbs.php` | — (строится по `post_parent`) | **1** |
| — | блок 1f | `footer.php` | Опции темы: контакты, реквизиты | **1** |
| — | блок 1i | `scss/abstracts/_tokens.scss` | — | **1** |
| — | блок 1h | справочный: как выглядит шапка на Tilda сейчас | — | не верстать |

Блок 1h — эталон для сверки, в тему не переносится.

## 3. Компоненты

| Макет | Вариант | Шаблон темы | Приоритет |
|---|---|---|---|
| `Формы.dc.html` | 6a | `template-parts/form/inline.php` | **2** |
| — | 6b, 6e | `template-parts/form/modal.php` | **2** |
| — | 6c | `template-parts/form/footer.php` | **2** |
| — | 6d | `template-parts/form/partner.php` | **2** |
| `Форма.dc.html` | все | общие поля → `template-parts/form/fields.php` | **2** |
| `Квиз-калькуляторы.dc.html` | 5a–5g | `template-parts/section/quiz.php` + `js/modules/quiz.js` | **2** |
| `Квиз.dc.html` | Ремонт / Дизайн-проект | конфиг шагов → `inc/quiz.php` | **2** |

Форма и квиз собираются до шаблонов страниц: дальше они встречаются почти на каждой.

## 4. Шаблоны страниц

| Макет | Вариант | Шаблон темы | URL | ACF-группы | Приоритет |
|---|---|---|---|---|---|
| `Пиллар услуги.dc.html` | Ремонт квартир | `tpl-pillar.php` | `/remont-kvartir/` | hero, lead, clusters, tariffs, steps, quiz, seo_text, faq | **3** |
| — | Дизайн интерьера | `tpl-pillar.php` | `/design/` | те же | **3** |
| — | Приёмка квартир | `tpl-pillar.php` | `/priemka/` | те же, tariffs отключены | **3** |
| `Категория услуги.dc.html` | Ремонт в новостройке | `tpl-category.php` | `/remont-kvartir-novostroyka/` | hero, lead, includes, rates, steps, quiz, seo_text, faq, siblings | **4** |
| — | Дизайн кухни | `tpl-category.php` | `/design-kuhni/` | те же | **4** |
| — | Приёмка без отделки | `tpl-category.php` | `/priemka-bez-otdelki/` | те же | **4** |
| `Главная.dc.html` | — | `tpl-home.php` | `/` | своя группа: 19 секций | **5** |
| `Портфолио и отзывы.dc.html` | Портфолио | `tpl-portfolio.php` | `/portfolio/` | таксономии + `area_m2` | **6** |
| — | Кейс | `single-project.php` | `/portfolio/{slug}/` | espada_project | **6** |
| — | Отзывы | `tpl-reviews.php` | `/otzyvy/` | espada_review | **6** |
| `О компании и контакты.dc.html` | О компании | `tpl-about.php` | `/o-kompanii/` | своя группа | **7** |
| — | Контакты | `tpl-contacts.php` | `/kontakty/` | опции темы | **7** |
| `Блог.dc.html` | Список | `home.php` или `tpl-blog.php` | `/blog/` | штатные рубрики | **8** |
| — | Статья | `single.php` | `/blog/{slug}/` | espada_faq (опционально), TOC из h2 | **8** |
| `Служебные страницы.dc.html` | Вопросы и ответы | `tpl-faq.php` | `/voprosy-i-otvety/` | espada_faq по группам | **9** |
| — | Страница ЖК | `tpl-zhk.php` | `/remont-v-zhk-{slug}/` | espada_zhk | **9** |
| — | Юридическая | `tpl-legal.php` | `/soglasie-na-obrabotku/`, `/politika-konfidencialnosti/` | wysiwyg | **9** |
| — | 404 | `404.php` | — | опции темы | **9** |
| — | Спасибо | `tpl-thanks.php` | `/spasibo/` | опции темы | **9** |
| `Дизайн интерьера.dc.html` | — | контент для `/design/` | `/design/` | — | справочный |
| `Комплектация.dc.html` | — | `tpl-pillar.php` | `/komplektaciya/` | hero, lead, steps, cta | **5** |
| `Приёмка квартир.dc.html` | — | контент для `/priemka/` | `/priemka/` | — | справочный |
| `Партнёрам.dc.html` | — | `tpl-partners.php` | `/partners/` | своя группа | **7** |

Четыре макета помечены «справочный»: это страницы текущего сайта, перенесённые 1-в-1 на этапе 2. Их вёрстка вобрана в шаблоны пиллара и категории — отдельные шаблоны для них не нужны, но **тексты и структуру секций брать оттуда**, а не из абстрактного пиллара.

## 5. Секции по шаблонам

Какие `template-parts/section/*` вызывает каждый шаблон, в порядке вывода.

**`tpl-pillar.php`**
```
breadcrumbs → hero → lead → clusters → tariffs → steps → works
→ quiz → seo-text → faq → reviews → cta → contacts
```

**`tpl-category.php`**
```
breadcrumbs → hero → lead → includes → rates-table → works
→ quiz → seo-text → faq → siblings → cta
```

**`tpl-home.php`** — самый длинный, 19 секций. Порядок в макете `Главная.dc.html`, сверяться по `data-screen-label` каждой секции:
```
hero → directions (4 направления) → works-with-us (шевроны) → case-intro
→ case-worries → case-moments → engineer → avoided → results + gallery
→ tariffs → portfolio → masters → designers → partners → faq → reviews
→ cta → contacts
```

**`single-project.php`**
```
breadcrumbs → title → gallery → params + story → before-after
→ scope → review → siblings (услуги проекта) → cta
```

**`tpl-portfolio.php`**
```
breadcrumbs → title → filters → works-grid → cta
```

**`tpl-reviews.php`**
```
breadcrumbs → title → rating-summary → filters → reviews-grid
→ leave-review (ссылки на площадки + форма) → cta
```

**`tpl-faq.php`**
```
breadcrumbs → title → faq-groups (боковая навигация + аккордеоны) → cta
```

**`single.php`** (статья блога)
```
breadcrumbs → article-head (рубрика, дата, автор) → cover → toc
→ prose → cta-inline → related
```

## 6. Опции темы

Значения, которые встречаются на всех страницах. Вынести в страницу настроек ACF (`acf_add_options_page`), а не хардкодить в шаблонах.

| Поле | Значение сейчас |
|---|---|
| `opt_phone_main` | `+7 (993) 891-40-64` → `tel:+79938914064` |
| `opt_phone_partners` | `+7 (980) 691-40-64` → `tel:+79806914064` |
| `opt_email` | `sk-espada@rambler.ru` |
| `opt_address` | Москва, ул. Дегунинская, д. 1, корп. 2 |
| `opt_hours` | Ежедневно, 9:00 – 21:00 |
| `opt_map_yandex` | `https://yandex.ru/maps/-/CLgmeD3e` |
| `opt_map_2gis` | `https://go.2gis.com/JknLA` |
| `opt_social` | Telegram, ВКонтакте, Дзен |
| `opt_legal_name` | ИП Ланин Кирилл Андреевич |
| `opt_inn` | 772142258108 |
| `opt_ogrnip` | 324774600528604 |
| `opt_hh_url` | `https://hh.ru/employer/12458493` |

Телефон вставлять только через хелпер `espada_phone_link()` — он гарантирует правильный формат `href` без пробелов.

## 7. Что переиспользуется чаще всего

Собрать один раз и вызывать везде:

| Часть | Где встречается |
|---|---|
| `section/cta.php` | все шаблоны, кроме 404 и юридических |
| `section/contacts.php` | пиллар, главная, о компании, контакты, партнёрам |
| `section/quiz.php` | пиллар, категория |
| `section/faq.php` | пиллар, категория, главная, FAQ |
| `section/reviews.php` | пиллар, главная, отзывы |
| `section/partners.php` | главная, дизайн, комплектация |
| `section/works.php` | пиллар, категория, главная, ЖК |
| `card/work.php` | портфолио, пиллар, категория, главная, ЖК |
| `form/modal.php` | все страницы с кнопками захвата |

Если часть вызывается больше трёх раз — у неё должны быть аргументы через `get_template_part($slug, null, $args)`, а не копия файла с правкой.

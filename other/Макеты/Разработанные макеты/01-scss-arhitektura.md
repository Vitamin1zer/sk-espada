# 01. Архитектура SCSS

## 1. Структура папок

Схема 7-1, адаптированная под проект. Один файл — один блок.

```
scss/
├── main.scss                  единственная точка входа, объявляет слои и порядок
├── abstracts/                 ничего не компилирует, только определения
│   ├── _index.scss            @forward всех абстракций одной строкой
│   ├── _tokens.scss           SCSS-переменные + генерация CSS custom properties
│   ├── _breakpoints.scss      карта брейкпоинтов и миксин mq()
│   ├── _mixins.scss           контейнер, секция, типографика, состояния
│   └── _functions.scss        rem(), z(), fluid()
├── vendor/
│   ├── _mdb-variables.scss    переопределение переменных MDB5 ДО его импорта
│   └── _mdb-reset.scss        гашение того, что MDB5 навязывает
├── base/
│   ├── _fonts.scss            @font-face TildaSans
│   ├── _reset.scss            минимальный сброс
│   ├── _typography.scss       h1–h6, p, ul, теги контента из WYSIWYG
│   └── _links.scss            a, a:hover, a:focus-visible
├── layout/
│   ├── _container.scss        .container-espada
│   ├── _section.scss          .section, .section--gray
│   ├── _header.scss           шапка, утилитарная строка, мега-меню
│   ├── _footer.scss           подвал
│   └── _breadcrumbs.scss      хлебные крошки
├── components/
│   ├── _button.scss           .btn-espada и модификаторы
│   ├── _form.scss             поля, чекбокс согласия, состояния ошибки
│   ├── _card-tariff.scss      карточка тарифа
│   ├── _card-work.scss        карточка объекта портфолио
│   ├── _card-cluster.scss     карточка группы ссылок в пилларе
│   ├── _chip.scss             чип-ссылка кластера
│   ├── _dropdown-filter.scss  фильтр портфолио
│   ├── _accordion.scss        FAQ и мобильное меню
│   ├── _steps.scss            этапы работ с анимацией наведения
│   ├── _quiz.scss             квиз-калькулятор
│   ├── _review.scss           карточка отзыва
│   ├── _seo-text.scss         SEO-блок с раскрытием
│   └── _modal.scss            попап заявки
├── pages/
│   ├── _home.scss             только то, что нигде больше не встречается
│   ├── _pillar.scss
│   ├── _category.scss
│   ├── _portfolio.scss
│   ├── _blog.scss
│   └── _service.scss          404, спасибо, юридические
└── utilities/
    └── _helpers.scss          .visually-hidden, .no-scroll, .text-brand
```

**Правило отнесения.** Стиль идёт в `components/`, если встречается больше чем на одной странице. В `pages/` — только уникальное для одного шаблона. Если файл в `pages/` перевалил за 100 строк, скорее всего внутри спрятался компонент.

## 2. Слои каскада

Объявление порядка — первая строка `main.scss`. Дальше порядок объявления слоёв важнее специфичности: любое правило в `components` перебьёт любое правило в `vendor`, даже если у вендора селектор длиннее.

```scss
@layer reset, vendor, base, layout, components, pages, utilities;
```

Что это даёт на практике: MDB5 задаёт `.btn { border-radius: .25rem }` с высокой специфичностью. Наш `.btn-espada { border-radius: 0 }` в слое `components` выигрывает без `!important` и без утяжеления селектора.

**Важно:** слой объявляется через `@layer имя { ... }` в каждом файле, который в него пишет. Не полагайтесь на то, что сборщик обернёт автоматически.

## 3. Порядок импортов в main.scss

Порядок критичен из-за MDB5: его переменные должны быть переопределены **до** его собственного импорта, иначе он скомпилируется со значениями по умолчанию.

```scss
// 1. Объявление слоёв — раньше любого кода
@layer reset, vendor, base, layout, components, pages, utilities;

// 2. Абстракции: только определения, ничего не выводят
@use 'abstracts' as *;

// 3. Переопределение переменных MDB5 — ДО его импорта
@use 'vendor/mdb-variables' as mdb-vars;

// 4. Сам MDB5, частично, в слой vendor
@layer vendor {
  @use 'mdb-ui-kit/src/scss/free' with (
    $primary:        #00AD9F,
    $border-radius:  0,
    $font-family-sans-serif: ('TildaSans', 'Helvetica Neue', Helvetica, sans-serif),
    $enable-shadows: false,
    $enable-gradients: false
  );
  @use 'vendor/mdb-reset';
}

// 5. Наши слои
@layer reset      { @use 'base/reset'; }
@layer base       { @use 'base/fonts'; @use 'base/typography'; @use 'base/links'; }
@layer layout     { @use 'layout/container'; @use 'layout/section'; @use 'layout/header';
                    @use 'layout/footer';   @use 'layout/breadcrumbs'; }
@layer components { @use 'components/button'; @use 'components/form'; /* … */ }
@layer pages      { @use 'pages/home'; /* … */ }
@layer utilities  { @use 'utilities/helpers'; }
```

Если MDB5 подключается собранным CSS-файлом, а не через SCSS-исходники — обернуть импорт слоем в самом CSS: `@import url('mdb.min.css') layer(vendor);` Тогда переопределение переменных недоступно, и придётся перекрывать классами; это хуже, но работает.

## 4. Именование

**BEM с дефисным разделителем, префикс для собственных блоков.**

```
.espada-header
.espada-header__nav
.espada-header__nav-item
.espada-header--sticky
.espada-header__nav-item--active
```

Зачем префикс: MDB5 занимает `.btn`, `.card`, `.navbar`, `.form-control`, `.dropdown`, `.accordion`, `.modal` — то есть почти все имена, которые захочется взять. Префикс снимает коллизии навсегда и делает очевидным на ревью, чей это класс.

Исключения, где префикс не нужен:
- Утилиты: `.visually-hidden`, `.no-scroll`.
- Классы, которые мы отдаём MDB5 сознательно, чтобы работал его JS: `.modal`, `.collapse`, `.dropdown-toggle` — они остаются как есть, стилизуются через наш блок-обёртку.

**Состояния** — через `is-` / `has-`, если ставятся из JS: `.is-open`, `.is-loading`, `.has-error`. Модификаторы через `--` — если задаются в шаблоне на этапе рендера.

## 5. Токены: SCSS-переменные и CSS custom properties

Держим оба слоя, у каждого своя работа.

- **SCSS-переменные** — для вычислений в компиляции: `math.div`, `map.get`, миксины, брейкпоинты. То, что не нужно менять в рантайме.
- **CSS custom properties** — для того, что может понадобиться переопределить в рантайме или на уровне секции: цвета темы, отступы контейнера. Генерируются один раз из SCSS-карты в `:root`.

```scss
// abstracts/_tokens.scss
$c-brand: #00AD9F;
$c-brand-dark: #026B63;

$colors: (
  'brand':      $c-brand,
  'brand-dark': $c-brand-dark,
  // …
);

:root {
  @each $name, $value in $colors {
    --c-#{$name}: #{$value};
  }
}
```

В компонентах используем `var(--c-brand)`, а не `$c-brand`, везде, где значение может понадобиться перекрыть. В `@media` и миксинах — SCSS-переменную, потому что `var()` в медиазапросах не работает.

Полный список токенов — `04-tokeny.md`.

## 6. Требования к сборке

- **Dart Sass**, API `@use`/`@forward`. `node-sass` мёртв, `@import` в Dart Sass объявлен устаревшим и будет удалён.
- **Autoprefixer** с `browserslist`: `> 0.5%, last 2 versions, not dead, not op_mini all`. Отдельно проверить Safari iOS 15 — там частичная поддержка `@layer`, но она есть; контейнерные запросы, если решите их сохранить, требуют Safari 16.
- **Выход:** один `main.css` для фронта. Критический CSS первого экрана — опционально, вторым проходом, не в первую итерацию.
- **Sourcemaps** в dev, минификация в prod, `cssnano` без агрессивных оптимизаций (`reduceIdents: false`, чтобы не поломало имена анимаций).
- **Stylelint** обязателен, конфиг:

```json
{
  "extends": ["stylelint-config-standard-scss"],
  "rules": {
    "declaration-no-important": true,
    "max-nesting-depth": 3,
    "selector-max-compound-selectors": 3,
    "color-no-hex": [true, { "message": "Только токены: var(--c-*) или $c-*" }],
    "scss/at-rule-no-unknown": [true, { "ignoreAtRules": ["layer", "use", "forward", "container"] }]
  },
  "overrides": [
    { "files": ["scss/abstracts/_tokens.scss", "scss/vendor/*.scss"], "rules": { "color-no-hex": null } }
  ]
}
```

Правило `color-no-hex` — не придирка. Оно единственное, что реально удерживает палитру в трёх цветах вместо расползания до двадцати оттенков бирюзового.

- **JS** — нативные ES-модули, по одному на компонент: `header.js`, `quiz.js`, `filters.js`, `forms.js`, `accordion.js`. jQuery не нужен: MDB5 в версии 5 от него не зависит. Если понадобится его JS-компонент — импортируйте точечно (`import { Modal } from 'mdb-ui-kit'`), не бандл целиком.

## 7. Что делать с контейнерными запросами из макетов

Макеты используют `container-type: inline-size` и единицы `cqw`, потому что дизайнеру нужно было показывать десктоп и мобильный в одном файле рядом.

**В теме есть два пути, выберите один и держитесь его:**

**Путь А, рекомендуемый — оставить контейнерные запросы.** Корневой блок шаблона получает `container-type: inline-size`, значения `cqw` переносятся как есть. Плюс: адаптив работает от ширины блока, а не окна — компонент в сайдбаре автоматически ведёт себя правильно. Минус: Safari младше 16 не поддерживает, нужен фолбэк через `@supports not (container-type: inline-size)` с обычными медиазапросами.

**Путь Б — перевести на fluid-типографику от вьюпорта.** `clamp(min, Xvw, max)` вместо `clamp(min, Xcqw, max)`. Правило пересчёта: контейнер контента равен 1200 px при вьюпорте 1440, то есть `1cqw ≈ 0.833vw`. Пример: `clamp(21px, 2.3cqw, 32px)` → `clamp(21px, 1.92vw, 32px)`. Плюс: поддержка везде. Минус: компонент не знает, в каком контейнере стоит.

По умолчанию берите путь Б — он проще в отладке и не требует фолбэков, а гибкость контейнерных запросов на этом проекте не понадобится: компоненты живут в одной колонке фиксированной ширины.

## 8. Порядок написания компонента

Чтобы код был предсказуемым для ревью, внутри блока порядок такой:

```scss
@layer components {
  .espada-card-tariff {
    // 1. Локальные custom properties блока
    --card-pad: #{$sp-4};

    // 2. Раскладка: display, grid/flex, position, размеры
    display: flex;
    flex-direction: column;

    // 3. Оформление: фон, рамка, тень, радиус
    background: var(--c-brand);
    border-radius: $radius-card;

    // 4. Типографика
    color: #fff;

    // 5. Переходы
    transition: box-shadow $dur-base $ease-base;

    // 6. Элементы
    &__title { /* … */ }
    &__price { /* … */ }

    // 7. Модификаторы
    &--featured { /* … */ }

    // 8. Состояния и медиазапросы
    &:hover { /* … */ }
    @include mq(md) { --card-pad: #{$sp-3}; }
  }
}
```

Первым идёт мобильный стиль, медиазапросы наращивают десктоп (mobile-first). Миксин `mq()` работает только вверх — `min-width`. Обратные запросы `max-width` не использовать, они ломают линейность каскада.

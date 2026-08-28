# -*- coding: utf-8 -*-
"""
Шаг 6б. Отбор по профилю клиента.

Стоп-листами 55 тысяч фраз не вычистить: среди доноров многопрофильные сайты,
и они приносят весь свой ассортимент. Надёжнее фильтр «от обратного» —
оставляем то, что относится к направлениям Эспады, остальное уходит
на лист «На разбор», а не в корзину.

Направления взяты из брифа клиента: ремонт квартир под ключ, дизайн интерьера,
приёмка квартир, комплектация, перепланировка.
"""
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAT = os.path.join(PROJ, 'материалы')

KV = r'(?:квартир\w*|новостройк\w*|вторичк\w*|студи\w*|комнатн\w*|апартамент\w*|жк\b|жилом\w*\s+комплекс\w*)'

POMESHCHENIYA = (r'(?:кухн\w*|ванн\w*|санузл\w*|сануз\w*|туалет\w*|спальн\w*|'
                 r'гостин\w*|детск\w*|прихож\w*|коридор\w*|балкон\w*|лоджи\w*|'
                 r'гардеробн\w*|кабинет\w*)')

STILI = (r'(?:лофт\w*|сканди\w*|скандинавск\w*|минимализм\w*|хай[\s-]?тек\w*|'
         r'неокласс\w*|классическ\w*|прованс\w*|джапанди|эклектик\w*|'
         r'модерн\w*|ар[\s-]деко|бохо|контемпорари|фьюжн)')

# Направление -> правило. Порядок важен: узкие раньше широких.
NAPRAVLENIYA = [
    ('Приёмка',        re.compile(r'при[её]мк\w*|при[её]мщик\w*|прием\s+квартир', re.I)),
    ('Комплектация',   re.compile(r'комплектац\w*|комплектатор\w*', re.I)),
    ('Перепланировка', re.compile(r'перепланировк\w*|узакон\w*\s+переплан|согласован\w*\s+переплан', re.I)),
    # отдельные услуги — нашлись при разборе листа «На разбор»
    ('Отдельные услуги', re.compile(
        r'механизированн\w*\s+штукатурк\w*|штукатурк\w*\s+механизированн\w*|'
        r'машинн\w*\s+штукатурк\w*|стяжк\w*\s+пола|полусух\w*\s+стяжк\w*|'
        r'электромонтаж\w*|разводк\w*\s+(?:электр|труб)|'
        r'сантехническ\w*\s+работ\w*|монтаж\w*\s+сантехник\w*|'
        r'демонтажн\w*\s+работ\w*|шумоизоляц\w*|звукоизоляц\w*|'
        r'натяжн\w*\s+потолк\w*|укладк\w*\s+плитк\w*|поклейк\w*\s+обо\w*|'
        r'малярн\w*\s+работ\w*|выравниван\w*\s+стен', re.I)),
    ('Дизайн',         re.compile(r'дизайн[\w-]*\s*(?:интерьер\w*|проект\w*)|'
                                  r'дизайн[\w-]*\s+' + KV + r'|'
                                  r'дизайн[\w-]*\s+' + POMESHCHENIYA + r'|'
                                  + POMESHCHENIYA + r'\s+дизайн|'
                                  r'дизайнер\w*\s+интерьер|интерьер\w*\s+дизайн|'
                                  r'интерьер\w*\s+в\s+стиле|' + STILI + r'\s+(?:интерьер|дизайн)|'
                                  r'(?:интерьер|дизайн)\w*\s+' + STILI, re.I)),
    ('Ремонт помещений', re.compile(r'(?:ремонт\w*|отделк\w*)\s+(?:в\s+)?' + POMESHCHENIYA + r'|'
                                    + POMESHCHENIYA + r'\s+(?:ремонт\w*|отделк\w*)', re.I)),
    ('Ремонт квартир', re.compile(r'(?:ремонт\w*|отделк\w*|отдела\w*)[\w\s]{0,30}?' + KV + r'|'
                                  + KV + r'[\w\s]{0,30}?(?:ремонт\w*|отделк\w*)|'
                                  r'ремонт\w*\s+под\s+ключ|под\s+ключ\s+ремонт|'
                                  r'евроремонт\w*|ремонтно[\s-]отделочн\w*|'
                                  r'ремонт\s+и\s+отделк\w*|отделк\w*\s+и\s+ремонт|'
                                  r'ремонт\w*\s+помещен\w*|отделк\w*\s+помещен\w*', re.I)),
]

# Явно чужой профиль: строим не там и не то
NE_NASH = re.compile(
    r'ремонт\w*\s+(?:дом\w*|коттедж\w*|дач\w*|таунхаус\w*|бани|гаража|склад\w*|'
    r'магазин\w*|кафе|ресторан\w*|салон\w*|подъезд\w*|фасад\w*|кровл\w*|'
    r'цех\w*|производств\w*|котельн\w*)|'
    r'строительств\w*\s+(?:дом\w*|коттедж\w*|бани)|'
    r'\bсруб\w*|\bкаркасн\w+\s+дом|\bфундамент\w*\s+(?:дом|под\s+дом)|'
    r'ландшафтн\w*|\bкровельн\w*|\bзабор\w*|\bсептик\w*|\bскважин\w*',
    re.I)


def main():
    kom = json.load(open(os.path.join(MAT, 'ядро_коммерч.json'), encoding='utf-8'))
    info = json.load(open(os.path.join(MAT, 'ядро_инфо.json'), encoding='utf-8'))
    print('коммерческих на входе: %d, информационных: %d' % (len(kom), len(info)))

    otobrano, na_razbor, ne_nash = {}, {}, {}
    by_dir = collections.Counter()

    for w, p in kom.items():
        if NE_NASH.search(w):
            ne_nash[w] = dict(p, reason='чужой профиль (не квартиры)')
            continue
        d = None
        for name, pat in NAPRAVLENIYA:
            if pat.search(w):
                d = name
                break
        if d:
            otobrano[w] = dict(p, napravlenie=d)
            by_dir[d] += 1
        else:
            na_razbor[w] = p

    # информационные тоже отбираем по профилю — для блога
    info_ok, info_razbor = {}, {}
    for w, p in info.items():
        if NE_NASH.search(w):
            continue
        if any(pat.search(w) for _, pat in NAPRAVLENIYA):
            info_ok[w] = p
        else:
            info_razbor[w] = p

    json.dump(otobrano, open(os.path.join(MAT, 'ядро_профиль.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump(na_razbor, open(os.path.join(MAT, 'ядро_на_разбор.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump(ne_nash, open(os.path.join(MAT, 'ядро_чужой_профиль.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump(info_ok, open(os.path.join(MAT, 'ядро_инфо_профиль.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    print('\nотобрано по профилю:  %d' % len(otobrano))
    print('чужой профиль:        %d' % len(ne_nash))
    print('на разбор:            %d' % len(na_razbor))
    print('сходимость: %d + %d + %d = %d из %d — %s'
          % (len(otobrano), len(ne_nash), len(na_razbor),
             len(otobrano) + len(ne_nash) + len(na_razbor), len(kom),
             'ок' if len(otobrano) + len(ne_nash) + len(na_razbor) == len(kom) else 'РАСХОЖДЕНИЕ'))

    print('\n=== по направлениям ===')
    for d, n in by_dir.most_common():
        print('  %-18s %d' % (d, n))

    print('\nинформационных по профилю (в блог): %d, вне профиля: %d'
          % (len(info_ok), len(info_razbor)))

    print('\n=== ЛИСТ «НА РАЗБОР», верх по общероссийской частоте ===')
    print('(разбирать обязательно: тут прячутся направления, которых нет ни у нас, ни у конкурентов)')
    top = sorted(na_razbor.items(), key=lambda kv: -kv[1].get('wsk', 0))[:35]
    for w, p in top:
        print('  %-62s %s' % (w[:62], p.get('wsk', 0)))


main()

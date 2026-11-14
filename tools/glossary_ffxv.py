"""Слой 2 глоссария: официальные русские термины FINAL FANTASY XV (из файлов игры, FFXV_dict).
Применяется поверх всех правок (кроме 90_normalize). Пишет edits/70_ffxv.json.
python -I tools/glossary_ffxv.py [show]
"""
import json, re, sys, glob
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8'))
base = json.load(open('ru/ru.json', encoding='utf-8'))
cur = dict(base)
for f in sorted(glob.glob('edits/*.json')):
    if not re.search(r'(70_ffxv|90_normalize)', f):
        cur.update(json.load(open(f, encoding='utf-8')))
ns = lambda k: k.split('␟')[0]
NAME_NS = ('ST_SkillName', 'ST_CommandSkillName', 'ST_PassiveSkillName', 'ST_ConsumablesName', 'ST_EquipmentName',
           'ST_UnitName', 'ST_CharaName', 'ST_ValuableName', 'ST_VisionName', 'ST_MasterSkillName')
DLG = lambda k: not (ns(k) in NAME_NS or 'Description' in ns(k) or 'Trait' in ns(k) or ns(k).startswith(('ST_UI', 'ST_Btl')))

# Точные названия (EN -> офиц. FFXV)
NAMES = {
    'Hi-Potion': 'Ультразелье', 'Mist Hi-Potion': 'Ультразелье тумана', 'X-Potion': 'Зелье-X', 'Mist X-Potion': 'Зелье-X тумана',
    'Megalixir': 'Мегаликсир', 'Fuma Shuriken': 'Фума-сюрикен',
    'Doom': 'Погибель', 'Libra': 'Сканирование', 'Meteor': 'Метеорит', 'Flare': 'Запредельный огонь',
    'Dualcast': 'Двойные чары', 'Zantetsuken': 'Зантецукен', 'Deathblow': 'Смертельный удар',
    'Warp-Strike': 'Атакующий телепорт', 'Armiger Unleashed': 'Пробуждение Оруженосца',
    'Bahamut': 'Багамут', 'Sahagin': 'Сахуагин',
    'Adamantoise': 'Адамантуаз', 'Coeurl': 'Кёрл', 'Gigantoad': 'Гигантожаба', 'Gigantuar': 'Гигантюар',
    'Malbodoom': 'Мальбодум', 'Master Tonberry': 'Тонберри-мастер', 'Mindflayer': 'Иллитид', 'Treant': 'Энт',
    'Wyvern': 'Виверн', 'Headband': 'Бандана', 'Jeweled Ring': 'Кольцо с самоцветами', 'War Hammer': 'Клевец',
}
# Ступени заклинаний как в FFXV: «Огонь-2», «Лёд-3»; Blizzard = «Лёд»
TIER = [(r'\bМетель\b', 'Лёд'), (r'\b(Огонь|Лёд|Гром|Лечение|Вода|Камень|Тьма|Аэро|Изгнание|Гравитация) III\b', r'\1-3'),
        (r'\b(Огонь|Лёд|Гром|Лечение|Вода|Камень|Тьма|Аэро|Изгнание|Гравитация) II\b', r'\1-2')]
# По всему тексту (включая диалоги): словоформы
WORDS = [
    (r'Бахамут(а|у|ом|е)?\b', lambda m: 'Багамут' + (m.group(1) or '')),
    (r'([Зз])ель(е|я|ю|ем)\+', lambda m: ('У' if m.group(1) == 'З' else 'у') + 'льтразель' + m.group(2)),
    (r'X-зель(е|я|ю|ем)', lambda m: 'зель' + m.group(1) + '-X'),
    (r'[Мм]егаэликсир', lambda m: m.group(0)[0] + 'егаликсир'),
    (r'Адамантов(ая|ой|ую) черепах(а|и|у|ой)', lambda m: 'адамантуаз' if m.group(2) in 'ау' else ('адамантуаза' if m.group(2) == 'и' else 'адамантуазом')),
    (r'Свежевател(ь|я|ю|ем) разума', lambda m: 'Иллитид' + {'ь': '', 'я': 'а', 'ю': 'у', 'ем': 'ом'}[m.group(1)]),
    (r'Дзантэцукэн', 'Зантецукен'),
    (r'«Рок(а|у|ом)?»', lambda m: '«Погибел' + {None: 'ь', 'а': 'и', 'у': 'ь', 'ом': 'ью'}[m.group(1)] + '»'),
    (r'«Анализ»', '«Сканирование»'),
    # Магитех — как в FFXV: «магитех-» через дефис
    (r'([Мм])агитехническ\w+ (\w+)', r'\1агитех-\2'),
    (r'([Мм])агитехов\w+ воздушн(\w+) (\w+)', lambda m: ('В' if m.group(1) == 'М' else 'в') + 'оздушн' + m.group(2) + ' магитех-' + m.group(3)),
    # Обозначения интерфейса как в официальной FFXV
    (r'(?<![A-Za-z{])HP(?![A-Za-z}])', 'ОЗ'), (r'(?<![A-Za-z{])MP(?![A-Za-z}])', 'ОМ'),
    (r'низком (ОЗ|ОМ)\b', r'низких \1'), (r'низкое (ОЗ|ОМ)\b', r'низкие \1'), (r'максимального (ОЗ|ОМ)\b', r'максимальных \1'),
    (r'текущее (ОЗ|ОМ)\b', r'текущие \1'), (r'собственное (ОЗ|ОМ)\b', r'собственные \1'), (r'оставшегося (ОЗ|ОМ)\b', r'оставшихся \1'),
    (r'^(\s*)EXP$', r'\1ОПЫТ'), (r'(много|мало|Подавитель|Получено) EXP\b', r'\1 опыта'), (r'Удвоенный EXP', 'Двойной опыт'), (r'(?<![A-Za-z{])EXP(?![A-Za-z}])', 'опыт'),
]
base_key = lambda k: re.sub(r'_(det_)?(sg|pl)$', '', k)
out = {}
for k in cur:
    r = cur[k]; new = r
    if ns(k) in NAME_NS:
        be = en.get(base_key(k), '').strip()
        if be in NAMES:
            nm = NAMES[be]
            new = nm if k == base_key(k) else ('шт. «' + nm + '»' if k.endswith('_pl') else '«' + nm + '»')
    if not DLG(k) or re.search(r'«[^»]*\b(Метель|II|III)\b[^»]*»', new):
        for a, b in TIER:
            if DLG(k):  # в диалогах — только внутри «»
                new = re.sub(r'«[^»]*»', lambda m: re.sub(a, b, m.group(0)), new)
            else:
                new = re.sub(a, b, new)
    for a, b in WORDS:
        new = re.sub(a, b, new)
    # «Зелье-X»/«Ультразелье» с заглавной в начале предложения/кавычек
    new = re.sub(r'(^|[.!?…]\s+|«|: )зель(е|я|ю|ем)-X', lambda m: m.group(1) + 'Зель' + m.group(2) + '-X', new)
    if new != r:
        out[k] = new
json.dump(out, open('edits/70_ffxv.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('изменено строк:', len(out))
if len(sys.argv) > 1:
    for k, v in out.items():
        print(ns(k)[3:22], '|', cur[k][:80].replace('\r\n', ' '), '=>', v[:80].replace('\r\n', ' '))

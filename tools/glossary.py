"""Глоссарий: приводит названия заклинаний, статусов и предметов к привычным для серии FF.

Пишет edits/10_glossary.json (ключ -> новый текст). Правила привязаны к EN/JA-оригиналу
строки, чтобы не задеть одноимённые характеристики (Physical Defense и т.п.).
python -I tools/glossary.py
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
ns = lambda k: k.split('␟')[0]
NAME_NS = ('ST_SkillName', 'ST_CommandSkillName', 'ST_PassiveSkillName', 'ST_ConsumablesName',
           'ST_EquipmentName', 'ST_ValuableName', 'ST_MasterSkillName', 'ST_VisionName', 'ST_ArtifactName')
NONDLG = NAME_NS + ('ST_SkillDescription', 'ST_PassiveSkillDescription', 'ST_EquipmentDescription',
                    'ST_ConsumablesDescription', 'ST_CommandSkillDescription', 'ST_MasterSkillDescription',
                    'ST_VisionDescription', 'ST_UnitTrait01', 'ST_UnitTrait02', 'ST_UnitTrait03', 'ST_UnitTrait04',
                    'ST_BtlCommon', 'ST_BtlAI', 'ST_UI_Word', 'ST_UI_Libra', 'ST_ArtifactDescription',
                    'ST_ValuableDescription', 'ST_UI_Guide', 'ST_UnitDescription')
is_dlg = lambda k: ns(k) not in NONDLG and not ns(k).startswith('ST_UI')

# 1. Точные названия (базовая форма названия). EN -> RU
NAMES = {
    'Thunder': 'Гром', 'Thundara': 'Гром II', 'Thundaga': 'Гром III',
    'Blizzard': 'Метель', 'Blizzara': 'Метель II', 'Blizzaga': 'Метель III',
    'Aero': 'Аэро', 'Aerora': 'Аэро II', 'Aeroga': 'Аэро III',
    'Banish': 'Изгнание', 'Banishra': 'Изгнание II', 'Banishga': 'Изгнание III',
    'Esuna': 'Эсуна', 'Esunaga': 'Эсунага',
    'Protect': 'Защита', 'Protectga': 'Массовая защита',
    'Shell': 'Панцирь', 'Shellga': 'Массовый панцирь',
    'Deprotect': 'Пробой защиты', 'Deprotega': 'Массовый пробой защиты',
    'Deshell': 'Пробой панциря', 'Deshellga': 'Массовый пробой панциря',
    'Debrave': 'Трусость', 'Debravega': 'Массовая трусость',
    'Defaith': 'Неверие', 'Defaithga': 'Массовое неверие',
    'Silence': 'Немота', 'Silencega': 'Массовая немота',
    'Confuse': 'Смятение', 'Confusega': 'Массовое смятение',
    'Blind': 'Слепота', 'Blindga': 'Массовая слепота',
    'Poison': 'Яд', 'Poisonga': 'Массовый яд',
    'Bio': 'Био', 'Holy': 'Святость', 'Flash': 'Блик',
    'Guard': 'Блок', 'Defend': 'Оборона', 'Carapace': 'Хитиновый покров',
    'Phoenix Down': 'Пух феникса', 'Phoenix Pinion': 'Перо феникса',
    'Hi-Potion': 'Зелье+', 'Mist Hi-Potion': 'Зелье+ тумана',
    'Knife of Confuse': 'Нож смятения', 'Throwing Knife of Confuse': 'Метательный нож смятения',
    'Knife of Blind': 'Нож слепоты', 'Throwing Knife of Blind': 'Метательный нож слепоты',
    'Add Slow': 'Замедление при ударе', 'Add Deshell': 'Пробой панциря при ударе',
    'Add Deprotect': 'Пробой защиты при ударе', 'Add Instant Death': 'Мгновенная смерть при ударе',
    'Add Blind': 'Слепота при ударе', 'Add Poison': 'Яд при ударе', 'Add Silence': 'Немота при ударе',
    'Add Confuse': 'Смятение при ударе', 'Add Sleep': 'Сон при ударе',
    'Auto-Shell': 'Постоянный панцирь', 'Auto-Protect': 'Постоянная защита',
    'Shell Opener': 'Панцирь в начале боя', 'Protect Opener': 'Защита в начале боя',
    'Deshell Opener': 'Пробой панциря в начале боя', 'Deprotect Opener': 'Пробой защиты в начале боя',
    'Nullify Silence': 'Иммунитет к немоте', 'Nullify Confuse': 'Иммунитет к смятению',
    'Nullify Blind': 'Иммунитет к слепоте',
    'Shell on Stagger': 'Панцирь при пробитии', 'Protect on Stagger': 'Защита при пробитии',
    'Shell and Protect on Stagger': 'Панцирь и защита при пробитии',
    'Deshell on Stagger': 'Пробой панциря при пробитии', 'Deprotect on Stagger': 'Пробой защиты при пробитии',
    'Shell at Half HP': 'Панцирь при низких HP', 'Protect at Half HP': 'Защита при низких HP',
}

# 2. Замены внутри названий/описаний, только если в оригинале есть термин.
#    (регэксп по EN/JA, [(регэксп по RU, замена)])
SUBS = [
    (r'\bProtect\b|プロテ', [(r'«Физическ(ая|ую|ой) защит(а|у|ы|ой)»', lambda m: '«Защит' + {'а': 'а', 'у': 'у', 'ы': 'ы', 'ой': 'ой'}[m.group(2)] + '»')]),
    (r'\bShell\b|シェル', [(r'«Магическ(ая|ую|ой) защит(а|у|ы|ой)»', lambda m: '«Панцир' + {'а': 'ь', 'у': 'ь', 'ы': 'я', 'ой': 'ем'}[m.group(2)] + '»')]),
    (r'\bDeshell\b|デシェル', [(r'«Ослаблени(е|я) магической защиты»', lambda m: '«Пробой панциря»' if m.group(1) == 'е' else '«Пробоя панциря»')]),
    (r'\bDeprotect\b|デプロテ', [(r'«Ослаблени(е|я) физической защиты»', lambda m: '«Пробой защиты»' if m.group(1) == 'е' else '«Пробоя защиты»')]),
    (r'\bConfuse\b|混乱', [(r'([Зз])амешательств(о|а|у|ом|е)\b', lambda m: ('С' if m.group(1) == 'З' else 'с') + 'мятени' + {'о': 'е', 'а': 'я', 'у': 'ю', 'ом': 'ем', 'е': 'и'}[m.group(2)])]),
    (r'\bSilence\b|沈黙', [(r'([МмБб])(?:олчани|езмолви)(е|я|ю|ем|и)\b', lambda m: ('Н' if m.group(1).isupper() else 'н') + 'емот' + {'е': 'а' if m.group(1).isupper() else 'у', 'я': 'ы', 'ю': 'е', 'ем': 'ой', 'и': 'е'}[m.group(2)])]),
    (r'\bBlind\b|暗闇|ブライン', [(r'([Оо])слеплени(е|я|ю|ем|и)\b', lambda m: ('С' if m.group(1) == 'О' else 'с') + 'лепот' + {'е': 'а' if m.group(1) == 'О' else 'у', 'я': 'ы', 'ю': 'е', 'ем': 'ой', 'и': 'е'}[m.group(2)])]),
    (r'\bEsuna\b|エスナ', [(r'«Очищение»', '«Эсуна»'), (r'«Очищением»', '«Эсуной»'), (r'«Очищения»', '«Эсуны»')]),
    (r'\bThund', [(r'Молния( I{1,3})?(?= Седьмой)', lambda m: 'Гром' + (m.group(1) or ''))]),
    (r'\bBlizz', [(r'Лёд( I{1,3})?(?= Седьмой)', lambda m: 'Метель' + (m.group(1) or ''))]),
    (r'\bAero', [(r'Ветер( I{1,3})?(?= Седьмой)', lambda m: 'Аэро' + (m.group(1) or ''))]),
]
# Для всех строк, включая диалоги: предметы.
GLOBAL = [
    (r'[Мм]аховое перо феникса', 'Перо феникса'),
    (r'([Пп])ер(о|а|ом|у) феникса', lambda m: ('П' if m.group(1) == 'П' else 'п') + 'ух' + {'о': '', 'а': 'а', 'ом': 'ом', 'у': 'у'}[m.group(2)] + ' феникса'),
    (r'([Сс])ильн(ое|ого|ым|ому) зель(е|я|ем|ю)', lambda m: ('З' if m.group(1) == 'С' else 'з') + 'ель' + m.group(3) + '+'),
]

base_key = lambda k: re.sub(r'_(det_)?(sg|pl)$', '', k)
out = {}
for k in en:
    e = en[k].strip(); r = ru[k]; new = r
    n = ns(k)
    if n in NAME_NS:
        b = base_key(k)
        be = en.get(b, '').strip()
        if be in NAMES:
            nm = NAMES[be]
            if k == b: new = nm
            elif k.endswith('_pl'): new = 'шт. «' + nm + '»'
            else: new = '«' + nm + '»'
    if not is_dlg(k) and new == r:
        for epat, rules in SUBS:
            if re.search(epat, en[k]):
                for rp, rep in rules:
                    new = re.sub(rp, rep, new)
    # GLOBAL: «Перо феникса» как новое имя Phoenix Pinion не трогаем повторно
    if not (n in NAME_NS and en.get(base_key(k), '').strip() in NAMES):
        tmp = new.replace('Маховое перо феникса', '\0PINION\0').replace('маховое перо феникса', '\0pinion\0')
        for rp, rep in GLOBAL[1:]:
            tmp = re.sub(rp, rep, tmp)
        new = tmp.replace('\0PINION\0', 'Перо феникса').replace('\0pinion\0', 'перо феникса')
    new = re.sub(r'([Сс]) (слепот|смятени)', r'о ', new)
    if new != r:
        out[k] = new

import os
os.makedirs('edits', exist_ok=True)
json.dump(out, open('edits/10_glossary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('изменено строк:', len(out))
for k in list(out)[:0]: pass
if len(sys.argv) > 1:
    for k, v in out.items():
        print(ns(k)[3:20], '|', ru[k][:90].replace('\r\n', ' '), '=>', v[:90].replace('\r\n', ' '))

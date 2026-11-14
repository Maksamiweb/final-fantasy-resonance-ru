"""Словарь надписей на скриншотах справки: англ. -> русский (из текста игры, где есть; иначе вручную)."""
import json, glob, re
_en = json.load(open('orig/en.json', encoding='utf-8')); _ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): _ru.update(json.load(open(f, encoding='utf-8')))
_T = re.compile(r'<[^<>]*>')
_PREF = ['ST_UI_', 'ST_Tutorial', 'ST_CommandSkillName', 'ST_SkillName', 'ST_PassiveSkillName', 'ST_EquipmentName', 'ST_ItemName', 'ST_CharaName', 'ST_UnitName', 'ST_']
def lookup(e):
    ks = [k for k, v in _en.items() if _T.sub('', v).strip() == e and not re.search(r'_(sg|pl|det_sg|det_pl)$', k)]
    ks.sort(key=lambda k: next(i for i, p in enumerate(_PREF) if k.startswith(p)))
    for k in ks:
        r = _T.sub('', _ru.get(k, '')).replace(' ', ' ').strip()
        if r and r != e: return r
    return None
MANUAL = {
 'Poison': 'Яд', 'Silence': 'Немота', 'Blind': 'Слепота', 'Paralysis': 'Паралич', 'Sleep': 'Сон', 'Petrify': 'Окаменение',
 'Berserk': 'Берсерк', 'Confuse': 'Смятение', 'Instant Death': 'Мгновенная смерть', 'Charm': 'Очарование',
 'Regen': 'Регенерация', 'Reflect': 'Отражение', 'Reraise': 'Автовоскрешение', 'Haste': 'Ускорение', 'Slow': 'Замедление',
 'Brave': 'Храбрость', 'Faith': 'Вера', 'Protect': 'Защита', 'Shell': 'Панцирь', 'Debrave': 'Трусость', 'Defaith': 'Неверие',
 'Deprotect': 'Пробой защиты', 'Deshell': 'Пробой панциря', 'Stagger defense down': 'Снижение защиты от пробития',
 'Physical attack': 'Физическая атака', 'Physical defense': 'Физическая защита', 'Magic attack': 'Магическая атака',
 'Magic defense': 'Магическая защита', 'Sanctity': 'Святость', 'Strength': 'Сила', 'Stamina': 'Выносливость', 'Magic': 'Магия',
 'Spirit': 'Дух', 'Speed': 'Скорость', 'AP': 'AP', 'HP': 'ОЗ', 'MP': 'ОМ', 'EXP': 'ОПЫТ', 'OFF': 'ВЫКЛ', 'ON': 'ВКЛ', 'Skills': 'Способности', 'Items': 'Предметы',
 'Leather Armor': 'Кожаные доспехи', 'Earrings of Health': 'Серьги здоровья', 'Crimson Saber': 'Багровый клинок', 'None': 'Нет',
 'Chapter 1 - Tailing the Truth': 'Глава 1: В поисках истины', 'RESONANCE': 'РЕЗОНАНС', 'Next Rank:': 'До ранга:',
 'SAVE': 'СОХРАНЕНИЕ', 'NO DATA': 'НЕТ ДАННЫХ', 'Normal': 'Обычная', 'Time Played': 'Время игры', 'Village of Kol': 'Деревня Кол',
 'Mastery Rank': 'Ранг мастерства', 'STAGGER': 'ПРОБИТИЕ', 'STAGGERED': 'ПРОБИТИЕ', 'Critical': 'Крит', 'Affinity': 'Сопротивления',
 'Lv.': 'Ур.', 'All': 'Все',
}
NAMES = ['Attack', 'Defend', 'Escape', 'Limit Bursts', 'Cancel', 'Hide Tips', 'Show Tips', 'Display Unit Info', 'Affinities', 'Weak',
 'Rain', 'Lasswell', 'Fina', 'Lid', 'Nichol', 'Leah', 'Tronn', 'Warrior of Light', 'Jake', 'Bahamut', 'Siren', 'Belmodar', 'Desert Sahagin', 'Magitek Armor',
 'Main Menu', 'Map', 'Quests', 'Recovery', 'Equipment & Abilities', 'Party', 'System', 'Save Point', 'Save progress', 'Rest in a tent', 'Teleport',
 'Grandshelt Castle', 'Kingdom of Grandshelt', 'Go to the town of Mitra', 'Go to the village of Kol', 'Fast Travel', 'Recommended Level', 'Town of Mitra',
 'Role', 'Attributes', 'Equipment', 'Visions', 'Abilities', 'Equippable', 'Sentinel', 'Breaker', 'Medic', 'Synergist', 'Element',
 'Awakening Level', 'Mastery Bonuses', 'Permanent', 'New', 'Growth', 'Mastery Rank Up!', 'Mastery Rank Up', 'Vision Enhancement', 'Awaken',
 'Magitek Armor Key', 'Magitek Airship Passkey', 'Not equipped', 'Battle Result', 'EXP Gained', 'Gil Obtained', 'MRP Gained', 'Items Obtained',
 'No Damage Bonus', 'Overkill Bonus', 'Stagger Finish Bonus', 'Main Story', 'Sub Quests', 'Goal', 'Rewards', 'Summary', 'Dream of an Idealist',
 'Talk to Scott in the village of Kol', 'Flamberge', 'Phys. Atk.', 'Phys. Def.', 'Mag. Atk.', 'Mag. Def.', 'Next Lv:', 'Formation: Assail', 'Formation: Charge',
 'Formation: Bulwark', 'Tactic: Fluid Warfare', 'Select Resonance', 'Sweeping Stagger', 'Healing Wind', 'Hibernal Fury', 'Infinity Drive', 'Crimson Onslaught',
 'Cure', 'Libra', 'Banish', 'Healing Magic +30%', 'Nullify Charm', 'Cura', 'Shellga', 'Esuna', 'Banishra', 'Magic Defense +20%', 'Nullify Poison',
 'First Aid', 'Pass the Torch', 'Pharmacology', 'Healing Magic +10%', 'Auto-Cure Ailments', 'Vanguard Glaive', 'Thunder Blade', 'Stone Blade',
 'Stagger Power +30%', 'Physical Defense +20%', 'Protectga', 'Stonera Blade', 'Thundara Blade', 'Shell at Half HP', 'Deprotect on Stagger',
 'Crystal Braver', 'Restore MP on Stagger', 'Fill LB on Stagger', 'Spirit of Tronn', 'Focus Magic', 'Half MP Cost', 'Spirit of Leah',
 'Codex Belli', 'Lunar Eclipse Robe', 'Tackle', 'Fire', 'Last Resonance', 'Provoke', 'Unity', 'Soul', 'Items', 'Teleport']
TERMS = {}
for n in NAMES:
    r = MANUAL.get(n) or lookup(n) or lookup(n.upper()) or lookup(n.title())
    TERMS[n] = r
TERMS.update(MANUAL)
if __name__ == '__main__':
    import sys; sys.stdout.reconfigure(encoding='utf-8')
    for k, v in TERMS.items(): print(f'{k!r:38} {v!r}')

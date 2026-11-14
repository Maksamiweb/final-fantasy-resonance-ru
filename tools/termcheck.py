"""Единство терминов: где в EN есть термин, а в RU нет ожидаемой основы. Только системные тексты (не диалоги)."""
import json, glob, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8')); ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): ru.update(json.load(open(f, encoding='utf-8')))
SYS = re.compile(r'^ST_(SkillDescription|PassiveSkillDescription|CommandSkillDescription|MasterSkillDescription|ConsumablesDescription|EquipmentDescription|VisionDescription|ArtifactDescription|Tutorial|UI_|BtlCommon|UnitTrait|ValuableDescription|TrophySummary|BuffDebuff)')
T = {  # англ. регэксп -> рус. основы (любая)
 r'\bVisions?\b': ['видени'], r'\bMastery\b': ['мастерств'], r'\bResonance\b': ['резонанс'], r'\bStagger': ['пробит', 'пробив'],
 r'\bLimit Bursts?\b|\bLB\b': ['предел'], r'\bEspers?\b': ['эспер'], r'\bCrystals?\b': ['кристалл'], r'\bAwaken': ['пробужд', 'пробуд'],
 r'\bFormation\b': ['строй', 'строя'], r'\bPoison': ['яд', 'отрав'], r'\bSilence': ['немот'], r'\bBlind': ['слеп'], r'\bParaly': ['парали'],
 r'\bSleep\b': ['сон', 'усып', 'сна'], r'\bPetrif': ['окамен'], r'\bConfus': ['смятен'], r'\bCharm': ['очаров'], r'\bBerserk': ['берсерк'],
 r'\bRegen\b': ['регенер'], r'\bHaste\b': ['ускорен'], r'\bSlow\b': ['замедл'], r'\bProtect\b': ['защит'], r'\bShell\b': ['панцир'],
 r'\bReflect\b': ['отраж'], r'\bReraise\b': ['автовоскреш'], r'\bBrave\b': ['храбр'], r'\bFaith\b': ['вер'], r'\bDebrave\b': ['трусост'],
 r'\bDefaith\b': ['невери'], r'\bDeprotect\b': ['пробой защит'], r'\bDeshell\b': ['пробой панцир'], r'\bHP\b': ['ОЗ'], r'\bMP\b': ['ОМ'],
 r'\bgil\b': ['гил'], r'\bPhoenix Down': ['пух феникс'], r'\bEthers?\b': ['эфир'], r'\bSanctity\b': ['святост'], r'\bSpirit\b': ['дух'],
 r'\bStamina\b': ['выносл'], r'\bInstant Death\b|\bKO\b': ['смерт', 'без сознания', 'нокаут'], r'\bTurns?\b': ['ход'], r'\bSummon': ['призыв', 'призов'],
}
bad = collections.defaultdict(list)
for k, e in en.items():
    if not SYS.match(k) or k not in ru: continue
    e2 = re.sub(r'<[^>]*>|\{[^}]*\}', '', e); r = ru[k].lower().replace(' ', ' ')
    for pat, stems in T.items():
        if re.search(pat, e2) and not any(s.lower() in r for s in stems): bad[pat].append(k)
for pat, ks in sorted(bad.items(), key=lambda x: -len(x[1])):
    print(f'\n## {pat}  ({len(ks)})')
    for k in ks[:6]: print('  ', k.split('␟')[1][:34], '| EN:', re.sub(r'\s+', ' ', en[k])[:90], '| RU:', re.sub(r'\s+', ' ', ru[k])[:90])
json.dump({p: v for p, v in bad.items()}, open('termcheck.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

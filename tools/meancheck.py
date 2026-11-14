"""Подозрительные реплики: числа, имена, вопрос/утверждение, длина. -> meancheck.json"""
import json, glob, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8')); ja = json.load(open('orig/ja.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): ru.update(json.load(open(f, encoding='utf-8')))
j2r = json.load(open('jp2ru_names.json', encoding='utf-8'))
# имена: EN -> RU основа (из ST_CharaName)
names = {}
for k, v in en.items():
    if k.startswith('ST_CharaName') and k in ru and re.fullmatch(r'[A-Z][a-z]{2,}', v.strip()):
        r = re.sub(r'[^А-Яа-яЁё]', '', ru[k])
        if len(r) >= 3: names[v.strip()] = r[:max(3, len(r) - 2)]
DLG = re.compile(r'^ST_(\d|ChrEv|SubEv|Summon|ATC|Town|LegendEV|Main|Sub|MainSummary|SubSummary|Ev)')
T = re.compile(r'<[^>]*>|\{[^}]*\}')
out = collections.defaultdict(list)
for k, e in en.items():
    if k not in ru or not DLG.match(k) or e.startswith('[') or ja.get(k, '') == e: continue
    e2 = T.sub('', e); r = T.sub('', ru[k]).replace(' ', ' ')
    num_e = set(re.findall(r'\d+', e2)); num_r = set(re.findall(r'\d+', r))
    if num_e - num_r: out['число'].append(k)
    for n, stem in names.items():
        if re.search(r'\b' + n + r'\b', e2) and stem.lower() not in r.lower(): out['имя'].append(k); break
    if e2.rstrip().endswith('?') and not re.search(r'[?？]', r) and len(e2) > 12: out['вопрос'].append(k)
    le, lr = len(e2), len(r)
    if le > 40 and (lr < le * 0.45): out['короче'].append(k)
for t, ks in out.items(): print(t, len(ks))
json.dump(out, open('meancheck.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

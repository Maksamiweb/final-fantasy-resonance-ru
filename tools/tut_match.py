"""OCR-строки -> ближайшая английская строка игры -> русский перевод. -> tut/match.json"""
import json, glob, re, sys, difflib, collections
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8')); ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): ru.update(json.load(open(f, encoding='utf-8')))
TAG = re.compile(r'<[^<>]*>')
voc = {}
for k, v in en.items():
    v2 = TAG.sub('', v).strip()
    if 2 <= len(v2) <= 45 and '{' not in v2 and '\n' not in v2 and k in ru and v2 not in voc:
        voc[v2] = TAG.sub('', ru[k]).replace(' ', ' ').strip()
keys = list(voc); low = {k.lower(): k for k in keys}
def clean(t):
    t = re.sub(r'^(?:[^A-Za-z]*|(?:[A-Za-z]{1,2}[)@]?\s*[<@]?\s+|[A-Za-z]@))', '', t)   # мусор от иконок слева
    t = re.sub(r'^(?:I|l|C\)|e|v|to|FF|IL|q|g|f|n|o,?)\s*[<@]?\s*(?=[A-Z])', '', t)
    return t.strip(' <>@*•"\'.-—_;|')
o = json.load(open('tut/ocr.json', encoding='utf-8')); out = {}; cache = {}
for name, lines in o.items():
    for l in lines:
        t = clean(l[4])
        if not re.search('[A-Za-z]{2}', t): continue
        if t not in cache:
            m = low.get(t.lower())
            if m: cache[t] = (m, 1.0)
            else:
                cand = difflib.get_close_matches(t, keys, 1, 0.6)
                cache[t] = (cand[0], round(difflib.SequenceMatcher(None, t, cand[0]).ratio(), 2)) if cand else (None, 0)
        m, sc = cache[t]
        out.setdefault(name, []).append([*map(round, l[:4]), l[4], t, m, sc, voc.get(m)])
json.dump(out, open('tut/match.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for t, (m, sc) in sorted(cache.items(), key=lambda x: x[1][1]):
    print(f'{sc:4} {t!r:45} -> {m!r} => {voc.get(m)!r}')

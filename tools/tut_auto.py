"""Черновая разметка: OCR + словарь -> tut/spec_auto.json {имя: [[x0,y0,x1,y1,ru,{}, 'en']]}; tut/unmatched.txt"""
import json, re, sys, difflib
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, 'tools')
from tut_terms import TERMS
KEYS = {k.lower(): k for k in TERMS}
JUNK = re.compile(r"^[^A-Za-z0-9]*$|^(I|l|C\)|e|v|to|FF|IL|q|g|f|n|o,?|c',|t'|@\w*|<|>|\]|\[|_|-)$")
def norm(w): return re.sub(r"[^A-Za-z0-9.:+%!&/-]", '', w)
def match(t):
    t2 = t.strip(' .<>@*•"\'-—_;|').lower()
    if t2 in KEYS: return KEYS[t2]
    if t2.rstrip('.:') in KEYS: return KEYS[t2.rstrip('.:')]
    c = difflib.get_close_matches(t2, list(KEYS), 1, 0.82)
    return KEYS[c[0]] if c else None
o = json.load(open('tut/ocr.json', encoding='utf-8')); spec = {}; un = []
for name, lines in o.items():
    items = []
    for x0, y0, x1, y1, text, words in lines:
        ws = [w for w in words]
        while ws and (JUNK.match(ws[0][4]) or (len(norm(ws[0][4])) <= 1 and len(ws) > 1)): ws.pop(0)
        if not ws: continue
        t = ' '.join(w[4] for w in ws)
        box = lambda W: [round(min(w[0] for w in W)), round(min(w[1] for w in W)), round(max(w[2] for w in W)), round(max(w[3] for w in W))]
        m = match(t)
        if m and TERMS[m] != m:
            items.append(box(ws) + [TERMS[m], {}, m]); continue
        # по словам: HP/MP/EXP/Lv.N, "Lv.N Имя"
        done = False
        for i, w in enumerate(ws):
            n = norm(w[4])
            if re.fullmatch(r'(HP|MP|EXP|ixp|txp|exp|€xp)', n, re.I) and not (n.upper() == 'MP' and i + 1 < len(ws) and ws[i+1][4].startswith('+')):
                items.append(box([w]) + [{'HP': 'ОЗ', 'MP': 'ОМ'}.get(n.upper(), 'ОПЫТ'), {}, n]); done = True
            elif re.fullmatch(r'[Ll]v\.?\s?\d*', n):
                rest = ' '.join(x[4] for x in ws[i+1:]); rm = match(rest) if rest else None
                num = re.sub(r'\D', '', n) or (re.sub(r'\D', '', ws[i+1][4]) if i + 1 < len(ws) else '')
                if rm:
                    items.append(box(ws[i:]) + [f'Ур. {num} {TERMS[rm]}'.replace('  ', ' '), {}, t]); done = True; break
                items.append(box([w]) + [f'Ур. {num}'.strip() if num else 'Ур.', {}, n]); done = True
        if not done and re.search('[A-Za-z]{3}', t): un.append(f'{name}\t{round(x0)},{round(y0)},{round(x1)},{round(y1)}\t{text}')
    spec[name] = items
json.dump(spec, open('tut/spec_auto.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
open('tut/unmatched.txt', 'w', encoding='utf-8').write('\n'.join(un))
print('авто', sum(len(v) for v in spec.values()), 'не распознано', len(un))

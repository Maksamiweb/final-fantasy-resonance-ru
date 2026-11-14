"""Убирает ручные переносы посреди предложения в окнах с автопереносом
(обучение/справка, описания, подсказки интерфейса). Абзацы (пустая строка) и пункты списков сохраняются.
Пишет edits/87_unwrap.json (до 88_nbsp).
"""
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if not re.search(r'(87_unwrap|88_nbsp|90_normalize)', f): ru.update(json.load(open(f, encoding='utf-8')))
ns = lambda k: k.split('␟')[0]
AUTO = re.compile(r'^ST_Tutorial|Description$|^ST_UnitTrait|^ST_UI_Option|^ST_UI_Guide|^ST_UI_Dialog|^ST_CommonDialog|^ST_EventDialog')
END = '.!?…:;»"”)'
def unwrap(s):
    nl = '\r\n' if '\r\n' in s else '\n'
    paras = s.split(nl)
    out = [paras[0]]
    for p in paras[1:]:
        prev = out[-1]
        join = (prev.strip() != '' and p.strip() != '' and prev.rstrip()[-1:] not in END
                and not re.match(r'\s*([-•・\d]|<text|<IA|　)', p))
        if join: out[-1] = prev.rstrip() + ' ' + p.lstrip()
        else: out.append(p)
    return nl.join(out)
out = {}
for k, v in ru.items():
    if AUTO.search(ns(k)) and ('\n' in v):
        nv = unwrap(v)
        if nv != v: out[k] = nv
json.dump(out, open('edits/87_unwrap.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('строк без лишних переносов:', len(out))

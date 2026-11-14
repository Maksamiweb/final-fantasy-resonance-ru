"""Проверка вместимости текста без запуска игры.
Ширина строк в пикселях шрифтом игры (UD Shin Go). Граница для каждого типа окна —
максимальная ширина английского оригинала в этом типе окна (он гарантированно влезает).
python -I tools/fitcheck.py
"""
import json, glob, re, sys, collections
from PIL import ImageFont
sys.stdout.reconfigure(encoding='utf-8')
F = ImageFont.truetype('fonts/BO-UDShinGoNTPr6N-Reg.otf', 32)
en = json.load(open('orig/en.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): ru.update(json.load(open(f, encoding='utf-8')))
ns = lambda k: k.split('␟')[0]
JP = re.compile('[぀-ヿ一-鿿]')

def clean(s):
    s = re.sub(r'\{[^{}|]*\}\|plural\(([^()]*)\)', lambda m: max(re.findall(r'=([^,)]*)', m.group(1)) or [''], key=len), s)
    s = re.sub(r'\{[Nn]um\w*\}|\{[Vv]alue\w*\}|\{\w*Param\w*\}|\{\w*Turn\w*\}|\{Cur\}|\{count\}|\{\w*[Ll]evel\}', '9999', s)
    s = re.sub(r'\{[^{}]*\}', 'Лассвелл', s)       # имена и названия — средняя длина
    s = re.sub(r'<[^<>]*/>', 'XX', s)               # иконки кнопок
    s = re.sub(r'<[^<>]*>|</>', '', s)
    return s
def lines(s): return [x for x in clean(s).replace('\r\n', '\n').split('\n')]
W = lambda t: F.getlength(t)

def family(n):
    if re.search(r'Name$|_NAME$|Title$|QuestBoardTitle', n): return n          # списки — по пространству имён
    if 'Description' in n or n.startswith('ST_UnitTrait'): return n
    if n.startswith('ST_ATC'): return 'ATC'
    if n.startswith('ST_Tutorial'): return 'Tutorial'
    if n.startswith(('ST_UI', 'ST_Btl', 'ST_CommonDialog', 'ST_EventDialog', 'ST_DialogChoice')): return n
    if re.search(r'Summary|Progress', n): return n
    if n.startswith('ST_GimEv_Bulletin'): return 'Bulletin'
    return 'DIALOG'

fam = collections.defaultdict(list)
for k in en:
    if en[k].strip() and k in ru: fam[family(ns(k))].append(k)
report = []
for fm, keys in fam.items():
    base = [k for k in keys if not JP.search(en[k])]
    if len(base) < 3: continue
    line_max = max(W(l) for k in base for l in lines(en[k]))
    tot = sorted(sum(W(l) for l in lines(en[k])) for k in base)
    tot_max = tot[-1]
    nl_max = max(len(lines(en[k])) for k in base)
    manual = sum('\n' in en[k] for k in base) / len(base) > 0.3   # переносы ставились вручную
    for k in keys:
        L = lines(ru[k]); lw = max(W(l) for l in L); tw = sum(W(l) for l in L)
        why = []
        if manual and lw > line_max * 1.02: why.append(f'строка {lw/line_max:.0%} от макс. EN')
        if not manual and tw > tot_max * 1.02: why.append(f'текст {tw/tot_max:.0%} от макс. EN')
        if len(L) > nl_max: why.append(f'строк {len(L)} > {nl_max}')
        if why: report.append((fm, k, '; '.join(why), en[k], ru[k]))
json.dump(report, open('fit_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
c = collections.Counter(r[0] for r in report)
print('подозрительных строк:', len(report)); print(c.most_common(40))

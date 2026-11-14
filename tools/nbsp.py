"""Неразрывные пробелы: короткие предлоги/союзы привязываются к следующему слову, тире — к предыдущему.
Только связный текст (диалоги, описания, обучение, задания); названия/заголовки не трогаем
(в декоративных шрифтах заголовков нет глифа U+00A0). Пишет edits/88_nbsp.json.
"""
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if not re.search(r'(88_nbsp|90_normalize)', f): ru.update(json.load(open(f, encoding='utf-8')))
ns = lambda k: k.split('␟')[0]
SKIP = re.compile(r'Name$|_NAME$|Title|ChapterTitle|ST_UI_Word|ST_UI_TitleMenu|ST_Dummy|Logo')
SHORT = r'в|во|к|ко|с|со|у|о|об|обо|и|а|но|не|ни|на|по|за|из|от|до|без|для|при|под|над|про|же|ли|бы'
NB = ' '
# защищаем теги и переменные
TOK = re.compile(r'<[^<>]*>|\{[^{}]*\}(\|plural\([^()]*\))?')
def fix(s):
    parts = TOK.split(s) if False else None
    out = []; pos = 0
    for m in TOK.finditer(s):
        out.append(proc(s[pos:m.start()])); out.append(m.group(0)); pos = m.end()
    out.append(proc(s[pos:]))
    return ''.join(out)
def proc(t):
    # предлог/союз + пробел -> неразрывный (только перед словом на кириллице/цифрой/кавычкой)
    t = re.sub(r'(?<![\w-])(' + SHORT + r') (?=[«"(]?[\wЁё])', lambda m: m.group(1) + NB, t, flags=re.I)
    t = re.sub(r'(?<=\S) — ', NB + '— ', t)   # тире не в начало строки
    return t
out = {}
for k, v in ru.items():
    n = ns(k)
    if SKIP.search(n) or len(v) < 30 or ' ' not in v: continue
    if n.startswith('ST_UI') and len(v) < 60: continue
    nv = fix(v)
    if nv != v: out[k] = nv
json.dump(out, open('edits/88_nbsp.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('строк с неразрывными пробелами:', len(out))

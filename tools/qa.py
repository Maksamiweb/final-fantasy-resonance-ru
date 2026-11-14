"""Автопроверка русского текста: находит проблемы, безопасные исправляет -> edits/92_qa.json."""
import json, glob, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if '92_qa' not in f: ru.update(json.load(open(f, encoding='utf-8')))
NB = ' '
TAG = re.compile(r'<[^<>]*>|\{[^{}]*\}(\|plural\([^()]*\))?')
def text_parts(s):  # (is_text, chunk)
    out = []; pos = 0
    for m in TAG.finditer(s): out.append((True, s[pos:m.start()])); out.append((False, m.group(0))); pos = m.end()
    out.append((True, s[pos:])); return out
def fix(s):
    res = []
    for t, ch in text_parts(s):
        if t:
            ch = re.sub(r'(?<=\S)[ ]{2,}(?=\S)', ' ', ch)                    # двойные пробелы
            ch = re.sub(r'(?<=[А-Яа-яЁё»)])[  ]+([,!?:;])', r'\1', ch)    # пробел перед знаком
            ch = re.sub(r'(?<=[А-Яа-яЁё])[ ]+\.(?!\.)', '.', ch)
            ch = re.sub(r'(?<=[А-Яа-яЁё,]) - (?=[А-Яа-яЁё])', ' — ', ch)      # дефис вместо тире
            ch = re.sub(r'"([А-Яа-яЁё][^"\n]{0,60})"', r'«\1»', ch)          # прямые кавычки
        res.append(ch)
    return ''.join(res)
out = {k: fix(v) for k, v in ru.items() if fix(v) != v}
MANUAL = {'ST_UI_Guide␟KeyGuideNext_02': ('Close', 'Закрыть'),
          'ST_BtlAI␟BtlAI0002': ('Please check the AI settings.', 'Проверьте настройки ИИ.')}
for k, (old, new) in MANUAL.items():
    if ru.get(k) == old: out[k] = new
json.dump(out, open('edits/92_qa.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('автоисправлено строк:', len(out))
# только отчёт
words = collections.Counter(w.lower() for v in ru.values() for w in re.findall(r'[А-Яа-яЁё]+', v.replace(NB, ' ')))
dbl = [(k, m.group(0)) for k, v in ru.items() for m in re.finditer(r'(?<![А-Яа-яЁё-])([А-Яа-яЁё]{2,})[  ]+\1(?![А-Яа-яЁё-])', v, re.I)]
print('задвоенные слова:', len(dbl)); [print('  ', k.split('␟')[1][:35], '|', w) for k, w in dbl[:25]]
ALLOW = re.compile(r'^(MRP|EXP|HP|MP|LB|Mk|II|III|SeeD|DDX|FXAA|MSAA|FPS|HUD|ID|OK|TEMP|ABCDE\w*|SQUARE|ENIX|YOSHITAKA|AMANO|MAKSAMI|LOGO|ILLUSTRATION|FINAL|FANTASY|RESONANCE|Steam|DLC|Nintendo|Switch|Xbox|PlayStation|Ultima|MASTER|RO|BE|MER|CHA|NT)$', re.I)
eng = collections.Counter(w for v in ru.values() for p in [TAG.sub(' ', v)] for w in re.findall(r'[A-Za-z]{3,}', p) if not ALLOW.match(w))
print('латиница:', sum(eng.values()), eng.most_common(25))
yo = {w.replace('ё', 'е'): w for w in words if 'ё' in w}
amb = {'все', 'всем', 'ее', 'небо', 'узнаем', 'совершенный', 'совершенно', 'летом', 'берет', 'передохнем', 'осел', 'падеж', 'мел', 'пятнадцатилетний'}
eio = [(w, yo[w], words[w], words[yo[w]]) for w in words if w in yo and w not in amb and words[w] >= 1]
print('слова без ё при варианте с ё:', len(eio)); print(sorted(eio, key=lambda x: -x[2])[:40])

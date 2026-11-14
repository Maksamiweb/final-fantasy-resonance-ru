"""Проверка правок одной части: python -I tools/check_part.py shards/SXX/part_NNN.jsonl out/SXX/part_NNN.json"""
import json, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
rows = {}
for line in open(sys.argv[1], encoding='utf-8'):
    if line.strip():
        r = json.loads(line); rows[r['k']] = r
try:
    out = json.load(open(sys.argv[2], encoding='utf-8'))
except Exception as e:
    print('ОШИБКА чтения JSON:', e); sys.exit(1)
TOK = re.compile(r'\{[^{}]*\}|<[^<>]*>|\|plural\(')
probs = []
for k, v in out.items():
    if k not in rows:
        probs.append(f'неизвестный ключ: {k!r}'); continue
    if not isinstance(v, str) or not v.strip():
        probs.append(f'{k}: пустое значение'); continue
    old = rows[k]['ru']
    a = collections.Counter(TOK.findall(old)); b = collections.Counter(TOK.findall(v))
    if a != b:
        probs.append(f'{k}: теги/переменные не совпадают. было {dict(a)} стало {dict(b)}')
    if v.count('\n') > old.count('\n'):
        probs.append(f'{k}: переносов строк больше, чем было ({old.count(chr(10))})')
    if '\n' in v and '\r\n' in old and v.replace('\r\n', '').count('\n'):
        probs.append(f'{k}: перенос должен быть \\r\\n, как в исходной строке')
    ml = lambda s: max(len(x) for x in s.split('\n'))
    if ml(v) > max(ml(old), ml(rows[k].get('en', '') or old)) * 1.25 + 5:
        probs.append(f'{k}: строка длиннее исходной ({ml(v)} > {ml(old)}): {v[:60]!r}')
    if re.search(r'[A-Za-z]{4,}', v) and not re.search(r'[A-Za-z]{4,}', old):
        probs.append(f'{k}: появилась латиница: {v[:60]!r}')
    if v.count('«') != v.count('»'):
        probs.append(f'{k}: непарные кавычки')
print(f'изменено {len(out)} из {len(rows)}')
if probs:
    print('\n'.join(probs)); sys.exit(1)
print('OK')

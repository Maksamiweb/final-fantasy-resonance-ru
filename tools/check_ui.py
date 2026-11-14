"""Проверка правок интерфейсных текстов: python -I tools/check_ui.py part.jsonl out.json"""
import json, sys, re, collections
sys.stdout.reconfigure(encoding='utf-8')
rows = {}
for line in open(sys.argv[1], encoding='utf-8'):
    if line.strip():
        r = json.loads(line); rows[r['id']] = r
try:
    out = json.load(open(sys.argv[2], encoding='utf-8'))
except Exception as e:
    print('ОШИБКА чтения JSON:', e); sys.exit(1)
TOK = re.compile(r'\{[^{}]*\}|<[^<>]*>|\|plural\(|\[[^\]]+\]')
probs = []
for i, v in out.items():
    if i not in rows: probs.append(f'неизвестный id: {i}'); continue
    if not isinstance(v, str) or not v.strip(): probs.append(f'{i}: пусто'); continue
    old = rows[i]['ru']
    a = collections.Counter(TOK.findall(old)); b = collections.Counter(TOK.findall(v))
    if a != b: probs.append(f'{i}: теги/переменные/[пометы] не совпадают: было {dict(a)} стало {dict(b)}')
    if v.count('\n') > old.count('\n'): probs.append(f'{i}: лишние переносы строк')
    if '\r\n' in old and v.replace('\r\n', '').count('\n'): probs.append(f'{i}: перенос должен быть \\r\\n')
    if len(v) > len(old) * 1.05 + 2: probs.append(f'{i}: длиннее исходного ({len(v)} > {len(old)}): {v[:60]!r}')
    if v.count('«') != v.count('»'): probs.append(f'{i}: непарные кавычки')
    if re.findall(r'\d+', re.sub(TOK, '', v)) != re.findall(r'\d+', re.sub(TOK, '', old)) and sorted(re.findall(r'\d+', v)) != sorted(re.findall(r'\d+', old)):
        probs.append(f'{i}: числа изменились: {re.findall(chr(92)+"d+", old)} -> {re.findall(chr(92)+"d+", v)}')
    if re.search(r'[A-Za-z]{4,}', v) and not re.search(r'[A-Za-z]{4,}', old): probs.append(f'{i}: появилась латиница')
print(f'изменено {len(out)} из {len(rows)}')
if probs: print('\n'.join(probs)); sys.exit(1)
print('OK')

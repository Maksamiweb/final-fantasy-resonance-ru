"""Сбор результатов агентов: out/SXX/part_NNN.json -> edits/50_dialogs.json с повторной проверкой."""
import json, glob, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
merged = {}; bad = []; stat = {}
for sh in sorted(glob.glob('shards/S*')):
    s = os.path.basename(sh); parts = sorted(glob.glob(f'{sh}/part_*.jsonl')); done = 0; n = 0
    for p in parts:
        o = f'out/{s}/' + os.path.basename(p).replace('.jsonl', '.json')
        if not os.path.exists(o):
            continue
        r = subprocess.run([sys.executable, '-I', 'tools/check_part.py', p, o], capture_output=True, text=True, encoding='utf-8')
        if 'OK' not in r.stdout.splitlines()[-1:]:
            bad.append((o, r.stdout[-400:])); continue
        d = json.load(open(o, encoding='utf-8')); merged.update(d); done += 1; n += len(d)
    stat[s] = f'{done}/{len(parts)} частей, {n} строк'
for s, v in stat.items(): print(s, v)
for o, t in bad: print('НЕ ПРОШЛО', o, t)
# старые термины, которых быть не должно
OLD = r'[Сс]ильн\w+ зель|[Зз]амешательств|«Очищени|«Физическ\w+ защит|«Магическ\w+ защит'
hits = [(k, v) for k, v in merged.items() if re.search(OLD, v)]
print('старые термины:', len(hits))
for k, v in hits[:20]: print('  ', k, '|', v[:100])
json.dump(merged, open('edits/50_dialogs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('итого строк:', len(merged))

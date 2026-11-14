"""Сбор правок интерфейсных текстов: ui_out/U*/part_*.json -> edits/84_ui.json (по всем ключам из ui_idmap.json)."""
import json, glob, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
idmap = json.load(open('ui_idmap.json', encoding='utf-8'))
fit = json.load(open('edits/85_fit.json', encoding='utf-8')) if os.path.exists('edits/85_fit.json') else {}
merged = {}; stat = {}; bad = []
for sh in sorted(glob.glob('ui_shards/U*')):
    s = os.path.basename(sh); parts = sorted(glob.glob(f'{sh}/part_*.jsonl')); done = n = 0
    for p in parts:
        o = f'ui_out/{s}/' + os.path.basename(p).replace('.jsonl', '.json')
        if not os.path.exists(o): continue
        r = subprocess.run([sys.executable, '-I', 'tools/check_ui.py', p, o], capture_output=True, text=True, encoding='utf-8')
        if 'OK' not in r.stdout.splitlines()[-1:]:
            bad.append((o, r.stdout[-300:])); continue
        for i, v in json.load(open(o, encoding='utf-8')).items():
            for k in idmap[i]:
                if k not in fit: merged[k] = v
            n += 1
        done += 1
    stat[s] = f'{done}/{len(parts)} частей, {n} текстов'
for s, v in stat.items(): print(s, v)
for o, t in bad: print('НЕ ПРОШЛО', o, t)
json.dump(merged, open('edits/84_ui.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('строк в игре изменено:', len(merged))

"""Авторазметка + ручные правки (tools/tut_spec.py) -> tut/ru/*.png и листы tut/rsheet_XX.png"""
import json, sys
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import tut_draw as D, importlib
from PIL import Image
import tut_spec as S
auto = json.load(open('tut/spec_auto.json', encoding='utf-8'))
names = list(json.load(open('tut/info.json')))
only = sys.argv[1:]
for n in names:
    if only and not any(o in n for o in only): continue
    items = []
    if n in S.SPEC: D.apply(n, S.SPEC[n]); continue
    for it in auto.get(n, []):
        if any(d in it[6] or d == tuple(it[:2]) for d in S.DROP.get(n, [])) or any(d == '*' for d in S.DROP.get(n, [])): continue
        o = dict(it[5]); o.update(S.OPT.get(n, {}).get(it[6], {})); o.update(S.OPT.get('*', {}).get(it[6], {}) if it[6] not in S.OPT.get(n, {}) else {})
        if 'ru' in o: it[4] = o.pop('ru')
        if 'box' in o: it[:4] = o.pop('box')
        items.append(it[:5] + [o])
    items += S.ADD.get(n, [])
    D.apply(n, items)
sheets = [names[i:i + 3] for i in range(0, len(names), 3)]
for i, grp in enumerate(sheets):
    if only and not any(o in g for g in grp for o in only): continue
    sh = Image.new('RGB', (1180, 340 * len(grp)), (255, 0, 255))
    for j, g in enumerate(grp): sh.paste(Image.open(f'tut/ru/{g}.png').convert('RGB'), (0, j * 340))
    sh.save(f'tut/rsheet_{i:02d}.png')

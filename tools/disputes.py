"""Решения по спорным местам -> edits/91_disputes.json (поверх всех слоёв)."""
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8')); ja = json.load(open('orig/ja.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if '91_disputes' not in f: ru.update(json.load(open(f, encoding='utf-8')))
out = {}
for k, v in ru.items():
    n = re.sub(r'([Сс])(-[Сс]-[Сс])?ахагин', lambda m: m.group(1) + (m.group(2) or '') + 'ахуагин', v)   # Сахуагин — офиц. FF XV
    if re.search(r'Tronn|トロン', en.get(k, '') + ' ' + ja.get(k, '')):
        n = re.sub(r'(?<![А-Яа-яЁё])Трон(?=(а|у|ом|е)?(?![А-Яа-яЁё]))', 'Тронн', n)                     # не «трон»
    if n != v: out[k] = n
# Шаблон пробуждения видения: «Расход: Камень ×3» вместо «Расход: 3 Камень»
k = 'ST_UI_Dialog␟DialogOtherVisionUpgradeConfirm'
old = 'Расход: {ItemNum} {ItemNum}|plural(one={ItemName}, other={ItemName}).'
if old in ru[k].replace(' ', ' '):
    out[k] = ru[k].replace(' ', ' ').replace(old, 'Расход: {ItemNum}|plural(one={ItemName}, other={ItemName}) ×{ItemNum}.')
json.dump(out, open('edits/91_disputes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('строк', len(out))

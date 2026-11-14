"""Финальная нормализация по всему тексту -> edits/90_normalize.json"""
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if '90_normalize' not in f: ru.update(json.load(open(f, encoding='utf-8')))
RULES = [(r'Дилмаги', 'Дильмаги'), (r'Фелиситас', 'Фелицитас'),
         (r'(?<![А-Яа-яЁё])кристалл(\w*)([  ])(Земли|Воды|Огня|Ветра|Света|Тьмы|Льда|Молнии)', r'Кристалл\1\2\3')]
out = {}
for k, v in ru.items():
    n = v
    for a, b in RULES: n = re.sub(a, b, n)
    if n != v: out[k] = n
json.dump(out, open('edits/90_normalize.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('нормализовано', len(out))

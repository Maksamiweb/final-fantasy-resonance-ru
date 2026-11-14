"""Выравнивание описаний после редактуры помощниками -> edits/86_uinorm.json"""
import json, glob, re, sys
sys.stdout.reconfigure(encoding='utf-8')
en = json.load(open('orig/en.json', encoding='utf-8')); ja = json.load(open('orig/ja.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if not re.search(r'(86_uinorm|87_|88_|90_)', f): ru.update(json.load(open(f, encoding='utf-8')))
ns = lambda k: k.split('␟')[0]
DESC = re.compile(r'Description$|^ST_UnitTrait')
NB = ' '
def W(s): return s.replace(' ', '[  ]')
out = {}
for k, v in ru.items():
    if not DESC.search(ns(k)): continue
    e = en.get(k, '') + ' ' + ja.get(k, '')
    n = v
    n = n.replace('[Магический клинок]', '[Магия меча]')
    n = re.sub(r'(^|[.!]\s+|\n)Повышает(?=[  ]максимум[  ](ОЗ|ОМ))', r'\1Увеличивает', n)
    n = re.sub(r'«Святой свет»', '«Святость»', n)
    if re.search(r'Deprotect|デプロテ|物防ダウン', e):
        n = re.sub(W('Массовое ослабление физической защиты'), '«Массовый пробой защиты»', n)
        n = re.sub(W(r'ослаблени(е|я) физической защиты'), lambda m: '«Пробой защиты»' if m.group(1) == 'е' else '«Пробоя защиты»', n)
    if re.search(r'Deshell|デシェル|魔防ダウン', e):
        n = re.sub(W(r'ослаблени(е|я) магической защиты'), lambda m: '«Пробой панциря»' if m.group(1) == 'е' else '«Пробоя панциря»', n)
    if re.search(r'Debrave|デブレイ', e):
        n = re.sub(W(r'ослаблени(е|я) атаки'), lambda m: '«Трусость»' if m.group(1) == 'е' else '«Трусости»', n)
    if re.search(r'Defaith|デフェイ', e):
        n = re.sub(W(r'ослаблени(е|я) магии'), lambda m: '«Неверие»' if m.group(1) == 'е' else '«Неверия»', n)
    if n != v: out[k] = n
# A00437: по японскому ОЗ и ОМ
for k in ['ST_SkillDescription␟SkillDescription100180']:
    out[k] = 'Полностью восстанавливает ОЗ и ОМ всем союзникам.'
json.dump(out, open('edits/86_uinorm.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('выровнено строк:', len(out))
if len(sys.argv) > 1:
    for k, v in list(out.items())[:40]: print(ns(k)[3:20], '|', ru[k][:80].replace('\r\n', ' '), '=>', v[:80].replace('\r\n', ' '))

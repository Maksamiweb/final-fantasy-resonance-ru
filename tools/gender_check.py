"""Проверка рода говорящего: формы первого лица (я ...л/ла, рад/рада и т.п.) против пола персонажа."""
import json, re, glob, sys, collections
sys.path.insert(0, 'tools'); import speaker_names as S
sys.stdout.reconfigure(encoding='utf-8')
sp = json.load(open('speakers.json', encoding='utf-8')); en = json.load(open('orig/en.json', encoding='utf-8'))
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')): ru.update(json.load(open(f, encoding='utf-8')))
NB = ' '
ADJ = r'(рад|готов|должен|уверен|счастлив|благодарен|виноват|обязан|сам|один|согласен|намерен|свободен|жив|спокоен|способен|нужен|прав|знаком|занят|удивлён|поражён|тронут|вынужден|ранен|спасён|сыт|зол|болен)'
ADJF = r'(рада|готова|должна|уверена|счастлива|благодарна|виновата|обязана|сама|одна|согласна|намерена|свободна|жива|спокойна|способна|нужна|права|знакома|занята|удивлена|поражена|тронута|вынуждена|ранена|спасена|сыта|зла|больна)'
def forms(t):
    t = t.replace(NB, ' ')
    m = f = 0
    for s in re.split(r'(?<=[.!?…])\s+|\r?\n', t):
        if not re.search(r'(^|[^\wё])(я|Я)([^\wё]|$)', s): continue
        if re.search(r'\b(мы|вы|ты|он|она|они)\b', s, re.I): continue  # только явные «я»-фразы без других лиц
        m += len(re.findall(r'(?<![\wё])(?:я\s+(?:\w+\s+){0,2}?)(\w{2,}(?:л|лся))(?![\wё])', s, re.I)) + len(re.findall(r'(?<![\wё])я\s+(?:\w+\s+)?' + ADJ + r'(?![\wё])', s, re.I))
        f += len(re.findall(r'(?<![\wё])(?:я\s+(?:\w+\s+){0,2}?)(\w{2,}(?:ла|лась))(?![\wё])', s, re.I)) + len(re.findall(r'(?<![\wё])я\s+(?:\w+\s+)?' + ADJF + r'(?![\wё])', s, re.I))
    return m, f
stat = collections.defaultdict(lambda: [0, 0, []])
for k, jp in sp.items():
    if k not in ru: continue
    n = S.norm(jp)
    if not n: continue
    m, f = forms(ru[k])
    if m or f:
        st = stat[n]; st[0] += m; st[1] += f; st[2].append((k, m, f))
json.dump({n: v for n, v in stat.items()}, open('gender_stat.json', 'w', encoding='utf-8'), ensure_ascii=False)
for n, (m, f, l) in sorted(stat.items(), key=lambda x: -(x[1][0] + x[1][1])):
    print(f'{n}: муж {m} / жен {f}')

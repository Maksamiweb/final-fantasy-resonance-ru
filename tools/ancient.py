"""Старинная речь древних персонажей -> edits/83b_ancient.json (до вёрстки: 85/87/88 пересчитываются после)."""
import json, glob, sys, runpy
sys.stdout.reconfigure(encoding='utf-8')
NB, BR = chr(0xA0), chr(10)
ru = json.load(open('ru/ru.json', encoding='utf-8'))
for f in sorted(glob.glob('edits/*.json')):
    if f.replace(chr(92), '/') < 'edits/83b': ru.update(json.load(open(f, encoding='utf-8')))
sp = json.load(open('speakers.json', encoding='utf-8'))
spk = {k.split(chr(0x241F))[-1]: s for k, s in sp.items()}
def N(s): return s.replace(NB, ' ').replace(chr(13), '').replace(BR, ' ')
def keepbr(orig, new):
    """Если в исходной реплике был ручной перенос — ставим его на ближайший пробел в той же доле строки."""
    if BR not in orig: return new
    br = chr(13) + BR if chr(13) + BR in orig else BR
    i = round(orig.index(br) / len(orig) * len(new)); sps = [m for m, c in enumerate(new) if c == ' ']
    if not sps: return new
    j = min(sps, key=lambda m: abs(m - i)); return new[:j] + br + new[j + 1:]
esp = runpy.run_path('ancient/espers_edits.py')['EDITS']; sak = runpy.run_path('ancient/sakura_edits.py')['EDITS']; eld = runpy.run_path('ancient/elder_edits.py')['EDITS']
esp_keys = {o['k'] for o in json.load(open('ancient/espers.json', encoding='utf-8'))}
GENERIC = {'Да, но...', 'Ты это потерял?', 'Я — Ифрит.', 'Моё имя — Ифрит.'}
out = {}; hit = {}
for k, v in ru.items():
    kk = k.split(chr(0x241F))[-1]; t = N(v)
    if spk.get(kk) == 'サクラ' and t in sak: out[k] = keepbr(v, sak[t]); hit[t] = 1
    elif spk.get(kk) == 'おばば' and t in eld: out[k] = keepbr(v, eld[t]); hit[t] = 1
    elif t in esp and (t not in GENERIC or k in esp_keys or kk.startswith('Summon')): out[k] = keepbr(v, esp[t]); hit[t] = 1
    elif kk.startswith('Summon'):
        for o_, n_ in esp.items():
            if len(o_) > 15 and o_ in t: out[k] = keepbr(v, t.replace(o_, n_)); hit[o_] = 1
miss = [t for t in list(esp) + list(sak) + list(eld) if t not in hit]
json.dump(out, open('edits/83b_ancient.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
later = {}
for f in ['edits/85_fit.json', 'edits/86_uinorm.json', 'edits/90_normalize.json', 'edits/91_disputes.json', 'edits/92_qa.json']:
    for k in json.load(open(f, encoding='utf-8')):
        if k in out: later[k] = f
print('строк изменено:', len(out), '| не найдено:', miss, '| перекрыто позже:', later)

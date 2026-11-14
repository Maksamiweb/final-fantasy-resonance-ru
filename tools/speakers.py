"""Извлекает говорящего для каждой реплики из таблиц DT_*_TalkEvent игры (IoStore).
Строка таблицы: ... FF FF FF FF <индекс имени говорящего u32> <номер u32> ... <FString ключ реплики>.
Пространство имён ключа — запись 'ST_...' из name map таблицы.
Пишет speakers.json: {"ST_ns␟key": "японское имя говорящего"}.
"""
import json, re, struct, sys
sys.path.insert(0, 'tools')
from iostore import IoStore
import zen
sys.stdout.reconfigure(encoding='utf-8')
s = IoStore(r'D:/SteamLibrary/steamapps/common/FINAL FANTASY RESONANCE/FFRS/Content/Paks/FFRS-Windows.utoc')
tabs = [k for k in s.files if re.search(r'/Datatable/(Event|Chat)/.*\.uasset$', k)]
print('таблиц разговоров:', len(tabs))
out = {}; bad = 0
for t in tabs:
    d = s.read(s.files[t])
    try:
        names, hsize = zen.names(d)
    except Exception:
        bad += 1; continue
    sts = [n for n in names if n.startswith('ST_')]
    keyset = set(names)
    body = d[hsize:]
    for m in re.finditer(rb'\xff\xff\xff\xff(....)(....)', body):
        idx, num = struct.unpack('<II', m.group(1) + m.group(2))
        if idx >= len(names) or num != 0: continue
        sp = names[idx]
        # ближайший FString-ключ после говорящего
        km = re.compile(rb'([\x02-\x40])\x00\x00\x00([ -~]+?)\x00').search(body, m.end(), m.end() + 120)
        if not km: continue
        key = km.group(2).decode()
        if key not in keyset or key.startswith(('ST_', '/', 'NewRow')): continue
        for ns in sts:
            out[ns + '\u241f' + key] = sp
json.dump(out, open('speakers.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('реплик с говорящим:', len(out), 'ошибок разбора:', bad)

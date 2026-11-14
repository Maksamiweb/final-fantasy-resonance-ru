"""Нормализация японских имён говорящих -> русское имя."""
import json, re
jp2ru = json.load(open('jp2ru_names.json', encoding='utf-8'))
def norm(jp):
    if jp.startswith('/') or jp in ('空白', 'テロップ'): return None
    m = re.match(r'^？？？[（(](.+?)[）)]$', jp)
    if m: jp = m.group(1)
    jp = re.sub(r'[（(](子ども|ＯＦＦ|OFF)[）)]$', '', jp)
    m = re.match(r'^.+?[（(](.+?)[）)]$', jp)
    if m and m.group(1) in jp2ru: jp = m.group(1)
    if jp == 'レイン＆ラスウェル': return 'Рейн и Лассвелл'
    return jp2ru.get(jp, jp)

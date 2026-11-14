import json,sys,collections,re; sys.stdout.reconfigure(encoding='utf-8')
en=json.load(open('orig/en.json',encoding='utf-8')); ru=json.load(open('ru/ru.json',encoding='utf-8'))
def ns(k): return k.split('\u241f')[0]
names={}
for k in en:
    if ns(k) in ('ST_CharaName','ST_MAP_NAME','ST_UnitName'):
        e=en[k].strip(); r=ru[k].strip()
        if e and r and len(e)>3 and ' ' not in e: names.setdefault(e,collections.Counter())[r]+=1
# names with multiple renderings in dictionaries
for e,c in names.items():
    if len(c)>1: print('MULTI',e,dict(c))
text=[k for k in en if not ns(k).endswith(('Name',))]
res=[]
for e,c in names.items():
    r=c.most_common(1)[0][0]; stem=r[:max(3,len(r)-2)].lower()
    hits=[k for k in text if re.search(r'\b'+re.escape(e)+r'\b',en[k])]
    miss=[k for k in hits if stem not in ru[k].lower()]
    if hits and len(miss)/len(hits)>0.15 and len(miss)>=2: res.append((len(miss),len(hits),e,r,miss[:3]))
res.sort(reverse=True)
for m,h,e,r,ks in res[:40]:
    print(f'{e} -> {r}: {m}/{h} не совпадают')
    for k in ks[:2]: print('   EN:',en[k][:120].replace('\r\n',' '),'\n   RU:',ru[k][:120].replace('\r\n',' '))

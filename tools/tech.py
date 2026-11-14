import json,sys,collections,re; sys.stdout.reconfigure(encoding='utf-8')
en=json.load(open('orig/en.json',encoding='utf-8')); ru=json.load(open('ru/ru.json',encoding='utf-8'))
ns=lambda k:k.split('\u241f')[0]
mix=[k for k in en if re.search(r'[А-Яа-яЁё][A-Za-z]|[A-Za-z][А-Яа-яЁё]',ru[k])]
print('mixed-script words:',len(mix))
for k in mix[:8]: print('  ',ru[k][:100].replace('\r\n',' / '))
lines=[k for k in en if ru[k].count('\n')>en[k].count('\n')]
print('RU has more line breaks than EN:',len(lines))
def maxline(s): return max((len(x) for x in s.split('\n')),default=0)
over=[]
for k in en:
    e,r=maxline(en[k]),maxline(ru[k])
    if e>=5 and r>e*1.5 and r-e>8: over.append((r/e,k))
over.sort(reverse=True); print('lines >1.5x longer than EN:',len(over))
c=collections.Counter(ns(k) for _,k in over); print(c.most_common(12))
for _,k in over[:12]: print('  ',k,'| EN:',en[k][:70].replace('\r\n',' / '),'| RU:',ru[k][:90].replace('\r\n',' / '))
dbl=[k for k in en if '  ' in ru[k] and '  ' not in en[k]]; print('double spaces:',len(dbl))
yo=sum('ё' in v for v in ru.values()); print('strings with ё:',yo)
ty=sum(bool(re.search(r'\bты\b',v,re.I)) for v in ru.values()); vy=sum(bool(re.search(r'\bвы\b',v,re.I)) for v in ru.values()); print('ты',ty,'вы',vy)

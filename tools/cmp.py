import json,re,collections,sys
en=json.load(open('orig/en.json',encoding='utf-8')); ru=json.load(open('ru/ru.json',encoding='utf-8'))
print('en',len(en),'ru',len(ru),'missing in ru',len(set(en)-set(ru)),'extra in ru',len(set(ru)-set(en)))
cyr=re.compile('[А-Яа-яЁё]'); lat=re.compile('[A-Za-z]{3,}')
same=[k for k in en if k in ru and ru[k]==en[k] and lat.search(en[k] or '')]
nocyr=[k for k in en if k in ru and en[k].strip() and not cyr.search(ru[k]) and lat.search(en[k])]
print('identical to EN (with latin words):',len(same)); print('no cyrillic:',len(nocyr))
tok=re.compile(r'\{[^}]*\}|<[^>]*>|%[sd]|\n|\r\n')
bad=[]
for k in en:
    if k in ru:
        a=collections.Counter(tok.findall(en[k])); b=collections.Counter(tok.findall(ru[k]))
        a.pop('\r\n',None); b.pop('\r\n',None)
        if a!=b: bad.append(k)
print('tag/var mismatches:',len(bad))
json.dump({'nocyr':nocyr,'bad':bad},open('report_keys.json','w',encoding='utf-8'),ensure_ascii=False)
ns=collections.Counter(k.split('\u241f')[0] for k in nocyr); print(ns.most_common(25))
for k in bad[:25]: print('---',k,'\n EN:',en[k][:200],'\n RU:',ru[k][:200])

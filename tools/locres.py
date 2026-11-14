import struct, sys, json
def rstr(d,p):
    n=struct.unpack_from('<i',d,p)[0]; p+=4
    if n==0: return '',p
    if n<0:
        n=-n; s=d[p:p+2*n].decode('utf-16-le')[:-1]; return s,p+2*n
    s=d[p:p+n].decode('utf-8','replace')[:-1]; return s,p+n
def parse(d):
    p=16; ver=d[p]; p+=1
    soff=struct.unpack_from('<q',d,p)[0]; p+=8
    if ver>=2: p+=4
    q=soff; cnt=struct.unpack_from('<i',d,q)[0]; q+=4; strs=[]
    for i in range(cnt):
        s,q=rstr(d,q)
        if ver>=2: q+=4
        strs.append(s)
    nns=struct.unpack_from('<I',d,p)[0]; p+=4; out={}
    for _ in range(nns):
        if ver>=2: p+=4
        ns,p=rstr(d,p); nk=struct.unpack_from('<I',d,p)[0]; p+=4
        for _ in range(nk):
            if ver>=2: p+=4
            k,p=rstr(d,p); sh,idx=struct.unpack_from('<Ii',d,p); p+=8
            out[ns+'\u241f'+k]=strs[idx]
    return out
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    if len(sys.argv)>3: d=d[int(sys.argv[3]):int(sys.argv[3])+int(sys.argv[4])]
    o=parse(d); json.dump(o,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=0); print(len(o))

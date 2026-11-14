import struct, sys, zlib
def rstr(d,p):
    n=struct.unpack_from('<i',d,p)[0]; p+=4
    if n<0: n=-n; return d[p:p+2*n].decode('utf-16-le')[:-1],p+2*n
    return d[p:p+n].decode('utf-8','replace')[:-1],p+n
def open_pak(fn):
    f=open(fn,'rb'); f.seek(0,2); L=f.tell(); f.seek(L-300); t=f.read()
    i=t.find(bytes.fromhex('e1126f5a')); io,isz=struct.unpack_from('<qq',t,i+8)
    names=[t[i+44+32*k:i+44+32*k+32].rstrip(b'\0').decode() for k in range(5)]
    f.seek(io); d=f.read(isz); p=0
    mp,p=rstr(d,p); n,=struct.unpack_from('<i',d,p); p+=4; p+=8
    h,=struct.unpack_from('<I',d,p); p+=4
    if h: p+=36
    h,=struct.unpack_from('<I',d,p); p+=4
    fdo,fds=struct.unpack_from('<qq',d,p); p+=36
    es,=struct.unpack_from('<I',d,p); p+=4; enc=d[p:p+es]
    f.seek(fdo); fd=f.read(fds); q=0; nd,=struct.unpack_from('<i',fd,q); q+=4; files={}
    for _ in range(nd):
        dn,q=rstr(fd,q); nf,=struct.unpack_from('<i',fd,q); q+=4
        for _ in range(nf):
            fn2,q=rstr(fd,q); loc,=struct.unpack_from('<i',fd,q); q+=4; files[mp+dn+fn2]=loc
    return f,enc,files,names
def entry(enc,loc):
    fl,=struct.unpack_from('<I',enc,loc); p=loc+4
    bs=(fl&0x3f)<<11 if (fl&0x3f)!=0x3f else None
    bc=(fl>>6)&0xffff; encr=(fl>>22)&1; cm=(fl>>23)&0x3f
    def rd(big):
        nonlocal p
        if big: v,=struct.unpack_from('<I',enc,p); p+=4
        else: v,=struct.unpack_from('<Q',enc,p); p+=8
        return v
    if bs is None: bs,=struct.unpack_from('<I',enc,p); p+=4
    off=rd(fl>>31&1); usz=rd(fl>>30&1); sz=rd(fl>>29&1) if cm else usz
    blocks=[]
    if bc>0 and (bc!=1 or encr): 
        for _ in range(bc): b,=struct.unpack_from('<I',enc,p); p+=4; blocks.append(b)
    return dict(off=off,usz=usz,sz=sz,cm=cm,bc=bc,enc=encr,bs=bs,blocks=blocks)
def extract(f,e,names):
    hdr=53 if not e['cm'] else 53+4+16*e['bc']
    if e['cm']==0:
        f.seek(e['off']+53); return f.read(e['usz'])
    method=names[e['cm']-1]
    f.seek(e['off']); raw=f.read(hdr+e['sz']+64*e['bc']+64)
    # read block table from header
    p=8+8+8+4+20; nb,=struct.unpack_from('<I',raw,p); p+=4; out=b''
    for _ in range(nb):
        s,en=struct.unpack_from('<QQ',raw,p); p+=16
        f.seek(e['off']+s); c=f.read(en-s)
        if method.lower()=='zlib': out+=zlib.decompress(c)
        elif method.lower()=='oodle': raise SystemExit('oodle')
        else: raise SystemExit(method)
    return out
if __name__=='__main__':
    f,enc,files,names=open_pak(sys.argv[1]); print(names)
    if len(sys.argv)==2 or sys.argv[2]=='ls':
        pat=sys.argv[3] if len(sys.argv)>3 else ''
        for k,v in files.items():
            if pat in k: print(k, entry(enc,v))
    else:
        e=entry(enc,files[sys.argv[2]]); open(sys.argv[3],'wb').write(extract(f,e,names))

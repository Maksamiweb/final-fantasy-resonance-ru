import sys, ctypes, struct
sys.path.insert(0, sys.argv[1]); import pak
dll=ctypes.WinDLL(sys.argv[1]+'/oo2core_7_win64.dll')
dec=dll.OodleLZ_Decompress
dec.restype=ctypes.c_int64
dec.argtypes=[ctypes.c_char_p,ctypes.c_int64,ctypes.c_char_p,ctypes.c_int64,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_int64,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int64,ctypes.c_int]
f,enc,files,names=pak.open_pak(sys.argv[2])
for lang in sys.argv[4:]:
    e=pak.entry(enc,files['../../../FFRS/Content/Localization/Game/%s/Game.locres'%lang])
    f.seek(e['off']); raw=f.read(53+4+16*e['bc']+64); p=48; nb,=struct.unpack_from('<I',raw,p); p+=4; out=b''; rem=e['usz']
    for _ in range(nb):
        s,en=struct.unpack_from('<QQ',raw,p); p+=16
        f.seek(e['off']+s); c=f.read(en-s); n=min(e['bs'],rem); ob=ctypes.create_string_buffer(n)
        r=dec(c,len(c),ob,n,1,0,0,None,0,None,None,None,0,3)
        assert r==n,(r,n); out+=ob.raw; rem-=n
    open(sys.argv[3]+'/'+lang+'.locres','wb').write(out); print(lang,len(out))

"""Чтение контейнера IoStore (UE5, .utoc/.ucas, TOC v8, Oodle) — только чтение.
from iostore import IoStore; s = IoStore(path_utoc); s.files -> {путь: индекс}; s.read(индекс) -> bytes
"""
import struct, ctypes, os

class IoStore:
    def __init__(self, utoc, oodle_dll=None):
        self.utoc = utoc; self.ucas = utoc[:-4] + 'ucas'
        d = open(utoc, 'rb').read()
        (hs, cnt, bcnt, bsz, mcnt, mlen, blk, disz, pcnt) = struct.unpack_from('<9I', d, 20)
        seeds, = struct.unpack_from('<I', d, 84); nophash, = struct.unpack_from('<I', d, 96)
        self.blk = blk; p = hs
        self.ids = [d[p + 12 * i:p + 12 * i + 12] for i in range(cnt)]; p += 12 * cnt
        self.offlen = []
        for i in range(cnt):
            b = d[p + 10 * i:p + 10 * i + 10]
            self.offlen.append((int.from_bytes(b[0:5], 'big'), int.from_bytes(b[5:10], 'big')))
        p += 10 * cnt + 4 * seeds + 4 * nophash
        self.blocks = []
        for i in range(bcnt):
            b = d[p + 12 * i:p + 12 * i + 12]
            self.blocks.append((int.from_bytes(b[0:5], 'little'), int.from_bytes(b[5:8], 'little'),
                                int.from_bytes(b[8:11], 'little'), b[11]))
        p += 12 * bcnt
        self.methods = [d[p + mlen * i:p + mlen * (i + 1)].rstrip(b'\0').decode() for i in range(mcnt)]; p += mcnt * mlen
        self.files = self._dirindex(d[p:p + disz])
        dll = oodle_dll or os.path.join(os.path.dirname(__file__), 'oo2core_7_win64.dll')
        self.oo = ctypes.WinDLL(dll).OodleLZ_Decompress
        self.oo.restype = ctypes.c_int64
        self.oo.argtypes = [ctypes.c_char_p, ctypes.c_int64, ctypes.c_char_p, ctypes.c_int64, ctypes.c_int, ctypes.c_int,
                            ctypes.c_int, ctypes.c_void_p, ctypes.c_int64, ctypes.c_void_p, ctypes.c_void_p,
                            ctypes.c_void_p, ctypes.c_int64, ctypes.c_int]
        self.fh = open(self.ucas, 'rb')

    def _dirindex(self, d):
        p = 0
        def rstr():
            nonlocal p
            n, = struct.unpack_from('<i', d, p); p += 4
            if n < 0:
                s = d[p:p - 2 * n].decode('utf-16-le')[:-1]; p += -2 * n
            else:
                s = d[p:p + n].decode('utf-8', 'replace')[:-1]; p += n
            return s
        mount = rstr()
        nd, = struct.unpack_from('<I', d, p); p += 4
        dirs = [struct.unpack_from('<4I', d, p + 16 * i) for i in range(nd)]; p += 16 * nd
        nf, = struct.unpack_from('<I', d, p); p += 4
        fents = [struct.unpack_from('<3I', d, p + 12 * i) for i in range(nf)]; p += 12 * nf
        ns, = struct.unpack_from('<I', d, p); p += 4
        strs = [rstr() for _ in range(ns)]
        NONE = 0xFFFFFFFF; out = {}
        def walk(di, path):
            name, child, sib, ffile = dirs[di]
            here = path + (strs[name] + '/' if name != NONE else '')
            f = ffile
            while f != NONE:
                fn, nxt, ud = fents[f]; out[mount + here + strs[fn]] = ud; f = nxt
            c = child
            while c != NONE:
                walk(c, here); c = dirs[c][2]
        walk(0, '')
        return out

    def read(self, idx):
        off, ln = self.offlen[idx]
        b0 = off // self.blk; b1 = (off + ln - 1) // self.blk
        out = bytearray()
        for bi in range(b0, b1 + 1):
            o, cs, us, m = self.blocks[bi]
            self.fh.seek(o); raw = self.fh.read((cs + 15) & ~15)[:cs]
            if m == 0:
                out += raw[:us]
            else:
                buf = ctypes.create_string_buffer(us)
                r = self.oo(raw, cs, buf, us, 1, 0, 0, None, 0, None, None, None, 0, 3)
                assert r == us, (r, us)
                out += buf.raw
        s = off - b0 * self.blk
        return bytes(out[s:s + ln])

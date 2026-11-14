"""Сборка русификатора: ru/ru.json (+ правки) -> Game.locres -> pak v11.

Структура locres (порядок, хеши пространств имён/ключей/исходников) берётся из
базового пакета, меняются только строки. Pak собирается по образцу базового.

python -I tools/build.py <базовый_pak> <ru.json> <выходной_pak>
"""
import struct, sys, json, hashlib

SEP = '␟'


def rstr(d, p):
    n = struct.unpack_from('<i', d, p)[0]; p += 4
    if n == 0:
        return '', p
    if n < 0:
        n = -n
        return d[p:p + 2 * n].decode('utf-16-le')[:-1], p + 2 * n
    return d[p:p + n].decode('utf-8', 'replace')[:-1], p + n


def wstr(s):
    if s == '':
        return struct.pack('<i', 0)
    try:
        b = s.encode('ascii') + b'\0'
        return struct.pack('<i', len(b)) + b
    except UnicodeEncodeError:
        b = s.encode('utf-16-le') + b'\0\0'
        return struct.pack('<i', -(len(b) // 2)) + b


def parse_struct(d):
    """Возвращает список (ns_hash, ns, [(key_hash, key, src_hash, str_idx)]) и таблицу строк."""
    assert d[16] == 3, 'ожидается locres v3'
    p = 17
    soff = struct.unpack_from('<q', d, p)[0]; p += 8
    p += 4  # entries count
    q = soff; cnt = struct.unpack_from('<i', d, q)[0]; q += 4; strs = []
    for _ in range(cnt):
        s, q = rstr(d, q); q += 4; strs.append(s)
    nns = struct.unpack_from('<I', d, p)[0]; p += 4; out = []
    for _ in range(nns):
        nh = struct.unpack_from('<I', d, p)[0]; p += 4
        ns, p = rstr(d, p); nk = struct.unpack_from('<I', d, p)[0]; p += 4; keys = []
        for _ in range(nk):
            kh = struct.unpack_from('<I', d, p)[0]; p += 4
            k, p = rstr(d, p); sh, idx = struct.unpack_from('<Ii', d, p); p += 8
            keys.append((kh, k, sh, idx))
        out.append((nh, ns, keys))
    return out, strs, d[:16]


def write_locres(structure, strs, magic, texts):
    table = []; index = {}; refs = []
    body = b''; total = 0
    for nh, ns, keys in structure:
        body += struct.pack('<I', nh) + wstr(ns) + struct.pack('<I', len(keys))
        for kh, k, sh, idx in keys:
            s = texts.get(ns + SEP + k, strs[idx])
            if s not in index:
                index[s] = len(table); table.append(s); refs.append(0)
            i = index[s]; refs[i] += 1; total += 1
            body += struct.pack('<I', kh) + wstr(k) + struct.pack('<Ii', sh, i)
    head_len = 16 + 1 + 8 + 4 + 4
    soff = head_len + len(body)
    st = struct.pack('<i', len(table)) + b''.join(wstr(s) + struct.pack('<i', r) for s, r in zip(table, refs))
    return magic + bytes([3]) + struct.pack('<qI', soff, total) + struct.pack('<I', len(structure)) + body + st


def read_mod_pak(fn):
    d = open(fn, 'rb').read(); L = len(d)
    i = d.rfind(bytes.fromhex('e1126f5a'), L - 300)
    io, isz = struct.unpack_from('<qq', d, i + 8)
    idx = d[io:io + isz]
    p = 0; mp, p = rstr(idx, p)
    cnt, seed = struct.unpack_from('<iQ', idx, p); p += 12
    p += 4; phi_off, phi_sz = struct.unpack_from('<qq', idx, p); p += 36
    p += 4; fdi_off, fdi_sz = struct.unpack_from('<qq', idx, p); p += 36
    es = struct.unpack_from('<I', idx, p)[0]; p += 4
    enc = idx[p:p + es]
    off, usz = struct.unpack_from('<II', enc, 4)
    loc = d[off + 53:off + 53 + usz]
    return dict(mount=mp, seed=seed, phi=d[phi_off:phi_off + phi_sz], fdi=d[fdi_off:fdi_off + fdi_sz],
                footer_pre=d[i - 17:i], footer_tail=d[i + 44:], locres=loc)


def write_pak(mod, data, out):
    sha = lambda b: hashlib.sha1(b).digest()
    hdr = struct.pack('<QQQI', 0, len(data), len(data), 0) + sha(data) + b'\0' + struct.pack('<I', 0)
    blob = hdr + data
    io = len(blob)
    enc = struct.pack('<III', 0xE0000000, 0, len(data))
    # длина индекса фиксирована: считаем смещения PHI/FDI после него
    def mkidx(phi_off, fdi_off):
        return (wstr(mod['mount']) + struct.pack('<iQ', 1, mod['seed']) +
                struct.pack('<Iqq', 1, phi_off, len(mod['phi'])) + sha(mod['phi']) +
                struct.pack('<Iqq', 1, fdi_off, len(mod['fdi'])) + sha(mod['fdi']) +
                struct.pack('<I', len(enc)) + enc + struct.pack('<I', 0))
    ilen = len(mkidx(0, 0))
    phi_off = io + ilen; fdi_off = phi_off + len(mod['phi'])
    idx = mkidx(phi_off, fdi_off)
    footer = mod['footer_pre'] + bytes.fromhex('e1126f5a') + struct.pack('<Iqq', 11, io, len(idx)) + sha(idx) + mod['footer_tail']
    open(out, 'wb').write(blob + idx + mod['phi'] + mod['fdi'] + footer)


if __name__ == '__main__':
    mod = read_mod_pak(sys.argv[1])
    structure, strs, magic = parse_struct(mod['locres'])
    texts = json.load(open(sys.argv[2], encoding='utf-8'))
    import glob, os
    for ef in sorted(glob.glob(os.path.join('edits', '*.json'))):
        ed = json.load(open(ef, encoding='utf-8'))
        unknown = [k for k in ed if k not in texts]
        assert not unknown, (ef, unknown[:5])
        texts.update(ed); print('правки', ef, len(ed))
    data = write_locres(structure, strs, magic, texts)
    write_pak(mod, data, sys.argv[3])
    print('locres', len(data), 'строк', len(texts))

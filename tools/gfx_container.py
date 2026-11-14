"""Сборка IoStore-контейнера с заменёнными текстурами (по образцу пакета Stage03_Graphics).
Текстура меняется на месте: те же размеры и формат, перезаписываются только байты пикселей.
from gfx_container import build; build(out_base, {путь_в_игре: bytes_pixels_mip0}, base_utoc)
"""
import struct, os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from iostore import IoStore
import zen

BLK = 65536

def texture_layout(d):
    """-> (w, h, pf, data_off_mip0, size_mip0) в байтах пакета."""
    names, hs = zen.names(d)
    pf = [n for n in names if n.startswith('PF_')][0]
    body = hs
    i = d.find(b'PF_', hs)
    slen, = struct.unpack_from('<i', d, i - 4)
    w, h = struct.unpack_from('<II', d, i - 4 - 12)
    p = i + slen          # после строки формата
    p += 4                # FirstMipToSerialize / флаги
    nm, = struct.unpack_from('<i', d, p); p += 4
    p += 4                # флаги bulk data
    if pf == 'PF_B8G8R8A8': size = w * h * 4
    elif pf == 'PF_BC7': size = ((w + 3) // 4) * ((h + 3) // 4) * 16
    else: raise ValueError(pf)
    assert struct.unpack_from('<II', d, p + size) == (w, h), 'размеры после данных не совпали'
    return w, h, pf, p, size

def texture_mips(d):
    """-> список (смещение, размер, w, h) для всех мип-уровней."""
    w, h, pf, off, size = texture_layout(d)
    nm, = struct.unpack_from('<i', d, off - 8)
    out = []; p = off; mw, mh = w, h
    for i in range(nm):
        sz = mw * mh * 4 if pf == 'PF_B8G8R8A8' else ((mw + 3) // 4) * ((mh + 3) // 4) * 16
        assert struct.unpack_from('<II', d, p + sz) == (mw, mh), f'мип {i}: размеры не совпали'
        out.append((p, sz, mw, mh))
        p += sz + 12 + 4          # данные + (w,h,d) + флаги следующего мипа
        mw, mh = max(1, mw // 2), max(1, mh // 2)
    return out

def mapped_names_blob(names, hashes):
    out = struct.pack('<II', len(names), sum(len(n) for n in names)) + struct.pack('<Q', 0xC1640000)
    out += b''.join(struct.pack('<Q', h) for h in hashes)
    out += b''.join(bytes([(len(n) >> 8) & 0x7f, len(n) & 0xff]) for n in names)
    out += b''.join(n.encode('ascii') for n in names)
    return out

def dir_index(paths_to_idx):
    """Простой индекс каталогов: mount '../../../' + дерево."""
    strings = []; sidx = {}
    def S(s):
        if s not in sidx: sidx[s] = len(strings); strings.append(s)
        return sidx[s]
    NONE = 0xFFFFFFFF
    dirs = [[NONE, NONE, NONE, NONE]]  # name, child, sibling, firstfile
    files = []
    def get_dir(parent, name):
        c = dirs[parent][1]
        while c != NONE:
            if dirs[c][0] == S(name): return c
            c = dirs[c][2]
        dirs.append([S(name), NONE, dirs[parent][1], NONE]); dirs[parent][1] = len(dirs) - 1
        return len(dirs) - 1
    for path, idx in paths_to_idx.items():
        parts = path.replace('../../../', '').split('/')
        cur = 0
        for part in parts[:-1]: cur = get_dir(cur, part)
        files.append([S(parts[-1]), dirs[cur][3], idx]); dirs[cur][3] = len(files) - 1
    def fstr(s):
        b = s.encode('utf-8') + b'\0'; return struct.pack('<i', len(b)) + b
    out = fstr('../../../')
    out += struct.pack('<I', len(dirs)) + b''.join(struct.pack('<4I', *x) for x in dirs)
    out += struct.pack('<I', len(files)) + b''.join(struct.pack('<3I', *x) for x in files)
    out += struct.pack('<I', len(strings)) + b''.join(fstr(s) for s in strings)
    return out

def build(out_base, replacements, base_utoc, localized=()):
    """replacements: {путь: новые байты mip0}; localized: [(source_package_id_u64, source_name, name_hash)]"""
    s = IoStore(base_utoc)
    chunks = []  # (chunk_id_bytes, data, path)
    pkg_ids = []
    for path, pixels in replacements.items():
        idx = s.files[path]; d = bytearray(s.read(idx))
        mips = texture_mips(bytes(d))
        if isinstance(pixels, (bytes, bytearray)): pixels = [pixels]
        for (off, size, _, _), px in zip(mips, pixels):
            assert len(px) == size, (path, len(px), size)
            d[off:off + size] = px
        cid = s.ids[idx]; chunks.append((cid, bytes(d), path)); pkg_ids.append(cid[:8])
    container_id = random.getrandbits(64).to_bytes(8, 'little')
    # заголовок контейнера (v5, как у Stage03_Graphics)
    hdr = b'nCoI' + struct.pack('<I', 5) + container_id
    hdr += struct.pack('<I', len(pkg_ids)) + b''.join(pkg_ids)
    hdr += struct.pack('<I', 16 * len(pkg_ids)) + b'\0' * (16 * len(pkg_ids))   # store entries: нет импортов
    hdr += struct.pack('<I', 0) + struct.pack('<I', 0)                          # optional segment
    hdr += mapped_names_blob([n for _, n, _ in localized], [h for _, _, h in localized])
    hdr += struct.pack('<I', len(localized)) + b''.join(struct.pack('<QII', pid, i, 0) for i, (pid, _, _) in enumerate(localized))
    hdr += struct.pack('<I', 0)                                                  # package redirects
    soft_off = len(hdr) + 16
    hdr += struct.pack('<qq', soft_off, 4) + b'\0' * 4                           # soft package refs: нет
    hdr += b'\0' * ((-len(hdr)) % 16)
    chunks.append((container_id + b'\0\0\0\x06', hdr, None))
    # ucas: несжатые блоки по 64К; смещения чанков в несжатом потоке выровнены по 64К
    ucas = bytearray(); blocks = []; offlen = []; ustream = 0
    for cid, data, _ in chunks:
        ustream = (ustream + BLK - 1) // BLK * BLK
        offlen.append((ustream, len(data)))
        for i in range(0, len(data), BLK):
            part = data[i:i + BLK]; blocks.append((len(ucas), len(part), len(part), 0)); ucas += part
        ustream += len(data)
    dix = dir_index({p: i for i, (_, _, p) in enumerate(chunks) if p})
    tmpl = open(os.path.join(os.path.dirname(base_utoc), 'FFRS-Windows.utoc'), 'rb').read(144)
    h = bytearray(tmpl)
    struct.pack_into('<9I', h, 20, 144, len(chunks), len(blocks), 12, 0, 32, BLK, len(dix), 1)
    h[56:64] = container_id; h[64:80] = b'\0' * 16; h[80] = 0x8
    struct.pack_into('<I', h, 84, 0); struct.pack_into('<Q', h, 88, 0xFFFFFFFFFFFFFFFF); struct.pack_into('<I', h, 96, 0)
    toc = bytes(h) + b''.join(c for c, _, _ in chunks)
    toc += b''.join(o.to_bytes(5, 'big') + l.to_bytes(5, 'big') for o, l in offlen)
    toc += b''.join(o.to_bytes(5, 'little') + cs.to_bytes(3, 'little') + us.to_bytes(3, 'little') + bytes([m]) for o, cs, us, m in blocks)
    toc += dix
    toc += b'\0' * (24 * len(chunks))   # мета-хэши чанков (в релизной игре не проверяются)
    open(out_base + '.utoc', 'wb').write(toc); open(out_base + '.ucas', 'wb').write(bytes(ucas))
    return [p for _, _, p in chunks if p]

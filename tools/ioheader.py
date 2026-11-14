"""Разбор заголовка IoStore-контейнера (v5): локализованные пакеты -> {имя_исходного_пакета: (id, hash)}."""
import struct
def localized(store):
    idx = next(i for i, c in enumerate(store.ids) if c[11] == 6)
    d = store.read(idx); p = 4
    ver, = struct.unpack_from('<I', d, p); p += 4 + 8
    n, = struct.unpack_from('<I', d, p); p += 4 + 8 * n
    sz, = struct.unpack_from('<I', d, p); p += 4 + sz              # store entries
    n2, = struct.unpack_from('<I', d, p); p += 4 + 8 * n2           # optional segment package ids
    sz2, = struct.unpack_from('<I', d, p); p += 4 + sz2             # optional segment store entries
    cnt, sbytes, hv = struct.unpack_from('<IIQ', d, p); p += 16
    hashes = struct.unpack_from(f'<{cnt}Q', d, p); p += 8 * cnt
    lens = []
    for i in range(cnt):
        b0, b1 = d[p], d[p + 1]; p += 2
        lens.append(((b0 & 0x7f) << 8) | b1); assert not b0 & 0x80, 'wide name'
    names = []
    for L in lens: names.append(d[p:p + L].decode('ascii')); p += L
    nl, = struct.unpack_from('<I', d, p); p += 4
    out = {}
    for i in range(nl):
        pid, ni, num = struct.unpack_from('<QII', d, p); p += 16
        ni &= 0x3FFFFFFF; out[names[ni]] = (pid, hashes[ni])
    return out

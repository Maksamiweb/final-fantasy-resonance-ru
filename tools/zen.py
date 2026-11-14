"""Мини-разбор Zen-пакета UE5: таблица имён (name map)."""
import struct
def names(d):
    has_ver, hsize = struct.unpack_from('<II', d, 0)
    p = 4 + 4 + 8 + 4 + 4 + 4 * 8  # summary до конца смещений
    # summary: bHasVersioningInfo, HeaderSize, Name(8), PackageFlags, CookedHeaderSize,
    # ImportedPublicExportHashesOffset, ImportMapOffset, ExportMapOffset, ExportBundleEntriesOffset,
    # DependencyBundleHeadersOffset, DependencyBundleEntriesOffset, ImportedPackageNamesOffset
    p = 4 + 4 + 8 + 4 + 4 + 4 * 9
    if has_ver:
        # ZenVersion u32, FileVersionUE4 i32, FileVersionUE5 i32, LicenseeVersion u32, CustomVersions TArray<FCustomVersion(20)>
        p += 4 + 4 + 4 + 4
        n, = struct.unpack_from('<i', d, p); p += 4 + 20 * n
    cnt, nbytes = struct.unpack_from('<II', d, p); p += 8
    p += 8  # hash version
    p += 8 * cnt
    hdr = [(d[p + 2 * i], d[p + 2 * i + 1]) for i in range(cnt)]; p += 2 * cnt
    out = []
    for b0, b1 in hdr:
        wide = b0 & 0x80; L = ((b0 & 0x7f) << 8) | b1
        if wide:
            out.append(d[p:p + 2 * L].decode('utf-16-le', 'replace')); p += 2 * L
        else:
            out.append(d[p:p + L].decode('latin-1')); p += L
    return out, hsize

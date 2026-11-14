"""49 скриншотов справки (L10N/en) -> tut/dds/*.dds (все мипы) -> tut/png/*.png (mip0)."""
import sys, os, struct, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from iostore import IoStore
from gfx_container import texture_layout, texture_mips
UTOC = r'D:\SteamLibrary\steamapps\common\FINAL FANTASY RESONANCE\FFRS\Content\Paks\FFRS-Windows.utoc'
def dds(w, h, nm, data, fmt=98):  # 98 = BC7_UNORM, DX10-заголовок
    hdr = struct.pack('<4sI6I44x', b'DDS ', 124, 0x1|0x2|0x4|0x1000|0x20000|0x80000, h, w, len(data[0]), 0, nm)
    hdr += struct.pack('<2I4s5I', 32, 4, b'DX10', 0, 0, 0, 0, 0)
    hdr += struct.pack('<5I', 0x1000|0x400000|0x8, 0, 0, 0, 0)
    hdr += struct.pack('<5I', fmt, 3, 0, 1, 0)
    return hdr + b''.join(data)
if __name__ == '__main__':
    s = IoStore(UTOC); info = {}
    paths = sorted(p for p in s.files if 'L10N/en/UI/Textures/Tutorial' in p)
    for p in paths:
        d = s.read(s.files[p]); w, h, pf, off, size = texture_layout(d); mips = texture_mips(d)
        n = p.split('/')[-1][:-7]; info[n] = (p, w, h, pf, len(mips))
        open(f'tut/dds/{n}.dds', 'wb').write(dds(w, h, len(mips), [d[o:o+sz] for o, sz, _, _ in mips]))
    json.dump(info, open('tut/info.json', 'w'), indent=0)
    subprocess.run([os.path.abspath('tools/texconv.exe'), '-nologo', '-y', '-m', '1', '-ft', 'png', '-f', 'R8G8B8A8_UNORM', '-o', os.path.abspath('tut/png')] + [os.path.abspath(f'tut/dds/{n}.dds') for n in info], check=True, stdout=subprocess.DEVNULL)
    for n, v in info.items(): print(n, v[1:])

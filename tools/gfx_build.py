"""Сборка графического контейнера русификатора FFRS-Windows_FULL_RU_Stage05_Gfx_18000_P (.utoc/.ucas/.pak).
Содержимое: надписи Азартного выстрела (6), «ЗАЖИГАНИЕ!», логотип «ПРОБИТИЕ», 49 скриншотов справки.
python -I tools/gfx_build.py"""
import sys, os, json, struct, subprocess, shutil, glob
sys.path.insert(0, os.path.dirname(__file__))
from iostore import IoStore
from gfx_container import build, texture_mips
import ioheader
from PIL import Image
PAKS = r'D:\SteamLibrary\steamapps\common\FINAL FANTASY RESONANCE\FFRS\Content\Paks'
BASE = os.path.join(PAKS, 'FFRS-Windows.utoc')
OUT = 'build/gfx/FFRS-Windows_FULL_RU_Stage05_Gfx_18000_P'
TEXCONV = os.path.abspath('tools/texconv.exe')
G = '../../../FFRS/Content/'
s = IoStore(BASE); loc = ioheader.localized(s)

def dds_mips(path, sizes):
    d = open(path, 'rb').read(); p = 148 if d[84:88] == b'DX10' else 128; out = []
    for sz in sizes: out.append(d[p:p + sz]); p += sz
    return out
def bgra(png, w, h):
    im = Image.open(png).convert('RGBA'); assert im.size == (w, h), (png, im.size)
    r, g, b, a = im.split(); return Image.merge('RGBA', (b, g, r, a)).tobytes()
def bc7(png, tmp='build/gfx/tmp'):
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([TEXCONV, '-nologo', '-y', '-f', 'BC7_UNORM', '-m', '1', '-bc', 'q', '-o', os.path.abspath(tmp), os.path.abspath(png)], check=True, stdout=subprocess.DEVNULL)
    return os.path.join(tmp, os.path.splitext(os.path.basename(png))[0] + '.dds')

rep = {}; localized = []
def add(path, data, l10n_src=None):
    rep[path] = data
    if l10n_src: pid, h = loc[l10n_src]; localized.append((pid, l10n_src, h))
def mips_of(path): return [sz for _, sz, _, _ in texture_mips(s.read(s.files[path]))]

# 1. Азартный выстрел (все мипы, BC7, готовые DDS)
for w in ('Good', 'Excellent', 'Amazing'):
    for kind in ('Text', 'TextGlow'):
        p = G + f'UI/Textures/Skill_2Dtex/T_Gambleshot_{w}_{kind}.uasset'
        add(p, dds_mips(f'tex/bc7/ru_T_Gambleshot_{w}_{kind}.dds', mips_of(p)))
# 2. «ЗАЖИГАНИЕ!»
p = G + 'L10N/en/UI/Textures/Skill_2Dtex/T_404031_message_01.uasset'
add(p, bgra('tex/T_404031_message_01_ru.png', 134, 24), '/Game/UI/Textures/Skill_2Dtex/T_404031_message_01')
# 3. Логотип «ПРОБИТИЕ» (было «ОШЕЛОМЛЁН», в тексте игры — «пробитие»)
p = G + 'L10N/en/UI/Textures/menu/T_Btl_Logo_Break.uasset'
add(p, bgra('tut/mod/T_Btl_Logo_Break_ru.png', 512, 128), '/Game/UI/Textures/Menu/T_Btl_Logo_Break')
# 4. Скриншоты справки
info = json.load(open('tut/info.json'))
for n, (path, w, h, pf, nm) in info.items():
    src = f'/Game/UI/Textures/Tutorial/{n}'
    if pf == 'PF_B8G8R8A8': data = bgra(f'tut/ru/{n}.png', w, h)
    else: data = dds_mips(bc7(f'tut/ru/{n}.png'), mips_of(path))
    add(path, data, src)
print('текстур:', len(rep), 'локализованных:', len(localized))
build(OUT, rep, BASE, localized)
if not os.path.exists(OUT + '.pak'):
    shutil.copy('base/FFRS-Windows_FULL_RU_Stage03_Graphics_16002_P.pak', OUT + '.pak')
for e in ('.utoc', '.ucas', '.pak'): print(OUT + e, os.path.getsize(OUT + e))

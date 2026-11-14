"""Замена английских надписей на скриншотах справки.
spec: {имя: [[x0,y0,x1,y1, 'русский', {опции}], ...]}  — рамка английского текста (из OCR, правится вручную).
опции: f=шрифт(sans|med|serif), s=кегль, c=(r,g,b), a=выравнивание(l|c|r), w=доступная ширина, e=доп. поля стирания [l,t,r,b],
       noerase, dy, sh=тень, h=высота заглавных."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONTS = {'sans': 'fonts/BO-UDShinGoNTPr6N-Reg.otf', 'med': 'fonts/BO-UDShinGoNTPr6N-Medium.otf',
         'serif': 'fonts/SE-GARRITHR.otf', 'bold': 'fonts/BO-FolkPro-Bold.otf', 'ryu': 'fonts/BO-RyuminPr6N-Bold.otf'}
def lum(p): return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
def erase(im, x0, y0, x1, y1):
    """Заливка прямоугольника билинейной интерполяцией от его границ (фон UI — плавные градиенты)."""
    px = im.load(); W, H = im.size
    x0 = max(1, x0); y0 = max(1, y0); x1 = min(W - 2, x1); y1 = min(H - 2, y1)
    top = [px[x, y0 - 1] for x in range(x0, x1 + 1)]; bot = [px[x, y1 + 1] for x in range(x0, x1 + 1)]
    lef = [px[x0 - 1, y] for y in range(y0, y1 + 1)]; rig = [px[x1 + 1, y] for y in range(y0, y1 + 1)]
    w = x1 - x0 + 2; h = y1 - y0 + 2
    for j, y in enumerate(range(y0, y1 + 1)):
        v = (j + 1) / h
        for i, x in enumerate(range(x0, x1 + 1)):
            u = (i + 1) / w
            a = [(1 - u) * lef[j][k] + u * rig[j][k] for k in range(3)]
            b = [(1 - v) * top[i][k] + v * bot[i][k] for k in range(3)]
            wu = min(u, 1 - u); wv = min(v, 1 - v)       # ближе к какой границе — та и весомее
            t = wv / (wu + wv + 1e-6)
            px[x, y] = tuple(int(t * a[k] + (1 - t) * b[k]) for k in range(3)) + ((px[x, y][3],) if len(px[x, y]) == 4 else ())
def text_color(im, x0, y0, x1, y1):
    px = im.load(); ring = [px[x, y] for x in range(x0 - 2, x1 + 3) for y in (y0 - 2, y1 + 2)] + [px[x, y] for y in range(y0, y1 + 1) for x in (x0 - 2, x1 + 2)]
    ring = sorted(ring, key=lum); bg = ring[len(ring) // 2]
    ins = sorted((px[x, y] for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)), key=lambda p: -abs(lum(p) - lum(bg)))
    top = ins[:max(3, len(ins) // 12)]
    return tuple(sum(p[k] for p in top) // len(top) for k in range(3)), bg
def cap_metrics(im, x0, y0, x1, y1, bg):
    """Высота и верх заглавной по первой букве оригинала."""
    px = im.load(); bl = lum(bg)
    d = [[abs(lum(px[x, y]) - bl) for x in range(x0, x1 + 1)] for y in range(y0, y1 + 1)]
    mx = max(max(r) for r in d) or 1; thr = mx * 0.45
    cols = [any(d[j][i] > thr for j in range(len(d))) for i in range(len(d[0]))]
    i = cols.index(True) if True in cols else 0; k = i
    while k < len(cols) and cols[k]: k += 1
    rows = [j for j in range(len(d)) if any(d[j][c] > thr for c in range(i, max(i + 1, k)))]
    if not rows: return y1 - y0, y0
    return rows[-1] - rows[0] + 1, y0 + rows[0]
def snap(im, x0, y0, x1, y1, thr=0.42):
    """Свободная рамка -> плотная рамка текста (пиксели, контрастные к медиане краёв)."""
    px = im.load()
    ring = sorted([px[x, y] for x in range(x0, x1 + 1) for y in (y0, y1)] + [px[x, y] for y in range(y0, y1 + 1) for x in (x0, x1)], key=lum)
    bl = lum(ring[len(ring) // 2])
    d = {(x, y): abs(lum(px[x, y]) - bl) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    mx = max(d.values()) or 1
    pts = [p for p, v in d.items() if v > mx * thr]
    if not pts: return x0, y0, x1, y1
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)
def wrap(txt, fname, h, width):
    rf = ImageFont.truetype(fname, 100); rb = rf.getbbox('Н'); f = ImageFont.truetype(fname, max(6, round(h / ((rb[3] - rb[1]) / 100))))
    out = []
    for para in txt.split(chr(10)):
        line = ''
        for w in para.split(' '):
            t = (line + ' ' + w).strip()
            if f.getlength(t) <= width or not line: line = t
            else: out.append(line); line = w
        out.append(line)
    return chr(10).join(out)
def render(im, x0, y0, x1, y1, txt, o):
    W, H = im.size
    if 'wrap' in o: txt = wrap(txt, FONTS[o.get('f', 'sans')], o['h'], o['wrap']); o = {k: v for k, v in o.items() if k != 'wrap'}
    if chr(10) in txt:     # абзац: стереть рамку целиком, строки рисовать по отдельности
        lines = txt.split(chr(10)); h = o['h']; lh = o.get('lh', round(h * 1.9)); ty = o.get('ty', y0)
        col = o.get('c') or text_color(im, *snap(im, x0, y0, x1, y1))[0]
        if not o.get('noerase'):
            e = o.get('e', [2, 2, 2, 2]); erase(im, x0 - e[0], y0 - e[1], x1 + e[2], y1 + e[3])
        for i, ln in enumerate(lines):
            oo = dict(o); oo.update(noerase=True, snap=False, h=h, ty=ty + i * lh, c=col)
            render(im, x0, ty + i * lh, x1, ty + i * lh + h, ln, oo)
        return
    if o.get('snap', True): x0, y0, x1, y1 = snap(im, x0, y0, x1, y1, o.get('thr', 0.42))
    if txt == '' or txt.startswith('@'):
        e = o.get('e', [2, 2, 2, 2])
        if not o.get('noerase'): erase(im, x0 - e[0], y0 - e[1], x1 + e[2], y1 + e[3])
        if txt.startswith('@'):     # '@путь.png': картинка (логотип) по центру рамки, высота o['ih']
            lg = Image.open(txt[1:]).convert('RGBA'); k = o['ih'] / lg.height
            lg = lg.resize((round(lg.width * k), o['ih']), Image.LANCZOS)
            cx, cy = (x0 + x1) // 2 + o.get('dx', 0), (y0 + y1) // 2 + o.get('dy', 0)
            im.alpha_composite(lg, (cx - lg.width // 2, cy - lg.height // 2))
        return
    col, bg = text_color(im, x0, y0, x1, y1)
    capH, capY = cap_metrics(im, x0, y0, x1, y1, bg)
    if 'h' in o: capH = o['h']; capY = y0
    if o.get('up'): txt = txt.upper()
    if 'ty' in o: capY = o['ty']
    col = tuple(o.get('c', col))
    e = o.get('e', [2, 2, 2, 2])
    if not o.get('noerase'): erase(im, x0 - e[0], y0 - e[1], x1 + e[2], y1 + e[3])
    fname = FONTS[o.get('f', 'sans')]
    rf = ImageFont.truetype(fname, 100); rb = rf.getbbox('Н'); ratio = (rb[3] - rb[1]) / 100
    size = o.get('s') or max(6, round(capH / ratio))
    avail = o.get('w', max(x1 - x0 + 12, (x1 - x0) * 1.25))
    while True:
        f = ImageFont.truetype(fname, size); l, t, r, b = f.getbbox(txt)
        tw = r - l; sx = 1.0
        if tw > avail: sx = max(0.78, avail / tw)
        if tw * sx <= avail or size <= 7: break
        size -= 1
    caps_t = f.getbbox('Н')[1]
    S = 4   # суперсэмплинг
    fb = ImageFont.truetype(fname, size * S)
    l, t, r, b = fb.getbbox(txt)
    m = Image.new('L', (r - l + 8 * S, size * 2 * S), 0)
    ImageDraw.Draw(m).text((4 * S - l, 0), txt, font=fb, fill=255)
    m = m.resize((max(1, round(m.width * sx / S)), m.height // S), Image.LANCZOS)
    a = o.get('a', 'l'); tw = m.width - 8
    ox = {'l': x0, 'c': (x0 + x1 - tw) // 2, 'r': x1 - tw}[a] - 4
    cap_top = caps_t
    hb = f.getbbox('Н'); ch = hb[3] - hb[1]
    oy = capY - cap_top + o.get('dy', 0)
    if o.get('it'):
        k = o['it']; m = m.transform((m.width + round(m.height * k), m.height), Image.AFFINE, (1, k, -k * m.height, 0, 1, 0), Image.BICUBIC)
    if o.get('ol'):
        ow = o.get('olw', 1); om = m.filter(ImageFilter.MaxFilter(2 * ow + 1))
        ol = Image.new('RGBA', m.size, tuple(o['ol']) + (255,)); ol.putalpha(om)
        if im.mode == 'RGBA': im.alpha_composite(ol, (max(0, ox), max(0, oy)))
    if o.get('sh'):
        sm = m.filter(ImageFilter.GaussianBlur(1)); shadow = Image.new('RGBA', m.size, (0, 0, 0, 255)); shadow.putalpha(sm.point(lambda v: v * 0.8))
        im.alpha_composite(shadow, (ox + 1, oy + 1)) if im.mode == 'RGBA' else im.paste(shadow, (ox + 1, oy + 1), shadow)
    layer = Image.new('RGBA', m.size, col + (255,)); layer.putalpha(m)
    if im.mode == 'RGBA': im.alpha_composite(layer, (max(0, ox), max(0, oy)))
    else: im.paste(layer, (ox, oy), layer)
def apply(name, items, src='tut/png', dst='tut/ru'):
    im = Image.open(f'{src}/{name}.png').convert('RGBA')
    for it in items:
        x0, y0, x1, y1, txt = it[:5]; o = it[5] if len(it) > 5 else {}
        keep = None
        if 'clip' in o:
            cb = (o['clip'], max(0, y0 - 8), im.width, min(im.height, y1 + 8)); keep = (cb, im.crop(cb))
        prot = [(r, im.crop(r)) for r in o.get('protect', [])]
        render(im, x0, y0, x1, y1, txt, o)
        if keep: im.paste(keep[1], keep[0][:2])
        for r, c in prot: im.paste(c, r[:2])
    os.makedirs(dst, exist_ok=True); im.save(f'{dst}/{name}.png'); return im

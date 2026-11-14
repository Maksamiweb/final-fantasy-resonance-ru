"""Рисует русские надписи Азартного выстрела в стиле оригинала."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
FONT = 'fonts/BO-FolkPro-Bold.otf'
WORDS = {'Good': 'ХОРОШО', 'Excellent': 'ОТЛИЧНО!', 'Amazing': 'ПОТРЯСНО!!'}
def bbox_alpha(im, thr=40):
    a = im.split()[3].point(lambda v: 255 if v > thr else 0); return a.getbbox()
def color_of(im, white=False):
    px = im.load(); w, h = im.size; acc = [0, 0, 0, 0]
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a > 120 and not (r > 220 and g > 220 and b > 220):
                acc[0] += r * a; acc[1] += g * a; acc[2] += b * a; acc[3] += a
    return tuple(int(c / acc[3]) for c in acc[:3]) if acc[3] else (255, 0, 0)
def text_mask(txt, size, box_w, box_h, shear=0.22):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(txt)
    m = Image.new('L', (r - l + int(size * 0.6) + 40, b - t + 40), 0)
    ImageDraw.Draw(m).text((20 - l + int(size * 0.3), 20 - t), txt, font=f, fill=255)
    m = m.transform(m.size, Image.AFFINE, (1, shear, -shear * m.size[1] / 2, 0, 1, 0), Image.BICUBIC)
    return m.crop(m.getbbox())
def fit_mask(txt, box_w, box_h):
    size = box_h * 2
    while size > 10:
        m = text_mask(txt, size, box_w, box_h)
        if m.height <= box_h:
            if m.width > box_w and box_w / m.width >= 0.72:      # сжать по горизонтали, сохранив высоту
                m = m.resize((box_w, m.height), Image.LANCZOS)
            if m.width <= box_w:
                return m.filter(ImageFilter.MaxFilter(3))          # чуть жирнее, как оригинал
        size -= 2
    return text_mask(txt, 10, box_w, box_h)
def draw(word, orig_text, orig_glow, out_text, out_glow):
    ot = Image.open(orig_text).convert('RGBA'); og = Image.open(orig_glow).convert('RGBA')
    cglow = color_of(og); ctext = tuple(int(c * 0.8) for c in cglow)
    x0, y0, x1, y1 = bbox_alpha(ot)
    pad = max(6, min(x0, ot.size[0] - x1, 16)); x0, x1 = pad, ot.size[0] - pad
    stroke = max(3, (y1 - y0) // 18)
    m = fit_mask(WORDS[word], x1 - x0 - 2 * stroke, y1 - y0 - 2 * stroke)
    W, H = ot.size
    mask = Image.new('L', (W, H), 0)
    mx = x0 + ((x1 - x0) - m.width) // 2; my = y0 + ((y1 - y0) - m.height) // 2
    mask.paste(m, (mx, my))
    outline = mask.filter(ImageFilter.MaxFilter(stroke * 2 + 1))
    soft = outline.filter(ImageFilter.GaussianBlur(stroke))
    img = Image.new('RGBA', (W, H), ctext + (0,))
    img.putalpha(ImageChops.lighter(outline, soft.point(lambda v: int(v * 0.8))))
    white = Image.new('RGBA', (W, H), (255, 255, 255, 255)); white.putalpha(mask)
    img = Image.alpha_composite(img, white); img.save(out_text)
    gx0, gy0, gx1, gy1 = bbox_alpha(og, 20); gx0, gx1 = 10, og.size[0] - 10
    gm = fit_mask(WORDS[word], int((gx1 - gx0) * 0.86), int((gy1 - gy0) * 0.70))
    gmask = Image.new('L', og.size, 0)
    gmask.paste(gm, (gx0 + ((gx1 - gx0) - gm.width) // 2, gy0 + ((gy1 - gy0) - gm.height) // 2))
    blur = max(4, (gy1 - gy0) // 14)
    ga = gmask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(blur))
    gl = Image.new('RGBA', og.size, cglow + (0,)); gl.putalpha(ga.point(lambda v: min(255, int(v * 1.3)))); gl.save(out_glow)
    return ctext, cglow
if __name__ == '__main__':
    for w in WORDS:
        print(w, draw(w, f'tex/gamble/T_Gambleshot_{w}_Text.png', f'tex/gamble/T_Gambleshot_{w}_TextGlow.png',
                      f'tex/gamble/ru_T_Gambleshot_{w}_Text.png', f'tex/gamble/ru_T_Gambleshot_{w}_TextGlow.png'))

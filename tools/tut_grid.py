"""Увеличенные фрагменты с сеткой координат: python tools/tut_grid.py out.png имя:x0,y0,x1,y1:k ..."""
import sys
from PIL import Image, ImageDraw
def g(n, box, k):
    im = Image.open(f'tut/png/{n}.png').convert('RGB').crop(box); im = im.resize((im.width * k, im.height * k), Image.NEAREST); d = ImageDraw.Draw(im)
    for x in range(box[0] - box[0] % 10, box[2], 10):
        if x >= box[0]: d.line([((x - box[0]) * k, 0), ((x - box[0]) * k, 5)], fill=(255, 0, 0)); d.text(((x - box[0]) * k + 1, 6), str(x % 1000), fill=(255, 90, 90))
    for y in range(box[1] - box[1] % 10, box[3], 10):
        if y >= box[1]: d.line([(0, (y - box[1]) * k), (5, (y - box[1]) * k)], fill=(0, 255, 0)); d.text((6, (y - box[1]) * k + 1), str(y), fill=(90, 255, 90))
    return im
ims = []
for a in sys.argv[2:]:
    n, b, k = a.split(':'); ims.append(g('T_Tutorial_' + n, tuple(map(int, b.split(','))), int(k)))
W = max(i.width for i in ims); H = sum(i.height + 4 for i in ims)
sh = Image.new('RGB', (W, H)); y = 0
for i in ims: sh.paste(i, (0, y)); y += i.height + 4
sh.save(sys.argv[1]); print(sh.size)

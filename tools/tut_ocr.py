"""OCR всех скриншотов справки -> tut/ocr.json {имя: [[x0,y0,x1,y1,текст,[слова]]]}"""
import sys, json, asyncio, glob, os
from PIL import Image
import winocr
S = 2
async def one(p):
    out = []
    for S in (2, 1):
        for l in await one_s(p, S):
            if not any(min(l[2], o[2]) - max(l[0], o[0]) > 0.5 * (l[2] - l[0]) and min(l[3], o[3]) - max(l[1], o[1]) > 0.5 * (l[3] - l[1]) for o in out):
                out.append(l)
    return out
async def one_s(p, S):
    im = Image.open(p).convert('RGB'); big = im.resize((im.width * S, im.height * S), Image.LANCZOS)
    r = await winocr.recognize_pil(big, 'en'); out = []
    for l in r.lines:
        ws = [(w.bounding_rect.x / S, w.bounding_rect.y / S, (w.bounding_rect.x + w.bounding_rect.width) / S, (w.bounding_rect.y + w.bounding_rect.height) / S, w.text) for w in l.words]
        out.append([min(w[0] for w in ws), min(w[1] for w in ws), max(w[2] for w in ws), max(w[3] for w in ws), l.text, ws])
    return out
async def main():
    res = {}
    for p in sorted(glob.glob('tut/png/*.png')): res[os.path.basename(p)[:-4]] = await one(p)
    json.dump(res, open('tut/ocr.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(sum(len(v) for v in res.values()), 'строк')
asyncio.run(main())

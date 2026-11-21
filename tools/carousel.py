"""Surgeon/doctor story carousel helpers (1080x1350)."""
import sys
sys.path.insert(0, "/home/claude")
from brand import *
from PIL import Image, ImageOps, ImageDraw

W, H = 1080, 1350; MW = W - 160

def slide(tag, n, total, name, series="Surgeon Stories"):
    return base(W, H, tag, f"{series} · {name}", f"{n} / {total}", footer_y=H - 110, mint_top=H - 160)

def cover(name, years, tagline, photo=None, crop=None, total=6, short=None, tag="SURGEON STORIES", wide=False, wide_h=600):
    im, d = slide(tag, 1, total, short or name.split()[-1], "Nobel Laureates" if tag == "NOBEL LAUREATES" else "Surgeon Stories")
    pw, ph_h = (MW, wide_h) if wide else (466, 604); px = (W - pw) // 2; py = 175
    d.rounded_rectangle([px - 10, py - 10, px + pw + 10, py + ph_h + 10], 36, fill=CARD, outline=RULE, width=3)
    if photo:
        p = Image.open(photo).convert("L")
        if crop: p = p.crop(crop)
        p = ImageOps.fit(p, (pw, ph_h), method=Image.LANCZOS, centering=(0.5, 0.5 if wide else 0.35))
        p = ImageOps.colorize(p, black=(40, 36, 32), white=(250, 244, 234))
        mask = Image.new("L", (pw, ph_h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph_h - 1], 28, fill=255)
        im.paste(p, (px, py), mask)
    else:
        d.text((W // 2, py + ph_h // 2 - 20), f"Add {short or name.split()[-1]}'s portrait", font=sans(38, "Medium"), fill=MUTED, anchor="mm")
        d.text((W // 2, py + ph_h // 2 + 35), "send it to me and I'll place it", font=sans(30), fill=MUTED, anchor="mm")
    f = serif(104)
    while d.textlength(name, font=f) > MW: f = serif(f.size - 6)
    d.text((80, 800), name, font=f, fill=FG)
    d.text((80, 940), years, font=sans(44, "Medium"), fill=TERRA)
    para(d, 80, 1010, tagline, ital(58), SAGE, MW, 8)
    return im

def find_border_crop(path, thresh=40, margin=4):
    """Crop a dark picture frame if present."""
    g = Image.open(path).convert("L"); w, h = g.size
    def inner(seq):
        i = 0
        while i < len(seq) and seq[i] > 200: i += 1          # white outside
        j = i
        while j < len(seq) and seq[j] < thresh: j += 1       # dark frame
        return j + margin if j > i and j - i < 40 else 0
    l = inner([g.getpixel((x, h // 2)) for x in range(w)]); r = inner([g.getpixel((w - 1 - x, h // 2)) for x in range(w)])
    t = inner([g.getpixel((w // 2, y)) for y in range(h)]); b = inner([g.getpixel((w // 2, h - 1 - y)) for y in range(h)])
    return (l, t, w - r, h - b)

def photo_slide(name, short, photo, n, total, caption, credit, tag="SURGEON STORIES", crop=None, box_h=860):
    """Last slide: the same portrait shown whole (original tones), with the source's credit line."""
    series = "Nobel Laureates" if tag == "NOBEL LAUREATES" else "Surgeon Stories"
    im, d = slide("PHOTO", n, total, short or name.split()[-1], series)
    p = Image.open(photo).convert("RGB")
    if crop: p = p.crop(crop)
    box_w = MW
    p = ImageOps.contain(p, (box_w, box_h), method=Image.LANCZOS)
    pw, ph = p.size; px = (W - pw) // 2; py = 170
    d.rounded_rectangle([px - 10, py - 10, px + pw + 10, py + ph + 10], 30, fill=CARD, outline=RULE, width=3)
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 22, fill=255)
    im.paste(p, (px, py), mask)
    y = py + ph + 40
    y = para(d, 80, y, caption, ital(44), FG, MW, 8) + 14
    para(d, 80, y, "Photo: " + credit, sans(30, "Medium"), MUTED, MW, 6)
    return im

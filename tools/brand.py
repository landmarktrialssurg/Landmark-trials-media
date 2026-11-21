"""Shared brand helpers for Landmark Trials posts (cream / sage / terracotta, Fraunces + DM Sans)."""
from PIL import Image, ImageDraw, ImageFont
import textwrap

import os as _os
def _hex(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
# Pastel background per organ: (background, top-right circle, bottom-left circle)
THEMES = {
    "Pancreas":         ("F6F0E7", "EADFCF", "E3ECE5"),   # warm cream (original)
    "Biliary":          ("FBF5DC", "F1E4B8", "E8EFD9"),   # butter yellow
    "Upper GI":         ("E9F0F7", "D6E3F0", "F3E9E1"),   # powder blue
    "Colorectal":       ("F1ECF6", "E2D8EE", "E6F0EA"),   # lavender
    "Emergency":        ("FAEAE6", "F2D6CF", "EAF1EC"),   # blush
    "Liver transplant": ("E8F3EC", "D3E8DA", "F5EEDF"),   # mint
    "Hepatology":       ("E5F2F2", "CDE5E5", "F6EDE3"),   # aqua
    "Liver surgery":    ("FCEFE4", "F2DCC8", "E7F0EA"),   # peach
    "Peritoneum":       ("F0F3E3", "DFE6C5", "F5EBE6"),   # pistachio
    "Neuroendocrine":   ("F9ECF1", "EED6E1", "E8F0EC"),   # rose
}
ORGAN = _os.environ.get("ORGAN", "Pancreas")
_t = THEMES[ORGAN]
BG = _hex(_t[0]); FG = (47, 58, 74); MUTED = (95, 107, 120)
SAGE = (70, 112, 95); TERRA = (196, 111, 85); OCHRE = (154, 116, 56)
SAND = _hex(_t[1]); MINT = _hex(_t[2]); CARD = (255, 252, 247); RULE = (220, 208, 190)
F = "/home/claude/render/fonts/"
_cache = {}
def _f(name, s):
    k = (name, s)
    if k not in _cache: _cache[k] = ImageFont.truetype(F + name + ".ttf", s)
    return _cache[k]
def sans(s, w="Regular"): return _f("DMSans-" + w, s)
def serif(s): return _f("Fraunces-SemiBold", s)
def ital(s): return _f("Fraunces-MediumItalic", s)

def text_w(d, t, f): return d.textlength(t, font=f)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def para(d, x, y, text, f, fill, maxw, gap=12):
    for line in wrap(d, text, f, maxw):
        d.text((x, y), line, font=f, fill=fill); y += f.size + gap
    return y

def base(W, H, tag, footer_l, footer_r="For education only", footer_y=None, mint_top=None):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    if POP: d.ellipse([W - 360, -260, W + 260, 360], fill=HL, outline=INK, width=5)
    else: d.ellipse([W - 360, -260, W + 260, 360], fill=SAND)
    mt = mint_top if mint_top is not None else H - 300
    d.ellipse([-320, mt, 300, mt + 620], fill=MINT)
    d.text((80, 110), tag, font=sans(34, "SemiBold"), fill=SAGE)
    fy = footer_y if footer_y is not None else H - 360
    d.text((80, fy), footer_l, font=sans(32, "Medium"), fill=MUTED)
    d.text((W - 80, fy), footer_r, font=sans(32, "Medium"), fill=MUTED, anchor="ra")
    return im, d

# Stomach (Upper GI) "pop" accent: bright yellow fill + black border, max 1-2 per slide.
# Never yellow text. Elsewhere these helpers fall back to the calm pastel look.
POP = ORGAN == "Upper GI"
HL = (255, 214, 10); INK = (20, 20, 20)

def highlight(d, x, y, text, f, pad=10):
    """Highlighter strip behind one line of text (black text on yellow)."""
    if POP:
        tw = d.textlength(text, font=f)
        d.rectangle([x - pad, y - 2, x + tw + pad, y + f.size + 22], fill=HL)
        d.text((x, y), text, font=f, fill=INK)
    else:
        d.text((x, y), text, font=f, fill=SAGE)
    return y + f.size + 22

def popcard(d, box, r=28, on=True, color=None):
    """Card with black border + hard shadow; yellow fill when on=True (the key result)."""
    x0, y0, x1, y1 = box
    if POP:
        d.rounded_rectangle([x0 + 8, y0 + 8, x1 + 8, y1 + 8], r, fill=INK)
        d.rounded_rectangle(box, r, fill=HL if on else CARD, outline=INK, width=5)
    else:
        d.rounded_rectangle(box, r, fill=CARD, outline=color or SAGE, width=4)

def bullets(d, x, y, items, f, maxw, color=SAGE, gap=12, between=34):
    """items: list of str or (str, color)."""
    for it in items:
        t, c = (it, color) if isinstance(it, str) else it
        d.ellipse([x, y + f.size * 0.38, x + 18, y + f.size * 0.38 + 18], fill=c)
        y = para(d, x + 44, y, t, f, FG, maxw - 44, gap) + between
    return y

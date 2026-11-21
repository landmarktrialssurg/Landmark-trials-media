"""Motion Reel engine (our style): word-synced captions with key-word highlights,
subtle eased animations, chapter colours, forest-plot progress bar."""
import os, sys, math, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude")
from brand import *
import reelkit
from PIL import Image, ImageDraw

W, H, FPS = 1080, 1920, 30
INKBG = (38, 48, 62)          # deep ink chapter background
CREAM = (250, 246, 236)

def mix(a, b, t):
    t = max(0.0, min(1.0, t)); return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def ease(t):  # easeOutCubic, clamped
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def ramp(t, start, dur=0.45): return ease((t - start) / dur)

class Scene:
    def __init__(self, bg, beats, draw=None, dark=False, hold=0.0):
        self.bg, self.beats, self.draw, self.dark, self.hold = bg, beats, draw, dark, hold
        # beat = (speech, caption)  — caption words wrapped in *...* are key words

# ---------------- audio ----------------
def synth(text, idx, workdir):
    """Expressive Voice 3 (sentence-level pace/pitch variation) — same engine as the guideline Reels."""
    a, sr = reelkit.speak(text, workdir, idx)
    return a.astype(np.float32), sr

def build_audio(scenes, workdir, lead=0.35, gap=0.16, outro=True):
    sr = 24000; chunks = []; t = 0.0; idx = 0
    for si, sc in enumerate(scenes):
        sc.start = t; sc.beat_t = []
        chunks.append(np.zeros(int(lead * sr), np.float32)); t += lead
        beats = list(sc.beats)
        if outro and si == len(scenes) - 1:
            beats.append((reelkit.OUTRO, reelkit.OUTRO))
            sc.beats = beats
        for sp, cap in beats:
            a, sr = synth(sp, idx, workdir); idx += 1
            d = len(a) / sr
            sc.beat_t.append((t, t + d)); chunks.append(a); t += d
            chunks.append(np.zeros(int(gap * sr), np.float32)); t += gap
        chunks.append(np.zeros(int(sc.hold * sr), np.float32)); t += sc.hold
        sc.end = t
    tail = np.zeros(int(0.5 * sr), np.float32); chunks.append(tail); scenes[-1].end = t + 0.5
    audio = np.concatenate(chunks); sf.write(f"{workdir}/voice.wav", audio, sr)
    for sc in scenes:
        sc.dur = sc.end - sc.start
        sc.beat_t = [(a - sc.start, b - sc.start) for a, b in sc.beat_t]
    return f"{workdir}/voice.wav", scenes[-1].end

# ---------------- captions ----------------
CAP_F = None
def caption(d, text, t0, t1, t, bg, dark, accent, accent_ink, y_mid=1330, maxw=840, f=None):
    """Whole phrase shown faint; words fill in as spoken; *key* words get an accent box."""
    f = f or (serif(66) if len(text) < 95 else serif(54))
    if len(text) >= 95: y_mid -= 40
    toks = text.split(); words = []
    for w in toks:
        key = w.startswith("*") or w.endswith("*") or w.strip("*.,:;?!").startswith("*")
        clean = w.replace("*", ""); words.append((clean, "*" in w))
    # line layout
    lines, cur, cw = [], [], 0; sp = d.textlength(" ", font=f)
    for w, k in words:
        ww = d.textlength(w, font=f) + (24 if k else 0)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w, k, ww)); cw += (sp if cw else 0) + ww
    if cur: lines.append(cur)
    lh = f.size + 26; y = y_mid - len(lines) * lh // 2
    ink = CREAM if dark else FG
    # timing: weight by characters
    wts = [len(w) + 2 for w, _ in words]; tot = sum(wts)
    span = max(0.01, t1 - t0); acc = 0; times = []
    for wt in wts: times.append(t0 + span * acc / tot); acc += wt
    i = 0
    for line in lines:
        x = 80; pk = False
        for w, k, ww in line:
            ts = times[i]; i += 1
            on = t >= ts
            if k and on:
                p = ease((t - ts) / 0.18)
                xl = x - sp - 2 if pk and t >= prev_ts else x
                d.rounded_rectangle([xl, y - 4, x + ww * p, y + f.size + 14], 10, fill=accent)
                col = mix(ink, accent_ink, p)
            else:
                col = ink if on else mix(bg, ink, 0.28)
            d.text((x + (12 if k else 0), y), w, font=f, fill=col)
            x += ww + sp; pk = k; prev_ts = ts
        y += lh

# ---------------- chrome ----------------
def chrome(d, sc_i, n, prog, organ, label, footer_l, dark, bg):
    ink = CREAM if dark else FG; faint = mix(bg, ink, 0.35)
    f = sans(30, "Bold"); tw = d.textlength(organ, font=f)
    d.rounded_rectangle([80, 150, 80 + tw + 40, 202], 26, fill=ink)
    d.text((100, 159), organ, font=f, fill=bg)
    d.text((W - 80, 159), label, font=sans(30, "SemiBold"), fill=faint, anchor="ra")
    # forest-plot progress: thin line, scene ticks, travelling diamond
    y = 250; d.line([80, y, W - 80, y], fill=faint, width=3)
    for k in range(n + 1):
        x = 80 + (W - 160) * k / n; d.line([x, y - 10, x, y + 10], fill=faint, width=3)
    xd = 80 + (W - 160) * prog
    d.line([80, y, xd, y], fill=ink, width=5)
    s = 15; d.polygon([(xd, y - s), (xd + s, y), (xd, y + s), (xd - s, y)], fill=TERRA)
    d.text((80, 1530), footer_l, font=sans(30, "Medium"), fill=faint)
    d.text((W - 80, 1530), "For education only", font=sans(30, "Medium"), fill=faint, anchor="ra")

# ---------------- render ----------------
def render(scenes, out, workdir, organ, label, footer_l, accent=TERRA, accent_ink=CREAM,
           dark_accent=None, only=None, stills=None):
    os.makedirs(workdir, exist_ok=True)
    wav, total = build_audio(scenes, workdir)
    n = len(scenes); files = []
    for si, sc in enumerate(scenes):
        prev_bg = scenes[si - 1].bg if si else sc.bg
        nfr = int(round(sc.dur * FPS))
        if stills is not None:
            frames_iter = [int(nfr * q) for q in stills]
        else:
            frames_iter = range(nfr)
        if stills is None:
            fn = f"{workdir}/scene{si:02d}.mp4"; tmp = fn[:-4] + ".part.mp4"
            p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                  "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                                  "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tmp],
                                 stdin=subprocess.PIPE)
        for fi in frames_iter:
            t = fi / FPS
            bg = mix(prev_bg, sc.bg, t / 0.25) if si else sc.bg
            im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
            acc = (dark_accent or (241, 228, 184)) if sc.dark else accent
            acc_ink = FG if sc.dark else accent_ink
            prog = (sc.start + t) / total
            chrome(d, si, n, prog, organ, label, footer_l, sc.dark, bg)
            if sc.draw: sc.draw(d, t, sc, bg)
            # caption = current (or last finished) beat
            cur = None
            for bi, (a, b) in enumerate(sc.beat_t):
                if t >= a - 0.05: cur = bi
            if cur is not None:
                a, b = sc.beat_t[cur]; cap = sc.beats[cur][1]
                caption(d, cap, a, b, t, bg, sc.dark, acc, acc_ink)
            if stills is not None:
                im.save(f"{workdir}/still_{si}_{fi}.png"); files.append(f"{workdir}/still_{si}_{fi}.png")
            else:
                p.stdin.write(im.tobytes())
        if stills is None:
            p.stdin.close(); p.wait(); os.replace(tmp, fn); files.append(fn)
    if stills is not None: return files
    with open(f"{workdir}/list.txt", "w") as fh:
        for fn in files: fh.write(f"file '{fn}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{workdir}/list.txt",
                    "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", reelkit.POST + "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    return total

def cover(scenes, idx, out, organ, label, footer_l, t=60.0):
    """Clean cover image (no caption) of scene idx — used as the Reel cover on Instagram and YouTube."""
    sc = scenes[idx]
    sc.beat_t = [(0, 0)] * 12; sc.dur = t
    im = Image.new("RGB", (W, H), sc.bg); d = ImageDraw.Draw(im)
    chrome(d, idx, len(scenes), (idx + 0.5) / len(scenes), organ, label, footer_l, sc.dark, sc.bg)
    if sc.draw: sc.draw(d, t, sc, sc.bg)
    im.save(out, quality=92)
    return out

"""Render a narrated Reel: list of (PIL image, narration) -> mp4 with Voice 3 and pronunciation fixes."""
import os, subprocess, numpy as np, soundfile as sf

FIX = {
    "ɐ ˈɛs dʒˈiː ˈiː": "ˈeɪ ˈɛs dʒˈiː ˈiː",          # A S G E (letter A, not schwa)
    "koʊlstˈɑːsiz": "kˌoʊlɪstˈeɪsɪs",                 # cholestasis
    "jˈuːz": "ˌiː jˌuː ˈɛs",                          # EUS
    "hˌɛpɐtˌɑːlɪθɪˈɑːsiz": "hˌɛpɐtoʊlɪθˈaɪəsɪs",      # hepatolithiasis
    "tʃˌɑːlɐŋɡɪˈɑːskəpi": "kˌoʊlændʒiˈɑːskəpi",       # cholangioscopy
    "ˈɜːɹɪsˌaɪpləz": "ˌɛɹɪsˈɪpɪləs",                  # erysipelas
    "ɡˈæŋɡɹɛn": "ɡˈæŋɡɹiːn",                          # gangrene
    "ˈɜːkp": "ˌiː ˌɑːɹ sˌiː pˈiː",                 # ERCP
    "tʃˌɑːlɐndʒˈaɪɾɪs": "kˌoʊlɐndʒˈaɪɾɪs",          # cholangitis
    "lˈɪpeɪs": "lˈaɪpeɪs",                          # lipase
    "ɛndˈoʊskəpi": "ɛndˈɑːskəpi",                    # endoscopy (en-DOS-copy)
    "dˈɛbɹaɪdmənt": "dɪbɹˈiːdmənt",                  # debridement
    "ˈɛndoʊskˌɑːpɪsts": "ɛndˈɑːskəpɪsts",            # endoscopist's
    "ˈɛndoʊskˌɑːpɪst": "ɛndˈɑːskəpɪst",              # endoscopist
    "kˈɑːɹbeɪpnəmz": "kˌɑːɹbəpˈɛnəmz",                # carbapenems
    "dˈɛbɹaɪd": "dɪbɹˈiːd",                          # debride
    "nˈæsoʊdʒdʒˌuːnəl": "nˌeɪzoʊdʒɪdʒˈuːnəl",        # nasojejunal
    "nˌæsoʊntˈɛɹɪk": "nˌeɪzoʊɛntˈɛɹɪk",              # nasoenteric
    "pˈɛɹəntɚɹəl": "pɚɹˈɛntɚɹəl",                    # parenteral
    "ɪmɹˈaɪ": "ˈɪmɹi",                               # Imrie
    "nˌæsəɡˈæstɹɪk": "nˌeɪzoʊɡˈæstɹɪk",              # nasogastric
    "hˈɛlɪkˌɑːbæktɚ": "hˌɛlɪkoʊbˈæktɚ",              # Helicobacter
    "kˈælɡʊɹli": "kælɡˈʊɹli",                        # Kalgoorlie
    "ɪndˈoʊmθɐsˌɪn": "ˌɪndoʊmˈɛθəsɪn",               # indomethacin
    "kˌoʊlsɪstˈɛktəmi": "kˌoʊləsɪstˈɛktəmi",         # cholecystectomy
    "kˌoʊlsɪstˈaɪɾɪs": "kˌoʊləsɪstˈaɪɾɪs",           # cholecystitis
    "kˌoʊlsɪstˈɑːstəmi": "kˌoʊləsɪstˈɑːstəmi",       # cholecystostomy
    "kˌoʊldəkˌɑːlɪθɪˈɑːsiz": "kəlˌɛdəkoʊlɪθˈaɪəsɪs", # choledocholithiasis
    "kˈælɑːt": "kælˈoʊ",                             # Calot
    "baɪlˈaɪɚɹi": "bˈɪliˌɛɹi",                       # biliary
    "kˈɑːtʃɚ": "kˈoʊkɚ",                             # Kocher
    "hˈiːdə": "hˈaɪdə",                              # HIDA
    "tʃˈaɪldpˈʌɡ": "tʃˈaɪld pjˈuː",                   # Child-Pugh
    "tʃˌɑːlɐŋɡɪˈɑːɡɹəfi": "kˌoʊlændʒiˈɑːɡɹəfi",       # cholangiography
    "baɪlˈɜːɹuːbˌɪn": "bˌɪlɪɹˈuːbɪn",                 # bilirubin
    "pˌæŋkɹiːˈeɪtˈaɪɾɪs": "pˌæŋkɹiətˈaɪɾɪs",          # pancreatitis
    "ɪndˈɑːsɪˌænaɪn": "ˌɪndoʊsˈaɪənˌiːn",             # indocyanine
    "flʊɹɹˈɛsəns": "flʊɹˈɛsəns",                      # fluorescence
    "hˌɛpɐtˌɪkoʊdʒdʒuːnˈɑːstəmi": "hɪpˌæɾɪkoʊdʒˌɛdʒuːnˈɑːstəmi",  # hepaticojejunostomy
    "hˌɛpɐtˌɪkədjˌuːoʊdnˈɑːstəmi": "hɪpˌæɾɪkoʊdˌuːoʊdɪnˈɑːstəmi", # hepaticoduodenostomy
    "bˌɪlɪoʊntˈɛɹɪk": "bˌɪlioʊɛntˈɛɹɪk",              # bilioenteric
    "tʃˈænɪlɹˌɑːdəpsˌɪn": "tʃˌænəlɹoʊdˈɑːpsɪn",       # channelrhodopsin
    "diːˈɪsɚɹˌɑːθ": "dˈaɪsɚɹˌɑːθ",                    # Deisseroth
    "hˈɛdʒɛmən": "hˈeɪɡəmˌæn",                        # Hegemann
    "nˈeɪdʒəl": "nˈɑːɡəl",                            # Nagel
    "hɛpˈɑːɾoʊpˌæŋkɹiːˈeɪɾoʊbˈɪliˌɛɹi": "hˌɛpɐtoʊ pˌæŋkɹiətoʊ bˈɪliˌɛɹi",  # Hepato-Pancreato-Biliary
    "hˌɛpɐtˌɑːpɐŋkɹiːˌeɪɾəbˈɪliəɹi": "hˌɛpɐtoʊpˌæŋkɹiətoʊbˈɪliˌɛɹi",       # hepatopancreatobiliary
    "hɛpˈɑːɾoʊ": "hˈɛpɐtoʊ",                          # Hepato
    "pˌæŋkɹiːˈeɪɾoʊ": "pˈæŋkɹiətoʊ",                  # Pancreato
}
_k = None
def _kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro("/home/claude/tts/kokoro.onnx", "/home/claude/tts/voices.bin")
    return _k

def phonemes(text):
    ph = _kokoro().tokenizer.phonemize(text, "en-us")
    for bad, good in FIX.items(): ph = ph.replace(bad, good)
    return ph

OUTRO = "Save, share and discuss this with your surgical colleagues, and follow us for more evidence-based medicine videos."

def render(slides, out_mp4, workdir, outro=True):
    """The OUTRO voice line is added to the end of the last slide's narration of every Reel."""
    os.makedirs(workdir, exist_ok=True)
    if outro and slides and OUTRO not in slides[-1][1]:
        slides = list(slides[:-1]) + [(slides[-1][0], (slides[-1][1] + " " + OUTRO).strip())]
    k = _kokoro()
    V = 0.5 * k.get_voice_style("am_michael") + 0.5 * k.get_voice_style("am_fenrir")
    vl, al, total = [], [], 0
    for i, (im, txt) in enumerate(slides, 1):
        a, sr = k.create(phonemes(txt), voice=V, speed=1.12, lang="en-us", is_phonemes=True)
        a = np.concatenate([np.zeros(int(0.15 * sr)), a, np.zeros(int(0.3 * sr))]).astype(np.float32)
        wav = f"{workdir}/v{i}.wav"; sf.write(wav, a, sr); al.append(f"file '{wav}'")
        dur = round(len(a) / sr, 3); total += dur
        png = f"{workdir}/s{i}.png"; im.save(png)
        tmp, mp4 = f"{workdir}/s{i}.tmp.mp4", f"{workdir}/s{i}.mp4"
        vf = f"format=yuv420p,loop=-1:1,trim=duration={dur},fade=t=in:st=0:d=0.3,fade=t=out:st={dur-0.3}:d=0.3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", png, "-vf", vf, "-c:v", "libx264",
                        "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp], check=True)
        os.rename(tmp, mp4); vl.append(f"file '{mp4}'")
    open(f"{workdir}/v.txt", "w").write("\n".join(vl)); open(f"{workdir}/a.txt", "w").write("\n".join(al))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{workdir}/v.txt", "-c", "copy", f"{workdir}/video.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{workdir}/a.txt",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", f"{workdir}/vo.wav"], check=True)
    tmp = out_mp4.replace(".mp4", ".tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{workdir}/video.mp4", "-i", f"{workdir}/vo.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.rename(tmp, out_mp4)
    return total

def contact(pngs, out, cols=6, w=270, h=480):
    from PIL import Image
    ims = [Image.open(p).resize((w, h)) for p in pngs]
    rows = (len(ims) + cols - 1) // cols
    m = Image.new("RGB", (w * cols, h * rows), "white")
    for i, im in enumerate(ims): m.paste(im, ((i % cols) * w, (i // cols) * h))
    m.save(out)


# ---------- Expressive narration (pitch, pace, pauses, breaths) ----------
import re as _re
_TAG = _re.compile(r"\[(slow|fast|up|down|pause|breath|calm)\]")
_CYCLE = [(1.10, 1.00), (1.14, 1.025), (1.07, 0.975), (1.16, 1.015), (1.09, 0.99)]   # (speed, pitch)

def _breath(sr, dur=0.34, gain=0.035):
    from scipy.signal import butter, lfilter
    n = int(dur * sr); x = np.random.default_rng(7).standard_normal(n)
    b, a = butter(2, [350 / (sr / 2), 2200 / (sr / 2)], btype="band"); x = lfilter(b, a, x)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    x = x / (np.abs(x).max() + 1e-9) * env * gain
    return np.concatenate([x, np.zeros(int(0.08 * sr))]).astype(np.float32)

def _pitch(a, sr, p, tmp):
    if abs(p - 1) < 0.004: return a
    sf.write(tmp + ".in.wav", a, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp + ".in.wav", "-af",
                    f"rubberband=pitch={p}:formant=preserved", "-ar", str(sr), tmp + ".out.wav"], check=True)
    b, _ = sf.read(tmp + ".out.wav", dtype="float32")
    return b

def speak(text, workdir, idx):
    """Narration with tags: [slow] [fast] [up] [down] [calm] apply to the next sentence; [pause] adds silence; [breath] adds a soft breath."""
    k = _kokoro()
    V = 0.5 * k.get_voice_style("am_michael") + 0.5 * k.get_voice_style("am_fenrir")
    sr = 24000; out = [np.zeros(int(0.12 * sr), np.float32)]
    parts = _re.split(r"(?<=[.!?])\s+", text.strip())
    for j, sent in enumerate(parts):
        tags = _TAG.findall(sent); s = _TAG.sub("", sent).strip()
        speed, pitch = _CYCLE[(idx + j) % len(_CYCLE)]
        if s.endswith("?"): pitch = max(pitch, 1.035)
        for t in tags:
            if t == "slow": speed = 1.0
            if t == "fast": speed = 1.2
            if t == "up": pitch = 1.05
            if t == "down": pitch = 0.96
            if t == "calm": speed, pitch = 1.04, 0.985
            if t == "breath": out.append(_breath(sr))
            if t == "pause": out.append(np.zeros(int(0.42 * sr), np.float32))
        if not s: continue
        a, sr = k.create(phonemes(s), voice=V, speed=speed, lang="en-us", is_phonemes=True)
        a = _pitch(a.astype(np.float32), sr, pitch, f"{workdir}/p{idx}_{j}")
        out.append(a)
        gap = 0.24 if s.endswith("?") else (0.14 if s.endswith(".") else 0.1)
        out.append(np.zeros(int(gap * sr), np.float32))
    out.append(np.zeros(int(0.2 * sr), np.float32))
    return np.concatenate(out), sr

def render_human(slides, out_mp4, workdir, outro=True):
    """Like render(), but sentence-by-sentence with varied pace and pitch, pauses and soft breaths."""
    os.makedirs(workdir, exist_ok=True)
    if outro and slides and OUTRO not in slides[-1][1]:
        slides = list(slides[:-1]) + [(slides[-1][0], (slides[-1][1] + " [breath] " + OUTRO).strip())]
    vl, al, total = [], [], 0
    for i, (im, txt) in enumerate(slides, 1):
        a, sr = speak(txt, workdir, i)
        wav = f"{workdir}/v{i}.wav"; sf.write(wav, a, sr); al.append(f"file '{wav}'")
        dur = round(len(a) / sr, 3); total += dur
        png = f"{workdir}/s{i}.png"; im.save(png)
        tmp, mp4 = f"{workdir}/s{i}.tmp.mp4", f"{workdir}/s{i}.mp4"
        vf = f"format=yuv420p,loop=-1:1,trim=duration={dur},fade=t=in:st=0:d=0.3,fade=t=out:st={dur-0.3}:d=0.3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", png, "-vf", vf, "-c:v", "libx264",
                        "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp], check=True)
        os.rename(tmp, mp4); vl.append(f"file '{mp4}'")
    open(f"{workdir}/v.txt", "w").write("\n".join(vl)); open(f"{workdir}/a.txt", "w").write("\n".join(al))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{workdir}/v.txt", "-c", "copy", f"{workdir}/video.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{workdir}/a.txt",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", f"{workdir}/vo.wav"], check=True)
    tmp = out_mp4.replace(".mp4", ".tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{workdir}/video.mp4", "-i", f"{workdir}/vo.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.rename(tmp, out_mp4)
    return total

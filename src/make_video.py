"""Genera un reel vertical 1080x1920 con voz argentina, clips de stock, subtítulos y cierre 'enlace en la bio'."""
import asyncio, os, random, subprocess, sys, json, glob, shutil, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts
W, H = 1080, 1920
VOICE = "es-AR-ElenaNeural"
LINUX = sys.platform.startswith("linux")
FONT_ASS = "DejaVu Sans" if LINUX else "Arial"
BOLD_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
def font(size):
    for p in BOLD_PATHS:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()
def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(path):
    import re
    r = subprocess.run(["ffmpeg","-i",path,"-f","null","-"], capture_output=True, text=True).stderr
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", r)[-1]
    return int(m[0])*3600 + int(m[1])*60 + float(m[2])

async def _tts(text, out):
    await edge_tts.Communicate(text, VOICE, rate="+8%").save(out)
def voice(lines, wd):
    outs = []
    for i, t in enumerate(lines):
        mp3, wav = f"{wd}/l{i}.mp3", f"{wd}/l{i}.wav"
        asyncio.run(_tts(t, mp3))
        run("ffmpeg","-y","-loglevel","error","-i",mp3,"-af",
            "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse",
            "-ar","24000","-ac","1",wav)
        outs.append(wav)
    return outs

# ---------- clips ----------
def pexels_clip(query, used, rnd, wd):
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        r = requests.get("https://api.pexels.com/videos/search", headers={"Authorization": key},
                         params={"query": query, "orientation": "portrait", "size": "medium", "per_page": 15}, timeout=30)
        r.raise_for_status()
        vids = [v for v in r.json().get("videos", []) if v["id"] not in used and v.get("duration", 0) >= 4]
        if vids:
            v = rnd.choice(vids[:8]); used.add(v["id"])
            files = [f for f in v["video_files"] if f.get("width") and f["width"] <= 1080 and f["height"] > f["width"]] or v["video_files"]
            f = max(files, key=lambda f: f.get("width", 0))
            out = f"{wd}/clip_{v['id']}.mp4"
            if not os.path.exists(out):
                with requests.get(f["link"], stream=True, timeout=120) as resp:
                    resp.raise_for_status()
                    with open(out, "wb") as fh: shutil.copyfileobj(resp.raw, fh)
            return out
    local = os.environ.get("LOCAL_CLIPS")           # solo para pruebas locales
    if local:
        c = sorted(glob.glob(f"{local}/*.mp4")); c = [x for x in c if x not in used] or c
        p = rnd.choice(c); used.add(p); return p
    return None
def fallback_bg(path, t):
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            k = y / H; c = (int(214-34*k), int(78-32*k), int(48-22*k))
            for dx in range(4): px[x+dx, y] = c
    p = path + ".png"; img.save(p); return p

VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,format=yuv420p"
def enc(out, src, t, still=False):
    pre = ["-loop","1","-framerate","30"] if still else ["-stream_loop","-1"]
    run("ffmpeg","-y","-loglevel","error",*pre,"-i",src,"-t",f"{t:.3f}","-vf",VF,"-an","-r","30","-c:v","libx264","-preset","veryfast","-crf","21",out)

# ---------- cierre "enlace en la bio" ----------
def end_card(path):
    bg = Image.new("RGB", (W, H)); px = bg.load()
    for y in range(H):
        for x in range(W):
            k = y/H*0.7 + x/W*0.3; px[x, y] = (int(214-34*k), int(78-32*k), int(48-22*k))
    d = ImageDraw.Draw(bg); cream = (255,244,226); gold = (255,214,64)
    def ct(t, y, f, fill=cream): d.text((W//2, y), t, font=f, fill=fill, anchor="mm")
    ct("¿QUÉ LE MANDO", 560, font(92)); ct("MAÑANA?", 680, font(120), gold)
    ct("Viandas de toda la semana,", 830, font(46)); ct("listas en una tarde.", 892, font(46))
    d.rounded_rectangle([110, 1040, W-110, 1190], radius=75, fill=cream)
    ct("ENLACE EN LA BIO", 1115, font(64), (150, 50, 30))
    # flecha hacia arriba
    d.polygon([(W//2, 1290), (W//2-90, 1410), (W//2-34, 1410), (W//2-34, 1500), (W//2+34, 1500), (W//2+34, 1410), (W//2+90, 1410)], fill=gold)
    ct("Munne Corporation", 1790, font(34), (255, 226, 200))
    bg.save(path)

def ts(x): h=int(x//3600); m=int(x%3600//60); s=x%60; return f"{h}:{m:02d}:{s:05.2f}"
def ass(lines, starts, durs, path):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,{FONT_ASS},72,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,2,2,70,70,520,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    ev = []
    for t, s, dd in zip(lines, starts, durs):
        words = t.split(); chunks = []; cur = []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or w.endswith((",", ".", ":", "?", "!")): chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        tot = sum(len(c) for c in chunks); tt = s + 0.03
        for c in chunks:
            x = dd * len(c) / tot; ev.append(f"Dialogue: 0,{ts(tt)},{ts(tt+x)},Main,,0,0,0,,{c}"); tt += x
    open(path, "w", encoding="utf-8").write(hdr + "\n".join(ev) + "\n")

def build(lines, queries, cta, out, seed=0, wd="work"):
    os.makedirs(wd, exist_ok=True); rnd = random.Random(seed)
    allv = voice(lines + [cta], wd)
    durs = [dur(a) + 0.22 for a in allv]; durs[-1] += 0.7
    end_card(f"{wd}/end.png")
    segs, used = [], set()
    for i, (t, _) in enumerate(zip(durs, allv)):
        o = f"{wd}/s{i}.mp4"
        if i == len(durs) - 1: enc(o, f"{wd}/end.png", t, still=True)
        else:
            src = pexels_clip(queries[i % len(queries)], used, rnd, wd)
            if src: enc(o, src, t)
            else: enc(o, fallback_bg(f"{wd}/bg{i}", t), t, still=True)
        segs.append(o)
    open(f"{wd}/list.txt", "w").write("".join(f"file 's{i}.mp4'\n" for i in range(len(segs))))
    run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{wd}/list.txt","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",f"{wd}/raw.mp4")
    # audio concatenado
    open(f"{wd}/alist.txt", "w").write("".join(f"file 'l{i}.wav'\n" for i in range(len(allv))))
    # relleno de pausas: cada wav se alarga a durs[i]
    padded = []
    for i, a in enumerate(allv):
        p = f"{wd}/p{i}.wav"; run("ffmpeg","-y","-loglevel","error","-i",a,"-af",f"apad=whole_dur={durs[i]:.3f}","-ar","24000","-ac","1",p); padded.append(p)
    open(f"{wd}/alist.txt", "w").write("".join(f"file 'p{i}.wav'\n" for i in range(len(padded))))
    run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{wd}/alist.txt","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-ar","44100",f"{wd}/voz.wav")
    starts, t0 = [], 0
    for d in durs: starts.append(t0); t0 += d
    ass(lines, starts[:-1], durs[:-1], f"{wd}/subs.ass")
    run("ffmpeg","-y","-loglevel","error","-i",f"{wd}/raw.mp4","-i",f"{wd}/voz.wav","-vf",f"subtitles={wd}/subs.ass","-map","0:v","-map","1:a",
        "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",out)
    return sum(durs)

"""On-screen cards: hook headline, keyword pops, listicle pill, end card, quote card."""
from __future__ import annotations

from pathlib import Path

from .common import FONTS, esc_drawtext, sh, ts


def wrap(text: str, font_file: Path, max_px: int, start: int, floor: int = 48, max_lines: int = 3):
    """Break text into lines that fit; shrink only if a single word is too wide. Returns (ASS text, px)."""
    from PIL import ImageFont
    px = start
    while True:
        f = ImageFont.truetype(str(font_file), px)
        lines, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if f.getlength(t) <= max_px:
                cur = t
            else:
                if cur: lines.append(cur)
                cur = w
        lines.append(cur)
        if (len(lines) <= max_lines and all(f.getlength(l) <= max_px for l in lines)) or px <= floor:
            return "\\N".join(lines), px
        px -= 4


def hook_event(text: str, brand: dict, W: int, H: int, dur: float = 2.6, serif: bool = False, y: float | None = None) -> str:
    fonts = brand["fonts"]
    ff = FONTS / (fonts["display_file"] if serif else fonts["caption_file"])
    start = int(H * (0.052 if serif else 0.044))
    lines, px = wrap(text if serif else text.upper(), ff, W - 180, start)
    yy = int(H * (y if y is not None else 0.30))
    style = "HookSerif" if serif else "Hook"
    return (f"Dialogue: 6,{ts(0)},{ts(dur)},{style},,0,0,0,,{{\\pos({W // 2},{yy})\\fs{px}\\fad(0,200)"
            f"\\fscx106\\fscy106\\t(0,180,\\fscx100\\fscy100)}}{lines}")


def pop_event(text: str, t: float, dur: float, W: int, H: int) -> str:
    """A 1 to 4 word keyword that lands on the spoken word, top zone, display face."""
    return (f"Dialogue: 5,{ts(t)},{ts(t + dur)},Pop,,0,0,0,,{{\\fad(60,160)\\fscx88\\fscy88\\t(0,120,\\fscx100\\fscy100)}}{text}")


def pill_events(items: list[tuple[float, float, str]]) -> list[str]:
    """Listicle progress pill: [(start, end, '1. MARKET'), ...] sits just above the caption band."""
    return [f"Dialogue: 4,{ts(a)},{ts(b)},Pill,,0,0,0,,{{\\fad(80,80)}}  {label.upper()}  " for a, b, label in items]


def end_card(brand: dict, W: int, H: int, dur: float, out: Path, cta: str | None = None, preset="medium", crf="18"):
    from PIL import ImageFont
    f1 = FONTS / brand["fonts"]["caption_file"]; f2 = FONTS / brand["fonts"]["caption_2_file"]
    c = brand["colors"]; cta = cta or brand["cta"]["line"]
    big = int(H * 0.040); small = int(H * 0.023)
    while big > 24 and ImageFont.truetype(str(f1), big).getlength(cta.upper()) > W * 0.86:
        big -= 2
    lines = [f"drawtext=fontfile={f1}:text='{esc_drawtext(cta.upper())}':fontsize={big}:fontcolor={c['accent']}:x=(w-tw)/2:y=h*0.44"]
    if brand["cta"].get("sub"):
        lines.append(f"drawtext=fontfile={f2}:text='{esc_drawtext(brand['cta']['sub'])}':fontsize={small}:fontcolor={c['text']}:x=(w-tw)/2:y=h*0.52")
    if brand.get("handle"):
        lines.append(f"drawtext=fontfile={f2}:text='{esc_drawtext(brand['handle'])}':fontsize={int(small * 0.9)}:fontcolor={c['text']}@0.7:x=(w-tw)/2:y=h*0.57")
    sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={c['bg']}:s={W}x{H}:d={dur}:r=30",
        "-vf", ",".join(lines) + ",vignette=a=0.4,format=yuv420p", "-c:v", "libx264", "-preset", preset, "-crf", crf, str(out)])
    return out


def quote_card(text: str, brand: dict, W: int, H: int, out: Path, attribution: str = ""):
    """Full-frame tweetable line on the brand background, serif, for a 2 to 3 s cutaway."""
    from PIL import Image, ImageDraw, ImageFont
    c = brand["colors"]
    img = Image.new("RGB", (W, H), c["bg"])
    d = ImageDraw.Draw(img)
    ff = FONTS / brand["fonts"]["display_file"]
    lines, px = wrap(text, ff, int(W * 0.80), int(H * 0.06), floor=int(H * 0.03), max_lines=5)
    f = ImageFont.truetype(str(ff), px)
    ls = lines.split("\\N")
    lh = int(px * 1.2); total = lh * len(ls)
    y = (H - total) // 2
    for ln in ls:
        w = f.getlength(ln)
        d.text(((W - w) / 2, y), ln, font=f, fill=c["text"]); y += lh
    d.rectangle([W * 0.46, y + lh * 0.4, W * 0.54, y + lh * 0.4 + max(3, H // 400)], fill=c["accent"])
    if attribution:
        f2 = ImageFont.truetype(str(FONTS / brand["fonts"]["caption_2_file"]), int(H * 0.02))
        w = f2.getlength(attribution)
        d.text(((W - w) / 2, y + lh * 0.9), attribution, font=f2, fill=c["muted"])
    img.save(out)
    return out

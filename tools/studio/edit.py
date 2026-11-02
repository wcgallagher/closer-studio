"""`closer.py edit VIDEO "what you want"`: drop a video in, say what you want, get a first cut and a plan to refine.

The sentence becomes decisions a person would make before touching the timeline, each one written into plan.json with
the reason, so the agent (or the owner) can change any of them in plain words and run it again:

  format    what the video is for (VSL, reel, YouTube, ad, tutorial, story) and its length
  dialect   how it should feel: documentary-premium (restraint, music carries the feeling) or high-energy (more
            punch-ins, more sound, faster captions)
  pacing    the breath between sentences and the beats before claims (a fast talker gets room, not more trimming)
  sound     voice-over-music targets per section, the SFX grammar, and the best-fitting track from a music folder
  look      the finish profile measured from the footage
  graphics  nothing invented: numbers and words on screen come from the speaker or the owner

Then it analyses the footage (or reuses the analysis), writes layers.json, and renders a preview unless told not to.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

INTENT_RULES = {
    "format": [   # first match wins; words a person would use
        (r"\b(vsl|sales video|homepage|landing page|hero video)\b", "vsl_hero"),
        (r"\b(ad|ads|paid|meta ad|facebook ad)\b", "paid_ad_reel"),
        (r"\b(reel|reels|tiktok|short|shorts|instagram)\b", "organic_reel"),
        (r"\b(youtube|long[- ]form|video essay|podcast)\b", "yt_authority"),
        (r"\b(lesson|tutorial|skool|course|training)\b", "skool_lesson"),
    ],
    "dialect": [
        (r"\b(nelk|hormozi|hype|energy|fast|punchy|loud|viral)\b", "nelk"),
        (r"\b(gadzhi|cinematic|premium|documentary|luxury|clean|elegant|minimal|apple)\b", "gadzhi"),
    ],
    "length": r"(\d{2,3})\s*(?:s\b|sec|seconds)|(\d)\s*(?:min|minute)",
}

DEFAULTS = {   # per format: platform, captions, sections, breath, finish profile
    "vsl_hero": {"platform": "web_vsl", "sections": [{"name": "hook", "vm": 11}, {"name": "body", "vm": 14}, {"name": "cta", "vm": 12}],
                 "breath": {"sentence": 0.45}, "finish": "vsl", "dialect": "gadzhi"},
    "paid_ad_reel": {"platform": "ig_reels", "sections": [{"name": "all", "vm": 12}], "breath": {"sentence": 0.3}, "finish": "reel", "dialect": "nelk"},
    "organic_reel": {"platform": "ig_reels", "sections": [{"name": "all", "vm": 16}], "breath": {"sentence": 0.3}, "finish": "reel", "dialect": "nelk"},
    "yt_authority": {"platform": "youtube", "sections": [{"name": "all", "vm": 20}], "breath": {"sentence": 0.4}, "finish": "brand", "dialect": "gadzhi"},
    "skool_lesson": {"platform": "youtube", "sections": [{"name": "all", "vm": 20}], "breath": {"sentence": 0.4}, "finish": "vsl", "dialect": "gadzhi"},
}


def read_intent(text: str) -> dict:
    t = text.lower()
    out, why = {}, {}
    for pat, fid in INTENT_RULES["format"]:
        if re.search(pat, t):
            out["format"], why["format"] = fid, f"'{re.search(pat, t).group(0)}' in the request"
            break
    out.setdefault("format", "yt_authority"); why.setdefault("format", "no format named: long-form master by default")
    for pat, d in INTENT_RULES["dialect"]:
        if re.search(pat, t):
            out["dialect"], why["dialect"] = d, f"'{re.search(pat, t).group(0)}' in the request"
            break
    m = re.search(INTENT_RULES["length"], t)
    if m:
        out["length_s"] = int(m.group(1)) if m.group(1) else int(m.group(2)) * 60
        why["length_s"] = f"'{m.group(0)}' in the request"
    return {"decisions": out, "why": why}


def pick_music(folder: Path | None, need_s: float, log=print) -> tuple[str | None, list]:
    """Score every track in a folder by its measured traits and return the best plus the ranked list (the owner listens
    to the top three; nothing here listens)."""
    if not folder or not Path(folder).exists():
        return None, []
    from . import sound
    ranked = []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aif", ".aiff"):
            continue
        try:
            p = sound.track_profile(f)
            s, why = sound.score_track(p, need_s)
            ranked.append({"file": str(f), "score": s, "why": why, "tempo": p["tempo"], "mode": p["mode"], "dur": p["dur"]})
        except Exception as e:  # a broken file is skipped, not fatal
            log(f"music: skipped {f.name} ({type(e).__name__})")
    ranked.sort(key=lambda r: -r["score"])
    return (ranked[0]["file"] if ranked else None), ranked[:5]


def plan(video: Path, intent: str, out: Path, brand: str, music_dir: Path | None = None, sfx_dir: Path | None = None,
         render: bool = True, log=print) -> Path:
    from . import analyze as an_mod, brands, formats as fm, longform as long_mod, platforms
    out.mkdir(parents=True, exist_ok=True)
    it = read_intent(intent)
    d = it["decisions"]
    fid = d["format"]
    base = DEFAULTS.get(fid, DEFAULTS["yt_authority"])
    dialect = d.get("dialect", base["dialect"])
    an = an_mod.analyze(video, out)
    speech = an["stats"]["speech_s"] if an.get("stats") else an["dur"]
    wpm = round(len(an["words"]) / max(speech / 60, 0.1))
    breath = dict(base["breath"])
    why_breath = "format default"
    if wpm > 200:   # a fast talker: more room between sentences, never trimmed tighter
        breath["sentence"] = max(breath["sentence"], 0.45)
        why_breath = f"{wpm} words per minute is fast (persuasion peaks near 181 in the research): sentences keep 450 ms"
    music, ranked = pick_music(music_dir, an["dur"] + 4, log)
    sections = [dict(s) for s in base["sections"]]
    if fid == "vsl_hero" and len(an["sentences"]) >= 4:   # hook = the first sentence, CTA = the last fifth
        sections[1]["from"] = f"{an['words'][an['sentences'][1]['i0']]['w']}@{an['sentences'][1]['s']:.2f}"
        k = max(2, int(len(an["sentences"]) * 0.8))
        sections[2]["from"] = f"{an['words'][an['sentences'][k]['i0']]['w']}@{an['sentences'][k]['s']:.2f}"
    layers = {"finish": {"profile": base["finish"]}, "breath": breath,
              "sound": {"dialect": dialect, "sections": sections, **({"sfx_dir": str(sfx_dir)} if sfx_dir else {})}}
    if music:
        layers["music"] = {"file": music}
    (out / "layers.json").write_text(json.dumps(layers, indent=1))
    p = {"video": str(video), "intent": intent, "format": fid, "platform": base["platform"], "brand": brand, "dialect": dialect,
         "words_per_minute": wpm, "why": dict(it["why"], breath=why_breath, music="best measured fit; owner listens to the top 3" if music else "no music folder given"),
         "music_ranked": ranked, "layers": str(out / "layers.json"),
         "next": ["read the transcript and add graphics only where the words name a thing or a sourced number (skills/video/placement)",
                  "listen to the top 3 tracks and pick (skills/video/sound-director)",
                  "render, read report.md, fix every FIX, then compare against the last version (skills/video/compare-cuts)"]}
    (out / "plan.json").write_text(json.dumps(p, indent=1))
    log(f"plan: {fid} for {base['platform']}, {dialect} dialect, {wpm} wpm, breath {breath}, music {Path(music).name if music else 'none'}")
    vertical = platforms.get(base["platform"])["h"] > platforms.get(base["platform"])["w"]
    if render and vertical:     # vertical formats go through the reel cutter, which does not read layers yet
        log(f"next: closer.py reel {video} --out {out / 'cut'} --format {fid} --brand {brand}" + (f" --music '{music}'" if music else ""))
        render = False
    if render:
        fmt = fm.get(fid)
        long_mod.longform(video, out / "cut", an, brands.load(brand), platforms.get(base["platform"], fmt.get("safe", "organic")), fmt,
                          layers=out / "layers.json", preview=True, log=log)
        from . import review
        review.run(out / "cut")
    return out / "plan.json"

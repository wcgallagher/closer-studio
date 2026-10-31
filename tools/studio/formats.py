"""Formats: what a video is for decides how it is cut. `formats.json` at the kit root (written from FORMATS.md) overrides
the built-in defaults below; both carry the same keys. `python3 tools/closer.py formats` prints the table."""
from __future__ import annotations

import json

from .common import KIT

FORMATS_FILE = KIT / "formats.json"

# conservative built-ins (house choices); FORMATS.md and formats.json carry the sourced numbers
DEFAULTS = [
    {"id": "organic_reel", "name": "Organic reel", "goal": "reach and saves", "funnel_stage": "cold", "kind": "short",
     "platforms": ["ig_reels", "tiktok", "yt_shorts"], "length_s": {"min": 15, "ideal": 30, "max": 60}, "captions": "impact", "safe": "organic",
     "cta": "end_card", "hook_deadline_s": 2.5, "change_every_s": 8, "payoff_window_pct": [55, 85], "music": "none", "fillers": "keep",
     "cover": "hook text over the best face frame", "checks": ["hook by 2.5 s", "one idea", "ends on the payoff"], "sources": []},
    {"id": "ad_reel", "name": "Paid ad (vertical)", "goal": "clicks to the quiz or sign-up", "funnel_stage": "paid", "kind": "short",
     "platforms": ["ig_reels", "fb_reels", "tiktok", "yt_shorts"], "length_s": {"min": 15, "ideal": 30, "max": 60}, "captions": "impact", "safe": "ads",
     "cta": "spoken_plus_card", "hook_deadline_s": 2.0, "change_every_s": 6, "payoff_window_pct": [40, 80], "music": "faint", "fillers": "cut",
     "cover": "first frame carries the hook text", "checks": ["hook by 2 s", "CTA spoken and on the card", "ad safe zones", "no income or guarantee claims"], "sources": []},
    {"id": "show_confirmation", "name": "Confirmation-page video", "goal": "the booked person shows up", "funnel_stage": "booked", "kind": "long",
     "platforms": ["web_vsl"], "length_s": {"min": 90, "ideal": 180, "max": 300}, "captions": "clean", "safe": "organic",
     "cta": "spoken_plus_card", "hook_deadline_s": 5, "change_every_s": 30, "payoff_window_pct": [50, 90], "music": "faint", "fillers": "cut",
     "cover": "the host's face, the words 'watch before your call'", "checks": ["names the call date and what to prepare", "who it is not for"], "sources": []},
    {"id": "show_reminder", "name": "Reminder clip", "goal": "a nudge before the call or the training", "funnel_stage": "booked", "kind": "short",
     "platforms": ["ig_story", "square"], "length_s": {"min": 10, "ideal": 20, "max": 30}, "captions": "clean", "safe": "organic",
     "cta": "in_band", "hook_deadline_s": 1.5, "change_every_s": 6, "payoff_window_pct": [40, 90], "music": "none", "fillers": "cut",
     "cover": "the time of the call in the band", "checks": ["says the time", "one ask"], "sources": []},
    {"id": "vsl_short", "name": "Short VSL", "goal": "book the call or create the account", "funnel_stage": "sales page", "kind": "long",
     "platforms": ["web_vsl"], "length_s": {"min": 180, "ideal": 360, "max": 600}, "captions": "clean", "safe": "organic",
     "cta": "spoken_plus_card", "hook_deadline_s": 10, "change_every_s": 30, "payoff_window_pct": [60, 90], "music": "bed", "fillers": "cut",
     "cover": "poster frame at the hook with the headline", "checks": ["mechanism before offer", "proof cut in", "CTA repeated at the end"], "sources": []},
    {"id": "vsl_long", "name": "Long VSL", "goal": "sell a high-ticket offer without a call", "funnel_stage": "sales page", "kind": "long",
     "platforms": ["web_vsl"], "length_s": {"min": 900, "ideal": 1500, "max": 2700}, "captions": "none", "safe": "organic",
     "cta": "spoken_plus_card", "hook_deadline_s": 10, "change_every_s": 40, "payoff_window_pct": [60, 90], "music": "bed", "fillers": "cut",
     "cover": "poster frame at the hook with the headline", "checks": ["every claim sourced", "offer stack on screen", "CTA at least twice"], "sources": []},
    {"id": "youtube_long", "name": "YouTube authority video", "goal": "trust and search", "funnel_stage": "warm", "kind": "long",
     "platforms": ["youtube"], "length_s": {"min": 420, "ideal": 720, "max": 1200}, "captions": "pops", "safe": "organic",
     "cta": "none", "hook_deadline_s": 10, "change_every_s": 40, "payoff_window_pct": [72, 95], "music": "faint", "fillers": "keep",
     "cover": "thumbnail: face, 2 to 4 words, high contrast", "checks": ["thesis by 10 s", "layout changes every 40 s", "no outro"], "sources": []},
    {"id": "skool_welcome", "name": "Skool welcome video", "goal": "a new member knows what to do first", "funnel_stage": "community", "kind": "long",
     "platforms": ["youtube"], "length_s": {"min": 90, "ideal": 180, "max": 300}, "captions": "pops", "safe": "organic",
     "cta": "spoken_plus_card", "hook_deadline_s": 5, "change_every_s": 30, "payoff_window_pct": [50, 90], "music": "faint", "fillers": "cut",
     "cover": "the host's face and 'start here'", "checks": ["one first action", "where things are"], "sources": []},
    {"id": "skool_lesson", "name": "Skool lesson module", "goal": "a member finishes and applies one skill", "funnel_stage": "community", "kind": "long",
     "platforms": ["youtube"], "length_s": {"min": 240, "ideal": 480, "max": 900}, "captions": "pops", "safe": "organic",
     "cta": "none", "hook_deadline_s": 10, "change_every_s": 40, "payoff_window_pct": [60, 95], "music": "none", "fillers": "cut",
     "cover": "module number and title on the brand plate", "checks": ["one skill", "chapters", "an action at the end"], "sources": []},
    {"id": "replay", "name": "Live training replay", "goal": "the training keeps working after the call", "funnel_stage": "warm", "kind": "long",
     "platforms": ["youtube"], "length_s": {"min": 600, "ideal": 1800, "max": 3600}, "captions": "none", "safe": "organic",
     "cta": "end_card", "hook_deadline_s": 15, "change_every_s": 60, "payoff_window_pct": [50, 95], "music": "none", "fillers": "keep",
     "cover": "the topic and the date", "checks": ["dead air cut", "chapters", "the ask at the end"], "sources": []},
    {"id": "testimonial", "name": "Testimonial or case-study clip", "goal": "proof", "funnel_stage": "warm", "kind": "short",
     "platforms": ["ig_reels", "square", "youtube"], "length_s": {"min": 20, "ideal": 45, "max": 90}, "captions": "clean", "safe": "organic",
     "cta": "end_card", "hook_deadline_s": 3, "change_every_s": 8, "payoff_window_pct": [50, 90], "music": "faint", "fillers": "keep",
     "cover": "the person's face and the result in their words", "checks": ["results disclaimer on screen", "the person's own words only"], "sources": []},
]


def load_all() -> list[dict]:
    if FORMATS_FILE.exists():
        try:
            data = json.loads(FORMATS_FILE.read_text())
            if isinstance(data, list) and data:
                ids = {d["id"] for d in data}
                return data + [d for d in DEFAULTS if d["id"] not in ids]
        except ValueError:
            pass
    return DEFAULTS


def get(fid: str) -> dict:
    for f in load_all():
        if f["id"] == fid:
            return f
    raise SystemExit(f"unknown format '{fid}'. Formats: {', '.join(f['id'] for f in load_all())}")


def table() -> str:
    rows = ["id                 kind   length (ideal)   captions  safe     cta               platforms"]
    for f in load_all():
        L = f["length_s"]
        rows.append(f"{f['id']:<18} {f['kind']:<6} {L['min']}-{L['max']} s ({L['ideal']})".ljust(43) +
                    f"{f['captions']:<9} {f['safe']:<8} {f['cta']:<17} {','.join(f['platforms'])}")
    return "\n".join(rows)


def check_length(f: dict, dur: float) -> str | None:
    L = f["length_s"]
    if dur < L["min"]:
        return f"{dur:.0f} s is under the {f['name']} minimum of {L['min']} s"
    if dur > L["max"]:
        return f"{dur:.0f} s is over the {f['name']} maximum of {L['max']} s"
    return None

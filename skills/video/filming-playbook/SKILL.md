---
name: filming-playbook
description: How to film for the edit. A one-page shoot sheet a founder can follow on a phone or a mirrorless camera (gear, mic and wind, room, light, exposure locks, one framing that serves 16:9 and 9:16, delivery (pauses between lines, repeated key lines, gestures held inside the frame for labels, slates), a B-roll list for a sales or coaching business), then the checks the kit runs on the raw takes before any edit (analyze, hands, the finish and sound measurements) with what to reshoot. Use before a shoot, when someone asks "how should I film this", "what mic should I buy", "what camera settings", "can you fix the wind", "why is my face so dark", "my hands keep leaving the frame", or as soon as new takes land in inbox.
---

# Filming playbook

The edit can only use what the camera caught. The first shoot this kit cut was three 4K, 30 fps takes on a windy balcony with the sky behind the speaker. The kit measured every problem afterwards and could fix none of them properly: wind in the pauses, a sky at 0.80 luma, a face at 0.33 to 0.36, 4 to 5 % of the frame clipped white, hands partly out of the frame on the gesture lines, and sentence ends too tight to cut. Each line of the shoot sheet below exists to stop one of those. Section 7 is how to check a shoot before anyone starts editing.

Every engine number here comes from the code (`tools/studio/sound.py`, `tools/studio/finish.py`, `tools/studio/hands.py`, `tools/studio/cut.py`, `tools/studio/placement.py`, `tools/studio/layers.py`). Craft numbers come from the research and are named as such. When this page and the code disagree, the code wins and this page gets fixed.

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
"$PY" "$KIT/tools/closer.py" hands --help
```

On a Mac or Linux, run these in Terminal. On Windows, run them in Git Bash or WSL: the second path on the PY line is the venv that `install.ps1` makes. The installers write `kit_path`; without it, run from the kit folder. The help screen should print `usage: closer hands [-h] [--start START] --end END [--fps FPS] --out OUT video`.

An agent's shell does not keep variables from one command to the next, so start every block below with the KIT and PY lines. Raw takes go in `inbox/` and are never changed; the checks write to `output/<job>/check/`. The blocks below use `shoot1` as the job name: change it in every block for a new shoot.

## 1. The shoot sheet

Send this to whoever is filming. It fits on one phone screen per heading.

```text
SHOOT SHEET

GEAR
[ ] Wireless lav mic with its own backup recording (DJI Mic 2 or 3, RODE Wireless PRO). Backup ON.
[ ] Fur windscreen on the mic for any shot outdoors.
[ ] Phone or camera on a tripod, lens at eye level.
[ ] A camera app that locks settings: Blackmagic Camera (free) or Final Cut Camera.
[ ] Light: a window in front of you, or one LED panel.

PLACE
[ ] Indoors, in the most furnished room you have (couch, rug, curtains, shelves).
[ ] Never a balcony corner or the windy edge of a building. Outside, stand behind a wall.
[ ] No window or sky behind you. The window goes in front of you, off to one side.
[ ] On the side of the frame you are not standing on: a plain, darker wall. The words go there.

CAMERA (set it once and lock it for every take)
[ ] Hold it sideways (16:9). 4K. 30 fps. HDR video off. Audio 48 kHz.
[ ] Shutter 1/60. For lines with hand gestures, 1/100 to 1/120.
[ ] White balance locked: Daylight 5600 K by a window, Tungsten 3200 K under lamps.
[ ] Focus and exposure locked on your face, then a touch darker. No zebras on your forehead.

FRAME
[ ] From mid-chest up. Eyes about a third of the way down the screen.
[ ] Stand in the centre or on the right third (the opening text of a VSL sits on the left).
[ ] Gestures in front of your chest, close to your body, never out to the side or down at the waist.

BEFORE TAKE 1
[ ] Record 10 seconds and play it back on headphones. Rumble, rustle, hum or echo: fix it first.
[ ] Start every take with a spoken slate ("take 3, offer section") and one clap in frame.

DELIVERY
[ ] Talk to the lens, not to the screen.
[ ] One second of quiet, hands at rest, between lines.
[ ] Stumbled? Pause, then start the whole sentence again.
[ ] Say each key line (hook, big claim, proof, the ask) two or three times, with different energy.
[ ] Naming a number or a list item? Lift the hand just before the word and hold it still for about a second.

B-ROLL
[ ] 8 to 10 seconds per shot, sideways, 30 fps, camera still or moving slowly. No client names on any screen.

AFTER
[ ] Put the takes in inbox and say "check my takes".
```

## 2. Sound: the mic, the wind, the room

**The mic.** A phone mic a metre or two away in a bare room records mostly room: past the critical distance the echo is as loud as the voice (research, critical distance). Clip a wireless lav on the sternum, 15 to 20 cm (6 to 8 in) below the chin. Run the cable inside the shirt and tape it at the collar and at the belt, and keep anything that rubs (a lanyard or necklace, an open jacket flap) away from it.

- Turn on the transmitter's own backup recording before every take. On DJI Mic 2 the 32-bit float internal recording has to be switched on in the DJI Mimo app; RODE Wireless PRO records on board. When the camera track clips or drops out, the backup is the take. The kit has no step that syncs it in for you yet (section 8).
- DJI Mic 2 noise cancelling does not run while the receiver is paired to the phone by Bluetooth. Plug the receiver in, or record raw and let the kit clean it.
- On DJI Mic 3, record dual-file and hand over the original file, not the enhanced one, so the kit's cleaner is the only processing on the voice.
- RODE Wireless Micro has no backup recording on its page, so a dropout cannot be recovered. Fine for a throwaway reel, never for a VSL.
- At a desk (a Skool lesson, a podcast), a dynamic desk mic such as the Shure MV7+ about a hand-width from the mouth rejects room echo better than a lav. The hand-width is a house value; the research found no published distance.

**Wind.** Wind on a mic capsule cannot be repaired after the shoot. Here is what the kit's voice cleaner can do about it, from `SOUND_RULES` in `tools/studio/sound.py`:

- It measures how much of the energy in your pauses sits under 150 Hz (`low_rumble_share_in_pauses`). Above 0.45 it calls the take windy and raises its high-pass from 80 Hz to 110 Hz.
- It finds frames where the energy under 150 Hz runs more than 8 dB over its median level while you talk, and cuts each one by the excess, 12 dB at most, on a low shelf that fades out at 180 Hz. `wind_burst_frames` counts the frames that get more than 1 dB of that cut.

A gust is louder than a 12 dB fix, and the noise reduction also stops at 12 dB on purpose, because deeper reduction sounds watery. On the balcony takes the pauses measured a rumble share of 0.24 and 0.46 and the bursts added up to 3.4 and 5.1 seconds per take, and the earlier attempts to clean that rumble left the voice sounding over-processed. So the fixes are all at the shoot:

- Fur on every capsule outdoors, no exceptions; the thin stock foam on most lavs is rarely enough. In gusts, put the lav under one thin layer of clothing plus the fur.
- Never a balcony corner or the windward edge of a tall building. On high-rise balconies, winds above 0.7 of the rooftop speed showed up almost only at the corners (Journal of Wind Engineering, 1986). Stand behind a wall or a partition (one simulation found partitions cut balcony wind by 68%), or go indoors.
- iPhone 16 Wind Noise Reduction (Settings, Camera, Record Sound) is a fallback for a failed lav, not a plan.
- Record 10 seconds of real speech and listen on headphones before the first take. Any rumble means move or fix the rig before rolling.

**The room.** Fix echo in this order. First get the mic close (the lav, or the desk mic). Then pick the most furnished room, stay out of kitchens, glass walls, bare floors and empty rooms, and hang blankets on bare hard walls facing the speaker. The research verified only the first step; the second is house practice.

## 3. Light and exposure

**Never the sky behind you.** The finish pass (`tools/studio/finish.py`, which `longform` runs when the layers file has a `finish` entry) measures the cut before it grades it, and every move it makes is capped:

| It measures | It does | Its limit |
|---|---|---|
| `sky_luma` (bright blue, plus bright colourless cloud or wall at half weight) | pulls the sky down once it is above 0.66 | 0.45 EV at most |
| `face_luma` inside the tracked face | lifts the face toward 0.52 | 0.30 EV at most |
| `sky_share`, how much of the frame the sky covers | switches the sky moves on above 0.03 | |
| `clipped_share`, pixels with luma above 0.985 | nothing to bring them back, since clipped pixels hold no detail; above 0.002 it only switches on the halation glow of a brand film, which the `vsl` and `reel` finishes leave off | |

The balcony takes measured a sky at 0.80, covering 36 to 44 % of the frame, with 3.8 to 4.9 % of the frame clipped and the face at 0.33 to 0.36. The finish pulled the sky down by about 0.3 EV and gave the face its full 0.30 EV, which takes a face at 0.33 only to about 0.41. Any face under about 0.40 gets the whole lift and still ends dark. A bright white wall behind you counts toward the sky too.

So turn around. Use a window as the key light, 30 to 45 degrees to one side of the lens and a little above eye level, with the speaker facing it. Fill the shadow side at up to half the key (a white wall or reflector, or an LED turned low); too much fill looks flat. With no window, one LED panel at 45 degrees does the job (an Elgato Key Light runs 2900 to 7000 K), set to match the room. For depth, one coloured lamp in the background kept darker than the face separates you from the wall (an editing guide on the premium look, low confidence).

**Lock everything.** Shoot in Blackmagic Camera (free on iOS and Android; on Android only Samsung Galaxy and Pixel phones) or Final Cut Camera on iPhone, not the stock app, and lock shutter, ISO, white balance and focus so every take matches.

- **30 fps.** The kit renders at 30 fps (`FPS` in `tools/studio/common.py`, and every platform in `tools/studio/platforms.py`), and `assemble` re-times every beat to 30. A 24 or 25 fps take gets frames repeated to fill 30. Never mix frame rates across takes.
- **Shutter** about 1/(2 x fps): 1/60 at 30 fps. For lines where a label rides your hand, 1/100 to 1/120 gives sharper hands for the tracker (the research's inference, not a measurement). If LED or fluorescent lights flicker on screen in a 60 Hz country, stay on multiples of 1/60 (house, unverified).
- **White balance** to the key light: Daylight 5600 K for a window, Tungsten 3200 K for lamps. Never daylight and warm bulbs on the same face.
- **Exposure**: in Blackmagic Camera, false color on the face should show pink for lighter skin or green for darker skin, never red; no zebras on the forehead. In the stock iPhone app, tap and hold the face until AE/AF Lock shows, then swipe down a touch so skin does not clip, and turn on Lock White Balance once under Settings, Camera, Record Video (iOS 17 and later).
- **HDR video off.** Nothing in the kit tone-maps (no `tonemap` or `zscale` filter anywhere in `tools/studio`) and the finish reads every clip as BT.709, so an HLG or Dolby Vision clip comes in washed out. The research marks the exact phone setting unverified: test one clip.
- **Mirrorless**: the same numbers, 4K, the lav into the camera plus the transmitter's backup, and timecode where the mic has it (RODE Wireless PRO, DJI Mic 3). Use a standard picture profile; the kit has no log-to-Rec.709 conversion.

## 4. One framing for 16:9 and 9:16

Shoot sideways in 4K and let the kit cut the vertical. The arithmetic:

- The widest 9:16 crop of a 16:9 frame is 31.6% of its width: 1215 of 3840 px, or 607.5 of 1920 px. From 4K that crop is wider than the 1080 px of a reel, so it stays sharp; from a 1080p take it gets stretched to almost twice its width. The cut also punches in: 1.10x and 1.20x in `tools/studio/cut.py`, which `reel` uses; 1.15x by default in `longform`, and 1.12x and 1.22x in its `vsl_hero` format (`formats.json`). 4K covers a 16:9 punch-in with room to spare. On a 9:16 reel the 1.20x punch-in leaves 1012 of those 1215 px, a slight stretch to 1080, where a 1080p take would leave 506.
- The kit's vertical camera follows your face (`tools/studio/track.py`), so that column is centred on you, not on the frame. Your gestures have about 15.8% of the frame width on each side of your face, and less whenever the kit zooms in: a punch-in, or a face shorter than 27 % of the frame height, which the reel camera zooms toward (up to about 1.29x from 4K, `camera` in `tools/studio/track.py`). On the balcony gesture beat, not one of 20 hand detections fell inside that column, and 4 touched the frame edge. When reels are the main output, film vertical instead.

The rest of the frame:

- **Eye line** about a third down from the top (research, headroom). The house band is 30 to 36 % of the height from the top, and more than 40 % down is a flag. The balcony takes sat at 38 and 39 %: too much empty space above the head, so move the camera closer or tilt it down a little.
- **Lens at eye level.** A phone low on a desk looking up reads as dominant; a high angle reads as weak (research, camera angle).
- **Mid-chest up** for any line with gestures, with the widest gesture kept about 10 % inside the frame (house). Rehearse it once and check it on the screen before the take.
- **The open side.** A website VSL with a lockup opens on a card covering about the left 38 % of the frame (`lockup` in `tools/studio/layers.py`: 70 px in and 650 px wide at 1080 tall), so stand in the centre or on the right third and keep the left plain and darker. A plain wall also gives chips somewhere to land (research: busy backgrounds push labels onto the speaker).
- **Where text lives.** On a 16:9 web VSL two caption lines sit from about 76 % to 89 % of the height (`caption_band` in `tools/studio/platforms.py`, the caption box in `tools/studio/longform.py`), so gestures stay above the bottom quarter of the frame. On a 9:16 cut the placement engine (`longform` with a layers file) puts text only between 6 % and 84 % across and 12 % and 70 % down (`PLACEMENT_RULES` in `tools/studio/placement.py`), so a labelled gesture belongs inside that box, at chest height. Paid reels need more: Meta asks for the bottom 35% to be free of text.
- **Tripod, always.** Held labels and the tracked camera assume a still background; handheld drift and moving plants or hair add jitter (research).

## 5. Delivery

- **Look into the lens.** Across 6.9M edX sessions, an informal desk recording with eye contact beat a studio lecture (Guo, Kim and Rubin, 2014).
- **Pace.** The house band in `FORMATS.md` (the Skool lesson checks) is 120 to 200 words per minute, inside Guo's measured 48 to 254 (mean 136); the research suggests aiming for 140 to 180. The balcony takes ran at 195 and 224.
- **One second of quiet between lines, hands at rest.** The cut splits only on a gap longer than 0.35 s (`GAP_MAX` in `tools/studio/cut.py`) and keeps up to 0.15 s of air on each side of a word, so a sentence end with less quiet than that runs into the next line and is hard to cut or move on its own. A full second leaves room (research: silence cutters pad 0.2 s each side). On the balcony takes 1 of 35 sentence ends had a second of quiet and 11 were too tight to cut.
- **Fluffs.** Stop, pause a second, restart the whole sentence, never mid-sentence, so the cut lands on a sentence boundary (house).
- **Repeat the lines that matter**, two or three times with different energy. `assemble` builds the video from beats picked from any take (`skills/video/vsl-builder/SKILL.md`), so a repeat is a choice for the editor, not a problem. Plan the pieces before the camera rolls; Hormozi's batch days run from a one-page run sheet ("an ounce of pre is worth a pound of post").
- **Gestures that carry a label.** The kit draws a label beside your hand at the top of the gesture, using the frames from 0.35 s before the word to 0.8 s after it, and takes it off when the hand drops by more than 0.12 of the frame height, when the caption line changes or the next label comes, and 1.6 s after the word at the latest; it stays up at least 0.45 s (`hand_events` in `tools/studio/layers.py`). So lift into the gesture just before the word and hold it still for about a second, at chest height on the open side. The whole hand, wrist to fingertips, stays inside the frame. Mark these lines in the script so the editor knows where they are.
- **Two labelled gestures per video at most**, one on each side of the screen: the layers file keys hand labels `L` and `R` by the half of the screen the hand is in, not by which hand it is, and each half yields one hand per frame. A label for a hand on the left of the screen is placed in the left 62 % of the frame, and one for a hand on the right in the right 62 %.
- **Slate every take.** Say the take and section aloud, then one clap in frame. The transcript then names the take, and the clap gives a sync point for the lav backup.

## 6. B-roll for a sales or coaching business

A house list (the research found no verified source for it):

- screen recordings of the real product or CRM, with every name blurred or fake
- close-up of hands typing
- a phone showing a booked-call notification
- a calendar filling up
- over the shoulder on a video sales call, with no client face or name visible
- writing a key number on a whiteboard (only a number you can source)
- walking into the office
- the team in a meeting, wide
- coffee and prep details before a call
- the building or the city, as an establishing shot
- client testimonial clips, filmed with written permission

Shoot each one 8 to 10 seconds, locked or moving slowly, at 30 fps, sideways, with no personal details on any screen. Why sideways: `longform` fills the frame with each clip and crops the rest (`render_overlay_clip` in `tools/studio/longform.py`), so a vertical clip in a 16:9 video keeps only a thin middle band. The engine plays B-roll silent, 3.2 s per cutaway, and when it reuses a clip it starts 3.7 s further in, so a 10 second clip gives two clean cutaways. Put the clips in one folder (`.mp4`, `.mov`, `.mkv` or `.m4v`), named in the order you want them used, and pass it as `--broll` (`skills/video/longform-editor/SKILL.md`).

## 7. After the shoot: check the takes

Run these on every raw take before writing a single beat. Tell the owner the result in plain words, one line per take, with the number that decided it.

**Step 1. The files.** Resolution, frame rate, sample rate and HDR, across every take (name each take after the `-`):

```bash
"$PY" - "$KIT/inbox/take1.mp4" "$KIT/inbox/take2.mp4" <<'EOF'
import json, subprocess, sys
rates = set()
for f in sys.argv[1:]:
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,width,height,r_frame_rate,sample_rate,color_transfer:format=duration", "-of", "json", f],
        capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    rates.add(v["r_frame_rate"])
    hdr = v.get("color_transfer") in ("arib-std-b67", "smpte2084")
    print(f"{f.split('/')[-1]}: {v['width']}x{v['height']} at {v['r_frame_rate']} fps, audio {a.get('sample_rate', 'none')} Hz, "
          f"{float(j['format']['duration']):.0f} s{', HDR' if hdr else ''}")
print("one frame rate across takes" if len(rates) == 1 else f"MIXED frame rates {sorted(rates)}")
EOF
```

**Step 2. The words and the face.** Analyse each take whole (no `--start` or `--end`):

```bash
T=take3
"$PY" "$KIT/tools/closer.py" analyze "$KIT/inbox/$T.mp4" --out "$KIT/output/shoot1/check/$T"
```

It prints the word count, the speech seconds and the share of frames with a face, and writes transcript.txt and analysis.json. A 70 second 4K take took 55 s in one run and 2 min 6 s in another on the Linux container we tested. Nothing is wasted: the assemble spec can point a take's `"words"` at this analysis.json, so the take is never transcribed again.

**Step 3. Delivery, framing, picture and sound.** Under a minute per take on the CPU we tested:

```bash
T=take3; VIDEO="$KIT/inbox/$T.mp4"; CHECK="$KIT/output/shoot1/check/$T"
"$PY" - "$KIT" "$VIDEO" "$CHECK" <<'EOF'
import json, subprocess, sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, sys.argv[1] + "/tools")
from studio import finish, sound
kit, video = sys.argv[1], Path(sys.argv[2])
an = json.loads((Path(sys.argv[3]) / "analysis.json").read_text())
w, s, tr = an["words"], an["sentences"], an.get("track") or {}
# delivery: pace and the pauses the cut needs
span = w[-1]["e"] - w[0]["s"]
gaps = [(a["e"], b["s"] - a["e"]) for a, b in zip(s, s[1:])]
tight = [round(t, 1) for t, g in gaps if g <= 0.35]
print(f"pace: {len(w) / span * 60:.0f} words per minute; face in {tr.get('coverage', 0):.0%} of frames")
print(f"pauses: {len(gaps)} sentence ends, {sum(g >= 1.0 for _, g in gaps)} with 1 s or more, too tight to cut at {tight}")
# framing: the eye line and the face's place across the width, from YuNet's eye points on 12 frames
W, H, fps, n = finish._probe(video)
aw, ah = 960, int(round(H * 960 / W / 2) * 2)
det = cv2.FaceDetectorYN.create(kit + "/tools/studio/models/face_detection_yunet_2023mar.onnx", "", (aw, ah), 0.6, 0.3, 50)
eyes, xs = [], []
for k in range(12):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(k + 0.5) * n / fps / 12:.2f}", "-i", str(video), "-frames:v", "1",
                          "-vf", f"scale={aw}:{ah}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    _, f = det.detect(np.frombuffer(raw, np.uint8).reshape(ah, aw, 3))
    if f is not None and len(f):
        f = max(f, key=lambda r: r[2] * r[3])
        eyes.append((f[5] + f[7]) / 2 / ah); xs.append((f[0] + f[2] / 2) / aw)
if eyes:
    print(f"framing: eye line at {np.median(eyes):.0%} of the height, face centre at {np.median(xs):.0%} of the width")
# picture: what the finish pass measures (face, sky, clipping) and what it would do about it
faces = [None] * n
for d in tr.get("dets", []):
    if "cx" in d:
        i = int(round((an["start"] + d["t"]) * fps))
        box = ((d["cx"] - d["fw"] / 2) * W, (d["cy"] - d["fh"] / 2) * H, (d["cx"] + d["fw"] / 2) * W, (d["cy"] + d["fh"] / 2) * H)
        faces[i:i + tr["stride"]] = [box] * len(faces[i:i + tr["stride"]])
st = finish.measure(video, faces)
print("picture:", st, "-> finish would move", {k: finish.plan(st, "vsl")[k] for k in ("sky_ev", "face_ev")})
# sound: what the voice cleaner measures in the pauses
y = sound.read_audio(video, start=an["start"], dur=an["dur"])
_, rep = sound.voice_master(y, [{"w": x["w"], "t": x["s"], "e": x["e"]} for x in w], log=lambda *a: None)
print(f"sound: rumble share in pauses {rep['low_rumble_share_in_pauses']} (high-pass {rep['highpass_hz']} Hz), "
      f"wind bursts {rep['wind_burst_frames']} frames = {rep['wind_burst_frames'] * 512 / 48000:.1f} s, room tone {rep['room_tone_dbfs']} dBFS")
EOF
```

OpenCV may print a `WARN` line about the graph engine; ignore it. A wind-burst frame is one STFT hop of the cleaner (512 samples at 48 kHz, about 10.7 ms), which is why the script turns the count into seconds.

**Step 4. The hands on every gesture line.** transcript.txt shows only where each sentence starts, so read the gesture words' times from analysis.json (on the take's own clock). Name the words after the analysis path:

```bash
T=take3; CHECK="$KIT/output/shoot1/check/$T"
"$PY" - "$CHECK/analysis.json" sell set <<'EOF'
import json, sys
an = json.load(open(sys.argv[1]))
for s in an["sentences"]:
    for w in an["words"][s["i0"]:s["i1"] + 1]:
        if w["w"].strip(".,?!").lower() in sys.argv[2:]:
            print(f'{w["w"]} at {w["s"]:.2f} s, in the line {s["s"]:.2f} to {s["e"]:.2f} s: {s["text"][:60]}')
EOF
```

Track from a little before the first gesture word to a little after its line ends (on the balcony take, "sell" at 34.54 s and "set" at 35.36 s in a line that ends at 36.36 s, so 33.9 to 36.6), then pass the face centre from step 3 (0.50 here):

```bash
T=take3; CHECK="$KIT/output/shoot1/check/$T"
"$PY" "$KIT/tools/closer.py" hands "$KIT/inbox/$T.mp4" --start 33.9 --end 36.6 --out "$CHECK/hands_34.json"
"$PY" - "$CHECK/hands_34.json" 0.50 <<'EOF'
import json, sys
rows, cx = json.load(open(sys.argv[1])), float(sys.argv[2])
half = 9 / 16 / (16 / 9) / 2                     # the widest 9:16 crop of a 16:9 frame is 31.6% of its width
seen = [h for r in rows for h in r["hands"]]
full = [h for h in seen if h["in_frame"]]
vert = [h for h in seen if h["left"] >= cx - half and h["right"] <= cx + half]
print(f"{len(rows)} frames, a hand in {sum(1 for r in rows if r['hands'])}; of {len(seen)} hands seen, "
      f"{len(full)} fully in frame ({len(full) / max(1, len(seen)):.0%}), {len(vert)} inside the 9:16 column ({len(vert) / max(1, len(seen)):.0%})")
for r in rows:
    cut = [h["side"] for h in r["hands"] if not h["in_frame"]]
    if cut:
        print(f"  {r['t']:.1f} s: hand {', '.join(cut)} touches the edge of the frame")
EOF
```

`in_frame` is true only when all 21 points of the hand sit more than 3 % inside every edge (`HAND_RULES` in `tools/studio/hands.py`). On the balcony take this stretch came back 16 of 20 hands fully in frame (80%) and 0 inside the 9:16 column.

**Step 5. The verdict.** One line per take: PASS, LOOK (listen or look before deciding) or RESHOOT.

| Check | PASS | LOOK | RESHOOT | Balcony takes | Where the line comes from |
|---|---|---|---|---|---|
| Frame rate | one rate, 30 fps | | mixed rates, or not 30 | 30 fps | research (never mix); `FPS` is 30 |
| HDR | none | HDR on one test clip | | none | nothing tone-maps; finish reads BT.709 only |
| Sample rate | 48000 Hz | 44100 Hz (the kit resamples to 48 kHz) | no audio track (or sync the lav backup by hand) | 44100 Hz | `SR` in `tools/studio/sound.py`; `assemble` encodes `-ar 48000` from the take's first audio stream |
| Resolution | 3840x2160 (2160x3840 when filmed vertical for reels) | 1920x1080 (no sharp 9:16) | | 3840x2160 | crop arithmetic |
| Face found | 50 % of frames or more | | under 50 % | 100 % | `longform` and `reel` track the camera only from 0.5; with no tracked camera there are no hand labels either |
| Pace | 120 to 200 wpm | outside the band | | 195, 224 | `FORMATS.md` house band |
| Pauses | every sentence end over 0.35 s | some too tight | the lines you need are all too tight | 11 of 35 tight | `GAP_MAX` |
| Eye line (from the top) | 30 to 36 % | 36 to 40 % | more than 40 % down | 38, 39 % | headroom research, house band |
| Rumble share in pauses | under 0.2 | 0.2 to 0.45 | over 0.45 | 0.24, 0.46 | 0.45 from `SOUND_RULES`; 0.2 from `docs/AUDIO_SPEC.md` (house) |
| Wind bursts | none heard | any; listen at headphone level | wind you can hear | 3.4 s, 5.1 s | no pass mark in the code yet |
| Face luma | 0.52 or more | 0.40 to 0.52 (the finish lifts it) | under about 0.40 | 0.33, 0.36 | target 0.52; the lift is capped at 0.30 EV, which a face under about 0.40 uses up |
| Sky luma | under 0.66 | 0.66 to about 0.86 (the finish pulls it down) | over about 0.86 | 0.80 | `FINISH_RULES`: pulled from 0.66, capped at 0.45 EV, which a sky over about 0.86 uses up |
| Clipped share | 0.002 or less | above 0.002: look at a frame | clipping on the face | 0.038, 0.049 | 0.002 is where the finish counts the highlights as hot |
| Hands on gesture lines | every frame `in_frame`, inside the 9:16 column | | any frame half out on a labelled word | 80%, 0 in column | research: anchor only to a hand fully in frame |

A take can be cut even with a RESHOOT line; say what it will cost (a dark face, wind under the voice, no label on that gesture, a line that cannot be moved) and let the owner decide.

## 8. Honest limits

- There is no single ingest command yet. The research plans one that grades each take PASS, WARN or RESHOOT with timestamps; until it lands, section 7 is the check.
- The rumble share missed one balcony take (0.24, under the 0.45 trigger) that had 5.1 s of wind bursts, and the code has no pass mark for bursts. Listen to the pauses on headphones every time.
- The kit does not measure noise under speech on a raw take. The research target is room noise at least 30 dB under the voice (house); judge it by ear.
- The kit uses the camera file's own audio track (`assemble` takes the take's first audio stream). Nothing yet syncs the lav's backup file in by the clap; that is a manual job.
- A second camera angle hides jump cuts between repeated lines (research), but the kit cannot sync two cameras. If a beat comes from the second camera, it plays that camera's own sound, so feed the lav to both cameras or skip the second angle.
- The hand-label code skips hands under `min_px` (2500 millionths of the frame, cleared easily from mid-chest: the balcony hands measured 38030 to 101566) but does not read `in_frame`, so it can pin a label on a hand that is half out of the frame. That is why step 4 checks it before a label is written (`skills/video/placement/SKILL.md`).
- Hand labels are drawn only on an assembled selects file (its beats map take time to the cut) with a tracked camera; without either, no label appears and nothing says so (`hand_events` in `tools/studio/layers.py`).
- The Windows python path on the PY line follows `install.ps1`, which has not yet been run on a Windows machine.

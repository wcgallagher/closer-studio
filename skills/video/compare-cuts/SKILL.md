---
name: compare-cuts
description: Judges two edits of the same video honestly. Measures both with the compare command (synced players, wipe, difference view, cut markers, momentary loudness, brightness and contrast, saturation, motion, face on screen, filmstrips, a numbers table, DNSMOS when installed) and then runs a blind A/B, with labels A and B only, a random order, fresh reviewers who look at contact sheets and frames at every cut and card, a seven-part rubric, and the order swapped to cancel position bias. The votes go into judge.json so the page shows the panel. Use when someone asks "is v9 better than v8", "which cut wins", "compare these two", "did the new hook help", before a new cut replaces a shipped one, or after a regrade of the same edit.
---

# Compare cuts

Two cuts of the same video go in, usually the last shipped cut and the new one. The engine measures both and draws them on one page. Then a blind panel judges what numbers cannot, such as whether a stranger would stop and whether they would believe it. One cut on its own goes to `skills/video/cold-review/SKILL.md` instead.

Nothing here listens. The engine measures the sound, and no reviewer can hear it, because reviewers only see frames and read numbers. Audio is judged by the numbers on the page and by the owner's ears, never by a reviewer's opinion of how it "sounds".

## 0. Where things are

```bash
KIT="$(cat ~/.closer-studio/kit_path 2>/dev/null || pwd)"
PY="$HOME/.closer-studio/venv/bin/python"; [ -x "$PY" ] || PY="$HOME/.closer-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
```

On a Mac or Linux, run the commands in Terminal. On Windows, run them in Git Bash or WSL: the middle `PY` path is the venv that `install.ps1` makes. Shell variables do not carry over from one command to the next, so start every block below with these two lines, plus the three path lines from section 1 once you have set them.

Optional, once: this adds the DNSMOS voice score (it installs only when the import fails).

```bash
"$PY" -c "from speechmos import dnsmos" 2>/dev/null || "$PY" -m pip install speechmos onnxruntime requests
```

The settings are `COMPARE_RULES` in `tools/studio/compare.py` and the page is `tools/studio/compare_template.html`. When this file and the code disagree, the code wins and this file gets fixed. Without speechmos the page still works and the table simply has no DNSMOS row.

## 1. Measure both cuts

```bash
A="$KIT/output/<job>/v8/<file>.mp4"      # left player, first label
B="$KIT/output/<job>/v9/<file>.mp4"      # right player, second label
C="$KIT/output/<job>/compare_1"          # a new folder for every new pair, no version in its name
"$PY" "$KIT/tools/closer.py" compare "$A" "$B" --out "$C" --labels v8,v9
```

Pass full paths: the engine stores them as given, and the blind packs in section 3 look for each cut's job.json and captions.srt beside it. It writes compare.json (every measure for both cuts) and compare.html. The page plays two web copies beside it, a.mp4 and b.mp4 (960 px wide, CRF 30). Open compare.html from that folder in any browser. Measuring takes a while: a 95 s 1080p cut plus a 12 s cut took 2 min 36 s on a test machine, so say how long before a long pair.

New pair, new folder. The engine reuses a.mp4 and b.mp4 when they already exist, so a different pair in an old folder plays the old videos beside the new numbers. Running the same pair into the same folder again (to add judge.json) is safe. Name the folder compare_1, compare_2 and so on, never after a version: the reviewers in section 3 are given paths inside it.

## 2. Read the page

| On the page | What it is | Read it for |
|---|---|---|
| Side by side, Play both | Both players start together; the right one follows the left and jumps back in step when they drift more than 0.08 s apart (checked every 120 ms) | The moment one of them loses you |
| Sound button | One cut is audible at a time, the right one by default | The same line in both, back to back |
| Wipe | The right cut drawn over the left one, visible to the right of the handle | A face or a card, dragged across |
| Difference | The right cut blended over the left; black where the frames match | Only the same edit with a new grade or encode. Between two different edits it lights up after the first changed cut and means nothing |
| Cuts | Every detected cut, the left cut's marks on the top half and the right cut's below; punch-ins count | Where the rhythm differs. Two marks 0.2 to 0.3 s apart are usually one dissolve or one card coming in or going out |
| Loudness, momentary | Loudness over 400 ms windows, a point every 0.2 s, drawn from -45 to -5 LUFS | A hook quieter than the body, holes where the sound drops, music rising over the voice, an end card louder than the talk |
| Brightness and contrast | Thick line: average brightness. Thin line: contrast, scaled to fit | A jump at a take change (the grade does not match) |
| Colour (saturation) | Average saturation | A card or a moment that shifts colour against the footage |
| Motion | Average change between samples, 4 samples a second | Long flat stretches, where the eye rests or leaves |
| Face on screen | A bar wherever the YuNet detector in `tools/studio/models` found a face, 2 checks a second | Long gaps are cards. The face carries trust: full-screen cards about half the runtime or less (`skills/video/vsl-builder/SKILL.md`) |
| Filmstrips | One frame every 2 s at 240 px. Click a frame or any track to jump there | A quick scan of both cuts, shot by shot |
| The numbers | The table below | Section 2a |
| Blind judges | The panel from judge.json (section 3), or a note that there is no verdict yet | Section 3e |

### 2a. The numbers table

| Row | Measured as | Green mark goes to |
|---|---|---|
| Length | the file's duration | no mark |
| Loudness | integrated LUFS, gated as BS.1770 (-70 LUFS absolute, -10 LU relative) | the one nearer -14 LUFS |
| True peak | 4x oversampled peak, dBTP | the one at or under -1 dBTP, only when the other is over |
| Loudness range (approx.) | P95 minus P10 of the short-term (3 s) loudness above -50 LUFS; close to EBU LRA but not the same | no mark |
| Shots | the number of shots; the figure in brackets is cuts per minute | no mark |
| Longest shot | seconds | the shorter |
| Face on screen | share of the checks that found a face | no mark |
| Clipped highlights | share of pixels brighter than 98% of white | the lower |
| Saturation | average | no mark |
| DNSMOS overall (mix) | only when speechmos is installed | the higher |

Read the green marks with care:

- The targets are fixed in the page at -14 LUFS and -1 dBTP for every platform. A web VSL is mixed to -15 LUFS and -1.2 dBTP, and every other platform but broadcast to -14 LUFS and -1.5 dBTP (`closer.py platforms` prints every target). So a correctly mixed VSL can lose the loudness mark, and a reel at -1.2 dBTP can win the true peak mark while it misses its -1.5 target. Read the number against the platform's target, not the colour.
- When both cuts are equally far from a target, the mark goes to the left cut. Ignore it then.
- The footnote under the table names targets for cut rate and face time, but those rows never get a mark.
- True peak can read low. On a test cut the page said -1.8 dBTP where ffmpeg's own meter said -1.7 and the cut's job.json said -1.65. Check a close call with the command below, and trust the job's report over the page.
- DNSMOS is Microsoft's speech-quality model: it guesses the mean opinion score listeners would give the voice (higher is better). The engine runs it on the full mix in 9.01 s windows, so music pulls the background score down by design. Compare A with B only when both carry the same music plan. A cut of 9.01 s or less gets no score: compare.json holds NaN for it and numbers.txt says not measured. The page then drops the row when the short cut is the left one, and when it is the right one it prints NaN and gives NaN the green mark. Ignore DNSMOS for that pair.

```bash
ffmpeg -nostats -hide_banner -i "$A" -af ebur128=peak=true -f null - 2>&1 | tail -12
```

Its last lines give the integrated loudness (`I:`) and the true peak (`Peak:`, which ffmpeg labels dBFS although it is the true peak). When the two cuts' loudness differs by more than 0.5 LU, say so before anyone listens: the louder cut tends to win a listening test for that reason alone.

## 3. The blind A/B

A judge that made the edit favours its own work, so no judge sees the plan or the version names. A judge shown two options also favours one position, and more so when the two are close. So labels A and B only, a random order, fresh reviewers, and both orders every time.

### 3a. Build the packs

```bash
"$PY" - "$C" <<'EOF'
import json, math, random, shutil, subprocess, sys
from pathlib import Path
c = Path(sys.argv[1]).resolve()
d = json.loads((c / "compare.json").read_text())
if (c / "votes").exists():
    sys.exit("votes already exist for the current key: move the votes folder away before a new draw")
fit = lambda n: f"scale={n}:{n}:force_original_aspect_ratio=decrease:force_divisible_by=2"
tc = lambda t: f"{int(t // 60)}m{t % 60:05.2f}s"
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True)

def pack(side, dst):
    m = d[side]; f = Path(m["file"]).resolve(); dur = m["probe"]["duration"]
    dst.mkdir(parents=True)
    ff("-i", f, "-vf", f"fps=1,{fit(320)},tile=6x5", dst / "sheet_%02d.jpg")
    ff("-i", f, "-t", 3, "-vf", f"fps=6,{fit(320)},tile=6x3", "-frames:v", 1, dst / "hook.jpg")
    for t in [t for t in m["cuts"] if t < dur - 0.2]:
        ff("-ss", max(t - 0.1, 0), "-i", f, "-ss", t, "-i", f, "-filter_complex",
           f"[0:v]{fit(640)}[x];[1:v]{fit(640)}[y];[x][y]hstack", "-frames:v", 1, dst / f"cut_{tc(t)}.jpg")
    job = f.parent / "job.json"
    s = json.loads(job.read_text())["summary"] if job.exists() else {}
    if s.get("file") and Path(s["file"]).resolve() == f:
        for g in s.get("scenes", []):
            for t in sorted({round(min(g["start"] + 0.5, g["end"] - 0.1), 2), round((g["start"] + g["end"]) / 2, 2)}):
                ff("-ss", t, "-i", f, "-frames:v", 1, "-vf", fit(960), dst / f"card_{tc(t)}.jpg")
    if (f.parent / "captions.srt").exists():
        shutil.copy(f.parent / "captions.srt", dst / "captions.srt")
    a, sh, dn = m["audio"], m["shots"], m["audio"].get("dnsmos", {})
    (dst / "numbers.txt").write_text("\n".join([
        f"length {dur:.1f} s",
        f"loudness {a['lufs']} LUFS integrated, true peak {a['true_peak']} dBTP, range about {a['lra_approx']} LU",
        f"DNSMOS on the full mix (higher is better): overall {dn['ovrl_mos']}, voice {dn['sig_mos']}, background {dn['bak_mos']}"
        if not math.isnan(dn.get("ovrl_mos", math.nan)) else "DNSMOS: not measured",
        f"shots {sh['n']} ({sh['per_min']} cuts per min), median {sh['median_s']} s, longest {sh['max_s']} s",
        f"face on screen in {round(m['faces']['share'] * 100)} % of samples", ""]))

first = random.choice(["a", "b"]); other = "b" if first == "a" else "a"
blind = c / "blind"
if blind.exists():
    shutil.rmtree(blind)
pack(first, blind / "order1" / "A"); pack(other, blind / "order1" / "B")
shutil.copytree(blind / "order1" / "A", blind / "order2" / "B"); shutil.copytree(blind / "order1" / "B", blind / "order2" / "A")
L = dict(zip("ab", d["labels"]))
(c / "key.json").write_text(json.dumps({"order1": {"A": L[first], "B": L[other]}, "order2": {"A": L[other], "B": L[first]}}))
print("packs in", blind, "; key in", c / "key.json", "(never show it to a reviewer)")
EOF
```

The draw decides which cut is A in order 1, and order 2 swaps them. Each letter's folder holds:

- hook.jpg: the first 3 s at six frames a second, the same window cold-review uses.
- sheet_01.jpg and on: one frame a second, six across and five down, so sheet_01 covers 0:00 to 0:29 and sheet_02 starts at 0:30.
- cut_<time>.jpg for every detected cut except one in the last 0.2 s: the left half a tenth of a second before, the right half on the cut.
- card_<time>.jpg for every card in the cut's job.json (0.5 s after it lands, or 0.1 s before it leaves when the card lasts under 0.6 s, and again at its middle), 960 px on the long side. Card frames come only when that job.json's summary names this same file, so a cut moved or copied away from its job folder gets none. When a cut has cards, check that its card_ files exist before you brief anyone.
- captions.srt when the cut's folder has one, and numbers.txt with the audio and pacing numbers (no green marks).

File names carry only the time, never a name or a version. Every image stays at or under 1920 px on its long side, inside the 2576 px that Claude reads at full detail. A 95 s cut with 9 cards gave 45 images (4 sheets, the hook, 22 cut frames, 18 card frames), and packing it beside a 12 s cut took 39 s. key.json is the answer: never show it or compare.html to a reviewer, and never point one at the job folders.

### 3b. Brief the reviewers

Three fresh reviewers per order, six in all. Start each one the way section 2 of `skills/video/cold-review/SKILL.md` starts a reviewer (a fresh agent, never a fork of this session). The session that made the edit never judges it. Give each reviewer only its order folder and this brief:

```text
You are judging two cuts of the same video, A and B. Platform and audience: <one line>.
Look at every file in <C>/blind/order<N>/A and <C>/blind/order<N>/B and nothing outside them.
File names are times. cut_0m33.47s.jpg is the cut at 0:33.47 (left half just before it, right half on it).
card_ files are on-screen graphics. hook.jpg is the first 3 s at six frames a second. sheet_01.jpg is one
frame a second from 0:00, six across and five down; sheet_02.jpg starts at 0:30. Picture every frame on a
phone, 360 px wide.
You cannot hear either cut. Score the audio only from numbers.txt. Target: <LUFS> LUFS integrated, true
peak at or under <dBTP> dBTP.
For each of the seven criteria below, first write the evidence for A and for B with timecodes, then give
each a score from 1 to 5. Pick only after all seven.
<the rubric table from section 3c>
End with this JSON and nothing after it:
{"pick": "A" or "B" or "tie", "score_a": <mean of A's seven scores, one decimal>, "score_b": <same for B>,
 "why": "<one sentence on what decided it, without the letters A and B>",
 "fix_a": ["<timecode: fix>"], "fix_b": ["<timecode: fix>"]}
```

Fill the targets from `closer.py platforms` for the cut's platform. Reject an answer that picks before the evidence or cites no timecodes, and brief a new reviewer instead.

### 3c. The rubric

| Criterion | Look at | A 5 means |
|---|---|---|
| Stopping power in 3 s | hook.jpg, the first row of sheet_01 | a stranger scrolling would stop: something worth staying for is on screen by 0.5 s and clear by 1.0 s |
| Clarity | captions and cards | a stranger could say what this is and who it is for, and every card reads at 360 px wide |
| Proof | cards, captions | the reason to believe is on screen early, and no number appears that nothing backs (`HOUSE_RULES.md`) |
| Pacing | sheets, numbers.txt | no stretch without a visible change longer than the clock in `skills/video/edit-grammar/SKILL.md` allows for this format |
| Aesthetics | everything | natural skin and grade, steady framing, clean type, cards and footage that look like one video |
| Placement errors | cut_ and card_ frames | none: no caption on a face or on a card's key line, no label over the face, nothing cut off at an edge, no card content in the caption band (the bottom fifth) |
| Audio numbers | numbers.txt | loudness within 1 LU of the target and true peak at or under it; DNSMOS weighed only against the other cut |

### 3d. Swap and count

A cut wins only when it takes the majority of reviewers in order 1 and again in order 2. Anything else is a tie and goes to the owner. Close cuts tie more often, because position bias grows as the gap between two options shrinks; a run of ties means the two cuts are not really different. Report both counts every time, never one total.

### 3e. Write judge.json

Save each reviewer's closing JSON as `<C>/votes/R1.json` to `<C>/votes/R6.json`, adding `"order": 1` or `"order": 2`. Then unblind and count:

```bash
"$PY" - "$C" <<'EOF'
import json, sys
from pathlib import Path
c = Path(sys.argv[1]).resolve()
key = json.loads((c / "key.json").read_text()); la, lb = json.loads((c / "compare.json").read_text())["labels"]
votes, picks = [], {"1": [], "2": []}
for p in sorted((c / "votes").glob("*.json")):
    v = json.loads(p.read_text()); k = key["order" + str(v["order"])]
    score = {k["A"]: v["score_a"], k["B"]: v["score_b"]}; pick = k.get(v["pick"], "tie")
    votes.append({"judge": f"{p.stem}, order {v['order']}", "pick": pick, "score_a": score[la], "score_b": score[lb], "why": v["why"]})
    picks[str(v["order"])].append(pick)
win = {o: next((x for x in (la, lb) if ps.count(x) * 2 > len(ps)), "tie") for o, ps in picks.items()}
verdict = win["1"] if win["1"] == win["2"] != "tie" else "tie, the owner decides"
count = lambda ps: ", ".join(f"{x} {ps.count(x)}" for x in (la, lb, "tie") if ps.count(x))
summary = f"{la} against {lb}, blind, both orders. Order 1: {count(picks['1'])}. Order 2: {count(picks['2'])}. Result: {verdict}."
(c / "judge.json").write_text(json.dumps({"summary": summary, "votes": votes}, indent=1))
print(summary)
EOF
"$PY" "$KIT/tools/closer.py" compare "$A" "$B" --out "$C" --labels v8,v9
```

The second command measures both cuts again (nearly as long as the first run) and puts the panel on the page; the engine reads judge.json only while it builds the page. The file looks like this:

```json
{"summary": "v8 against v9, blind, both orders. Order 1: v8 1, v9 2. Order 2: v9 2, tie 1. Result: v9.",
 "votes": [{"judge": "R1, order 1", "pick": "v9", "score_a": 3.1, "score_b": 3.6, "why": "opens on the face"}]}
```

- `summary`: both order counts and the result, printed first on the page.
- `judge`: the reviewer and the order it judged.
- `pick`: a label from `--labels`, or `tie`. Never a letter, because letters change meaning between orders.
- `score_a` and `score_b`: that reviewer's mean for the first file given to compare (the left player) and for the second, whichever letter the reviewer saw. The page prints each vote as "picked v9 (3.1 vs 3.6)".
- `why`: one sentence, printed after the scores.

## 4. The owner's ears

Reviewers cannot hear; the owner can. Open compare.html and play the opening and the densest stretch of both, pressing the Sound button on the same line. Listen for a voice that sounds clean but not processed, music felt under the words rather than over them, hits on the frame rather than early, and an ending that lands with the last word. When the loudness rows differ by more than 0.5 LU, tell the owner first. For a blind listen, run compare again into a new folder with the two files in order 1's order (key.json says which is A) and `--labels A,B`, and give the owner only that page.

## 5. Decide

- The panel picks the same cut in both orders and the owner agrees: ship it after its fixes (its `fix_a` or `fix_b` lists), and log what changed and why.
- A tie, or the owner disagrees with the panel: the owner's pick ships.
- Keep score. Note the owner's pick next to the panel's every time. The panel only advises until it has matched the owner on about 80% of at least 20 pairs.
- A VSL with traffic gets a live split test on the page; bookings and play-through outrank both the panel and the owner.

## Same edit, a different grade or encode

When both files share one timeline (the same frames at the same size, with only the grade or the encode changed), full-reference scores mean something:

```bash
cd "$C" && ffmpeg -hide_banner -i "$A" -i "$B" -lavfi "[0:v][1:v]ssim=stats_file=ssim.log;[0:v][1:v]psnr=stats_file=psnr.log" -f null - 2>&1 | grep -E "SSIM|PSNR"
```

Run it from the compare folder so the log names inside the filter carry no drive letter (a Windows colon breaks a filter option). Never quote SSIM or PSNR between two different edits: they compare frame n with frame n, and after the first changed cut those are unrelated frames. VMAF needs an ffmpeg built with libvmaf; when one version adds sharpening or contrast, use its NEG model, since plain VMAF rewards enhancement.

## Rules

- Labels A and B only. No file name, version, date or plan reaches a reviewer.
- Both orders, every time, and a win must hold in both.
- Evidence with timecodes before any pick.
- Audio is the numbers and the owner's ears. Never write that a reviewer heard anything.
- Report the page as measured, not listened, and never claim a run that did not happen.

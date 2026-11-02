// Renders the motion-graphic scenes in scenes.html to frame-exact 30 fps clips with headless Chromium.
// Usage: node render.js <graphics.json> <out_dir> [--stills t1,t2,...] [--only scene]
// graphics.json: [{ "id": "g1", "scene": "crm", "dur": 7.6, "cues": { "c401": 3.1, ... } }, ...]
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const [spec, outDir] = process.argv.slice(2);
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const stills = arg("--stills") ? arg("--stills").split(",").map(Number) : null;
const only = arg("--only");
const FPS = 30;
const here = __dirname;
const HTML = arg("--html") ? path.resolve(arg("--html")) : path.join(here, "scenes.html");
const ICONS = Object.fromEntries(fs.readdirSync(path.join(here, "icons")).filter((f) => f.endsWith(".svg"))
  .map((f) => [f.slice(0, -4), fs.readFileSync(path.join(here, "icons", f), "utf8").replace(/<!--.*?-->/s, "")]));

// a clip is reusable when its scene, length and cue offsets match; where it sits in the timeline does not matter
const SRC_MTIME = fs.statSync(HTML).mtimeMs;
const key = (g) => JSON.stringify({ scene: g.scene, dur: Number(g.dur).toFixed(2), alpha: !!g.alpha, text: g.text || null,
  cues: Object.fromEntries(Object.entries(g.cues || {}).map(([k, v]) => [k, Number(v).toFixed(2)])) });
const fresh = (stored) => stored._src === undefined || stored._src === SRC_MTIME;   // legacy entries carry no source stamp
async function renderOne(browser, g) {
  const ext = g.alpha ? "mov" : "mp4";   // alpha scenes keep a transparent background (overlay beside the speaker)
  if (!stills && fs.existsSync(path.join(outDir, `${g.id}.${ext}`)) && fs.existsSync(path.join(outDir, `${g.id}.json`)) &&
      (() => { const st = JSON.parse(fs.readFileSync(path.join(outDir, `${g.id}.json`), "utf8")); return fresh(st) && key(st) === key(g); })()) { console.log(`${g.id} cached`); return; }
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.addInitScript(([cfg, icons]) => { window.CFG = cfg; window.ICONS = icons; }, [g, ICONS]);
  await page.goto("file://" + HTML);
  await page.waitForFunction(() => window.READY === true);
  await page.evaluate(() => document.fonts.ready);
  const dir = path.join(outDir, g.id);
  fs.mkdirSync(dir, { recursive: true });
  const times = stills || Array.from({ length: Math.round(g.dur * FPS) }, (_, i) => i / FPS);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate((t) => window.render(t), times[i]);
    await page.screenshot({ path: path.join(dir, stills ? `still_${times[i].toFixed(2)}.png` : `f${String(i).padStart(5, "0")}.png`), omitBackground: !!g.alpha });
  }
  await page.close();
  if (!stills) {
    const enc = g.alpha ? ["-c:v", "qtrle", "-pix_fmt", "argb"] : ["-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
      "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"];   // PNG frames are RGB: convert with the BT.709 matrix, not the 601 default
    execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(dir, "f%05d.png"),
      ...enc, "-r", String(FPS), path.join(outDir, `${g.id}.${ext}`)]);
    for (const f of fs.readdirSync(dir)) if (f.endsWith(".png")) fs.unlinkSync(path.join(dir, f));
    fs.writeFileSync(path.join(outDir, `${g.id}.json`), JSON.stringify({ ...g, _src: SRC_MTIME }));
  }
  console.log(`${g.id} ${g.scene} ${times.length} frames`);
}

(async () => {
  const all = JSON.parse(fs.readFileSync(spec, "utf8")).filter((g) => !only || g.scene === only || g.id === only);
  const browser = await chromium.launch();
  const queue = [...all];
  const workers = Array.from({ length: Math.min(3, queue.length) }, async () => { while (queue.length) await renderOne(browser, queue.shift()); });
  await Promise.all(workers);
  await browser.close();
})();

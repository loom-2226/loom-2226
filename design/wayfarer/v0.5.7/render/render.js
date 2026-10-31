// render.js -- ALL bodies. ALL sponsors. 2026-2226.
// Renders every view in views.json with headless Chromium and writes PNGs plus
// out/manifest.json (each file with the geometry hash it was made from).
// Usage: node render.js [viewId ...]   (serves ../ on a local port)
const {chromium} = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path"), crypto = require("crypto");
const ROOT = path.resolve(__dirname, "..");
const geo = fs.readFileSync(path.join(ROOT, "out/wayfarer_v05_geometry.json"));
const sha = crypto.createHash("sha256").update(geo).digest("hex");
const types = {".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml"};
const srv = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split("?")[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {"Content-Type": types[path.extname(f)] || "application/octet-stream"}); fs.createReadStream(f).pipe(res);
});
(async () => {
  await new Promise(r => srv.listen(0, "127.0.0.1", r));
  const port = srv.address().port;
  const V = JSON.parse(fs.readFileSync(path.join(__dirname, "views.json")));
  const want = process.argv.slice(2);
  const browser = await chromium.launch({args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]});
  const page = await browser.newPage({viewport: {width: V.size[0], height: V.size[1]}, deviceScaleFactor: 1});
  page.on("console", m => { if (m.type() === "error") console.log("console:", m.text()); });
  page.on("pageerror", e => console.log("pageerror:", e.message));
  const manPath = path.join(__dirname, "out/manifest.json");
  const man = fs.existsSync(manPath) ? JSON.parse(fs.readFileSync(manPath)) : {files: []};
  for (const v of V.views) {
    if (want.length && !want.includes(v.id)) continue;
    const t0 = Date.now();
    await page.goto(`http://127.0.0.1:${port}/render/render.html?view=${v.id}&sha=${sha}`);
    await page.waitForFunction("window.__done === true", null, {timeout: 600000});
    const file = `${v.id}.png`;
    await page.screenshot({path: path.join(__dirname, "out", file), timeout: 400000});
    const info = await page.evaluate("window.__info");
    man.files = man.files.filter(f => f.file !== file);
    man.files.push({file, kind: v.kind, title: v.title, geometry_sha256: sha});
    console.log(v.id, info.tris, "triangles", ((Date.now() - t0) / 1000).toFixed(1), "s");
  }
  // deck plans (SVG drawn by deckplans.py) -> PNG
  if (!want.length || want.includes("decks")) {
    const svgs = fs.readdirSync(path.join(__dirname, "out")).filter(f => /^deck_.*\.svg$/.test(f)).sort();
    for (const f of svgs) {
      const svgTxt = fs.readFileSync(path.join(__dirname, "out", f), "utf8");
      const m = svgTxt.match(/width="(\d+)" height="(\d+)"/);
      const dp = await browser.newPage({viewport: {width: +m[1], height: +m[2]}, deviceScaleFactor: f.includes("overview") ? 1 : 1.5});
      await dp.goto(`http://127.0.0.1:${port}/render/out/${f}`);
      const png = f.replace(".svg", ".png");
      await dp.screenshot({path: path.join(__dirname, "out", png)}); await dp.close();
      man.files = man.files.filter(x => x.file !== png);
      man.files.push({file: png, kind: "deckplan", title: f, geometry_sha256: sha});
      console.log(png);
    }
  }
  man.geometry_sha256 = sha; man.header = "ALL bodies. ALL sponsors. 2026-2226."; man.status = "VISUAL REFERENCE images generated from the hashed v0.5 geometry";
  fs.writeFileSync(manPath, JSON.stringify(man, null, 1));
  await browser.close(); srv.close();
})();

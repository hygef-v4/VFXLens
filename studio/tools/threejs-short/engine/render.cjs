// node render.cjs [out.mp4] [w] [h] [fps] [still-seconds...]
// Production copy (v2): resilient — each frame has a 60 s cap; on a hung/failed frame the browser is relaunched and the
// render resumes at that frame (ffmpeg keeps its pipe), shaders are warmed before frame 0, ffmpeg stderr is drained.
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const puppeteer = require('puppeteer-core');
const ROOT = __dirname, [, , OUT = 'out/preview.mp4', w = '960', h = '540', fps = '24', ...stills] = process.argv;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const CHROME = process.env.CHROME || ['C:/Program Files/Google/Chrome/Application/chrome.exe', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'].find(f => fs.existsSync(f));
(async () => {
  const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(0);
  const url = `http://127.0.0.1:${srv.address().port}/${process.env.PAGE || 'index.html'}?w=${w}&h=${h}&look=${process.env.LOOK || 'c'}&style=${process.env.STYLE || 'ph'}${process.env.XQ || ''}`;
  let browser = null, page = null, gpuBad = false, sinceOpen = 0;   // gpuBad: OOM / lost context seen in the page log
  const open = async () => {
    if (browser) { const pr = browser.process(); await Promise.race([browser.close().catch(() => {}), new Promise(r => setTimeout(r, 5000))]); try { pr && pr.kill('SIGKILL'); } catch {} }
    browser = await puppeteer.launch({ executablePath: CHROME, headless: true, protocolTimeout: 60000, args: [process.platform === 'darwin' ? '--use-angle=metal' : process.platform === 'win32' ? '--use-angle=d3d11' : '--use-gl=angle', '--enable-gpu', '--ignore-gpu-blocklist'] });
    page = await browser.newPage(); page.on('pageerror', e => console.log('PAGE ERROR', e.message)); page.on('console', m => { const x = m.text(); if (/OUT_OF_MEMORY|CONTEXT_LOST|context lost/i.test(x)) gpuBad = true; /* VALIDATE_STATUS warnings are harmless here */ if (!/X3595|404/.test(x)) console.log('console:', x); }); gpuBad = false; sinceOpen = 0;
    await page.goto(url); await page.waitForFunction('window.ready', { timeout: 180000 });
    await page.evaluate(() => { const D = window.DUR; for (const k of [0.1, 0.35, 0.6, 0.9]) window.frame(D * k); });   // warm shaders/textures before the real frames
  };
  const shot = async t => { if (sinceOpen >= 300) await open(); for (let a = 0; ; a++) { try { const d = await page.evaluate(x => window.frame(x), t); sinceOpen++; if (!gpuBad && d.length > 60000) return d; throw new Error(gpuBad ? 'GPU error in page log' : 'blank frame ' + d.length); } catch (e) { if (a >= 3) throw e; console.log(`\nframe t=${t.toFixed(3)} failed (${e.message.slice(0, 60)}), relaunching browser`); await open(); } } };
  await open();
  fs.mkdirSync(path.join(ROOT, path.dirname(OUT)), { recursive: true });
  if (stills.length) {
    for (const s of stills) { const d = await shot(+s); fs.writeFileSync(path.join(ROOT, path.dirname(OUT), `still-${s}.jpg`), Buffer.from(d.split(',')[1], 'base64')); }
  } else {
    const dur = await page.evaluate(() => window.DUR), n = Math.round(dur * +fps), t0 = Date.now();
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', path.join(ROOT, OUT)]);
    let ffDead = null; ff.stderr.on('data', d => process.stderr.write('ffmpeg: ' + d)); ff.stdin.on('error', e => { ffDead = e; });
    const done = new Promise(r => ff.on('close', code => { if (code) ffDead = ffDead || new Error('ffmpeg exited ' + code); r(code); }));
    for (let f = 0; f < n; f++) { const d = await shot(f / +fps); if (ffDead) throw ffDead;
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise((r, j) => { const c = () => j(ffDead || new Error('ffmpeg closed')); ff.once('close', c); ff.stdin.once('drain', () => { ff.off('close', c); r(); }); });
      if (f % 24 === 0) process.stdout.write(`\r${f}/${n}`); }
    ff.stdin.end(); await done; if (ffDead) throw ffDead; console.log(`\n${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s -> ${OUT}`);
  }
  await browser.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });

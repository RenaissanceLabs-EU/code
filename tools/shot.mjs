// Screenshot built pages in headless Chrome.  node tools/shot.mjs OUTDIR [--mobile] [--dark] [--full] /path/ ...
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from './node/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
const here = path.dirname(fileURLToPath(import.meta.url)), docs = path.join(here, '..', 'docs');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json' };
const resolve = (p) => { p = decodeURIComponent(p.split('?')[0].split('#')[0]); let f = path.join(docs, p); if (p.endsWith('/')) f = path.join(f, 'index.html'); return f; };
const server = http.createServer((q, r) => { const f = resolve(q.url); if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); });
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const args = process.argv.slice(2), out = args.shift(), mobile = args.includes('--mobile'), dark = args.includes('--dark'), full = args.includes('--full');
const paths = args.filter((a) => !a.startsWith('--'));
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--no-sandbox'] });
for (const p of paths) {
  const page = await b.newPage(); await page.setViewport(mobile ? { width: 390, height: 844, isMobile: true, deviceScaleFactor: 1 } : { width: 1280, height: 900 });
  if (dark) await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
  page.on('pageerror', (e) => console.log('ERR', p, e.message)); page.on('console', (m) => { if (m.type() === 'error') console.log('CONSOLE', p, m.text()); });
  await page.goto(`http://127.0.0.1:${server.address().port}${p}`, { waitUntil: 'load' }); await new Promise((r) => setTimeout(r, 300));
  const name = (p.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home') + (mobile ? '_m' : '') + (dark ? '_d' : '') + '.png';
  await page.screenshot({ path: path.join(out, name), fullPage: full }); console.log('shot', name); await page.close();
}
await b.close(); server.close();

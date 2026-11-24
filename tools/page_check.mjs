// Loads every built page in headless Chrome (desktop + mobile), checks console errors, failed requests,
// horizontal overflow, and that internal links resolve. Optionally exercises the catalog filters and the recipe planner.
//   node tools/page_check.mjs            (all pages from docs/sitemap.xml)
//   node tools/page_check.mjs /recipe/ /  (only these paths)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import puppeteer from './node/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
const here = path.dirname(fileURLToPath(import.meta.url));
const docs = path.join(here, '..', 'docs');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json', '.txt': 'text/plain', '.xml': 'application/xml', '.csv': 'text/csv' };
const resolve = (p) => { p = decodeURIComponent(p.split('?')[0].split('#')[0]); let f = path.join(docs, p); if (p.endsWith('/')) f = path.join(f, 'index.html'); return f; };
const server = http.createServer((req, res) => {
  const f = resolve(req.url);
  if (!f.startsWith(docs) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end('nf'); }
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;
let paths = process.argv.slice(2);
if (!paths.length) paths = [...fs.readFileSync(path.join(docs, 'sitemap.xml'), 'utf8').matchAll(/<loc>https:\/\/code\.renaissancelabs\.eu([^<]*)<\/loc>/g)].map((m) => m[1]);
const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--no-sandbox'] });
let bad = 0; const linkBad = new Set();
for (const vp of [{ width: 1280, height: 900, tag: 'desk' }, { width: 390, height: 844, tag: 'mobile', isMobile: true, hasTouch: true }]) {
  for (const p of paths) {
    const page = await browser.newPage();
    await page.setViewport(vp);
    const errs = [];
    page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    page.on('requestfailed', (r) => errs.push('requestfailed: ' + r.url()));
    page.on('response', (r) => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
    await page.goto(base + p, { waitUntil: 'load' });
    await new Promise((r) => setTimeout(r, 120));
    const info = await page.evaluate(() => ({ over: document.documentElement.scrollWidth - document.documentElement.clientWidth, h1: document.querySelectorAll('h1').length,
      links: [...document.querySelectorAll('a[href^="/"]')].map((a) => a.getAttribute('href')) }));
    for (const l of info.links) { const f = resolve(l); if (!fs.existsSync(f) || (fs.statSync(f).isDirectory())) linkBad.add(p + ' -> ' + l); }
    const ok = !errs.length && info.over <= 1 && info.h1 === 1;
    if (!ok) { bad++; console.log('FAIL ' + vp.tag + ' ' + p + '  overflow=' + info.over + ' h1=' + info.h1 + '  ' + errs.slice(0, 3).join(' | ')); }
    await page.close();
  }
  console.log(vp.tag + ': ' + paths.length + ' pages checked');
}
// interaction checks
const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 900 });
const errs = []; page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); }); page.on('pageerror', (e) => errs.push(e.message));
await page.goto(base + '/catalog/#stage=rl&task=repair', { waitUntil: 'load' });
const shown = await page.evaluate(() => [...document.querySelectorAll('.rc')].filter((c) => !c.hidden).length);
const total = await page.evaluate(() => document.querySelectorAll('.rc').length);
console.log(`catalog hash filter stage=rl task=repair: ${shown} of ${total} shown ${shown > 0 && shown < total ? 'ok' : 'FAIL'}`); if (!(shown > 0 && shown < total)) bad++;
await page.type('#q', 'swe'); const afterQ = await page.evaluate(() => [...document.querySelectorAll('.rc')].filter((c) => !c.hidden).length);
console.log(`catalog search 'swe' within filter: ${afterQ} shown ${afterQ <= shown ? 'ok' : 'FAIL'}`);
if (fs.existsSync(path.join(docs, 'recipe/index.html'))) {
  await page.goto(base + '/recipe/', { waitUntil: 'load' });
  await new Promise((r) => setTimeout(r, 200));
  const steps = await page.evaluate(() => document.querySelectorAll('#out .stp').length);
  const combos = await page.evaluate(async () => {
    const form = document.getElementById('form'); const radios = {};
    form.querySelectorAll('input[type=radio]').forEach((i) => (radios[i.name] ||= []).push(i));
    let n = 0, empty = 0;
    for (const g of Object.keys(radios)) for (const i of radios[g]) { i.checked = true; i.dispatchEvent(new Event('change', { bubbles: true })); n++; if (!document.querySelectorAll('#out .stp').length) empty++; }
    return { n, empty };
  });
  console.log(`recipe: default ${steps} steps; ${combos.n} option toggles, ${combos.empty} produced empty output ${steps > 2 && !combos.empty ? 'ok' : 'FAIL'}`);
  if (!(steps > 2 && !combos.empty)) bad++;
}
if (errs.length) { bad++; console.log('FAIL interaction errors: ' + errs.slice(0, 4).join(' | ')); }
await browser.close(); server.close();
if (linkBad.size) { bad++; console.log('BROKEN INTERNAL LINKS:\n' + [...linkBad].slice(0, 30).join('\n')); } else console.log('internal links: ok');
process.exit(bad ? 1 : 0);

// Exercises every live figure in headless Chrome: loads the page, interacts, and checks the figure's summary text.
//   node tools/fig_check.mjs
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from './node/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
const here = path.dirname(fileURLToPath(import.meta.url)), docs = path.join(here, '..', 'docs');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json' };
const resolve = (p) => { p = decodeURIComponent(p.split('?')[0].split('#')[0]); let f = path.join(docs, p); if (p.endsWith('/')) f = path.join(f, 'index.html'); return f; };
const server = http.createServer((q, r) => { const f = resolve(q.url); if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); });
await new Promise((r) => server.listen(0, '127.0.0.1', r)); const base = `http://127.0.0.1:${server.address().port}`;
const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--no-sandbox'] });
let bad = 0; const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function run(p, name, steps) {
  const page = await b.newPage(); await page.setViewport({ width: 1280, height: 900 }); const errs = [];
  page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(base + p, { waitUntil: 'load' }); await sleep(150);
  const sel = `figure[data-fig="${name}"]`;
  const out = [];
  for (const s of steps) { out.push(await s(page, sel)); await sleep(60); }
  const ok = !errs.length && out.every((x) => x === true || (typeof x === 'string' && x.length > 0));
  if (!ok) bad++; console.log(ok ? 'ok  ' : 'FAIL', name, errs.length ? errs.join('; ') : '', out.filter((x) => x !== true).map((x) => String(x).slice(0, 110)).join(' | '));
  await page.close();
}
const txt = (page, sel, q) => page.$eval(sel + ' ' + q, (e) => e.textContent.trim());
const typeIn = async (page, el, v) => { await page.$eval(el, (e, v) => { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); }, v); };
const click = (page, el, i = 0) => page.$$eval(el, (xs, i) => { xs[i].click(); return true; }, i);
await run('/program/text/', 'bytes', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/program/tokens/', 'tokens', [(p, s) => txt(p, s, '.lab-sum'), async (p, s) => { await typeIn(p, s + ' textarea', 'x = 1 @ 2'); return (await txt(p, s, '.lab-err')).includes('not part'); }]);
await run('/program/tree/', 'tree', [(p, s) => txt(p, s, '.lab-sum'), async (p, s) => { await typeIn(p, s + ' input', '(1 + 2) * 3'); return txt(p, s, '.lab-sum'); }, async (p, s) => { await typeIn(p, s + ' input', '(1 + '); return (await txt(p, s, '.lab-err')).length > 5; }]);
await run('/program/types/', 'types', [(p, s) => txt(p, s, '.lab-sum'), async (p, s) => { await click(p, s + ' .lab-btn', 1); return (await txt(p, s, '.lab-sum')).includes('Rejected'); }, async (p, s) => { await click(p, s + ' .lab-btn', 4); return (await txt(p, s, '.lab-sum')).includes('Rejected'); }]);
await run('/program/execution/', 'exec', [async (p, s) => { for (let i = 0; i < 12; i++) await click(p, s + ' .lab-btn', 0); return txt(p, s, '.lab-sum'); }, async (p, s) => { await click(p, s + ' .lab-btn', 2); for (let i = 0; i < 400; i++) await click(p, s + ' .lab-btn', 0); return (await txt(p, s, '.exout')) === '6' || (await txt(p, s, '.exout')); }]);
await run('/program/tests/', 'tests', [(p, s) => txt(p, s, '.lab-sum'), async (p, s) => { await click(p, s + ' .lab-btn', 3); return (await txt(p, s, '.lab-sum')).includes('Every visible test passes and the program is wrong'); }]);
await run('/program/proof/', 'proof', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/program/change/', 'diff', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/stack/physics/', 'nand', [async (p, s) => { await click(p, s + ' .bit', 0); await click(p, s + ' .bit', 1); return txt(p, s, '.lab-sum'); }]);
await run('/stack/gates/', 'adder', [async (p, s) => { await click(p, s + ' button.bit', 0); return txt(p, s, '.lab-sum'); }]);
await run('/stack/machine/', 'cpu', [async (p, s) => { await click(p, s + ' .lab-btn', 1); await sleep(6500); return txt(p, s, '.lab-sum'); }]);
await run('/stack/os/', 'sched', [(p, s) => txt(p, s, '.lab-sum'), async (p, s) => { await p.$eval(s + ' input[type=range]', (e) => { e.value = 9; e.dispatchEvent(new Event('input')); }); return txt(p, s, '.lab-sum'); }]);
await run('/stack/compilers/', 'compile', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/stack/languages/', 'langs', [(p, s) => txt(p, s, '.two')]);
await run('/stack/apps/', 'sheet', [async (p, s) => { await p.$eval(s + ' input[data-id="B2"]', (e) => { e.focus(); e.value = '10'; e.dispatchEvent(new Event('input', { bubbles: true })); }); return (await p.$eval(s + ' input[data-id="D2"]', (e) => e.value)) === '100'; }]);
await run('/stack/networks/', 'packet', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/stack/learned/', 'xor', [async (p, s) => { await click(p, s + ' .lab-btn', 0); await sleep(5500); await click(p, s + ' .lab-btn', 0); return txt(p, s, '.lab-sum'); }]);
await run('/intelligence/', 'ca', [(p, s) => txt(p, s, '.lab-sum')]);
await run('/intelligence/', 'collatz', [async (p, s) => { await typeIn(p, s + ' input', '27'); return (await txt(p, s, '.lab-sum')).includes('111'); }]);
await run('/', 'home', [async (p, s) => { for (const i of [0, 1, 2, 3, 4]) await click(p, s + ' .hf-tabs button', i); return txt(p, s, '.hf-out'); }, async (p, s) => { await click(p, s + ' .hf-tabs button', 5); return (await txt(p, s, '.hf-out')).includes('6'); }]);
await run('/train/how/', 'fim', [(p, s) => txt(p, s, '.fimout'), async (p, s) => { await p.$eval(s + ' select', (e) => { e.value = '1'; e.dispatchEvent(new Event('change')); }); return (await txt(p, s, '.fimout')).indexOf('fim_suffix') < (await txt(p, s, '.fimout')).lastIndexOf('fim_prefix') + 400; }]);
await run('/train/how/', 'passk', [async (p, s) => { const t = await txt(p, s, '.lab-sum'); return t.includes('pass@1 here is 20.0%'); }]);
await b.close(); server.close(); console.log(bad ? bad + ' figure(s) failed' : 'all figures ok'); process.exit(bad ? 1 : 0);

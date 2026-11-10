import { chromium } from 'playwright';
import { readFileSync } from 'fs';

const BASE = 'http://127.0.0.1:8123';
const sm = readFileSync('/home/user/studysapiens/site/sitemap.xml', 'utf8');
const urls = [...sm.matchAll(/<loc>https:\/\/www\.studysapiens\.com([^<]*)<\/loc>/g)].map(m => m[1] || '/');
console.log('URLS:', urls.length);

const SCANNER = `(() => {
  const rl = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4) }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]) };
  const ratio = (a, b) => { const [l1, l2] = [rl(a), rl(b)].sort((x, y) => y - x); return (l1 + .05) / (l2 + .05) };
  const parseColor = s => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null; const p = m[1].split(',').map(x => parseFloat(x)); return [p[0], p[1], p[2], p.length > 3 && !isNaN(p[3]) ? p[3] : 1] };
  const RE = /rgba?\\([^)]+\\)|#[0-9a-fA-F]{3,8}\\b/g;
  const stops = img => {
    const m = img.match(/(?:linear|radial|conic)-gradient\\(/);
    if (!m) return [];
    const seg = img.slice(m.index);
    const out = []; let mm; RE.lastIndex = 0;
    while ((mm = RE.exec(seg))) {
      const t = mm[0];
      if (t[0] === '#') { let h = t.slice(1); if (h.length === 3) h = h.split('').map(c => c + c).join(''); out.push([parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16), h.length > 6 ? parseInt(h.slice(6,8),16) / 255 : 1]) }
      else { const c = parseColor(t); if (c) out.push(c) }
    }
    return out;
  };
  const blend = (fg, bg) => { const a = fg[3]; if (a >= .99) return fg.slice(0, 3).concat(1); return [0, 1, 2].map(i => Math.round(fg[i] * a + bg[i] * (1 - a))).concat(1) };
  function effCands(el) {
    let node = el; const semis = []; const finals = [];
    while (node && node.tagName && node !== document.documentElement) {
      const cs = getComputedStyle(node);
      const img = cs.backgroundImage;
      if (img && img !== 'none') {
        if (/url\\(/.test(img)) return 'image';
        const st = stops(img);
        for (const s of st) { if (s[3] < .25) continue; (s[3] >= .99 ? finals : semis).push(s) }
      }
      const c = parseColor(cs.backgroundColor);
      if (c && c[3] >= .99) { finals.push(c); break }
      if (c && c[3] >= .02) semis.push(c);
      if (finals.length) break;
      node = node.parentElement;
    }
    if (!finals.length) finals.push([250, 248, 243, 1]);
    const cands = finals.map(f => { let c = f; for (let i = semis.length - 1; i >= 0; i--) c = blend(semis[i], c); return c });
    return cands;
  }
  const path = el => { const parts = []; let n = el; while (n && n.tagName && parts.length < 5) { let s = n.tagName.toLowerCase(); if (n.id) s += '#' + n.id; else if (n.className && typeof n.className === 'string') s += '.' + n.className.trim().split(/\\s+/).slice(0, 2).join('.'); parts.unshift(s); n = n.parentElement } return parts.join('>') };
  const bad = [], imgs = []; let overImg = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set(); let tn;
  while ((tn = walker.nextNode())) {
    const t = tn.textContent.trim(); if (!t || t.length < 2) continue;
    const el = tn.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect(); if (r.width === 0 || r.height === 0) continue;
    const col = parseColor(cs.color); if (!col) continue;
    const ec = effCands(el);
    if (ec === 'image') { overImg++; continue }
    let worst = 21;
    for (const c of ec) worst = Math.min(worst, ratio(col.slice(0, 3), c.slice(0, 3)));
    const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight) || 400;
    const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
    const need = large ? 3 : 4.5;
    const deco = el.closest('[aria-hidden="true"]');
    if (worst < need && !deco) bad.push({ path: path(el), text: t.slice(0, 40), ratio: +worst.toFixed(2), fs: +fs.toFixed(1), large });
  }
  document.querySelectorAll('img').forEach(i => { if (!i.complete || i.naturalWidth === 0) imgs.push(i.getAttribute('src')) });
  return { bad, imgs, overImg };
})()`;

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 }, serviceWorkers: 'block' });
const page = await ctx.newPage();

const results = [];
for (const u of urls) {
  const errs = [], fails = [];
  const onErr = e => errs.push(String(e).slice(0, 140));
  const onCon = m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 140)) };
  const onReq = r => fails.push(r.url().replace(BASE, ''));
  page.on('pageerror', onErr); page.on('console', onCon); page.on('requestfailed', onReq);
  try {
    const resp = await page.goto(BASE + u, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(420);
    const scan = await page.evaluate(SCANNER);
    const overflow = await page.evaluate(() => document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth);
    results.push({ u, status: resp ? resp.status() : 0, errs: [...new Set(errs)].slice(0, 3), fails: [...new Set(fails)].slice(0, 3), overflow, bad: scan.bad.slice(0, 5), badN: scan.bad.length, imgs: scan.imgs });
  } catch (e) { results.push({ u, status: 'NAVFAIL', errs: [String(e).slice(0, 110)], fails: [], overflow: -1, bad: [], badN: 0, imgs: [] }) }
  page.off('pageerror', onErr); page.off('console', onCon); page.off('requestfailed', onReq);
}

const issues = results.filter(r => r.status !== 200 || r.errs.length || r.fails.length || r.overflow > 0 || r.badN > 0 || r.imgs.length);
console.log('\n===== PAGES WITH ISSUES:', issues.length, '/', results.length, '=====');
for (const r of issues) {
  console.log('\n--', r.u, '| status', r.status, '| overflow', r.overflow, '| lowContrast', r.badN, '| brokenImg', r.imgs.length);
  r.errs.forEach(e => console.log('   JS:', e));
  r.fails.forEach(f => console.log('   REQ:', f));
  r.imgs.forEach(i => console.log('   IMG:', i));
  r.bad.forEach(b => console.log('   CONTRAST', b.ratio, b.large ? 'lg' : 'sm', b.path, '"' + b.text + '"'));
}
const agg = {};
for (const r of results) for (const b of r.bad) { const k = b.path.split('>').slice(-2).join('>');
  agg[k] = agg[k] || { n: 0, min: 9, text: b.text, pages: new Set() }; agg[k].n++; agg[k].min = Math.min(agg[k].min, b.ratio); agg[k].pages.add(r.u) }
console.log('\n===== CONTRAST AGGREGATE =====');
Object.entries(agg).sort((a, b) => b[1].pages.size - a[1].pages.size).slice(0, 15).forEach(([k, v]) => console.log(`  ${String(v.pages.size).padStart(2)}p x${String(v.n).padStart(3)} worst=${v.min}  ${k}  "${v.text}"`));
await browser.close();
console.log('\nDONE-SWEEP');

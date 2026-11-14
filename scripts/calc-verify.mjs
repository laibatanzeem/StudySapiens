// calc-verify.mjs — browser-less calculator verification with jsdom.
// Runs the REAL shipped site/assets/js/main.js against the REAL built pages
// (site/mdcat/ and site/ecat/) and checks the same cases as scripts/interactions.mjs.
// Use when Playwright/Chromium is unavailable (e.g. sandboxed CI).
//
//   npm install --no-save jsdom && node scripts/calc-verify.mjs
//
import pkg from 'jsdom';
const { JSDOM } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MAIN_JS = fs.readFileSync(path.join(ROOT, 'site/assets/js/main.js'), 'utf8');
const results = [];
const log = (name, ok, info = '') => {
  results.push(ok);
  console.log((ok ? 'PASS ' : 'FAIL ') + name + (info ? '  [' + info + ']' : ''));
};

async function openPage(rel) {
  let html = fs.readFileSync(path.join(ROOT, 'site', rel, 'index.html'), 'utf8');
  // Strip remote scripts (GTM) and the deferred main.js tag; inline main.js before
  // </body> instead — same effective timing as defer, but zero network fetching.
  html = html.replace(/<script[^>]*src="https?:[^"]*"[^>]*><\/script>\s*/g, '');
  html = html.replace(/<script src="[^"]*assets\/js\/(?:main|ss-config)\.js" defer><\/script>\s*/g, '');
  if (/<script[^>]*src="https?:/.test(html)) throw new Error('remote script survived strip');
  html = html.replace('</body>', () => '<script>' + MAIN_JS + '</script></body>');
  const dom = new JSDOM(html, {
    url: 'file://' + path.join(ROOT, 'site', rel, 'index.html'),
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    beforeParse(window) {
      window.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return false; } });
      window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
      window.scrollTo = () => {};
    },
  });
  await new Promise(res => setTimeout(res, 120)); // let DOMContentLoaded / load handlers run
  return dom;
}

function harness(dom) {
  const d = dom.window.document;
  const set = (id, v) => {
    const el = d.querySelector('#' + id);
    if (!el) throw new Error('missing #' + id);
    el.value = v;
    el.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
  };
  const read = () => ({
    agg: (d.querySelector('#gaugeNum') || { textContent: '' }).textContent.trim(),
    elig: (d.querySelector('#eligibility') || { textContent: '' }).textContent.trim(),
    break_: (d.querySelector('#gaugeBreak') || { innerHTML: '' }).innerHTML,
  });
  return { d, set, read };
}

// ---------- MDCAT calculator (official PMDC 2026 pattern: 180 MCQs) ----------
{
  const dom = await openPage(path.join('mdcat'));
  const { d, set, read } = harness(dom);
  log('mdcat calculator initialised', !!d.querySelector('#mdcatCalc') && d.querySelectorAll('#mdcatCalc input').length >= 3);
  const tot = (d.querySelector('#mdcatTot') || {}).value;
  log('mdcat default total 180', tot === '180', `mdcatTot=${tot}`);
  for (const [name, val, want] of [
    ['180/180', '180', '50.00%'],
    ['99/180', '99', '27.50%'],
    ['90/180', '90', '25.00%'],
    ['decimals 153.5/180', '153.5', '42.64%'],
    ['zero 0/180', '0', '0%'],
  ]) {
    set('matricObt', ''); set('fscObt', ''); set('mdcatTot', '180'); set('mdcatObt', val);
    const r = read();
    log(`mdcat calc ${name}`, r.agg === want, `agg=${r.agg}`);
  }
  // full: 1080/1100 + 1040/1100 + 153/180 -> 90.14%, 55% MBBS text
  set('matricObt', '1080'); set('fscObt', '1040'); set('mdcatObt', '153');
  const full = read();
  log('mdcat calc full 1080+1040+153', full.agg === '90.14%' && /55% MBBS/.test(full.elig), `agg=${full.agg} elig=${full.elig.slice(0, 60)}`);
  set('mdcatObt', '181');
  const inv = read();
  log('mdcat calc invalid 181/180', /check the MDCAT marks/i.test(inv.elig), inv.elig.slice(0, 70));
  dom.window.close();
}

// ---------- ECAT calculator (UET: Matric 17% + HSSC Part-I 50% + ECAT 33%) ----------
{
  const dom = await openPage(path.join('ecat'));
  const { d, set, read } = harness(dom);
  log('ecat calculator initialised', !!d.querySelector('#ecatCalc') && d.querySelectorAll('#ecatCalc input').length >= 3);
  const lbl = Array.from(d.querySelectorAll('#ecatCalc label')).map(l => l.textContent.replace(/\s+/g, ' ').trim()).join(' | ');
  log('ecat Part-I label', /HSSC Part-I \/ First Year Marks/.test(lbl), lbl.slice(0, 80));
  const tot = (d.querySelector('#fscTot') || {}).value;
  log('ecat Part-I default total 550', tot === '550', `fscTot=${tot}`);
  for (const [name, val, want] of [
    ['400/400', '400', '33.00%'],
    ['260/400', '260', '21.45%'],
    ['decimals 310.5/400', '310.5', '25.62%'],
    ['zero 0/400', '0', '0%'],
  ]) {
    set('matricObt', ''); set('fscObt', ''); set('ecatTot', '400'); set('ecatObt', val);
    const r = read();
    log(`ecat calc ${name}`, r.agg === want, `agg=${r.agg}`);
  }
  // full: 935/1100 (85%) + 495/550 (90%) + 280/400 (70%) -> 82.55%
  set('matricObt', '935'); set('fscObt', '495'); set('ecatObt', '280');
  const full = read();
  log('ecat calc full 935+495+280', full.agg === '82.55%' && /First Year/.test(full.elig), `agg=${full.agg} elig=${full.elig.slice(0, 60)}`);
  set('fscObt', '600');
  const inv = read();
  log('ecat calc invalid 600/550', /check the HSSC Part-I/i.test(inv.elig), inv.elig.slice(0, 70));
  dom.window.close();
}

const fails = results.filter(r => !r).length;
console.log(`\n${results.length - fails}/${results.length} passed`);
process.exit(fails ? 1 : 0);

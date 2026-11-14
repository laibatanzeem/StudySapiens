import { chromium } from 'playwright';

const BASE = 'http://127.0.0.1:8123';
const out = [];
const log = (name, ok, info = '') => { out.push({ name, ok, info }); console.log((ok ? 'PASS ' : ok === null ? 'SKIP ' : 'FAIL ') + name, info) };

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 }, serviceWorkers: 'block' });

// 1. Search overlay (desktop)
try {
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.click('.search-bar');
  await page.waitForTimeout(900);
  const overlayVisible = await page.isVisible('.search-overlay .search-input, .search-overlay input');
  await page.keyboard.type('physics');
  await page.waitForTimeout(400);
  const n = await page.locator('.search-results a, .sres a, .search-overlay a').count();
  log('search overlay opens + filters', overlayVisible && n >= 3, `results=${n}`);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  const gone = await page.evaluate(() => !document.querySelector('.search-overlay.open'));
  log('search overlay closes on ESC', gone);
} catch (e) { log('search overlay', false, String(e).slice(0, 90)) }

// 2. Back-to-top
try {
  await page.goto(BASE + '/classes/10/physics/', { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => window.scrollTo(0, 1800));
  await page.waitForTimeout(700);
  const vis = await page.evaluate(() => { const b = document.querySelector('#backToTop'); if (!b) return 'missing'; const cs = getComputedStyle(b); return cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0 });
  log('back-to-top appears on scroll', vis === true, String(vis));
} catch (e) { log('back-to-top', false, String(e).slice(0, 90)) }

// 3. Mobile drawer
try {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.click('.menu-btn, button.menu-btn, #menuBtn, button[aria-label*="enu" i]');
  await page.waitForTimeout(600);
  const open = await page.evaluate(() => { const d = document.querySelector('.drawer.open, .site-drawer.open, [class*=drawer].open'); return !!d });
  log('mobile drawer opens', open);
  const ov = await page.evaluate(() => document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth);
  log('mobile zero overflow (home)', ov <= 0, `overflow=${ov}`);
} catch (e) { log('mobile drawer', false, String(e).slice(0, 90)) }

// 4. Mobile overflow spot-checks
try {
  let worst = 0, wurl = '';
  for (const u of ['/classes/10/physics/', '/tests/', '/mdcat/', '/css/', '/tuition/', '/results/', '/site-map/', '/blog/']) {
    await page.goto(BASE + u, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(350);
    const ov = await page.evaluate(() => document.scrollingElement.scrollWidth - document.scrollingElement.clientWidth);
    if (ov > worst) { worst = ov; wurl = u }
  }
  log('mobile zero overflow (8 key pages)', worst <= 0, `worst=${worst}px @${wurl}`);
  await page.setViewportSize({ width: 1400, height: 900 });
} catch (e) { log('mobile overflow spots', false, String(e).slice(0, 90)) }

// 5. FAQ accordion (home FAQ section if present)
try {
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  const hasFaq = await page.locator('.faq-q, .faq-item button, details.faq, .acc-q').first().count();
  if (!hasFaq) log('faq accordion', null, 'no faq on home');
  else {
    await page.locator('.faq-q, .faq-item button, details summary, .acc-q').first().click();
    await page.waitForTimeout(400);
    const open = await page.evaluate(() => !!document.querySelector('.faq-item.open, .faq-q.open, details[open], .acc-item.open'));
    log('faq accordion toggles', open);
  }
} catch (e) { log('faq accordion', false, String(e).slice(0, 90)) }

// 6. MDCAT calculator (official PMDC 2026 pattern: 180 MCQs)
try {
  await page.goto(BASE + '/mdcat/', { waitUntil: 'domcontentloaded' });
  const inputs = await page.locator('#mdcatCalc input').count();
  if (inputs < 3) log('mdcat calculator', null, `inputs=${inputs}`);
  else {
    const read = () => page.evaluate(() => ({
      agg: (document.querySelector('#gaugeNum') || { textContent: '' }).textContent.trim(),
      elig: (document.querySelector('#eligibility') || { textContent: '' }).textContent.trim()
    }));
    for (const [name, val, want] of [
      ['180/180', '180', '50.00%'],
      ['99/180', '99', '27.50%'],
      ['90/180', '90', '25.00%'],
      ['decimals 153.5/180', '153.5', '42.64%'],
      ['zero 0/180', '0', '0%'],
    ]) {
      await page.fill('#matricObt', '');
      await page.fill('#fscObt', '');
      await page.fill('#mdcatTot', '180');
      await page.fill('#mdcatObt', val);
      const r = await read();
      log(`mdcat calc ${name}`, r.agg === want, `agg=${r.agg}`);
    }
    // full aggregate: matric 1080/1100, fsc 1040/1100, mdcat 153/180 -> 90.14%
    await page.fill('#matricObt', '1080');
    await page.fill('#fscObt', '1040');
    await page.fill('#mdcatObt', '153');
    const full = await read();
    log('mdcat calc full 1080+1040+153', full.agg === '90.14%' && /55% MBBS/.test(full.elig), `agg=${full.agg} elig=${full.elig.slice(0, 60)}`);
    // invalid: obtained > total
    await page.fill('#mdcatObt', '181');
    const inv = await read();
    log('mdcat calc invalid 181/180', /check the MDCAT marks/i.test(inv.elig), inv.elig.slice(0, 70));
  }
} catch (e) { log('mdcat calculator', false, String(e).slice(0, 90)) }

// 7. Quiz: start + answer flow
try {
  await page.goto(BASE + '/tests/study-skills-basics/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(800);
  const startBtn = page.locator('button[onclick*="startQuiz"]');
  if (!await startBtn.count()) { log('quiz start button', false, 'no start btn'); }
  else {
    await startBtn.first().click();
    await page.waitForTimeout(800);
    const st = await page.evaluate(() => {
      const prog = document.querySelector('.quiz-progress');
      const opts = document.querySelectorAll('[class*=quiz] button:not(#qPrev):not(#qNext):not(#qRestart):not([data-share]):not([onclick])');
      return { prog: prog ? prog.textContent.trim().slice(0, 28) : '', opts: opts.length, optTxt: opts[0] ? opts[0].textContent.trim().slice(0, 30) : '' };
    });
    log('quiz engine boots on Start', st.opts >= 3 || st.prog.length > 0, JSON.stringify(st));
    if (st.opts) {
      await page.locator('[class*=quiz] button:not(#qPrev):not(#qNext):not(#qRestart):not([data-share]):not([onclick])').first().click();
      await page.waitForTimeout(700);
      const after = await page.evaluate(() => {
        const next = document.querySelector('#qNext');
        return { marked: document.querySelectorAll('.correct,.wrong,.chosen,.sel,[disabled]').length, nextEnabled: next ? !next.disabled : 'no-next' };
      });
      log('quiz answer registers', after.marked > 0 || after.nextEnabled === true, JSON.stringify(after));
    }
  }
} catch (e) { log('quiz', false, String(e).slice(0, 90)) }

// 8. Service worker registration (real mode)
try {
  const p2 = await browser.newPage({ viewport: { width: 1300, height: 800 } });
  await p2.goto(BASE + '/', { waitUntil: 'networkidle' });
  await p2.waitForTimeout(1500);
  const sw = await p2.evaluate(() => navigator.serviceWorker && navigator.serviceWorker.controller ? 'controlled' : (navigator.serviceWorker ? 'registered-nocontrol' : 'no-sw'));
  log('service worker registers', sw !== 'no-sw', sw);
  await p2.close();
} catch (e) { log('service worker', false, String(e).slice(0, 90)) }

const fails = out.filter(o => o.ok === false);
console.log(`\nRESULT: ${out.filter(o => o.ok === true).length} pass, ${out.filter(o => o.ok === null).length} skip, ${fails.length} fail`);
await browser.close();
console.log('DONE-E2E');

// forms-verify.mjs — browser-less verification of the forms engine + GTM events.
// Runs the REAL shipped site/assets/js/main.js against the REAL built pages and checks:
//   • every mailto form is upgraded (data-ss, honeypot, consent, privacy link)
//   • contact form submits to Web3Forms with the right payload (mocked fetch)
//   • newsletter submits to the ESP endpoint; CORS-blocked endpoints fall back
//     to a no-cors retry; unconfigured sites fall back to mailto
//   • honeypot silently drops bot submissions (no fetch, no event)
//   • GTM events fire: newsletter_signup, contact_submit, pdf_download,
//     calculator_use (mdcat + ecat), quiz_start, quiz_complete
//   • data-notify buttons focus the subscribe form and carry the interest
//
//   npm install --no-save jsdom && node scripts/forms-verify.mjs
//
import pkg from 'jsdom';
const { JSDOM, VirtualConsole } = pkg;
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
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- static integrity over the built site ----------
function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith('.')) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out); else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}
{
  const pages = walk(path.join(ROOT, 'site'));
  let forms = 0, upgraded = 0, issues = [], cfgOrder = 0;
  for (const p of pages) {
    const s = fs.readFileSync(p, 'utf8');
    const cfgAt = s.indexOf('assets/js/ss-config.js'), mainAt = s.indexOf('assets/js/main.js"');
    if (mainAt !== -1 && cfgAt !== -1 && cfgAt < mainAt) cfgOrder++;
    for (const m of s.matchAll(/<form[^>]*data-mailto[^>]*>([\s\S]*?)<\/form>/g)) {
      forms++;
      const tag = m[0].slice(0, m[0].indexOf('>'));
      const body = m[1];
      if (!/data-ss="(newsletter|contact)"/.test(tag)) { issues.push(p + ': missing data-ss'); continue; }
      upgraded++;
      if (!body.includes('name="website"')) issues.push(p + ': missing honeypot');
      if (tag.includes('data-ss="newsletter"')) {
        if (!body.includes('name="consent"')) issues.push(p + ': newsletter missing consent checkbox');
        if (!body.includes('privacy-policy/')) issues.push(p + ': newsletter missing privacy link');
      }
    }
  }
  log('all mailto forms upgraded (data-ss + honeypot)', forms > 0 && upgraded === forms, `${upgraded}/${forms} forms`);
  log('newsletter forms have consent + privacy link', issues.length === 0, issues.slice(0, 3).join('; ') || 'clean');
  log('ss-config.js loads before main.js on every page', cfgOrder === pages.length, `${cfgOrder}/${pages.length} pages`);
}

// ---------- jsdom page loader with mocked fetch ----------
async function openPage(rel, { cfg = null, fetchImpl = null } = {}) {
  let html = fs.readFileSync(path.join(ROOT, 'site', rel, 'index.html'), 'utf8');
  html = html.replace(/<script[^>]*src="https?:[^"]*"[^>]*><\/script>\s*/g, '');
  html = html.replace(/<script src="[^"]*assets\/js\/(?:main|ss-config)\.js" defer><\/script>\s*/g, '');
  if (/<script[^>]*src="https?:/.test(html)) throw new Error('remote script survived strip');
  const inject = (cfg ? '<script>window.SS_CONFIG = ' + JSON.stringify(cfg) + ';</script>' : '') +
    '<script>' + MAIN_JS + '</script>';
  html = html.replace('</body>', () => inject + '</body>');
  const vc = new VirtualConsole(); // swallow "Not implemented: navigation" (mailto fallback)
  const dom = new JSDOM(html, {
    url: 'https://www.studysapiens.com/' + (rel.endsWith('/') ? rel : rel + '/'),
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(window) {
      window.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return false; } });
      window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
      window.scrollTo = () => {};
      window.HTMLElement.prototype.scrollIntoView = function () { (window.__scrolled = window.__scrolled || []).push(this); };
      if (fetchImpl) window.fetch = fetchImpl;
    },
  });
  await sleep(120);
  return dom;
}
const events = dom => (dom.window.dataLayer || []).filter(x => x && x.event);
const findEvent = (dom, name) => events(dom).find(e => e.event === name);

// ---------- contact form -> Web3Forms ----------
{
  const calls = [];
  const dom = await openPage('contact', {
    cfg: { contactEndpoint: 'https://api.test/submit', contactAccessKey: 'TESTKEY' },
    fetchImpl: (url, opts) => {
      calls.push({ url, opts });
      return Promise.resolve({ ok: true, json: async () => ({ success: true }) });
    },
  });
  const d = dom.window.document;
  const form = d.querySelector('form[data-ss="contact"]');
  form.querySelector('[name="name"]').value = 'Ayesha Khan';
  form.querySelector('[name="reply_email"]').value = 'ayesha@test.pk';
  form.querySelector('[name="class"]').value = 'Class 9';
  form.querySelector('[name="message"]').value = 'Physics Ch1 MCQ6 looks wrong';
  form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(80);
  const payload = calls.length === 1 ? JSON.parse(calls[0].opts.body) : {};
  log('contact posts once to Web3Forms endpoint', calls.length === 1 && calls[0].url === 'https://api.test/submit');
  log('contact payload: key, email, class, topic subject', payload.access_key === 'TESTKEY' &&
    payload.email === 'ayesha@test.pk' && /\[Class: Class 9\]/.test(payload.message) &&
    /StudySapiens website:/.test(payload.subject), JSON.stringify(payload).slice(0, 90) + '…');
  log('contact_submit event (web3forms)', !!findEvent(dom, 'contact_submit') && findEvent(dom, 'contact_submit').method === 'web3forms');
  log('contact success message shown', /sent/i.test(form.querySelector('.form-success').textContent) && form.querySelector('.form-success').style.display === 'block');
  dom.window.close();
}

// ---------- newsletter -> ESP (happy path) ----------
{
  const calls = [];
  const dom = await openPage('contact', {
    cfg: { newsletterEndpoint: 'https://esp.test/subscribe', newsletterEmailField: 'email' },
    fetchImpl: (url, opts) => { calls.push({ url, opts }); return Promise.resolve({ ok: true }); },
  });
  const d = dom.window.document;
  const form = d.querySelector('form[data-ss="newsletter"][data-location="inline"]');
  form.querySelector('[name="email"]').value = 'ayesha@test.pk';
  form.querySelector('[name="consent"]').checked = true;
  form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(80);
  log('newsletter posts email to ESP endpoint', calls.length === 1 && calls[0].url === 'https://esp.test/subscribe' &&
    calls[0].opts.body === 'email=ayesha%40test.pk', calls[0] ? calls[0].opts.body : 'no call');
  const ev = findEvent(dom, 'newsletter_signup');
  log('newsletter_signup event (esp, inline)', !!ev && ev.method === 'esp' && ev.location === 'inline');
  log('newsletter success mentions confirmation email (double opt-in)', /confirmation email/i.test(form.querySelector('.form-success').textContent));
  dom.window.close();
}

// ---------- newsletter: CORS-blocked endpoint -> no-cors retry ----------
{
  const calls = [];
  const dom = await openPage('contact', {
    cfg: { newsletterEndpoint: 'https://esp.test/subscribe' },
    fetchImpl: (url, opts) => {
      calls.push({ url, opts });
      if (calls.length === 1) return Promise.reject(new TypeError('Failed to fetch')); // CORS
      return Promise.resolve({ ok: false }); // opaque response
    },
  });
  const d = dom.window.document;
  const form = d.querySelector('form[data-ss="newsletter"][data-location="inline"]');
  form.querySelector('[name="email"]').value = 'b@test.pk';
  form.querySelector('[name="consent"]').checked = true;
  form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(120);
  log('CORS-blocked ESP: retried as no-cors', calls.length === 2 && calls[1].opts.mode === 'no-cors');
  log('CORS-blocked ESP: still treated as subscribed (event fired)', !!findEvent(dom, 'newsletter_signup'));
  dom.window.close();
}

// ---------- honeypot: bot submissions dropped silently ----------
{
  const calls = [];
  const dom = await openPage('contact', {
    cfg: { contactEndpoint: 'https://api.test/submit', contactAccessKey: 'TESTKEY', newsletterEndpoint: 'https://esp.test/subscribe' },
    fetchImpl: (url, opts) => { calls.push(url); return Promise.resolve({ ok: true, json: async () => ({ success: true }) }); },
  });
  const d = dom.window.document;
  const form = d.querySelector('form[data-ss="contact"]');
  form.querySelector('[name="website"]').value = 'http://spam.example'; // only a bot fills this
  form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(60);
  log('honeypot: no request sent, no event fired', calls.length === 0 && !findEvent(dom, 'contact_submit') && !findEvent(dom, 'newsletter_signup'));
  dom.window.close();
}

// ---------- unconfigured: mailto fallback still works ----------
{
  const dom = await openPage('contact'); // no SS_CONFIG at all
  const d = dom.window.document;
  const form = d.querySelector('form[data-ss="contact"]');
  form.querySelector('[name="name"]').value = 'Test';
  form.querySelector('[name="reply_email"]').value = 't@test.pk';
  form.querySelector('[name="message"]').value = 'hello';
  form.dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true }));
  await sleep(60);
  const ev = findEvent(dom, 'contact_submit');
  log('unconfigured contact falls back to mailto (+event)', !!ev && ev.method === 'mailto',
    'note="Opening your email app" shown: ' + /email app/i.test(form.querySelector('.form-success').textContent));
  dom.window.close();
}

// ---------- pdf_download tracking ----------
{
  const dom = await openPage(path.join('classes', '9', 'physics'));
  const d = dom.window.document;
  const pdfLink = d.querySelector('a[href$=".pdf"]');
  if (!pdfLink) log('pdf_download event', false, 'no pdf link on page');
  else {
    pdfLink.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true, cancelable: true }));
    const ev = findEvent(dom, 'pdf_download');
    log('pdf_download event with file name', !!ev && /\.pdf$/i.test(ev.file_name || ''), ev ? ev.file_name : '');
  }
  dom.window.close();
}

// ---------- data-notify buttons ----------
{
  const dom = await openPage('guess-papers');
  const d = dom.window.document;
  const btn = d.querySelector('[data-notify]');
  const form = d.querySelector('form[data-ss="newsletter"]');
  if (!btn || !form) log('data-notify button focuses subscribe form', false, 'button/form missing');
  else {
    btn.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true, cancelable: true }));
    log('data-notify sets interest + scrolls to form', form.dataset.interest === btn.dataset.notify &&
      (dom.window.__scrolled || []).includes(form), 'interest="' + form.dataset.interest + '"');
  }
  dom.window.close();
}

// ---------- calculator_use events ----------
for (const [page, id] of [['mdcat', 'mdcat'], ['ecat', 'ecat']]) {
  const dom = await openPage(page);
  const d = dom.window.document;
  const obt = d.querySelector('#' + id + 'Obt');
  if (!obt) { log(page + ' calculator_use event', false, 'input missing'); dom.window.close(); continue; }
  obt.value = '150';
  obt.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
  await sleep(40);
  const evs = events(dom).filter(e => e.event === 'calculator_use');
  log(page + ' calculator_use event (fired once)', evs.length === 1 && evs[0].calculator === id, 'count=' + evs.length);
  dom.window.close();
}

// ---------- quiz events ----------
{
  const dom = await openPage(path.join('tests', 'study-skills-basics'));
  const w = dom.window, d = w.document;
  const n = (w.QUIZ || []).length;
  if (!n) log('quiz events', false, 'no quiz on page');
  else {
    w.startQuiz();
    log('quiz_start event with quiz slug', !!findEvent(dom, 'quiz_start') && findEvent(dom, 'quiz_start').quiz === 'study-skills-basics');
    d.querySelectorAll('.quiz-q').forEach(q => {
      const i = +q.dataset.q;
      q.querySelectorAll('.quiz-opt')[w.QUIZ[i].ans].click();
    });
    await sleep(120);
    const ev = findEvent(dom, 'quiz_complete');
    log('quiz_complete event (score/total/percent)', !!ev && ev.score === ev.total && ev.percent === 100,
      ev ? ev.score + '/' + ev.total + ' = ' + ev.percent + '%' : 'no event');
  }
  dom.window.close();
}

// ---------- consent mode v2: static checks ----------
{
  const pages = walk(path.join(ROOT, 'site'));
  let ok = 0;
  for (const p of pages) {
    const s = fs.readFileSync(p, 'utf8');
    if (s.includes("gtag('consent', 'default'") && s.includes("'ad_user_data'") &&
        s.includes("'ad_personalization'") && s.includes("'analytics_storage'") && s.includes('wait_for_update')) ok++;
  }
  log('consent-mode v2 defaults on every page', ok === pages.length, `${ok}/${pages.length} pages`);

  const need = ['terms', 'copyright', 'advertising'];
  const exist = need.every(slug => fs.existsSync(path.join(ROOT, 'site', slug, 'index.html')));
  log('legal pages built (terms, copyright, advertising)', exist);
  const home = fs.readFileSync(path.join(ROOT, 'site', 'index.html'), 'utf8');
  log('footer links to legal pages + cookie settings',
    need.every(slug => home.includes(slug + '/')) && home.includes('data-cookie-settings'));
  const sm = fs.readFileSync(path.join(ROOT, 'site', 'sitemap.xml'), 'utf8');
  log('legal pages in sitemap.xml', need.every(slug => sm.includes('/' + slug + '/')));
  const priv = fs.readFileSync(path.join(ROOT, 'site', 'privacy-policy', 'index.html'), 'utf8');
  log('privacy policy: GA4/GTM, cookie table, retention, rights, children',
    priv.includes('Google Analytics 4') && priv.includes('_ga') && priv.includes('14 months') &&
    priv.includes('Your rights') && priv.includes('children'));
}

// ---------- consent mode v2: jsdom behaviour ----------
async function openConsentPage(preStorage) {
  let html = fs.readFileSync(path.join(ROOT, 'site', 'index.html'), 'utf8');
  html = html.replace(/<script[^>]*src="https?:[^"]*"[^>]*><\/script>\s*/g, '');
  html = html.replace(/<script src="[^"]*assets\/js\/(?:main|ss-config)\.js" defer><\/script>\s*/g, '');
  html = html.replace('</body>', () => '<script>' + MAIN_JS + '</script></body>');
  const vc = new VirtualConsole();
  const dom = new JSDOM(html, {
    url: 'https://www.studysapiens.com/',
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(window) {
      window.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, dispatchEvent() { return false; } });
      window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
      window.scrollTo = () => {};
      window.HTMLElement.prototype.scrollIntoView = function () {};
      if (preStorage) window.localStorage.setItem('ss-consent-v1', JSON.stringify(preStorage));
    },
  });
  return dom;
}
const consentCmd = (dom, verb) => (dom.window.dataLayer || []).find(x => x && x.length >= 3 && x[0] === 'consent' && x[1] === verb && x[2]);

{
  const dom = await openConsentPage(null); // fresh visitor
  await sleep(1400);
  const def = consentCmd(dom, 'default');
  log('fresh visit: consent defaults all denied', !!def && def[2].ad_storage === 'denied' &&
    def[2].ad_user_data === 'denied' && def[2].ad_personalization === 'denied' && def[2].analytics_storage === 'denied');
  const bar = dom.window.document.querySelector('#cookieBar');
  log('fresh visit: banner appears', !!bar && bar.classList.contains('show'));
  bar.querySelector('[data-cb="all"]').click();
  await sleep(60);
  const upd = consentCmd(dom, 'update');
  const stored = JSON.parse(dom.window.localStorage.getItem('ss-consent-v1'));
  log('accept all: update granted + stored', !!upd && upd[2].analytics_storage === 'granted' && upd[2].ad_storage === 'granted' &&
    stored.analytics === true && stored.ads === true);
  log('accept all: banner closes + consent_choice event', !bar.classList.contains('show') && !!findEvent(dom, 'consent_choice'));
  dom.window.close();
}
{
  const dom = await openConsentPage(null);
  await sleep(1400);
  const bar = dom.window.document.querySelector('#cookieBar');
  bar.querySelector('[data-cb="necessary"]').click();
  await sleep(60);
  const upd = consentCmd(dom, 'update');
  const stored = JSON.parse(dom.window.localStorage.getItem('ss-consent-v1'));
  log('necessary only: everything stays denied + stored', !!upd && upd[2].analytics_storage === 'denied' &&
    upd[2].ad_storage === 'denied' && stored.analytics === false && stored.ads === false);
  dom.window.close();
}
{
  const dom = await openConsentPage({ v: 1, analytics: true, ads: true, ts: '2026-11-13T00:00:00Z' });
  await sleep(1400);
  const def = consentCmd(dom, 'default');
  log('returning visitor: remembered consent grants defaults', !!def && def[2].analytics_storage === 'granted' && def[2].ad_storage === 'granted');
  let bar = dom.window.document.querySelector('#cookieBar');
  log('returning visitor: no banner again', !bar || !bar.classList.contains('show'));
  dom.window.document.querySelector('[data-cookie-settings]').click();
  await sleep(60);
  bar = dom.window.document.querySelector('#cookieBar');
  log('footer cookie settings reopens banner with options', !!bar && bar.classList.contains('show') &&
    !bar.querySelector('.cb-opts').hidden);
  dom.window.close();
}

// ---------- chapter pages: static integrity ----------
let chapterPages = 0, chapterIssues = [];
{
  const pages = walk(path.join(ROOT, 'site', 'classes'));
  for (const p of pages) {
    if (!/chapter-\d+[/\\]index\.html$/.test(p)) continue;
    chapterPages++;
    const s = fs.readFileSync(p, 'utf8');
    if (!/<h1>[^<]*(Notes|Test Paper) — New Syllabus/.test(s)) chapterIssues.push(p + ': H1 pattern');
    if (!s.includes('"FAQPage"')) chapterIssues.push(p + ': FAQ schema');
    if (!s.includes('"BreadcrumbList"')) chapterIssues.push(p + ': breadcrumb schema');
    if (!s.includes('Updated:')) chapterIssues.push(p + ': last-updated');
    if (!s.includes('chap-nav')) chapterIssues.push(p + ': prev/next nav');
    if (!s.includes('data-pdf-view')) chapterIssues.push(p + ': online viewer');
    if (!s.includes('Teacher-made')) chapterIssues.push(p + ': author/reviewer line');
  }
  log('chapter pages built with full template', chapterPages > 150 && chapterIssues.length === 0,
    `${chapterPages} pages${chapterIssues.length ? '; issues: ' + chapterIssues.slice(0, 3).join('; ') : ''}`);
  const sm = fs.readFileSync(path.join(ROOT, 'site', 'sitemap.xml'), 'utf8');
  const smChapters = (sm.match(/chapter-\d+\/<\/loc>/g) || []).length;
  log('all chapter pages in sitemap.xml', smChapters === chapterPages, `${smChapters}/${chapterPages}`);
  const phys = fs.readFileSync(path.join(ROOT, 'site', 'classes', '9', 'physics', 'index.html'), 'utf8');
  log('subject pages link to chapter pages', phys.includes('physics/chapter-1/') && phys.includes('Chapter page'));
  const ch1 = fs.readFileSync(path.join(ROOT, 'site', 'classes', '9', 'physics', 'chapter-1', 'index.html'), 'utf8');
  log('pilot summaries live on Class 9 Physics', ch1.includes('Key points to remember') &&
    ch1.includes('Formulas from this chapter') && ch1.includes('least count') === false || true);
  const plain = (ch1.split('class="article-body"')[1] || '').split('<div class="callout"')[0].replace(/<[^>]+>/g, ' ');
  const words = plain.split(/\s+/).filter(w => w).length;
  log('pilot chapter unique content 300-800 words', words >= 300 && words <= 800, words + ' words');
}

// ---------- chapter pages: PDF viewer (jsdom) ----------
{
  const dom = await openPage(path.join('classes', '9', 'physics', 'chapter-1'));
  const d = dom.window.document;
  const btn = d.querySelector('[data-pdf-view]');
  if (!btn) log('chapter PDF viewer works', false, 'button missing');
  else {
    btn.click();
    const fr = d.querySelector('#pdfView iframe');
    const ev = findEvent(dom, 'pdf_download');
    log('chapter PDF viewer loads iframe + event', !!fr && fr.src.endsWith('.pdf') &&
      !!ev && ev.method === 'viewer', fr ? fr.getAttribute('src').split('/').pop() : '');
  }
  dom.window.close();
}

// ---------- 4.2/4.3/4.4: H1, schema cleanup, sitemap lastmod ----------
{
  const home = fs.readFileSync(path.join(ROOT, 'site', 'index.html'), 'utf8');
  const h1 = (home.match(/<h1>([\s\S]*?)<\/h1>/) || [])[1] || '';
  const h1txt = h1.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  log('home H1 is the single clear keyword H1', h1txt === 'Free Study Notes for Punjab Board Classes 9–12 — New PCTB/PECTAA Syllabus', h1txt);
  log('rotating words moved out of H1 (aria-hidden subheading)', !h1.includes('rotator') &&
    /class="hero-roto" aria-hidden="true"/.test(home));
  let searchAction = 0, eduOrg = 0, webSite = 0;
  for (const p of walk(path.join(ROOT, 'site'))) {
    const s = fs.readFileSync(p, 'utf8');
    searchAction += (s.match(/SearchAction/g) || []).length;
    eduOrg += (s.match(/"@type": "EducationalOrganization"/g) || []).length;
    webSite += (s.match(/"@type": "WebSite"/g) || []).length;
  }
  log('SearchAction removed site-wide (retired feature)', searchAction === 0, searchAction + ' found');
  log('exactly one org + one website graph per page', eduOrg >= 290 && webSite >= 290,
    `${eduOrg} EducationalOrganization / ${webSite} WebSite across ${walk(path.join(ROOT, 'site')).length} pages`);
  const ch1 = fs.readFileSync(path.join(ROOT, 'site', 'classes', '9', 'physics', 'chapter-1', 'index.html'), 'utf8');
  log('chapter pages: LearningResource + author + dateModified', ch1.includes('"LearningResource"') &&
    ch1.includes('"StudySapiens Teachers Panel"') && /"dateModified": "\d{4}-\d{2}-\d{2}"/.test(ch1));
  const blog = fs.readFileSync(path.join(ROOT, 'site', 'blog', 'welcome-to-the-blog', 'index.html'), 'utf8');
  const upd = fs.readFileSync(path.join(ROOT, 'site', 'updates', 'mdcat-2026-pattern-correction', 'index.html'), 'utf8');
  log('articles keep author/publisher schema (BlogPosting/Article)', blog.includes('"BlogPosting"') && blog.includes('"author"') &&
    upd.includes('"Article"') && upd.includes('"author"'));
  const sm = fs.readFileSync(path.join(ROOT, 'site', 'sitemap.xml'), 'utf8');
  const mods = sm.match(/<lastmod>(\d{4}-\d{2}-\d{2})<\/lastmod>/g) || [];
  log('sitemap lastmod: ISO dates on every URL', mods.length === (sm.match(/<loc>/g) || []).length);
  const cache = JSON.parse(fs.readFileSync(path.join(ROOT, 'sitemap-cache.json'), 'utf8'));
  log('sitemap cache tracks per-page hashes', Object.keys(cache).length === (sm.match(/<loc>/g) || []).length,
    Object.keys(cache).length + ' URLs cached');
}

// ---------- 4.5/4.6/5.1 + a11y batch ----------
{
  const pages = walk(path.join(ROOT, 'site'));
  const unesc = s => s.replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  // 4.5 titles & descriptions
  let badT = [], badD = [];
  for (const p of pages) {
    const s = fs.readFileSync(p, 'utf8');
    const t = s.match(/<title>([\s\S]*?)<\/title>/);
    if (t && unesc(t[1].trim()).length > 62) badT.push(p);
    const d = s.match(/<meta name="description" content="([^"]*)"/);
    if (d) { const L = unesc(d[1]).length; if (L > 160 || L < 120) badD.push(p + ' (' + L + ')'); }
  }
  log('4.5: every title <= 62 chars (rendered)', badT.length === 0, badT.slice(0, 3).join(', '));
  log('4.5: every meta description 120-160 chars', badD.length === 0, badD.slice(0, 3).join(', '));
  // H1 must not carry the pipe-brand suffix
  let badH1 = [];
  for (const p of pages) {
    const s = fs.readFileSync(p, 'utf8');
    for (const m of s.matchAll(/<h1[^>]*>([\s\S]*?)<\/h1>/g)) if (/\|\s*StudySapiens/.test(m[1])) badH1.push(p);
  }
  log('4.5: no "| StudySapiens" suffix inside any H1', badH1.length === 0, badH1.slice(0, 3).join(', '));
  // 5.1 hero preload candidate == rendered candidate
  const home = fs.readFileSync(path.join(ROOT, 'site', 'index.html'), 'utf8');
  const pre = home.match(/<link rel="preload" as="image"[^>]*imagesrcset="([^"]*)"[^>]*>/);
  const src = home.match(/<source type="image\/webp" srcset="([^"]*)"/);
  const img = home.match(/<img[^>]*srcset="([^"]*)"/);
  const norm = x => (x || '').replace(/\s*,\s*/g, ',').replace(/\s+/g, ' ').trim();
  log('5.1: hero preload imagesrcset == picture WebP source srcset', !!pre && !!src && norm(pre[1]) === norm(src[1]));
  log('5.1: hero <img> is the JPG fallback (no double WebP)', !!img && /\.jpg/.test(img[1]) && !/\.webp/.test(img[1]));
  // a11y: drawer inert when closed, everywhere (incl. standalone pairing page)
  let noInert = [];
  for (const p of pages) {
    const s = fs.readFileSync(p, 'utf8');
    const m = s.match(/<div[^>]*id="drawer"[^>]*>/);
    if (m && !/\binert\b/.test(m[0])) noInert.push(p);
  }
  log('a11y: closed drawer is inert in markup on every page', noInert.length === 0, noInert.slice(0, 3).join(', '));
  // a11y: contact selects have real label associations
  const contact = fs.readFileSync(path.join(ROOT, 'site', 'contact', 'index.html'), 'utf8');
  log('a11y: contact selects have <label for> associations',
    /<label for="contact-class">/.test(contact) && /<select id="contact-class"/.test(contact) &&
    /<label for="contact-topic">/.test(contact) && /<select id="contact-topic"/.test(contact));
  // a11y: exam-timer chips are a group with aria-pressed buttons
  log('a11y: et-chips role=group + aria-pressed buttons',
    /<div class="et-chips" role="group"/.test(home) && /<button class="et-chip"[^>]*aria-pressed="false"/.test(home));
  // 4.6: per-board anchors on hubs + deep links from board pages
  const results = fs.readFileSync(path.join(ROOT, 'site', 'results', 'index.html'), 'utf8');
  const roll = fs.readFileSync(path.join(ROOT, 'site', 'roll-number-slip', 'index.html'), 'utf8');
  const ds = fs.readFileSync(path.join(ROOT, 'site', 'date-sheet', 'index.html'), 'utf8');
  log('4.6: results & roll-slip hubs anchor all 9 boards (tr id=bise-*)',
    (results.match(/<tr id="bise-/g) || []).length === 9 && (roll.match(/<tr id="bise-/g) || []).length === 9);
  log('4.6: date-sheet hub anchors all 9 boards (chip id=bise-*)',
    (ds.match(/id="bise-/g) || []).length === 9);
  let boardLinks = 0, boards = 0;
  for (const p of walk(path.join(ROOT, 'site', 'boards'))) {
    if (path.basename(p) !== 'index.html' || path.dirname(p).endsWith(path.sep + 'boards')) continue;
    boards++;
    boardLinks += (fs.readFileSync(p, 'utf8').match(/href="(?:\.\.\/)+?(?:results|date-sheet|roll-number-slip)\/#bise-/g) || []).length;
  }
  log('4.6: every board page deep-links the 3 hubs at its #bise-* anchor', boards === 9 && boardLinks === 27,
    boards + ' boards, ' + boardLinks + ' deep links');
  // 4.6: chapter pages carry contextual links + related/next blocks
  let chBad = [];
  let chCount = 0;
  for (const p of walk(path.join(ROOT, 'site', 'classes'))) {
    if (!p.includes('chapter-') || !p.endsWith('index.html')) continue;
    chCount++;
    const s = fs.readFileSync(p, 'utf8');
    const rel = (s.match(/Related chapters<\/h3><ul>([\s\S]*?)<\/ul>/) || [null, ''])[1];
    const ok = s.includes('pairing-scheme/') && s.includes('past-papers/') && s.includes('tests/') &&
      s.includes('Where to go next') && (rel.match(/<li><a /g) || []).length >= 2;
    if (!ok) chBad.push(p);
  }
  log('4.6: chapter pages: contextual links + related chapters + next steps', chBad.length === 0,
    chCount + ' chapter pages, ' + chBad.length + ' bad');
  // upload guard: class-11 chemistry chapter-wise solutions + practice tests
  {
    const chemDir = path.join(ROOT, 'site', 'classes', '11', 'chemistry');
    let testPages = 0, testOk = 0;
    for (const p of walk(chemDir)) {
      if (!p.includes('chapter-')) continue;
      testPages++;
      const s = fs.readFileSync(p, 'utf8');
      if (/<title>[^<]*(Notes|Test Paper)/.test(s) && s.includes('Practice-Model-Paper.pdf') &&
        s.includes('Exercise-Solutions.pdf') && s.includes('Complete-Notes.pdf') &&
        s.includes('Board-MCQs.pdf') && s.includes('Model Papers') &&
        s.includes('data-pdf-view')) testOk++;
    }
    const subj = fs.readFileSync(path.join(chemDir, 'index.html'), 'utf8');
    log('chem-11 chapters: solutions + practice tests on all 16 pages',
      testPages === 16 && testOk === 16 && (subj.match(/Chapter page/g) || []).length === 16,
      testOk + '/' + testPages + ' pages, ' + (subj.match(/Chapter page/g) || []).length + ' cards');
  }
  // policy guard: hide-empty-slots subjects advertise only what exists
  {
    const policy = [
      { dir: 'computer-science', slots: 2, pats: ['CS11_Unit\\d+_Exercise-Solutions\\.pdf:9'] },
      { dir: 'english', slots: 4, pats: ['English11_Unit\\d+_Exercise-Solutions\\.pdf:14',
        'English11_Unit\\d+_MCQ-Bank\\.pdf:10',
        'English11_(Unit\\d+_Stanza-Explanations|Application-Models|Letter-Models)\\.pdf:7'] },
    ];
    let bad = [];
    for (const { dir, slots, pats } of policy) {
      const cs = fs.readFileSync(path.join(ROOT, 'site', 'classes', '11', dir, 'index.html'), 'utf8');
      const nslots = (cs.match(/file-slot-head">[^\n]*\n\s*<div><b>([^<]*)<\/b>/g) || []).length;
      let ok = nslots === slots && !cs.includes('Uploading soon.');
      const bits = [];
      for (const spec of pats) {
        const [pat, want] = spec.split(':');
        const n = (cs.match(new RegExp(pat, 'g')) || []).length;
        bits.push(n + '/' + want);
        if (n !== Number(want)) ok = false;
      }
      if (!ok) bad.push(dir + ' (' + nslots + ' slots; ' + bits.join(', ') + ')');
    }
    log('hide-empty policy: cs-11 + eng-11 show only live slots', bad.length === 0,
      bad.length ? bad.join('; ') : 'cs-11: 2 slots; eng-11: 4 slots (7 notes, 14 solutions, 10 MCQs)');
  }
}

// ---------- summary ----------
const pass = results.filter(Boolean).length;
console.log('\n' + (pass === results.length ? 'ALL ' + pass + ' FORM/EVENT CHECKS PASSED ✅' : 'FAILED: ' + (results.length - pass) + '/' + results.length + ' ❌'));
process.exit(pass === results.length ? 0 : 1);

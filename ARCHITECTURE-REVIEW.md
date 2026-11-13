# StudySapiens — Technical Architecture Review
**Date:** 2026-11-07 · **Scope:** inspection only, nothing modified/rebuilt · **Build reviewed:** 87 pages / 89 HTML files, ss-v7
**Method:** every claim below was verified by reading the source, the built output in `site/`, or the audit tools. Nothing is assumed.

---

## 1. Frontend: framework, languages, libraries

**Verified facts**
- **Zero framework, zero npm/CDN dependencies in the shipped site.** Hand-written HTML5 emitted by Python f-strings; one CSS file; one JS file. Icons are hand-inlined SVGs (`_IC` dict in build.py, 47 icons).
- **CSS:** `assets/css/style.css` — 64,812 bytes source, regex-minified at build to 59,168 bytes (12.5 KB gzipped). Custom properties design system (olive/navy/gold palette), light mode only.
- **JS:** `assets/js/main.js` — 31,229 bytes, ships **unminified** (9.7 KB gz), `defer`-loaded. Handles: nav/drawer, overlay search, accordions (FAQ/QA), quiz engine, MDCAT/ECAT calculators, exam countdown, filters, mailto forms, share, PWA install, save/bookmark + proactive offline caching.
- **Fonts:** Google Fonts (Fraunces 600-800 + Inter 400-800) via one render-blocking `<link>` with `display=swap`; system fallbacks exist (`Georgia/Times`, `system-ui` stack) so failure degrades gracefully.
- **Inline JS per page is tiny and verified:** home 312 B (exam dates), quiz pages ~2.2 KB (`window.QUIZ`), everything else 25 B (`SITE_ROOT`).

**Verdict:** ideal for a content site; the only JavaScript "debt" is that main.js isn't minified (≈1.5 KB gz savings — cosmetic).

## 2. Backend architecture & server-side functionality

**Verified facts**
- **Production has no backend.** The site is pure static output; hosting serves files, nothing executes.
- `server.py` (74 lines) is a **dev/preview server only**: single-threaded `socketserver.TCPServer`, branded 404 passthrough, two basic security headers (nosniff, SAMEORIGIN), and an optional `/api/contact` POST that appends JSON to `messages.csv`.
- **Site forms do NOT use that endpoint**: all forms are `data-mailto` → JS composes a `mailto:` URL (`main.js:382-392`). Verified on the built contact page.
- Consequences: no server-side validation, no spam protection, no data persistence in production. "Notify Me Free" / contact / newsletter forms open the visitor's email app and rely on them pressing Send.

## 3. Database technology, schema, content storage

**Verified facts — there is no database.** Content storage is file-based:
| Store | Format | Acts as |
|---|---|---|
| `data.py` (516 lines) | Python dicts/lists | the "CMS" — site text, classes, subjects, updates, FAQs, chapters |
| `blogs/*.md` | front-matter markdown | blog posts (regex renderer `md_to_html`) |
| `quizzes/*.json` | JSON | quiz bank, embedded inline as `window.QUIZ` per test page |
| `files/` tree | PDF/DOC binaries | downloadable study files (owner uploads) |
| `scripts/watch_state.json` | JSON | board-watcher baseline |
Schema exists only by convention (keys in data.py). No migrations, no integrity layer, no concurrent editing.

## 4. How educational pages are generated & managed

**Verified flow (observed this session, reproducible):**
1. `build.py` (3,101 lines, single file) reads `data.py`, scans `files/` (`scan_files()`), scans `blogs/`, then renders 87 pages through `layout()` into `site/` — observed full builds complete in well under a second to ~2 s.
2. Subject pages: 24 SEO guides + upload slots, chapter-aware via `CHAPTERS` (verified live for 10th Chemistry Ch14-26 and 10th Biology Ch1-10 with real PDFs).
3. File pipeline: drop PDF in `files/class-N/<subject>/<category>/` → `sync_files.py` → chapter parsed from filename (`Ch01`, `chapter-14`, `unit_3`), label cleaned, card appears with size/ext badge. Honest "Uploading soon" otherwise.
4. Updates: `scripts/new_update.py` inserts into `UPDATES` with auto-backup + syntax check + rebuild; ticker/hub/home all regenerate.
5. Management = editing text files and running one command. Atomic from the owner's view, but there is **no staging/preview branch, no diff, no undo** beyond `scripts/data_backup.py` (single rolling version of data.py only).

## 5. SSR / SSG / CSR

**100% SSG (static generation at build time).** Verified: every page is complete HTML on disk; no client rendering of content. JS adds interactivity only. Search is the lone runtime fetch (`search.json`, lazy — fetched on first search open, 18 KB today). No SSR, no hydration, no SPA. This is the correct architecture for a content site and is a core strength.

## 6. Hosting infrastructure, server config, deployment

**Verified facts**
- Output targets any static host. `site/_headers` written for **Netlify/Cloudflare Pages conventions**: nosniff, Referrer-Policy, Permissions-Policy, 1-year immutable `/assets/*`, 1-day + `Content-Disposition: inline` for `/files/*` (view-not-download PDFs), no-cache HTML and sw.js.
- PWA: `site.webmanifest` + `sw.js` (ss-v7): precaches 6 core pages + CSS/JS + images, network-first navigations with offline fallback, stale-while-revalidate for assets incl. opaque Google Fonts, old-cache cleanup on activate.
- **Deployment process today is manual**: build locally → upload `site/` (drag-and-drop/zip). No CI/CD, no atomic deploys on self-managed hosting, no rollback.
- DNS/TLS/HTTP2+/Brotli will all be host-provided (not present in the repo to verify).

## 7. PDF & image storage, delivery, bandwidth

**Verified facts**
- Everything lives inside `site/` and is served from the same host — no object storage, no CDN-behind-CDN, no range/inline tuning beyond the one inline header.
- Deploy weight: **site = 11 MB** total; images = 6.0 MB; PDFs = 648 KB (10 files). Per-page transfer after gzip ≈ 15 KB HTML + 12.5 KB CSS + 9.7 KB JS + fonts (~40-60 KB first visit), then cached.
- **Verified hotspots:** `hero.png = 2.67 MB` (displayed 640×360, `fetchpriority="high"` on home); header logo `logo-trim-light.png = 333 KB` on all 89 pages; `og-base.png = 2.52 MB` deployed but **zero references** in HTML/CSS/JS (dead build-source file); `logo-trim.png = 322 KB`, `icon-512.png = 72 KB`, `og-image.jpg = 169 KB` acceptable.
- Image markup is CLS-safe (width/height present on hero and logos — verified), but **no `srcset`/responsive variants, no WebP/AVIF, 0 `loading="lazy"` attributes** (mostly harmless today since the 270 `<img>` tags are overwhelmingly above-the-fold logos; becomes important once photo-heavy blogs land).
- Bandwidth math: at current weights, ~100-130 KB per first pageview; 100k pageviews/mo ≈ 10-13 GB; 1M pageviews/mo ≈ 100-130 GB → free-tier edge (Netlify free = 100 GB/mo; Cloudflare Pages unmetered-ish). PDF views (~60 KB each) are negligible until thousands/day.

## 8. Can the architecture support 1,000-10,000 pages?

**Yes, without re-architecture** — verified reasoning:
- Build time is O(pages); 87 pages build in ~1 s, so 10k pages ≈ 1-3 min single-threaded Python. Acceptable for a one-author workflow.
- Output is static: hosting/caching/CDN all scale for free. Sitemap/robots/feed all regenerate mechanically.
- Deployment size: 10k pages × ~60-100 KB avg ≈ 0.6-1 GB of HTML — fine for Netlify/CF (deploy minutes get slower; zip drag-drop becomes impractical → move to Git-based deploy).
- Real bottlenecks at that scale are NOT rendering: (a) `data.py` becomes a multi-thousand-line content blob — needs splitting into per-topic data files or a headless CMS; (b) `search.json` grows ~200 B/entry → ~2 MB at 10k, still lazy-loaded so OK, but should become paginated/indexed; (c) content QA (the audit tools) must be wired as build gates.

## 9. Scalability limits when traffic increases significantly

| Layer | Today | At 100x traffic | Status |
|---|---|---|---|
| Page HTML | static files | CDN-cached, trivially serves | ✅ no code change |
| CSS/JS/fonts | static | same | ✅ |
| Hero/logo PNGs | 3+ MB per first visit | wasteful at scale; hurts users on 3G now | ⚠ exist now |
| PDFs | 648 KB total | fine to ~100k views/mo on free tiers; beyond that offload to R2/B2 or Drive-embed | ⚠ future risk |
| Search | lazy 18 KB fetch | fine to ~10k pages | ⚠ future (see §8) |
| Forms | mailto (no backend) | no data pipeline = no scaling question, but no data | ⚠ exist now (feature gap) |
| Service worker | correctly versioned | fine | ✅ |
Money, not code, becomes the constraint: Netlify free bandwidth or moving PDFs off the web host.

## 10. Security, authentication, access control

**Verified strengths**
- Attack surface is minimal: no server code in production, no accounts, no sessions, no cookies set by the site, no DB, no admin panel exposed, zero third-party JS (no supply-chain/script-injection vector in output).
- Server-side escaping: all interpolated content HTML-escaped via `esc()`; client-side `esc()` before `innerHTML` in search (verified at main.js:121); quiz/quiz data is self-authored; no `eval`; forms use mailto (no injection into any backend).
- Verified headers: nosniff, Referrer-Policy, Permissions-Policy; PDFs `inline` (intended).
- `localStorage` used only for class preference + saved items (`ss-et-class`, save shelf) — no sensitive data.
- 404 offline and search pages are `noindex` (verified).
- All external links `https` (no mixed content found); `rel="noopener"` on file/tab-opening links (verified on file rows).

**Verified gaps**
| Finding | Sev |
|---|---|
| No Content-Security-Policy anywhere — one bad paste into a blog .md/HTML (which renders raw-ish HTML) or a hijacked font CDN could inject script; X-Frame-Options/frame-ancestors missing from `_headers` (present only in dev server.py) → clickjacking possible on production host | Medium |
| Email exposed as plaintext `mailto:` on many pages → harvestable for spam | Low |
| SW fetches Google Fonts and caches opaque responses — standard, but fonts.googleapis.com is a runtime trust dependency | Low |
| `/api/contact` in server.py writes CSV with no validation/rate-limit — **not deployed**, but keep it that way or harden before use | Low |
Authentication/access control: none needed for current scope — correct design; admin surface = the laptop that runs build.py (protect that login + this workspace).

## 11. Backup, restoration, source-code ownership

**Verified facts**
- **No version control** (`.git` does not exist). No remote copy. `scripts/data_backup.py` = rolling single-version backup of data.py only, created by new_update.py. Workspace snapshotting is the only "history".
- Restoration test would fail for: full project history, bisecting a regression, recovering assets edited in place (e.g. minified CSS is regenerated, but PNGs are single-copied sources).
- **Ownership: 100% yours** — every byte of output is generated from local files; only runtime third-party dependency is Google Fonts (replaceable).
- Severity: **High** as an existing process gap (one bad edit/loss event = unrecoverable work; also blocks CI/CD and collaboration later).

## 12. SEO architecture, crawlability, indexing, structured data

**Verified via the audit tools + file inspection (0 issues across all 89 pages in latest runs):**
- Unique titles (≤66) + descriptions (≤160) on all pages; canonicals; `en` + `x-default` hreflang; robots meta `max-image-preview:large, max-snippet:-1`; OG/Twitter cards with explicit 1200×630 dims + alt.
- JSON-LD verified in output: sitewide `@graph` (Organization `#org` + logo/email/address, WebSite, per-page WebPage) on all 89; BreadcrumbList on 84; FAQPage on 38 (home + 37 subject-class pages); Article on 6 updates (ISO dates, publisher logo, `citation` array where sources exist); BlogPosting on 2; Quiz (practice-problem) on 1; ItemList on subject pages.
- `sitemap.xml` auto-generated with lastmod=build date, priorities, changefreq; 404/offline excluded (verified). `robots.txt` allows all + explicitly welcomes 11 AI crawlers; `llms.txt` present; RSS `feed.xml` (validated well-formed, RFC-822 dates, autodiscovery link in every head).
- Answer capsules (Quick Answer boxes) on MDCAT/ECAT/date-sheet/results; honest "Expected" labeling machine-visible.
- Internal linking: breadcrumbs + footer + subnav + related cards; broken-link audit = 0. Crawlability: pure HTML, no JS-rendered content, no orphan pages detected by audits.
- Gaps: no per-page OG images (single global og-image.jpg); sitemap lastmod always = today (fine but noisy for 10k pages → track real mtimes later); no hreflang to Urdu (no Urdu content yet).

## 13. Core Web Vitals & mobile performance

**Verified good:** deferred JS (9.7 KB gz), tiny inline scripts, minified CSS (12.5 KB gz), width/height on images (hero 640×360, logos dimensioned), fetchpriority=high on LCP, system font fallbacks, fonts `display=swap`, no carousel/heavy widgets, mobile-responsiveness machine-verified earlier (0 horizontal overflow across the sweep; 11/11 interaction tests incl. mobile viewport).
**Verified problems:**
| Finding | Sev |
|---|---|
| hero.png 2.67 MB as the LCP image on the page optimized for 3G users — self-defeating; LCP likely 4-8 s on real Pakistani 3G/4G | **High** |
| Header logo 333 KB PNG (134×44 display) on every page (SW precaches it, mitigating repeats) | Medium |
| Google Fonts CSS is render-blocking; on flaky networks FOUT period stretches; self-hosting the two fonts would remove it | Medium |
| No responsive image variants (srcset) anywhere | Medium (future: blog photos) |
| main.js not minified; HTML unminified (101 KB raw home — 14.5 KB gz, acceptable) | Low |
Lab-estimated today: LCP desktop ~fast, 3G mobile home **poor** purely because of hero.png; other pages have no hero and should be comfortably green.

## 14. Google AdSense compatibility

**Verified facts**
- Technically compatible: static pages accept `adsbygoogle` snippets anywhere; policy pages exist (About, Contact, Privacy). Privacy policy already contains AdSense + cookies language (verified quote: "If we display ads in future (e.g. Google AdSense), those partners may use cookies…").
- No ads.txt yet (normal pre-approval: needs your publisher ID after approval). No CMP/consent banner (not legally required for PK-only audience; add if you later target EU/UK).
- UPDATED 2026-11-13: owner asked to remove all public ad/no-ad statements.
  No ad network is configured or currently planned. Do not claim either "ad-free"
  or "no popup ads". Any future advertising requires explicit owner approval,
  privacy-policy review and CSP changes.
- Content eligibility looks fine: original teacher-written notes/explainers, no scraped copyrighted books hosted (eBooks page links OUT to elearn.punjab.gov.pk — verified).
- AdSense Auto Ads JS is render-deferred by design; expect measurable CWV hit (CLS risk from late-inserted slots) → reserve ad box heights when you integrate.

## 15. Technical debt & long-term maintenance risks

| # | Item | Exists now / future | Sev |
|---|---|---|---|
| 1 | No git + no offsite backup (§11) | exists | High |
| 2 | hero.png 2.67 MB LCP; header logo 333 KB; og-base.png 2.5 MB unused-but-deployed | exists | High / Med / Low |
| 3 | No CSP + no frame-ancestors in production `_headers` | exists | Medium |
| 4 | Forms are mailto: no subscription/contact data ever reaches you | exists | Medium |
| 5 | Single-file build.py (3.1k lines) + content-in-`data.py` Python strings (HTML bodies triple-quoted) | exists, grows worse | Medium |
| 6 | Manual deploys, no CI gate running the 4 audit tools before upload | exists | Medium |
| 7 | Hardcoded yearly dates (exam_date in data.py, "2027" copy) — Jan-Mar rollover ritual needed | exists | Low |
| 8 | Regex-based markdown renderer for blogs (subset MD) | exists | Low |
| 9 | Google Fonts runtime dependency (perf + privacy) | exists | Low |
| 10 | search.json monolith; sitemap mtimes | future (>3-5k pages) | Low |
| 11 | PDF/images on web host bandwidth beyond ~100k-1M views/mo | future | Medium |
| 12 | i18n/Urdu version would require templating refactor (hardcoded English in build.py strings) | future | Medium |
| 13 | PWA precache includes 2.67 MB hero → first-visit storage/heavy install (lighten once hero is optimized) | exists | Low |

---

## Prioritized improvement roadmap
(P0 = do now, P1 = before launch/AdSense, P2 = scale milestones. All are additive; none requires re-architecture.)

**P0 — correctness & safety (hours)**
1. Put the project under git with a remote (GitHub private repo). This single step closes the biggest risk in the whole review.
2. Re-compress images: hero.png → ~2,000-px WebP/quality-80 JPEG ≈ 150-250 KB; header logo → resized PNG/WebP ≈ 10-20 KB; stop shipping og-base.png in `site/` (keep it outside assets).
3. Add CSP + `X-Frame-Options: SAMEORIGIN` (or frame-ancestors) to `_headers`; start CSP in Report-Only, then enforce (`default-src 'self'; font/style exceptions for Google Fonts` until self-hosted).

**P1 — launch readiness (days)**
4. Minify main.js at build (same regex trick as CSS) or keep source + ship .min; self-host the two fonts (WOFF2, ~60-90 KB total) to kill the render-blocking third-party request.
5. Decide the data path for forms: keep mailto (state it honestly) or wire a real collector (Formspree/Netlify Forms/worker → email) so "Notify Me" actually subscribes people.
6. Wire the 4 audit tools as a pre-deploy checklist/build gate; add OG-per-page for the hubs that matter (classes, MDCAT).
7. Advertising: no network is configured or currently planned. If the owner later asks to revisit monetization, obtain approval first, then review privacy disclosures, CSP, consent needs and layout shifts.

**P2 — scale milestones (when approaching them)**
8. ~1-3k pages: split data.py into per-section modules; switch to Git-based deploys (atomic + rollback); paginate/index search.json; real mtimes in sitemap.
9. Traffic >100k views/mo or PDFs >500 MB: move `files/` to R2/B2 (or Drive-embed like competitors) with CDN caching; keep HTML on Pages/Netlify.
10. Yearly ritual: January review of data.py dates/labels (exam_date, "Expected" windows, session strings) — one PR per year keeps honesty guarantees true.

*End of report.*

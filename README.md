# StudySapiens 🎓

A complete, professional, SEO-optimized website for the new PCTB / PECTAA syllabus
(Class 9–12 Punjab Boards) — notes, exercise solutions, MCQ tests, pairing schemes,
guess papers, past papers, date sheets, MDCAT corner (with aggregate calculator),
CSS corner and eBooks.

**Navy `#011639` + Gold `#C5A059`** design system matching your logo.

---

## 📂 Project structure

```
studysapiens/
├── data.py            ← site text content (updates, plans, blurbs…)
├── build.py           ← the generator: python3 build.py → makes ./site
├── sync_files.py      ← ★ YOUR MAIN TOOL: publishes uploaded PDF/DOC files
├── files/             ← ★ DROP YOUR NOTES HERE (see below)
├── server.py          ← local preview:  python3 server.py  → http://localhost:8000
├── scripts/           ← board watcher + update publisher + audit tools (see below)
├── assets/            ← css, js, optimized images (webp/jpg/png actually deployed)
├── assets-src/        ← ORIGINAL full-size images (never deployed, never delete)
└── site/              ← ★ THE FINISHED WEBSITE (upload this folder to hosting)
    ├── index.html
    ├── classes/9/  classes/9/physics/  … (24 subject pages, no chapter pages)
    ├── files/           (your uploaded PDFs, auto-copied here)
    ├── pairing-scheme/  guess-papers/  past-papers/  date-sheet/
    ├── mdcat/  css/  ebooks/  updates/  about/  contact/
    ├── search.json  (powers the instant search)
    ├── sitemap.xml    (submit to Google Search Console)
    └── robots.txt
```

---

## 📁 How to upload notes / papers (your main job)

**No code editing needed.** Three steps:

1. **Drop the file** into the right folder (create folders as you need them):

```
files/class-9/physics/notes/Chapter 1 - Physical Quantities.pdf
files/class-9/physics/solutions/Chapter 1 - Solved Exercise.docx
files/class-9/physics/mcq/Chapter 1 MCQ Bank.pdf
files/class-10/chemistry/guess/Guess Paper 2027.pdf
files/class-12/biology/scheme/Official Pairing Scheme.pdf
files/class-9/physics/past/Lahore Board 2026.pdf
```

- Classes: `class-9` `class-10` `class-11` `class-12`
- Subjects: `physics` `chemistry` `biology` `mathematics` `computer-science` `english`
- Categories: `notes` `solutions` `mcq` `guess` `scheme` `past`
- File types: `.pdf` `.doc` `.docx` `.zip` `.ppt` `.pptx`
- The **file name becomes the button text** — write it the way students should read it.

2. **Run** `python3 sync_files.py`
3. **Upload** the regenerated `site/` folder to your hosting. Done.

Each file instantly appears on its **subject page** (Downloads section) and —
for guess/scheme/past — also on the matching **hub page**. Slots without files
show an honest *"Uploading soon"* placeholder automatically.

### Other content changes
- **Updates / ticker:** append to `UPDATES` in `data.py`, run `python3 build.py`.
- **Subject-page guide text:** edit `SUBJECT_INFO` in `data.py`.
- **Email / domain:** edit `SITE` in `data.py` and rebuild.

---

## 📡 Board updates workflow (ticker + /updates/ page)

Two scripts keep the site fresh without you manually checking 10 board sites.

**1. `scripts/watch_boards.py`** - checks all 9 BISE boards + PMDC + PCTB for new
notices. It only **detects and alerts**; it never touches the site.

```bash
python3 scripts/watch_boards.py --verify     # test which sources respond
python3 scripts/watch_boards.py --baseline   # first run: record current state
python3 scripts/watch_boards.py              # every day after: alert on new items
python3 scripts/watch_boards.py --source lahore pmdc   # check only some
```

- Baseline state lives in `scripts/watch_state.json`. Only genuinely NEW items
  are printed, with the board name.
- Some boards block visitors from outside Pakistan (you will see `HTTP 403` for
  Gujranwala / Faisalabad / Rawalpindi / Sahiwal from some networks). Run it on
  your own PC; failed sources are skipped and keep their old state.

**2. `scripts/new_update.py`** - publish a confirmed update in about 60 seconds:

```bash
python3 scripts/new_update.py --title "Sargodha Board HSSC Roll No Slips Out" \
    --tag "Date Sheet" --excerpt "One honest sentence for the ticker and cards."
```

It backs up `data.py`, inserts the entry at the top of `UPDATES` (so it shows
first in the ticker, home page and /updates/), syntax-checks, and rebuilds.
Then open `data.py`, replace the `[bracketed]` scaffold lines with the verified
details, and run `python3 build.py` again.

**Rule (unchanged):** publish only what you confirmed on the official board
website. The watcher tells you something changed; you decide what is true.

---

## 🧪 Pre-deploy validation (runs automatically)

Every `python3 sync_files.py` run ends with `scripts/precheck.py`: broken links,
missing PDFs, duplicate titles, bad JSON-LD, accidental noindex, sitemap checks,
JS syntax (via node when available). **0 critical = safe to deploy; any critical =
do not upload site/ until fixed.** Run standalone anytime:

```bash
python3 scripts/precheck.py          # full report
python3 scripts/precheck.py --quiet  # summary only
```

Images: put new originals in `assets-src/img/` first; optimized copies live in
`assets/img/` (hero is responsive WebP + JPEG fallback). Source images are never
overwritten or deleted.

Git: the project is a local git repo (history: `git log`). Roll back any change
with `git checkout` / revert to a commit. The full-backup zip
`studysapiens-full-backup-2026-11-07.zip` additionally restores + rebuilds the
exact pre-optimization state (verified).

---

## 🖥️ Preview locally

```bash
python3 build.py
python3 server.py        # → http://localhost:8000
```

---

## 🚀 Deploying (all free options)

| Host | Steps |
|---|---|
| **Netlify** (recommended) | drag the `site/` folder onto app.netlify.com → live in 10 s. Forms: change the forms' `data-mailto` behavior later if you want server-side submissions. |
| **GitHub Pages** | push `site/` to a repo → Settings → Pages → serve from `/docs` or root (`gh-pages` branch). |
| **Vercel** | `vercel deploy site/` |
| **cPanel / shared hosting (PK)** | zip `site/`, upload to `public_html`, unzip. Works since it's plain HTML/CSS/JS — no database needed. |

Point your domain (e.g. buy `studysapiens.com` for ~Rs 3,000/yr) → set it in
`SITE["domain"]` → rebuild → upload.

---

## 🔍 SEO checklist (already built in)

- ✅ Unique title + meta description per page — **0 duplicates, 0 missing, all descriptions ≤160 chars** across every page (auto-audit tools in scripts/)
- ✅ Canonical URLs, Open Graph + Twitter cards with image dimensions (1200×630) + alt
- ✅ JSON-LD `@graph` on every page: Organization (`#org` with logo/email/address), WebSite (`#website`), per-page WebPage + BreadcrumbList; chapter pages add LearningResource **and Quiz (practice problems with explained answers)**; every subject page adds FAQPage (auto-generated honest Q&As); updates add Article (ISO dates, publisher logo, official-source citations)
- ✅ `sitemap.xml` (all public pages, 404/offline excluded) + `robots.txt` (blocks `/offline/`, explicitly allows AI answer bots)
- ✅ hreflang (`en` + `x-default`), meta robots control (`noindex` on 404/offline/saved), author meta
- ✅ Semantic HTML — exactly one `<h1>` per page, all images have alt text
- ✅ Performance: minified CSS (‑9%), hero image `fetchpriority="high"` + preload, lazy-loaded media, no render-blocking JS
- ✅ `_headers` file (Netlify/Cloudflare): nosniff, Referrer-Policy, Permissions-Policy, 1-year immutable cache for `/assets/*`, no-cache for `sw.js`
- ✅ Branded 404 page served with a real 404 status (host-level + dev server)
- ✅ Instant site search (also a UX ranking factor)

**Deliberately skipped (with reasons):** sitelinks SearchAction schema (deprecated by
Google, Nov 2024), FAQ rich snippets everywhere as a *rankings* trick (Google now shows FAQ
snippets mainly for authoritative gov/health sites) — we still ship FAQPage schema
on subject pages because answer engines and AI crawlers read the schema even when
Google shows no visible snippet,
Course schema (not courses), image sitemap (few images, low value), HTML/JS
minification (risk > reward at our file sizes).

**After launch:**
1. Create Google Search Console → verify domain → submit `sitemap.xml`.
2. Create Bing Webmaster Tools → same.
3. Register Google Analytics (optional).
4. Ads are not currently configured or planned. Do not make public promises about
   whether ads will or will not appear. Any future ad integration needs explicit
   owner approval plus privacy-policy and CSP review.

---

## 🤖 AEO / GEO (answer + generative engine optimization, built in)

The site is built to be **quoted by AI**, not just ranked by Google:

- ✅ **robots.txt explicitly welcomes AI crawlers** — GPTBot, OAI-SearchBot,
  ChatGPT-User, ClaudeBot, Claude-User, PerplexityBot, Perplexity-User,
  Google-Extended, Applebot-Extended, CCBot, cohere-ai (one line to reverse)
- ✅ **llms.txt** at the root: plain-language site summary, trust policy, the
  canonical answers (MDCAT 50/40/10, ECAT 17/50/33, syllabus rollout years)
  and links to every core page — the emerging standard for LLM discovery
- ✅ **Answer capsules** ("Quick Answer" boxes) on the highest-question pages:
  MDCAT formula, ECAT formula, date-sheet timing, result windows. Question
  phrased exactly how students ask it, answer in 40-60 words, honest caveat
  underneath — the exact format AI overviews and ChatGPT quote
- ✅ **FAQPage schema on all subject pages** (auto-generated, honest, evergreen
  questions; chapter-count question appears only where chapter data is verified,
  e.g. Class 10 Chemistry Ch14-26)
- ✅ **Official-source citations** on update posts: visible "Official sources"
  line + Article schema `citation` field (E-E-A-T + the #1 GEO ranking factor)
- ✅ **RSS feed** (`feed.xml`): updates + blog posts, RFC-822 dates, for fast
  discovery by aggregators and AI tools
- ✅ Honest labelling ("Expected", "Uploading soon") doubles as an AI-trust
  signal: models prefer sources that distinguish fact from expectation

**Your part when writing blogs:** the AEO/GEO writing checklist lives at the
bottom of `blogs/README-BLOG.txt` (question headings, answer-first paragraphs,
numbers and tables, source citations, freshness bumps).

---

## 🧮 Feature inventory (what's inside)

- **Home** – animated hero w/ rotating words, stats counters, subject marquee,
  class grid, why-us, exam toolkit, MDCAT + CSS teasers, updates, FAQ,
  subscribe form
- **Classes mega-menu** – all 4 classes → **24 subject pages**; every subject has a
  short keyword-rich study guide + 5 download slots (notes, solutions, MCQ bank,
  guess paper, pairing scheme) that fill themselves when you drop files into `files/`
- **Pairing Schemes / Guess Papers / Past Papers** – filterable by class & subject,
  honest "expected" badges, notify-me CTAs, download buttons appear automatically
  when files land in the matching folders
- **Date Sheets** – expected 2027 timeline table + per-board alerts
- **MDCAT** – live **aggregate calculator** (Matric 10/ FSc 40/ MDCAT 50) with
  animated gauge, breakdown, 55% eligibility check • pattern table • syllabus accordion • admission timeline
- **CSS** – eligibility cards, compulsory (600) table, 7 optional groups,
  12-month strategy timeline, book list, mentorship CTA
- **eBooks** – official-textbook links (eLearn Punjab) per class/subject
- **Updates** – 6 generic, syllabus-safe posts + ticker
- **Contact / About / Privacy Policy / Site Map**
- **Global** – instant search (Ctrl+K), mobile drawer with accordions, dark-navy
  sticky header, scroll reveals, back-to-top, toasts, print styles,
  `prefers-reduced-motion` support

---

## 🛠️ Tech

Zero dependencies: hand-rolled static generator (Python), vanilla CSS (custom
properties, grid/flex) and vanilla JS (~14 kB). No frameworks to break, loads fast
even on 3G in rural Punjab.

Made with 💛 for Pakistan's students.

## Round 3 — UX & Visual Polish (Aug 2026)
- **Dark mode** — full olive/charcoal dark theme, toggle in header + mobile drawer, remembers choice (localStorage), respects system preference on first visit, zero white flash on load, adaptive browser theme-color.
- **Save chapters (bookmarks)** — every chapter has a "Save chapter" button; saved items live on the new /saved/ shelf page (device-local storage, no account), with a live count badge on the header bookmark icon.
- **Print / Save PDF** — chapter pages have a print button with dedicated print CSS: chrome stripped, notes + full exercise solutions auto-expanded, clean black-on-white output from either theme.
- **Reading progress bar** — thin olive progress bar under the header (site-wide).
- **Staggered reveal animations** — sibling cards fly in one after another; everything disabled under prefers-reduced-motion.
- Smooth theme-switch transitions; responsive header tuned for the new buttons (icon-only CTA at mid widths).

## Round 4 — Content & Utilities (Aug 2026)
- **Board exam countdown** — live d/h/m/s timer on home + date-sheet pages, per-class chips (auto-selects nearest exam), expected 2027 BISE windows, persists choice, dark-mode safe.
- **Real pairing schemes** — 5 complete chapter-wise scheme pages (Class 9 Physics, Chemistry, Biology, Mathematics, CS) from the PECTAA-issued 2026 assessment scheme: paper pattern, MCQ spread, SQ blocks, LQ pairing, high-weight chapters, prep tips, FAQ schema, printable.
- **Offline mode (PWA)** — service worker (network-first pages, stale-while-revalidate assets, Google Fonts cached), branded offline fallback page, saved chapters proactively precached, "back online/offline" toasts, install prompt bar (14-day dismissal).
- **4 new complete chapters** — 9 Physics Ch 2 (Kinematics), 9 Chemistry Ch 1 (States of Matter & Phase Changes), 11 Physics Ch 2 (Force and Motion), 11 Biology Ch 1 (Biodiversity & Classification). Each: intro + 6 note blocks + 5 solved exercise Q&As + 10 explained MCQs.

## Round 5 — Technical SEO Overhaul (Aug 2026)
- **Sitewide JSON-LD `@graph`** on all 344 pages: Organization (with `#org` id, logo, email, Punjab/PK address), WebSite, and a per-page WebPage node with `primaryImageOfPage`; everything cross-linked by `@id`.
- **Adaptive titles & descriptions** — chapter titles front-load "9th Class Physics Chapter N: Name" and only append "— Notes & MCQs" when under 60 chars; descriptions auto-trim at word boundaries ≤160. Result: 0 duplicates, 0 over-length descriptions site-wide.
- **Quiz practice-problem schema** on every completed chapter (10 Question nodes, each with `acceptedAnswer` + explanation Comment) — eligible for Google's practice-problem rich results.
- **Bug fixes found by the audit:** mixed quiz explanation keys (`e` vs `exp`) are now normalised at build time (with a defensive JS fallback); branded 404 page is now served with a real 404 status from every host (and the dev server); fixed a washed-out button on the 404 page and a 14px mobile horizontal wiggle (switched to `overflow-x:clip` on `<html>` with an `overflow:hidden` fallback, so `position:sticky` headers keep working).
- Chapter CTAs now deep-link to the matching **published pairing scheme page** (badged "2026 ✓") when one exists.
- Subject pages gained ItemList schema; hub titles trimmed; site-wide meta author; og/twitter image dimensions; `_headers` caching + security rules for Netlify/Cloudflare.

## Round 6 — Honest Content Reset → File-Download Model (Aug 2026)
> Owner decision: earlier unverified textbook drafts were removed. Current study resources
> are **made by teachers and verified by subject experts**, then uploaded file by file.

- **Removed:** all 288 chapter pages, the 15 demo chapters, the 5 hard-coded pairing-scheme
  detail pages, all chapter lists/unit numbers from data, and every specific syllabus claim
  in blog posts (two posts rewritten as generic, honest guidance).
- **New subject pages (24):** short keyword-rich study guide (unique per class × subject,
  evergreen content — no chapter names anywhere) + a **Downloads** section with 5 labelled
  slots (Chapter Notes · Exercise Solutions · MCQ Bank · Guess Paper · Pairing Scheme).
- **File-driven publishing:** drop a PDF/DOC into `files/class-9/physics/notes/` and it
  appears on the subject page (and the correct hub for guess/scheme/past) with a download
  button, file-type badge and size. No file yet → honest "Uploading soon" placeholder +
  notify-me email link. One command publishes everything: `python3 sync_files.py`.
- **Hubs stay honest:** pairing/guess/past-paper hubs show "expected / in preparation"
  badges and swap to download buttons automatically when files exist.
- **Also removed:** the save-chapters shelf (nothing to save without chapter pages) and all
  chapter entries from search/sitemap. Site is now 49 pages, every claim verifiable.
- **Full link audit:** 0 broken internal links, 0 duplicate titles/descriptions, 0 JSON-LD
  errors, 0 mobile overflow — verified with an automated checker after the rebuild.

## Content progress
Now owner-driven: content = the files you upload. See "How to upload notes / papers" above.

## Corrections & policy changelog
- **13 Nov 2026 - MDCAT pattern corrected (critical):** earlier pages showed the old
  200-MCQ pattern (Bio 68 / Chem 54 / Phy 54 / Eng 18 / LR 6). PMDC's official MDCAT-2026
  notices confirm **180 MCQs: Biology 81, Chemistry 45, Physics 36, English 9, Logical
  Reasoning 9**, no negative marking, difficulty mix 15/70/15; exam held 20 Sep 2026
  (rescheduled from 16 Aug). Fixed on /mdcat/ (pattern table + calculator defaults, now
  out of 180), the MDCAT-2026 guide article, homepage promo, journey timeline and the
  blog-guide example. Added "last verified" lines linking both PMDC PDFs, calculator test
  cases (180 / 99 / 90 / decimals / zero / invalid), and a public correction notice at
  /updates/mdcat-2026-pattern-correction/. MDCAT 2027 content waits for the official notice.
- **13 Nov 2026 - ECAT merit basis corrected (critical):** the /ecat/ calculator asked for
  FSc marks out of 1100, implying merit uses the combined FSc. UET's official Undergraduate
  Prospectus (Fall 2026) and admission portal confirm the intermediate-stream merit is
  **Matric 17% + First Year (HSSC Part-I) 50% + ECAT 33%**. Fixed the calculator label
  ("HSSC Part-I / First Year Marks"), default Part-I total (550, Punjab boards; editable),
  worked example, journey timeline and facts; eligibility wording now states the 50/60%
  minimums apply to the complete Intermediate. Added "last verified" lines linking UET's
  prospectus and portal, notes for A-Level / DAE / B.Tech streams (UET's own calculator
  tracks), calculator test cases (400 / 260 / decimals / zero / invalid / full 935+495+280
  = 82.55%), and a public correction notice at /updates/ecat-2026-merit-basis-correction/.
- **13 Nov 2026 - CSS optional-subject selection clarified (correction):** /css/ showed
  "choose 200 / choose 100" group cards that could be read as one subject from every group
  (which would total 900, not the official 600), and Group 3 was missing Town Planning &
  Urban Management entirely. Replaced with the official Appendix-I selection matrix
  (Group I: one 200-mark subject, codes 11-15; Group II: one 200-mark subject codes 16-17
  or two 100-mark subjects codes 18-21; Groups III-VII: one 100-mark subject per group,
  two of them taken to complete 600), two worked 600-mark examples, the Rule 11(13)/(14)
  rejection warning, a CE-2027 current-cycle callout (apply by 25 Nov 2026, hard copy by
  4 Dec 2026, exam ~Jan 2027), Rule-12 passing benchmarks, and "last verified" lines
  linking the FPSC rules PDF and the CE-2027 public notice. Public notice at
  /updates/css-optional-selection-rules/.
- **13 Nov 2026 - wrong Tarjuma scheme PDFs fixed (critical):** the Class 10 Tarjuma-tul-Quran
  page linked a pairing-scheme PDF that was actually "Urdu Compulsory - Grade 10" (2026-27).
  The new pdf_audit.py also caught the same mistake at Class 9 (title: "Urdu Compulsory -
  Grade 9"). Both files moved to their correct homes (files/class-9/urdu/scheme/ and
  files/class-10/urdu/scheme/ - both Urdu pairing-scheme cards are now live), the two
  Tarjuma cards revert to Coming Soon, and the static pairing-scheme page was updated.
  Added a pre-publish QA checklist (below) and the automated deploy gate
  scripts/pdf_audit.py, wired into sync_files.py.

## Pre-publish QA checklist (run for every PDF before it goes live)
1. **File name** follows the convention and names the right subject and class
   (e.g. `StudySapiens_Pairing-Scheme_2026-27_Grade10_Urdu-Compulsory.pdf` belongs in
   `files/class-10/urdu/scheme/`, not in `tarjuma-tul-quran/`).
2. **PDF title** (open the file, read page 1) matches the subject AND class of the folder
   it lives in.
3. **Subject, class and category** in the file name, the PDF's own title, the folder and
   the target page all agree.
4. **Session / exam year** in the PDF (e.g. "Session 2026-27 - Annual Examination 2027")
   matches what the page promises.
5. **Page count** looks right for the category (a pairing scheme is 1-3 pages; notes are
   longer). Anything unreadable or 0 pages is rejected.
6. **Download test**: after `python3 sync_files.py`, open the built page in site/ and click
   the link - the PDF must open.

Automated safety net: `python3 sync_files.py` now runs `scripts/pdf_audit.py` automatically.
It blocks the deploy when a PDF's file name or page-1 title names a different subject or
class than its folder, when a linked PDF is missing, or when a PDF is empty/unreadable, and
it warns about orphan PDFs. Title checks need pypdf (`pip3 install --break-system-packages
pypdf`); without it, file-name + link checks still run.

## Hosting, WAF & crawler policy (Hostooze) — ops runbook
Reviewed 13 Nov 2026 after a "Security Verification" challenge was observed for
headless-browser clients (some browser-like UAs got 403/401; Googlebot-like and curl
got 200).

**What the site itself guarantees (verified):**
- No user-agent sniffing or bot blocking anywhere in our JS/HTML - the site never
  challenges anyone.
- robots.txt explicitly allows Googlebot, Bing, and 12 AI/answer-engine crawlers.
- Every page has the full og:/twitter: meta set, so social scrapers (WhatsApp,
  Facebook) can build previews the moment the edge lets them through.

**Required policy at the Hostooze edge/WAF (ask support to set/confirm):**
1. No JavaScript or interstitial "Security Verification" challenge for ordinary
   desktop/mobile browsers. Challenges should only trigger on clearly malicious
   traffic.
2. Verified crawler allowlisting by reverse DNS, not by user-agent string:
   - Googlebot: forward-confirmed reverse DNS must end in `googlebot.com` or `google.com`
   - Bingbot: must end in `bingbot.com` or `search.msn.com`
   - Facebook/DuckDuckGo and other legit bots: same rDNS principle.
   (UA strings are trivially spoofed; rDNS is the verification Google itself documents.)
3. Rate limits generous enough for classroom/result-day peaks; normal visitors
   should never see 429.
4. Static-file caching (our .htaccess already sets long cache for assets, 1 day for
   PDFs, no-cache for HTML/sw.js) - keep the edge cache honoring these.

**How to verify after any WAF change:**
- Google Search Console -> URL Inspection -> Live Test on the homepage and /mdcat/
  (must render fully, no challenge).
- Rich Results Test (search.google.com/test/rich-results) on the homepage.
- Facebook Sharing Debugger -> "Scrape Again" (preview must show title/description/image).
- Share a link on WhatsApp from a real phone and open it on mobile data.
- `curl -A "<browser UA>" -I https://www.studysapiens.com/` -> expect 200, not 403.

**Monitoring:**
- Hostooze panel/server logs: watch 401/403/429/5xx rates; investigate spikes.
- Search Console -> Settings -> Crawl stats (Googlebot response spikes in 4xx/5xx).
- If a challenge is ever served to a real visitor: capture time + URL + their network
  and send it to Hostooze support asking for a WAF exception for the site.


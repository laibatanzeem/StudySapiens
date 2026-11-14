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
- **14 Nov 2026 - forms go server-side + GTM event tracking (monetization/retention):**
  every "Notify me"/subscribe form and the contact form only opened the visitor's email
  app - no list building, and many mobile users have no configured mail client. All
  forms now submit server-side once configured (newsletter -> your ESP endpoint,
  contact -> Web3Forms), with a required consent checkbox, privacy + unsubscribe links,
  double opt-in messaging, a hidden honeypot spam trap, and inline success/error states.
  Until keys are pasted into the new site/assets/js/ss-config.js they automatically fall
  back to the old mailto behaviour, so nothing breaks while setup is pending. "Notify me"
  buttons on coming-soon cards (pairing schemes, guess & model papers) now focus the
  subscribe form and pass an `interest` value for segmentation. Added GTM dataLayer
  events: newsletter_signup, contact_submit, pdf_download, calculator_use, quiz_start,
  quiz_complete (quiz engine now tags slug/score/total/percent). Privacy policy
  rewritten to match reality (newsletter + ESP, form backend, analytics cookies,
  your-choices section with an #unsubscribe anchor). Site email switched from
  admin.studysapiens@gmail.com to **admin@studysapiens.com** everywhere (footer, contact
  page + meta, FAQ, blogs, JSON-LD, pairing-scheme page). Service worker bumped to
  ss-v14 (precaches ss-config.js but fetches it network-first, so an edited key applies
  on the next page view). New automated gate scripts/forms-verify.mjs (20 checks: form
  integrity across all 91 built pages, Web3Forms payload, ESP submit + CORS-blocked
  fallback, honeypot drop, mailto fallback, all six events) - run it after every rebuild
  alongside scripts/calc-verify.mjs (still 18/18).
- **14 Nov 2026 - ads-readiness privacy/consent stack:** GTM/GA4 loaded with no consent
  banner, thin privacy wording, and no terms/copyright/ad-disclosure pages - a blocker
  for AdSense. Implemented **Google Consent Mode v2** on every page (ad_storage,
  ad_user_data, ad_personalization, analytics_storage all DENIED by default, set from
  the visitor's saved choice in a synchronous head script that runs before gtm.js;
  the GTM tag itself is untouched and still first in <head>). Added a first-party
  cookie banner (main.js): Accept all / Necessary only / Customize (separate analytics
  and ads toggles), choice stored 12 months in ss-consent-v1, reopenable anytime via
  "Cookie settings" in every footer, pushes consent 'update' + a consent_choice GTM
  event. Disable it in one line (SS_CONFIG.consentBanner=false) when switching to a
  Google-certified CMP - see the runbook below. Privacy policy fully rewritten: GA4/GTM
  disclosure, a cookie/local-storage table (_ga, ss-consent-v1, ss-saved-v1,
  ss-et-class, ss-install-hide-until), legal basis in plain words, third parties
  (Google, ESP, Web3Forms, Hostooze, Google Fonts), retention periods (analytics 14
  months, contact messages 24, newsletter until unsubscribe), user rights, and a
  children's-data section (13+, parent email, non-personalised ads stance). New legal
  pages: /terms/ (Terms of Use), /copyright/ (DMCA-style takedown, 2-working-day
  promise), /advertising/ (honest "no ads yet" + future display/affiliate rules,
  personalised-ads-only-with-consent, child treatment). All linked from every footer,
  the site map, and sitemap.xml. Service worker bumped to ss-v15. forms-verify.mjs
  extended to 33 checks (consent defaults on every page, banner accept/reject/custom/
  returning-visitor flows, legal pages built + linked + in sitemap).
- **14 Nov 2026 - chapter-level SEO pages (P1):** the site had subject hubs linking to
  PDFs, while competitors rank with chapter-specific pages. Added
  /classes/{cid}/{sid}/chapter-{n}/ — **197 new pages**, one per chapter that has at
  least one live file (site: 92 → 289 pages, all in sitemap.xml at priority 0.55 and
  in search.json). Each page: H1 "Class X Subject Chapter N Notes — New Syllabus
  {session}", unique meta description, breadcrumb + prev/next chapter navigation,
  author/reviewer line ("Teacher-made · expert-reviewed"), last-updated date from the
  newest file, all of that chapter's downloads (notes / solved exercises / MCQs /
  numericals) with category headers, a click-to-load **online PDF viewer** (fires
  pdf_download like a normal download), an honest structured overview, FAQ block with
  FAQPage + BreadcrumbList JSON-LD, share row, and the review-promise callout.
  Verified chapter titles come from the existing CHAPTERS table; chapter numbers are
  parsed from file names the same way subject-page cards do (Tarjuma pages use Surah
  names, e.g. "Class 9 Tarjuma-tul-Quran Surah Maryam Notes"). NEW
  **chapter_content.py** holds hand-written summaries — pilot: all 9 Class 9 Physics
  chapters (summary + key points + formulas table + exam tips + 2 custom FAQs each,
  ~340 words of unique content per page). Chapters without hand content get an honest
  structured overview (~330 words: what the chapter is, which files are live, how to
  study it, correction promise) — never fabricated definitions. Subject-page chapter
  cards now link to each chapter page. forms-verify.mjs extended to 39 checks. To
  enrich more chapters: add entries to chapter_content.py and re-run sync_files.py.
- **14 Nov 2026 - SEO fixes 4.2/4.3/4.4 (H1, schema, sitemap):** homepage H1 was
  keyword-stuffed with rotating words ("Free Notes Pairing Schemes Guess Papers MCQ
  Tests Notes…"). Replaced with the single clear H1 "Free Study Notes for Punjab
  Board Classes 9–12 — New PCTB/PECTAA Syllabus"; the rotating word animation moved
  into a decorative aria-hidden subheading (.hero-roto) so sighted users keep the
  effect and screen readers get one clean H1. Structured data cleanup: removed the
  homepage's duplicate EducationalOrganization + WebSite JSON-LD and its SearchAction
  (Google retired the sitelinks searchbox, and /?q= was never a real results page -
  site search is an overlay on search.json); the whole site now carries exactly ONE
  organization node per page (layout @graph, upgraded to EducationalOrganization) and
  one WebSite node; pairing-scheme.html's static graph matches. Chapter pages gained
  LearningResource schema with author (StudySapiens Teachers Panel), provider/publisher
  @id-linked into the site graph, teaches/educationalLevel and dateModified from the
  newest file. Blog/updates articles already carried BlogPosting/Article author +
  publisher @id schema (verified). FAQPage markup is KEPT on purpose: Google retired
  the FAQ rich result, but the markup stays valid and useful for Bing and the AI
  answer engines the site targets (AEO/GEO). Sitemap lastmod is now real: sitemap.xml
  dates bump only when a page's built HTML actually changes (md5 hash vs the committed
  sitemap-cache.json; unchanged pages keep their old date forever; verified by double
  rebuild producing a byte-identical sitemap). forms-verify.mjs extended to 47 checks.

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


## Newsletter & contact forms — one-time setup (ESP + Web3Forms)

Why: the old forms only opened the visitor's email app (many mobile users have none, and
no addresses were ever collected). Since 14 Nov 2026 every form submits server-side and
falls back to the email-app behaviour only while your keys are still missing - the site
never breaks while setup is pending.

**Already built and verified (nothing to do):**
- Footer subscribe form + "Notify Me Free" forms on every page -> your ESP, with consent
  checkbox, privacy link and unsubscribe mention.
- "Notify me" buttons on coming-soon cards (pairing schemes, guess & model papers) focus
  the nearest subscribe form and remember what the student asked for (`interest` field).
- Contact form (/contact/) -> Web3Forms with a hidden honeypot field + provider-side spam
  filtering; inline success/error messages, no page reload.
- Privacy policy updated (newsletter, contact form, analytics, "your choices" section).
- Site email switched everywhere to admin@studysapiens.com.
- GTM events (table below) verified by scripts/forms-verify.mjs (20/20).

**Step 1 - contact form (5 minutes, no account):**
1. Open https://web3forms.com , enter admin@studysapiens.com and submit.
2. Check that inbox for their "Access Key" email.
3. Edit `site/assets/js/ss-config.js` (Hostooze File Manager) and paste the key into
   `contactAccessKey: ""`. Or send the key here and it gets baked in and rebuilt.
   Submissions then arrive in the admin@studysapiens.com inbox.

**Step 2 - newsletter / ESP:**
1. Sign up at MailerLite (recommended, free up to 1,000 subscribers) using
   admin@studysapiens.com. Brevo / Buttondown / Kit also work.
2. Create a sign-up form and turn DOUBLE OPT-IN **on** in its settings.
3. Copy the form action URL from the embed code (`<form action="...">`) into
   `newsletterEndpoint: ""` in ss-config.js. For MailerLite also change
   `newsletterEmailField` to `"fields[email]"` and copy any hidden inputs from the embed
   into `newsletterFields`.
4. Optional segmentation: "Notify me" buttons send an `interest` value (e.g. "12th
   Physics pairing scheme"). Create a text custom field named `interest` in the ESP if
   you want to see it; otherwise it is harmlessly ignored.
5. Deliverability (when comfortable): ask Hostooze to add the ESP's SPF/DKIM DNS records
   for studysapiens.com so confirmation emails do not land in spam.

> Never paste a secret API key into ss-config.js - only public form URLs and website
> access keys. Everything in that file is visible in the visitor's browser by design.

**Events pushed to the GTM dataLayer (container GTM-5ZRS53MF):**

| Event              | Fires when                              | Extra data                                  |
|--------------------|-----------------------------------------|---------------------------------------------|
| newsletter_signup  | subscribe form sent (ESP or fallback)   | method, location (footer/inline), interest  |
| contact_submit     | contact form sent                       | method                                      |
| pdf_download       | any PDF link clicked                    | file_name, link_url                         |
| calculator_use     | first valid aggregate computed          | calculator: mdcat / ecat                    |
| quiz_start         | "Start the Test" clicked                | quiz slug                                   |
| quiz_complete      | last question answered                  | quiz, score, total, percent                 |

To see the events: use GTM Preview mode, or create a GA4 property and add a GA4
configuration tag in GTM - the events then appear under Reports > Engagement > Events
(file_name etc. arrive as event parameters).

**Automated tests:** `node scripts/forms-verify.mjs` - 20 checks (form integrity across
all built pages, Web3Forms payload, ESP submit + CORS-blocked fallback, honeypot drop,
mailto fallback, all six events). Run after every rebuild, alongside
`node scripts/calc-verify.mjs`.

## Ads readiness: consent (CMP), cookies & legal pages

Built 14 Nov 2026 so the site can pass AdSense/Ad Manager review when ads are enabled.
What is already live: Consent Mode v2 on every page (all denied by default), the
first-party cookie banner, the rewritten Privacy Policy, and /terms/, /copyright/
(DMCA), /advertising/ pages — all linked in every footer, site map and sitemap.xml.

**The one thing Google additionally requires for personalised ads in the EEA/UK/
Switzerland: a Google-CERTIFIED consent management platform (IAB TCF).** Our
first-party banner is NOT certified. Decision tree when ads are enabled:

1. **AdSense route (recommended, free, no code):** in the AdSense console open
   *Privacy & messaging* and create an EEA/UK/CH consent message. Google serves its
   own certified CMP to those regions only. Then set `consentBanner: false` in
   site/assets/js/ss-config.js the SAME DAY, so EEA visitors never see two banners
   (visitors elsewhere see none either way — Google's CMP geo-targets).
2. **Third-party certified CMP route (CookieYes / Cookiebot / etc.):** paste their
   script per their instructions, then again set `consentBanner: false`.
3. **Never** enable personalised ads for EEA/UK/CH traffic before one of the above.

Consent Mode v2 wiring (for reference): the inline script right after the GTM tag in
`<head>` reads `ss-consent-v1` from localStorage and calls
`gtag('consent','default',{ad_storage, ad_user_data, ad_personalization,
analytics_storage, wait_for_update:500})` — denied until the visitor accepts, granted
per their saved choice on return visits. The banner pushes `gtag('consent','update')`
plus a `consent_choice` dataLayer event when the visitor decides. In GTM, consent
types map to Google's built-in consent variables; GA4 already respects them
(cookieless pings while analytics consent is denied).

Children: the audience is secondary/higher-secondary (≈13+); the site is declared
NOT child-directed, the privacy policy forbids knowingly collecting under-13 data,
and the Advertising Disclosure commits to non-personalised treatment where required.
When AdSense is enabled, review Google's child-directed guidance for the junior
class pages and keep personalised ads off where unsure.

Verification: `node scripts/forms-verify.mjs` (33 checks — includes consent defaults
on all pages, accept/reject/customize/returning-visitor banner flows, and the legal
pages) + `node scripts/calc-verify.mjs` (18/18).

## Chapter pages (long-tail SEO) — how they work

`/classes/{cid}/{sid}/chapter-{n}/` exists for **every chapter that has at least one
live file** (197 pages as of 14 Nov 2026). Titles/names come from the verified
`CHAPTERS` table in data.py; the file→chapter matching is the same one the subject
pages use, so a new PDF upload automatically gets its chapter page on the next
`python3 sync_files.py`.

Each page contains: H1 "Class X Subject Chapter N Notes — New Syllabus {session}",
unique meta description, breadcrumbs + prev/next chapter links, teacher/expert
byline + last-updated date (from the newest file), all downloads for that chapter
(notes / solved exercises / MCQs / numericals), a click-to-load online PDF viewer
(tracked as pdf_download), FAQ block with FAQPage + BreadcrumbList JSON-LD, share
row, and the correction-promise callout. Sitemap priority 0.55 / weekly; also added
to search.json.

**Hand-written summaries** live in `chapter_content.py` (pilot: all 9 Class 9
Physics chapters — summary, key points, formulas table, exam tips, 2 custom FAQs;
~340 unique words per page). Chapters without an entry get an honest structured
overview (~330 words) instead — we never fabricate definitions. To enrich a chapter,
add an entry and rebuild; to cover a whole subject next, copy the Class 9 Physics
pattern. Best order to expand: Class 9 Mathematics → Class 9 Biology/Chemistry →
Class 11 Biology (they have the most files).

Verification: `node scripts/forms-verify.mjs` (39 checks — includes chapter template
integrity on all pages, sitemap coverage, subject-page links, pilot word count, and
the PDF viewer behaviour).

## Schema & sitemap policy (4.2 / 4.3 / 4.4)

- **One H1 per page with one keyword focus.** The homepage's rotating-word animation
  is decorative only (`aria-hidden`), never inside the H1.
- **One schema graph per page.** The layout emits a single @graph: EducationalOrganization
  (`@id …/#org`) + WebSite + WebPage, plus page-specific nodes (BreadcrumbList, and where
  relevant FAQPage / Article / BlogPosting / LearningResource) that link to the org via
  `@id`. No SearchAction anywhere (retired by Google; our search is a client-side
  overlay on search.json, not a crawlable results page).
- **FAQPage markup is kept deliberately**: Google retired the FAQ rich result, so do not
  expect it there — but the markup is valid and helps Bing + AI answer engines (our
  AEO/GEO strategy). The visible FAQ content stays regardless.
- **Authorship**: articles use BlogPosting/Article with an Organization author; chapter
  pages use LearningResource authored by "StudySapiens Teachers Panel" with
  dateModified from the newest uploaded file. To upgrade to real Person author/reviewer
  schema, give the teacher/reviewer names and they get their own Person nodes.
- **sitemap.xml lastmod is real**: build.py hashes each built page and compares with
  `sitemap-cache.json` (committed); a page's date only changes when its HTML changes.
  Don't delete that file — losing it bumps every date once. Splitting sitemaps by type
  (pages/chapters/PDFs/updates) is a later optimisation once we pass ~500 URLs.
- **Verify after deploying** (user-side): Rich Results Test on a chapter page and a
  blog post (expect: breadcrumb only), and the Schema Markup Validator on the homepage
  (expect: zero errors, one clean graph).

## Batch 4.5 / 4.6 / 5.1 — titles, internal linking, hero preload, a11y (14 Nov 2026)

- **4.5 Titles & meta descriptions (site-wide, 290 pages):** every `<title>` is now
  ≤ 62 rendered chars, keyword-first, brand appended only while it fits (`ttl()` helper
  in build.py — never use it for visible H1s, it appends the brand). Home: "Free Notes &
  Past Papers (New PCTB Syllabus) | StudySapiens". Class pages: "Class 9 Notes: All
  Subjects — 2025-26". Chapters: "Class 9 Physics Chapter 3 Notes — 2025-26" (session
  replaces the repeated "New Syllabus"). Updates articles + Tarjuma surah titles trimmed
  at word boundaries. Every meta description is 120–160 chars (was up to 181).
- **4.6 Internal linking:** chapter pages now carry contextual links inside the article
  body (subject hub, pairing scheme, past papers) + two new blocks on all 197 chapter
  pages: **"Related chapters"** (2–3 nearest siblings, never duplicating prev/next) and
  **"Where to go next"** (pairing scheme / past papers / MCQ tests, plus MDCAT & ECAT
  calculators on class 11–12 chapters). Board pages deep-link the results, date-sheet and
  roll-number-slip hubs at per-board anchors (`#bise-lahore` …) — those hubs now tag all
  9 board rows/chips with `id="bise-*"`.
- **5.1 Hero preload = rendered candidate:** the hero ships `<picture>` (WebP source +
  JPG `<img>` fallback); the preload's `imagesrcset`/`imagesizes` match the WebP source
  exactly, so modern browsers reuse the preloaded bytes. Locked in by forms-verify.
- **A11y fixes (from the local axe audit, contrast re-computed to WCAG AA):**
  - Drawer is `inert` in markup when closed and main.js toggles `inert` + `aria-hidden`
    together on open/close (it previously stayed `aria-hidden` even when open).
  - Contact form class/topic selects now have real `<label for>` associations.
  - Exam-timer chips: `role="tablist"` → `role="group"` (they're filters, not tabs) with
    `aria-pressed` synced by JS.
  - Inline links in prose (article bodies, callouts, chapter boxes, FAQ answers, card
    paragraphs) get underlines with a soft decoration colour — no longer colour-only.
  - Contrast fixes: `.hero-roto` on the navy hero → #D9DCC2 (was ink-on-navy, 1.56:1 →
    11:1); `.badge-gold` text → #565A2E (3.24:1 → 6.25:1). The other flagged elements
    (hero badge, stat labels, `.et-lbl`, gauge muted text, kickers) already pass AA —
    measured, not guessed.
- **Service worker bumped to `ss-v16`** (CSS + JS changed this batch).
- forms-verify now runs **59 checks** (adds: title length, desc length, H1 brand-suffix,
  preload/picture match, drawer inert, contact labels, et-chip roles, board anchors,
  board deep links, chapter contextual links).

## Security headers — current state & switch conditions

Current `.htaccess` (already live in the build): security headers with **CSP in
Report-Only mode**, `frame-ancestors 'self'`, `X-Content-Type-Options nosniff`,
`Referrer-Policy strict-origin-when-cross-origin`, plus `Permissions-Policy`. **No HSTS
yet.** These two are deliberately deferred — flip them only when:

- **HSTS (Strict-Transport-Security):** enable only after the canonical redirect is
  stable and verified — i.e. http→https and any www/non-www redirect resolve in a single
  hop on every URL (check with `curl -sIL http://studysapiens.com/`), because HSTS pins
  HTTPS for every visitor and a redirect loop would lock people out. Start with a short
  `max-age=300` for a week, then raise to `max-age=31536000; includeSubDomains` (add
  `preload` only if we register at hstspreload.org).
- **CSP report-only → enforce:** first collect and clear the reports (browser console +
  any reporting endpoint). Enforcing now would risk breaking GTM/GA4, the PDF viewer or
  Web3Forms. When enforcing, keep `frame-ancestors 'self'`.
- **When ads/monetization is switched on**, the enforced CSP must allow the Google ad +
  CMP stack before enabling it, roughly:
  `script-src` += `https://pagead2.googlesyndication.com https://*.doubleclick.net https://www.googletagmanager.com`
  (GTM host is already loaded first-party-async); `img-src`/`connect-src` += the same +
  `https://googleads.g.doubleclick.net https://*.googleusercontent.com`;
  `frame-src` += `https://*.doubleclick.net https://td.doubleclick.net` and the certified
  CMP's frame origin; `consent` is handled client-side (Consent Mode v2 already
  installed). Re-run a Report-Only pass with the ad tags live before enforcing.

## Upload: Class 11 Chemistry chapter-wise practice tests (14 Nov 2026)

- **16 practice model papers** (Ch 1–16, one page each: 8 MCQs + 6 short + 2 long
  questions in board pattern) → `files/class-11/chemistry/model/`.
- **New chapter set:** `CHAPTERS[("11", "chemistry")]` with the 16 titles of the new
  syllabus book (Periodic Table → Lab Safety), taken from the papers themselves.
- **Chapter pages now include test categories:** `CHAPTER_CATS` extended with `model`
  and `testpapers`, so practice papers / test papers show inside chapter cards and on
  chapter pages (download row + online PDF viewer). Class 11 Biology's existing model
  papers moved into their chapter cards too.
- **Test-only chapters get honest wording:** title/H1 say "Chapter N Test Paper"
  (not "Notes"), the description and how-to paragraph are test-specific
  ("sit this paper in one go — timed, book closed"), and the study-guide wording stays
  on chapters that actually have notes/solutions/MQCs.
- 16 new pages (`/classes/11/chemistry/chapter-1/` … `chapter-16/`), site now 305 pages,
  349 published files; forms-verify 60 checks (adds a chem-11 upload guard).

## Upload: Class 11 Chemistry exercise solutions (14 Nov 2026)

- **16 exercise-solutions PDFs** (Ch 1–16, 5–10 pages each) →
  `files/class-11/chemistry/solutions/`. Chapter titles on the PDFs match the
  chapter set added with the practice tests.
- Every class-11 chemistry chapter page now carries **both** the solved exercise and
  the practice model paper: two download sections, and the online viewer opens the
  solutions first (notes → solutions → mcq → numericals → model → testpapers priority).
- Wording auto-adapted: with real study content present, titles/H1s are back to
  "Chapter N Notes — New Syllabus 2025-26" and the study-guide paragraph replaces the
  test-only how-to. Site stays at 305 pages, now 365 published files; forms-verify 60.

## Upload: Class 11 Chemistry complete notes (14 Nov 2026)

- **16 complete-notes PDFs** (Ch 1–16, 3–8 pages each) → `files/class-11/chemistry/notes/`,
  titles verified against the chapter set.
- Every class-11 chemistry chapter page now carries the full stack: **Chapter Notes +
  Exercise Solutions + Model Papers** (three download sections), with the online viewer
  opening the complete notes first. Row labels match the biology convention
  (Notes / Exercise Solutions / Practice Model Paper).
- Class 11 Chemistry is the first subject with notes + solutions + tests on all 16
  chapters. 381 published files; forms-verify 60 (chem-11 guard now checks all three
  file types per chapter).

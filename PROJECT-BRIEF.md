# StudySapiens — PROJECT BRIEF (handoff doc)

Read this FIRST if you are a fresh AI agent picking up this project.
Last updated: 2026-11-13. Repo: github.com/laibatanzeem/StudySapiens (PRIVATE).
Live preview: https://sswebtesting.netlify.app (auto-deploys from GitHub `main`).
Planned domain: https://www.studysapiens.com (not purchased yet).

## 1. What this project is

Static educational website for Pakistani Punjab-board students, classes 9-12, NEW
PCTB / PECTAA syllabus. Owner is a teacher. Audience = non-native English students.
Contact email: admin.studysapiens@gmail.com

## 2. IRONCLAD RULES (never break these)

1. HONESTY: never publish unverified textbook/board data. Use "Expected" /
   "Uploading soon" labels. Board watcher is DETECT+ALERT only, never auto-publish.
2. LANGUAGE: simple English, short sentences. No em dashes or en dashes anywhere in
   site text. Colons and hyphens are fine.
3. DESIGN: LIGHT MODE ONLY. Body #FAF8F3, cards #FFF, near-black olive header,
   cream boxes. No dark theme, no tuition/tutor feature (removed on purpose,
   never re-add). Highly responsive, professional, HD realistic Pakistani
   photos only.
   BRAND COPY (owner decision 2026-11-13): describe StudySapiens as "Made by
   teachers and verified by subject experts." Do not claim the site is made by
   AI. Remove all public ad/no-ad promises (including "ad-free", "no ads" and
   "no popup ads"). No ad network is currently configured. Any future ad
   integration requires explicit owner approval and a privacy/CSP review.
4. Prefer revealing facts: ECAT/UET aggregate = 17% Matric + 50% FSc + 33% ECAT(400).
   MDCAT aggregate = 10% Matric + 40% FSc + 50% MDCAT; 55% for MBBS, 50% for BDS.
5. Never delete original high-res images; originals live in assets-src/img/.
6. Keep the workspace clean; do not leave scratch files behind.

## 3. How the site is built

    data.py      all content + site config (UPDATES, CHAPTERS, CLASSES, SUBJECTS,
                 BOARDS, FAQs, RESULT_WINDOWS...)
    build.py     ~3150 lines, generates the whole site (~87 pages) into site/
    sync_files.py copies files/ uploads into the build, then runs the precheck gate
    server.py    local dev server (python3 server.py) + /api/contact mock
    scripts/     watch_boards.py, new_update.py, precheck.py, seo_audit.py,
                 anchor_audit.py, e2e_audit.mjs, interactions.mjs
    assets/      css/style.css, js/main.js, img/ (optimized)  <- what ships
    assets-src/  original full-size images (do not ship, do not delete)
    files/       downloadable PDFs (class-10/biology/solutions/ has 10 solved exercises)
    blogs/       blog posts + README-BLOG.txt (AEO/GEO checklist)

Build command:  python3 build.py      (writes ./site/, ~87 pages)
Precheck:       python3 scripts/precheck.py   (exit 1 on critical; also runs
                automatically at the end of sync_files.py)

## 4. Deploy pipeline (the only one we use)

    edit code -> upload to GitHub -> Netlify rebuilds automatically (~60 s)

Netlify settings: build command `python build.py`, publish dir `site`, branch `main`.
The owner uploads files by hand via GitHub web UI (Add file -> Upload files).
Folders must be dragged as folders; the file picker cannot select folders.

## 5. Current state (2026-11-07)

Local commits: 96ce5a5 baseline, a623dd6 optimization, 0a0a51c light hero + merged
header, 21907d9 nav overlap fix + SW ss-v9.

Done and verified:
- 87 pages, full AEO/GEO layer (robots.txt with 11 AI bots, llms.txt, feed.xml,
  37 subject FAQPages, answer boxes, citations).
- Biology 10: 10 solved-exercise PDFs live, verified against PECTAA headers.
  PDFs open IN BROWSER (Content-Disposition: inline in _headers), never "download".
- Board watcher (6/11 sources reachable from sandbox; 4 are geo-blocked to PK, fine).
- Optimization: assets/img 6120KB -> 823KB (-86.5%), home transfer ~435KB,
  WebP + JPEG fallbacks with fixed dimensions (no CLS), lazy below the fold.
- Security: CSP in Report-Only, X-Frame-Options SAMEORIGIN, HSTS, nosniff.
- Brand identity: made by teachers and verified by subject experts; no AI authorship claim or public ad/no-ad promise.
- Smart Syllabus is PECTAA's class-level ALP (deleted topics / exercise questions,
  with pairing schemes and model papers where included), NOT notes and NOT a
  replacement textbook. As of 2026-11-10, link only Grade 9 Notification 1238 and
  Grade 11 Notification 1239 (both 2026-11-06) directly to official PECTAA PDFs.
  Grade 10 and 12 notices are pending. Keep ALP links on the Smart Syllabus page
  and relevant class hubs only; do NOT add ALP cards/links to individual subjects.
- Subject availability is per official textbook: do not list Class 10 Islamiat or
  Class 9 Pakistan Studies (no prescribed books for these classes per owner).
- Pairing schemes uploaded 2026-11-13: 16 PDFs for Grades 9 and 11. Their covers
  say Annual Examination 2026, so store/display them as "StudySapiens reference
  · Annual Exam 2026" only, not as current/official 2027 schemes. Pairing hub
  links current PECTAA 2027 ALP notices 1238 (Grade 9) and 1239 (Grade 11).
  Grade 9 Computer Science and Grade 11 Islamiyat are not listed in those ALP
  notices; their uploaded PDFs are explicitly marked as reference copies.
- Class 10 pairing PDFs added 2026-11-13: Biology, Chemistry, Computer Science,
  English, Mathematics, Pakistan Studies, Physics and Urdu. They are StudySapiens-
  prepared summaries for Annual Exam 2027, not original PECTAA PDFs. Each subject
  page and pairing hub labels them accordingly. Mark arithmetic checked; no content
  corrections found in the 8 supplied files. Tarjuma-tul-Quran not supplied yet.
- Class 10 pairing-scheme PDFs uploaded 2026-11-13 (8 core subjects) are
  StudySapiens-prepared summaries for the 2026-27 session / Annual Exam 2027.
  Label them "StudySapiens summary · 2027"; do not call them original PECTAA PDFs.
  Totals/question distributions were checked against published paper-setter
  instruction transcriptions. One Class 10 scheme (Tarjuma-tul-Quran) was not
  included in this batch.
- Pairing scheme PDFs uploaded 2026-11-13 are historical StudySapiens reference
  copies. Their covers label Annual Examination 2026. Display them as "2026
  reference" only; never label them official/current for 2027. Pairing hub links
  current PECTAA 2027 notices separately. Grade 9 Computer Science and Grade 11
  Islamiyat are outside the current ALP notice subject sets; keep that explicit.
- For chapter-based subjects, chapter exercise PDFs appear in chapter cards. The
  separate Exercise Solutions category must say the chapter files are available
  above, not "Uploading soon", when matching chapter solution files exist.
  Official links: pectaa.edu.pk/wp-content/uploads/2026/11/ALP-9-Notification-06.11.2026-F.pdf
  and pectaa.edu.pk/wp-content/uploads/2026/11/ALP-Notification-Grade-11.pdf.
- Home: light cream hero + ONE merged header (old duplicate subnav bar deleted).
  Header links (12): Classes mega, Smart Syllabus, Pairing, Guess Papers,
  Past Papers, Date Sheet, Results, Online Tests, MDCAT, CSS, eBooks, Blog.
  "Home" = logo link. "Updates" = the news ticker above the header.
  Mobile: below 1240px the links collapse into the hamburger drawer.

PENDING (owner decisions, do not do these unasked):
- Form backend (forms are mailto only today; nothing is stored anywhere).
- 10 title-length warnings (68-80 rendered chars) - needs owner approval to trim.
- Chemistry 10 chapter-slots Ch14-26 still empty (no verified files).
- CSP move from Report-Only to enforced (after a clean-console period).
- Font self-hosting (currently Google Fonts).
- Domain purchase + DNS pointing to Netlify.

## 6. Traps that have already bitten us

1. SERVICE WORKER CACHE: any change to CSS/JS requires bumping the SW version in
   build.py (currently `ss-v9`). Otherwise returning visitors mix old CSS with new
   HTML and report "bugs" that are pure stale cache. Also tell the owner to press
   Ctrl+Shift+R once after a deploy.
2. HEADER GEOMETRY: .nav-wrap is `grid-template-columns:1fr auto 1fr`. The center
   nav can grow past its 1fr track and slide under the search pill on wide screens.
   Current guard: compact nav font .74rem / padding .26rem, search pill 142px wide,
   nav hides at max-width 1240px. Any new nav item MUST be re-tested at
   1241 / 1280 / 1366 / 1440 / 1920 px (measure the pixel gap, do not eyeball).
3. CONTRAST: run the empirical scanner, do not trust manual math. Approved small-text
   colors on cream: #5A5D49, #5F6249, #1E4620 (badges), var(--navy-900).
4. NO EM DASHES in generated text. build.py source uses \u2014 escapes where needed.
5. Editing with heredoc scripts: \n inside a triple-quoted match string becomes a
   real newline and breaks the match; trailing spaces cause silent count=0 asserts.
   Always assert the occurrence count before replacing.
6. `node --check /dev/stdin` fails in this sandbox; check real files only.
7. Playwright is not preinstalled: apt-get the lib list, npm i playwright,
   npx playwright install chromium, keep test scripts in /tmp, serve site/ on
   http://127.0.0.1:8123. Never pkill a pattern that matches your own command line.

## 7. How to make a content change safely

1. Edit data.py (content) or build.py (layout/logic) - never hand-edit site/.
2. python3 build.py  -> must print 87 pages.
3. python3 scripts/precheck.py -> must print SAFE TO DEPLOY.
4. Visual check with Playwright screenshots (desktop 1440 + mobile 390).
5. If CSS/JS changed: bump SW version string in build.py.
6. Commit locally, then tell the owner exactly which files to upload on GitHub.

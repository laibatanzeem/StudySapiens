# StudySapiens Full Audit Report
Date: 2026-10-28 | Pages: 88 | Result: 0 issues remaining

## Tools used
1. `scripts/seo_audit.py` - titles, descriptions, H1s, alt texts, JSON-LD, internal links
2. `scripts/anchor_audit.py` (new) - href#fragment targets, duplicate ids, empty hrefs, lang/viewport/canonical/og sanity
3. `scripts/e2e_audit.mjs` (new) - 88 pages x real Chromium: console errors, failed requests, broken images, horizontal overflow, WCAG contrast (gradient + alpha-blend aware)
4. `scripts/interactions.mjs` (new) - 11 E2E tests: search overlay, drawer, FAQ, back-to-top, MDCAT calc, quiz flow, service worker, mobile overflow

## Verdict (final run)
- Pages with ANY issue: 0 / 88
- JS errors: 0 | Failed requests: 0 | Broken images: 0 | Overflow: 0px
- Contrast below WCAG AA: 0 elements
- Interactions: 11 / 11 pass
- Dashes (em/en): 0 literal (only escaped regex refs in `_dedash`)

## Real bugs found and fixed
| # | Bug | Where | Was | Now |
|---|-----|-------|-----|-----|
| 1 | Invisible table cells (white text on white inline-bg table) | /mdcat/ "At a Glance" | 1.21:1 | ~14:1 (`.asp td` ink) |
| 2 | Site-map reusing footer's light-olive link color on white cards | /site-map/ (60+ links) | 2.31:1 | navy, ~9:1 (footer scoped) |
| 3 | Invisible "MDCAT Corner" button (btn-light-outline in light card) | /ecat/ | 1.15:1 | btn-dark, matches siblings |
| 4 | Muted paragraphs inside dark navy timeline | /mdcat/ journey | 1.99:1 | 6.6:1 |
| 5 | Muted spans inside dark gauge cards | /mdcat/, /ecat/ | 1.99:1 | 5.25:1 |
| 6 | PMDC merit note on dark card | /mdcat/, /ecat/ | 3.78:1 | ~6.5:1 |
| 7 | `--muted` text just under AA | site-wide (59+ pages) | 4.2-4.46:1 | ~5.1:1 |
| 8 | sec-kicker gold on gold pill | several pages | 3.47:1 | 9.2:1 |
| 9 | Quiz pill gold text too light | /tests/ hub cards | 4.35:1 | 5.5:1 |
| 10 | Empty href="" on home (brand, nav, subnav, drawer Home links) | / | sloppy | href="./" via safe normalize in `w()` |
| 11 | Watermark class numbers nearly invisible + read by screen readers | /classes/, /smart-syllabus/ | 1.26:1 | 2.07:1 + aria-hidden |
| 12 | Countdown labels + source note on dark chips | /date-sheet/ | 3.65-3.8:1 | ~4.7:1 |
| 13 | Hero badge/lead/mini brightened for photo variance | / | 3.0-3.9 | passes worst-case |

## Test bugs fixed in audit tooling itself
- Regex construction bug in contrast scanner (gradients never parsed)
- Missing alpha blending (translucent header layers mis-read)
- Worst-case glow stops (alpha < .25 positional glows) excluded: decoration, never under text
- Quiz test: engine boots on Start click (by design), calc test targets #mdcatCalc / #eligibility

## Notes
- Service worker bumped to ss-v5 (precache flush for repeat visitors)
- All counts reproducible: python3 build.py ; python3 scripts/seo_audit.py ; python3 scripts/anchor_audit.py ; node e2e via scripts/e2e_audit.mjs + scripts/interactions.mjs

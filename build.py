# -*- coding: utf-8 -*-
"""
==================================================================
 StudySapiens. Static site generator
 Run:   python3 build.py
 Out:   ./site/   (upload this folder to any web host)
==================================================================
"""
import os, json, re, shutil, html, datetime, subprocess
from data import (SITE, CLASSES, SUBJECTS, SUBJECT_ORDER, SUBJECT_INFO, FILE_CATEGORIES,
                  SUBJECT_CLASSES, NUMERICAL_SUBJECTS, RESULT_WINDOWS, ECAT, CHAPTERS, CHAPTER_CATS,
                  EXTRA_CATEGORIES, BOARDS, UPDATES, FAQS, MDCAT, CSS_EXAM, CONTACT_TOPICS)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
DOM = SITE["domain"]
EMAIL = SITE["email"]
YEAR = datetime.date.today().year
URLS = []          # (path, priority, changefreq)
SEARCH = []        # search index entries

# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def w(path, content, priority=None, changefreq="weekly"):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if 'href=""' in content:
        content = content.replace('href=""', 'href="./"')
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    if priority:
        URLS.append((path.replace("index.html", "").replace("//", "/"), priority, changefreq))

def rel(depth): return "../" * depth

def esc(s): return html.escape(str(s), quote=True)

# ------------------------------------------------------------------
# FILE UPLOADS. Drop PDF/DOC files into  files/class-<9-12>/<subject>/<category>/
# They are auto-listed on the matching subject page & resource hubs. See README.
# ------------------------------------------------------------------
FILES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
FILE_EXT = {".pdf": "PDF", ".doc": "DOC", ".docx": "DOCX", ".zip": "ZIP", ".ppt": "PPT", ".pptx": "PPTX"}
FILES = {}   # filled by scan_files() in main()

def subjects_for(cid):
    """subjects that actually exist for a class (boards notify subject sets class by class)"""
    return [s for s in SUBJECT_ORDER if cid in SUBJECT_CLASSES.get(s, ("9", "10", "11", "12"))]

def pretty_label(stem):
    t = re.sub(r"[-_]+", " ", stem).strip()
    t = re.sub(r"\s+", " ", t).title()
    t = t.replace("Mcqs", "MCQs").replace("Mcq", "MCQ")
    t = re.sub(r"\b(\d+)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), t)
    return t

CH_RE = re.compile(r"(?i)(?:^|[^a-z0-9])(?:ch|chapter|unit|surah)[\s._-]?(\d{1,2})(?!\d)")

def chapter_of(stem):
    """Chapter number from a file name, e.g. ..._Ch14_... or chapter-14-...."""
    m = CH_RE.search(stem)
    return int(m.group(1)) if m else None

def chapter_file_label(label, num, fallback):
    """Short row label inside a chapter card: drop brand/class/subject/chapter tokens."""
    t = re.sub(r"(?i)\bstudysapiens\b", "", label)
    t = re.sub(r"(?i)\b\d{1,2}(st|nd|rd|th)\b", "", t)
    t = re.sub(r"(?i)\b(?:ch|chapter|unit|surah)\s?\d{1,2}\b", "", t)
    t = re.sub(r"(?i)\b(chem|chemist|phys|phy|bio|math|maths|comp|cs|eng|isl|tarjuma|quran)\w*\b", "", t)
    t = re.sub(r"(?i)\b(?:pak\s?studies|mutalia)\b", "", t)
    t = re.sub(r"[-_]+", " ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" -")
    return t if len(t) >= 3 else fallback

def _minify_js(js):
    """Conservative JS minify: strips /* */ and full-line // comments, trailing
    whitespace and blank lines. String-aware (handles ' and " + escapes); never
    touches regex literals or string contents. Verified with node --check by caller."""
    out, i, n = [], 0, len(js)
    quote = None
    while i < n:
        ch = js[i]
        if quote:
            out.append(ch)
            if ch == "\\":
                if i + 1 < n: out.append(js[i + 1]); i += 2; continue
            elif ch == quote:
                quote = None
            i += 1; continue
        if ch in ("'", '"'):
            quote = ch; out.append(ch); i += 1; continue
        if ch == "/" and i + 1 < n and js[i + 1] == "*":
            j = js.find("*/", i + 2)
            if j < 0: raise ValueError("unterminated block comment")
            i = j + 2; continue
        if ch == "/" and i + 1 < n and js[i + 1] == "/":
            j = js.find("\n", i + 2)
            if j < 0: break
            i = j; continue
        out.append(ch); i += 1
    lines = [ln.rstrip() for ln in "".join(out).split("\n")]
    lines = [ln for ln in lines if ln.strip()]
    return "\n".join(lines) + "\n"

def fmt_size(n):
    return f"{n/1048576:.1f} MB" if n >= 1048576 else f"{max(1, n // 1024)} KB"

def scan_files():
    """files/ → {(cid, sid): {category: [{label, url, size, ext}]}}"""
    out = {}
    if not os.path.isdir(FILES_ROOT):
        return out
    for cls_dir in sorted(os.listdir(FILES_ROOT)):
        m = re.fullmatch(r"class-(9|10|11|12)", cls_dir)
        if not m:
            continue
        cid = m.group(1)
        for sid in sorted(os.listdir(os.path.join(FILES_ROOT, cls_dir))):
            if sid not in SUBJECTS:
                continue
            for cat in sorted(os.listdir(os.path.join(FILES_ROOT, cls_dir, sid))):
                cat_p = os.path.join(FILES_ROOT, cls_dir, sid, cat)
                if not os.path.isdir(cat_p):
                    continue
                for fn in sorted(os.listdir(cat_p)):
                    ext = os.path.splitext(fn)[1].lower()
                    if ext not in FILE_EXT:
                        continue
                    if (cat == "scheme" and "studySapiens-reference-alp-pairing-scheme-annual-exam-2026".lower() in fn.lower()):
                        file_label = "StudySapiens reference scheme · Annual Exam 2026"
                    elif cat == "scheme" and fn.startswith("StudySapiens_Pairing-Scheme_2026-27_Grade10_"):
                        file_label = "StudySapiens scheme summary · Annual Exam 2027"
                    else:
                        file_label = pretty_label(os.path.splitext(fn)[0])
                    out.setdefault((cid, sid), {}).setdefault(cat, []).append({
                        "label": file_label,
                        "ch": chapter_of(os.path.splitext(fn)[0]),
                        "url": f"files/{cls_dir}/{sid}/{cat}/{fn}",
                        "size": os.path.getsize(os.path.join(cat_p, fn)),
                        "ext": FILE_EXT[ext]})
    return out

def file_count(cid=None, sid=None, cat=None):
    n = 0
    for (c, s), cats in FILES.items():
        if cid and c != cid: continue
        if sid and s != sid: continue
        for k, v in cats.items():
            if cat and k != cat: continue
            n += len(v)
    return n

def file_rows(R, cid, sid, cat):
    """Download rows for one category of one subject (empty string if none)."""
    return dl_rows(R, FILES.get((cid, sid), {}).get(cat, []))

def dl_rows(R, files):
    rows = ""
    for f in files:
        rows += (f'<a class="file-row" href="{R}{f["url"]}" target="_blank" rel="noopener">'
                 f'<span class="file-ic">{icon("external", 15)}</span>'
                 f'<span class="file-tx"><b>{esc(f["label"])}</b>'
                 f'<span class="file-meta">{f["ext"]} • {fmt_size(f["size"])}</span></span>'
                 f'<span class="file-btn">Open</span></a>')
    return rows

# ------------------------------------------------------------------
# EXTRA file trees: files/formulas/class-N/<subject>/, files/english/<topic>/
# (copied to site/ automatically with the rest of FILES_ROOT)
# ------------------------------------------------------------------
EXTRA_FILES = {}   # {(top, rel_dir): [files]} ? filled by scan_extra() in main()

def scan_extra():
    out = {}
    for top in ("formulas", "english"):
        top_p = os.path.join(FILES_ROOT, top)
        if not os.path.isdir(top_p):
            continue
        for dirpath, _dirs, fns in os.walk(top_p):
            rel = os.path.relpath(dirpath, top_p)
            rel = "" if rel == "." else rel.replace(os.sep, "/")
            for fn in sorted(fns):
                ext = os.path.splitext(fn)[1].lower()
                if ext not in FILE_EXT:
                    continue
                out.setdefault((top, rel), []).append({
                    "label": pretty_label(os.path.splitext(fn)[0]),
                    "url": f"files/{top}/{(rel + '/') if rel else ''}{fn}",
                    "size": os.path.getsize(os.path.join(dirpath, fn)),
                    "ext": FILE_EXT[ext]})
    return out

def extra_rows(R, top, rel):
    return dl_rows(R, EXTRA_FILES.get((top, rel), []))

def extra_count():
    return sum(len(v) for v in EXTRA_FILES.values())

def slot_html(hue, ic, title, sub, rows, request_subject):
    """one labelled upload slot (live rows or honest placeholder)"""
    live = f'<span class="badge badge-new" style="margin-left:auto">live</span>' if rows else ''
    inner = rows if rows else (f'<div class="file-empty">{icon("clock",15)} <span><b>Uploading soon.</b> Being prepared by teachers right now. '
                               f'<a href="mailto:{EMAIL}?subject={request_subject}">Email us and we\'ll send it to you first</a>.</span></div>')
    return f'''
<div class="file-slot reveal">
  <div class="file-slot-head"><span class="file-slot-ic" style="background:{hue}">{icon(ic,17)}</span>
    <div><b>{title}</b><span>{sub}</span></div>{live}</div>
  {inner}
</div>'''

# ------------------------------------------------------------------
# ICONS (inline SVG, stroke style)
# ------------------------------------------------------------------
_IC = {
 "atom": '<circle cx="12" cy="12" r="2.2"/><ellipse cx="12" cy="12" rx="9" ry="3.6"/><ellipse cx="12" cy="12" rx="9" ry="3.6" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.6" transform="rotate(120 12 12)"/>',
 "flask": '<path d="M9 3h6M10 3v5.2L4.7 17a2 2 0 001.8 3h11a2 2 0 001.8-3L14 8.2V3"/><path d="M7.5 14h9"/>',
 "dna": '<path d="M7 3c0 5 10 5 10 10S7 18 7 21M17 3c0 5-10 5-10 10s10 5 10 10M8 5.5h8M8 18.5h8M9.5 8.5h5M9.5 15.5h5"/>',
 "sigma": '<path d="M17 6V5H7l6 7-6 7h10v-1"/>',
 "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M4 9h2M4 15h2M18 9h2M18 15h2M9 4v2M15 4v2M9 18v2M15 18v2"/>',
 "book": '<path d="M4 5.5A2.5 2.5 0 016.5 3H20v15H6.5A2.5 2.5 0 004 20.5z"/><path d="M4 20.5A2.5 2.5 0 016.5 18H20"/><path d="M9 7.5h7"/>',
 "chevron": '<path d="M6 9l6 6 6-6"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "close": '<path d="M6 6l12 12M18 6L6 18"/>',
 "download": '<path d="M12 4v11m0 0l-4-4m4 4l4-4M5 20h14"/>',
 "arrow": '<path d="M4 12h16m-6-6l6 6-6 6"/>',
 "check": '<path d="M4 12.5l5 5L20 6.5"/>',
 "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
 "cal": '<rect x="4" y="5.5" width="16" height="15" rx="2.5"/><path d="M8 3.5v4M16 3.5v4M4 10.5h16"/>',
 "doc": '<path d="M6 3h8l4 4v13a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z"/><path d="M13 3v5h5M9 12h6M9 16h6"/>',
 "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8L3.5 9.7l5.9-.8z"/>',
 "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9z"/>',
 "print": '<path d="M7 8V3h10v5"/><rect x="4" y="8" width="16" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 6 8.5-6"/>',
 "whatsapp": '<path d="M12 3.5a8.5 8.5 0 00-7.3 12.8L3.5 20.5l4.4-1.1A8.5 8.5 0 1012 3.5z"/><path d="M9 8.8c0 3.6 2.6 6.2 6.2 6.2l1.3-1.5-2-1.2-.9.7a4.8 4.8 0 01-2.6-2.6l.7-.9-1.2-2z"/>',
 "facebook": '<path d="M14 8h2V5h-2.5A3.5 3.5 0 0010 8.5V11H8v3h2v7h3v-7h2.5l.5-3H13V9a1 1 0 011-1z"/>',
 "xicon": '<path d="M4 4l16 16M20 4L4 20"/>',
 "bookmark": '<path d="M6.5 3.5h11a1 1 0 011 1V21l-6.5-4.2L5.5 21V4.5a1 1 0 011-1z"/>',
 "sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4M12 19.1v2.4M4.3 4.3l1.7 1.7M18 18l1.7 1.7M2.5 12h2.4M19.1 12h2.4M4.3 19.7L6 18M18 6l1.7-1.7"/>',
 "moon": '<path d="M20.4 14.2A8.5 8.5 0 019.8 3.6a8.5 8.5 0 1010.6 10.6z"/>',
 "trash": '<path d="M4 7h16M9.5 7V4.5h5V7M6.5 7l1 13.5h9l1-13.5M10 11v5.5M14 11v5.5"/>',
 "link": '<path d="M9 15l6-6M10.5 6.5l1.4-1.4a4 4 0 015.7 5.7l-1.5 1.4M13.5 17.5l-1.4 1.4a4 4 0 01-5.7-5.7l1.5-1.4"/>',
 "cap": '<path d="M2.5 9L12 4.5 21.5 9 12 13.5z"/><path d="M6.5 11v4.5c0 1.4 2.5 3 5.5 3s5.5-1.6 5.5-3V11M21.5 9v5"/>',
 "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13.5l9 5 9-5M3 17.5l9 5 9-5"/>',
 "shield": '<path d="M12 3l7.5 2.8v5.4c0 4.6-3.2 8-7.5 9.8-4.3-1.8-7.5-5.2-7.5-9.8V5.8z"/><path d="M9 12l2 2 4-4"/>',
 "zap": '<path d="M13 2L4 14h6l-1 8 9-12h-6z"/>',
 "calc": '<rect x="5" y="3" width="14" height="18" rx="2.4"/><path d="M8.5 7h7M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 15.5h.01M12 15.5h.01M15.5 15.5h.01"/>',
 "refresh": '<path d="M20 12a8 8 0 11-2.3-5.6M20 3v4h-4"/>',
 "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 014 19V8a1.5 1.5 0 011.5-1.5h5"/>',
 "bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.7 10.7c.7.6 1.2 1.4 1.2 2.3h5c0-.9.5-1.7 1.2-2.3A6 6 0 0012 3z"/>',
 "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4"/>',
 "money": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v10M15 9.3c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .8-3 2.1s1.1 1.9 3 2.2 3 .9 3 2.2-1.3 2.1-3 2.1c-1.3 0-2.4-.5-3-1.5"/>',
 "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c.5-3.2 2.8-5 5.5-5s5 1.8 5.5 5M15.5 5.4a3.2 3.2 0 010 5.6M17 15.4c2 .6 3.2 2.2 3.5 4.6"/>',
 "flag": '<path d="M6 21V4"/><path d="M6 4.5c4-2 8 2 12 0v9c-4 2-8-2-12 0"/>',
 "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.3 3.9 5.2 3.9 8.5s-1.3 6.2-3.9 8.5c-2.6-2.3-3.9-5.2-3.9-8.5s1.3-6.2 3.9-8.5z"/>',
 "leaf": '<path d="M5 19C5 9 11 4 20 4c0 9-5 15-15 15z"/><path d="M5 19c3-5 7-9 11-11"/>',
 "phone": '<path d="M5 4h4l1.5 4.5L8 10a12 12 0 006 6l1.5-2.5L20 15v4a2 2 0 01-2.2 2A15.5 15.5 0 013 6.2 2 2 0 015 4z"/>',
 "bell": '<path d="M6 9a6 6 0 0112 0c0 5 2 6.5 2 6.5H4S6 14 6 9z"/><path d="M10 19a2 2 0 004 0"/>',
 "grid": '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
 "home": '<path d="M4 11l8-7 8 7v9a1.5 1.5 0 01-1.5 1.5h-13A1.5 1.5 0 014 20z"/><path d="M9.5 21v-7h5v7"/>',
 "trophy": '<path d="M8 4h8v5a4 4 0 01-8 0z"/><path d="M8 4H4.5a3.5 3.5 0 003.6 4M16 4h3.5a3.5 3.5 0 01-3.6 4M12 13v3M8.5 20h7M10 16.5h4"/>',
 "notes": '<path d="M5 4h11l3 3v13H5z"/><path d="M15 4v4h4M8 11h8M8 15h5"/>',
 "shieldx": '<path d="M12 3l7.5 2.8v5.4c0 4.6-3.2 8-7.5 9.8-4.3-1.8-7.5-5.2-7.5-9.8V5.8z"/><path d="M9.5 9.5l5 5M14.5 9.5l-5 5"/>',
 "teacher": '<circle cx="12" cy="7.5" r="3.2"/><path d="M6 20.5c.6-3.4 3-5.2 6-5.2s5.4 1.8 6 5.2"/><path d="M3 9.5l4.5-1.5v5L3 11.5zM21 9.5l-4.5-1.5v5l4.5-1.5z"/>',
}
def icon(name, size=20, cls=""):
    body = _IC.get(name, _IC["doc"])
    return (f'<svg class="svg {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')

# ------------------------------------------------------------------
# shared chrome
# ------------------------------------------------------------------
def gtag_jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'

NAV_ITEMS = [
    ("home", "Home", ""),
    ("classes", "Classes", "classes/"),
    ("smart", "Smart Syllabus \u2726", "smart-syllabus/"),
    ("pairing", "Pairing Scheme", "pairing-scheme/"),
    ("guess", "Guess Papers", "guess-papers/"),
    ("past", "Past Papers", "past-papers/"),
    ("datesheet", "Date Sheet", "date-sheet/"),
    ("results", "Results", "results/"),
    ("tests", "Online Tests", "tests/"),
    ("mdcat", "MDCAT", "mdcat/"),
    ("css", "CSS", "css/"),
    ("ebooks", "eBooks", "ebooks/"),
    ("blog", "Blog", "blog/"),
]

def ticker_html(R):
    items = "".join(
        f'<a href="{R}updates/{p["slug"]}/"><span class="dot">✦</span> {esc(p["title"])}</a>' for p in UPDATES)
    return (f'<div class="ticker"><div class="container">'
            f'<span class="ticker-label">{icon("bell",12)} Updates</span>'
            f'<div style="overflow:hidden;flex:1"><div class="ticker-track">{items}{items}</div></div></div></div>')

def mega_menu(R):
    cols = ""
    for cid, c in CLASSES.items():
        links = "".join(
            f'<li><a href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a></li>' for s in subjects_for(cid))
        cols += (f'<div class="mega-col"><span class="badge badge-gold">New Syllabus {c["session"]}</span>'
                 f'<h4>{c["name"]} <span class="muted small">· {c["level"]}</span></h4>'
                 f'<ul>{links}</ul>'
                 f'<a class="view-all" href="{R}classes/{cid}/">All subjects {icon("arrow",13)}</a></div>')
    return cols

def header_html(R, page_key):
    nav = ""
    nav += (f'<li class="has-mega"><button class="nav-btn" data-nav="classes" type="button">Classes '
            f'<svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg></button>'
            f'<div class="mega"><div class="mega-grid">{mega_menu(R)}</div></div></li>')
    for key, label, path in NAV_ITEMS[2:]:
        nav += f'<li><a href="{R}{path}" data-nav="{key}">{label}</a></li>'
    return f"""
<header class="site-header" id="site-header">
  <div class="container nav-wrap">
    <a class="brand" href="{R}" aria-label="StudySapiens home">
      <img src="{R}assets/img/logo-trim-light.png" alt="StudySapiens. New PCTB syllabus notes" width="134" height="44">
    </a>
    <ul class="main-nav">{nav}</ul>
    <div class="header-actions">
      <button class="search-bar" data-open-search aria-label="Search website">{icon("search",15)}<span class="sb-txt">Search notes...</span></button>
      <button class="icon-btn search-icon" data-open-search aria-label="Search website">{icon("search",19)}</button>
      <button class="icon-btn menu-toggle" data-open-drawer aria-label="Open menu">{icon("menu",21)}</button>
    </div>
  </div>
</header>"""

def drawer_html(R):
    cls_subs = ""
    for cid in CLASSES:
        links = "".join(f'<li><a href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a></li>' for s in subjects_for(cid))
        cls_subs += (f'<li><button class="d-btn" type="button">{CLASSES[cid]["name"]}'
                     f'<svg class="caret" width="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg></button>'
                     f'<ul class="drawer-sub">{links}<li><a href="{R}classes/{cid}/" style="color:var(--gold-300)">All {CLASSES[cid]["name"]} resources →</a></li></ul></li>')
    main_links = "".join(f'<li><a href="{R}{p}">{l}</a></li>' for l, p in [
        ("Smart Syllabus ✦", "smart-syllabus/"),
        ("Pairing Scheme", "pairing-scheme/"), ("Guess Papers", "guess-papers/"),
        ("Past Papers", "past-papers/"), ("Date Sheet", "date-sheet/"),
        ("Results", "results/"), ("Online Tests", "tests/"),
        ("MDCAT Corner", "mdcat/"), ("ECAT Corner", "ecat/"),
        ("CSS Corner", "css/"), ("eBooks", "ebooks/"), ("Blog", "blog/")])
    more = "".join(f'<li><a href="{R}{p}">{l}</a></li>' for l, p in [
        ("Model Papers", "model-papers/"), ("Formula Sheets", "formulas/"),
        ("English Corner", "english-corner/"), ("Roll Number Slip", "roll-number-slip/"),
        ("Boards: All 9 BISE", "boards/"),
        ("Latest Updates", "updates/"),
        ("About StudySapiens", "about/"), ("Contact Us", "contact/")])
    return f"""
<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer-bg"></div>
  <nav class="drawer-panel" aria-label="Mobile menu">
    <div class="drawer-head">
      <img src="{R}assets/img/logo-trim-light.png" alt="StudySapiens" width="122" height="40" loading="lazy" decoding="async">
      <div style="display:flex;gap:8px;align-items:center">
        <button class="drawer-close" data-close-drawer aria-label="Close menu">{icon("close",18)}</button>
      </div>
    </div>
    <ul class="drawer-nav">
      <li><a href="{R}">Home</a></li>
      <li><button class="d-btn" type="button">Classes
        <svg class="caret" width="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" style="margin-left:auto"><path d="M6 9l6 6 6-6"/></svg></button>
        <ul class="drawer-sub">{cls_subs}</ul></li>
      {main_links}
      {more}
    </ul>
    <div class="drawer-cta">
      <button class="btn btn-light-outline" data-open-search>{icon("search",16)} Search notes & papers</button>
    </div>
    <p class="drawer-note">Made by teachers • verified by subject experts • for Punjab students</p>
  </nav>
</div>"""

def search_overlay():
    return """
<div class="search-overlay" id="searchOverlay" role="dialog" aria-label="Site search">
  <div class="search-box">
    <div class="search-input-row">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <input id="search-input" type="text" placeholder="Search chapters, notes, schemes… (Ctrl+K)" autocomplete="off">
      <span class="search-esc">ESC</span>
    </div>
    <div class="search-results" id="search-results"></div>
  </div>
</div>"""

def footer_html(R):
    subj_links = "".join(
        f'<li><a href="{R}classes/9/{s}/">Class 9 {SUBJECTS[s]["name"]}</a></li>' for s in SUBJECT_ORDER[:3])
    subj_links += "".join(
        f'<li><a href="{R}classes/11/{s}/">1st Year {SUBJECTS[s]["name"]}</a></li>' for s in SUBJECT_ORDER[:3])
    res = "".join(f'<li><a href="{R}{p}">{l}</a></li>' for l, p in [
        ("Smart Syllabus", "smart-syllabus/"),
        ("Pairing Schemes", "pairing-scheme/"), ("Guess Papers", "guess-papers/"),
        ("Past Papers", "past-papers/"), ("Date Sheets", "date-sheet/"),
        ("Results", "results/"), ("Online Tests", "tests/"), ("Model Papers", "model-papers/"),
        ("MDCAT Calculator", "mdcat/#calculator"), ("ECAT Calculator", "ecat/#calculator"),
        ("eBooks (Official)", "ebooks/"),
        ("Latest Updates", "updates/"), ("Site Map", "site-map/")])
    comp = "".join(f'<li><a href="{R}{p}">{l}</a></li>' for l, p in [
        ("About Us", "about/"), ("Contact", "contact/"),
        ("Privacy Policy", "privacy-policy/"), ("MDCAT Corner", "mdcat/"), ("CSS Corner", "css/"), ("Blog", "blog/"),
        ("Formula Sheets", "formulas/"), ("English Corner", "english-corner/"),
        ("Roll Number Slip", "roll-number-slip/"), ("Boards (All 9 BISE)", "boards/")])
    return f"""
<footer class="site-footer">
  <div class="container footer-top">
    <div class="footer-brand">
      <img src="{R}assets/img/logo-trim-light.png" alt="StudySapiens logo" width="140" height="46" loading="lazy" decoding="async">
      <p>Free study material for the new PCTB / PECTAA syllabus. Made by teachers and verified by subject experts.</p>
      <div class="f-contact">
        <a href="mailto:{EMAIL}">{icon("mail",15)} {EMAIL}</a>
        <span>{icon("globe",15)} Serving all 9 BISE boards of Punjab</span>
      </div>
      <div class="socials">
        <a href="mailto:{EMAIL}" aria-label="Email us">{icon("mail",17)}</a>
        <a href="https://wa.me/?text=Assalam-o-Alaikum!%20I%20need%20notes%20from%20StudySapiens" target="_blank" rel="noopener" aria-label="WhatsApp">{icon("whatsapp",17)}</a>
      </div>
    </div>
    <div><h4>Popular Notes</h4><ul class="f-links">{subj_links}</ul></div>
    <div><h4>Exam Resources</h4><ul class="f-links">{res}</ul></div>
    <div><h4>StudySapiens</h4><ul class="f-links">{comp}</ul>
      <div style="margin-top:18px">
        <form data-mailto="{EMAIL}" data-subject="Subscribe. StudySapiens Updates" style="display:flex;gap:8px">
          <input type="email" name="email" required placeholder="Email for updates" style="flex:1;min-width:0;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.06);border-radius:10px;padding:.6rem .8rem;color:#fff;font-size:.85rem">
          <button class="btn btn-primary btn-sm" type="submit">Notify me</button>
        </form>
        <div class="form-success">Opening your email app. Press Send to subscribe ✔</div>
      </div>
    </div>
  </div>
  <div class="container footer-bottom">
    <span>© {YEAR} StudySapiens • Free for every student, forever.</span>
    <span>Not affiliated with PCTB/PECTAA or any BISE. Made with {icon("sparkle",13)} in Pakistan.</span>
  </div>
</footer>
<button id="backToTop" aria-label="Back to top"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 19V5m-6 6l6-6 6 6"/></svg></button>"""

def layout(*, page_key, depth, title, desc, path, body, extra_ld=None, image=None,
           noindex=False, head_extra="", abs_paths=False):
    R = "/" if abs_paths else rel(depth)   # 404.html can be served at ANY depth → absolute paths
    canon = f"{DOM}/{path}"
    ld = extra_ld or []
    ld_script = "\n".join(gtag_jsonld(x) for x in ld)
    og = image or f"{DOM}/assets/img/og-image.jpg"
    robots = ("noindex, follow" if noindex
              else "index, follow, max-image-preview:large, max-snippet:-1")
    global_ld = {"@context": "https://schema.org", "@context_id": None, "@graph": [
        {"@type": "Organization", "@id": f"{DOM}/#org", "name": "StudySapiens",
         "url": f"{DOM}/", "email": SITE["email"],
         "logo": {"@type": "ImageObject", "url": f"{DOM}/assets/img/logo.png", "width": 1020, "height": 562},
         "address": {"@type": "PostalAddress", "addressRegion": "Punjab", "addressCountry": "PK"}},
        {"@type": "WebSite", "@id": f"{DOM}/#website", "url": f"{DOM}/", "name": "StudySapiens",
         "publisher": {"@id": f"{DOM}/#org"}, "inLanguage": "en"},
        {"@type": "WebPage", "@id": f"{canon}#webpage", "url": canon,
         "name": title, "description": desc, "isPartOf": {"@id": f"{DOM}/#website"},
         "inLanguage": "en", "primaryImageOfPage": {"@type": "ImageObject", "url": og}}]}
    base_ld = gtag_jsonld({k: v for k, v in global_ld.items() if k != "@context_id"})
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-5ZRS53MF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<link rel="alternate" type="application/rss+xml" title="StudySapiens Updates" href="{DOM}/feed.xml">
<link rel="alternate" hreflang="en" href="{canon}">
<link rel="alternate" hreflang="x-default" href="{canon}">
<meta name="author" content="StudySapiens">
<meta name="theme-color" content="#2E3324">
<meta property="og:type" content="website">
<meta property="og:site_name" content="StudySapiens">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta property="og:locale" content="en_PK">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="StudySapiens. New PCTB/PECTAA syllabus notes for Class 9-12">
<meta name="twitter:image:alt" content="StudySapiens. New syllabus notes for Class 9-12, Punjab boards">
<link rel="icon" type="image/png" sizes="64x64" href="{R}assets/img/favicon-64.png">
<link rel="icon" type="image/png" sizes="32x32" href="{R}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{R}assets/img/favicon-180.png">
<link rel="manifest" href="{R}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/css/style.css">
{head_extra}
{base_ld}
{ld_script}
</head>
<body data-page="{page_key}">
<div class="read-progress" id="readProgress"></div>
<a class="skip-link" href="#main">Skip to content</a>
{ticker_html(R)}
{header_html(R, page_key)}
{drawer_html(R)}
{search_overlay()}
<main id="main">
{body}
</main>
{footer_html(R)}
<div style="display:none" id="site-mail">{EMAIL}</div>
<script>window.SITE_ROOT = "{R}";</script>
<script src="{R}assets/js/main.js" defer></script>
</body>
</html>"""

def breadcrumb_json(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                 "item": f"{DOM}/{u}"} for i, (n, u) in enumerate(items)]}

# ------------------------------------------------------------------
# AEO / GEO helpers: answer capsules, FAQ blocks + FAQPage schema
# ------------------------------------------------------------------
def answer_box(question, answer_html, note=""):
    """Direct-answer capsule: question phrased the way students ask it,
    one short honest answer. This is the format answer engines quote."""
    n = f'<p class="ab-note muted">{note}</p>' if note else ""
    return (f'<div class="answer-box reveal">'
            f'<span class="ab-tag">{icon("bulb",13)} Quick Answer</span>'
            f'<p class="ab-q">{esc(question)}</p>'
            f'<p class="ab-a">{answer_html}</p>{n}</div>')


def faq_items_html(faqs):
    return "".join(f"""
<div class="faq-item reveal">
  <button class="faq-q" aria-expanded="false">{esc(q)}<svg class="chev" width="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg></button>
  <div class="faq-a"><p>{a}</p></div>
</div>""" for q, a in faqs)


def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer",
                            "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}}
                           for q, a in faqs]}


def subject_faqs(cid, sid):
    """Honest, evergreen Q&A set for a class x subject page.
    No chapter numbers or syllabus claims unless CHAPTERS has verified data."""
    c, s = CLASSES[cid], SUBJECTS[sid]
    boards = ", ".join(b["short"] for b in BOARDS[:-1]) + f" and {BOARDS[-1]['short']}"
    faqs = [
        (f"Where can I download {c['alt']} {s['name']} notes for the new syllabus?",
         f"Right here on this page, free. Click any file and it opens in your browser to read instantly: the files section above holds "
         f"{c['name']} {s['name']} notes, solved exercises, MCQ bank, guess paper and pairing "
         f"scheme for the new {c['session']} book. Each file goes live only after a teacher "
         f"checks it against the printed book; anything not ready yet is honestly "
         f"labelled &quot;Uploading soon&quot; with a request link."),
        (f"Are {c['alt']} {s['name']} notes the same for all Punjab boards?",
         f"Yes. All nine Punjab boards ({boards}) follow the same PCTB / PECTAA books "
         f"for the {c['session']} session, so one correct set of notes serves every "
         f"board. Only exam dates and roll number slips come from your own board."),
        (f"How should I prepare {c['name']} {s['name']} for the board exam?",
         f"Use one order for every chapter: read the notes, write the solved exercise "
         f"with your own hand, attempt the MCQ bank, then revise with the guess paper "
         f"and pairing scheme in the last month. Written practice every day beats "
         f"hours of only reading."),
    ]
    chaps = CHAPTERS.get((cid, sid))
    if chaps:
        faqs.insert(2, (f"Which chapters are in the new {c['alt']} {s['name']} book?",
            f"The new {c['session']} book runs from Chapter {chaps[0][0]} to Chapter "
            f"{chaps[-1][0]} ({len(chaps)} chapters). The chapter-wise section above "
            f"lists every official chapter title with its own downloads, so you can "
            f"match it against your printed book in one minute."))
    return faqs

def crumbs_html(R, items):
    lis = [f'<li><a href="{R}">{icon("home",13)} Home</a></li>']
    for i, (n, u) in enumerate(items):
        last = i == len(items) - 1
        lis.append(f'<li><span class="sep">›</span>' + (f'<span aria-current="page">{esc(n)}</span>' if last else f'<a href="{R}{u}">{esc(n)}</a>') + '</li>')
    return f'<div class="crumb-bar"><div class="container"><ul class="crumbs">{"".join(lis)}</ul></div></div>'

def page_hero(R, *, badge, title, lead, actions=""):
    return f"""
<section class="page-hero">
  <div class="container">
    {f'<span class="badge badge-gold">{badge}</span>' if badge else ''}
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
    {f'<div class="hero-actions">{actions}</div>' if actions else ''}
  </div>
</section>"""

def crumbs_bar_html(R, items):
    return crumbs_html(R, items)

def share_row():
    return f"""
<div class="share-row no-print">
  <span class="s-lbl">Share with a friend:</span>
  <button class="share-btn" data-share="whatsapp" aria-label="Share on WhatsApp" title="WhatsApp">{icon("whatsapp",16)}</button>
  <button class="share-btn" data-share="facebook" aria-label="Share on Facebook" title="Facebook">{icon("facebook",16)}</button>
  <button class="share-btn" data-share="x" aria-label="Share on X" title="X (Twitter)">{icon("xicon",15)}</button>
  <button class="share-btn" data-share="copy" aria-label="Copy link" title="Copy link">{icon("link",16)}</button>
  <button class="share-btn" data-print aria-label="Print / Save PDF" title="Print / Save as PDF">{icon("print",16)}</button>
</div>"""

def join_updates_form(R, small=False):
    return f"""
<form data-mailto="{EMAIL}" data-subject="Notify me. New content upload" style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center">
  <input type="email" name="email" required placeholder="Your email address"
    style="flex:1;min-width:220px;max-width:340px;border:1.5px solid var(--line);border-radius:12px;padding:.75rem 1rem;font:inherit;background:#fff">
  <button class="btn btn-primary" type="submit">{icon("bell",16)} Notify Me Free</button>
  <div class="form-success" style="width:100%">Opening your email app. Just press Send ✔</div>
</form>"""

# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------
def exam_timer_html(R):
    chips = "".join(f'<button class="et-chip" type="button" data-et-class="{cid}">{c["name"]}</button>'
                    for cid, c in CLASSES.items())
    exams_js = json.dumps({cid: {"date": c["exam_date"], "label": f'{c["name"]} Annual Exams 2027'}
                           for cid, c in CLASSES.items()})
    return f"""
<div class="container">
  <div class="exam-timer reveal" id="examTimer">
    <div class="et-head">
      <span class="et-kicker">{icon("cal",14)} Board Exam Countdown</span>
      <h2 id="etTitle">Annual Exams</h2>
      <p class="et-note" id="etNote"></p>
      <div class="et-chips" role="tablist" aria-label="Choose your class">{chips}</div>
    </div>
    <div class="et-cells" aria-live="polite">
      <div class="et-cell"><span class="et-num" id="etD">00</span><span class="et-lbl">days</span></div>
      <div class="et-cell"><span class="et-num" id="etH">00</span><span class="et-lbl">hours</span></div>
      <div class="et-cell"><span class="et-num" id="etM">00</span><span class="et-lbl">minutes</span></div>
      <div class="et-cell"><span class="et-num" id="etS">00</span><span class="et-lbl">seconds</span></div>
    </div>
    <div class="et-foot">
      <a class="btn btn-primary btn-sm" href="{R}date-sheet/">{icon("cal",14)} See Date Sheet</a>
      <span class="et-src">Expected window from last years' BISE schedules. The official date sheet will replace it here automatically.</span>
    </div>
  </div>
</div>
<script>window.EXAMS = {exams_js};</script>"""

def build_home(posts=None):
    R = ""
    # ---- hero
    classes_cards = ""
    for i, (cid, c) in enumerate(CLASSES.items()):
        chips = "".join(f'<a class="sc" href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a>' for s in subjects_for(cid))
        classes_cards += f"""
<div class="class-card reveal" data-delay="{i}">
  <div class="class-num" aria-hidden="true">{cid.zfill(2)}</div>
  <h3><a href="{R}classes/{cid}/">{c['name']}</a></h3>
  <div class="cls-sub">{c['level']} • {c['book_note']}</div>
  <div class="subject-chips">{chips}</div>
  <div class="class-foot">
    <span class="badge badge-new">{icon("check",11)} {c['first_exam']}</span>
    <a class="c-link" href="{R}classes/{cid}/">Explore class {icon("arrow",15)}</a>
  </div>
</div>"""
    # ---- why us
    features = [
        ("teacher", "Made by Teachers", "Study materials are created by teachers and verified by subject experts against the current printed books."),
        ("flag", "New Syllabus First", "Built for the NEW PCTB/PECTAA books only. Files go live only after matching the printed book. Never old content with a '2026' sticker."),
        ("check", "Verified by Experts", "Subject experts check notes, solutions and MCQ banks against current PCTB/PECTAA books before publication."),
        ("zap", "Simple English", "Written for Pakistani students whose first language is not English. Short sentences, easy words, exam-focused key points."),
        ("calc", "Smart Free Tools", "MDCAT aggregate calculator, downloadable MCQ banks with answer keys, and live exam countdowns. All free."),
        ("zap", "Fast, Even on 3G", "Built for the phone in your pocket. Light pages that open in seconds on patchy connections. Notes on the bus, in the van, anywhere."),
    ]
    feat_html = "".join(f"""
<div class="feature-card reveal" data-delay="{i%3}">
  <div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon(ic,24)}</div>
  <h3>{t}</h3><p>{d}</p>
</div>""" for i, (ic, t, d) in enumerate(features))
    # ---- resources
    res = [
        ("zap", "Smart Syllabus ✦", "Official PECTAA ALP PDFs for Classes 9 and 11. Classes 10 and 12 are awaiting notices.", "smart-syllabus/"),
        ("layers", "Pairing Schemes", "Official & teacher-prepared paper schemes for every class and subject.", "pairing-scheme/"),
        ("target", "Guess Papers", "High-probability questions for annual exams, prepared from board trends.", "guess-papers/"),
        ("doc", "Past Papers", "New-syllabus board papers with clear, printable PDFs. Board-wise.", "past-papers/"),
        ("cal", "Date Sheets", "Expected schedule + official date sheets the moment BISEs announce.", "date-sheet/"),
        ("check", "MCQ Banks", "Chapter-wise MCQ files with answer keys. Download and self-test in minutes.", "classes/"),
        ("notes", "Exercise Solutions", "Step-by-step solved exercises including numericals and derivations (PDF/DOC).", "classes/"),
        ("book", "Full Chapter Notes", "Complete, simple-English notes written from the new printed books.", "classes/"),
        ("trophy", "Board Results", "Expected result dates, SMS codes and official portal links for all 9 boards.", "results/"),
        ("zap", "Online MCQ Tests", "Self-scoring tests right in your browser. Instant result with explained answers.", "tests/"),
        ("calc", "MDCAT Calculator", "50/40/10 aggregate in seconds, with eligibility guidance.", "mdcat/#calculator"),
        ("notes", "Study Blog", "Teacher-written study plans, exam strategy and syllabus explainers in simple English.", "blog/"),
    ]
    res_html = "".join(f"""
<a class="res-card reveal" data-delay="{i%4}" href="{R}{u}">
  <div class="icon-tile" style="background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon(ic,24)}</div>
  <h3>{t}</h3><p>{d}</p>
  <span class="res-link">Open {icon("arrow",14)}</span>
</a>""" for i, (ic, t, d, u) in enumerate(res))
    # ---- updates preview
    ups = ""
    for p in UPDATES[:3]:
        ups += f"""
<article class="update-card reveal">
  <div class="up-top"><span class="badge badge-gold">{esc(p["tag"])}</span>
    <div class="up-date">{icon("clock",13)} {esc(p["date"])}</div>
    <h3><a href="{R}updates/{p['slug']}/">{esc(p["title"])}</a></h3>
  </div>
  <div class="up-body"><p>{esc(p["excerpt"])}</p>
    <a class="read-more" href="{R}updates/{p['slug']}/">Read update {icon("arrow",13)}</a>
  </div>
</article>"""
    blog_section = ""
    if posts:
        bcards = "".join(blog_card(b, R, "reveal") for b in posts[:3])
        blog_section = f"""
<section class="section section-tight">
  <div class="container">
    <div class="sec-head reveal" style="margin-bottom:34px">
      <span class="sec-kicker">{icon("notes",13)} From the Blog</span>
      <h2>Study Guides in Simple English</h2>
      <p>Practical exam tips and syllabus explainers, written and fact checked by teachers.</p>
    </div>
    <div class="grid grid-3">{bcards}</div>
    <div class="center" style="margin-top:28px"><a class="btn btn-outline" href="{R}blog/">Read All Posts {icon("arrow",15)}</a></div>
  </div>
</section>"""
    faqs = "".join(f"""
<div class="faq-item reveal">
  <button class="faq-q" aria-expanded="false">{esc(q)}<svg class="chev" width="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg></button>
  <div class="faq-a">{a}</div>
</div>""" for q, a in FAQS)
    strip = "".join(f'<span class="strip-pill">{icon(SUBJECTS[s]["icon"],15)} {CLASSES[c]["name"]} {SUBJECTS[s]["name"]}</span>'
                    for c in CLASSES for s in subjects_for(c))
    body = f"""
<section class="hero">
  <div class="hero-orb orb-1"></div><div class="hero-orb orb-2"></div>
  <div class="container">
    <div class="reveal-l">
      <span class="hero-badge"><span class="pulse"></span> Note Bank for the NEW PCTB / PECTAA Syllabus</span>
      <h1>Free
        <span class="rotator"><span>Notes</span><span>Pairing Schemes</span><span>Guess Papers</span><span>MCQ Tests</span><span>Notes</span></span><br>
        for Class 9-12, Made <span class="grad">Simple</span>.</h1>
      <p class="lead">Looking for dependable study materials for the new syllabus? StudySapiens is made by teachers and verified by subject experts for Punjab board students. Every file is checked against the printed book, in easy English, and free.</p>
      <div class="hero-ctas">
        <a class="btn btn-primary btn-lg" href="#classes">{icon("cap",18)} Explore Classes</a>
        <a class="btn btn-light-outline btn-lg" href="{R}mdcat/#calculator">{icon("calc",18)} MDCAT Calculator</a>
      </div>
      <div class="hero-mini">
        <span>{icon("check",15)} 100% free</span>
        <span>{icon("teacher",15)} Made by teachers</span>
        <span>{icon("flag",15)} New syllabus only</span>
      </div>
    </div>
    <div class="hero-art reveal-r">
      <picture>
        <source type="image/webp" srcset="{R}assets/img/hero-640.webp 640w, {R}assets/img/hero-900.webp 900w, {R}assets/img/hero-1300.webp 1300w, {R}assets/img/hero-1600.webp 1600w" sizes="(max-width: 900px) 96vw, 52vw">
        <img src="{R}assets/img/hero-1300.jpg" srcset="{R}assets/img/hero-640.jpg 640w, {R}assets/img/hero-900.jpg 900w, {R}assets/img/hero-1300.jpg 1300w, {R}assets/img/hero-1600.jpg 1600w" sizes="(max-width: 900px) 96vw, 52vw" alt="Pakistani students studying with the new PCTB syllabus on StudySapiens" width="960" height="540" fetchpriority="high" decoding="async">
      </picture>
      <div class="float-card fc-1">{icon("check",16)} Verified against printed books</div>
      <div class="float-card fc-2">{icon("teacher",16)} Made by teachers</div>
    </div>
  </div>
</section>
<div class="stats-band">
  <div class="container">
    <div class="stat reveal"><div class="num" data-count="4">0</div><div class="lbl">Classes (9-12)</div></div>
    <div class="stat reveal" data-delay="1"><div class="num" data-count="37">0</div><div class="lbl">Subjects Covered</div></div>
    <div class="stat reveal" data-delay="2"><div class="num" data-count="100" data-suffix="%">0</div><div class="lbl">Free, Forever</div></div>
    <div class="stat reveal" data-delay="3"><div class="num" data-count="9">0</div><div class="lbl">Punjab Boards</div></div>
  </div>
</div>
<div class="subj-strip" aria-hidden="true"><div class="strip-track">{strip}{strip}</div></div>

<section class="section section-tight" style="padding-bottom:0">{exam_timer_html(R)}</section>

<section class="section" id="classes">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("layers",14)} Choose Your Class</span>
      <h2>All Four Classes, All New Books</h2>
      <p>Every major subject, all four classes. Every subject page has a short exam guide plus free notes, solutions and MCQ downloads. New files added on a rolling schedule.</p>
    </div>
    <div class="grid grid-4">{classes_cards}</div>
  </div>
</section>

<section class="section section-navy">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("sparkle",14)} Why StudySapiens</span>
      <h2>Built Because Students Deserve Better</h2>
      <p>Last year we watched students (and teachers!) struggle with the syllabus change. This site is the fix.</p>
    </div>
    <div class="grid grid-3">{feat_html}</div>
  </div>
</section>

<section class="section" id="resources">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("grid",14)} Exam Toolkit</span>
      <h2>Everything You Need, One Click Away</h2>
      <p>Schemes, guess papers, past papers, date sheets, solved exercises and free tests. Organised class-wise.</p>
    </div>
    <div class="grid grid-3">{res_html}</div>
  </div>
</section>

<section class="section section-tight section-gold">
  <div class="container">
    <div class="grid grid-2" style="align-items:center;gap:40px">
      <div class="reveal-l">
        <span class="sec-kicker">{icon("calc",14)} MDCAT Corner</span>
        <h2 style="font-size:clamp(1.6rem,3vw,2.2rem);margin-bottom:12px">Know Your Aggregate Before UHS Tells You</h2>
        <p class="muted" style="margin-bottom:8px">Matric 10% + FSc 40% + MDCAT 50%. Enter your marks and see your exact aggregate, a live breakdown, and whether you clear the 55% MBBS eligibility mark.</p>
        <ul style="margin-bottom:22px;color:var(--ink-soft)">
          <li>{icon("check",15)} Official PMDC pattern: 180 MCQs, no negative marking</li>
          <li>{icon("check",15)} Subject-wise MDCAT syllabus & prep strategy</li>
          <li>{icon("check",15)} Chapter-wise free MCQ practice from our test bank</li>
        </ul>
        <div style="display:flex;gap:12px;flex-wrap:wrap">
          <a class="btn btn-dark" href="{R}mdcat/#calculator">{icon("calc",16)} Calculate My Aggregate</a>
          <a class="btn btn-outline" href="{R}mdcat/">MDCAT Syllabus & Updates</a>
        </div>
      </div>
      <div class="reveal-r">
        <div class="calc-card" style="text-align:center;padding:30px">
          <div style="display:flex;justify-content:center;gap:10px;margin-bottom:18px">
            <span class="badge badge-navy">Matric 10%</span><span class="badge badge-navy">FSc 40%</span><span class="badge badge-gold">MDCAT 50%</span>
          </div>
          <div style="font-family:var(--font-display);font-size:3rem;font-weight:800;color:var(--navy-900);line-height:1" id="homeAggDemo">92.48%</div>
          <div class="muted" style="margin-bottom:16px">typical closing-merit territory. Compute yours</div>
          <div class="quiz-progress"><i style="width:92.4%"></i></div>
          <a class="btn btn-primary btn-sm" href="{R}mdcat/#calculator">Try the live calculator {icon("arrow",14)}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight">
  <div class="container">
    <div class="grid grid-2" style="align-items:center;gap:40px">
      <div class="reveal-l" style="order:2">
        <div class="card" style="padding:32px">
          <h3 style="margin-bottom:14px">{icon("flag",22)} CSS 12-Month Game Plan</h3>
          <div class="timeline">
            <div class="tl-item"><h4>Foundation (Months 1-2)</h4><p>Eligibility check, optional subject selection, daily Dawn habit.</p></div>
            <div class="tl-item"><h4>Core + English (Months 3-6)</h4><p>GSA & Pak Affairs done; weekly essay writing with checking.</p></div>
            <div class="tl-item"><h4>Optionals + MPT (Months 7-9)</h4><p>All optionals finished; pass the MPT screening test.</p></div>
            <div class="tl-item"><h4>Written sprint (Months 10-12)</h4><p>Past papers, timed answers, current-affairs revision.</p></div>
          </div>
        </div>
      </div>
      <div class="reveal-r" style="order:1">
        <span class="sec-kicker">{icon("flag",14)} CSS Corner</span>
        <h2 style="font-size:clamp(1.6rem,3vw,2.2rem);margin-bottom:12px">Dream of the Civil Service? Start Early.</h2>
        <p class="muted" style="margin-bottom:22px">Complete CSS roadmap for Pakistani students: eligibility rules, compulsory & optional subjects with marks, MPT screening guide, recommended books and a realistic 12-month strategy. In plain, simple English.</p>
        <a class="btn btn-dark" href="{R}css/">{icon("flag",16)} Open CSS Guide</a>
      </div>
    </div>
  </div>
</section>

<section class="section section-navy">
  <div class="container">
    <div class="sec-head reveal" style="display:flex;justify-content:space-between;align-items:center;max-width:none;text-align:left;gap:20px;flex-wrap:wrap">
      <div>
        <span class="sec-kicker">{icon("bell",14)} Fresh Updates</span>
        <h2 style="margin-bottom:4px">Academic News & Announcements</h2>
        <p>New books, date sheets, MDCAT & CSS. No rumours, only verified updates.</p>
      </div>
      <a class="btn btn-light-outline" href="{R}updates/">View all updates {icon("arrow",15)}</a>
    </div>
    <div class="grid grid-3">{ups}</div>
  </div>
</section>
{blog_section}
<section class="section section-tight" id="faq">
  <div class="container" style="max-width:860px">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("doc",14)} Good Questions</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    {faqs}
    <div class="card reveal" style="margin-top:26px;text-align:center;padding:28px">
      <h3 style="margin-bottom:8px">{icon("bell",22)} Get new-upload alerts by email</h3>
      <p class="muted" style="margin-bottom:18px;font-size:.93rem">One short email when notes, schemes or date sheets go live. No spam, ever.</p>
      {join_updates_form(R)}
    </div>
  </div>
</section>"""
    ld = [
        {"@context": "https://schema.org", "@type": "EducationalOrganization",
         "name": "StudySapiens", "url": DOM, "logo": f"{DOM}/assets/img/logo.png",
         "email": EMAIL, "description": SITE["description"],
         "address": {"@type": "PostalAddress", "addressCountry": "PK", "addressRegion": "Punjab"}},
        {"@context": "https://schema.org", "@type": "WebSite", "name": "StudySapiens", "url": DOM,
         "potentialAction": {"@type": "SearchAction", "target": f"{DOM}/?q={{query}}", "query-input": "required name=query"}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS]},
    ]
    SEARCH.append({"t": "Home. StudySapiens", "s": "New syllabus notes, schemes & tests", "u": "", "c": "Page", "pop": 1})
    w("index.html", layout(page_key="home", depth=0, title=f"StudySapiens: New PCTB Syllabus Notes, Schemes & Past Papers",
        desc=SITE["description"], path="", body=body, extra_ld=ld,
        head_extra='<link rel="preload" as="image" href="assets/img/hero-1300.webp" imagesrcset="assets/img/hero-640.webp 640w, assets/img/hero-900.webp 900w, assets/img/hero-1300.webp 1300w, assets/img/hero-1600.webp 1600w" imagesizes="(max-width: 900px) 96vw, 52vw" type="image/webp" fetchpriority="high">'), priority="1.0", changefreq="daily")

# ------------------------------------------------------------------
# CLASSES overview
# ------------------------------------------------------------------
def build_classes():
    R = "../"
    cards = ""
    for i, (cid, c) in enumerate(CLASSES.items()):
        chips = "".join(f'<a class="chip" href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a>' for s in subjects_for(cid))
        cards += f"""
<div class="class-card reveal" data-delay="{i}">
  <div class="class-num" aria-hidden="true">{['09','10','11','12'][i]}</div>
  <h3>{c['name']} <span class="badge badge-gold">New {c['session']}</span></h3>
  <div class="cls-sub">{c['level']} • {c['first_exam']}</div>
  <div class="subject-chips" style="margin-top:14px">{chips}</div>
  <div class="class-foot"><span class="badge badge-navy">{len(subjects_for(cid))} subjects</span>{f'<span class="badge badge-new">{icon("check",11)} {file_count(cid)} file(s) live</span>' if file_count(cid) else ''}
  <a class="c-link" href="{R}classes/{cid}/">Open class page {icon("arrow",14)}</a></div>
</div>"""
    body = crumbs_html(R, [("Classes", "classes/")]) + page_hero(R,
        badge="New Syllabus 2025-27",
        title="Classes: Matric & Intermediate",
        lead="Pick your class. Browse every available subject, with a short study guide plus free notes, solved exercises and MCQ downloads uploaded file by file.",
        actions=f'<a class="btn btn-primary" href="{R}pairing-scheme/">{icon("layers",15)} Pairing Schemes</a> <a class="btn btn-light-outline" href="{R}past-papers/">Past Papers</a>')
    body += f'<section class="section"><div class="container"><div class="grid grid-2" style="gap:26px">{cards}</div></div></section>'
    ld = [breadcrumb_json([("Classes", "classes/")])]
    w("classes/index.html", layout(page_key="classes", depth=1,
        title="All Classes (9, 10, 11, 12): New PCTB Syllabus Notes & Resources | StudySapiens",
        desc="Class-wise notes, solved exercises, MCQ tests, pairing schemes, guess and past papers for Classes 9, 10, 11 & 12 following the new PCTB/PECTAA syllabus.",
        path="classes/", body=body, extra_ld=ld), priority="0.9")

ALP_OFFICIAL = {
    "9": {
        "url": "https://pectaa.edu.pk/wp-content/uploads/2026/11/ALP-9-Notification-06.11.2026-F.pdf",
        "notification": "PECTAA/C&C Unit/2026/1238",
    },
    "11": {
        "url": "https://pectaa.edu.pk/wp-content/uploads/2026/11/ALP-Notification-Grade-11.pdf",
        "notification": "PECTAA/C&C Unit/2026/1239",
    },
}
PECTAA_COMPLIANCE_URL = "https://pectaa.edu.pk/curriculum-compliance/"
ALP_CHECKED_DATE = "10 November 2026"

def build_smart_syllabus():
    R = "../"
    cards = ""
    for i, (cid, c) in enumerate(CLASSES.items()):
        notice = ALP_OFFICIAL.get(cid)
        if notice:
            status = '<span class="badge badge-live">Official PECTAA ALP available</span>'
            detail = (f"Official notification {notice['notification']}, dated 6 November 2026. "
                      "For the 2026-27 session and Annual Examination 2027.")
            action = (f'<a class="btn btn-primary btn-sm" href="{notice["url"]}" '
                      f'target="_blank" rel="noopener noreferrer">Open official PECTAA PDF {icon("external",14)}</a>')
        else:
            status = '<span class="badge badge-gold">Awaiting official PECTAA notice</span>'
            detail = (f"PECTAA had not posted a Class {cid} ALP notice as of {ALP_CHECKED_DATE}. "
                      "Until it is published, follow the full textbook syllabus.")
            action = '<span class="muted small">Official PDF link will appear here when published.</span>'
        cards += f"""
<div class="class-card reveal" data-delay="{i}">
  <div class="class-num" aria-hidden="true">{cid.zfill(2)}</div>
  <h3>{c['name']}</h3>
  <div class="cls-sub">{c['level']} · Academic Session 2026-27 · Annual Exam 2027</div>
  <div style="margin:14px 0 8px">{status}</div>
  <p class="muted small">{detail}</p>
  <div class="class-foot">{action}</div>
</div>"""
    body = crumbs_html(R, [("Smart Syllabus", "smart-syllabus/")]) + page_hero(R,
        badge="PECTAA · Accelerated Learning Programme",
        title="Smart Syllabus (ALP): Classes 9 and 11",
        lead="Official PECTAA ALP notices for the 2026-27 session and Annual Examination 2027. Classes 9 and 11 are available. Notices for Classes 10 and 12 are pending.",
        actions=f'<a class="btn btn-primary btn-sm" href="#classes">{icon("layers",15)} Check class status</a>')
    body += f"""
<section class="section section-tight" id="classes">
  <div class="container">
    <div class="card" style="margin-bottom:24px;padding:18px 22px;background:var(--navy-50)">
      <h2 style="font-size:1.15rem;margin:0 0 8px">What does Smart Syllabus mean?</h2>
      <p class="small" style="color:var(--ink-soft);margin-bottom:8px">The Smart Syllabus is PECTAA's official Accelerated Learning Programme (ALP). It lists topics and exercise questions excluded from the regular textbook syllabus. The notification may also include pairing schemes and model papers. It is not a replacement textbook or a separate set of notes.</p>
      <p class="small" style="color:var(--ink-soft);margin:0">Use the official ALP for your class. ALP links are shown at class level only, not on individual subject pages. Check <a href="{PECTAA_COMPLIANCE_URL}" target="_blank" rel="noopener noreferrer">PECTAA Curriculum and Compliance</a> for official updates.</p>
    </div>
    <div class="grid grid-2" style="gap:26px">{cards}</div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Smart Syllabus", "smart-syllabus/")])]
    w("smart-syllabus/index.html", layout(page_key="smart", depth=1,
        title="PECTAA Smart Syllabus (ALP): Classes 9 and 11",
        desc="Official PECTAA ALP PDFs for Classes 9 and 11, Annual Exam 2027. Class 10 and 12 notices are pending.",
        path="smart-syllabus/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "PECTAA Smart Syllabus / ALP", "s": "official class 9 and 11 notices; class 10 and 12 awaiting upload",
                   "u": "smart-syllabus/", "c": "Resource", "pop": 1, "k": "PECTAA smart syllabus ALP reduced syllabus class 9 10 11 12"})

# ------------------------------------------------------------------
# CLASS page
# ------------------------------------------------------------------
def build_class(cid):
    R = "../../"
    c = CLASSES[cid]
    cards = ""
    for i, s in enumerate(subjects_for(cid)):
        nf = file_count(cid, s)
        status = (f'<span>{icon("check",13)} {nf} file(s) live</span>' if nf else
                  f'<span>{icon("clock",13)} uploading soon</span>')
        cards += f"""
<a class="subject-card reveal" data-delay="{i%3}" style="--sc:{SUBJECTS[s]['hue']}" href="{R}classes/{cid}/{s}/">
  <div class="icon-tile">{icon(SUBJECTS[s]['icon'],24)}</div>
  <h3>{SUBJECTS[s]['name']}</h3>
  <div class="sub-meta"><span>{icon("book",13)} study guide + downloads</span>{status}</div>
  <div class="badges"><span class="badge badge-navy">Notes</span><span class="badge badge-navy">Solutions</span><span class="badge badge-navy">MCQ Bank</span><span class="badge badge-navy">Scheme</span></div>
  <span class="s-link">Open {SUBJECTS[s]['name']} page {icon("arrow",14)}</span>
</a>"""
    res = [
        ("Pairing Scheme", f"{R}pairing-scheme/", "layers"), ("Guess Paper", f"{R}guess-papers/", "target"),
        ("Past Papers", f"{R}past-papers/", "doc"), ("Date Sheet", f"{R}date-sheet/", "cal"),
    ]
    res_html = "".join(f'<a class="chip" href="{u}">{icon(ic,14)} {t}. {c["name"]}</a>' for t, u, ic in res)
    body = crumbs_html(R, [("Classes", "classes/"), (c["name"], f"classes/{cid}/")]) + page_hero(R,
        badge=f"New PCTB/PECTAA Syllabus • Session {c['session']}",
        title=f"{c['name']}: Notes, Solutions & Tests ({c['level']})",
        lead=f"All {c['name']} subjects from the new {c['session']} books. Every subject page has a short study guide plus free downloadable notes, solved exercises and MCQ banks. {c['first_exam']}.",
        actions=f'<a class="btn btn-primary btn-sm" href="#subjects">{icon("book",15)} View Subjects</a> <a class="btn btn-light-outline btn-sm" href="{R}pairing-scheme/">Pairing Scheme {cid}th</a>' )
    notice = ALP_OFFICIAL.get(cid)
    if notice:
        alp_status = (f'<span class="badge badge-live">Official PECTAA ALP available</span>'
                      f'<p class="muted small" style="margin:8px 0 12px">Notification {notice["notification"]}, dated 6 November 2026. Applies to Annual Examination 2027.</p>'
                      f'<a class="btn btn-primary btn-sm" href="{notice["url"]}" target="_blank" rel="noopener noreferrer">Open official PECTAA PDF {icon("external",14)}</a>')
    else:
        alp_status = (f'<span class="badge badge-gold">Awaiting official PECTAA notice</span>'
                      f'<p class="muted small" style="margin:8px 0 0">As of {ALP_CHECKED_DATE}, PECTAA has not posted an ALP notice for this class. Follow the full textbook syllabus until an official notice is published.</p>')
    alp_banner = f"""
<section class="section section-tight" style="padding-bottom:0">
  <div class="container"><div class="card" style="padding:18px 22px;background:var(--navy-50)">
    <h2 style="font-size:1.15rem;margin:0 0 10px">Smart Syllabus (ALP) · {c['name']}</h2>
    {alp_status}
    <a class="small" href="{R}smart-syllabus/">Check ALP status for all classes</a>
  </div></div>
</section>"""
    body += alp_banner
    body += f"""
<section class="section section-tight" id="subjects">
  <div class="container">
    <div class="filter-bar" data-scope="#subjects"><span class="fb-label">{icon("zap",13)} Quick links</span> {res_html}
      <span style="margin-left:auto"></span><span class="badge badge-new">{icon("check",11)} every file verified against the printed book</span></div>
    <div class="grid grid-3">{cards}</div>
    <div class="card" style="margin-top:30px;background:var(--gold-100);text-align:center">
      <h3 style="font-size:1.1rem;margin-bottom:6px">{icon("bell",20)} Waiting for a notes file?</h3>
      <p class="muted" style="font-size:.92rem;margin-bottom:14px">All {c['name']} subjects are being uploaded on a rolling schedule. Drop your email and we'll poke you the moment yours is live.</p>
      {join_updates_form(R)}
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Classes", "classes/"), (c["name"], f"classes/{cid}/")])]
    w(f"classes/{cid}/index.html", layout(page_key="classes", depth=2,
        title=f"{c['name']} Notes New Syllabus {c['session']}: All Subjects | StudySapiens",
        desc=f"{c['alt']} {c['level']} notes, solved exercises, MCQ tests, schemes & guess papers. All subjects, new {c['session']} books. Made by teachers, verified by experts.",
        path=f"classes/{cid}/", body=body, extra_ld=ld), priority="0.9")
    SEARCH.append({"t": f"{c['name']}. All Subjects & Notes", "s": f"{c['level']} · {c['session']} · pairing, past papers, tests",
                   "u": f"classes/{cid}/", "c": "Class", "pop": 1, "k": f"{c['alt']} class"})

# ------------------------------------------------------------------
# SUBJECT page
# ------------------------------------------------------------------
# class-level angle paragraphs for subject blogs (safe, evergreen exam guidance)
CLASS_ANGLES = {
    "9":  "Class 9 is your first board exam (SSC-I), and these marks become half of your final matric result. Papers of the new syllabus have an objective (MCQ) part and a subjective part of short and long questions. So you need clear concepts AND written practice, not just reading.",
    "10": "Class 10 completes your matric. Your SSC-II marks combine with Class 9 to form the matric percentage that college admissions and scholarship forms ask for. So this single year's paper deserves a planned, serious effort from month one.",
    "11": "1st year (HSSC-I) is the foundation of your FSc. And of entry tests like MDCAT and ECAT, which are built mostly from FSc books. Intermediate papers are longer than matric ones and questions come in fresh wording, so memorising without understanding does not work here.",
    "12": "2nd year (HSSC-II) carries the heaviest weight in every merit formula. Your FSc marks are 40% of the MDCAT aggregate. Finish syllabus coverage early so the last two months can go fully to revision, timed practice and past-paper style questions.",
}

def build_subject(cid, sid):
    R = "../../../"
    c, s = CLASSES[cid], SUBJECTS[sid]
    info = SUBJECT_INFO[sid]
    sub_faqs = subject_faqs(cid, sid)
    upload_note = ("Every file on this page is checked against the printed new book before it goes live. "
                   "If you ever spot a mismatch, one email fixes it.")

    # ---- short keyword-rich blog (unique per class × subject)
    blog = f"""
<article class="card blog-card reveal" id="guide">
  <h2>{c['name']} {s['name']} Notes: New {c['session']} Syllabus (Free Downloads)</h2>
  <p>Welcome to the cleanest page for <b>{c['alt']} {s['name']}</b> on the internet. This is where we publish free
     <b>{c['name']} {s['name']} notes</b>, <b>solved exercises</b>, <b>MCQ banks</b>, the <b>{c['name']} {s['name']} guess paper</b>
     and the official <b>pairing scheme</b> for the new PCTB/PECTAA {c['session']} syllabus. Valid for all nine Punjab boards
     (Lahore, Gujranwala, Multan, Faisalabad, Rawalpindi, Sargodha, Bahawalpur, DG Khan and Sahiwal).</p>
  <p>{info['about']}</p>
  <p>{CLASS_ANGLES[cid]}</p>
  <h3>What you get on this page</h3>
  <ul>{''.join(f'<li>{x}</li>' for x in info['skills'])}</ul>
  <h3>How toppers study {s['name']}</h3>
  <p>Follow one simple order for every chapter: <b>read the notes → write the solved exercise with your own hand → attempt the MCQ bank →
     revise with the guess paper and pairing scheme</b> before the exam. {info['tip']}</p>
  <p class="muted small" style="margin-top:6px">{icon("shield",13)} {upload_note} Files are added on a rolling schedule through the session.
     Fresh uploads appear in the chapter boxes at the top of this page (chapter by chapter, in order).</p>
</article>"""

    # ---- chapter-wise cards (only when a chapter set exists for this subject)
    chaps = CHAPTERS.get((cid, sid))
    chap_nums = {n for n, _ in chaps} if chaps else set()
    cat_titles = {k: t for k, _i, t, _s in FILE_CATEGORIES}
    chap_section = ""
    if chaps:
        cats_for = [k for k in CHAPTER_CATS if k != "numericals" or sid in NUMERICAL_SUBJECTS]
        sub_names = {"notes": "notes", "solutions": "solved exercise", "mcq": "MCQs", "numericals": "numericals"}
        chap_sub = ", ".join(sub_names[k] for k in cats_for)
        cards = ""
        for num, title in chaps:
            mine = []
            for k in cats_for:
                for f in FILES.get((cid, sid), {}).get(k, []):
                    if f.get("ch") == num:
                        mine.append((k, f))
            mine.sort(key=lambda x: (cats_for.index(x[0]), x[1]["label"]))
            rows = dl_rows(R, [{**f, "label": chapter_file_label(f["label"], num, cat_titles[k])} for k, f in mine])
            t_disp = f"Chapter {num}: {esc(title)}" if title else f"Chapter {num}"
            cards += f"""
<div class="file-slot chap-card reveal">
  <div class="file-slot-head"><span class="chap-no">Ch {num}</span>
    <div><b>{t_disp}</b><span>{chap_sub}</span></div>{f'<span class="badge badge-new" style="margin-left:auto">live</span>' if rows else ''}</div>
  {rows if rows else f'<div class="file-empty compact">{icon("clock",14)} <span>Uploading soon. Goes live after matching the printed book.</span></div>'}
</div>"""
        first_n, last_n = chaps[0][0], chaps[-1][0]
        chap_section = f"""
<section class="section section-tight" id="chapters" style="padding-top:10px">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("book",14)} Chapter-wise files</span>
      <h2>{c['name']} {s['name']}: Chapter {first_n} to {last_n}</h2>
      <p>Every chapter gets its own files: {chap_sub} per chapter. Click to open and read instantly: files appear the moment they pass verification.</p>
    </div>
    <div class="chap-grid">{cards}</div>
  </div>
</section>"""

    # ---- whole-book upload slots (chapter files move into chapter cards above)
    slots = ""
    for cat, ic, t, sub in FILE_CATEGORIES:
        if cat == "numericals" and sid not in NUMERICAL_SUBJECTS:
            continue
        all_items = FILES.get((cid, sid), {}).get(cat, [])
        chapter_items = []
        items = all_items
        if chaps and cat in CHAPTER_CATS:
            chapter_items = [f for f in all_items if f.get("ch") in chap_nums]
            items = [f for f in all_items if f.get("ch") not in chap_nums]
        rows = dl_rows(R, items)
        if rows:
            slot_content = rows
        elif chapter_items:
            n_chapter_files = len(chapter_items)
            file_word = "file is" if n_chapter_files == 1 else "files are"
            slot_content = (
                f'<div class="file-empty">{icon("check",15)} '
                f'<span><b>{n_chapter_files} chapter exercise {file_word} available above.</b> '
                f'Open the chapter cards to find each solution. '
                f'<a href="#chapters">Browse chapter files</a>.</span></div>')
        else:
            slot_content = (
                f'<div class="file-empty">{icon("clock",15)} '
                f'<span><b>Uploading soon.</b> Being prepared by teachers right now. '
                f'<a href="mailto:{EMAIL}">Request this file</a>.</span></div>')
        slot_live = bool(rows or chapter_items)
        slot_badge = '<span class="badge badge-new" style="margin-left:auto">live</span>' if slot_live else ''
        slots += (
            f'\n<div class="file-slot reveal">\n'
            f'  <div class="file-slot-head"><span class="file-slot-ic" style="background:{s["hue"]}">{icon(ic,17)}</span>\n'
            f'    <div><b>{t}</b><span>{sub}</span></div>{slot_badge}</div>\n'
            f'  {slot_content}\n'
            f'</div>\n')
    any_files = file_count(cid, sid) > 0
    live_chip = (f'<span class="badge badge-live">{icon("check",11)} {file_count(cid, sid)} file(s) live</span>' if any_files
                 else f'<span class="badge badge-gold">{icon("clock",11)} uploads in progress</span>')

    body = crumbs_html(R, [("Classes", "classes/"), (c["name"], f"classes/{cid}/"), (s["name"], f"classes/{cid}/{sid}/")])
    body += page_hero(R,
        badge=f"{c['name']} • {c['level']} • New Syllabus {c['session']}",
        title=f"{c['name']} {s['name']}: Notes, Solutions & Downloads",
        lead=f"Free {s['name']} notes, solved exercises, MCQ bank, guess paper and pairing scheme for the new {c['session']} book. Uploaded file by file after teacher verification.",
        actions=f'<a class="btn btn-primary btn-sm" href="{("#chapters" if chaps else "#downloads")}">{icon("doc",15)} View Files</a> <a class="btn btn-light-outline btn-sm" href="#guide">{icon("book",15)} Study Guide</a> <a class="btn btn-light-outline btn-sm" href="{R}ebooks/">{icon("external",15)} Official Book (Free)</a>')
    dl_title = f"Files: {c['name']} {s['name']}" if not chaps else f"Whole-Book Files: {c['name']} {s['name']}"
    dl_mt = "34px"
    body += f"""
{chap_section}
<section class="section section-tight">
  <div class="container" style="max-width:880px">
    {blog}
  </div>
</section>
<section class="section section-tight">
  <div class="container" style="max-width:880px">
    <div style="display:flex;align-items:center;gap:12px;margin:{dl_mt} 0 14px;flex-wrap:wrap">
      <h2 style="font-size:1.35rem;margin:0" id="downloads">{icon("doc",21)} {dl_title}</h2>{live_chip}
    </div>
    <p class="muted" style="margin-bottom:18px;font-size:.94rem">Click any file: it opens right in your browser like a Drive file, no downloading forced. Read online (the PDF viewer can still save a copy if you want one). Missing something? <a href="mailto:{EMAIL}?subject=File%20request%20-%20{c['name']}%20{s['name']}">Request it</a> and it jumps the queue.</p>
    <div class="file-grid">{slots}</div>
    <div class="grid grid-2" style="margin-top:22px">
      <a class="chip" style="justify-content:center" href="{R}pairing-scheme/">{icon("layers",14)} All Pairing Schemes</a>
      <a class="chip" style="justify-content:center" href="{R}guess-papers/">{icon("target",14)} All Guess Papers</a>
      <a class="chip" style="justify-content:center" href="{R}past-papers/">{icon("doc",14)} Past Papers (All Boards)</a>
      <a class="chip" style="justify-content:center" href="{R}date-sheet/">{icon("cal",14)} Date Sheet {c['name']}</a>
    </div>
    {share_row()}
  </div>
</section>
<section class="section section-tight" id="faq" style="padding-top:6px">
  <div class="container" style="max-width:880px">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("bulb",14)} Quick Answers</span>
      <h2 style="font-size:1.5rem">{c['name']} {s['name']}: Questions Students Ask</h2>
    </div>
    {faq_items_html(sub_faqs)}
  </div>
</section>"""
    ld = [breadcrumb_json([("Classes", "classes/"), (c["name"], f"classes/{cid}/"), (s["name"], f"classes/{cid}/{sid}/")]),
          faq_schema(sub_faqs)]
    t_base = f"{c['alt']} {s['name']} Notes & Solutions: New {c['session']} Syllabus"
    if len(t_base) > 66: t_base = f"{c['alt']} {s['name']} Notes: New {c['session']} Syllabus"
    d1 = f"Free {c['alt']} {s['name']} notes, solved exercises, MCQ bank, guess paper & pairing scheme. New PCTB/PECTAA {c['session']} syllabus, all Punjab boards. Open-and-read PDF downloads."
    d2 = f"Free {c['alt']} {s['name']} notes, solved exercises, MCQ bank, guess paper & pairing scheme. New {c['session']} syllabus. Open-and-read PDF downloads."
    w(f"classes/{cid}/{sid}/index.html", layout(page_key="classes", depth=3,
        title=t_base, desc=(d1 if len(d1) <= 160 else d2),
        path=f"classes/{cid}/{sid}/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": f"{c['name']} {s['name']}. Notes, Solutions & Downloads", "s": f"{c['level']} · new {c['session']} syllabus · free PDFs",
                   "u": f"classes/{cid}/{sid}/", "c": "Subject", "pop": 1, "k": f"{c['alt']} {sid} notes solved exercises mcq guess paper pairing scheme pdf"})

def resource_filter(cid_list=True):
    cls = "".join(f'<button class="chip" data-group="cls" data-filter="{k}">{v["name"]}</button>' for k, v in CLASSES.items())
    subs = "".join(f'<button class="chip" data-group="sub" data-filter="{k}">{v["name"]}</button>' for k, v in SUBJECTS.items())
    return (f'<div class="filter-bar" data-scope="#resGrid"><span class="fb-label">Class</span>'
            f'<button class="chip active" data-group="cls" data-filter="all">All</button>{cls}'
            f'<span class="filter-sep"></span><span class="fb-label">Subject</span>'
            f'<button class="chip active" data-group="sub" data-filter="all">All</button>{subs}</div>')


def build_pairing():
    """Custom owner-designed pairing-scheme page: pages/pairing-scheme.html.
    Edit that file and rebuild. (The old generated layout is retired; git history keeps it.)"""
    pages_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
    with open(os.path.join(pages_root, "pairing-scheme.html"), encoding="utf-8") as f:
        w("pairing-scheme/index.html", f.read(), priority="0.85")
    SEARCH.append({"t": "Pairing Schemes: All Classes", "s": "assessment schemes · all subjects · Punjab boards",
                   "u": "pairing-scheme/", "c": "Resource", "pop": 1, "k": "paper scheme assessment combination"})


def build_guess():
    R = "../"
    cards = ""
    for cid in CLASSES:
        exam_year = "2027"
        for sid in subjects_for(cid):
            rows = file_rows(R, cid, sid, "guess")
            status = '<span class="badge badge-live" style="margin-left:6px">✓ live</span>' if rows else '<span class="badge badge-gold" style="margin-left:4px">in preparation</span>'
            cards += f"""
<article class="res-item reveal" data-filter-item data-cls="{cid}" data-sub="{sid}">
  <div class="res-ico" style="background:{SUBJECTS[sid]['hue']}">{icon("target",22)}</div>
  <div><h3>{CLASSES[cid]['name']} {SUBJECTS[sid]['name']} Guess Paper {exam_year}{status}</h3>
    <p>Most-expected MCQs, short & long questions. Prepared from the new book + first board patterns.</p>
    {rows}
  </div>
  <div class="res-cta">{'' if rows else f'''
    <a class="btn btn-ghost btn-sm" href="{R}classes/{cid}/{sid}/">{icon("grid",13)} Subject page</a>
    <a class="btn btn-dark btn-sm" href="mailto:{EMAIL}?subject={cid}th {SUBJECTS[sid]['name']} guess paper. Notify me">{icon("bell",13)} Notify me</a>'''}
  </div>
</article>"""
    body = crumbs_html(R, [("Guess Papers", "guess-papers/")]) + page_hero(R,
        badge="Prepared by Teachers",
        title="Guess Papers: Annual Exams 2027 (New Syllabus)",
        lead="Smart, honest guess papers: built by analysing the new books and the first board papers. Not recycled old-syllabus content. Releasing progressively through the session.",
        actions=f'<a class="btn btn-primary btn-sm" href="#resGrid">{icon("target",15)} Browse Guess Papers</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    {resource_filter()}
    <div class="grid" id="resGrid" style="gap:12px">{cards}
      <div class="card filter-empty" style="display:none;text-align:center">Nothing here yet for that filter. Check another subject.</div>
    </div>
    <div class="grid grid-2" style="margin-top:40px">
      <div class="card">
        <h3 style="margin-bottom:10px">{icon("bulb",22)} How our guess papers are made</h3>
        <ol>
          <li><b>New book SLOs</b>. Every chapter's learning outcomes are listed; questions map to them.</li>
          <li><b>First board papers analysed</b>. The {('2026' )} exams of Class 9 & 11 reveal the boards' questioning style.</li>
          <li><b>Teacher experience</b>. A working teacher separates "frequently asked" from "filler".</li>
          <li><b>Marked free</b>. MCQs, short and long sections labelled by probability, never sold.</li>
        </ol>
      </div>
      <div class="card">
        <h3 style="margin-bottom:10px">{icon("shield",22)} Honest promise (please read)</h3>
        <p class="muted" style="margin-bottom:10px">No guess paper guarantees marks. Anyone claiming that is lying. A guess paper tells you <b>where to aim</b>; the notes and practice on this site do the actual shooting.</p>
        <p class="muted">Use order: <b>Notes → Exercise → MCQ test → Past paper → Guess paper</b>, in that order, for every chapter.</p>
      </div>
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Guess Papers", "guess-papers/")])]
    w("guess-papers/index.html", layout(page_key="guess", depth=1,
        title="Guess Papers 2027: Class 9-12, All Subjects (New Syllabus)",
        desc="Guess papers for the new PCTB syllabus, prepared by teachers. Expected MCQs, short & long questions for Class 9-12, all Punjab boards, free.",
        path="guess-papers/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "Guess Papers 2027: All Classes", "s": "expected questions · all subjects", "u": "guess-papers/",
                   "c": "Resource", "pop": 1, "k": "guess important questions"})

def build_past():
    R = "../"
    boards = "".join(f'<a class="chip" href="{R}boards/{b["slug"]}/">{b["short"]}</a>' for b in BOARDS)
    cards = ""
    live = {"9": "2026", "11": "2026"}
    for cid in CLASSES:
        for sid in subjects_for(cid):
            rows = file_rows(R, cid, sid, "past")
            if cid in live:
                status = f'<span class="badge badge-new">first new-syllabus papers</span>'
                p = f"Annual {live[cid]} papers (all 9 boards, PDF). Being collected & uploaded."
            else:
                status = '<span class="badge badge-gray">first exams 2027</span>'
                p = "New-book papers appear here right after the first annual exam in 2027."
            if rows:
                status = '<span class="badge badge-live">✓ live</span>'
                p = "Official board paper PDFs. Download below."
            cards += f"""
<article class="res-item reveal" data-filter-item data-cls="{cid}" data-sub="{sid}">
  <div class="res-ico" style="background:{SUBJECTS[sid]['hue']}">{icon("doc",22)}</div>
  <div><h3>{CLASSES[cid]['name']} {SUBJECTS[sid]['name']} Past Papers {status}</h3><p>{p}</p>
    {rows}
  </div>
  <div class="res-cta">{'' if rows else f'''
    <a class="btn btn-ghost btn-sm" href="{R}classes/{cid}/{sid}/">{icon("grid",13)} Subject page</a>
    <a class="btn btn-dark btn-sm" href="mailto:{EMAIL}?subject=Past paper request. {cid}th {SUBJECTS[sid]['name']}">{icon("bell",13)} Request</a>'''}
  </div>
</article>"""
    body = crumbs_html(R, [("Past Papers", "past-papers/")]) + page_hero(R,
        badge="Board-wise PDFs",
        title="Past Papers: New Syllabus Board Papers (All 9 BISEs)",
        lead="Real question papers from Lahore, Gujranwala, Multan, Faisalabad, Rawalpindi, Sargodha, Bahawalpur, DG Khan and Sahiwal boards. We only host papers of YOUR syllabus. Old-syllabus papers are archived separately so you never mix them.",
        actions=f'<a class="btn btn-primary btn-sm" href="#resGrid">{icon("doc",15)} Browse Papers</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    <div class="card" style="margin-bottom:22px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("bulb",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Why old papers are still worth solving:</b> for Class 10 & 12 your first new-syllabus exam is in 2027. But many core topics overlap with the old books. Solving the matching questions from 2022-25 papers is smart practice; your subject page points you to the right material.</p>
    </div>
    {resource_filter()}
    <div class="grid" id="resGrid" style="gap:12px">{cards}
      <div class="card filter-empty" style="display:none;text-align:center">No paper set yet for that combination. Try another filter.</div>
    </div>
    <div class="card" style="margin-top:30px">
      <h3 style="margin-bottom:12px">{icon("flag",20)} Boards we cover</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">{boards}</div>
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Past Papers", "past-papers/")])]
    w("past-papers/index.html", layout(page_key="past", depth=1,
        title="Past Papers New Syllabus: Class 9-12, All Punjab Boards (BISE) | StudySapiens",
        desc="Past papers of the new PCTB syllabus for Class 9, 10, 1st & 2nd year. Board-wise PDFs from all 9 Punjab BISE boards, correctly labelled, free.",
        path="past-papers/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "Past Papers: All Boards", "s": "new syllabus BISE papers", "u": "past-papers/", "c": "Resource", "pop": 1, "k": "old papers five years"})

def build_datesheet():
    R = "../"
    rows = [
        ("Matric (9th & 10th) Date Sheet", "February 2027", "Expected", "Delivered first on our WhatsApp/email list"),
        ("Matric Annual Exams", "March 2027", "Expected", "All Punjab boards within the same week"),
        ("Inter (1st & 2nd Year) Date Sheet", "April 2027", "Expected", "Check back. Official PDF posted here instantly"),
        ("Inter Annual Exams", "May-June 2027", "Expected", "Practicals usually follow written exams"),
        ("Matric Result", "July-August 2027", "Expected", "Gazette + online result links"),
        ("Inter Result", "September-October 2027", "Expected", "Position holders announced a day earlier"),
    ]
    tr = "".join(f"""
<tr class="res-item" data-filter-item style="display:table-row">
  <td style="font-weight:700;color:var(--navy-800)">{a}</td><td>{e}</td>
  <td><span class="badge badge-gold">{s}</span></td><td class="muted small">{n}</td></tr>""" for a, e, s, n in rows)
    boards = "".join(f'<a class="chip" href="{R}boards/{b["slug"]}/">{icon("flag",13)} {b["short"]} Board</a>' for b in BOARDS)
    body = crumbs_html(R, [("Date Sheet", "date-sheet/")]) + page_hero(R,
        badge="Session 2026-27",
        title="Date Sheets: Matric & Intermediate (Punjab Boards)",
        lead="Expected schedule for 2027 based on recent years, plus official date sheets as soon as a BISE releases them. Expected and confirmed dates are clearly labelled.",
        actions=f'<a class="btn btn-primary btn-sm" href="#tbl">{icon("cal",15)} View Expected Timeline</a>')
    body += f"""
<section class="section section-tight" style="padding-bottom:0">
  <div class="container" style="max-width:880px">{answer_box("When will the 2027 date sheets come?",
    "Based on recent years: <b>Matric date sheet expected February 2027</b>, exams from March 2027. <b>Inter date sheet expected April 2027</b>, exams May-June 2027. These are expected windows, clearly labelled, not official. The day any BISE publishes the real PDF, it appears here and in the site ticker.",
    "Always treat your own board's official website as the final source for dates.")}</div>
</section>
<section class="section section-tight" style="padding-bottom:0;padding-top:0">{exam_timer_html(R)}</section>
<section class="section section-tight" id="tbl">
  <div class="container">
    <div class="card" style="padding:0;overflow:hidden">
      <table class="asp" style="margin:0">
        <thead><tr><th>Event</th><th>Expected</th><th>Status</th><th>Notes</th></tr></thead>
        <tbody>{tr}</tbody>
      </table>
    </div>
    <div class="card" style="margin-top:26px;background:var(--gold-100);border-color:var(--gold-300);padding:24px;text-align:center">
      <h3 style="font-size:1.1rem;margin-bottom:6px">{icon("bell",20)} Official date sheet announced?</h3>
      <p class="muted" style="font-size:.92rem;margin-bottom:14px">Be the first to know in your class. Join the free alert list.</p>
      {join_updates_form(R)}
    </div>
    <div class="card" style="margin-top:24px">
      <h3 style="margin-bottom:12px">{icon("flag",20)} Your board: get an alert</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">{boards}</div>
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Date Sheet", "date-sheet/")])]
    w("date-sheet/index.html", layout(page_key="datesheet", depth=1,
        title="Date Sheet 2027: Matric & Inter (All Punjab BISE Boards)",
        desc="Expected & official date sheets for matric and intermediate annual exams 2027. All 9 Punjab BISE boards, free PDF download, announced dates updated instantly.",
        path="date-sheet/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "Date Sheets 2027", "s": "matric & inter exam schedules", "u": "date-sheet/", "c": "Resource", "pop": 1, "k": "datesheet exam dates bise"})

def build_ebooks():
    R = "../"
    sec = ""
    for cid in CLASSES:
        cards = "".join(f"""
<article class="ch-item">
  <div class="ch-num" style="background:{SUBJECTS[sid]['hue']}">{icon(SUBJECTS[sid]['icon'],20)}</div>
  <div class="ch-body">
    <h3>{CLASSES[cid]['name']} {SUBJECTS[sid]['name']}: Official Textbook</h3>
    <div class="ch-actions">
      <a class="ch-pill p-notes" href="https://elearn.punjab.gov.pk/" target="_blank" rel="noopener">{icon("external",12)} Read on eLearn Punjab</a>
      <a class="ch-pill p-quiz" href="{R}classes/{cid}/{sid}/">{icon("book",12)} Our notes & files</a>
    </div>
  </div>
</article>""" for sid in subjects_for(cid))
        sec += f"""
<div style="margin-bottom:34px">
  <h2 style="font-size:1.4rem;margin-bottom:4px">{CLASSES[cid]['name']} <span class="badge badge-gold">{CLASSES[cid]['session']}</span></h2>
  <p class="muted" style="margin-bottom:14px;font-size:.92rem">{CLASSES[cid]['book_note']}. Free official PDFs on eLearn Punjab, plus our notes, solutions and more for every subject.</p>
  <div class="grid" style="gap:10px">{cards}</div>
</div>"""
    body = crumbs_html(R, [("eBooks", "ebooks/")]) + page_hero(R,
        badge="Official & Free",
        title="eBooks: New PCTB / PECTAA Textbook PDFs",
        lead="Direct links to the official digital textbooks of every subject and class, plus StudySapiens study material for each subject. Read anywhere: phone, tablet or laptop.",
        actions=f'<a class="btn btn-primary btn-sm" href="https://elearn.punjab.gov.pk/" target="_blank" rel="noopener">{icon("external",15)} eLearn Punjab (official library)</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    <div class="grid grid-3" style="margin-bottom:34px">
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("check",22)}</div>
        <h3>Only official books</h3><p>We link the government's own eLearn Punjab library: correct edition, correct syllabus, no viruses, no fake “PDF” buttons.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("book",22)}</div>
        <h3>Pair it with our notes</h3><p>Read the unit from the book, then revise with our simple-English notes and test yourself: that's the complete loop.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("layers",22)}</div>
        <h3>Scheme inside the book</h3><p>New PECTAA books now print a sample/pattern paper at the end: flip to the last pages for an early look at your exam design.</p></div>
    </div>
    {sec}
  </div>
</section>"""
    ld = [breadcrumb_json([("eBooks", "ebooks/")])]
    w("ebooks/index.html", layout(page_key="ebooks", depth=1,
        title="eBooks: New PCTB/PECTAA Textbooks PDF (Class 9-12 All Subjects) | StudySapiens",
        desc="Official new-syllabus textbook PDFs for Class 9-12. Physics, Chemistry, Biology, Maths, Computer, English. Free via eLearn Punjab, with matching notes.",
        path="ebooks/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "eBooks. Official Textbooks", "s": "new syllabus book PDFs", "u": "ebooks/", "c": "Resource", "pop": 1, "k": "books pdf download pctb"})

# ------------------------------------------------------------------
# MDCAT
# ------------------------------------------------------------------
def build_mdcat():
    R = "../"
    W = MDCAT["weights"]
    mdcat_total = sum(m for _, m in MDCAT["pattern"])
    pattern_rows = "".join(f'<tr><td style="font-weight:700">{esc(s)}</td><td>{m}</td><td>{round(m*100/mdcat_total)}%</td></tr>' for s, m in MDCAT["pattern"])
    syl = "".join(f"""
<div class="qa">
  <button class="qa-head" aria-expanded="false"><span class="q-tag" style="background:var(--navy-700)">{icon('book',11)} {subj}</span> {len(topics)} topic areas
    <svg class="chev" width="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg></button>
  <div class="qa-body"><ul>{''.join(f'<li>{esc(t)}</li>' for t in topics)}</ul></div>
</div>""" for subj, topics in MDCAT["syllabus"].items())
    tl = "".join(f'<div class="tl-item"><h4>{esc(t)}</h4><p>{esc(d)}</p></div>' for t, d in MDCAT["timeline"])
    body = crumbs_html(R, [("MDCAT", "mdcat/")]) + page_hero(R,
        badge="For Pre-Medical Students",
        title="MDCAT Corner: Calculator, Syllabus & Updates",
        lead="Everything an MBBS/BDS aspirant needs in one calm place: live aggregate calculator (50/40/10), latest paper pattern, subject-wise syllabus and a step-by-step admission timeline.",
        actions=f'<a class="btn btn-primary btn-sm" href="#calculator">{icon("calc",15)} Calculate Aggregate</a> <a class="btn btn-light-outline btn-sm" href="#syllabus">MDCAT Syllabus</a>')
    body += f"""
<section class="section" style="padding-top:26px;padding-bottom:0">
  <div class="container" style="max-width:880px">{answer_box("What is the MDCAT aggregate formula for MBBS admission?",
    "Public-sector colleges in Punjab (through UHS) use: <b>Matric 10% + FSc 40% + MDCAT 50%</b>. Each percentage is weighted and added. You also need at least 55% in MDCAT for MBBS and 50% for BDS to stay eligible. Example: Matric 90%, FSc 85%, MDCAT 153/180 (85%) gives 9 + 34 + 42.5 = <b>85.5% aggregate</b>.",
    "Weights are from the official PMDC / UHS admission policy. Confirm the current year's advertisement before applying; we update this page whenever policy changes.")}</div>
</section>
<section class="section" id="calculator" style="padding-top:26px">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("calc",14)} Aggregate Calculator</span>
      <h2>What Will Your Merit Be?</h2>
      <p>Formula used by UHS & most public colleges: <b>Matric 10% + FSc 40% + MDCAT 50%</b>. Enter marks. Watch the gauge move.</p>
    </div>
    <div class="calc-wrap" id="mdcatCalc" data-wmatric="{W['matric']}" data-wfsc="{W['fsc']}" data-wmdcat="{W['mdcat']}">
      <div class="calc-card reveal-l">
        <div class="calc-row">
          <label>Matric Marks <span class="wt">weight {W['matric']}%</span></label>
          <div class="calc-inputs">
            <input id="matricObt" type="number" inputmode="numeric" min="0" max="1200" placeholder="Obtained e.g. 1080">
            <input id="matricTot" type="number" inputmode="numeric" min="1" max="1200" value="1100" placeholder="Total">
          </div>
        </div>
        <div class="calc-row">
          <label>FSc / Intermediate Marks <span class="wt">weight {W['fsc']}%</span></label>
          <div class="calc-inputs">
            <input id="fscObt" type="number" inputmode="numeric" min="0" max="1200" placeholder="Obtained e.g. 1040">
            <input id="fscTot" type="number" inputmode="numeric" min="1" max="1200" value="1100" placeholder="Total">
          </div>
        </div>
        <div class="calc-row">
          <label>MDCAT Score <span class="wt">weight {W['mdcat']}%</span></label>
          <div class="calc-inputs">
            <input id="mdcatObt" type="number" inputmode="numeric" min="0" max="180" placeholder="Obtained e.g. 153">
            <input id="mdcatTot" type="number" inputmode="numeric" min="1" max="180" value="180" placeholder="Total">
          </div>
        </div>
        <p class="calc-note">Tip: you can estimate with expected MDCAT marks too. Totals are editable in case your year differs.</p>
        <div id="eligibility" class="eligibility" style="margin-top:0"></div>
      </div>
      <div class="gauge-card reveal-r">
        <div class="gauge">
          <svg viewBox="0 0 200 200">
            <circle class="g-track" cx="100" cy="100" r="84" fill="none" stroke-width="16"/>
            <circle class="g-val" cx="100" cy="100" r="84" fill="none" stroke-width="16"/>
            <defs><linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#C7CB9D"/><stop offset="1" stop-color="#7E8347"/></linearGradient></defs>
          </svg>
          <div class="g-center"><div><div class="val" id="gaugeNum">0%</div><div class="cap">Your Aggregate</div></div></div>
        </div>
        <table class="gauge-break" id="gaugeBreak"></table>
        <p class="pmdc-note">Reference: 2024-25 closing merits for public-sector MBBS in Punjab hovered around 91-93%. Private colleges set their own merit. Always confirm the current year's policy on PMDC/UHS.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight section-navy">
  <div class="container">
    <div class="grid grid-2" style="gap:36px;align-items:start">
      <div class="reveal-l">
        <span class="sec-kicker">{icon("doc",14)} Paper Pattern</span>
        <h2 style="margin-bottom:14px">MDCAT at a Glance</h2>
        <table class="asp" style="background:#fff;border-radius:12px;overflow:hidden">
          <thead><tr><th>Section</th><th>MCQs</th><th>Weight</th></tr></thead>
          <tbody>{pattern_rows}<tr style="font-weight:800"><td>Total</td><td>{mdcat_total}</td><td>100%</td></tr></tbody>
        </table>
        <p class="small" style="color:#CCCDB4;margin-top:12px">Last verified against PMDC's official MDCAT-2026 notices on 13 November 2026: <a style="color:var(--gold-300)" href="https://pmdc.pk/Documents/Others/Public%20Notice%20Regarding%20Opening%20of%20Online%20Registration%20Portal%20for%20MDCAT-2026.pdf" target="_blank" rel="noopener">pattern &amp; registration notice (PDF)</a> &middot; <a style="color:var(--gold-300)" href="https://pmdc.pk/Documents/Others/MDCAT-2026%20Rescheduling%20Public%20Notice.pdf" target="_blank" rel="noopener">rescheduling notice (PDF)</a>. MDCAT 2026 was held on 20 September 2026. MDCAT 2027 details will appear here the day PMDC announces them.</p>
        <ul style="margin-top:18px;color:#CCCDB4">
          <li>{icon("check",15)} Paper-based test in English. Difficulty mix: 15% easy, 70% moderate, 15% difficult</li>
          <li>{icon("check",15)} No negative marking. Attempt everything</li>
          <li>{icon("check",15)} Passing: 55% for MBBS, 50% for BDS</li>
          <li>{icon("check",15)} Valid nationwide; NUMS uses MDCAT score too</li>
        </ul>
      </div>
      <div class="reveal-r">
        <span class="sec-kicker">{icon("flag",14)} From Registration to Admission</span>
        <h2 style="margin-bottom:20px">The MDCAT Journey</h2>
        <div class="timeline" style="color:#CCCDB4">{tl}</div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="syllabus">
  <div class="container" style="max-width:900px">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("book",14)} Syllabus</span>
      <h2>MDCAT Syllabus: Topic Areas</h2>
      <p>Closely mapped on FSc (Class 11 & 12) books. That is exactly why the Class 11 & 12 resources below double as MDCAT practice.</p>
    </div>
    {syl}
    <div class="card" style="margin-top:26px;background:var(--gold-100);text-align:center;padding:28px">
      <h3 style="font-size:1.1rem;margin-bottom:8px">{icon("zap",20)} Practise now, free</h3>
      <p class="muted" style="font-size:.93rem;margin-bottom:16px">Our Class 11 & 12 physics, chemistry and biology resources double as MDCAT drills. New uploads land regularly.</p>
      <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        <a class="btn btn-dark btn-sm" href="{R}classes/11/biology/">11 Biology</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/12/biology/">12 Biology</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/11/physics/">11 Physics</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/11/chemistry/">11 Chemistry</a>
      </div>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("MDCAT", "mdcat/")])]
    w("mdcat/index.html", layout(page_key="mdcat", depth=1,
        title="MDCAT Aggregate Calculator, Syllabus & Updates 2026 | StudySapiens",
        desc="Free MDCAT aggregate calculator (Matric 10% + FSc 40% + MDCAT 50%). Eligibility rules, latest paper pattern, subject-wise syllabus and admission timeline.",
        path="mdcat/", body=body, extra_ld=ld), priority="0.9")
    SEARCH.append({"t": "MDCAT Corner. Aggregate Calculator & Syllabus", "s": "50/40/10 merit calculator, pattern, prep",
                   "u": "mdcat/", "c": "Test & Tool", "pop": 1, "k": "calculator merit uhs pmdc mbbs bds"})

# ------------------------------------------------------------------
# CSS exam page
# ------------------------------------------------------------------
def build_css_page():
    R = "../"
    comp_rows = "".join(f'<tr><td style="font-weight:700">{esc(s)}</td><td>{m}</td><td class="muted">{esc(d)}</td></tr>'
                        for s, m, d in CSS_EXAM["compulsory"])
    groups = "".join(f"""
<div class="syl-item reveal"><div class="syl-ico">{icon("layers",17)}</div>
  <div><h4>{esc(g)}</h4><p>{esc(s)}</p></div></div>""" for g, s in CSS_EXAM["groups"])
    strat = "".join(f'<div class="tl-item"><h4>{esc(t)}</h4><p>{esc(d)}</p></div>' for t, d in CSS_EXAM["strategy"])
    mats = "".join(f"""
<article class="res-item reveal"><div class="res-ico" style="background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("book",20)}</div>
  <div><h3>{esc(k)}</h3><p>{esc(v)}</p></div></article>""" for k, v in CSS_EXAM["material"])
    body = crumbs_html(R, [("CSS", "css/")]) + page_hero(R,
        badge="FPSC • Once a Year",
        title="CSS Corner: Subjects, Syllabus & 12-Month Strategy",
        lead="A calm, complete guide to the Central Superior Services exam: who can apply, MPT screening, compulsory and optional subjects with marks, recommended books and a realistic plan. In simple English.",
        actions=f'<a class="btn btn-primary btn-sm" href="#subjects">{icon("layers",15)} See Subjects</a> <a class="btn btn-light-outline btn-sm" href="#plan">12-Month Plan</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    <div class="grid grid-4" style="margin-bottom:40px">
      <div class="card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("cap",22)}</div>
        <h3 style="font-size:1rem">Education</h3><p class="muted small">Bachelor's (14-year) degree, minimum 2nd division</p></div>
      <div class="card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("cal",22)}</div>
        <h3 style="font-size:1rem">Age Limit</h3><p class="muted small">21-30 years (up to 32 with relaxation) • cutoff 31 Dec</p></div>
      <div class="card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("refresh",22)}</div>
        <h3 style="font-size:1rem">Attempts</h3><p class="muted small">Maximum 3 written attempts per candidate</p></div>
      <div class="card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("trophy",22)}</div>
        <h3 style="font-size:1rem">Selection</h3><p class="muted small">MPT → Written (1200) → Medical → Interview (300)</p></div>
    </div>
    <div class="sec-head reveal" id="subjects">
      <span class="sec-kicker">{icon("notes",14)} 1200 Written Marks</span>
      <h2>Compulsory Subjects: 600 Marks</h2>
      <p>Every candidate sits these six papers. Passing benchmark in each compulsory paper is 40%. English Essay fails the most candidates, so start it first.</p>
    </div>
    <div class="card" style="padding:0;overflow:hidden;margin-bottom:40px">
      <table class="asp" style="margin:0"><thead><tr><th>Subject</th><th>Marks</th><th>What's tested</th></tr></thead><tbody>{comp_rows}</tbody></table>
    </div>
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("layers",14)} Choose Your Weapons</span>
      <h2>Optional Subjects: 600 Marks</h2>
      <p>Pick subjects totalling 600 marks from seven groups. Golden rule: overlap with your degree & interest beats 'high-scoring myths'.</p>
    </div>
    <div class="syl-grid" style="margin-bottom:44px">{groups}</div>
    <div class="grid grid-2" style="gap:36px;align-items:start" id="plan">
      <div>
        <span class="sec-kicker">{icon("flag",14)} The Roadmap</span>
        <h2 style="margin-bottom:20px">12-Month Preparation Plan</h2>
        <div class="timeline">{strat}</div>
      </div>
      <div>
        <span class="sec-kicker">{icon("book",14)} Study Material</span>
        <h2 style="margin-bottom:16px">Recommended Books & Sources</h2>
        <div class="grid" style="gap:12px">{mats}</div>
        <div class="card" style="margin-top:18px;background:var(--navy-50)">
          <p class="small muted" style="margin:0">{icon("bulb",14)} <b>Note:</b> always buy the latest editions and cross-check the current FPSC syllabus PDF at fpsc.gov.pk before finalising optionals. Rules evolve. We update this page whenever they do.</p>
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:40px;background:var(--gold-100);text-align:center;padding:28px">
      <h3 style="font-size:1.15rem;margin-bottom:8px">{icon("teacher",22)} Have a CSS question?</h3>
      <p class="muted" style="font-size:.93rem;margin-bottom:16px">Subjects, eligibility, strategy or the essay paper. Email us and a real teacher replies with guidance.</p>
      <a class="btn btn-dark" href="{R}contact/">{icon("mail",16)} Ask us anything</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("CSS", "css/")])]
    w("css/index.html", layout(page_key="css", depth=1,
        title="CSS Exam Guide: Eligibility, Subjects & Preparation Plan",
        desc="CSS (FPSC) guide in simple English: eligibility, MPT screening, compulsory & optional subjects with marks, books and a 12-month preparation strategy.",
        path="css/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "CSS Corner. Subjects, Syllabus & Strategy", "s": "FPSC exam guide", "u": "css/", "c": "Page", "pop": 1, "k": "civil service fpsc pms"})

# ------------------------------------------------------------------
# Updates
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# RESULTS section: hub + one page per class
# ------------------------------------------------------------------
def board_table(R):
    rows = "".join(
        f'<tr><td style="font-weight:700;color:var(--navy-800)"><a href="{R}boards/{b["slug"]}/">{b["name"]}</a></td>'
        f'<td><span class="sms-code">{b["sms"]}</span></td>'
        f'<td class="muted small">{b["districts"]}</td>'
        f'<td><a class="res-link" href="{b["site"]}" target="_blank" rel="noopener">{icon("external",12)} Visit</a></td></tr>'
        for b in BOARDS)
    return f'''<div class="card" style="padding:0;overflow:hidden;margin-top:16px">
  <table class="asp" style="margin:0">
    <thead><tr><th>Board</th><th>SMS Code</th><th>Districts Covered</th><th>Official Site</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>'''

def result_methods_cards():
    return f"""
<div class="grid grid-3" style="margin-top:24px">
  <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("globe",22)}</div>
    <h3>1. Online by Roll Number</h3>
    <p>On result day at 10:00 AM, open your board's official website, pick your class and year, and enter the roll number exactly as printed on your admit card. Direct links for every board are in the table below.</p></div>
  <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("phone",22)}</div>
    <h3>2. By SMS</h3>
    <p>Type only your roll number (no extra words) and send it to your board's SMS code from the table. The reply lands in seconds with your total marks. Normal SMS charges apply.</p></div>
  <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("doc",22)}</div>
    <h3>3. Gazette PDF</h3>
    <p>Every board posts the full result gazette PDF on its own site the same morning. You can search your roll number inside it: schools read it the same way.</p></div>
</div>"""

def build_results():
    R = "../"
    cards = ""
    for i, (cid, c) in enumerate(CLASSES.items()):
        cards += f"""
<a class="res-card reveal" data-delay="{i%4}" href="{R}results/class-{cid}/">
  <div class="icon-tile" style="background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("trophy",24)}</div>
  <h3>{c['alt']} Result ({c['level']})</h3>
  <p>{RESULT_WINDOWS[cid]}. Your result lives on your board's official portal. We link it directly: no fake "check here" boxes.</p>
  <span class="res-link">How to check {icon("arrow",14)}</span>
</a>"""
    body = crumbs_html(R, [("Results", "results/")]) + page_hero(R,
        badge="All 9 Punjab Boards • Honest Dates Only",
        title="Board Results 2027: Matric & Intermediate",
        lead="Expected result dates for every class, three ways to check (online, SMS, gazette), and direct links to the official portals of all nine BISE boards. When a date is not announced yet, we say so.",
        actions=f'<a class="btn btn-primary btn-sm" href="#classes">Choose Your Class</a> <a class="btn btn-light-outline btn-sm" href="#boards">{icon("flag",15)} Board SMS Codes</a>')
    body += f"""
<section class="section section-tight" style="padding-bottom:0">
  <div class="container" style="max-width:880px">{answer_box("When are Punjab board results expected in 2027?",
    "Expected windows from recent years: <b>Class 10 first week of August</b>, Class 9 late August to early September, Class 12 late September, Class 11 late October 2027. Boards usually announce all nine Punjab boards within the same week. Until a date is official, we label it Expected instead of pretending to know it.",
    "Your result lives on your board's official portal only. Pick your class below for the portal link and SMS code.")}</div>
</section>
<section class="section section-tight" id="classes" style="padding-top:18px">
  <div class="container">
    <div class="grid grid-4">{cards}</div>
    <div class="card" style="margin-top:24px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("shield",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Our date rule:</b> until a board officially announces a date, we show the <b>expected</b> window from recent years, clearly labelled. The morning a board announces, we update these pages and the ticker. Your result itself always lives on your board's official site: we send you there instead of trapping you here.</p>
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="container">
    <div class="sec-head reveal"><span class="sec-kicker">{icon("zap",14)} Three Ways To Check</span>
      <h2>Result Day, Without the Panic</h2>
      <p>All three methods show the same official marks. Pick whichever works when the server is busy. It will be.</p>
    </div>
    {result_methods_cards()}
  </div>
</section>
<section class="section section-tight" id="boards">
  <div class="container">
    <div class="sec-head reveal"><span class="sec-kicker">{icon("flag",14)} Nine Boards, One Table</span>
      <h2>Board SMS Codes & Official Portals</h2>
      <p>Save your board's SMS code now. On result day you will thank yourself.</p>
    </div>
    {board_table(R)}
    <div class="grid grid-2" style="margin-top:24px">
      <a class="chip" style="justify-content:center" href="{R}date-sheet/">{icon("cal",14)} Date Sheet 2027</a>
      <a class="chip" style="justify-content:center" href="{R}roll-number-slip/">{icon("doc",14)} Roll Number Slip Guide</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Results", "results/")])]
    w("results/index.html", layout(page_key="results", depth=1,
        title="Result 2027: 9th, 10th, 1st & 2nd Year (All Punjab Boards)",
        desc="Expected result dates for Class 9-12 with board SMS codes, gazette info and official portal links for all 9 Punjab boards. Honest labels, no fake checkers.",
        path="results/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "Board Results: All Classes & Boards", "s": "expected dates · SMS codes · official portals",
                   "u": "results/", "c": "Resource", "pop": 1, "k": "result 9th 10th 1st 2nd year check roll number sms gazette bise"})

def build_result_class(cid):
    R = "../../"
    c = CLASSES[cid]
    chips = "".join(f'<a class="chip" href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a>' for s in subjects_for(cid))
    body = crumbs_html(R, [("Results", "results/"), (f"{c['name']} Result", f"results/class-{cid}/")]) + page_hero(R,
        badge=f"{c['level']} • Session {c['session']}",
        title=f"{c['name']} Result 2027: Expected Date & How to Check",
        lead=f"{RESULT_WINDOWS[cid]}. Not announced yet: the confirmed date appears here the moment your board makes it official. Three working ways to check are below, with SMS codes for all nine boards.",
        actions=f'<a class="btn btn-primary btn-sm" href="#how">{icon("zap",15)} How To Check</a> <a class="btn btn-light-outline btn-sm" href="#codes">{icon("phone",15)} SMS Codes</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:920px">
    <div class="card" style="background:var(--gold-100);border-color:var(--gold-300);text-align:center">
      <h2 style="font-size:1.15rem;margin-bottom:6px">{icon("clock",22)} Status: not announced yet</h2>
      <p class="muted" style="font-size:.93rem;margin-bottom:14px">{RESULT_WINDOWS[cid]}. Drop your email and we send one short message the moment your board announces the {c['name']} result. No spam, ever.</p>
      {join_updates_form(R)}
    </div>
    <h2 id="how" style="margin-top:34px">How to Check Your {c['name']} Result</h2>
    {result_methods_cards()}
    <h2 id="codes" style="margin-top:34px">{c['name']} Result SMS Codes: All Nine Punjab Boards</h2>
    <p class="muted">Type your roll number only and send it to your board's code. The reply usually arrives in under a minute.</p>
    {board_table(R)}
    <div class="card" style="margin-top:26px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("bulb",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>After the result:</b> if a mark looks wrong, your board opens an online rechecking window right after the gazette. We post that link and its last date in <a href="{R}updates/">Updates</a>. And when you are ready, next session's downloads are already waiting below.</p>
    </div>
    <h3 style="margin-top:28px">{c['name']} downloads while you wait</h3>
    <div class="subject-chips">{chips}</div>
    <div class="grid grid-2" style="margin-top:18px">
      <a class="chip" style="justify-content:center" href="{R}date-sheet/">{icon("cal",14)} {c['name']} Date Sheet</a>
      <a class="chip" style="justify-content:center" href="{R}past-papers/">{icon("doc",14)} {c['name']} Past Papers</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Results", "results/"), (c["name"], f"results/class-{cid}/")])]
    w(f"results/class-{cid}/index.html", layout(page_key="results", depth=2,
        title=f"{c['alt']} Result 2027: Expected Date, SMS Codes & How to Check",
        desc=f"{c['alt']} result 2027: expected window, how to check by roll number, SMS code or gazette, and official portals for all 9 Punjab boards.",
        path=f"results/class-{cid}/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": f"{c['name']} Result 2027", "s": f"{RESULT_WINDOWS[cid]} · SMS codes · official portals",
                   "u": f"results/class-{cid}/", "c": "Resource", "k": f"{c['alt']} result 2027 roll number sms gazette bise"})

# ------------------------------------------------------------------
# ROLL NUMBER SLIP guide
# ------------------------------------------------------------------
def build_roll_slip():
    R = "../"
    body = crumbs_html(R, [("Roll Number Slip", "roll-number-slip/")]) + page_hero(R,
        badge="Your Admit Card for the Board Exam",
        title="Roll Number Slip 2027: When, Where & What To Do",
        lead="Everything about the board admit card: when slips are issued, how regular and private candidates get theirs, and what to check on it before exam day.",
        actions=f'<a class="btn btn-primary btn-sm" href="#boards">{icon("flag",15)} Board Links</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:980px">
    <div class="grid grid-3">
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("cal",22)}</div>
        <h3>When do slips come?</h3>
        <p>Boards issue slips about 2-4 weeks before the first paper. For the 2027 cycle that means <b>expected February for matric</b> and <b>expected April for inter</b>. Clearly expected until a board announces: we update the moment one does.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("users",22)}</div>
        <h3>Regular students</h3>
        <p>Your school receives the slips from the board and hands them over. If nothing arrives a week before your first paper, ask the school office with your admission form copy. The slip is your responsibility to chase, not the school's to remember.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("download",22)}</div>
        <h3>Private candidates</h3>
        <p>Download from your board's online portal using your registration number and CNIC/B-Form, or collect it as instructed in your registration letter. Print two copies and keep one in your bag from day one.</p></div>
    </div>
    <div class="card" style="margin-top:26px">
      <h3 style="margin-bottom:10px">{icon("check",20)} Five things to verify the minute you get it</h3>
      <ul style="color:var(--ink-soft);line-height:2">
        <li><b>Name spelling</b> matches your CNIC/B-Form exactly (this follows you to certificates)</li>
        <li><b>Photo</b> is yours and clearly printed</li>
        <li><b>Subjects & group</b> (science / arts, compulsory + electives) are correct</li>
        <li><b>Exam centre</b> name and address: visit it once before the first paper</li>
        <li><b>Roll number</b>: memorise it. You need it for result day and every board portal</li>
      </ul>
      <p class="muted small" style="margin-top:8px">Spot a mistake? Contact your board's facilitation centre the same day, not the same week. Corrections are quick early and painful late.</p>
    </div>
    <div class="sec-head reveal" id="boards" style="margin-top:34px"><span class="sec-kicker">{icon("flag",14)} Your Board's Portal</span>
      <h2>Download & Help Links, Board by Board</h2>
      <p>Slip portals open on the same official sites where results appear.</p>
    </div>
    {board_table(R)}
    <div class="card" style="margin-top:26px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("shield",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Honest note:</b> slips are issued only by your board. Any site (including us) can only show you the way there. If a portal charges anyone for a "slip download", it is not the official one.</p>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Roll Number Slip", "roll-number-slip/")])]
    w("roll-number-slip/index.html", layout(page_key="datesheet", depth=1,
        title="Roll Number Slip 2027: Matric & Inter, All Punjab Boards",
        desc="When roll number slips are issued, learn how regular and private candidates can get them from each Punjab board's official portal.",
        path="roll-number-slip/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "Roll Number Slip 2027", "s": "when & how to download · all 9 boards",
                   "u": "roll-number-slip/", "c": "Resource", "k": "roll number slip admit card matric inter download bise"})

# ------------------------------------------------------------------
# MODEL / SAMPLE PAPERS hub
# ------------------------------------------------------------------
def build_model_papers():
    R = "../"
    cards = ""
    for cid in CLASSES:
        for sid in subjects_for(cid):
            rows = file_rows(R, cid, sid, "model")
            if rows:
                status = '<span class="badge badge-live" style="margin-left:6px">✓ live</span>'
                blurb = "Verified model / sample paper PDF for the new book. Download below."
            else:
                status = '<span class="badge badge-gold" style="margin-left:4px">expected</span>'
                blurb = "Uploaded the day PECTAA or boards issue the official sample paper for the new book. Teacher-made practice papers are always clearly labelled."
            cards += f"""
<article class="res-item reveal" data-filter-item data-cls="{cid}" data-sub="{sid}">
  <div class="res-ico" style="background:{SUBJECTS[sid]['hue']}">{icon("star",22)}</div>
  <div><h3>{CLASSES[cid]['name']} {SUBJECTS[sid]['name']} Model Paper {CLASSES[cid]['session']}{status}</h3>
    <p>{blurb}</p>
    {rows}
  </div>
  <div class="res-cta">{'' if rows else f'<a class="btn btn-ghost btn-sm" href="{R}classes/{cid}/{sid}/">{icon("grid",13)} Subject page</a><a class="btn btn-dark btn-sm" href="mailto:{EMAIL}?subject={cid}th%20{SUBJECTS[sid]["name"].replace(" ","%20")}%20model%20paper%20request">{icon("bell",13)} Notify me</a>'}</div>
</article>"""
    body = crumbs_html(R, [("Model Papers", "model-papers/")]) + page_hero(R,
        badge="The Exact Exam Pattern, On Paper",
        title="Model & Sample Papers: Official Pattern for the New Books",
        lead="The single best way to see your real paper before the exam: official sample papers with the new marking scheme, uploaded for every class and subject as boards release them.",
        actions=f'<a class="btn btn-primary btn-sm" href="#resGrid">{icon("star",15)} Browse Model Papers</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    {resource_filter()}
    <div class="grid" id="resGrid" style="gap:12px">{cards}
      <div class="card filter-empty" style="display:none;text-align:center">No model paper matches that filter yet. Try another class/subject.</div>
    </div>
    <div class="card" style="margin-top:28px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("shield",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Source labels, always:</b> official PECTAA/board sample papers are marked <b>official</b>; anything our own teachers prepare is marked <b>teacher-made practice paper</b>. You will never have to guess which is which.</p>
    </div>
    <div class="grid grid-3" style="margin-top:40px">
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("zap",22)}</div>
        <h3>See the Real Pattern</h3><p>How many MCQs, how much choice in short questions, where the long questions come from. Ten quiet minutes with a model paper beats a week of worry.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("clock",22)}</div>
        <h3>Practise Timed Attempts</h3><p>Attempt it in one sitting with the real time limit. Most marks are lost to bad time management, not bad preparation.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("notes",22)}</div>
        <h3>Study the Marking Scheme</h3><p>Official samples show how markers split steps. Write your answers to match those steps and your score climbs with the same knowledge.</p></div>
    </div>
    <div class="grid grid-2" style="margin-top:24px">
      <a class="chip" style="justify-content:center" href="{R}pairing-scheme/">{icon("layers",14)} Pairing Schemes</a>
      <a class="chip" style="justify-content:center" href="{R}past-papers/">{icon("doc",14)} Past Papers</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Model Papers", "model-papers/")])]
    w("model-papers/index.html", layout(page_key="past", depth=1,
        title="Model & Sample Papers 2027: Class 9-12, New Syllabus Pattern",
        desc="Official model papers & sample papers for the new PCTB/PECTAA books, class 9 to 12, all subjects. Uploaded as boards issue them, clearly labelled. Free PDF.",
        path="model-papers/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "Model Papers: All Classes", "s": "official sample papers · new pattern · all subjects",
                   "u": "model-papers/", "c": "Resource", "pop": 1, "k": "model paper sample paper pattern paper new syllabus 9th 10th 1st 2nd year"})

# ------------------------------------------------------------------
# FORMULA SHEETS hub (maths, physics, chemistry · per class)
# ------------------------------------------------------------------
FORMULA_SUBS = [("mathematics", "Maths"), ("physics", "Physics"), ("chemistry", "Chemistry")]

def build_formulas():
    R = "../"
    sections = ""
    for cid, c in CLASSES.items():
        slots = ""
        for sid, label in FORMULA_SUBS:
            s = SUBJECTS[sid]
            slots += slot_html(s["hue"], s["icon"], f"{label} Formula Sheet",
                               f"{c['name']} {label}, new {c['session']} book (PDF)",
                               extra_rows(R, "formulas", f"class-{cid}/{sid}"),
                               f"{c['name']}%20{label}%20formula%20sheet%20request").replace(
                               'class="file-slot reveal"', 'class="file-slot"')
        sections += f"""
<div class="sec-head reveal" style="margin-top:34px"><span class="sec-kicker">{icon("sigma",14)} {c['name']} · {c['level']}</span>
  <h2 style="font-size:1.4rem">{c['name']} Formula Sheets</h2>
</div>
<div class="file-grid">{slots}</div>"""
    body = crumbs_html(R, [("Formula Sheets", "formulas/")]) + page_hero(R,
        badge="Printable, One-Page-Per-Chapter",
        title="Formula Sheets: Maths, Physics & Chemistry (Class 9-12)",
        lead="Every important formula of the new books on a single clean sheet per chapter: the thing you revise on the bus on result-day morning. Uploaded class by class by our teachers.",
        actions=f'<a class="btn btn-primary btn-sm" href="#f9">Choose Your Class</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:980px">
    <div class="card" style="padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("bulb",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Why a formula sheet works:</b> numericals decide the topper from the average in physics, chemistry and maths. A sheet you revise ten times sticks far better than a chapter you read once. Ours are compiled from the new printed books and checked twice before upload.</p>
    </div>
    <div id="f9">{sections}</div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Formula Sheets", "formulas/")])]
    w("formulas/index.html", layout(page_key="classes", depth=1,
        title="Formula Sheets: Maths, Physics & Chemistry (Class 9-12, Free PDF)",
        desc="Chapter-wise formula sheets for Class 9, 10, 1st & 2nd year maths, physics and chemistry. New PCTB/PECTAA books, printable one-pagers, free PDF downloads.",
        path="formulas/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "Formula Sheets: Maths, Physics, Chemistry", "s": "class-wise printable PDFs",
                   "u": "formulas/", "c": "Resource", "k": "formula sheet math physics chemistry important formulas class nine ten 1st 2nd year pdf"})

# ------------------------------------------------------------------
# ENGLISH corner: essays, letters & applications, grammar
# ------------------------------------------------------------------
def build_english_corner():
    R = "../"
    slots = (
        slot_html("var(--c-english)", "notes", "Essays", "Full-mark essay samples for Class 9-12 (PDF)",
                  extra_rows(R, "english", "essays"), "English%20essay%20file%20request").replace('class="file-slot reveal"', 'class="file-slot"')
        + slot_html("var(--c-english)", "mail", "Letters & Applications", "Board-format letters & applications (PDF)",
                  extra_rows(R, "english", "letters-applications"), "Letters%20applications%20file%20request").replace('class="file-slot reveal"', 'class="file-slot"')
        + slot_html("var(--c-english)", "book", "Grammar & Translation", "Tenses, narration, voice, translation practice (PDF)",
                  extra_rows(R, "english", "grammar"), "English%20grammar%20file%20request").replace('class="file-slot reveal"', 'class="file-slot"'))
    body = crumbs_html(R, [("English Corner", "english-corner/")]) + page_hero(R,
        badge="The Paper Section Everyone Underestimates",
        title="English Corner: Essays, Letters & Applications (Class 9-12)",
        lead="The writing section is the easiest place to gain 15-20 marks and the most ignored. Exact board formats, teacher-written samples in simple English, and grammar drills that match the new papers.",
        actions=f'<a class="btn btn-primary btn-sm" href="#downloads">{icon("download",15)} Downloads</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:920px">
    <div class="grid grid-3">
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("notes",22)}</div>
        <h3>Essays That Score</h3><p>Short, clear, quoted where it counts. Our samples show the exact structure markers reward: intro, three points, conclusion. No flowery memorised paragraphs.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("mail",22)}</div>
        <h3>Letters & Applications</h3><p>Fee concession, sick leave, character certificate, letters to editor: one correct format each, memorised once, used for years.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("book",22)}</div>
        <h3>Grammar Drills</h3><p>Tenses, narration, voice and translation presented the way the paper asks them, with answers so you can self-check.</p></div>
    </div>
    <h2 id="downloads" style="margin-top:32px">Downloads</h2>
    <p class="muted" style="margin-bottom:16px;font-size:.94rem">Written by our own teachers in deliberately simple English. Uploaded file by file; request anything missing and it jumps the queue.</p>
    <div class="file-grid">{slots}</div>
    <div class="grid grid-2" style="margin-top:22px">
      <a class="chip" style="justify-content:center" href="{R}classes/9/english/">{icon("book",14)} Class 9 English Page</a>
      <a class="chip" style="justify-content:center" href="{R}classes/10/english/">{icon("book",14)} Class 10 English Page</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("English Corner", "english-corner/")])]
    w("english-corner/index.html", layout(page_key="classes", depth=1,
        title="English Essays, Letters & Applications (Class 9-12) | StudySapiens",
        desc="Board-format English essays, letters, applications and grammar drills for Class 9-12. Simple-English samples written by teachers, free PDF downloads.",
        path="english-corner/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "English Corner: Essays, Letters, Grammar", "s": "board-format writing files",
                   "u": "english-corner/", "c": "Resource", "k": "english essay letter application grammar translation tenses class 9 10 1st 2nd year"})

# ------------------------------------------------------------------
# BOARDS directory: hub + one page per BISE
# ------------------------------------------------------------------
def build_boards():
    R = "../"
    cards = ""
    for i, b in enumerate(BOARDS):
        cards += f"""
<a class="res-card reveal" data-delay="{i%3}" href="{R}boards/{b['slug']}/">
  <div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("flag",24)}</div>
  <h3>{b['name']}</h3>
  <p>{b['districts']}. Result SMS code <b>{b['sms']}</b>.</p>
  <span class="res-link">Open board page {icon("arrow",14)}</span>
</a>"""
    body = crumbs_html(R, [("Boards", "boards/")]) + page_hero(R,
        badge="Nine BISE Boards of Punjab",
        title="Boards Directory: All 9 BISE Boards of Punjab",
        lead="One clean page per board: the districts it covers, its result SMS code, and its official website for date sheets, roll number slips and results.",
        actions=f'<a class="btn btn-primary btn-sm" href="#boards">Find Your Board</a>')
    body += f"""
<section class="section section-tight" id="boards">
  <div class="container">
    <div class="card" style="margin-bottom:24px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("bulb",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Which board is yours?</b> Your board is decided by your school's district, not your choice. Find your district in a card below: if yours is missing from every card, it is covered by the nearest division's board (e.g. Sialkot students belong to Gujranwala board).</p>
    </div>
    <div class="grid grid-3">{cards}</div>
    <div class="grid grid-2" style="margin-top:26px">
      <a class="chip" style="justify-content:center" href="{R}results/">{icon("trophy",14)} Results Hub</a>
      <a class="chip" style="justify-content:center" href="{R}date-sheet/">{icon("cal",14)} Date Sheets</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Boards", "boards/")])]
    w("boards/index.html", layout(page_key="results", depth=1,
        title="All 9 BISE Boards of Punjab: Districts, SMS Codes & Websites",
        desc="All nine Punjab BISE boards: districts covered, result SMS codes and official sites for Lahore, Gujranwala, Multan, Rawalpindi, Sargodha and more.",
        path="boards/", body=body, extra_ld=ld), priority="0.8")
    SEARCH.append({"t": "Boards Directory: All 9 BISE", "s": "districts · SMS codes · official sites",
                   "u": "boards/", "c": "Resource", "k": "bise board lahore gujranwala multan faisalabad rawalpindi sargodha sahiwal bahawalpur dg khan"})

def build_board(b):
    R = "../../"
    body = crumbs_html(R, [("Boards", "boards/"), (b["short"], f"boards/{b['slug']}/")]) + page_hero(R,
        badge="Board of Intermediate & Secondary Education",
        title=f"{b['name']}: Districts, SMS Code & Official Links",
        lead=f"Everything a {b['short']} board student needs in one place: which districts it covers, how to reach it, and where its date sheets, slips and results actually live.",
        actions=f'<a class="btn btn-primary btn-sm" href="{b["site"]}" target="_blank" rel="noopener">{icon("external",15)} Official Website</a> <a class="btn btn-light-outline btn-sm" href="{R}results/">{icon("trophy",15)} Result Guide</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:880px">
    <div class="card" style="padding:0;overflow:hidden">
      <table class="asp" style="margin:0">
        <tbody>
          <tr><td style="font-weight:700;color:var(--navy-800)">Board</td><td>{b['name']}</td></tr>
          <tr><td style="font-weight:700;color:var(--navy-800)">Districts covered</td><td>{b['districts']}</td></tr>
          <tr><td style="font-weight:700;color:var(--navy-800)">Result SMS code</td><td><span class="sms-code">{b['sms']}</span> <span class="muted small">send your roll number on result day</span></td></tr>
          <tr><td style="font-weight:700;color:var(--navy-800)">Official website</td><td><a class="res-link" href="{b['site']}" target="_blank" rel="noopener">{icon("external",12)} {b['site'].replace('https://www.','')}</a></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card" style="margin-top:24px;padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("shield",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>How we cover {b['short']} board:</b> date sheets, roll number slip news, result dates and gazette links for {b['name']} appear first in our <a href="{R}updates/">Updates</a> and on the hubs below, always labelled <b>expected</b> until the board itself announces. Final documents live on the official site linked above.</p>
    </div>
    <h3 style="margin-top:28px">Handy for {b['short']} board students</h3>
    <div class="grid grid-2" style="margin-top:12px">
      <a class="chip" style="justify-content:center" href="{R}results/">{icon("trophy",14)} Result Dates & SMS Codes</a>
      <a class="chip" style="justify-content:center" href="{R}roll-number-slip/">{icon("doc",14)} Roll Number Slip Guide</a>
      <a class="chip" style="justify-content:center" href="{R}date-sheet/">{icon("cal",14)} Date Sheet 2027</a>
      <a class="chip" style="justify-content:center" href="{R}past-papers/">{icon("layers",14)} Past Papers (New Syllabus)</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Boards", "boards/"), (b["short"], f"boards/{b['slug']}/")])]
    w(f"boards/{b['slug']}/index.html", layout(page_key="results", depth=2,
        title=f"{b['name']} ({b['short']} Board): SMS Code, Districts & Links",
        desc=f"{b['name']}: districts covered, result SMS code {b['sms']}, official website link and exam guidance for {b['short']} board students.",
        path=f"boards/{b['slug']}/", body=body, extra_ld=ld), priority="0.7")
    SEARCH.append({"t": f"{b['name']}: Board Page", "s": f"{b['districts'].split(',')[0]} · SMS {b['sms']}",
                   "u": f"boards/{b['slug']}/", "c": "Board", "k": f"{b['short']} board bise result date sheet roll number slip"})

# ------------------------------------------------------------------
# ONLINE TESTS: interactive self-scoring MCQ quizzes
# ------------------------------------------------------------------
QUIZ_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quizzes")

def scan_quizzes():
    qs = []
    if os.path.isdir(QUIZ_ROOT):
        for fn in sorted(os.listdir(QUIZ_ROOT)):
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(QUIZ_ROOT, fn)) as fh:
                q = json.load(fh)
            q.setdefault("slug", fn[:-5])
            qs.append(q)
    return qs

def build_test_player(q):
    R = "../../"
    n = len(q["questions"])
    qjson = json.dumps(q["questions"], ensure_ascii=False).replace("</", "<\\/")
    body = crumbs_html(R, [("Online Tests", "tests/"), (q["title"], f"tests/{q['slug']}/")]) + page_hero(R,
        badge=f"{q.get('cls','All classes')} • {q.get('subject','General')} • {n} questions",
        title=q["title"],
        lead=q.get("desc", "Answer all questions, get your score instantly, and review every answer with an explanation."),
        actions="")
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:780px">
    <div class="card" id="quiz" style="padding:28px">
      <div id="quizStart">
        <div style="text-align:center;padding:10px 4px 6px">
          <div class="icon-tile" style="margin:0 auto 14px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("zap",26)}</div>
          <h2 style="margin-bottom:8px">Ready when you are</h2>
          <p class="muted" style="max-width:460px;margin:0 auto 6px">{n} questions, one at a time. You see the correct answer and a short explanation right after each question. No timer pressure: the clock only counts up.</p>
          <p class="muted small" style="margin-bottom:18px">Answers are made by teachers and verified by subject experts. No login required; free to use.</p>
          <button class="btn btn-primary btn-lg" type="button" onclick="startQuiz()">{icon("zap",17)} Start the Test</button>
        </div>
      </div>
      <div id="quizBody" style="display:none">
        <div class="quiz-top">
          <span id="quizCount">Question 1 of {n}</span>
          <span id="quizTimer">{icon("clock",13)} <span>00:00</span></span>
          <span id="quizLiveScore">Score: 0/0</span>
        </div>
        <div class="quiz-progress" style="margin-bottom:18px"><i id="quizBar"></i></div>
        <div id="quizQuestions"></div>
        <div class="quiz-navrow">
          <button class="btn btn-light-outline btn-sm" type="button" id="qPrev">← Prev</button>
          <button class="btn btn-dark btn-sm" type="button" id="qNext">Next →</button>
        </div>
      </div>
      <div class="quiz-result" id="quizResult">
        <div class="score-ring">
          <svg viewBox="0 0 160 160">
            <circle class="sr-track" cx="80" cy="80" r="64" fill="none" stroke-width="14"/>
            <circle class="sr-val" id="scoreRingVal" cx="80" cy="80" r="64" fill="none" stroke-width="14"/>
          </svg>
          <div class="sr-txt" id="scoreText">0%</div>
        </div>
        <h3 id="scoreMsg" style="margin:10px 0 4px"></h3>
        <p class="muted" id="scoreDetail" style="margin-bottom:16px"></p>
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:16px">
          <button class="btn btn-primary btn-sm" type="button" id="qRestart">{icon("refresh",14)} Retake</button>
          <a class="btn btn-light-outline btn-sm" href="{R}tests/">{icon("grid",14)} All Tests</a>
        </div>
        <div id="quizReviewList" style="text-align:left"></div>
      </div>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Online Tests", "tests/"), (q["title"], f"tests/{q['slug']}/")]),
          {"@context": "https://schema.org", "@type": "Quiz",
           "name": q["title"], "about": q.get("subject", "Study skills"),
           "assesses": q.get("subject", "general knowledge"), "isAccessibleForFree": True}]
    t = f"{q['title']} | Online Test"
    if len(t) > 66: t = q["title"]
    w(f"tests/{q['slug']}/index.html", layout(page_key="tests", depth=2,
        title=t, desc=(q.get("desc", f"Free self-scoring online test: {n} MCQs with instant results and explanations."))[:160],
        path=f"tests/{q['slug']}/", body=body, extra_ld=ld,
        head_extra=f"<script>window.QUIZ={qjson};</script>"), priority="0.6")
    SEARCH.append({"t": f"Test: {q['title']}", "s": f"{q.get('cls','all classes')} · {n} questions · self-scoring",
                   "u": f"tests/{q['slug']}/", "c": "Test", "k": f"online test mcq quiz {q.get('subject','')} {q.get('cls','')}"})

def build_tests():
    R = "../"
    quizzes = scan_quizzes()
    for q in quizzes:
        build_test_player(q)
    if quizzes:
        cards = ""
        for i, q in enumerate(quizzes):
            cards += f"""
<a class="res-card reveal" data-delay="{i%3}" href="{R}tests/{q['slug']}/">
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px">
    <span class="badge badge-navy">{esc(q.get('cls','All classes'))}</span>
    <span class="badge badge-gold">{esc(q.get('subject','General'))}</span>
    <span class="badge badge-gray">{len(q['questions'])} questions</span>
  </div>
  <h3>{esc(q['title'])}</h3>
  <p>{esc(q.get('desc',''))[:110]}</p>
  <span class="res-link">Start test {icon("arrow",14)}</span>
</a>"""
        grid = f'<div class="grid grid-3">{cards}</div>'
    else:
        grid = f"""
<div class="card" style="text-align:center;padding:40px 26px">
  <div class="icon-tile" style="margin:0 auto 14px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("zap",26)}</div>
  <h3 style="margin-bottom:6px">First tests are uploading soon</h3>
  <p class="muted" style="max-width:520px;margin:0 auto 14px">Chapter-wise tests for the new books are being written and checked by our teachers right now. Leave your email and we'll tell you the moment your class goes live. Until then, the downloadable MCQ banks on every subject page work great for self-testing.</p>
  {join_updates_form(R)}
</div>"""
    body = crumbs_html(R, [("Online Tests", "tests/")]) + page_hero(R,
        badge="Answer, Score, Review. Right Here",
        title="Online MCQ Tests: Self-Scoring, Instant Explanations",
        lead="Real practice in your browser: attempt questions one by one, get your score instantly, and review every answer with a teacher-written explanation. Free to use, with no login required.",
        actions=f'<a class="btn btn-primary btn-sm" href="#tests">{icon("zap",15)} Take a Test</a>')
    body += f"""
<section class="section section-tight" id="tests">
  <div class="container">
    {grid}
    <div class="grid grid-3" style="margin-top:40px">
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("zap",22)}</div>
        <h3>Instant, Honest Scoring</h3><p>Your score is computed in your browser the moment you finish. Nothing is uploaded, nothing tracked.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("bulb",22)}</div>
        <h3>Explanation for Every Answer</h3><p>Right or wrong, each question tells you WHY. That is where the real learning hides in MCQ practice.</p></div>
      <div class="feature-card"><div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("refresh",22)}</div>
        <h3>Retake Anytime</h3><p>Tests are unlimited and free forever. Retake after revising the notes and watch your score climb.</p></div>
    </div>
    <div class="grid grid-2" style="margin-top:26px">
      <a class="chip" style="justify-content:center" href="{R}classes/">{icon("download",14)} Downloadable MCQ Banks</a>
      <a class="chip" style="justify-content:center" href="{R}guess-papers/">{icon("target",14)} Guess Papers</a>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("Online Tests", "tests/")])]
    w("tests/index.html", layout(page_key="tests", depth=1,
        title="Online MCQ Tests: Class 9-12, Self-Scoring & Free | StudySapiens",
        desc="Free self-scoring online MCQ tests for Class 9, 10, 1st & 2nd year (new PCTB/PECTAA syllabus). Instant results with teacher-written explanations. No login required.",
        path="tests/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "Online Tests: Self-Scoring MCQs", "s": "instant score · explanations · all classes",
                   "u": "tests/", "c": "Resource", "pop": 1, "k": "online mcq test practice quiz self assessment class 9 10 1st 2nd year"})

# ------------------------------------------------------------------
# ECAT corner (engineering entry test, UET formula 17/50/33)
# ------------------------------------------------------------------
def build_ecat():
    R = "../"
    W = ECAT["weights"]
    pattern_rows = "".join(
        f'<tr><td style="font-weight:700">{esc(s)}</td><td>{m}</td><td>{mk}</td></tr>'
        for s, m, mk in ECAT["pattern"])
    facts = "".join(f"<li>{icon('check',15)} {esc(f)}</li>" for f in ECAT["facts"])
    tl = "".join(f'<div class="tl-item"><h4>{esc(t)}</h4><p>{esc(d)}</p></div>' for t, d in ECAT["journey"])
    body = crumbs_html(R, [("ECAT", "ecat/")]) + page_hero(R,
        badge="For Pre-Engineering Students",
        title="ECAT Corner: UET Aggregate Calculator & Guide",
        lead="The engineering entry test, minus the confusion: live UET aggregate calculator (Matric 17% + FSc 50% + ECAT 33%), the paper pattern, and the road from registration to merit list.",
        actions=f'<a class="btn btn-primary btn-sm" href="#calculator">{icon("calc",15)} Calculate Aggregate</a> <a class="btn btn-light-outline btn-sm" href="#journey">Admission Roadmap</a>')
    body += f"""
<section class="section" style="padding-top:26px;padding-bottom:0">
  <div class="container" style="max-width:880px">{answer_box("What is the ECAT / UET aggregate formula for engineering admission?",
    "UET calculates merit as: <b>Matric 17% + FSc 50% + ECAT 33%</b>. The ECAT paper is out of 400 marks; convert it to a percentage before weighting. Example: Matric 88%, FSc 82%, ECAT 280/400 (70%) gives 14.96 + 41 + 23.1 = <b>79.06% aggregate</b>.",
    "Formula is from UET's official admission policy. Other universities (NUST, FAST, GIKI) use their own formulas; this calculator follows UET Lahore.")}</div>
</section>
<section class="section" id="calculator" style="padding-top:26px">
  <div class="container">
    <div class="sec-head reveal">
      <span class="sec-kicker">{icon("calc",14)} Aggregate Calculator</span>
      <h2>Where Would You Stand on the Merit List?</h2>
      <p>Current UET formula: <b>Matric 17% + FSc 50% + ECAT 33%</b> (ECAT out of 400). Enter your marks and watch the gauge.</p>
    </div>
    <div class="calc-wrap" id="ecatCalc" data-wmatric="{W['matric']}" data-wfsc="{W['fsc']}" data-wecat="{W['ecat']}">
      <div class="calc-card reveal-l">
        <div class="calc-row">
          <label>Matric Marks <span class="wt">weight {W['matric']}%</span></label>
          <div class="calc-inputs">
            <input id="matricObt" type="number" inputmode="numeric" min="0" max="1200" placeholder="Obtained e.g. 1020">
            <input id="matricTot" type="number" inputmode="numeric" min="1" max="1200" value="1100" placeholder="Total">
          </div>
        </div>
        <div class="calc-row">
          <label>FSc / ICS Marks <span class="wt">weight {W['fsc']}%</span></label>
          <div class="calc-inputs">
            <input id="fscObt" type="number" inputmode="numeric" min="0" max="1200" placeholder="Obtained e.g. 990">
            <input id="fscTot" type="number" inputmode="numeric" min="1" max="1200" value="1100" placeholder="Total">
          </div>
        </div>
        <div class="calc-row">
          <label>ECAT Score <span class="wt">weight {W['ecat']}%</span></label>
          <div class="calc-inputs">
            <input id="ecatObt" type="number" inputmode="numeric" min="0" max="400" placeholder="Obtained e.g. 260">
            <input id="ecatTot" type="number" inputmode="numeric" min="1" max="400" value="400" placeholder="Total">
          </div>
        </div>
        <p class="calc-note">Tip: totals are editable in case your year or board totals differ. You can also estimate with your expected ECAT score.</p>
        <div id="eligibility" class="eligibility" style="margin-top:0"></div>
      </div>
      <div class="gauge-card reveal-r">
        <div class="gauge">
          <svg viewBox="0 0 200 200">
            <circle class="g-track" cx="100" cy="100" r="84" fill="none" stroke-width="16"/>
            <circle class="g-val" cx="100" cy="100" r="84" fill="none" stroke-width="16"/>
            <defs><linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#C7CB9D"/><stop offset="1" stop-color="#7E8347"/></linearGradient></defs>
          </svg>
          <div class="g-center"><div><div class="val" id="gaugeNum">0%</div><div class="cap">Your Aggregate</div></div></div>
        </div>
        <table class="gauge-break" id="gaugeBreak"></table>
        <p class="pmdc-note">Reference: closing merits at UET vary widely by department and campus, roughly from the low 60s to mid 80s. Always check the current merit lists on UET's own admission portal before deciding.</p>
      </div>
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="container">
    <div class="sec-head reveal"><span class="sec-kicker">{icon("grid",14)} Paper Pattern</span>
      <h2>ECAT at a Glance</h2>
      <p>100 MCQs in 100 minutes, computer-based, no negative marking. Chemistry swaps with Computer Science for ICS groups.</p>
    </div>
    <div class="card" style="padding:0;overflow:hidden;max-width:680px;margin:0 auto">
      <table class="asp" style="margin:0">
        <thead><tr><th>Section</th><th>MCQs</th><th>Marks</th></tr></thead>
        <tbody>{pattern_rows}</tbody>
      </table>
    </div>
    <ul class="check-list" style="max-width:680px;margin:20px auto 0">{facts}</ul>
  </div>
</section>
<section class="section section-tight" id="journey">
  <div class="container">
    <div class="sec-head reveal"><span class="sec-kicker">{icon("flag",14)} From Registration to Admission</span>
      <h2>The ECAT Journey</h2>
    </div>
    <div class="timeline">{tl}</div>
  </div>
</section>
<section class="section section-tight">
  <div class="container" style="max-width:880px">
    <div class="card" style="padding:16px 22px;display:flex;gap:12px;align-items:flex-start;background:var(--navy-50)">
      <span style="color:var(--navy-700)">{icon("shield",20)}</span>
      <p class="small" style="color:var(--ink-soft)"><b>Honest note:</b> the 17/50/33 formula is the current UET Lahore pattern (verified October 2026). Other universities (NUST, GIKI, FAST, NED) run their own tests and formulas, and UET itself can revise weightages any year. Always confirm the final formula on the official admission portal of the university you apply to.</p>
    </div>
    <div class="card" style="margin-top:26px;background:var(--gold-100);text-align:center;padding:28px">
      <h3 style="font-size:1.1rem;margin-bottom:8px">{icon("zap",20)} ECAT prep = your Class 11 & 12 books</h3>
      <p class="muted" style="font-size:.93rem;margin-bottom:16px">ECAT MCQs come from FSc maths, physics and chemistry. Our Class 11 & 12 resources double as ECAT drills.</p>
      <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        <a class="btn btn-dark btn-sm" href="{R}classes/11/mathematics/">11 Maths</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/12/mathematics/">12 Maths</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/11/physics/">11 Physics</a>
        <a class="btn btn-dark btn-sm" href="{R}classes/11/chemistry/">11 Chemistry</a>
        <a class="btn btn-dark btn-sm" href="{R}mdcat/">MDCAT Corner →</a>
      </div>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("ECAT", "ecat/")])]
    w("ecat/index.html", layout(page_key="ecat", depth=1,
        title="ECAT Corner: UET Aggregate Calculator (17/50/33) & Pattern",
        desc="Free ECAT aggregate calculator using the current UET formula (Matric 17% + FSc 50% + ECAT 33%), paper pattern, eligibility rules and admission roadmap.",
        path="ecat/", body=body, extra_ld=ld), priority="0.85")
    SEARCH.append({"t": "ECAT Corner: Calculator & Guide", "s": "UET 17/50/33 aggregate · pattern · roadmap",
                   "u": "ecat/", "c": "Resource", "pop": 1, "k": "ecat uet engineering entry test aggregate calculator merit formula"})

def build_updates():
    R = "../"
    cards = "".join(f"""
<article class="update-card reveal">
  <div class="up-top"><span class="badge badge-gold">{esc(p["tag"])}</span>
    <div class="up-date">{icon("clock",13)} {esc(p["date"])}</div>
    <h3><a href="{R}updates/{p['slug']}/">{esc(p['title'])}</a></h3>
  </div>
  <div class="up-body"><p>{esc(p['excerpt'])}</p>
    <a class="read-more" href="{R}updates/{p['slug']}/">Read update {icon("arrow",13)}</a></div>
</article>""" for p in UPDATES)
    body = crumbs_html(R, [("Updates", "updates/")]) + page_hero(R,
        badge="Verified Only",
        title="Academic Updates & Announcements",
        lead="New books, syllabus changes, date sheets, MDCAT news and CSS guidance. Short, verified updates without the rumour mill.",
        actions=f'<a class="btn btn-primary btn-sm" href="#list">{icon("bell",15)} Read Latest</a>')
    body += f"""
<section class="section section-tight" id="list">
  <div class="container"><div class="grid grid-3">{cards}</div>
  <div class="card" style="margin-top:36px;background:var(--gold-100);text-align:center;padding:28px">
    <h3 style="font-size:1.1rem;margin-bottom:6px">Never miss an update</h3>
    <p class="muted" style="font-size:.92rem;margin-bottom:14px">Join the free alert list. One short email when something important happens.</p>
    {join_updates_form(R)}
  </div></div>
</section>"""
    ld = [breadcrumb_json([("Updates", "updates/")])]
    w("updates/index.html", layout(page_key="updates", depth=1,
        title="Academic Updates: New Syllabus, Date Sheets, MDCAT & CSS News | StudySapiens",
        desc="Latest verified academic updates for Punjab students: new PCTB books, exam schedules, pairing schemes, MDCAT and CSS announcements.",
        path="updates/", body=body, extra_ld=ld), priority="0.7", changefreq="daily")

def build_post(p):
    R = "../../"
    others = [x for x in UPDATES if x["slug"] != p["slug"]][:3]
    rel_cards = "".join(f"""
<article class="update-card"><div class="up-top"><span class="badge badge-gold">{esc(x["tag"])}</span>
  <div class="up-date">{icon("clock",13)} {esc(x["date"])}</div>
  <h3><a href="{R}updates/{x['slug']}/">{esc(x['title'])}</a></h3></div>
  <div class="up-body"><p>{esc(x['excerpt'][:110])}…</p>
  <a class="read-more" href="{R}updates/{x['slug']}/">Read {icon("arrow",13)}</a></div></article>""" for x in others)
    body_html = p["body"].replace('href="/', f'href="{R}')
    src_html = ""
    if p.get("sources"):
        links = " &nbsp;&middot;&nbsp; ".join(
            f'<a href="{esc(u)}" rel="noopener nofollow">{icon("external",11)} {esc(n)}</a>'
            for n, u in p["sources"])
        src_html = f'<p class="sources-line">{icon("shield",14)} <b>Official sources:</b> {links}</p>'
    body = crumbs_html(R, [("Updates", "updates/"), (p["title"], f"updates/{p['slug']}/")])
    body += f"""
<section class="section" style="padding-top:44px">
  <div class="container">
    <div class="article">
      <span class="badge badge-gold">{esc(p["tag"])}</span>
      <h1 style="margin-top:12px">{esc(p["title"])}</h1>
      <div class="art-meta"><span>{icon("cal",14)} {esc(p["date"])}</span><span>{icon("teacher",14)} StudySapiens Team</span><span>{icon("clock",14)} 4 min read</span></div>
      <div class="article-body">{body_html}</div>
      {src_html}
      {share_row()}
      <div class="card" style="background:var(--navy-50);margin:26px 0;padding:22px">
        <p class="small muted" style="margin:0">{icon("doc",13)} <b>Disclaimer:</b> schedules and policies are summarised from official announcements for students' convenience. Always confirm the final document from your board / PMDC / FPSC. Have a correction? Email {EMAIL}.</p>
      </div>
    </div>
    <div style="margin-top:52px">
      <h2 style="font-size:1.4rem;margin-bottom:20px">More updates</h2>
      <div class="grid grid-3">{rel_cards}</div>
    </div>
  </div>
</section>"""
    try: iso = datetime.datetime.strptime(p["date"], "%B %d, %Y").date().isoformat()
    except Exception: iso = p["date"]
    ld = [breadcrumb_json([("Updates", "updates/"), (p["title"], f"updates/{p['slug']}/")]),
          {"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
           "description": p["excerpt"], "datePublished": iso, "dateModified": iso,
           "citation": [u for _n, u in p.get("sources", [])] or None,
           "image": f"{DOM}/assets/img/og-image.jpg", "mainEntityOfPage": f"{DOM}/updates/{p['slug']}/",
           "author": {"@type": "Organization", "name": "StudySapiens", "url": f"{DOM}/"},
           "publisher": {"@id": f"{DOM}/#org", "name": "StudySapiens",
                         "logo": {"@type": "ImageObject", "url": f"{DOM}/assets/img/logo.png"}},
           "articleSection": p["tag"], "inLanguage": "en"}]
    w(f"updates/{p['slug']}/index.html", layout(page_key="updates", depth=2,
        title=f"{p['title']} | StudySapiens",
        desc=(p["excerpt"] if len(p["excerpt"]) <= 158 else p["excerpt"][:152].rsplit(" ", 1)[0] + "…"),
        path=f"updates/{p['slug']}/", body=body, extra_ld=ld), priority="0.6", changefreq="monthly")
    SEARCH.append({"t": p["title"], "s": f"Update · {p['tag']} · {p['date']}", "u": f"updates/{p['slug']}/",
                   "c": "Update", "k": p["tag"]})

# ------------------------------------------------------------------
# BLOG. Teacher-written posts. Drop blogs/<slug>.md and rebuild. See blogs/README-BLOG.txt
# ------------------------------------------------------------------
BLOG_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blogs")

def _dedash(t):
    t = re.sub("\\s*\u2014\\s*", ": ", t)
    t = re.sub("\\s*\u2013\\s*", "-", t)
    return t

def md_inline(s):
    s = esc(s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy" decoding="async">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    return s

def md_to_html(md):
    """Tiny safe markdown: h2/h3, paragraphs, bold/italic, links, images, ul/ol, blockquote."""
    out, toc, items, para = [], [], [], []
    def flush():
        nonlocal items, para
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>"); para = []
        if items:
            tag, its = items
            out.append(f"<{tag}>" + "".join(f"<li>{md_inline(i)}</li>" for i in its) + f"</{tag}>"); items = []
    for raw in md.splitlines():
        t = raw.strip()
        if not t:
            flush(); continue
        if t.startswith("### "):
            flush(); out.append(f"<h3>{md_inline(t[4:])}</h3>")
        elif t.startswith("## "):
            flush()
            txt = re.sub(r"<[^>]+>", "", md_inline(t[3:]))
            sid = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            toc.append((sid, txt))
            out.append(f'<h2 id="{sid}">{md_inline(t[3:])}</h2>')
        elif t.startswith("# "):
            flush(); out.append(f"<h2>{md_inline(t[2:])}</h2>")
        elif re.match(r"^[-*] ", t):
            if para or (items and items[0] != "ul"): flush()
            if not items: items = ["ul", []]
            items[1].append(t[2:])
        elif re.match(r"^\d+[.)] ", t):
            if para or (items and items[0] != "ol"): flush()
            if not items: items = ["ol", []]
            items[1].append(re.sub(r"^\d+[.)] ", "", t))
        elif t.startswith("> "):
            flush(); out.append(f"<blockquote>{md_inline(t[2:])}</blockquote>")
        else:
            if items: flush()
            para.append(t)
    flush()
    return "\n".join(out), toc

def scan_blogs():
    """blogs/<slug>.md -> post dicts, newest first. Skips draft: true files."""
    posts = []
    if not os.path.isdir(BLOG_ROOT):
        return posts
    for fn in sorted(os.listdir(BLOG_ROOT)):
        if not fn.endswith(".md"):
            continue
        raw = _dedash(open(os.path.join(BLOG_ROOT, fn), encoding="utf-8").read())
        slug = fn[:-3]
        meta, body_md = {}, raw
        m = re.match(r"\A\s*---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            body_md = m.group(2)
        if meta.get("draft", "").lower() in ("1", "true", "yes"):
            continue
        title = meta.get("title") or pretty_label(slug)
        try:
            d = datetime.date.fromisoformat(meta.get("date", "2026-01-01")[:10])
        except ValueError:
            d = datetime.date(2026, 1, 1)
        try:
            du = datetime.date.fromisoformat(meta.get("updated", "")[:10]) if meta.get("updated") else d
        except ValueError:
            du = d
        tags = [x.strip() for x in meta.get("tags", "Study Tips").split(",") if x.strip()][:4] or ["Study Tips"]
        html_body, toc = md_to_html(body_md)
        words = len(re.sub(r"<[^>]+>", " ", html_body).split())
        desc = meta.get("description") or re.sub(r"<[^>]+>", " ", html_body).strip()
        desc = re.sub(r"\s+", " ", desc)
        if len(desc) > 158:
            desc = desc[:152].rsplit(" ", 1)[0] + "…"
        posts.append({"slug": slug, "title": title, "desc": desc,
                      "date": d.isoformat(), "date_h": f"{d.strftime('%B')} {d.day}, {d.year}",
                      "updated": du.isoformat(), "updated_h": f"{du.strftime('%B')} {du.day}, {du.year}",
                      "is_updated": du > d, "tags": tags,
                      "author": meta.get("author", "StudySapiens Team"),
                      "html": html_body, "toc": toc, "mins": max(1, round(words / 200))})
    posts.sort(key=lambda b: (b["date"], b["slug"]), reverse=True)
    return posts

def blog_card(b, R_, cls=""):
    tags = "".join(f'<span class="badge badge-gold">{esc(t)}</span>' if i == 0
                   else f'<span class="badge badge-navy">{esc(t)}</span>'
                   for i, t in enumerate(b["tags"][:2]))
    return f"""
<article class="update-card {cls}">
  <div class="up-top"><div style="display:flex;gap:6px;flex-wrap:wrap">{tags}</div>
    <div class="up-date">{icon("cal",13)} {esc(b["date_h"])} &middot; {b["mins"]} min read</div>
    <h3><a href="{R_}blog/{b['slug']}/">{esc(b["title"])}</a></h3>
  </div>
  <div class="up-body"><p>{esc(b["desc"])}</p>
    <a class="read-more" href="{R_}blog/{b['slug']}/">Read guide {icon("arrow",13)}</a>
  </div>
</article>"""

def build_blog(blogs):
    R = "../"
    cards = "".join(blog_card(b, R, "reveal") for b in blogs) or """
<div class="card" style="grid-column:1/-1;text-align:center;padding:40px 26px">
  <h3 style="margin-bottom:8px">First guides are in the writing stage</h3>
  <p class="muted" style="margin-bottom:0">Every guide is written by a teacher and fact checked before publishing. Tell us what you want to read about.</p>
</div>"""
    body = crumbs_html(R, [("Blog", "blog/")]) + page_hero(R,
        badge="Written by Teachers",
        title="Blog: Study Tips & Exam Guides",
        lead="Simple-English guides for Punjab board classes 9-12: study plans, exam strategy and syllabus explainers. No rumours, no filler.",
        actions=f'<a class="btn btn-primary btn-sm" href="#posts">{icon("notes",15)} Read Latest Posts</a>')
    body += f"""
<section class="section section-tight" id="posts">
  <div class="container"><div class="grid grid-3">{cards}</div>
  <div class="card" style="margin-top:36px;background:var(--gold-100);text-align:center;padding:28px">
    <h3 style="font-size:1.1rem;margin-bottom:6px">Request a topic</h3>
    <p class="muted" style="font-size:.92rem;margin-bottom:14px">Stuck on a topic? Email us and a teacher may write a full guide on it.</p>
    {join_updates_form(R)}
  </div></div>
</section>"""
    ld = [breadcrumb_json([("Blog", "blog/")])]
    w("blog/index.html", layout(page_key="blog", depth=1,
        title="Blog: Study Tips, Exam Guides & Syllabus News | StudySapiens",
        desc="Simple English study guides, exam strategies and syllabus news for Punjab board classes 9-12. Written and fact checked by teachers.",
        path="blog/", body=body, extra_ld=ld), priority="0.7", changefreq="weekly")
    SEARCH.append({"t": "Blog: Study Tips & Exam Guides", "s": "Blog · Study guides by teachers",
                   "u": "blog/", "c": "Blog", "k": "blog study tips exam guide"})

def build_blog_post(blogs, i):
    p = blogs[i]
    R = "../../"
    body_html = p["html"].replace('href="/', f'href="{R}').replace('src="/', f'src="{R}')
    toc_html = ""
    if len(p["toc"]) >= 2:
        toc_html = ('<nav class="toc-box no-print" aria-label="On this page"><b>On this page</b><ol>'
                    + "".join(f'<li><a href="#{sid}">{esc(txt)}</a></li>' for sid, txt in p["toc"])
                    + "</ol></nav>")
    spans = [f'{icon("cal",14)} {esc(p["date_h"])}']
    if p["is_updated"]:
        spans.append(f'{icon("refresh",14)} Updated {esc(p["updated_h"])}')
    spans += [f'{icon("teacher",14)} {esc(p["author"])}', f'{icon("clock",14)} {p["mins"]} min read']
    meta = '<div class="art-meta">' + "".join(f"<span>{s}</span>" for s in spans) + "</div>"
    chips = "".join(f'<span class="badge badge-gold">{esc(t)}</span>' if j == 0
                    else f'<span class="badge badge-navy">{esc(t)}</span>'
                    for j, t in enumerate(p["tags"]))
    chips = f'<div style="display:flex;gap:6px;flex-wrap:wrap">{chips}</div>'
    newer = blogs[i - 1] if i > 0 else None
    older = blogs[i + 1] if i + 1 < len(blogs) else None
    pn = ""
    if newer or older:
        a = (f'<a href="{R}blog/{newer["slug"]}/"><span>&larr; Newer</span>{esc(newer["title"][:60])}</a>' if newer
             else "<a style=\"visibility:hidden\"></a>")
        b2 = (f'<a class="next" href="{R}blog/{older["slug"]}/"><span>Older &rarr;</span>{esc(older["title"][:60])}</a>' if older
              else "<a class=\"next\" style=\"visibility:hidden\"></a>")
        pn = f'<div class="pnav no-print">{a}{b2}</div>'
    tagset = set(p["tags"])
    rest = [x for x in blogs if x["slug"] != p["slug"]]
    rel = sorted(rest, key=lambda x: 0 if tagset & set(x["tags"]) else 1)[:3]
    rel_cards = "".join(blog_card(x, R) for x in rel) or '<p class="muted">More guides coming soon.</p>'
    body = crumbs_html(R, [("Blog", "blog/"), (p["title"], f"blog/{p['slug']}/")])
    body += f"""
<section class="section" style="padding-top:44px">
  <div class="container">
    <article class="article">
      {chips}
      <h1 style="margin-top:12px">{esc(p["title"])}</h1>
      {meta}
      {toc_html}
      <div class="article-body">{body_html}</div>
      {share_row()}
      {pn}
      <div class="author-box">
        <img src="{R}assets/img/mark.png" alt="StudySapiens mark" width="52" height="52">
        <div><b>{esc(p["author"])}</b>
        <p class="small muted" style="margin:4px 0 0">Every StudySapiens guide is written by a teacher and fact checked against official board documents before publishing. Spot a mistake? Email {EMAIL}.</p></div>
      </div>
    </article>
    <div style="margin-top:52px">
      <h2 style="font-size:1.4rem;margin-bottom:20px">More from the blog</h2>
      <div class="grid grid-3">{rel_cards}</div>
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Blog", "blog/"), (p["title"], f"blog/{p['slug']}/")]),
          {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
           "description": p["desc"], "datePublished": p["date"], "dateModified": p["updated"],
           "image": f"{DOM}/assets/img/og-image.jpg", "mainEntityOfPage": f"{DOM}/blog/{p['slug']}/",
           "author": {"@type": "Organization", "name": "StudySapiens", "url": f"{DOM}/"},
           "publisher": {"@id": f"{DOM}/#org"},
           "articleSection": p["tags"][0], "keywords": ", ".join(p["tags"]), "inLanguage": "en"}]
    w(f"blog/{p['slug']}/index.html", layout(page_key="blog", depth=2,
        title=f"{p['title']} | StudySapiens",
        desc=p["desc"], path=f"blog/{p['slug']}/", body=body, extra_ld=ld),
        priority="0.7", changefreq="monthly")
    SEARCH.append({"t": p["title"], "s": f"Blog · {p['tags'][0]} · {p['date_h']}",
                   "u": f"blog/{p['slug']}/", "c": "Blog", "k": " ".join(p["tags"])})

# ------------------------------------------------------------------
# About / Contact / Privacy / Site-map
# ------------------------------------------------------------------
def build_about():
    R = "../"
    body = crumbs_html(R, [("About", "about/")]) + page_hero(R,
        badge="Our Story",
        title="Teachers Building Better Study Resources",
        lead="StudySapiens started with a simple frustration: when Punjab changed the syllabus, students deserved honest, updated study material. And couldn't find it anywhere.",
        actions=f'<a class="btn btn-primary btn-sm" href="{R}contact/">{icon("mail",15)} Say Salaam to Us</a>')
    body += f"""
<section class="section section-tight">
  <div class="container" style="max-width:860px">
    <div class="article">
      <h2 style="font-size:1.5rem;margin-bottom:14px">Why StudySapiens exists</h2>
      <p>When PCTB (now PECTAA) introduced the new books for matric and intermediate, everything students relied on turned upside down overnight. Searching for notes of the <i>new</i> books meant clicking through websites that:</p>
      <ul>
        <li>slapped “New Syllabus 2026” on articles that still taught the old books,</li>
        <li>mixed up chapter numbers so badly that even teachers got confused.</li>
      </ul>
      <p>As teachers, we saw students struggle to find clear material that matched the new books. We built StudySapiens to help. Our resources are <b>made by teachers and verified by subject experts</b>, with the right book, right chapter and simple words. Study materials are free for every student.</p>
      <div class="callout">Every note here is written or checked by a teacher before publishing. If a chapter is not ready yet, we say so honestly instead of uploading filler.</div>
      <h2 style="font-size:1.5rem;margin:30px 0 16px">What we stand for</h2>
    </div>
    <div class="grid grid-4">
      <div class="feature-card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("check",22)}</div>
        <h3 style="font-size:1rem">Accuracy</h3><p class="small">Chapter numbers always match your printed book.</p></div>
      <div class="feature-card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("shieldx",22)}</div>
        <h3 style="font-size:1rem">Made by Teachers</h3><p class="small">Study materials are created by teachers and verified by subject experts.</p></div>
      <div class="feature-card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("zap",22)}</div>
        <h3 style="font-size:1rem">Easy English</h3><p class="small">Written for students whose first language isn't English.</p></div>
      <div class="feature-card center"><div class="icon-tile" style="margin:0 auto 12px;background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("money",22)}</div>
        <h3 style="font-size:1rem">Free Forever</h3><p class="small">Education money shouldn't gatekeep. Every note and tool here stays free.</p></div>
    </div>
    <div class="article" style="margin-top:44px">
      <h2 style="font-size:1.5rem;margin-bottom:14px">What's coming next (roadmap)</h2>
      <ul>
        <li><b>Urdu-medium notes</b> for science subjects</li>
        <li><b>Video explanations</b> of hard chapters</li>
        <li><b>Urdu translations & summaries</b> for every English lesson</li>
        <li><b>Daily MCQ challenges</b> and leaderboards for MDCAT</li>
        <li><b>A mobile app</b>, once the web version is rock-solid</li>
      </ul>
      <p style="margin-top:16px">Want to suggest a feature, report a mistake, or contribute notes as a fellow teacher? Email <b>{EMAIL}</b>. Real humans reply.</p>
    </div>
    {share_row()}
  </div>
</section>"""
    ld = [breadcrumb_json([("About", "about/")])]
    w("about/index.html", layout(page_key="about", depth=1,
        title="About StudySapiens: Made by Teachers",
        desc="StudySapiens resources are made by teachers and verified by subject experts for Punjab board students.",
        path="about/", body=body, extra_ld=ld), priority="0.6")
    SEARCH.append({"t": "About StudySapiens", "s": "our story & mission", "u": "about/", "c": "Page", "k": "teacher mission story"})

def build_contact():
    R = "../"
    topics = "".join(f'<option>{t}</option>' for t in CONTACT_TOPICS)
    body = crumbs_html(R, [("Contact", "contact/")]) + page_hero(R,
        badge="We Actually Reply",
        title="Contact StudySapiens",
        lead="Correction in a note? Need a specific paper? Want to say thank you (we love those)? Write to us. A teacher reads every message.",
        actions=f'<a class="btn btn-primary btn-sm" href="mailto:{EMAIL}">{icon("mail",15)} {EMAIL}</a>')
    body += f"""
<section class="section section-tight">
  <div class="container">
    <div class="calc-wrap">
      <div class="form-card reveal-l">
        <h2 style="font-size:1.3rem;margin-bottom:6px">Send a Message</h2>
        <p class="muted small" style="margin-bottom:20px">Fill this in. Your email app will open with everything written. Just press send.</p>
        <form data-mailto="{EMAIL}" data-subject="StudySapiens. Contact Form">
          <div class="f-2col">
            <div class="f-row"><label>Your name *</label><input name="name" required placeholder="e.g. Ayesha Khan"></div>
            <div class="f-row"><label>Your email *</label><input type="email" name="reply_email" required placeholder="you@example.com"></div>
          </div>
          <div class="f-2col">
            <div class="f-row"><label>Your class</label><select name="class"><option>Class 9</option><option>Class 10</option><option>Class 11 (1st year)</option><option>Class 12 (2nd year)</option><option>MDCAT</option><option>CSS</option><option>Other/Parent</option></select></div>
            <div class="f-row"><label>Topic *</label><select name="topic">{topics}</select></div>
          </div>
          <div class="f-row"><label>Message *</label><textarea name="message" rows="5" required placeholder="Write clearly, e.g. 'In Class 9 Physics Chapter 1 MCQ 6, I think…'"></textarea></div>
          <button class="btn btn-primary btn-lg" type="submit" style="width:100%">{icon("mail",17)} Compose Email</button>
          <div class="form-success">Your email app opened. Press Send there and we'll reply, InshaAllah ✔</div>
          <p class="form-note">By sending, you agree to a reply at your given email. We reply within 1-2 working days (faster in exam season).</p>
        </form>
      </div>
      <div>
        <div class="card reveal-r" style="margin-bottom:18px">
          <div class="icon-tile" style="background:linear-gradient(135deg,var(--navy-700),var(--navy-600))">{icon("mail",22)}</div>
          <h3 style="font-size:1.05rem">Email (fastest)</h3>
          <p class="muted small" style="margin-bottom:8px">For corrections, requests and feedback.</p>
          <a class="btn btn-ghost btn-sm" href="mailto:{EMAIL}">{EMAIL}</a>
          <button class="btn btn-ghost btn-sm" data-copy="{EMAIL}" style="margin-left:6px">{icon("link",13)} Copy</button>
        </div>
        <div class="card reveal-r" data-delay="1" style="margin-bottom:18px">
          <div class="icon-tile" style="background:linear-gradient(135deg,#FFFDF7,#EAE7D3);color:var(--navy-900)">{icon("bell",22)}</div>
          <h3 style="font-size:1.05rem">Exam-season alerts</h3>
          <p class="muted small" style="margin-bottom:10px">Join the free list: schemes, date sheets, new chapters. Straight to your inbox.</p>
          {join_updates_form(R)}
        </div>
        <div class="card reveal-r" data-delay="2">
          <div class="icon-tile" style="background:linear-gradient(135deg,var(--teal),#0E8C8A)">{icon("shield",22)}</div>
          <h3 style="font-size:1.05rem">Quick answers</h3>
          <p class="muted small">Most questions are already answered on our <a href="{R}#faq"><b>FAQ section</b></a> (is it free, how are resources verified, which boards…). Teachers who want to contribute notes: mention your subject & city. We'd love to have you.</p>
        </div>
      </div>
    </div>
  </div>
</section>"""
    ld = [breadcrumb_json([("Contact", "contact/")])]
    w("contact/index.html", layout(page_key="contact", depth=1,
        title="Contact StudySapiens: Corrections, Requests & Feedback",
        desc="Contact the StudySapiens team: report a mistake, request notes or papers, or suggest an improvement. Email admin.studysapiens@gmail.com. Real teachers reply.",
        path="contact/", body=body, extra_ld=ld), priority="0.6")
    SEARCH.append({"t": "Contact Us", "s": "corrections, requests, feedback", "u": "contact/", "c": "Page", "k": "email help support"})

def build_privacy():
    R = "../"
    body = crumbs_html(R, [("Privacy Policy", "privacy-policy/")]) + f"""
<section class="section">
  <div class="container article" style="max-width:820px">
    <h1>Privacy Policy</h1>
    <div class="art-meta"><span>{icon("cal",14)} Last updated: July 2026</span></div>
    <div class="article-body">
      <p>StudySapiens ("we", "our site") is a free educational website for students of Punjab boards. This page explains, in simple words, what information we handle and what we never do with it.</p>
      <h2>What we collect</h2>
      <ul>
        <li><b>Information you type:</b> if you email us or use a contact or subscribe form, we receive your name, email and message. The quiz and calculator run entirely in your browser. Answers and marks never leave your device.</li>
        <li><b>Basic analytics:</b> we may use privacy-respecting analytics (e.g. page counts) to know which chapters students need most. No personal profiles are built.</li>
      </ul>
      <h2>What we never do</h2>
      <ul>
        <li>We never sell, rent or share your personal information with advertisers.</li>
        <li>We don't require accounts, and we don't store test scores.</li>
      </ul>
      <h2>Cookies & third parties</h2>
      <p>External sites we link to (eLearn Punjab, PMDC, FPSC and education boards) have their own privacy policies. We will update this policy if the site adds features that change how information is handled.</p>
      <h2>Students under 13</h2>
      <p>Our content is safe for all ages. Younger students should use the contact forms with a parent/guardian's email.</p>
      <h2>Contact</h2>
      <p>Questions about privacy? Email <b>{EMAIL}</b>.</p>
    </div>
  </div>
</section>"""
    w("privacy-policy/index.html", layout(page_key="privacy", depth=1,
        title="Privacy Policy | StudySapiens",
        desc="StudySapiens privacy policy. No data selling, no forced sign-ups, no intrusive ads. How we handle your information, in simple words.",
        path="privacy-policy/", body=body), priority="0.3", changefreq="yearly")

def build_sitemap_page():
    R = "../"
    cls = ""
    for cid in CLASSES:
        rows = "".join(f'<li><a href="{R}classes/{cid}/{s}/">{SUBJECTS[s]["name"]}</a></li>' for s in subjects_for(cid))
        cls += f'<div class="card"><h3 style="margin-bottom:10px"><a href="{R}classes/{cid}/">{CLASSES[cid]["name"]}</a></h3><ul class="f-links" style="color:var(--ink-soft)">{rows}</ul></div>'
    other = "".join(f'<li><a href="{R}{p}">{l}</a></li>' for l, p in [
        ("Smart Syllabus","smart-syllabus/"),("Pairing Schemes","pairing-scheme/"),("Guess Papers","guess-papers/"),("Past Papers","past-papers/"),
        ("Date Sheets","date-sheet/"),("MDCAT & Calculator","mdcat/"),("ECAT & Calculator","ecat/"),("CSS Guide","css/"),("eBooks","ebooks/"),
        ("Results","results/"),("Online Tests","tests/"),("Model Papers","model-papers/"),("Formula Sheets","formulas/"),
        ("English Corner","english-corner/"),("Roll Number Slip","roll-number-slip/"),("Boards","boards/"),
        ("Updates","updates/"),("Blog","blog/"),("About","about/"),("Contact","contact/"),("Privacy Policy","privacy-policy/")])
    body = crumbs_html(R, [("Site Map","site-map/")]) + page_hero(R, badge="Everything, one page",
        title="Site Map", lead="Every main page of StudySapiens. Looking for notes? Open your subject: the study guide and all downloads live inside.")
    body += f"""
<section class="section section-tight"><div class="container">
  <div class="grid grid-4">{cls}</div>
  <div class="card" style="margin-top:26px"><h3 style="margin-bottom:10px">Resources & Company</h3><ul class="f-links" style="columns:2;color:var(--ink-soft)">{other}</ul></div>
</div></section>"""
    w("site-map/index.html", layout(page_key="sitemap", depth=1,
        title="Site Map: Every Page of StudySapiens", desc="Full site map of StudySapiens: classes, subjects, resources and company pages.",
        path="site-map/", body=body), priority="0.4", changefreq="monthly")


SW_JS = r"""
/* StudySapiens service worker. V1 */
const VERSION = 'ss-v13';
const CORE = [
  './', 'classes/', 'pairing-scheme/', 'mdcat/', 'date-sheet/', 'offline/',
  'assets/css/style.css', 'assets/js/main.js',
  'assets/img/logo-trim-light.png', 'assets/img/mark.png', 'assets/img/favicon-32.png',
  'assets/img/favicon-64.png', 'assets/img/favicon-180.png', 'assets/img/hero-1300.webp',
  'assets/img/og-image.jpg', 'site.webmanifest'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('message', e => {
  if (e.data && e.data.type === 'CACHE_URLS' && Array.isArray(e.data.urls)) {
    caches.open(VERSION).then(c => c.addAll(e.data.urls)).catch(() => {});
  }
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Pages: network-first, fall back to cache, then the offline page
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone();
      caches.open(VERSION).then(c => c.put(req, copy));
      return res;
    }).catch(() => caches.match(req).then(cached => cached || caches.match('offline/'))));
    return;
  }

  // Assets (css/js/img/fonts incl. Google Fonts): stale-while-revalidate
  e.respondWith(caches.match(req).then(cached => {
    const network = fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(req, copy));
      }
      return res;
    }).catch(() => cached);
    return cached || network;
  }));
});
"""

def build_404():
    R = "/"   # served at any URL depth by the host → root-absolute links
    pops = "".join(f'<a class="btn btn-ghost btn-sm" href="{R}{u}">{l}</a>' for l, u in [
        ("Class 9 Physics Notes", "classes/9/physics/"), ("1st Year Physics Notes", "classes/11/physics/"),
        ("Pairing Schemes", "pairing-scheme/"), ("MDCAT Calculator", "mdcat/"), ("Guess Papers", "guess-papers/")])
    body = f"""
<section class="page-hero" style="padding:64px 0 54px">
  <div class="container" style="text-align:center">
    <span class="badge badge-gold">Error 404</span>
    <h1>Lost? Let's Get You <em>Back on Track</em></h1>
    <p class="lead" style="margin-left:auto;margin-right:auto">The page you asked for isn't here. Maybe a mistyped link or a moved note. Everything important is one click below.</p>
  </div>
</section>
<section class="section section-tight" style="text-align:center">
  <div class="container" style="max-width:740px">
    <button class="btn btn-primary btn-lg" data-open-search>{icon("search",17)} Search All Notes</button>
    <a class="btn btn-outline btn-lg" href="{R}">{icon("home",17)} Back to Home</a>
    <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:30px">{pops}</div>
  </div>
</section>"""
    w("404.html", layout(page_key="404", depth=1,
        title="Page Not Found (404) | StudySapiens",
        desc="The page you requested could not be found. Search free notes, schemes and past papers for Class 9-12 on StudySapiens.",
        path="404.html", body=body, noindex=True, abs_paths=True))

def build_offline():
    R = "../"
    body = f"""
<section class="page-hero" style="padding:60px 0 50px">
  <div class="container" style="text-align:center">
    <span class="badge badge-gold">{icon("zap",13)} You are offline</span>
    <h1>No Internet? No Problem.</h1>
    <p class="lead" style="margin-left:auto;margin-right:auto">Pages you visited before still open normally from the offline cache. Try one below.</p>
  </div>
</section>
<section class="section section-tight">
  <div class="container" style="max-width:720px;text-align:center">
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
      <a class="btn btn-primary" href="{R}classes/">{icon("grid",16)} Open Classes</a>
      <a class="btn btn-dark" href="{R}">{icon("home",16)} Home (cached)</a>
      <button class="btn btn-ghost" onclick="location.reload()">{icon("refresh",15)} Retry Connection</button>
    </div>
    <script>window.addEventListener("online",function(){{location.reload()}});</script>
    <p class="small muted" style="margin-top:22px">StudySapiens works offline. Install it from your browser's "Add to Home Screen" for the app experience.</p>
  </div>
</section>"""
    w("offline/index.html", layout(page_key="offline", depth=1,
        title="Offline Mode: StudySapiens",
        desc="You appear to be offline. Previously visited StudySapiens pages still open without internet.",
        path="offline/", body=body, noindex=True))

# ------------------------------------------------------------------
# SEO files
# ------------------------------------------------------------------
def write_seo():
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{DOM}/{u}</loc><lastmod>{today}</lastmod><changefreq>{cf}</changefreq><priority>{p}</priority></url>\n"
                   for u, p, cf in URLS)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>'
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f: f.write(sitemap)
    # robots.txt: allow classic crawlers AND the reputable AI answer/search bots.
    # GEO logic: we want ChatGPT/Gemini/Perplexity to read and cite us.
    AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended",
               "CCBot", "cohere-ai"]
    robots = ["User-agent: *", "Allow: /", "Disallow: /offline/", ""]
    for bot in AI_BOTS:
        robots += [f"User-agent: {bot}", "Allow: /", ""]
    robots += [f"Sitemap: {DOM}/sitemap.xml", ""]
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("\n".join(robots))

    # ---- llms.txt: the emerging AI-discovery standard (like robots for LLMs)
    boards_line = ", ".join(b["short"] for b in BOARDS[:-1]) + f" and {BOARDS[-1]['short']}"
    llms = f"""# StudySapiens

> Free study resources for Pakistani students of Class 9-12 on the new PCTB / PECTAA syllabus. Made by teachers and verified by subject experts. Includes notes, solved exercises, MCQ banks, pairing schemes, guess papers, date sheets, results guidance, MDCAT / ECAT / CSS guides. All nine Punjab boards: {boards_line}.

## Trust policy (why our answers are citable)
- Every downloadable file is checked by a teacher against the printed official book before it goes live.
- Dates and schedules are published only after an official announcement. Until then they are clearly labelled "Expected".
- Corrections by email within a day: admin.studysapiens@gmail.com.

## Key facts (canonical answers)
- MDCAT aggregate formula (UHS, public sector): Matric 10% + FSc 40% + MDCAT 50%. Eligibility: 55% MDCAT for MBBS, 50% for BDS.
- ECAT / UET aggregate formula: Matric 17% + FSc 50% + ECAT 33%. The ECAT paper is out of 400 marks.
- New syllabus rollout: Class 9 and Class 11 from 2025-26, Class 10 and Class 12 from 2026-27 (PECTAA books).

## Core pages
- [Classes 9-12 notes & downloads]({DOM}/classes/): per-subject guides with free PDFs
- [MDCAT Corner + aggregate calculator]({DOM}/mdcat/): 50/40/10 formula, pattern, syllabus
- [ECAT Corner + UET calculator]({DOM}/ecat/): 17/50/33 formula and admission roadmap
- [Date sheets]({DOM}/date-sheet/), [Results 2027]({DOM}/results/), [Pairing schemes]({DOM}/pairing-scheme/)
- [Guess papers]({DOM}/guess-papers/) and [Past papers]({DOM}/past-papers/) for all 9 boards
- [Latest verified updates]({DOM}/updates/) and [study blog]({DOM}/blog/)
- [eBooks: official free PDFs]({DOM}/ebooks/), [Online MCQ tests]({DOM}/tests/)

## Contact
- Email: admin.studysapiens@gmail.com
- Contact page: {DOM}/contact/
"""
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms)

    # ---- RSS feed (updates + blog): helps Google News-style & AI aggregators find new content fast
    def _iso(disp):
        try: return datetime.datetime.strptime(disp, "%B %d, %Y").date().isoformat()
        except Exception: return "2026-01-01"
    items = [(_iso(p["date"]), p["title"], f"updates/{p['slug']}/", p["excerpt"], p.get("tag", "Update")) for p in UPDATES]
    for b in globals().get("BLOGS", []):
        items.append((b["date"], b["title"], f"blog/{b['slug']}/", b["desc"], "Blog"))
    items.sort(key=lambda x: x[0], reverse=True)

    def _rfc(iso):
        try:
            d = datetime.date.fromisoformat(iso[:10])
            return datetime.datetime(d.year, d.month, d.day, 9, 0).strftime("%a, %d %b %Y %H:%M:%S +0500")
        except Exception:
            return ""
    rss_items = "".join(
        f"  <item><title>{esc(t)}</title><link>{DOM}/{u}</link><guid>{DOM}/{u}</guid>"
        f"<pubDate>{_rfc(d)}</pubDate><category>{esc(cat)}</category>"
        f"<description>{esc(x)}</description></item>\n" for d, t, u, x, cat in items)
    rss = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<rss version="2.0"><channel><title>StudySapiens</title><link>{DOM}/</link>'
           f'<description>Verified study updates for Punjab board students: new syllabus books, date sheets, results, MDCAT &amp; study guides.</description>'
           f'<language>en</language><lastBuildDate>{_rfc(datetime.date.today().isoformat())}</lastBuildDate>\n'
           f'{rss_items}</channel></rss>')
    with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss)
    manifest = (
        '{\n'
        '  "name": "StudySapiens - New PCTB Syllabus Notes",\n'
        '  "short_name": "StudySapiens",\n'
        '  "description": "Free notes, exercise solutions, MCQ tests, pairing schemes and guess papers for the new PCTB / PECTAA syllabus - Class 9-12, all Punjab boards.",\n'
        '  "start_url": "/",\n'
        '  "display": "standalone",\n'
        '  "background_color": "#F6F2E7",\n'
        '  "theme_color": "#2E3324",\n'
        '  "icons": [\n'
        '    { "src": "assets/img/favicon-64.png",  "sizes": "64x64",   "type": "image/png" },\n'
        '    { "src": "assets/img/favicon-180.png", "sizes": "180x180", "type": "image/png" },\n'
        '    { "src": "assets/img/icon-512.png",    "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }\n'
        '  ]\n'
        '}\n')
    with open(os.path.join(OUT, "site.webmanifest"), "w") as f: f.write(manifest)
    with open(os.path.join(OUT, "sw.js"), "w") as f: f.write(SW_JS)
    headers = ("/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "  Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://www.googletagmanager.com; connect-src 'self' https://www.google-analytics.com https://analytics.google.com; manifest-src 'self'; worker-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self' mailto:; object-src 'none'\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "/files/*\n"
        "  Cache-Control: public, max-age=86400\n"
        "  Content-Disposition: inline\n"
        "*.html\n"
        "  Cache-Control: public, max-age=0, must-revalidate\n"
        "/sw.js\n"
        "  Cache-Control: no-cache\n")
    with open(os.path.join(OUT, "_headers"), "w") as f: f.write(headers)
    # Apache / LiteSpeed version of _headers (for cPanel-style shared hosting)
    htaccess = ("# StudySapiens .htaccess - Apache / LiteSpeed\n"
        "# Mirrors the Netlify _headers rules and serves the custom 404 page.\n"
        "DirectoryIndex index.html\n"
        "ErrorDocument 404 /404.html\n"
        "<IfModule mod_headers.c>\n"
        "  Header always set X-Content-Type-Options \"nosniff\"\n"
        "  Header always set Referrer-Policy \"strict-origin-when-cross-origin\"\n"
        "  Header always set Permissions-Policy \"camera=(), microphone=(), geolocation=()\"\n"
        "  Header always set X-Frame-Options \"SAMEORIGIN\"\n"
        "  Header always set Content-Security-Policy-Report-Only \"default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://www.googletagmanager.com; connect-src 'self' https://www.google-analytics.com https://analytics.google.com; manifest-src 'self'; worker-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self' mailto:; object-src 'none'\"\n"
        "  <FilesMatch \"\\.(css|js|jpg|jpeg|png|webp|svg|ico|woff2?)$\">\n"
        "    Header set Cache-Control \"public, max-age=31536000, immutable\"\n"
        "  </FilesMatch>\n"
        "  <FilesMatch \"\\.pdf$\">\n"
        "    Header set Cache-Control \"public, max-age=86400\"\n"
        "    Header set Content-Disposition \"inline\"\n"
        "  </FilesMatch>\n"
        "  <FilesMatch \"\\.html?$\">\n"
        "    Header set Cache-Control \"public, max-age=0, must-revalidate\"\n"
        "  </FilesMatch>\n"
        "  <FilesMatch \"^sw\\.js$\">\n"
        "    Header set Cache-Control \"no-cache\"\n"
        "  </FilesMatch>\n"
        "</IfModule>\n")
    with open(os.path.join(OUT, ".htaccess"), "w") as f: f.write(htaccess)
    with open(os.path.join(OUT, "search.json"), "w") as f:
        json.dump(SEARCH, f, ensure_ascii=False)

# ------------------------------------------------------------------
# main
# ------------------------------------------------------------------
def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(os.path.dirname(OUT), "assets"), os.path.join(OUT, "assets"))
    _css = os.path.join(OUT, "assets/css/style.css")
    with open(_css) as f: cs = f.read()
    cs = re.sub(r"/\*.*?\*/", "", cs, flags=re.S)
    cs = re.sub(r"\s+", " ", cs)
    cs = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", cs)
    cs = cs.replace(";}", "}").strip()
    with open(_css, "w") as f: f.write(cs)
    # main.js: ship comment-stripped copy; source stays readable in assets/.
    # Any doubt (no node, syntax error) -> fall back to shipping the raw file.
    _js_src = os.path.join("assets", "js", "main.js")
    _js_out = os.path.join(OUT, "assets", "js", "main.js")
    try:
        with open(_js_src, encoding="utf-8") as f: _js = f.read()
        _min = _minify_js(_js)
        with open(_js_out, "w", encoding="utf-8") as f: f.write(_min)
        node = shutil.which("node")
        if node:
            r = subprocess.run([node, "--check", _js_out], capture_output=True)
            if r.returncode != 0:
                err = r.stderr.decode()[:400]
                raise RuntimeError("node --check rejected minified JS: " + err)
        print(f"   🗜  main.js minified: {len(_js)//1024} KB -> {len(_min)//1024} KB" + (" (node-verified)" if node else " (node missing, syntax check skipped)"))
    except Exception as e:
        shutil.copyfile(_js_src, _js_out)
        print(f"   ⚠️  JS minify skipped, shipped raw main.js. Reason: {e}")
    global FILES, EXTRA_FILES
    FILES = scan_files()
    EXTRA_FILES = scan_extra()
    BLOGS = scan_blogs()
    if os.path.isdir(FILES_ROOT):
        shutil.copytree(FILES_ROOT, os.path.join(OUT, "files"), ignore=shutil.ignore_patterns("*.txt"))
    build_home(BLOGS)
    build_classes()
    build_smart_syllabus()
    for cid in CLASSES:
        build_class(cid)
        for sid in subjects_for(cid):
            build_subject(cid, sid)
    build_pairing()
    build_guess(); build_past(); build_datesheet()
    build_ebooks(); build_mdcat(); build_css_page()
    build_results()
    for cid in CLASSES: build_result_class(cid)
    build_roll_slip(); build_model_papers(); build_formulas(); build_english_corner()
    build_boards()
    for b in BOARDS: build_board(b)
    build_tests(); build_ecat()
    build_blog(BLOGS)
    for bi in range(len(BLOGS)): build_blog_post(BLOGS, bi)
    build_updates()
    for p in UPDATES: build_post(p)
    build_about(); build_contact(); build_privacy(); build_offline(); build_404(); build_sitemap_page()
    write_seo()
    pages = len(URLS)
    print(f"✅ Done. {pages} pages generated in ./site/  (+search.json {len(SEARCH)} entries, sitemap.xml, robots.txt)")
    print(f"   📁 {file_count()} uploaded file(s) published from ./files/")

if __name__ == "__main__":
    main()

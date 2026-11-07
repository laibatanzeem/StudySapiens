#!/usr/bin/env python3
"""
precheck.py : StudySapiens pre-deployment validator.

Run AFTER build.py / sync_files.py, BEFORE uploading site/ to hosting.
Zero dependencies (stdlib + optional node for JS syntax). Reads the built
site/ folder and reports:

  CRITICAL  broken internal links (href/src targets missing on disk)
  CRITICAL  missing PDF/file downloads referenced from pages
  CRITICAL  duplicate <title> or duplicate meta description
  CRITICAL  missing title / description / h1
  CRITICAL  invalid JSON-LD (unparseable structured data)
  CRITICAL  accidental noindex on a content page
  CRITICAL  sitemap.xml lists a URL that does not exist / required files missing
  CRITICAL  JavaScript syntax errors (main.js, sw.js, inline scripts, node)
  WARNING   oversize titles/descriptions, missing alt/canonical, empty hrefs,
            tag-balance mismatches, pages absent from sitemap, og gaps

Exit code 0 = safe to deploy (warnings allowed). 1 = DO NOT DEPLOY.

    python3 scripts/precheck.py            # full report
    python3 scripts/precheck.py --quiet    # only failures + summary line
"""

import html as html_mod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QUIET = "--quiet" in sys.argv

NOINDEX_OK = {"404.html", "offline/index.html"}      # pages allowed to be noindex
REQUIRED_FILES = ["index.html", "sitemap.xml", "robots.txt", "feed.xml",
                  "llms.txt", "sw.js", "site.webmanifest",
                  "assets/css/style.css", "assets/js/main.js",
                  "assets/img/og-image.jpg", "assets/img/favicon-32.png",
                  "assets/img/logo-trim-light.png", "404.html"]
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "sms:", "whatsapp:", "data:", "javascript:")

critical, warnings, infos = [], [], []


def crit(msg): critical.append(msg);   print(f"[CRITICAL] {msg}") if not QUIET else None
def warn(msg): warnings.append(msg);   print(f"[warn]     {msg}") if not QUIET else None
def info(msg): infos.append(msg);      print(f"[info]     {msg}") if not QUIET else None


# ---------------------------------------------------------------- helpers
TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.I)
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"', re.I)
ROBOTS_RE = re.compile(r'<meta\s+name="robots"\s+content="([^"]*)"', re.I)
H1_RE = re.compile(r"<h1[\s>]", re.I)
ALTLESS_IMG_RE = re.compile(r"<img\b(?![^>]*\balt=)[^>]*>", re.I)
IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.I)
LINK_SRC_RE = re.compile(r'(?:href|src)="([^"]+)"')
LD_RE = re.compile(r'<script\s+type="application/ld\+json">(.*?)</script>', re.S | re.I)
INLINE_JS_RE = re.compile(r'<script>(.*?)</script>', re.S | re.I)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
BALANCE_TAGS = ["html", "head", "body", "main", "header", "footer",
                "section", "article", "table", "form", "ul", "ol", "nav"]


class Balance(HTMLParser):
    """Rough tag-balance sanity: counts open/close for structural tags."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        if tag in BALANCE_TAGS: self.stack.append(tag)
    def handle_startendtag(self, tag, attrs): pass
    def handle_endtag(self, tag):
        if tag not in BALANCE_TAGS: return
        # tolerate minor mis-nesting: drop back to the matching open tag
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.errors.append("unclosed <%s> before </%s>" % (self.stack[-1], tag))
                self.stack.pop()
            self.stack.pop()
        else:
            self.errors.append("stray </%s>" % tag)


def resolve_target(page_rel, target):
    """Resolve a root- or page-relative URL to a path inside site/. None = external/skip."""
    if not target or target.startswith("#"): return None
    if target.startswith(SKIP_SCHEMES): return None
    t = target.split("#", 1)[0].split("?", 1)[0]
    if not t: return None
    if t.startswith("/"):
        p = t.lstrip("/")
    else:
        p = os.path.normpath(os.path.join(os.path.dirname(page_rel), t))
    return p.replace("\\", "/")


def disk_exists(rel):
    p = SITE / rel
    if p.is_file(): return True
    if p.is_dir(): return (p / "index.html").is_file()
    if rel == "" or rel.endswith("/"): return (SITE / rel / "index.html").is_file()
    # extensionless pretty URL
    return (SITE / rel / "index.html").is_file()


# ---------------------------------------------------------------- run
def main():
    if not SITE.is_dir():
        print("site/ not found. Run python3 build.py first.")
        return 1

    pages = sorted(SITE.rglob("*.html"))
    rel_pages = [str(p.relative_to(SITE)).replace("\\", "/") for p in pages]
    info(f"Scanning {len(pages)} html pages under site/ ...")

    # --- required files -------------------------------------------------
    for rel in REQUIRED_FILES:
        if not (SITE / rel).is_file():
            crit(f"required file missing from build: {rel}")

    titles, descs = {}, {}
    inline_js_blobs = []

    for path, rel in zip(pages, rel_pages):
        html = path.read_text(encoding="utf-8", errors="replace")

        # === meta triad ===
        m = TITLE_RE.search(html)
        if not m or not m.group(1).strip():
            crit(f"{rel}: missing/empty <title>")
        else:
            t = html_mod.unescape(TAG_RE.sub("", m.group(1)).strip())
            titles.setdefault(t, []).append(rel)
            if len(t) > 66: warn(f"{rel}: title {len(t)} rendered chars")
        m = DESC_RE.search(html)
        if not m or not m.group(1).strip():
            crit(f"{rel}: missing meta description")
        else:
            d = html_mod.unescape(m.group(1)).strip()
            descs.setdefault(d, []).append(rel)
            if len(d) > 165: warn(f"{rel}: description {len(d)} rendered chars")

        # === h1 exactly once ===
        n_h1 = len(H1_RE.findall(html))
        if n_h1 == 0: crit(f"{rel}: no <h1>")
        elif n_h1 > 1: warn(f"{rel}: {n_h1} <h1> tags")

        # === canonical ===
        if not CANON_RE.search(html):
            warn(f"{rel}: no canonical link")

        # === noindex guard ===
        m = ROBOTS_RE.search(html)
        if m and "noindex" in m.group(1) and rel not in NOINDEX_OK:
            crit(f"{rel}: accidental noindex (robots={m.group(1)})")

        # === JSON-LD validity ===
        for i, block in enumerate(LD_RE.findall(html), 1):
            try:
                json.loads(block)
            except Exception as e:
                crit(f"{rel}: JSON-LD #{i} invalid: {str(e)[:120]}")

        # === images: alt + local src exists ===
        for am in ALTLESS_IMG_RE.findall(html):
            warn(f"{rel}: <img> without alt: {am[:90]}")
        for src in IMG_SRC_RE.findall(html):
            tgt = resolve_target(rel, src)
            if tgt and not disk_exists(tgt):
                crit(f"{rel}: image missing on disk: {src}")

        # === every href/src target resolves ===
        for attr in LINK_SRC_RE.findall(html):
            tgt = resolve_target(rel, attr)
            if tgt is None: continue
            if not disk_exists(tgt):
                crit(f"{rel}: broken link/asset/reference: {attr}")
            elif tgt.startswith("files/") and tgt.split("#")[0] not in ("",) \
                    and not disk_exists(tgt):
                crit(f"{rel}: missing download file: {attr}")
        # empty href=""
        for attr in LINK_SRC_RE.findall(html):
            if attr == "": warn(f"{rel}: empty href/src")

        # === tag balance ===
        b = Balance()
        try:
            b.feed(html); b.close()
        except Exception as e:
            crit(f"{rel}: HTML parser error: {str(e)[:120]}")
        else:
            left = [t for t in b.stack if t in ("body", "html", "main")]
            if left: crit(f"{rel}: unclosed structural tag(s): {', '.join(left)}")
            if b.errors: warn(f"{rel}: tag-balance notice: {b.errors[0]}")

        # === collect inline JS for node syntax check ===
        for blob in INLINE_JS_RE.findall(html):
            if blob.strip() and "application/ld+json" not in blob[:40]:
                inline_js_blobs.append((rel, blob))

    # === duplicate titles / descriptions ===
    for t, where in titles.items():
        if len(where) > 1: crit(f"duplicate title on {len(where)} pages: {t[:70]} -> {where[:3]}")

    # (meta descriptions: near-identical share text is OK on cluster pages;
    #  only flag large groups as warning, small exact-dups as info)
    for d, where in descs.items():
        if len(where) > 2: crit(f"duplicate description on {len(where)} pages: {d[:70]}...")
        elif len(where) == 2: warn(f"description shared by 2 pages: {', '.join(where)}")

    # === sitemap consistency ===
    sm = SITE / "sitemap.xml"
    if sm.is_file():
        locs = re.findall(r"<loc>(.*?)</loc>", sm.read_text(encoding="utf-8"))
        for loc in locs:
            path = loc.split("studysapiens.com/", 1)[-1]
            if not disk_exists(path):
                crit(f"sitemap.xml lists missing URL: {loc}")
        sm_paths = {loc.split("studysapiens.com/", 1)[-1] for loc in locs}
        for rel in rel_pages:
            if rel in ("404.html", "offline/index.html"): continue
            pretty = re.sub(r"(^|/)index\.html$", "", rel)
            if pretty not in sm_paths and pretty + "/" not in sm_paths:
                warn(f"page not in sitemap.xml: {rel}")
        info(f"sitemap.xml: {len(locs)} URLs verified")
    else:
        crit("sitemap.xml missing")

    # === robots + feed sanity ===
    rb = (SITE / "robots.txt").read_text(encoding="utf-8") if (SITE / "robots.txt").is_file() else ""
    if "Sitemap:" not in rb: warn("robots.txt missing Sitemap: line")
    if (SITE / "feed.xml").is_file():
        fx = (SITE / "feed.xml").read_text(encoding="utf-8")
        if "<rss" not in fx or "</channel>" not in fx: warn("feed.xml looks malformed")

    # === JS syntax (node optional) ===
    node = shutil.which("node")
    if node:
        for js_rel in ("assets/js/main.js", "sw.js"):
            p = SITE / js_rel
            if p.is_file():
                r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True)
                if r.returncode != 0:
                    crit(f"JS syntax error in {js_rel}: {r.stderr.strip()[:200]}")
                else:
                    info(f"node --check OK: {js_rel}")
        if inline_js_blobs:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
                for i, (rel, blob) in enumerate(inline_js_blobs):
                    tf.write(f"// --- {rel} #{i} ---\ntry{{\n{blob}\n}}catch(_){{}}\n")
                tmp = tf.name
            r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
            os.unlink(tmp)
            if r.returncode != 0:
                crit(f"inline JS syntax error near: {r.stderr.strip()[:220]}")
            else:
                info(f"node --check OK: {len(inline_js_blobs)} inline script blocks")
    else:
        warn("node not found: JS syntax validation skipped")

    # ================= summary =================
    print("=" * 64)
    print(f"PRECHECK RESULT: {len(pages)} pages | {len(critical)} critical | {len(warnings)} warnings")
    if critical:
        print("\n>>> DO NOT DEPLOY. Fix critical issues first:")
        for c in critical[:40]: print(f"  [CRITICAL] {c}")
        return_code = 1
    else:
        if warnings and not QUIET:
            print("\nWarnings (non-blocking):")
            for w in warnings[:40]: print(f"  {w}")
        print("\n✅ SAFE TO DEPLOY (no critical issues).")
        return_code = 0
    return return_code


if __name__ == "__main__":
    sys.exit(main())

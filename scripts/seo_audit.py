#!/usr/bin/env python3
"""StudySapiens SEO audit — run: python3 scripts/seo_audit.py"""
import os, re, json, html, glob, sys
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
files = sorted(glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True))
titles, descs = {}, {}
long_titles, long_descs, no_h1, multi_h1, bad_imgs, bad_jsonld = [], [], [], [], [], []
for f in files:
    rel = os.path.relpath(f, ROOT)
    src = open(f, encoding="utf-8").read()
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    t = html.unescape(m.group(1).strip()) if m else ""
    titles.setdefault(t, []).append(rel)
    if len(t.replace(" | StudySapiens", "")) > 66: long_titles.append((len(t.replace(" | StudySapiens","")), rel))
    md = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
    d = html.unescape(md.group(1).strip()) if md else ""
    descs.setdefault(d, []).append(rel)
    if len(d) > 165: long_descs.append((len(d), rel))
    h1s = re.findall(r"<h1[ >]", src)
    if len(h1s) == 0: no_h1.append(rel)
    if len(h1s) > 1: multi_h1.append((rel, len(h1s)))
    for im in re.findall(r"<img\b[^>]*>", src):
        if "alt=" not in im: bad_imgs.append((rel, im[:60]))
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try: json.loads(block)
        except Exception as e: bad_jsonld.append((rel, str(e)[:60]))
dup_t = {k: v for k, v in titles.items() if len(v) > 1}
dup_d = {k: v for k, v in descs.items() if len(v) > 1}
print(f"PAGES: {len(files)}")
print(f"DUP TITLES: {sum(len(v) for v in dup_t.values())} in {len(dup_t)} groups")
print(f"DUP DESCS: {sum(len(v) for v in dup_d.values())} in {len(dup_d)} groups")
print("TITLES >66:", len(long_titles), sorted(long_titles, reverse=True)[:4])
print("DESCS >165:", len(long_descs), sorted(long_descs, reverse=True)[:6])
print(f"NO H1: {len(no_h1)} | MULTI H1: {len(multi_h1)} | IMG no-alt: {len(bad_imgs)} | BAD JSONLD: {len(bad_jsonld)}")
links = {}
for f in files:
    rel = os.path.relpath(f, ROOT)
    for href in re.findall(r'href="([^"#]+)', open(f, encoding="utf-8").read()):
        if href.startswith(("http", "mailto:", "tel:", "data:")): continue
        p2 = href.lstrip("/") if href.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(rel), href))
        links.setdefault(p2, []).append(rel)
broken = []
for p, srcs in links.items():
    full = os.path.join(ROOT, p)
    if p in ("", "."): continue
    ok = (os.path.exists(os.path.join(full, "index.html")) or os.path.exists(full)) if ("." not in os.path.basename(p)) else os.path.exists(full)
    if not ok: broken.append((p, srcs[:3]))
print(f"BROKEN INTERNAL LINKS: {len(broken)}")
for p, s in broken[:12]: print("   ", p, "<-", s)
sys.exit(1 if (dup_t or dup_d or long_descs or no_h1 or multi_h1 or bad_imgs or bad_jsonld or broken) else 0)

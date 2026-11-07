#!/usr/bin/env python3
"""Anchor audit: every internal href#fragment must resolve to a real id on the target page.
Also: duplicate id check, empty href check, lang/viewport/charset/canonical sanity."""
import os, re, sys, json
from urllib.parse import unquote

OUT = "site"
pages = []
for root, _, files in os.walk(OUT):
    for f in files:
        if f.endswith(".html"):
            pages.append(os.path.join(root, f))

def url_for(path):
    rel = os.path.relpath(path, OUT).replace(os.sep, "/")
    if rel.endswith("/index.html"): rel = rel[:-len("index.html")]
    elif rel == "index.html": rel = ""
    return "/" + rel

def file_for_url(u, from_page):
    u = u.split("#")[0].split("?")[0]
    if u.startswith("http") or u.startswith("mailto") or u.startswith("tel") or u.startswith("javascript"): return None
    if u == "":
        return from_page
    if u.startswith("/"):
        p = os.path.join(OUT, u.lstrip("/"))
    else:
        p = os.path.normpath(os.path.join(os.path.dirname(from_page), u))
    if os.path.isdir(p): p = os.path.join(p, "index.html")
    elif not p.endswith(".html") and os.path.isdir(p + "/"): p = os.path.join(p, "index.html")
    return p if os.path.isfile(p) else None

id_re = re.compile(r'\bid="([^"]+)"')
href_re = re.compile(r'href="([^"]*)"')

bad_anchor, missing_file, empty_href = [], [], []
dup_ids, sanity = [], []

for p in pages:
    html = open(p, encoding="utf-8").read()
    ids = id_re.findall(html)
    from collections import Counter
    for i, n in Counter(ids).items():
        if n > 1 and i not in ("",): dup_ids.append((url_for(p), i, n))
    idset = set(ids)
    for h in href_re.findall(html):
        if h == "": empty_href.append(url_for(p))
        if "#" not in h: continue
        frag = unquote(h.split("#", 1)[1])
        if not frag: continue
        tgt = file_for_url(h, p)
        if tgt is None:
            if not h.startswith(("http", "mailto", "tel")):
                base = h.split("#")[0]
                if base: missing_file.append((url_for(p), h))
            continue
        thtml = open(tgt, encoding="utf-8").read()
        tids = set(id_re.findall(thtml))
        if frag not in tids:
            bad_anchor.append((url_for(p), h))
    # sanity
    for pat, name in [(r'<html[^>]*lang="en"', 'lang'), (r'name="viewport"', 'viewport'), (r'rel="canonical"', 'canonical'), (r'property="og:title"', 'og:title'), (r'property="og:image"', 'og:image')]:
        if not re.search(pat, html): sanity.append((url_for(p), name))

print(f"PAGES: {len(pages)}")
print(f"BAD ANCHORS (fragment missing on target): {len(bad_anchor)}")
for a in bad_anchor[:20]: print("  ", a)
print(f"HREF TO MISSING FILE: {len(missing_file)}")
for a in missing_file[:10]: print("  ", a)
print(f"EMPTY HREF: {len(empty_href)}")
for a in empty_href[:10]: print("  ", a)
print(f"DUPLICATE IDS: {len(dup_ids)}")
for a in dup_ids[:10]: print("  ", a)
print(f"SANITY (lang/viewport/canonical/og): {len(sanity)}")
for a in sanity[:10]: print("  ", a)

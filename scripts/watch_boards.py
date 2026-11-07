#!/usr/bin/env python3
"""
watch_boards.py : StudySapiens board-news watcher (DETECT + ALERT only)

Checks Punjab board websites and PMDC for new notices/news items and tells
you what changed. It NEVER writes to data.py and NEVER rebuilds the site.
Publishing is always a human decision (honesty rule).

Usage:
    python3 scripts/watch_boards.py             Check all sources, alert on changes
    python3 scripts/watch_boards.py --verify    Just test every source (status + item count)
    python3 scripts/watch_boards.py --baseline  Record current state silently (first run)
    python3 scripts/watch_boards.py --source lahore pmdc   Check only some sources

State is stored in scripts/watch_state.json so only NEW items are reported.

Notes:
    - Runs on plain Python 3 (3.8+), no packages to install.
    - Some board sites block visitors from outside Pakistan. Run this on your
      own machine in Pakistan for reliable results. --verify shows which
      sources respond from wherever you run it.
    - All console output is ASCII-safe for Windows terminals.
"""

import html as html_mod
import json
import re
import ssl
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except ImportError:  # pragma: no cover
    print("Python 3 required.")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = Path(__file__).resolve().parent / "watch_state.json"

TIMEOUT = 25
MAX_ITEMS = 40
MAX_ALERTS_SHOWN = 12

# Verified source list (checked 2026-10-28). Some sites refuse requests from
# outside Pakistan; the watcher treats every source independently, so one
# failing site never stops the others.
SOURCES = {
    "lahore":     ("BISE Lahore",     "https://biselahore.com/"),
    "gujranwala": ("BISE Gujranwala", "https://bisegrw.edu.pk/"),
    "multan":     ("BISE Multan",     "https://web.bisemultan.edu.pk/"),
    "faisalabad": ("BISE Faisalabad", "https://bisefsd.edu.pk/"),
    "rawalpindi": ("BISE Rawalpindi", "https://biserwp.edu.pk/"),
    "sargodha":   ("BISE Sargodha",   "https://bisesargodha.edu.pk/"),
    "bahawalpur": ("BISE Bahawalpur", "https://bisebwp.edu.pk/"),
    "dgkhan":     ("BISE DG Khan",    "https://bisedgkhan.edu.pk/"),
    "sahiwal":    ("BISE Sahiwal",    "https://bisesahiwal.edu.pk/"),
    "pmdc":       ("PMDC",            "https://pmdc.pk/"),
    "pctb":       ("PCTB / PECTAA",   "https://pctb.punjab.gov.pk/"),
}

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
DATE_RE = re.compile(
    r"(\b\d{1,2}[-/ ](" + MONTHS + r")[a-z]*[-/ ]\d{2,4}\b)"
    r"|(\b(" + MONTHS + r")[a-z]*\s+\d{1,2},?\s+\d{4}\b)"
    r"|(\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b)",
    re.IGNORECASE,
)
NEWS_WORDS = re.compile(
    r"\b(result|date[\s-]?sheet|admission|notification|notified|press|exam|"
    r"schedule|registration|merit|intermediate|matric|hssc|ssc|mdcat|ecat|"
    r"recheck|supply|supplementary|roll\s?no|admit|fee|form|202[5-9])\b",
    re.IGNORECASE,
)
SKIP_TEXTS = {
    "home", "about", "about us", "contact", "contact us", "downloads",
    "results", "result", "login", "log in", "read more", "view all",
    "click here", "more", "news", "notices", "tenders", "gallery",
    "privacy policy", "terms", "sitemap", "site map", "skip to content",
    "facebook", "twitter", "youtube", "instagram", "whatsapp",
}
# Service-card / nav junk that is never "news" (boards put these on homepages)
BAD_SUBSTR = (
    "learn more", "submit form", "read more", "apply online",
    "board of intermediate & secondary education",
    "board of intermediate and secondary education",
    "all rights reserved", "designed by", "developed by",
    "get your result card", "date of birth correction",
)
SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>")
TAG_RE = re.compile(r"(?s)<[^>]+>")
ANCHOR_RE = re.compile(r'(?is)<a\b[^>]*>(.*?)</a>')
ROW_RE = re.compile(r"(?is)<tr\b[^>]*>(.*?)</tr>")
WS_RE = re.compile(r"\s+")


BADGE_RE = re.compile(r"\s+(NEW|New|new)\s*$")


def clean_text(html_fragment):
    text = html_mod.unescape(TAG_RE.sub(" ", html_fragment))
    text = WS_RE.sub(" ", text).strip()
    text = BADGE_RE.sub("", text).strip()
    return text


def is_junk(text):
    low = text.lower().strip(" .")
    if low in SKIP_TEXTS:
        return True
    return any(bad in low for bad in BAD_SUBSTR)


def looks_like_news(text):
    if not (25 <= len(text) <= 400):
        return False
    if is_junk(text):
        return False
    if DATE_RE.search(text) or NEWS_WORDS.search(text):
        return True
    return False


def extract_items(html):
    """Pull candidate news lines out of a board homepage."""
    html = SCRIPT_STYLE_RE.sub(" ", html)
    items = []
    for m in ROW_RE.finditer(html):
        text = clean_text(m.group(1))
        if DATE_RE.search(text) and len(text) >= 25 and not is_junk(text):
            items.append(text[:400])
    for m in ANCHOR_RE.finditer(html):
        text = clean_text(m.group(1))
        if looks_like_news(text):
            items.append(text[:400])
    seen, out = set(), []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
        if len(out) >= MAX_ITEMS:
            break
    return out


def fetch(url):
    """Fetch a URL. Returns (html, None) or (None, error_message)."""
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = Request(url, headers=headers)
    ctx = ssl.create_default_context()
    try:
        with urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            raw = r.read(1_500_000)
        return raw.decode("utf-8", errors="replace"), None
    except HTTPError as e:
        return None, "HTTP " + str(e.code)
    except (URLError, ssl.SSLError) as e:
        reason = str(getattr(e, "reason", e))
        if "CERTIFICATE" in reason.upper() or "SSL" in reason.upper():
            try:  # retry without cert verification, with a clear warning
                ctx2 = ssl._create_unverified_context()
                with urlopen(req, timeout=TIMEOUT, context=ctx2) as r:
                    raw = r.read(1_500_000)
                return raw.decode("utf-8", errors="replace"), None
            except Exception as e2:
                return None, "SSL/fetch failed: " + str(e2)[:120]
        return None, reason[:120]
    except Exception as e:  # socket.timeout etc.
        return None, str(e)[:120]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def check_source(key, verify_only=False):
    label, url = SOURCES[key]
    html, err = fetch(url)
    if err:
        return {"label": label, "url": url, "status": "error", "error": err,
                "items": []}
    items = extract_items(html)
    status = "ok" if items else "empty"
    return {"label": label, "url": url, "status": status, "error": "",
            "items": items}


def cmd_verify(keys):
    print("StudySapiens board watcher: source verification")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("-" * 64)
    ok = 0
    for key in keys:
        res = check_source(key, verify_only=True)
        if res["status"] == "ok":
            ok += 1
            print("[OK]   %-16s %3d news-like items found  %s"
                  % (res["label"], len(res["items"]), res["url"]))
        elif res["status"] == "empty":
            print("[WARN] %-16s page loads but no news items  %s"
                  % (res["label"], res["url"]))
        else:
            print("[FAIL] %-16s %s" % (res["label"], res["error"]))
    print("-" * 64)
    print("%d/%d sources fully working from this machine." % (ok, len(keys)))
    if ok < len(keys):
        print("Tip: some boards block non-Pakistan visitors. Run --verify on")
        print("your own PC in Pakistan; results are usually better there.")
    return 0


def cmd_check(keys, baseline=False):
    state = load_state()
    new_state = dict(state)
    total_new = 0
    failures = 0
    print("StudySapiens board watcher: change check")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("-" * 64)
    for key in keys:
        res = check_source(key)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if res["status"] == "error":
            failures += 1
            print("[FAIL] %-16s %s (skipped, state kept)" % (res["label"], res["error"]))
            continue
        old_items = (state.get(key) or {}).get("items", [])
        old_set = set(old_items)
        fresh = [it for it in res["items"] if it not in old_set]
        new_state[key] = {"items": res["items"], "checked": now,
                          "status": res["status"], "url": res["url"]}
        if baseline:
            print("[BASE] %-16s %d items recorded as baseline" % (res["label"], len(res["items"])))
            continue
        if not state.get(key):
            print("[NEW]  %-16s first time seen, baseline recorded (%d items)"
                  % (res["label"], len(res["items"])))
            continue
        if fresh:
            total_new += len(fresh)
            print("[ALERT] %-15s %d NEW item(s):" % (res["label"], len(fresh)))
            for it in fresh[:MAX_ALERTS_SHOWN]:
                print("         * " + it[:180])
            if len(fresh) > MAX_ALERTS_SHOWN:
                print("         ... and %d more (see site directly)" % (len(fresh) - MAX_ALERTS_SHOWN))
        else:
            print("[ok]   %-16s nothing new" % res["label"])
    print("-" * 64)
    save_state(new_state)
    if baseline:
        print("Baseline saved to scripts/watch_state.json. Run without --baseline")
        print("from now on to get alerts.")
    elif total_new:
        print(">> %d new item(s) detected. NEXT STEPS:", total_new)
        print("   1. Open the board site and confirm the news yourself.")
        print("   2. If it is real and useful for students, publish it in 60 seconds:")
        print('      python3 scripts/new_update.py --title "..." --tag "Boards"')
        print("   3. If it is a rumour or unclear, do nothing. We never guess.")
    else:
        print("No changes on working sources. State saved.")
    if failures:
        print("Note: %d source(s) unreachable this run; their old state was kept." % failures)
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Watch Punjab boards + PMDC for new notices. "
                    "Detect and alert only; never auto-publishes.")
    ap.add_argument("--verify", action="store_true",
                    help="just test that every source responds")
    ap.add_argument("--baseline", action="store_true",
                    help="record current state without alerting (first run)")
    ap.add_argument("--source", nargs="+", metavar="KEY",
                    help="check only these sources, e.g. --source lahore pmdc")
    args = ap.parse_args()

    if args.source:
        keys = []
        for k in args.source:
            k = k.lower()
            if k not in SOURCES:
                print("Unknown source '%s'. Known: %s" % (k, ", ".join(SOURCES)))
                return 2
            keys.append(k)
    else:
        keys = list(SOURCES)

    if args.verify:
        return cmd_verify(keys)
    return cmd_check(keys, baseline=args.baseline)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
new_update.py : publish a StudySapiens update in about 60 seconds.

What it does:
    1. Backs up data.py (rolling copy at scripts/data_backup.py)
    2. Inserts a new entry at the TOP of UPDATES in data.py
       (top = newest = appears first on ticker, home page and /updates/)
    3. Syntax-checks data.py; auto-restores the backup if anything is wrong
    4. Rebuilds the whole site (ticker + /updates/ hub + home + sitemap)

Usage (fully non-interactive):
    python3 scripts/new_update.py --title "Date Sheet Announced for Matric 2027" \
        --tag "Boards" --excerpt "One honest sentence for the ticker and cards."

Or just run it and answer the prompts:
    python3 scripts/new_update.py

Options:
    --slug my-slug          Custom slug (default: made from the title)
    --date "July 22, 2026"  Display date (default: today)
    --no-build              Insert the entry but skip the rebuild
    --body-file path.html   Use this HTML file as the body instead of the scaffold

After publishing, open data.py and replace the scaffold paragraphs in the
new entry's "body" with the real, verified details. Rebuild again afterwards:
    python3 build.py
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PY = ROOT / "data.py"
BACKUP = Path(__file__).resolve().parent / "data_backup.py"

SCAFFOLD_BODY = '''"""
<p>[Paragraph 1: what happened, in one or two simple sentences. Say only what is confirmed.]</p>
<h2>What students should do</h2>
<ul>
<li>[Point 1: one clear action for students]</li>
<li>[Point 2: another clear action]</li>
<li>[Point 3: where to confirm officially, with source name]</li>
</ul>
<div class="callout"><b>Note:</b> Always confirm from your board's official website or office before acting. StudySapiens publishes an update only after the source has been checked. If any detail here ever proves wrong, <a href="/contact/">tell us</a> and we fix it the same day.</div>"""'''

VALID_TAGS = ["Boards", "Results", "Date Sheet", "Syllabus", "MDCAT", "ECAT",
              "Admissions", "Exams", "Books", "CSS", "Study Tips", "Site News"]


def q(text):
    """Quote a string safely as a Python double-quoted literal."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s[:60] or "update"


def prompt_if_empty(value, question):
    value = (value or "").strip()
    while not value:
        try:
            value = input(question + " ").strip()
        except EOFError:
            print("Missing %s and no input available. Use the flags; see --help.")
            sys.exit(2)
    return value


def insert_entry(slug, title, date, tag, excerpt, body):
    src = DATA_PY.read_text(encoding="utf-8")

    marker = "UPDATES = [\n"
    if marker not in src:
        print("ERROR: could not find 'UPDATES = [' in data.py.")
        return False
    if q(slug) in src or ("slug" in src and re.search(
            r'"slug":\s*' + q(slug), src)):
        print("ERROR: an entry with slug '%s' already exists." % slug)
        return False

    entry = (
        "    {\n"
        "        \"slug\": %s,\n"
        "        \"title\": %s,\n"
        "        \"date\": %s,\n"
        "        \"tag\": %s,\n"
        "        \"excerpt\": %s,\n"
        "        \"body\": %s,\n"
        "    },\n"
    ) % (q(slug), q(title), q(date), q(tag), q(excerpt), body)

    shutil.copyfile(DATA_PY, BACKUP)
    src = src.replace(marker, marker + entry, 1)
    DATA_PY.write_text(src, encoding="utf-8")

    # syntax-check; auto-restore on failure so the site can never be broken
    chk = subprocess.run([sys.executable, "-m", "py_compile", str(DATA_PY)],
                         capture_output=True, text=True)
    if chk.returncode != 0:
        shutil.copyfile(BACKUP, DATA_PY)
        print("ERROR: insertion broke data.py; backup restored automatically.")
        print(chk.stderr[:600])
        return False
    return True


def rebuild():
    print("Rebuilding site ...")
    r = subprocess.run([sys.executable, str(ROOT / "build.py")],
                       cwd=str(ROOT), capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    tail = "\n".join(out.strip().splitlines()[-6:])
    print(tail)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(
        description="Insert a new UPDATES entry in data.py and rebuild.")
    ap.add_argument("--title")
    ap.add_argument("--tag")
    ap.add_argument("--excerpt")
    ap.add_argument("--slug")
    ap.add_argument("--date")
    ap.add_argument("--body-file", help="HTML file to use as the body")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    title = prompt_if_empty(args.title, "Title of the update:")
    tag = (args.tag or "").strip() or "Boards"
    excerpt = prompt_if_empty(
        args.excerpt, "One-sentence excerpt (ticker + cards):")
    slug = args.slug or slugify(title)
    date = (args.date or "").strip()
    if not date:  # "November 6, 2026" style, platform-independent
        now = datetime.now()
        date = "%s %d, %d" % (now.strftime("%B"), now.day, now.year)

    if args.body_file:
        bf = Path(args.body_file)
        if not bf.exists():
            print("ERROR: body file not found: %s" % bf)
            return 2
        body = '"""' + bf.read_text(encoding="utf-8") + '"""'
    else:
        body = SCAFFOLD_BODY

    if tag not in VALID_TAGS:
        print("Note: tag '%s' is new. Usual tags: %s" % (tag, ", ".join(VALID_TAGS)))

    print("Inserting: %s" % slug)
    if not insert_entry(slug, title, date, tag, excerpt, body):
        return 1
    print("OK: entry added at the top of UPDATES. Backup: scripts/data_backup.py")

    if args.no_build:
        print("Skipped rebuild (--no-build). Run: python3 build.py")
    else:
        if not rebuild():
            print("WARNING: build failed. data.py is valid; check build output above.")
            return 1

    print("-" * 64)
    print("PUBLISHED (scaffold body). Your 60-second checklist:")
    print("  1. Open data.py, find slug '%s'." % slug)
    print("  2. Replace the [bracketed] scaffold lines with verified details.")
    print("  3. Run: python3 build.py")
    print("  4. STRONGLY recommended: add official source links to the entry:")
    print('       "sources": [("BISE Lahore", "https://www.biselahore.com/")],')
    print("     They show as an Official sources line and boost AI/Google trust (GEO).")
    print("  5. Spot-check: site/updates/%s/index.html" % slug)
    print("Reminder: publish only what you confirmed from the official source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

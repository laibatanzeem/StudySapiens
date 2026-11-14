#!/usr/bin/env python3
"""
pdf_audit.py — automated PDF & link audit for StudySapiens.

Called automatically by sync_files.py as part of pre-deploy validation, or run
standalone:   python3 scripts/pdf_audit.py

What it checks
  CRITICAL  subject mismatch: a PDF under files/class-N/<subject>/ (or
            files/formulas/class-N/<subject>/) whose file name or page-1 title
            clearly names a DIFFERENT subject. Examples it must catch: an
            "Urdu Compulsory - Grade 10" scheme sitting in tarjuma-tul-quran/.
  CRITICAL  class mismatch: file name or page-1 title names a different class
            (grade/class/9th/10th/11th/12th/SSC-I/SSC-II/HSSC-I/HSSC-II).
  CRITICAL  broken PDF links: any page in site/ that links a .pdf which does
            not exist on disk.
  CRITICAL  empty (0-byte) PDFs in site/.
  WARNING   orphan PDFs (in site/ but never linked from any page),
            PDFs whose text could not be extracted (no pypdf / scanned PDF).

Medium-marker awareness: in this repo's naming convention a trailing "-Urdu"
or "-English" (or "Urdu medium" / "in English") marks the LANGUAGE EDITION of
a file, not its subject - those tokens are ignored before subject matching.

Text extraction uses pypdf when available:
    pip3 install --break-system-packages pypdf
Without pypdf the file-name + link checks still run (text checks are skipped).

Exit code: 0 = pass (warnings allowed) · 1 = FAIL — do not deploy.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FILES = ROOT / "files"
QUIET = "--quiet" in sys.argv

critical, warnings = [], []


def crit(msg):
    critical.append(msg)
    print(f"  [CRITICAL] {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  [warn]     {msg}") if not QUIET else None


def info(msg):
    print(f"  [info]     {msg}") if not QUIET else None


# folder slug -> distinctive name tokens (lowercase, word-boundary matched)
SUBJECT_TOKENS = {
    "physics": ["physics"],
    "chemistry": ["chemistry"],
    "biology": ["biology"],
    "mathematics": ["mathematics", "maths"],
    "computer-science": ["computer science", "computer-science"],
    "english": ["english"],
    "urdu": ["urdu"],
    "islamiat": ["islamiat", "islamiyat", "islamic studies"],
    "pak-studies": ["pakistan studies", "pak studies", "pakistan-studies"],
    "tarjuma-tul-quran": ["tarjuma", "tarjama"],
}

CLASS_PATTERNS = {
    "9": [r"grade\s*9\b", r"\b9th\b", r"\bclass\s*9\b", r"\bssc[\s-]*i\b"],
    "10": [r"grade\s*10\b", r"\b10th\b", r"\bclass\s*10\b", r"\bssc[\s-]*ii\b"],
    "11": [r"grade\s*11\b", r"\b11th\b", r"\bclass\s*11\b", r"\bhssc[\s-]*i\b"],
    "12": [r"grade\s*12\b", r"\b12th\b", r"\bclass\s*12\b", r"\bhssc[\s-]*ii\b"],
}

# language-edition markers, not subject claims
MEDIUM_PATTERNS = [
    r"\b(urdu|english)[\s-]*medium\b",
    r"\bmedium\s*[:\-]?\s*(urdu|english)\b",
    r"\bin\s+(urdu|english)\b",
]

try:
    from pypdf import PdfReader
    HAVE_PYPDF = True
except Exception:
    HAVE_PYPDF = False


def folder_context(pdf: Path):
    """Return (class_str_or_None, subject_slug_or_None) for a files/ path."""
    parts = pdf.relative_to(FILES).parts
    if len(parts) >= 3 and re.fullmatch(r"class-\d+", parts[0]):
        return parts[0].replace("class-", ""), (parts[1] if parts[1] in SUBJECT_TOKENS else None)
    if len(parts) >= 3 and parts[0] == "formulas" and re.fullmatch(r"class-\d+", parts[1]):
        return parts[1].replace("class-", ""), (parts[2] if parts[2] in SUBJECT_TOKENS else None)
    if parts[0] == "english":
        return None, "english"
    return None, None


def title_zone(pdf: Path, limit=150):
    """First `limit` characters of page-1 text (the title area), '' if unreadable."""
    if not HAVE_PYPDF:
        return ""
    try:
        r = PdfReader(str(pdf))
        txt = (r.pages[0].extract_text() or "") if r.pages else ""
        return re.sub(r"\s+", " ", txt[:limit])
    except Exception:
        return ""


def strip_medium_markers(s: str) -> str:
    for pat in MEDIUM_PATTERNS:
        s = re.sub(pat, " ", s)
    return s


def normalize_name(stem: str) -> str:
    """File stem -> comparable text; separators become spaces, medium markers removed."""
    s = re.sub(r"[_\-.]+", " ", stem.lower())
    s = strip_medium_markers(s)
    s = re.sub(r"\s+", " ", s).strip()
    # a lone trailing 'urdu'/'english' is the language-edition marker in our convention
    s = re.sub(r"\s(urdu|english)$", "", s)
    return s.strip()


def normalize_title(tz: str) -> str:
    return strip_medium_markers(re.sub(r"\s+", " ", tz.lower())).strip()


def audit_content():
    """Subject / class agreement between folder, file name and PDF title."""
    pdfs = sorted(FILES.rglob("*.pdf"))
    info(f"content check: {len(pdfs)} PDFs under files/")
    no_text = 0
    for pdf in pdfs:
        cls, subj = folder_context(pdf)
        if subj is None and cls is None:
            continue
        rel = pdf.relative_to(FILES)
        name = normalize_name(pdf.stem)
        tz = title_zone(pdf)
        title = normalize_title(tz)

        # --- subject mismatch: another subject's token in name or title area
        for other, toks in SUBJECT_TOKENS.items():
            if other == subj:
                continue
            for tok in toks:
                if re.search(rf"\b{re.escape(tok)}\b", name):
                    crit(f"subject mismatch: {rel} file name names '{tok}' "
                         f"but the folder subject is '{subj}'")
                    break
                if title and re.search(rf"\b{re.escape(tok)}\b", title):
                    crit(f"subject mismatch: {rel} page-1 title names '{tok}' "
                         f"but the folder subject is '{subj}'")
                    break

        # --- class mismatch
        if cls is not None:
            for other_cls, pats in CLASS_PATTERNS.items():
                if other_cls == cls:
                    continue
                for pat in pats:
                    hit = re.search(pat, name) or (title and re.search(pat, title))
                    if hit:
                        crit(f"class mismatch: {rel} says '{hit.group(0)}' "
                             f"but lives in class-{cls}/")
                        break

        if not tz:
            no_text += 1
    if no_text:
        warn(f"{no_text} PDFs could not be text-checked (scanned or pypdf missing) "
             f"- file-name checks still applied")


def audit_links():
    """Every .pdf href in site/**/*.html must exist; every site PDF must be linked."""
    href_re = re.compile(r'href="([^"]+?\.pdf)"')
    linked = set()
    pages = list(SITE.rglob("*.html"))
    for page in pages:
        html = page.read_text(encoding="utf-8", errors="ignore")
        for href in href_re.findall(html):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target = (page.parent / unquote(href.split("#")[0])).resolve()
            if not target.exists():
                crit(f"broken PDF link: {page.relative_to(SITE)} -> {href}")
            else:
                linked.add(str(target))
    site_pdfs = {str(p.resolve()) for p in SITE.rglob("*.pdf")}
    for p in sorted(site_pdfs - linked):
        warn(f"orphan PDF (in site/ but never linked): {Path(p).relative_to(SITE)}")
    for p in sorted(site_pdfs):
        if Path(p).stat().st_size == 0:
            crit(f"empty 0-byte PDF: {Path(p).relative_to(SITE)}")
    return len(site_pdfs), len(linked)


def main():
    if not FILES.is_dir():
        print("pdf_audit: files/ not found - nothing to do")
        return 0
    print("PDF & link audit")
    if not HAVE_PYPDF:
        warn("pypdf not installed - PDF title text checks skipped "
             "(pip3 install --break-system-packages pypdf)")
    audit_content()
    n_pdfs, n_linked = audit_links()
    print(f"AUDIT RESULT: {n_pdfs} site PDFs | {n_linked} linked | "
          f"{len(critical)} critical | {len(warnings)} warnings")
    if critical:
        print(">>> PDF AUDIT FAILED - DO NOT DEPLOY. Fix the issues above.")
        return 1
    print("✅ PDF audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

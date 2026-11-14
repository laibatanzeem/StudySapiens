#!/usr/bin/env python3
"""
=====================================================================
 StudySapiens — FILE PUBLISHER
---------------------------------------------------------------------
 HOW TO UPLOAD NOTES / PAPERS (the only thing you ever do):
   1. Drop your PDF / DOC / DOCX / ZIP file into the RIGHT folder:

        files/
          class-9/
            physics/
              notes/        ← chapter notes
              solutions/    ← solved exercises
              mcq/          ← MCQ banks with answer keys
              guess/        ← guess papers
              scheme/       ← pairing / assessment schemes
              past/         ← past board papers

      (same for class-10, class-11 and class-12, for available subjects:
       physics, chemistry, biology, mathematics, computer-science, english,
       urdu, islamiat, pak-studies, tarjuma-tul-quran)

   2. Name the file what students should read, e.g.
        Chapter 1 - Physical Quantities.pdf
        Unit 3 Dynamics - Solved Exercise.docx
      (dashes/underscores become spaces automatically)

   3. Run:   python3 sync_files.py
   4. Upload the regenerated  site/  folder to your hosting. Done.

 The file instantly appears:
   • on the matching subject page  (Class 9 → Physics → Downloads)
   • on the right hub page  (guess papers → Guess Papers hub, etc.)
=====================================================================
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")

def count(folder):
    n = 0
    if os.path.isdir(folder):
        for _, _, names in os.walk(folder):
            n += sum(1 for x in names if os.path.splitext(x)[1].lower()
                     in (".pdf", ".doc", ".docx", ".zip", ".ppt", ".pptx"))
    return n

n = count(FILES)
print(f"🔎  Scanning {os.path.relpath(FILES)}/ … found {n} file(s)")
if n == 0:
    print("    (folders are empty for now — drop your first PDF in and run me again)")

print("🔨  Rebuilding the site …")
r = subprocess.run([sys.executable, os.path.join(HERE, "build.py")], cwd=HERE)
if r.returncode != 0:
    sys.exit(r.returncode)

# pre-deploy validation gate: refuses to pass if anything critical is broken
precheck = os.path.join(HERE, "scripts", "precheck.py")
if os.path.exists(precheck):
    print("\n🧪  Pre-deploy validation …")
    p = subprocess.run([sys.executable, precheck], cwd=HERE)
    if p.returncode != 0:
        print("\n⛔  Validation FAILED. The site/ folder was built but DO NOT deploy it yet.")
        sys.exit(1)
    print("✅  Validation passed. site/ is safe to upload.")

# automated PDF/link audit gate: subject-class-content match, broken links, orphans
pdf_audit = os.path.join(HERE, "scripts", "pdf_audit.py")
if os.path.exists(pdf_audit):
    print("\n📎  PDF & link audit …")
    p = subprocess.run([sys.executable, pdf_audit], cwd=HERE)
    if p.returncode != 0:
        print("\n⛔  PDF audit FAILED. Fix the issues above; DO NOT deploy site/ yet.")
        sys.exit(1)
    print("✅  PDF audit passed.")
sys.exit(0)

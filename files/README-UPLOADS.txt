==================================================================
StudySapiens upload folders. Drop verified files, then publish.
==================================================================

SUBJECT FILES (all classes)
  files/class-9/<subject>/<category>/your-file.pdf
  files/class-10/<subject>/<category>/
  files/class-11/<subject>/<category>/
  files/class-12/<subject>/<category>/

  <subject>: physics, chemistry, biology, mathematics, computer-science,
             english, urdu, islamiat, pak-studies, tarjuma-tul-quran
  <category>: notes, solutions, mcq, guess, scheme, numericals,
              model, testpapers
             (numericals shows only on physics/chemistry/mathematics;
              pak-studies only exists for class-10 and class-12,
              islamiat for class-9, 10 and 11)

  File names become the download labels:
    "chapter-1-physical-quantities.pdf" shows as "Chapter 1 Physical Quantities"

FORMULA SHEETS
  files/formulas/class-<9|10|11|12>/<physics|chemistry|mathematics>/x.pdf

ENGLISH CORNER
  files/english/essays/x.pdf
  files/english/letters-applications/x.pdf
  files/english/grammar/x.pdf

ONLINE TESTS (interactive quizzes)
  quizzes/<slug>.json   (see quizzes/study-skills-basics.json for the format:
                         q, opts (4), ans (0-3), e (explanation))
  The test page appears automatically at /tests/<slug>/ after publish.

RULES
  * Only upload files verified against the printed NEW book.
  * .txt files are ignored (never published). PDF/DOC/DOCX/PPT/ZIP publish.
  * After dropping files: run  python3 sync_files.py  (or python3 build.py)
    then upload the site/ folder as usual.
==================================================================

CHAPTER-WISE PAGES (currently: Class 10 Chemistry, chapters 14-26)
  Put the chapter number in the file name and drop it in the right
  category folder. The file then appears under that chapter's card:
    files/class-10/chemistry/solutions/StudySapiens_10th_Chem_Ch14_Solved-Exercise.pdf
    -> shows on Chapter 14 card, labelled "Solved Exercise"
  Accepted markers: Ch14, ch-14, chapter-14-, unit_14 ...
  Files with no chapter number stay in the whole-book area below
  (use that area for the guess paper and pairing scheme).

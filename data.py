# -*- coding: utf-8 -*-
"""
==================================================================
 StudySapiens · CONTENT DATABASE
 ------------------------------------------------------------------
 This single file holds ALL the content of the website.
 To add/change chapters, notes, papers, updates etc:
   1. Edit the relevant section below
   2. Run:  python3 build.py
   3. Upload the generated  site/  folder to your hosting
==================================================================
"""

SITE = {
    "name": "StudySapiens",
    "domain": "https://www.studysapiens.com",
    "tagline": "New PCTB Syllabus, Made Simple",
    "email": "admin.studysapiens@gmail.com",
    "description": "Class 9-12 Punjab board notes and solved exercises, made by teachers and verified by subject experts. New PCTB/PECTAA syllabus + MDCAT tools.",
}

# ------------------------------------------------------------------
# CLASSES
# ------------------------------------------------------------------
CLASSES = {
    "9":  {"name": "Class 9",  "alt": "9th Class",  "level": "Matric (SSC-I)",
           "session": "2025-26", "book_note": "New PCTB books, first session 2025-26",
           "first_exam": "Annual exams 2026", "exam_date": "2027-03-15"},
    "10": {"name": "Class 10", "alt": "10th Class", "level": "Matric (SSC-II)",
           "session": "2026-27", "book_note": "New PECTAA books, first session 2026-27",
           "first_exam": "Annual exams 2027", "exam_date": "2027-03-02"},
    "11": {"name": "Class 11", "alt": "1st Year",   "level": "Intermediate (HSSC-I)",
           "session": "2025-26", "book_note": "New PCTB books, first session 2025-26",
           "first_exam": "Annual exams 2026", "exam_date": "2027-05-17"},
    "12": {"name": "Class 12", "alt": "2nd Year",   "level": "Intermediate (HSSC-II)",
           "session": "2026-27", "book_note": "New PECTAA books, first session 2026-27",
           "first_exam": "Annual exams 2027", "exam_date": "2027-05-04"},
}

SUBJECT_ORDER = ["physics", "chemistry", "biology", "mathematics", "computer-science", "english"]

SUBJECTS = {
    "physics":          {"name": "Physics",          "hue": "var(--c-physics)",          "icon": "atom"},
    "chemistry":        {"name": "Chemistry",        "hue": "var(--c-chemistry)",        "icon": "flask"},
    "biology":          {"name": "Biology",          "hue": "var(--c-biology)",          "icon": "dna"},
    "mathematics":      {"name": "Mathematics",      "hue": "var(--c-mathematics)",      "icon": "sigma"},
    "computer-science": {"name": "Computer Science", "hue": "var(--c-computer-science)", "icon": "chip"},
    "english":          {"name": "English",          "hue": "var(--c-english)",          "icon": "book"},
}

# ------------------------------------------------------------------
# SUBJECT_INFO · evergreen, syllabus-safe content for subject pages
# (deliberately generic: no chapter lists, no unit numbers. The actual
#  books live in the uploaded PDF files, never hard-coded here)
# ------------------------------------------------------------------
SUBJECT_INFO = {
    "physics": {
        "about": "Physics teaches you how the world actually works: motion, forces, energy, heat, light, electricity and the modern physics behind medical machines and space science. At board level it is a theory-plus-numerical subject. Definitions must be written in the board's exact wording, and numericals must be solved step by step with units.",
        "skills": ["Definitions & laws in exact board-exam wording", "Step-by-step solved numericals with units", "Labelled diagrams, formula tables & MCQ banks", "Guess paper & pairing scheme for smart revision"],
        "tip": "Write units from the very first line of every numerical. Most board marks in physics are lost on missing units and skipped steps, not on final answers.",
    },
    "chemistry": {
        "about": "Chemistry is the science of matter. Atoms, bonding, chemical reactions, energetics and the organic chemistry that the new books introduce earlier than before. It rewards students who memorise smartly: reactions, trends and short reasoning answers written as clean points.",
        "skills": ["Balanced equations written in clean exam format", "Trends, reasons & differences as short points", "Key definitions with everyday examples", "Chapter-wise MCQ bank, guess paper & pairing scheme"],
        "tip": "Keep one reaction sheet per chapter and revise it weekly. Chemistry is remembered by repetition, not by one-night reading.",
    },
    "biology": {
        "about": "Biology is the detailed study of living things, from cells to the complete human body systems, inheritance, biotechnology and ecology. It is a high-volume subject. Neat, labelled diagrams with point-wise answers are what separate average marks from 90 plus.",
        "skills": ["Large labelled diagrams you can actually redraw", "Point-wise answers in simple, easy English", "Definitions with one clear example each", "MCQ bank, guess paper & pairing scheme per syllabus"],
        "tip": "Never write a biology answer as one long paragraph. Examiners award marks point by point, so number your points and underline the key term.",
    },
    "mathematics": {
        "about": "Mathematics is pure practice: algebra, trigonometry, geometry and the foundations of calculus. There is almost nothing to memorise. Marks come from clean, complete, step-by-step working that any examiner can follow without guessing.",
        "skills": ["Fully solved exercise questions in proper order", "Theorems with clear figure references", "One-page formula sheet for quick revision", "Practice MCQs for the objective section"],
        "tip": "Re-solve yesterday's questions before starting today's new ones. Maths skill fades quickly, and re-solving is the only revision that truly works.",
    },
    "computer-science": {
        "about": "Computer Science in the new books is no longer just theory. It covers computational thinking, real programming, data, networks and modern topics like artificial intelligence. It is a highly scoring subject when programs and flowcharts are written neatly and in standard form.",
        "skills": ["Programs in clean, exam-style handwriting format", "Flowcharts with correct standard symbols", "Theory answers in short, simple sentences", "Glossary of technical terms + chapter MCQs"],
        "tip": "Write every program once by hand on paper. In the exam hall there is no compiler to catch your syntax mistakes for you.",
    },
    "english": {
        "about": "English carries heavy marks and often decides positions. Lessons, poems and the novel or drama come with grammar, translation, letters or applications and essays. Steady daily practice always beats weekend cramming.",
        "skills": ["Lesson summaries & question-answers in easy words", "Grammar rules with solved examples", "Model letters, applications, stories and essays", "Important MCQs from every lesson and poem"],
        "tip": "Learn five new words with usage daily and write one short paragraph every day. Visible improvement starts within about three weeks.",
    },
}

# Upload slots shown on every subject page (files auto-detected from
#   files/class-<9|10|11|12>/<subject>/<category>/  · see README)
FILE_CATEGORIES = [
    ("notes",     "doc",     "Chapter Notes",      "Complete chapter notes in simple English (PDF)"),
    ("solutions", "check",   "Exercise Solutions", "Step-by-step solved exercises (PDF / DOC)"),
    ("mcq",       "zap",     "MCQ Bank",           "Chapter-wise MCQs with answer keys"),
    ("guess",     "target",  "Guess Paper",        "Expected questions for the annual exam"),
    ("scheme",    "layers",  "Pairing Scheme",     "Pairing-scheme file or clearly labelled StudySapiens summary"),
]
EXTRA_CATEGORIES = {"past": "Past Papers"}   # listed on the past-papers hub

# ------------------------------------------------------------------
# BOARDS (for past papers / date sheets)
# ------------------------------------------------------------------
BOARDS = ["Lahore", "Gujranwala", "Multan", "Faisalabad", "Rawalpindi",
          "Sargodha", "Bahawalpur", "DG Khan", "Sahiwal"]

# ------------------------------------------------------------------
# UPDATES / BLOG POSTS
# ------------------------------------------------------------------
UPDATES = [
    {
        "slug": "class-10-new-books-2026",
        "title": "Class 10 New PECTAA Books 2026-27: What Students Should Know",
        "date": "July 22, 2026",
        "tag": "Syllabus",
        "excerpt": "Class 10 becomes the second batch of the new PECTAA books in matric part-II. What the change means, how to check you have the right book, and how to avoid re-labelled old notes.",
        "sources": [("PCTB / PECTAA: Punjab Curriculum & Textbook authority", "https://pctb.punjab.gov.pk/")],
        "body": """
<p>From session <b>2026-27</b>, Class 10 students study from the new books issued by <b>PECTAA</b> (the renamed Punjab Curriculum & Textbook Board authority). If you passed Class 9 on the new books, the style will feel familiar: concept-based chapters, learning outcomes (SLOs) at the start of every unit, and QR codes linking to digital material.</p>
<h2>How to confirm you have the correct book</h2>
<ol>
<li>Check the <b>PECTAA name and print year</b> on the title page. Old PCTB editions are still sold in many shops.</li>
<li>Compare the contents page with your board's official notification, not with any website (including ours).</li>
<li>Ask your subject teacher before buying any helping book or notes set.</li>
</ol>
<div class="callout"><b>Teacher's tip:</b> Do NOT study from old-syllabus notes re-labelled as "new". The order and wording of chapters genuinely changed. On StudySapiens a file goes live only after it has been checked against the printed book. If anything on this site ever mismatches your book, <a href="/contact/">tell us</a> and it is corrected or removed within a day.</div>
<h2>How to start the session strong</h2>
<ol>
<li>Download the official book PDFs first (see our <a href="/ebooks/">eBooks page</a>) and skim the table of contents in the first week.</li>
<li>Follow your subject pages here. Notes, solved exercises and MCQ banks are uploaded file by file as they clear verification.</li>
<li>Solve something daily. Ten honest minutes of written practice per subject beats two hours of passive reading.</li>
</ol>""",
    },
    {
        "slug": "mdcat-2026-guide",
        "title": "MDCAT 2026: Paper Pattern, Syllabus & Aggregate Formula Explained",
        "date": "July 15, 2026",
        "tag": "MDCAT",
        "excerpt": "200 MCQs, 3 hours, no negative marking. But the real battle is the 50% MDCAT + 40% FSc + 10% Matric aggregate. A simple guide for pre-medical students and their parents.",
        "sources": [("PMDC: Pakistan Medical & Dental Council", "https://pmdc.pk/"),
                    ("UHS: University of Health Sciences, Lahore", "https://www.uhs.edu.pk/")],
        "body": """
<p>MDCAT (Medical & Dental College Admission Test) is mandatory for admission to all MBBS and BDS programmes in Pakistan. It is conducted under <b>PMDC</b> rules and is accepted by public and private medical colleges across the country, including NUMS-affiliated admissions that use the national MDCAT.</p>
<h2>Paper pattern (latest)</h2>
<ul>
<li><b>Total MCQs:</b> 200 (Biology 68, Chemistry 54, Physics 54, English 18, Logical Reasoning 6)</li>
<li><b>Time:</b> 3 hours (180 minutes), about 54 seconds per MCQ</li>
<li><b>Negative marking:</b> none, so attempt every single question</li>
<li><b>Minimum pass marks:</b> 55% for MBBS, 50% for BDS</li>
</ul>
<h2>How the merit (aggregate) is calculated</h2>
<p>Public-sector admissions (through UHS in Punjab) use this formula:</p>
<ul>
<li>MDCAT score: <b>50%</b></li>
<li>FSc (HSSC/equivalent) marks: <b>40%</b></li>
<li>Matric (SSC/equivalent) marks: <b>10%</b></li>
</ul>
<p>Use our free <a href="/mdcat/#calculator">MDCAT aggregate calculator</a>. Enter your three marks and it shows your exact aggregate with a full breakdown.</p>
<div class="callout"><b>Reality check:</b> closing merits for government MBBS seats in Punjab stay very high (around 91-93%+). Since 270,000+ students compete, treat MDCAT like a full-time subject from day one of 2nd year.</div>
<h2>Smart preparation in 3 steps</h2>
<ol>
<li><b>Master your FSc books first</b>. MDCAT MCQs come from the same concepts, just asked in tricky language.</li>
<li><b>Practice chapter-wise MCQs daily</b>. Free downloadable MCQ banks for Class 11 &amp; 12 physics, chemistry and biology are being added on the subject pages.</li>
<li><b>Mock-test every weekend</b> in the last 8 weeks, strictly in one 3-hour sitting.</li>
</ol>""",
    },
    {
        "slug": "class-12-new-books-2026",
        "title": "2nd Year (Class 12) New Books 2026-27: What Students Should Know",
        "date": "July 8, 2026",
        "tag": "Syllabus",
        "excerpt": "The new HSSC-II books complete Punjab's curriculum change. What 2nd year students should check before session starts, and how the new books affect MDCAT and ECAT preparation.",
        "body": """
<p>Class 12 (session <b>2026-27</b>) completes Punjab's move to the new PECTAA books for intermediate. Because MDCAT and ECAT draw heavily from 2nd year content, starting the session with the correct books genuinely matters.</p>
<h2>Before the session starts</h2>
<ol>
<li>Buy only the <b>PECTAA editions notified for 2026-27</b>, and confirm the print year on the title page.</li>
<li>Get the official free PDFs from our <a href="/ebooks/">eBooks page</a> so you always have a clean reference copy.</li>
<li>If you are a <b>repeater or improver</b> on the old syllabus, confirm your board's policy first. Your paper may follow the old course, and mixing the two is the costliest mistake of the year.</li>
</ol>
<h2>How StudySapiens handles the new books</h2>
<p>We do not guess chapter lists. Notes, solved exercises and MCQ banks are made by teachers from the printed books and verified by subject experts before upload. Files arrive steadily so each resource can be checked carefully.</p>
<h2>Timing your preparation</h2>
<p>Boards usually hold intermediate exams in May-June. A safe plan: finish syllabus coverage by January, revise in February-March (pairing schemes help here), and dedicate April to timed practice. Everything we upload lands on your subject page first, so check it weekly.</p>""",
    },
    {
        "slug": "pairing-scheme-guide",
        "title": "What is a Pairing Scheme? How Toppers Actually Use It",
        "date": "June 28, 2026",
        "tag": "Exam Strategy",
        "excerpt": "Pairing schemes are legal, official, and the single most underused advantage a board student has. Learn how to read one, and how to squeeze 10-15 extra marks out of it.",
        "body": """
<p>A <b>pairing scheme</b> (also called assessment scheme or paper scheme) is issued by the boards to show how the paper will be built from the book: how many MCQs come from each chapter, which chapters are paired together in long questions, and how short-question choices are distributed.</p>
<h2>How to read one in 60 seconds</h2>
<ol>
<li><b>Objective part:</b> MCQs are normally taken from every chapter, so no chapter can be fully skipped.</li>
<li><b>Short questions:</b> you are given extra choices (e.g. attempt 8 out of 12). The scheme tells you which chapters appear in each short-question block.</li>
<li><b>Long questions:</b> each long question combines parts from <b>two paired chapters</b> (e.g. Q5 = Chapter 2 + Chapter 5). Master the pairs, not just chapters.</li>
</ol>
<div class="callout"><b>Safety rule:</b> a pairing scheme tells you the <i>pattern</i>, not the questions. Use it to prioritise revision, never as a licence to skip chapters. Boards can and do surprise.</div>
<h2>The topper's method</h2>
<p>Toppers go through the scheme at least three times: in December (to plan coverage), in February (to decide revision order) and two weeks before the paper (to lock long-question pairs). On StudySapiens, every class has its own <a href="/pairing-scheme/">pairing scheme page</a>. Official schemes are uploaded the day boards release them, and our teacher-prepared practice schemes help you till then.</p>""",
    },
    {
        "slug": "css-2027-guide",
        "title": "CSS Exam: Eligibility, Subjects & a 12-Month Preparation Plan",
        "date": "July 18, 2026",
        "tag": "CSS",
        "excerpt": "Dreaming of PAS, PSP or the Foreign Service? Start with the facts: who can apply, how the MPT screening works, which subjects carry the most marks. Plus a realistic month-by-month plan.",
        "body": """
<p>The CSS (Central Superior Services) exam, conducted by <b>FPSC</b> every year, is Pakistan's gateway into 12 occupational groups including PAS (administrative), PSP (police) and FSP (foreign service). Every year around 30,000+ candidates appear for roughly 300-400 seats, so a planned start matters more than a hard start.</p>
<h2>Eligibility in one minute</h2>
<ul>
<li><b>Education:</b> Bachelor's degree (14 years of education) with at least a 2nd division</li>
<li><b>Age:</b> 21-30 years (cut-off 31 December of the exam year; up to 32 with age relaxation categories)</li>
<li><b>Citizenship:</b> Pakistani / AJK national; fresh candidates get <b>3 attempts</b></li>
</ul>
<h2>The three filters</h2>
<ol>
<li><b>MPT (screening, since CSS-2022):</b> an MCQ-based test you must pass to reach the written exam.</li>
<li><b>Written exam (1200 marks):</b> 6 compulsory papers of 600 marks + optional subjects of 600 marks chosen from 7 groups.</li>
<li><b>Medical + viva voce (300 marks):</b> final allocation on overall merit + provincial quota.</li>
</ol>
<h2>Compulsory subjects (600 marks)</h2>
<ul>
<li>English Essay (100) · English Précis & Composition (100) · General Science & Ability (100) · Current Affairs (100) · Pakistan Affairs (100) · Islamic Studies (100)</li>
</ul>
<div class="callout"><b>Killer papers:</b> most candidates fail English Essay or Précis. Start writing practice from month one, even before choosing optionals.</div>
<p>Read the full subject lists and our month-by-month strategy on the <a href="/css/">CSS page</a>.</p>""",
    },
    {
        "slug": "board-exams-timeline-2027",
        "title": "Matric & Inter Exams 2027: Expected Timeline for Punjab Boards",
        "date": "July 26, 2026",
        "tag": "Date Sheet",
        "excerpt": "All 9 BISE boards of Punjab move together. Based on recent years, here is when date sheets, exams and results are expected in 2027. Bookmark this and plan backwards.",
        "body": """
<p>All nine boards of Punjab (Lahore, Gujranwala, Multan, Faisalabad, Rawalpindi, Sargodha, Bahawalpur, DG Khan, Sahiwal) conduct exams on almost the same schedule. While exact dates are announced by each board, the recent-years pattern is very stable:</p>
<h2>Expected timeline (2027)</h2>
<ul>
<li><b>Matric date sheet:</b> expected <b>February 2027</b></li>
<li><b>Matric annual exams:</b> expected <b>March 2027</b></li>
<li><b>Intermediate date sheet:</b> expected <b>April 2027</b></li>
<li><b>Intermediate annual exams:</b> expected <b>May-June 2027</b></li>
<li><b>Results:</b> matric usually July-August; intermediate September-October</li>
</ul>
<div class="callout"><b>Important:</b> these are expected dates for planning only. The official date sheet is issued by your own BISE. The moment any board uploads its date sheet, we post it on our <a href="/date-sheet/">Date Sheet page</a> and in the ticker above.</div>
<h2>Plan backwards from the paper</h2>
<p>Count the weeks left, divide chapters by weeks, and keep the last 20 days only for past papers and pairing-scheme revision. A date written on paper beats an ambition kept in your head. Our downloadable chapter MCQ banks are the quickest way to see whether a week's target actually landed.</p>""",
    },
]

# ------------------------------------------------------------------
# FAQ (homepage) · also used for FAQ JSON-LD
# ------------------------------------------------------------------
FAQS = [
    ("Is StudySapiens completely free?",
     "Yes. Every note, exercise solution, MCQ test, pairing scheme and calculator on StudySapiens is 100% free for students. No sign-up or paywall."),
    ("Which syllabus do your notes follow?",
     "Only the NEW PCTB / PECTAA syllabus (National Curriculum). Class 9 and 11 follow the 2025-26 books; Class 10 and 12 follow the 2026-27 books. We do not re-label old-syllabus content as new. A file goes live only after it is checked against the printed book."),
    ("Which boards are covered?",
     "All nine BISE boards of Punjab: Lahore, Gujranwala, Multan, Faisalabad, Rawalpindi, Sargodha, Bahawalpur, DG Khan and Sahiwal. They are all covered because PCTB books and pairing schemes are common to every board."),
    ("I found a mistake in a note. What should I do?",
     "Please tell us! StudySapiens is made by teachers and verified by subject experts. Student feedback also helps keep it accurate. Email a screenshot to admin.studysapiens@gmail.com. Genuine corrections are fixed quickly and credited in our updates."),
    ("Can I get notes in Urdu medium?",
     "Content is currently in easy English, with Urdu translations for English-subject lessons in progress. A full Urdu-medium track for science subjects is on our roadmap. Join the update list to know when it launches."),
    ("Is everything on StudySapiens free?",
     "Yes. Notes, solved exercises, MCQ banks, guess papers, pairing schemes, past papers and the calculators are free for every student, forever. No sign-up, no trial, no catch."),
    ("How often is the website updated?",
     "New files are uploaded on a rolling schedule throughout the session. Pairing schemes and date sheets appear the moment boards release them. The gold “NEW” badge on any page means it was added in the last 30 days."),
    ("Can I download notes as PDF?",
     "Yes. That is exactly how StudySapiens works now. Every subject page has download boxes for notes, solved exercises, MCQ banks, guess papers and pairing schemes. PDF/DOC files open in your browser with one click and can be saved or printed."),
]

# ------------------------------------------------------------------
# MDCAT page data
# ------------------------------------------------------------------
MDCAT = {
    "weights": {"matric": 10, "fsc": 40, "mdcat": 50},
    "pattern": [
        ("Biology", 68), ("Chemistry", 54), ("Physics", 54),
        ("English", 18), ("Logical Reasoning", 6),
    ],
    "syllabus": {
        "Biology": ["Biodiversity & classification", "Cell structure and function", "Biological molecules & enzymes",
                    "Bioenergetics (respiration & photosynthesis)", "Cell cycle & division", "Human physiology: digestive, respiratory, circulatory, urinary, nervous & endocrine systems",
                    "Reproduction & development", "Inheritance & chromosomes", "Biotechnology, immunity & pharmacology", "Evolution & ecology"],
        "Chemistry": ["Atomic structure & periodicity", "Chemical bonding", "States of matter & gases",
                      "Stoichiometry", "Chemical equilibrium & kinetics", "Electrochemistry", "Energetics",
                      "Acids & bases", "Organic chemistry: hydrocarbons, alcohols, carbonyls, acids", "Inorganic: nitrogen, sulfur, halogens & atmosphere"],
        "Physics": ["Measurements & units", "Motion, force & energy", "Circular & rotational motion",
                    "Waves, sound & vibrations", "Light & physical optics", "Heat & thermodynamics",
                    "Electrostatics & current electricity", "Electromagnetism", "Modern physics: relativity, quantum & nuclear"],
        "English": ["Synonyms & antonyms", "Sentence completion", "Spot the error", "Prepositions & grammar",
                    "Sentence structure & tenses", "Reading comprehension vocabulary"],
        "Logical Reasoning": ["Critical thinking", "Letter & number series", "Logical deductions", "Cause & effect", "Analytical puzzles"],
    },
    "timeline": [
        ("Register online", "PMDC opens registration on its portal a few weeks before the test. You need your CNIC/B-form and a photo."),
        ("Download roll number slip", "Print your admit card. It shows your test city and reporting time. No slip, no entry."),
        ("Test day", "200 MCQs in 180 minutes. No negative marking, so attempt everything. Reach the centre at least an hour early."),
        ("Result (same week)", "MDCAT results are announced within days. Your result card is used by all provinces and by NUMS."),
        ("Apply to colleges", "In Punjab, UHS opens admissions after FSc results; your aggregate (50/40/10) decides your merit position."),
        ("Merit lists & admission", "Public colleges publish 2-3 merit lists; private colleges have their own merit calculations. Closing merits are highest in the first list."),
    ],
}

# ------------------------------------------------------------------
# CSS page data
# ------------------------------------------------------------------
CSS_EXAM = {
    "compulsory": [
        ("English Essay", 100, "Write a 2500-3000 word argumentative essay."),
        ("English (Precis & Composition)", 100, "Precis, comprehension, grammar, expansion."),
        ("General Science & Ability", 100, "Everyday science + quantitative & analytical ability."),
        ("Current Affairs", 100, "National & international issues in the news."),
        ("Pakistan Affairs", 100, "1857 to date: ideology, history, economy, foreign policy."),
        ("Islamic Studies", 100, "Quranic teachings, Seerah, Islamic thought (Ethics for non-Muslims)."),
    ],
    "groups": [
        ("Group 1 (choose 200)", "Accounting & Auditing, Economics, Computer Science, Political Science, International Relations"),
        ("Group 2 (choose 200)", "Physics, Chemistry, Applied Mathematics, Pure Mathematics, Statistics, Geology"),
        ("Group 3 (choose 100)", "Business Administration, Public Administration, Governance & Public Policies"),
        ("Group 4 (choose 100)", "History of Pakistan & India, Islamic History & Culture, British History, European History, History of USA"),
        ("Group 5 (choose 100)", "Gender Studies, Environmental Sciences, Agriculture & Forestry, Botany, Zoology, English Literature, Urdu Literature"),
        ("Group 6 (choose 100)", "Law, Constitutional Law, International Law, Muslim Law & Jurisprudence, Mercantile Law, Criminology, Philosophy"),
        ("Group 7 (choose 100)", "Journalism & Mass Communication, Psychology, Geography, Sociology, Anthropology, Punjabi, Sindhi, Pashto, Balochi, Persian, Arabic"),
    ],
    "strategy": [
        ("Months 1-2 · Foundation", "Confirm eligibility, read the FPSC rules and past papers, shortlist optional subjects (overlap with your degree = half the work saved), and start daily Dawn reading. Just 30 minutes with a vocabulary diary."),
        ("Months 3-6 · Core + English", "Finish GSA & Pakistan Affairs while writing one essay outline every week and one full essay every two weeks. Get essays checked. Unmarked essays don't improve."),
        ("Months 7-9 · Optionals + MPT", "Complete optional subjects with notes of your own (A4 summaries, not photocopies). Give the MPT screening. Qualifying it is now the first gate."),
        ("Months 10-12 · Written sprint", "Past papers under timed conditions: two papers a week, examiner-style answers (intro, headings, conclusion). Revise current affairs from your own notes, not fresh sources."),
    ],
    "material": [
        ("English", "Dawn editorials daily · 'Exploring the World of English' (Sayyid Saadat Ali Shah) · Wren & Martin for grammar basics"),
        ("Pakistan Affairs", "Analytical reading in the style of 'Pakistan: A Hard Country' · Ikram Rabbani's book · recorded lectures for pre-1947 timeline"),
        ("Current Affairs", "Dawn + JWT (Jahangir's World Times) · monthly compilations of your own bullet notes"),
        ("GSA / Everyday Science", "FPSC past papers (most repeated bank) · NCERT-style basics for physics/bio concepts"),
        ("Islamic Studies", "Standard FPSC-aligned Islamiat guide + direct translation references for Quranic verses"),
    ],
}

# ------------------------------------------------------------------
# CONTACT quick topics
# ------------------------------------------------------------------
CONTACT_TOPICS = ["Question about notes", "Correction in content", "Request notes / paper", "Partnership / advertise", "Other"]

# ==========================================================================
# ROUND 7: competitor-gap expansion (results, boards, 4 new subjects,
# model/test/numerical slots, formulas, english corner, ECAT corner, tests)
# ==========================================================================

# ---- 4 compulsory subjects we were missing ---------------------------
SUBJECTS.update({
    "urdu":              {"name": "Urdu",              "hue": "var(--c-urdu)",   "icon": "notes"},
    "islamiat":          {"name": "Islamiat",          "hue": "var(--c-islam)",  "icon": "moon"},
    "pak-studies":       {"name": "Pak Studies",       "hue": "var(--c-pakst)",  "icon": "flag"},
    "tarjuma-tul-quran": {"name": "Tarjuma-tul-Quran", "hue": "var(--c-tq)",     "icon": "book"},
})
SUBJECT_ORDER += ["urdu", "islamiat", "pak-studies", "tarjuma-tul-quran"]

# which classes each subject actually belongs to (boards notify subject sets class by class;
# anything not listed here applies to all four classes)
SUBJECT_CLASSES = {
    "urdu":              ["9", "10", "11", "12"],
    "islamiat":          ["9", "11"],       # no prescribed Class 10 book
    "pak-studies":       ["10", "12"],      # no prescribed Class 9 book
    "tarjuma-tul-quran": ["9", "10", "11", "12"],
}

SUBJECT_INFO.update({
    "urdu": {
        "about": "Urdu is the compulsory national-language paper every matric and inter student sits. The new books mix prose and poetry lessons with grammar, letter and application writing, summaries and explanation (tashreeh) practice. Marks hide in presentation: the correct format for letters, neat paragraphing and quoted lines from the lesson.",
        "skills": ["Lesson summaries & question answers in simple wording",
                    "Ghazal and nazm tashreeh with poet names done right",
                    "Grammar rules, singular-plural, idioms & correction exercises",
                    "Letters, applications & essays in the exact board format"],
        "tip": "Board markers reward format as much as content. Practise one letter or application a week until the addresses, salutation and closing lines become automatic."},
    "islamiat": {
        "about": "Islamiat at matric and 1st year level is a short syllabus with a high return: Quranic verses with translation, Ahadith, Seerah topics and short answers. Because questions repeat patterns across boards, a verified question-answer file is one of the fastest ways to secure marks.",
        "skills": ["Ayat & Ahadith with correct translation and references",
                    "Short & long question answers in marker-friendly points",
                    "Important terms, definitions and MCQ practice",
                    "Guess paper & pairing scheme for focused revision"],
        "tip": "Memorise translations word-perfect. One wrong word in an Ayat translation costs more marks than a weak long answer."},
    "pak-studies": {
        "about": "Pak Studies (Mutalia Pakistan) comes in 10th class and 2nd year. It moves from the Pakistan Movement to geography, resources, economy and foreign policy. The answers are factual, so crisp notes with dates, names and numbered points beat long paragraphs every single time.",
        "skills": ["Chapter summaries with dates, names & events in order",
                    "Long questions broken into point-wise model answers",
                    "Resources, economy & population tables for quick recall",
                    "MCQ bank & guess paper for the objective part"],
        "tip": "Make a one-line-per-event timeline from 1857 to 1947. Half the long questions are just that timeline in disguise."},
    "tarjuma-tul-quran": {
        "about": "Tarjuma-tul-Quran is the new compulsory subject boards added class by class: selected Surahs and verses with word-by-word translation and explanation. It is genuinely score-able when you follow the exact board-approved translation, which is exactly what our files are checked against.",
        "skills": ["Word-by-word translation of the selected Surahs & verses",
                    "Short question answers from the official book",
                    "MCQs on translations, themes & vocabulary",
                    "Clearly labelled uploads as boards notify the exact scope each year"],
        "tip": "Practise the translation in writing, not just by reading. The paper asks you to translate specific verses, and writing builds the vocabulary memory."},
})

# ---- 3 new download slots --------------------------------------------
FILE_CATEGORIES += [
    ("numericals", "calc",  "Solved Numericals", "Step-by-step numerical problems with units (PDF)"),
    ("model",      "star",  "Model Papers",      "Official sample / pattern papers when boards issue them"),
    ("testpapers", "notes", "Test Papers",       "Chapter, half-book & full-book tests (PDF)"),
]
# solved numericals only make sense for these subjects
NUMERICAL_SUBJECTS = {"physics", "chemistry", "mathematics"}

# ------------------------------------------------------------------
# CHAPTER SETS: subjects whose downloads organize chapter by chapter.
# Unit titles for Class 10 Chemistry = new 2026-27 PCTB/PECTAA book
# (verified against public Punjab-board listings; add more sets the same way).
# ------------------------------------------------------------------
CHAPTERS = {
    ("11", "biology"): [
        (1, "Biodiversity and Classification"),
        (2, "Bacteria and Viruses"),
        (3, "Cells and Subcellular Organelles"),
        (4, "Biomolecules"),
        (5, "Enzymes"),
        (6, "Bioenergetics"),
        (7, "Structural and Computational Biology"),
        (8, "Plant Physiology"),
        (9, "Human Digestive System"),
        (10, "Human Respiratory System"),
        (11, "Human Circulatory System"),
        (12, "Human Skeletal and Muscular Systems"),
    ],
    ("10", "chemistry"): [
        (14, "States of Matter and Phase Changes"),
        (15, "Stoichiometry"),
        (16, "Electrochemistry"),
        (17, "Reaction Kinetics"),
        (18, "Salts"),
        (19, "Nitrogen and Sulphur"),
        (20, "Water"),
        (21, "Organic Chemistry"),
        (22, "Hydrocarbons"),
        (23, "Alcohols (Monohydroxy Alkanes)"),
        (24, "Carboxylic Acids"),
        (25, "Biochemistry"),
        (26, "Polymers"),
    ],
    # Class 10 Biology (PECTAA 2026-27): titles verified against the owner's
    # solved-exercise PDFs + ilmkidunya / studyplusplus / maryamnotes (Nov 2026)
    ("10", "biology"): [
        (1, "Human Digestive System"),
        (2, "Human Respiratory System"),
        (3, "Human Blood Circulatory System"),
        (4, "Human Urinary System"),
        (5, "Coordination"),
        (6, "Reproductive System"),
        (7, "Inheritance"),
        (8, "Biotechnology"),
        (9, "Diseases and Immunity"),
        (10, "Evolution"),
    ],
    # Class 10 Computer Science (PECTAA 2026-27): titles verified against the
    # owner's solved-exercise PDFs + ilmkidunya / maryamnotes / punjabboardnotes
    # (Nov 2026). Book: "Computer Science and Entrepreneurship" (PCTB).
    ("10", "computer-science"): [
        (1, "Operating Systems: Structure and Services"),
        (2, "System Recovery and Advanced Maintenance"),
        (3, "Introduction to Python Programming"),
        (4, "Control Structures in Python"),
        (5, "Data Science"),
        (6, "Introduction to Artificial Intelligence (AI) and Machine Learning (ML)"),
        (7, "Applications of AI"),
        (8, "Digital Entrepreneurship"),
    ],
    # Class 10 English (PCTB / PECTAA 2026-27): unit titles verified against the
    # owner's solved PDFs + freeilm / ilmkidunya / maryamnotes / studyplusplus
    # (Nov 2026). Reviews 1 and 2 cover units 1-5 and 6-10 and are not chapters.
    ("10", "english"): [
        (1, "Hazrat Muhammad (PBUH): Social Reforms for Women, Orphans and Slaves"),
        (2, "My Beloved Pakistan (Poem)"),
        (3, "Digital Globalisation Transforming the English Language"),
        (4, "The Earth: Act Now for Tomorrow"),
        (5, "The Happy Prince"),
        (6, "Drug Abuse"),
        (7, "Time (Poem)"),
        (8, "Pollution-free Pakistan with Greenery all Around"),
        (9, "The Road Not Taken (Poem)"),
        (10, "The Three Questions"),
    ],
    # Class 10 Mathematics (PCTB / PECTAA 2026-27): 12 units verified against the
    # owner's solved PDFs + class10.pk / ilmkidunya / maryamnotes / notesofmath
    # (Nov 2026).
    ("10", "mathematics"): [
        (1, "Complex Numbers"),
        (2, "Quadratic Equations and Inequalities"),
        (3, "Matrices and Determinants"),
        (4, "Functions and Graphs"),
        (5, "Algebraic Fractions"),
        (6, "Vectors in Plane"),
        (7, "Trigonometry"),
        (8, "Chords and Arcs of a Circle"),
        (9, "Tangent and Angles of a Circle"),
        (10, "Practical Geometry of Circles"),
        (11, "Information Handling"),
        (12, "Probability"),
    ],
    # Class 10 Pakistan Studies (PCTB / PECTAA 2026-27, NEW edition order):
    # chapters verified from the owner's own PDF headers (Urdu) and hiraacademy's
    # 2026 PECTAA edition page. NOTE: this new-edition order differs from older
    # sites that still list Geography as chapter 4.
    ("10", "pak-studies"): [
        (1, "Ideological Basis of Pakistan"),
        (2, "The Pakistan Movement and Emergence of Pakistan"),
        (3, "History of Pakistan (1971 onwards)"),
        (4, "Pakistan and World Affairs"),
        (5, "Land and Environment"),
        (6, "Population, Society and Culture of Pakistan"),
        (7, "Economic Development of Pakistan"),
        (8, "Women Empowerment"),
    ],
    # Class 10 Physics (PCTB / PECTAA 2026-27): chapters are numbered 10-21
    # (the new book continues the Class 9 numbering). Titles verified against the
    # owner's solved PDFs + class10.pk / ilmkidunya / maryamnotes / studyplusplus
    # (Nov 2026).
    ("10", "physics"): [
        (10, "Thermal Physics"),
        (11, "Transfer of Thermal Energy"),
        (12, "Waves"),
        (13, "Sound"),
        (14, "Light"),
        (15, "Electrostatics"),
        (16, "Electricity"),
        (17, "Electromagnetism"),
        (18, "Electromagnetic Induction and Electromagnetic Waves"),
        (19, "Electronics"),
        (20, "Atomic and Nuclear Physics"),
        (21, "Space and Environment"),
    ],
    # Class 9 Biology (PCTB / PECTAA 2026-27): titles verified against the owner's
    # solved PDFs + parho.pk / ilmkidunya / maryamnotes / hiraacademy / stepacademy
    # (Nov 2026).
    ("9", "biology"): [
        (1, "The Science of Biology"),
        (2, "Biodiversity"),
        (3, "The Cell"),
        (4, "Cell Cycle"),
        (5, "Tissues, Organs and Organ Systems"),
        (6, "Biomolecules"),
        (7, "Enzymes"),
        (8, "Bioenergetics"),
        (9, "Plant Physiology"),
        (10, "Reproduction in Plants"),
        (11, "Biostatistics"),
    ],
    # Class 9 Chemistry (PCTB / PECTAA 2026-27): titles verified against the
    # owner's solved PDFs + maryamnotes / studyplusplus / ilmkidunya /
    # stepacademy / ahsa.pk (Nov 2026). Chapter 12 uses the full board title
    # "Empirical Data Collection and Analysis".
    ("9", "chemistry"): [
        (1, "States of Matter and Phase Changes"),
        (2, "Atomic Structure"),
        (3, "Chemical Bonding"),
        (4, "Stoichiometry"),
        (5, "Energetics"),
        (6, "Equilibria"),
        (7, "Acid Base Chemistry"),
        (8, "Periodic Table and Periodicity"),
        (9, "Group Properties and Elements"),
        (10, "Environmental Chemistry"),
        (11, "Hydrocarbons"),
        (12, "Empirical Data Collection and Analysis"),
        (13, "Laboratory and Practical Skills"),
    ],
    # Class 9 Computer Science (PCTB / PECTAA 2026-27). Book title is
    # "Computer Science & Entrepreneurship". Titles verified against the owner's
    # solved PDFs + maryamnotes (book + notes) / studyplusplus (Nov 2026).
    # NOTE: some older listings show a 12-chapter scheme; the 2026-27 book has 9.
    ("9", "computer-science"): [
        (1, "Introduction to Computational Systems"),
        (2, "System Design and Troubleshooting"),
        (3, "Introduction to Computer Networks"),
        (4, "Computational Thinking"),
        (5, "Web Development with HTML, CSS and JavaScript"),
        (6, "Data Science and Data Gathering"),
        (7, "Emerging Technologies in Computer Science"),
        (8, "Ethical, Social, and Legal Concerns in Computer Usage"),
        (9, "Entrepreneurship in Digital Age"),
    ],
    # Class 9 English (PCTB / PECTAA 2026-27): 11 units verified against the
    # owner's solved PDFs + ilmkidunya (book + notes) / maryamnotes /
    # studyplusplus / freebooks.pk (Nov 2026). Full board titles used for units
    # 8-10. Some listings show a 12th "Grammar and Composition" unit; the
    # 2026-27 book has 11 units.
    ("9", "english"): [
        (1, "The Saviour of Mankind"),
        (2, "Patriotism"),
        (3, "Daffodils (Poem)"),
        (4, "Hazrat Asma (R.A)"),
        (5, "Women Empowerment through Entrepreneurship"),
        (6, "The Value of Time"),
        (7, "If (Poem)"),
        (8, "The Impact of Globalisation on Culture and Economy"),
        (9, "Quality Education: A Key to Success"),
        (10, "The Silent Predator and the Majestic Prey: Snow Leopard and Markhor"),
        (11, "The Dear Departed (One-Act Play)"),
    ],
    # Class 9 Islamiat (PCTB / PECTAA 2026-27): 7 units. Files are Urdu medium.
    # Titles verified against the owner's own solved PDFs (Urdu text decoded and
    # spot-checked per chapter) + ilmkidunya (book + notes) / parho.pk /
    # class9.pk (Nov 2026).
    ("9", "islamiat"): [
        (1, "Quran-e-Majeed aur Hadees-e-Nabwi (S.A.W)"),
        (2, "Imaniyat aur Ibadaat"),
        (3, "Seerat-e-Nabwi (S.A.W)"),
        (4, "Akhlaq-o-Adaab"),
        (5, "Husn-e-Mamlaat aur Muashrat"),
        (6, "Hidayat ke Sar Chashme aur Mashaheer-e-Islam"),
        (7, "Islami Taleemaat aur Asr-e-Hazir ke Taqaze"),
    ],
    # Class 9 Mathematics (PCTB / PECTAA 2026-27): 13 units, NEW book.
    # Units 1-5 confirmed directly from the owner's own PDFs (each file header
    # names the chapter: Real Numbers, Logarithms, Sets and Functions,
    # Factorization and Algebraic Manipulation, Linear Equations and
    # Inequalities). Full 13-unit list verified against hiraacademy /
    # swalnama.pk / ahsa.pk / taleemguru (Nov 2026).
    ("9", "mathematics"): [
        (1, "Real Numbers"),
        (2, "Logarithms"),
        (3, "Sets and Functions"),
        (4, "Factorization and Algebraic Manipulation"),
        (5, "Linear Equations and Inequalities"),
        (6, "Trigonometry"),
        (7, "Coordinate Geometry"),
        (8, "Logic"),
        (9, "Similar Figures"),
        (10, "Graphs of Functions"),
        (11, "Loci and Construction"),
        (12, "Information Handling"),
        (13, "Probability"),
    ],
    # Class 9 Physics (PCTB / PECTAA 2026-27): 9 chapters, titles verified
    # against the owner's solved PDFs + ilmdo / pdfclassnotes / studyplusplus /
    # punjabboardnotes / hsanotes (Nov 2026).
    ("9", "physics"): [
        (1, "Physical Quantities and Measurements"),
        (2, "Kinematics"),
        (3, "Dynamics"),
        (4, "Turning Effects of Force"),
        (5, "Work, Energy and Power"),
        (6, "Mechanical Properties of Matter"),
        (7, "Thermal Properties of Matter"),
        (8, "Magnetism"),
        (9, "Nature of Science"),
    ],
    # Class 9 Tarjuma-tul-Quran (PCTB / PECTAA 2026-27). Each "chapter" is a
    # Surah; the number is the Surah number so students can find it either way.
    # Every surah name was confirmed by decoding the Urdu text inside the
    # owner's own PDFs (Nov 2026). Set = Surahs 19-22, 25-32 and 34-45;
    # Surahs 23, 24 and 33 are deliberately not included.
    ("9", "tarjuma-tul-quran"): [
        (19, "Surah Maryam"),
        (20, "Surah Taha"),
        (21, "Surah Al-Anbiya"),
        (22, "Surah Al-Hajj"),
        (25, "Surah Al-Furqan"),
        (26, "Surah Ash-Shuara"),
        (27, "Surah An-Naml"),
        (28, "Surah Al-Qasas"),
        (29, "Surah Al-Ankabut"),
        (30, "Surah Ar-Rum"),
        (31, "Surah Luqman"),
        (32, "Surah As-Sajdah"),
        (34, "Surah Saba"),
        (35, "Surah Fatir"),
        (36, "Surah Ya-Sin"),
        (37, "Surah As-Saffat"),
        (38, "Surah Sad"),
        (39, "Surah Az-Zumar"),
        (40, "Surah Ghafir"),
        (41, "Surah Fussilat"),
        (42, "Surah Ash-Shura"),
        (43, "Surah Az-Zukhruf"),
        (44, "Surah Ad-Dukhan"),
        (45, "Surah Al-Jathiya"),
    ],
    # Class 10 Tarjuma-tul-Quran (PCTB / PECTAA 2026-27). Number = Surah number.
    # Every surah name confirmed by decoding the Urdu text inside the owner's
    # own PDFs (Nov 2026). Note: Surah 40 is called Al-Mu'min in the class 10
    # book and Ghafir in the class 9 book; both names are correct for it.
    ("10", "tarjuma-tul-quran"): [
        (6, "Surah Al-An'am"),
        (7, "Surah Al-A'raf"),
        (10, "Surah Yunus"),
        (11, "Surah Hud"),
        (13, "Surah Ar-Ra'd"),
        (14, "Surah Ibrahim"),
        (15, "Surah Al-Hijr"),
        (16, "Surah An-Nahl"),
        (17, "Surah Bani Israil"),
        (18, "Surah Al-Kahf"),
        (23, "Surah Al-Mu'minun"),
        (39, "Surah Az-Zumar"),
        (40, "Surah Al-Mu'min"),
        (41, "Surah Fussilat"),
        (42, "Surah Ash-Shura"),
    ],
}
# categories that become chapter-wise when a chapter set exists
CHAPTER_CATS = ("notes", "solutions", "mcq", "numericals")

# ---- the 9 BISE boards of Punjab, with verified contact data ---------
BOARDS = [
    {"slug": "lahore",      "short": "Lahore",      "name": "BISE Lahore",
     "districts": "Lahore, Kasur, Sheikhupura, Nankana Sahib",
     "sms": "800291", "site": "https://www.biselahore.com"},
    {"slug": "gujranwala",  "short": "Gujranwala",  "name": "BISE Gujranwala",
     "districts": "Gujranwala, Gujrat, Hafizabad, Mandi Bahauddin, Narowal, Sialkot",
     "sms": "800299", "site": "https://www.bisegrw.edu.pk"},
    {"slug": "rawalpindi",  "short": "Rawalpindi",  "name": "BISE Rawalpindi",
     "districts": "Rawalpindi, Attock, Chakwal, Jhelum",
     "sms": "800296", "site": "https://www.biserawalpindi.edu.pk"},
    {"slug": "faisalabad",  "short": "Faisalabad",  "name": "BISE Faisalabad",
     "districts": "Faisalabad, Chiniot, Jhang, Toba Tek Singh",
     "sms": "800240", "site": "https://www.bisefsd.edu.pk"},
    {"slug": "multan",      "short": "Multan",      "name": "BISE Multan",
     "districts": "Multan, Khanewal, Lodhran, Vehari",
     "sms": "800293", "site": "https://www.bisemultan.edu.pk"},
    {"slug": "sargodha",    "short": "Sargodha",    "name": "BISE Sargodha",
     "districts": "Sargodha, Bhakkar, Khushab, Mianwali",
     "sms": "800290", "site": "https://www.bisesargodha.edu.pk"},
    {"slug": "sahiwal",     "short": "Sahiwal",     "name": "BISE Sahiwal",
     "districts": "Sahiwal, Okara, Pakpattan",
     "sms": "800292", "site": "https://www.bisesahiwal.edu.pk"},
    {"slug": "bahawalpur",  "short": "Bahawalpur",  "name": "BISE Bahawalpur",
     "districts": "Bahawalpur, Bahawalnagar, Rahim Yar Khan",
     "sms": "800298", "site": "https://www.bisebwp.edu.pk"},
    {"slug": "dg-khan",     "short": "DG Khan",     "name": "BISE DG Khan",
     "districts": "Dera Ghazi Khan, Layyah, Muzaffargarh, Rajanpur",
     "sms": "800295", "site": "https://www.bisedgkhan.edu.pk"},
]
BOARD_BY_SLUG = {b["slug"]: b for b in BOARDS}

# ---- result windows (pattern of recent cycles; always labelled expected) ----
RESULT_WINDOWS = {
    "10": "Expected: first week of August 2027",
    "9":  "Expected: late August to early September 2027",
    "12": "Expected: late September 2027",
    "11": "Expected: late October 2027",
}

# ---- ECAT corner data (UET: 17% Matric + 50% FSc + 33% ECAT, out of 400) ---
ECAT = {
    "weights": {"matric": 17, "fsc": 50, "ecat": 33},
    "totals":  {"matric": 1100, "fsc": 1100, "ecat": 400},
    "pattern": [
        ("Mathematics", "30", "120"),
        ("Physics", "30", "120"),
        ("Chemistry or Computer Science", "30", "120"),
        ("English", "10", "40"),
        ("Total", "100", "400"),
    ],
    "facts": [
        "Duration: 100 minutes, about 1 minute per MCQ",
        "Computer-based test, conducted by UET at assigned centres",
        "No negative marking, so attempt everything",
        "Used by UET Lahore, UET Taxila and UET-affiliated colleges; other universities (NUST, GIKI, FAST) run their own tests",
        "Minimum FSc to sit it: usually 60% for engineering programmes, 50% for computing programmes",
    ],
    "journey": [
        ("Register online", "UET opens ECAT registration on its admission portal a few weeks before the test. You need your CNIC or B-form and a recent photo."),
        ("Choose your test centre", "Pick the nearest UET centre when you register. Print the admit card as soon as it appears in your portal."),
        ("Test day", "100 MCQs in 100 minutes on a computer. No negative marking, so attempt everything. Reach the centre early with your admit card and original ID."),
        ("Result within days", "UET announces ECAT results quickly on the same portal. Your score stays valid for that admission cycle."),
        ("Apply for admission", "After FSc results, apply through the UET admission portal. Your aggregate (17/50/33) decides your merit position."),
        ("Merit lists", "UET publishes several merit lists; each department and campus closes at its own aggregate. Apply to multiple programmes to stay safe."),
    ],
}

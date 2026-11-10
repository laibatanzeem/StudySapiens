======================================================================
 StudySapiens BLOG. How to publish a new post (60 seconds)
======================================================================

STEP 1. Create a new file in THIS folder:

        blogs/your-post-name.md

        The file name becomes the URL:
        blogs/how-to-revise-fast.md  ->  studysapiens.com/blog/how-to-revise-fast/

        Rules for the file name: small letters, hyphens between words,
        no spaces, no capitals. Example: mdcat-tips-2027.md

STEP 2. Start the file with the info block (between the --- lines):

        ---
        title: Your Post Title (keep it under 48 characters)
        description: One or two sentences for Google search results. (under 155)
        date: 2026-10-20
        updated: 2026-10-25
        tags: Study Tips, Class 9
        author: Your Name   (optional, default is StudySapiens Team)
        draft: true   (optional: post stays hidden while you write)
        ---

        date and updated use the format YYYY-MM-DD.
        "updated" is optional. Use it when you improve an old post.

STEP 3. Write the post under the info block. Supported formatting:

        ## Big heading         (shows in the "On this page" box)
        ### Small heading
        Normal paragraph text. Just write.
        **bold** and *italic* words
        - bullet list item
        1. numbered list item
        > quote / teacher tip box
        [link text](/classes/9/physics/)    internal links start with /
        ![alt text](/assets/img/hero.png)   images start with /

        Leave one empty line between paragraphs, and after lists.

STEP 4. Rebuild the site:

        python3 build.py

        Your post appears on /blog/, on the home page, in search.json
        and in sitemap.xml automatically. Article schema, breadcrumbs,
        reading time, share buttons and next/previous links are added
        for you.

IMPORTANT STYLE RULES
---------------------
1. Do NOT type em dashes or en dashes (the long dashes). The build
   converts them automatically, but better to avoid them. Use colons
   or short hyphens like 9-12 or 2500-3000.
2. Write simple English. Short sentences. Our readers are Class 9-12
   students whose first language is not English.
3. Fact check every date, formula and board rule twice before
   publishing. Google now expects manual fact checking, and so do we.
4. If something is only expected or rumored, label it "Expected".
5. 600-1500 words works best. Answer the question fully, then stop.

To edit a post: change the .md file, rebuild. To delete it: delete
the file, rebuild.

----------------------------------------------------------------------
AEO + GEO CHECKLIST: how to get quoted by Google AI, ChatGPT, Perplexity
----------------------------------------------------------------------
AI answer engines pick sources that answer questions directly and
clearly. When writing a post, follow this:

1. HEADINGS AS QUESTIONS. Turn H2s into the exact questions students
   type: "How many MCQs are in MDCAT 2026?" beats "Paper pattern info".
2. ANSWER FIRST, DETAIL AFTER. Right under each question heading, give
   the full answer in 2-4 short sentences (about 40-60 words). Then add
   the longer explanation below. AI engines quote that first block.
3. ONE IDEA PER SENTENCE. Short sentences are quoted more accurately.
4. NUMBERS AND STEPS WIN. Exact figures ("200 MCQs, 180 minutes, no
   negative marking") and numbered steps get picked up far more than
   vague advice.
5. TABLES FOR COMPARISONS. Use a small markdown table when comparing
   options (old vs new books, MBBS vs BDS marks). Tables survive the
   copy by AI engines better than prose.
6. CITE THE OFFICIAL SOURCE. When you state a rule or date, name its
   official source in the same paragraph (PMDC, UHS, your BISE). It
   builds E-E-A-T and AI engines prefer cited claims.
7. FRESHNESS. If you update a post with new info, bump the "updated:"
   line in the front matter. Fresh pages get cited more.
8. NEVER pad. Answer the question fully, then stop. Fluff drops both
   rankings and AI citations.
======================================================================

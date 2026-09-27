# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

I chose **Undergraduate Research Opportunities at Howard University (Finding Labs, Faculty Outreach, Summer Fellowships, and Student Realities)**.

This is a useful topic for a RAG system because getting research experience is a huge deal for Howard students who want to go to grad school, med school, or get an engineering job later. The problem is that a lot of the "how do I actually get into a lab" info isn't in one easy place. The official Howard websites list big formal programs (like Amgen Scholars or Karsh STEM Scholars) and have faculty directories, but they don't really explain the practical stuff, like how to find a professor who's actually taking students, how to email a professor cold, whether you should ask for course credit or a paid stipend, or how people end up presenting at Howard Research Month or publishing in *Ukweli*. That kind of info is scattered across The Hilltop articles, student profiles in The Dig, department webpages, and word of mouth. A RAG system that pulls all of this together in one place would actually be really helpful for students trying to figure this out.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | The Dig at Howard University — Camille Wimberly Goldwater Scholar Profile | University news feature (May 27, 2026): a biology undergraduate describes joining a microbiology lab in her first year, faculty and peer mentorship, summer research, symposium presentations, and the Goldwater Scholarship. | `https://thedig.howard.edu/all-stories/howard-university-student-camille-wimberly-selected-2026-goldwater-scholarship-recipient` |
| 2 | Howard University Karsh STEM Scholars Program (Official Site) | Official program page: full scholarship structure (tuition, room/board, books), mandatory summer research internships, mission to increase underrepresented-minority PhD/MD-PhD attainment, and program requirements. | `https://karshstemscholars.howard.edu/about` |
| 3 | The Hilltop (Student Newspaper) | News feature: "Beyond the Numbers: What R1 Status Can Mean for Howard" — interviews with three named undergraduate researchers on how R1 status affects lab access, funding, fellowships, and national-lab partnerships. | `https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/` |
| 4 | Howard University Office of Undergraduate Studies | Central portal for undergraduate research programs, institutional fellowships (Mellon Mays, FLAS), and research engagement opportunities. | `https://ous.howard.edu/undergraduate-research` |
| 5 | Howard University Provost's Office | Amgen Scholars Program at Howard: Structure of the 9-week residential summer research program in biotechnology, lab expectations, and stipends. | `https://provost.howard.edu/amgen-scholars` |
| 6 | Howard University Department of Afro-American Studies — Independent Study | Official independent-study instructions: a 3.0 cumulative weighted average by the end of the second year, a written faculty-supervision agreement, an approved proposal, and a request in the preceding semester. Includes proposal and full-time AFRO faculty-advisor requirements. | `https://afroamericanstudies.howard.edu/beyond-classroom/independent-study` |
| 7 | Ukweli: Howard University Undergraduate Research Journal | Official journal portal detailing student author guidelines, faculty mentor endorsements, submission types, and the peer-review/publishing process. | `https://coas.howard.edu/experiential-learning/independent-research/ukweli-howard-university-undergraduate-research-journal` |
| 8 | Howard University Research Month | Official portal for the annual university-wide research symposium, presentation categories, abstract submission deadlines, and student presentation awards. | `https://researchmonth.howard.edu/` |
| 9 | College of Engineering and Architecture (CEA) | Department of Electrical Engineering & Computer Science directory of active faculty research centers, labs, and sponsored projects, with named PI directors. | `https://cea.howard.edu/academics/departments/electrical-engineering-and-computer-science/research/research-centers-and` |
| 10 | Howard University Department of Chemistry | Undergraduate Research portal: project descriptions in computational modeling, nanoparticles, biomaterials, publication examples, and explicit instructions for cold-emailing faculty to join a lab. | `https://chemistry.howard.edu/academics/undergraduate-program/undergraduate-research` |

**Source revision (September 27, 2026):** The Dig profile replaces the inaccessible Reddit thread, and the Afro-American Studies guide replaces the unavailable Political Science PDF. The student-perspective source is university-published reporting with attributed student quotes, not an anonymous community discussion. Independent-study rules in this corpus now apply to Afro-American Studies; the former POLS GPA, credit, and grading rules are no longer evaluation evidence.

---

## Chunking Strategy

**Chunk size:** 500 characters (~100–125 tokens) for student commentary and news articles; 800 characters (~160–200 tokens) for administrative guides, lab directories, and procedural documents.

**Overlap:** 100 characters (~20–25 tokens) for student commentary; 150 characters (~30–35 tokens) for administrative guides and directories.

**Reasoning:**

My documents basically fall into two types, so I used two different chunk sizes:

1. *Student experiences and news (The Dig profile, The Hilltop article):*
   * These combine reporting with short student quotes about lab experience, mentorship, and research opportunities.
   * I used a smaller chunk size (500 characters) here because the articles move between reporting and individual student perspectives. If I made the chunks bigger, I'd end up mixing multiple people's opinions into one chunk, which would confuse the retrieval (the system wouldn't know whose comment it's even pulling up). If I made the chunks too small, I'd cut sentences into random fragments that don't make sense on their own, like a chunk that just says "you also have to email them first" with no context about what "them" even refers to.
   * I added a 100-character overlap to carry context between chunks. Exact character overlap can still start inside a sentence or word, so samples need manual inspection.
2. *Official/formal stuff (Amgen Scholars, Karsh Scholars, the Afro-American Studies independent-study guide, EECS lab listings):*
   * These are longer, more structured documents with steps, requirements, and rules that build on each other.
   * I used a bigger chunk size (800 characters) here because a lot of these documents have requirements that depend on each other and need to stay together. For example, the Afro-American Studies guide lists an academic threshold, a faculty-supervision agreement, and a written proposal, all pretty close together in the text. If I chunked it too small, I might split the academic threshold from the supervision requirement, and the chatbot could give a half-true answer.
   * I used a 150-character overlap so that when there's a section break, the requirement and the rule that goes with it don't get separated.

**Note:** Some formal sources (e.g., the Karsh Scholars "About" page, the Afro-American Studies independent-study guide) are pretty short, so they'll only make a few 800-character chunks each. That's fine — it just means the source itself is short, not that something went wrong with chunking.

**Implementation detail:** The custom recursive chunker uses the sizes above as
maximum character counts, preferring paragraph, line, sentence, then word
boundaries. Consecutive chunks retain exactly the configured character overlap;
an overlap may start inside a word or sentence. The active corpus consists of
10 HTML sources, each kept as a separate document with citation metadata.
The loader also supports Reddit JSON and PDFs for future manifests. HTML is parsed
to remove navigation and footer elements before regex whitespace cleanup.
`python ingest.py --check-tokens` checks actual MiniLM token counts, including
special tokens, against 256; the character-based estimates alone are not a
guarantee. A token overflow is reported as a source failure instead of truncated.

---

## Retrieval Approach

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2` (runs locally, 384 dimensions, 256-token maximum sequence length).

**Top-k:** 5 chunks.

**Why I picked k = 5:**
* If k is too low (like 2 or 3), the system might not pull in enough info to answer questions that have multiple parts, like comparing getting course credit vs. getting paid for research. You need chunks from more than one source to answer that well.
* If k is too high (like 10+), you start pulling in chunks that aren't actually relevant, which just adds noise and can confuse the LLM or make it mix up facts from unrelated sources.
* k = 5 feels like a good middle ground — enough chunks to mix an official guideline with a student's real experience, without drowning the model in irrelevant text.

**Why semantic search makes sense here:**
Semantic search compares the *meaning* of a query to the *meaning* of a chunk, not just the exact words. So if a student asks "how do I get paid for lab work," the system can still find chunks about "research stipends" or "fellowship funding" even though the word "paid" never shows up in those chunks. A basic keyword search (like ctrl+F) would completely miss that.

**Things I'd have to think about if this were a real production system:**
* **Weird vocabulary:** This topic uses a lot of specific jargon (PI, R1, REU, Karsh, Ukweli, Amgen, "independent study"). A bigger, more powerful embedding model like OpenAI's `text-embedding-3-small/large` or Cohere's `embed-english-v3.0` would probably understand this specific college jargon better than the small local model I'm using.
* **Length limits:** `all-MiniLM-L6-v2` can only handle up to 256 tokens per input before it starts cutting text off. My chunks (500–800 characters) fit fine under that limit, but if a bug ever let a chunk get too long (like over 1,000 characters), part of it could get silently cut off without me noticing, so I should test for that.
* **Speed vs. scale:** Running this small model locally on my laptop's CPU is fast enough for a small class project (under 30ms per query). But if Howard actually wanted to roll this out for thousands of students at once, they'd need real GPU servers or a hosted embedding API to keep up with all the traffic.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What does a Howard student receive as a Karsh STEM Scholar, and what is required of them in return? | Karsh STEM Scholars receive a scholarship covering tuition (75–100% depending on family income), room and board, and a books/supplies stipend. In return, scholars are required to complete summer research internships every year and are expected to ultimately pursue a PhD or combined MD/PhD in a STEM discipline. |
| 2 | What impact does Howard University's Carnegie R1 status have on student research opportunities, according to student researchers in The Hilltop? | Student researchers quoted in *The Hilltop* report that R1 status increases research funding, creates more research fellowships and scholarships, connects students to higher-profile external partnerships (such as Brookhaven National Laboratory and the National Renewable Energy Laboratory), and raises the university's credibility with outside institutions and donors. |
| 3 | What are the eligibility and commitment requirements for the Amgen Scholars Program at Howard University? | The Amgen Scholars Program is a 9-week intensive residential summer research program hosted through the Provost's Office. Applicants must be sophomores or above with a 3.2 cumulative GPA and an interest in a STEM PhD or MD/PhD. Selected undergraduates conduct hands-on biotechnology and molecular science research under faculty mentors, receive a $5,000 stipend plus housing, meals, and travel, and must present their findings at the Amgen Scholars Symposium. |
| 4 | What must a student arrange before beginning an Independent Study in Howard’s Department of Afro-American Studies? | The department requires a cumulative weighted average of 3.0 or better by the end of the second year, a written agreement from a full-time faculty member, and a written proposal submitted for approval. The request must be made in the preceding semester. A full-time AFRO professor must approve, supervise, and evaluate the project. These are department-specific requirements. |
| 5 | Where can Howard undergraduate students publish their independent research findings on campus? | Students can submit their manuscripts to *Ukweli: The Howard University Undergraduate Research Journal*, a student-led biannual peer-reviewed journal housed in the College of Arts and Sciences and supported by the Office of Undergraduate Studies, the Office of the Provost, and the Office of the Vice President for Research. |
| 6 | Do these sources establish an automatic university research stipend available without applying to a program or arranging a research opportunity? | The collected sources do not establish such an entitlement. They describe specific program benefits and application or mentorship arrangements. The system should explain that evidence limit rather than invent a university-wide funding policy or treat the Goldwater tuition scholarship as an automatic lab stipend. |
| 7 | How did Camille Wimberly begin undergraduate research, and what mentoring did she describe? | The Dig profile reports that she joined Dr. Karl Thompson’s microbiology lab in her first year at Howard. She describes support from older undergraduates and an available faculty mentor, and credits peer mentor Ananya Hota with help in coursework and her academic journey. This is one student’s experience, not a guaranteed placement route. |

---

## Anticipated Challenges

1. **Students and official pages don't use the same words:**
   * *Risk:* Students search using casual phrases like "how to get in a lab" or "paid research for sophomores," but the official pages use formal words like "independent study" or "research internship." Since my system relies on semantic similarity, this mismatch could sometimes lower the match quality for really slangy questions.
   * *Fix:* Clean up and normalize text during preprocessing, and maybe try adding a basic keyword search (like BM25) alongside the semantic search as a stretch feature, so exact keyword matches can help catch what semantic search misses.

2. **Multi-step instructions could get cut apart:**
   * *Risk:* Some official documents (like the Afro-American Studies independent-study guide) have rules that only make sense together, like "you need a 3.0 cumulative weighted average by the end of the second year AND a faculty-supervision agreement." If chunking splits these apart, the chatbot might answer with only half the requirement and mislead a student.
   * *Fix:* Use a chunking method that tries to respect natural breaks in the text (like paragraphs) and keep the 150-character overlap so related rules stay near each other. I'll also manually double check that this specific guide's requirements survive chunking correctly.

3. **Some official pages don't actually have much content:**
   * *Risk:* Some Howard department pages are mostly just navigation menus and links, not actual paragraphs of useful info. If I treat every source as equally rich in content, I might end up chunking a bunch of menu text and giving it the same retrieval weight as an actually useful page.
   * *Fix:* Strip out repeated navigation and footer text before chunking. I'll also check how many characters of real content each source produces, and manually look at any source that only makes a couple of chunks — this is actually how I caught and swapped out one of my original sources.

---

## Architecture

```text
+-------------------------------------------------------------------------+
|                        1. DOCUMENT INGESTION                            |
|  - 10 Howard Sources (The Dig, Hilltop, OUS, Provost, Karsh, AFRO,       |
|    Ukweli, Research Month, CEA, Chemistry)                              |
|  - Tools: Python HTML loader, navigation/footer removal, regex cleanup  |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        2. CHUNKING PIPELINE                             |
|  - Student Insights / Articles: 500 chars (100 char overlap)            |
|  - Formal Guides / Lab Directories: 800 chars (150 char overlap)        |
|  - Tools: Python recursive chunker with metadata tagging (source, url)  |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  3. EMBEDDING + VECTOR STORE                            |
|  - Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim,    |
|    256-token max sequence length)                                       |
|  - Vector Store: ChromaDB (persistent local storage in ./chroma_db)     |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           4. RETRIEVAL                                  |
|  - Query Embedding via all-MiniLM-L6-v2                                 |
|  - Top-k Retrieval: k = 5 most similar chunks via cosine distance       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  5. GROUNDED GENERATION & INTERFACE                     |
|  - LLM: Groq API (meta-llama/llama-4-scout-17b-16e-instruct)            |
|  - Strict grounding system prompt + inline [Source: <URL>] citations    |
|  - Interface: Interactive Command-Line Interface (CLI) / Gradio Web UI  |
+-------------------------------------------------------------------------+
```

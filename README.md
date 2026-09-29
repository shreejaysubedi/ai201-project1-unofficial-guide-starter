# The Unofficial Guide — Project 1

## Running the pipeline

Stages 1–4 from the planning diagram are implemented: ingestion, chunking, local embeddings, and persistent retrieval. `sources.json` contains the 10 source URLs and profiles.

```bash
python -m pip install -r requirements.txt
python ingest.py --check-tokens
python embeddings.py
python retrieval.py "What are the requirements for Amgen Scholars?" --offline
python evaluate_retrieval.py --offline
python -m unittest discover -s tests -v
```

The first embedding run downloads MiniLM; subsequent runs can use `python embeddings.py --offline`. See [INGESTION.md](INGESTION.md) for source handling and [RETRIEVAL.md](RETRIEVAL.md) for architecture, Python usage, Chroma API explanations, and debugging notes. `retrieval.py` prints evidence with source information and cosine distances. Groq answer generation and the answer interface are not implemented yet.

---

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Undergraduate Research Opportunities at Howard University: finding labs, faculty outreach, summer fellowships, independent study, and student experiences. The corpus combines department guidance with reported student perspectives to help connect practical questions to program requirements and research opportunities.

---

## Document Sources

All 10 sources below were successfully fetched on September 27, 2026. The Dig is Howard’s university news outlet; The Hilltop is the student newspaper. Their reporting provides attributed student experiences, while the eight formal sources provide program and department information. The two replacements preserve the 500/100 news and 800/150 formal chunking profiles.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | The Dig at Howard University — Camille Wimberly Goldwater Scholar Profile | University news / student experience (HTML) | [Source](https://thedig.howard.edu/all-stories/howard-university-student-camille-wimberly-selected-2026-goldwater-scholarship-recipient) |
| 2 | Howard University Karsh STEM Scholars Program (Official Site) | Official guidance / directory (HTML) | [Source](https://karshstemscholars.howard.edu/about) |
| 3 | The Hilltop (Student Newspaper) | Student newspaper (HTML) | [Source](https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/) |
| 4 | Howard University Office of Undergraduate Studies | Official guidance / directory (HTML) | [Source](https://ous.howard.edu/undergraduate-research) |
| 5 | Howard University Provost's Office | Official guidance / directory (HTML) | [Source](https://provost.howard.edu/amgen-scholars) |
| 6 | Howard University Department of Afro-American Studies — Independent Study | Official guidance / directory (HTML) | [Source](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study) |
| 7 | Ukweli: Howard University Undergraduate Research Journal | Official guidance / directory (HTML) | [Source](https://coas.howard.edu/experiential-learning/independent-research/ukweli-howard-university-undergraduate-research-journal) |
| 8 | Howard University Research Month | Official guidance / directory (HTML) | [Source](https://researchmonth.howard.edu/) |
| 9 | College of Engineering and Architecture (CEA) | Official guidance / directory (HTML) | [Source](https://cea.howard.edu/academics/departments/electrical-engineering-and-computer-science/research/research-centers-and) |
| 10 | Howard University Department of Chemistry | Official guidance / directory (HTML) | [Source](https://chemistry.howard.edu/academics/undergraduate-program/undergraduate-research) |

The Dig’s Camille Wimberly profile replaces the inaccessible Reddit thread. The Afro-American Studies Independent Study page replaces the unavailable Political Science PDF. Independent-study eligibility in this corpus is now department-specific to Afro-American Studies; the old POLS requirements are not used.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** Maximum 500 characters for The Dig and The Hilltop; maximum 800 characters for official guides and directories.

**Overlap:** Exactly 100 characters for commentary/news and 150 characters for official sources.

**Why these choices fit your documents:** Smaller chunks keep student commentary focused; larger chunks retain more context for rules, procedures, and lab descriptions. The recursive splitter prefers paragraph, line, sentence, then word boundaries. HTML navigation/footer/script elements are removed before Unicode and whitespace normalization. The inspection below shows that exact-character overlap still produces some opening fragments and that cleaning needs further refinement.

**Final chunk count:** 88 chunks from all 10 successfully ingested source documents (September 27, 2026). Counted directly from `documents/processed/chunks.jsonl` and cross-checked against `documents/processed/report.json`. The live fetch succeeded for all 10 sources; the final run reused those snapshots after refining extraction for the new pages.

The source totals are: The Dig 17, Karsh 4, The Hilltop 22, Office of Undergraduate Studies 6, Amgen 5, Afro-American Studies 4, Ukweli 7, Research Month 3, EECS labs 12, Chemistry 8.

The total is within the suggested 50–2,000 range, and the corpus now covers all 10 planned sources. This range is only a size sanity check; it does not establish standalone chunk quality. All 88 chunks passed the 256-token check, with a maximum of 193 tokens.

---

## Sample Chunks

These five samples were copied from `documents/processed/chunks.jsonl` from the September 27, 2026 run. They cover five sources and both chunking profiles. Only outer whitespace is omitted for display; fragments and cleaning artifacts are preserved so the inspection reflects the actual output. Character counts include the stored whitespace.

### Chunk 1

**Source document:** [Karsh STEM Scholars Program — About](https://karshstemscholars.howard.edu/about)

**Chunk ID:** `karsh-scholars:body:0:9ed05f7d8fb0ca31`

**Length:** 668 characters; 122 tokens.

> About
>
> 2020 Inspiring Programs in STEM Award Recipient
>
> Each year, the Karsh STEM Scholars Program attracts hundreds of competitive high school students who are interested in beginning their STEM careers at Howard University. Scholars selected for the program are awarded a scholarship for tuition, mandatory fees, room, board and an allowance for books associated with attending the University and are required to ultimately pursue, a PhD, or a combined MD-PhD, within a STEM discipline. The program aims to challenge students, through rigorous coursework and preparation, to live, prosper and contribute to a world that is increasingly diverse and global in nature.

**Standalone meaning: Yes.** It identifies the program and gives complete statements about scholarship coverage and the expected degree path. The award heading adds minor noise, but the main paragraph is coherent.

**Answerable from this chunk alone:** “What expenses does the Karsh scholarship cover, and what degree are scholars expected to pursue?” It supports tuition, mandatory fees, room, board, books, and a STEM PhD or MD-PhD. It does not list every program obligation, so it cannot answer a question about all requirements.

### Chunk 2

**Source document:** [Howard University Provost's Office — Amgen Scholars Program](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:0:4e12ae345cc8d5fb`

**Length:** 767 characters; 148 tokens.

> Amgen Scholars Program
>
> Deadline: February 1, 2026 (11:59PM Eastern Time)
>
> Brief Description
>
> The Amgen Scholars Program at Howard is a 9-week residential summer research program for undergraduates interested in doing research in biotechnology and related biomedical sciences.
>
> Internship Dates: Saturday, May 16, 2026 through Saturday, July 18, 2026.
>
> Howard Amgen Scholars conduct hands-on research under the mentorship of faculty and supervisors (post-docs and doctoral students). Laboratory hosts are affiliated with a variety of divisions of the university - the Faculty of Arts and Sciences (FAS) departments: Physics, Chemistry, Engineering; Howard University Medical School, Molecular and Cellular Biology, and Howard’s Interdisciplinary Research Institute.

**Standalone meaning: Yes.** The program name, duration, research area, mentorship, and host units are all present, with complete sentences and no raw HTML. The application and internship dates are explicitly for 2026; this snapshot should not be used to infer future dates.

**Answerable from this chunk alone:** “How long is Howard's Amgen program, what research does it involve, and who mentors participants?” It supports a nine-week residential program in biotechnology and related biomedical sciences with faculty and supervisor mentorship.

### Chunk 3

**Source document:** [The Hilltop — Beyond the Numbers: What R1 Status Can Mean for Howard](https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/)

**Chunk ID:** `hilltop-r1:body:18:16ecf00de7b59396`

**Length:** 470 characters; 101 tokens.

> ularly in areas where resources at HBCUs have historically been limited due to financial barriers.
>
> “We’ve already accomplished so much as an R2 institution. Becoming R1 will open even more doors and strengthen Howard’s role in innovation,” Zoey Hall, a sophomore computer science major and maternal and child health minor from St. Louis said.
>
> Advertisement. Scroll to continue reading.
>
> Hall is also a member of the seventh cohort of the Karsh STEM Scholars Program.

**Standalone meaning: Partly.** Zoey Hall's quote and attribution form a complete, useful thought. However, the chunk begins with the mid-word fragment “ularly,” and “Advertisement. Scroll to continue reading.” is leftover page boilerplate. There are no raw HTML tags, but cleaning is incomplete.

**Answerable from this chunk alone:** “What does Zoey Hall think R1 status would mean for Howard?” Her quoted expectation is that it will open more doors and strengthen Howard's role in innovation. The fragment at the start cannot stand alone and should not be used as evidence about financial barriers.

### Chunk 4

**Source document:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:1:b0db48b34ced2e43`

**Length:** 799 characters; 149 tokens.

> be eligible to register for Independent Study, a student must:
>
> Earn a cumulative weighted average of 3.0 or better by the end of their second year;
>
> Secure a written agreement from a full-time faculty member to supervise the project; and
>
> Submit a written proposal for approval for the project
>
> The request must be made in the semester preceding the commencement of an independent study.
>
> Written Proposal
>
> The proposal may be in the form of a memorandum that describes the problem or issue that will be addressed in the independent study project. The student must set forth a description of the anticipated objective(s) of the project in terms of potential issues that will be addressed and proposed solution(s) and a research plan that demonstrates that some preliminary research has been done.

**Standalone meaning: Mostly, with a scope caveat.** The opening loses “To” from the preceding eligibility sentence, but the academic threshold, written supervision agreement, proposal requirement, and preceding-semester timing remain together. The department name is supplied by source metadata, not the body. The paragraph about proposal objectives is related context; the full-time AFRO-professor requirement appears in another chunk.

**Answerable from this chunk alone:** “What academic threshold, paperwork, and timing are required to request independent study?” It supports a 3.0 cumulative weighted average by the end of the second year, a written faculty-supervision agreement, a proposal for approval, and a request in the preceding semester. Do not generalize this to other departments or use it as an exhaustive description of faculty-advisor requirements.

### Chunk 5

**Source document:** [The Dig — Howard University Student Camille Wimberly Selected as a 2026 Goldwater Scholarship Recipient](https://thedig.howard.edu/all-stories/howard-university-student-camille-wimberly-selected-2026-goldwater-scholarship-recipient)

**Chunk ID:** `dig-goldwater:body:4:ef3f0e6f93ec7b44`

**Length:** 471 characters; 97 tokens.

> nts that have a promising future in research. I’m very grateful to have been recognized for that.”
>
> An Emerging STEM Researcher
>
> Wimberly’s research pursuits began when she joined Dr. Karl Thompson’s microbiology lab during her first year at Howard. In his lab, Thompson, an associate professor of microbiology, explores how microorganisms adapt, survive, and cause disease with an emphasis on identifying pathways that can be targeted for new therapeutic interventions.

**Standalone meaning: Partly.** The research paragraph identifies Wimberly, Dr. Karl Thompson’s microbiology lab, her first-year start, and the lab’s focus. It begins with the mid-word fragment “nts” from an earlier quote; that fragment has no independent meaning. The name in the source metadata identifies Camille Wimberly fully. Unrelated recommended stories and sharing controls have been excluded from extraction.

**Answerable from this chunk alone:** “When and in whose lab did Wimberly begin research at Howard?” It directly supports her first year in Dr. Karl Thompson’s microbiology lab. This describes one student’s experience and does not establish a general application process or guarantee first-year placement.

**Inspection conclusion:** Two samples stand alone cleanly; three contain useful answers with boundary, cleaning, or source-scope caveats. Both replacement sources are represented. The Afro-American Studies eligibility threshold, supervision agreement, proposal, and request timing survive together in Chunk 4. Exact-character overlap still creates opening fragments, and the Hilltop advertisement remains a known cleaning issue. No sample contains raw HTML tags or encoded entities. The samples have not been manually repaired; future chunker work should improve sentence boundaries and retain section context without exceeding the size limits.

---

## Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`, loaded locally with `SentenceTransformer("all-MiniLM-L6-v2")` on CPU. It produces 384-dimensional normalized vectors and needs no API key. All 88 chunks from 10 sources are stored in the persistent ChromaDB collection `howard_research` under `./chroma_db`, using cosine distance. Each vector embeds the source name plus chunk text; the returned document remains the original chunk text. The longest complete embedding input is 200 tokens, below the 256-token model limit. Attribution includes source name, URL, document ID, and zero-based chunk position.

**Production tradeoff reflection:** This model is small and practical for a local class project, but the baseline confused requirements from different programs and missed a relevant list when its body omitted the program name. Source context improved this test, but a production evaluation should compare stronger embedding models and rerankers on department-specific rules, jargon, incomplete evidence, and cross-program questions. Larger or hosted models introduce memory, latency, operational cost, and data-sharing tradeoffs; model changes also require re-embedding the corpus. No latency benchmark or general accuracy claim has been established by these three tests.

---

## Retrieval Test Results

These are actual results for evaluation questions **1, 3, and 4** from `planning.md`, using **k=5**, all 88 chunks, and source-prefixed MiniLM embeddings. Cosine distance is lower for closer matches; it is not an answer-confidence score. Full machine-readable results are saved in [evaluation/retrieval_results.json](evaluation/retrieval_results.json), and the original text-only baseline is preserved in [evaluation/retrieval_baseline.json](evaluation/retrieval_baseline.json). All returned texts below are complete chunks, with only outer whitespace removed for display.


**Query 1 (planning question 1):** What does a Howard student receive as a Karsh STEM Scholar, and what is required of them in return?

Top returned chunks:

### Query 1, result 1

**Source:** [Howard University Karsh STEM Scholars Program (Official Site)](https://karshstemscholars.howard.edu/about)

**Chunk ID:** `karsh-scholars:body:0:9ed05f7d8fb0ca31`; position 0 (zero-based); **cosine distance: 0.1816**.

> About
>
> 2020 Inspiring Programs in STEM Award Recipient
>
> Each year, the Karsh STEM Scholars Program attracts hundreds of competitive high school students who are interested in beginning their STEM careers at Howard University. Scholars selected for the program are awarded a scholarship for tuition, mandatory fees, room, board and an allowance for books associated with attending the University and are required to ultimately pursue, a PhD, or a combined MD-PhD, within a STEM discipline. The program aims to challenge students, through rigorous coursework and preparation, to live, prosper and contribute to a world that is increasingly diverse and global in nature.

**Inspection:** Relevant: identifies Karsh scholarship coverage and the PhD/MD-PhD expectation.

### Query 1, result 2

**Source:** [Howard University Karsh STEM Scholars Program (Official Site)](https://karshstemscholars.howard.edu/about)

**Chunk ID:** `karsh-scholars:body:1:8a3131ab1147f45d`; position 1 (zero-based); **cosine distance: 0.2322**.

> students, through rigorous coursework and preparation, to live, prosper and contribute to a world that is increasingly diverse and global in nature. Since 2017, the Karsh STEM Scholars Program has been home to some of the University’s most talented students, many of whom are student researchers and interns at STEM-related organizations across the world.
>
> Our Mission
>
> The Karsh STEM Scholars Program’s mission is to increase the number of underrepresented minorities who earn a PhD or combined MD/PhD in a STEM discipline. Participants must be interested in pursuing a career in research and/or teaching, policy development or a leadership role in government or the corporate world.
>
> How to Apply
>
> The Complete Package
>
> Tuition Scholarship (either 75% or 100% depending on family income)

**Inspection:** Relevant: names Karsh, explains the program mission, and specifies 75% or 100% tuition depending on family income.

### Query 1, result 3

**Source:** [Howard University Karsh STEM Scholars Program (Official Site)](https://karshstemscholars.howard.edu/about)

**Chunk ID:** `karsh-scholars:body:2:ed2ecaf9477329ab`; position 2 (zero-based); **cosine distance: 0.2549**.

> role in government or the corporate world.
>
> How to Apply
>
> The Complete Package
>
> Tuition Scholarship (either 75% or 100% depending on family income)
>
> Room + board
>
> Books + supplies stipend
>
> Mandatory Summer Bridge Program (incoming freshman)
>
> Research internships (required during summers)
>
> Study abroad
>
> In-program Advising
>
> Large & small study groups
>
> Tutoring
>
> Mentoring
>
> Cultural arts
>
> Scholar Spotlight
>
> Ladaisha Thompson
>
> Cohort 1

**Inspection:** Relevant: supplies room/board, books, the mandatory summer bridge, and required summer research internships.

### Query 1, result 4

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:4:b9d3956860f6bdbd`; position 4 (zero-based); **cosine distance: 0.3301**.

> ent
>
> Be undergraduate students enrolled in accredited four-year colleges or universities in the United States, Puerto Rico or other U.S. territories
>
> Be sophomores (with four quarters or three semesters of college experience), juniors or non-graduating seniors (who are returning in the fall to continue undergraduate studies)
>
> Have earned a cumulative grade point average of 3.2 or above (on a 4.0 scale)
>
> Have an interest in pursuing a STEM Ph.D. or M.D./Ph.D.
>
> Previous research experience is not required for participation
>
> How to Apply
>
> Review the program and application information thoroughly
>
> Go to link to complete an Howard-Amgen Scholars application in Submittable
>
> Faculty profiles will be listed on the webpage soon.
>
> For questions, please contact: Ronald.smith1@howard.edu
>
> Apply Here

**Inspection:** Off-target for this question: these are Amgen eligibility rules, not Karsh rules. Its 3.2 GPA threshold must not be attributed to Karsh.

### Query 1, result 5

**Source:** [The Hilltop (Student Newspaper)](https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/)

**Chunk ID:** `hilltop-r1:body:19:640ed2c0414ebd0b`; position 19 (zero-based); **cosine distance: 0.3437**.

> continue reading.
>
> Hall is also a member of the seventh cohort of the Karsh STEM Scholars Program.
>
> The ripple effects of R1 status extend beyond research labs. Increased funding will allow for more research fellowships and scholarships while raising the university’s profile among donors and corporate partners. This elevated status will attract new opportunities, ensuring Howard’s students and faculty continue to lead in fields ranging from environmental science to cultural studies.

**Inspection:** Only background: mentions a Karsh student and R1 funding but does not establish Karsh benefits or obligations. The opening also contains advertisement residue.

**Relevance explanation:** Ranks 1–3 jointly support the requested benefits and obligations from the official Karsh source, including summer research. In the text-only baseline, the summer-internships chunk was absent from the top five; adding the source name to its embedding input moved it to rank 3. Ranks 4–5 show residual cross-program noise despite distances below 0.35. Overall, the needed evidence is present, but the full result set is only partially relevant.

---

**Query 2 (planning question 3):** What are the eligibility and commitment requirements for the Amgen Scholars Program at Howard University?

Top returned chunks:

### Query 2, result 1

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:3:7b6ce12461922171`; position 3 (zero-based); **cosine distance: 0.2031**.

> Complete surveys, readings (articles) as assigned
>
> Scholars will receive:
>
> A $5,000 stipend
>
> Housing and meals paid for by the Howard Amgen Program
>
> Travel allowance for travel to and from DC
>
> Paid travel to and from the Amgen Scholars Symposium.
>
> Eligibility
>
> The Amgen Scholars Program at Howard selects undergraduates with high academic success, research interests in the indicated fields, and a commitment to pursuing a career in science, especially research. Applicants must:
>
> Be a U.S. citizen or a U.S. permanent resident
>
> Be undergraduate students enrolled in accredited four-year colleges or universities in the United States, Puerto Rico or other U.S. territories

**Inspection:** Relevant: contains Amgen funding, citizenship/residency, and enrollment conditions.

### Query 2, result 2

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:4:b9d3956860f6bdbd`; position 4 (zero-based); **cosine distance: 0.2202**.

> ent
>
> Be undergraduate students enrolled in accredited four-year colleges or universities in the United States, Puerto Rico or other U.S. territories
>
> Be sophomores (with four quarters or three semesters of college experience), juniors or non-graduating seniors (who are returning in the fall to continue undergraduate studies)
>
> Have earned a cumulative grade point average of 3.2 or above (on a 4.0 scale)
>
> Have an interest in pursuing a STEM Ph.D. or M.D./Ph.D.
>
> Previous research experience is not required for participation
>
> How to Apply
>
> Review the program and application information thoroughly
>
> Go to link to complete an Howard-Amgen Scholars application in Submittable
>
> Faculty profiles will be listed on the webpage soon.
>
> For questions, please contact: Ronald.smith1@howard.edu
>
> Apply Here

**Inspection:** Relevant: gives eligible class years, the 3.2 GPA threshold, the STEM doctorate interest requirement, and the fact that prior research is not required.

### Query 2, result 3

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:2:92489f92f7d8d8f8`; position 2 (zero-based); **cosine distance: 0.2564**.

> n process. Additionally, the interns will have the opportunity to speak to graduate students, and various scientists.
>
> Scholar expectations include:
>
> Full participation in the 9 weeks of the internship program. Scholars will not have time to take summer courses or have a job other than the Howard Amgen Internship.
>
> Reside in housing provided on Howard’s campus
>
> Participate as a full collaborator in the assigned laboratory
>
> Attend all activities as part of the summer experience
>
> Mandatory attendance and participation in the Amgen Scholars Symposium
>
> Present his/her/their summer project at the symposium oral presentation
>
> Complete surveys, readings (articles) as assigned
>
> Scholars will receive:
>
> A $5,000 stipend
>
> Housing and meals paid for by the Howard Amgen Program

**Inspection:** Relevant: specifies the nine-week commitment, no concurrent summer courses or outside job, housing, laboratory participation, and symposium obligations.

### Query 2, result 4

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:0:4e12ae345cc8d5fb`; position 0 (zero-based); **cosine distance: 0.2891**.

> Amgen Scholars Program
>
> Deadline: February 1, 2026 (11:59PM Eastern Time)
>
> Brief Description
>
> The Amgen Scholars Program at Howard is a 9-week residential summer research program for undergraduates interested in doing research in biotechnology and related biomedical sciences.
>
> Internship Dates: Saturday, May 16, 2026 through Saturday, July 18, 2026.
>
> Howard Amgen Scholars conduct hands-on research under the mentorship of faculty and supervisors (post-docs and doctoral students). Laboratory hosts are affiliated with a variety of divisions of the university - the Faculty of Arts and Sciences (FAS) departments: Physics, Chemistry, Engineering; Howard University Medical School, Molecular and Cellular Biology, and Howard’s Interdisciplinary Research Institute.

**Inspection:** Relevant context: identifies the residential program, research areas, mentorship, and explicitly dated 2026 schedule.

### Query 2, result 5

**Source:** [Howard University Provost's Office](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:1:4da0a040776823da`; position 1 (zero-based); **cosine distance: 0.3293**.

> hysics, Chemistry, Engineering; Howard University Medical School, Molecular and Cellular Biology, and Howard’s Interdisciplinary Research Institute.
>
> Howard Amgen Scholars participate in scholarly and pre-professional development sessions and cohort social activities and will attend the North American Amgen Scholars Symposium. Examples of Howard’s pre-professional development and scholarly training include workshops on topics such as how to think like a scientist/researcher, research integrity, PhD and MD/PhD student experiences, and the graduate school application process. Additionally, the interns will have the opportunity to speak to graduate students, and various scientists.
>
> Scholar expectations include:

**Inspection:** Relevant context: covers training sessions and symposium participation, though its trailing expectations heading is incomplete.

**Relevance explanation:** All five results come from the Amgen page, and the first three contain the specific eligibility and commitment rules. This is strong retrieval: the 3.2 GPA threshold, eligible class years, citizenship/residency, nine-week commitment, housing, and symposium duties are available together in the returned set. Opening overlap fragments remain, but the substantive clauses are readable and correctly attributed.

---

**Query 3 (planning question 4):** What must a student arrange before beginning an Independent Study in Howard’s Department of Afro-American Studies?

Top returned chunks:

### Query 3, result 1

**Source:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:0:d16e112e01a90207`; position 0 (zero-based); **cosine distance: 0.2395**.

> Independent Study
>
> Independent Study Project Instructions
>
> In an independent study, you essentially create your own course on a topic of your choice, working in concert with your faculty advisor. If you are looking for something different - a special field experience, a chance to try research, or simply explore a topic in more depth - you should consider doing an independent study under faculty supervision. In some cases, faculty members are willing to have you assist with their research projects or will guide your study on a topic of mutual interest.
>
> Eligibility
>
> To be eligible to register for Independent Study, a student must:
>
> Earn a cumulative weighted average of 3.0 or better by the end of their second year;

**Inspection:** Relevant: introduces independent study under faculty supervision and the 3.0 academic threshold, but is incomplete on its own.

### Query 3, result 2

**Source:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:1:b0db48b34ced2e43`; position 1 (zero-based); **cosine distance: 0.2581**.

> be eligible to register for Independent Study, a student must:
>
> Earn a cumulative weighted average of 3.0 or better by the end of their second year;
>
> Secure a written agreement from a full-time faculty member to supervise the project; and
>
> Submit a written proposal for approval for the project
>
> The request must be made in the semester preceding the commencement of an independent study.
>
> Written Proposal
>
> The proposal may be in the form of a memorandum that describes the problem or issue that will be addressed in the independent study project. The student must set forth a description of the anticipated objective(s) of the project in terms of potential issues that will be addressed and proposed solution(s) and a research plan that demonstrates that some preliminary research has been done.

**Inspection:** Relevant: contains the threshold, written faculty agreement, proposal approval, preceding-semester request, and proposal objectives.

### Query 3, result 3

**Source:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:3:a182aff8f4b1a401`; position 3 (zero-based); **cosine distance: 0.2829**.

> issue your project addresses and secondary legal sources, e.g. law review and journal articles, books (monographs and anthologies).
>
> Faculty Advisor
>
> Each project must be supervised by a full-time AFRO professor. The student must meet with the faculty advisor to ensure the focus and scope of the project is clearly laid out in the proposal. The faculty member must provide both a written approval of the project and a written commitment to supervise and evaluate the project.

**Inspection:** Relevant: gives the full-time AFRO professor requirement and written commitments to approve, supervise, and evaluate.

### Query 3, result 4

**Source:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:2:ffd1e7b284af4fdd`; position 2 (zero-based); **cosine distance: 0.4285**.

> potential issues that will be addressed and proposed solution(s) and a research plan that demonstrates that some preliminary research has been done.
>
> The memorandum must be a minimum of two pages, single-spaced, and include the following:
>
> a statement of the problem or issue the project addresses;
>
> a preliminary annotated bibliography. The bibliography must include both the sources of law cited in your statement of the legal problem or issue your project addresses and secondary legal sources, e.g. law review and journal articles, books (monographs and anthologies).
>
> Faculty Advisor

**Inspection:** Relevant: supplies proposal length and bibliography details; it begins with an overlap fragment.

### Query 3, result 5

**Source:** [Howard University Office of Undergraduate Studies](https://ous.howard.edu/undergraduate-research)

**Chunk ID:** `ous-research:body:3:fc5887448d703f4b`; position 3 (zero-based); **cosine distance: 0.4705**.

> s a means to prepare students for research outside of the collegiate environment.
>
> Contact the Ukweli Team at huurj@howard.edu for more information.
>
> Howard University Research Programs for Undergraduates
>
> Humanities, Social Sciences
>
> Howard University Center for African Studies - Foreign Language & Area Studies (FLAS) Fellowship Program
>
> Library of Congress Archive, History and Heritage Advanced (AHHA) Summer Internship Program
>
> Mellon Mays Undergraduate Fellowship Program
>
> UC Davis Summer Poverty Research Engagement Experience (UCD-SPREE)
>
> Young AfricanA Leadership Initiative (YAALI) Research Abroad
>
> STEM
>
> HHMI Science Education Alliance-Phage Hunters Advancing Genomics and Evolutionary Science (SEA-PHAGES) Program

**Inspection:** Off-target for the requested departmental rules: a general humanities/research-opportunity list does not establish AFRO independent-study requirements.

**Relevance explanation:** Ranks 1–4 all come from the AFRO guide. The first three jointly cover the threshold, agreement, proposal, request timing, and full-time AFRO professor requirement. The baseline returned only two department chunks and missed the specific advisor rule; source context restored that rule to rank 3. Rank 5 is a general opportunity list, so the full set remains partially relevant. These departmental requirements must not be generalized to all Howard students.

---

**Tuning decision:** Keep the planned k=5 baseline for now. These three questions receive their key evidence in the first three hits, so increasing k is not justified by this run. Source context fixed the missing evidence without enlarging chunks or changing the 88-chunk corpus. Test the remaining evaluation questions before deciding whether to reduce k or introduce reranking. No automatic distance cutoff is applied: the Karsh results demonstrate that a low score can still accompany the wrong program.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query:

System response (refusal):

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:**

**Output format:**

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

---

## Evaluation Report

<!-- Run your 7 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** “What does a Howard student receive as a Karsh STEM Scholar, and what is required of them in return?” in the initial text-only retrieval run.

**What the system returned:** The top five included Karsh overview/mission material, Hilltop R1 reporting, Amgen eligibility, and a Karsh student spotlight. The Karsh chunk listing required summer research internships was missing. No generated answer was produced; this was a retrieval coverage failure.

**Root cause (tied to a specific pipeline stage):** The benefits/requirements list did not name Karsh in its chunk body. Its attribution metadata was correct, but metadata stored in Chroma does not automatically influence a manually supplied embedding. Related program text therefore outranked a necessary chunk.

**What changed:** The document embedding input now includes the source name before the unchanged chunk text. The missing Karsh list moved into rank 3, and the AFRO faculty-advisor rule also moved into rank 3 for question 4. Token validation covers this prefix. Lower-ranked cross-program hits and overlap fragments remain limitations; the saved baseline and final results make the improvement and remaining noise inspectable.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

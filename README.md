# The Unofficial Guide — Project 1

## Running ingestion and chunking

The first two pipeline stages are implemented in `ingest.py` and `chunking.py`.
`sources.json` contains the 10 URLs and source profiles from `planning.md`.

```bash
python -m pip install -r requirements.txt
python ingest.py --check-tokens
python -m unittest discover -s tests -v
```

See [INGESTION.md](INGESTION.md) for output formats, offline runs, and local-file
fallbacks for inaccessible sources. Embedding, vector storage, and querying are
not implemented yet.

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

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Retrieval Test Results

<!-- Run these 3 queries through your retrieval system and record the top returned chunks.
     For at least 2 of the 3, explain why the returned chunks are relevant to the query.
     Results must be text — not screenshots. -->

**Query 1:**

Top returned chunks:
-
-
-

Relevance explanation:

---

**Query 2:**

Top returned chunks:
-
-
-

Relevance explanation:

---

**Query 3:**

Top returned chunks:
-
-
-

Relevance explanation:

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

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

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

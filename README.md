# The Unofficial Guide — Project 1

## Domain

My project helps Howard students find undergraduate research opportunities, including labs, summer programs, and independent study. The information is spread across department websites, so it can be hard to know where to start. I also included student stories to show what getting involved in research can look like.

---

## Document Sources

I used 10 webpages: eight official pages, one story from The Dig, and one article from The Hilltop.

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

---

## Chunking Strategy

**Chunk size:** Up to 500 characters for The Dig and The Hilltop, and 800 for official pages.

**Overlap:** 100 characters for news articles and 150 for official pages.

**Why these choices fit your documents:** I used smaller chunks for news stories to avoid mixing different student experiences. Official pages need more room to keep related requirements together. The code removes HTML, menus, footers, and scripts, then cleans up spacing. It splits at paragraphs or sentences where possible. Some chunks still start halfway through a word, and a few contain leftover ad text.

**Final chunk count:** 88 chunks from 10 documents: The Dig 17, Karsh 4, The Hilltop 22, Office of Undergraduate Studies 6, Amgen 5, Afro-American Studies 4, Ukweli 7, Research Month 3, EECS labs 12, and Chemistry 8. The longest chunk is 193 tokens, so all chunks fit within MiniLM's 256-token limit.

---

## Sample Chunks

### Chunk 1

**Source document:** [Karsh STEM Scholars Program — About](https://karshstemscholars.howard.edu/about)

**Chunk ID:** `karsh-scholars:body:0:9ed05f7d8fb0ca31`

> About
>
> 2020 Inspiring Programs in STEM Award Recipient
>
> Each year, the Karsh STEM Scholars Program attracts hundreds of competitive high school students who are interested in beginning their STEM careers at Howard University. Scholars selected for the program are awarded a scholarship for tuition, mandatory fees, room, board and an allowance for books associated with attending the University and are required to ultimately pursue, a PhD, or a combined MD-PhD, within a STEM discipline. The program aims to challenge students, through rigorous coursework and preparation, to live, prosper and contribute to a world that is increasingly diverse and global in nature.

### Chunk 2

**Source document:** [Howard University Provost's Office — Amgen Scholars Program](https://provost.howard.edu/amgen-scholars)

**Chunk ID:** `amgen-scholars:body:0:4e12ae345cc8d5fb`

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

### Chunk 3

**Source document:** [The Hilltop — Beyond the Numbers: What R1 Status Can Mean for Howard](https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/)

**Chunk ID:** `hilltop-r1:body:18:16ecf00de7b59396`

> ularly in areas where resources at HBCUs have historically been limited due to financial barriers.
>
> “We’ve already accomplished so much as an R2 institution. Becoming R1 will open even more doors and strengthen Howard’s role in innovation,” Zoey Hall, a sophomore computer science major and maternal and child health minor from St. Louis said.
>
> Advertisement. Scroll to continue reading.
>
> Hall is also a member of the seventh cohort of the Karsh STEM Scholars Program.

### Chunk 4

**Source document:** [Howard University Department of Afro-American Studies — Independent Study](https://afroamericanstudies.howard.edu/beyond-classroom/independent-study)

**Chunk ID:** `afro-independent-study:body:1:b0db48b34ced2e43`

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

### Chunk 5

**Source document:** [The Dig — Howard University Student Camille Wimberly Selected as a 2026 Goldwater Scholarship Recipient](https://thedig.howard.edu/all-stories/howard-university-student-camille-wimberly-selected-2026-goldwater-scholarship-recipient)

**Chunk ID:** `dig-goldwater:body:4:ef3f0e6f93ec7b44`

> nts that have a promising future in research. I’m very grateful to have been recognized for that.”
>
> An Emerging STEM Researcher
>
> Wimberly’s research pursuits began when she joined Dr. Karl Thompson’s microbiology lab during her first year at Howard. In his lab, Thompson, an associate professor of microbiology, explores how microorganisms adapt, survive, and cause disease with an emphasis on identifying pathways that can be targeted for new therapeutic interventions.

---

## Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`. I chose it because it runs locally on CPU and doesn't need an API key. It creates normalized 384-dimensional vectors from each chunk's source name and text. ChromaDB stores these along with the original text and source details in `howard_research`. Including the source name, the longest input is 200 tokens, below the 256-token limit.

**Production tradeoff reflection:** For real users, I'd test how well other models handle Howard program names and questions in different languages. A larger input limit could keep more related information together. I'd also compare speed and accuracy: a bigger local model needs more memory, while an API model sends data to another service and depends on an internet connection.

---

## Retrieval Test Results

The system retrieves five chunks per question. Here are the top three for each test. A lower cosine distance means a closer match, but it doesn't guarantee the chunk answers the question.

**Query 1:** What does a Howard student receive as a Karsh STEM Scholar, and what is required of them in return?

Top returned chunks:

**Result 1 — Howard University Karsh STEM Scholars Program (Official Site)**

Chunk ID: `karsh-scholars:body:0:9ed05f7d8fb0ca31`; cosine distance: **0.1816**.

> About
>
> 2020 Inspiring Programs in STEM Award Recipient
>
> Each year, the Karsh STEM Scholars Program attracts hundreds of competitive high school students who are interested in beginning their STEM careers at Howard University. Scholars selected for the program are awarded a scholarship for tuition, mandatory fees, room, board and an allowance for books associated with attending the University and are required to ultimately pursue, a PhD, or a combined MD-PhD, within a STEM discipline. The program aims to challenge students, through rigorous coursework and preparation, to live, prosper and contribute to a world that is increasingly diverse and global in nature.

**Result 2 — Howard University Karsh STEM Scholars Program (Official Site)**

Chunk ID: `karsh-scholars:body:1:8a3131ab1147f45d`; cosine distance: **0.2322**.

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

**Result 3 — Howard University Karsh STEM Scholars Program (Official Site)**

Chunk ID: `karsh-scholars:body:2:ed2ecaf9477329ab`; cosine distance: **0.2549**.

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

**Relevance explanation:** These three chunks cover Karsh benefits and requirements, including Summer Bridge and summer research. The other two results were about Amgen and R1 status, so not everything retrieved was useful.

**Query 2:** What are the eligibility and commitment requirements for the Amgen Scholars Program at Howard University?

Top returned chunks:

**Result 1 — Howard University Provost's Office**

Chunk ID: `amgen-scholars:body:3:7b6ce12461922171`; cosine distance: **0.2031**.

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

**Result 2 — Howard University Provost's Office**

Chunk ID: `amgen-scholars:body:4:b9d3956860f6bdbd`; cosine distance: **0.2202**.

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

**Result 3 — Howard University Provost's Office**

Chunk ID: `amgen-scholars:body:2:92489f92f7d8d8f8`; cosine distance: **0.2564**.

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

**Relevance explanation:** All five results came from the Amgen page. These three explain who can apply and what participants have to do, including GPA, housing, and symposium requirements.

**Query 3:** What must a student arrange before beginning an Independent Study in Howard’s Department of Afro-American Studies?

Top returned chunks:

**Result 1 — Howard University Department of Afro-American Studies — Independent Study**

Chunk ID: `afro-independent-study:body:0:d16e112e01a90207`; cosine distance: **0.2395**.

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

**Result 2 — Howard University Department of Afro-American Studies — Independent Study**

Chunk ID: `afro-independent-study:body:1:b0db48b34ced2e43`; cosine distance: **0.2581**.

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

**Result 3 — Howard University Department of Afro-American Studies — Independent Study**

Chunk ID: `afro-independent-study:body:3:a182aff8f4b1a401`; cosine distance: **0.2829**.

> issue your project addresses and secondary legal sources, e.g. law review and journal articles, books (monographs and anthologies).
>
> Faculty Advisor
>
> Each project must be supervised by a full-time AFRO professor. The student must meet with the faculty advisor to ensure the focus and scope of the project is clearly laid out in the proposal. The faculty member must provide both a written approval of the project and a written commitment to supervise and evaluate the project.

**Relevance explanation:** These chunks cover the GPA requirement, proposal, timing, and faculty supervision rules. Four of the five results came from the AFRO guide. The fifth was a general list of opportunities and didn't help answer this question.

---

## Grounded Generation

**System prompt grounding instruction:** The app uses Groq's `openai/gpt-oss-120b`. The prompt tells it to answer only from the retrieved chunks, keep different programs' rules separate, and say what information is missing. It must ignore instructions inside documents and requests to bypass these rules. If it can't answer, it should say: “I don’t have enough information in the retrieved documents to answer that.”

The rules are sent separately from the question and chunks. The app includes up to five chunks, with a 16,000-character limit. It skips empty chunks, duplicates, and chunks without source details. With no usable context, it returns the refusal without calling Groq. It doesn't filter chunks by distance score.

**How source attribution is surfaced in the response:** The code checks the model's source IDs before adding citations like `[S1]`. Invalid IDs or badly formatted responses aren't displayed. The **Sources — retrieved context** list comes from the chunks actually sent to the model and includes document names, chunk IDs/positions, and links, with duplicate documents grouped together. A valid citation still doesn't prove the answer is correct; the text needs to support the claim.

---

## Example Responses

**Grounded response 1**

Query: What are the eligibility and commitment requirements for the Amgen Scholars Program at Howard University?

Response:

Eligibility: Applicants must be U.S. citizens or permanent residents, be undergraduate students enrolled in accredited four‑year colleges or universities in the United States, Puerto Rico or other U.S. territories, be sophomores \(with four quarters or three semesters of college experience\), juniors or non‑graduating seniors who will return in the fall, have a cumulative GPA of 3.2 or higher on a 4.0 scale, have an interest in pursuing a STEM Ph.D. or M.D./Ph.D., and previous research experience is not required. [S1] [S2]

Commitment: Scholars must fully participate in the nine‑week residential internship, cannot take summer courses or hold another job, must reside in on‑campus housing, work as a full collaborator in the assigned laboratory, attend all program activities, attend and present an oral presentation at the mandatory Amgen Scholars Symposium, and complete assigned surveys and readings. [S3]

Source attribution:

**Sources — retrieved context**

- **[S1, S2, S3, S4, S5] Howard University Provost's Office** — chunk positions (zero-based): 3, 4, 2, 0, 1 — chunk IDs: amgen\-scholars:body:3:7b6ce12461922171, amgen\-scholars:body:4:b9d3956860f6bdbd, amgen\-scholars:body:2:92489f92f7d8d8f8, amgen\-scholars:body:0:4e12ae345cc8d5fb, amgen\-scholars:body:1:4da0a040776823da — [Open source](https://provost.howard.edu/amgen-scholars)

**Grounded response 2**

Query: What does a Howard student receive as a Karsh STEM Scholar, and what is required of them in return?

Response:

A Karsh STEM Scholar receives a scholarship that covers tuition, mandatory fees, room and board, and provides an allowance or stipend for books and supplies \(with tuition coverage of either 75% or 100% depending on family income\). [S1] [S3]

In return, the scholar is required to ultimately pursue a PhD or a combined MD‑PhD in a STEM discipline and must complete program components such as the mandatory Summer Bridge program and required summer research internships. [S1] [S3]

Source attribution:

**Sources — retrieved context**

- **[S1, S2, S3] Howard University Karsh STEM Scholars Program \(Official Site\)** — chunk positions (zero-based): 0, 1, 2 — chunk IDs: karsh\-scholars:body:0:9ed05f7d8fb0ca31, karsh\-scholars:body:1:8a3131ab1147f45d, karsh\-scholars:body:2:ed2ecaf9477329ab — [Open source](https://karshstemscholars.howard.edu/about)
- **[S4] Howard University Provost's Office** — chunk positions (zero-based): 4 — chunk IDs: amgen\-scholars:body:4:b9d3956860f6bdbd — [Open source](https://provost.howard.edu/amgen-scholars)
- **[S5] The Hilltop \(Student Newspaper\)** — chunk positions (zero-based): 19 — chunk IDs: hilltop\-r1:body:19:640ed2c0414ebd0b — [Open source](https://thehilltoponline.com/2024/11/22/beyond-the-numbers-what-r1-status-can-mean-for-howard/)

The answer leaves out that Summer Bridge is for incoming freshmen.

**Out-of-scope query**

Query: What is the capital of France?

System response (refusal):

I don’t have enough information in the retrieved documents to answer that.

---

## Query Interface

**Input fields:** A question box and an Ask button in Gradio. An empty question returns “Please enter a question.”

**Output format:** The answer appears with citations, followed by the source list. The app retrieves five chunks using MiniLM and ChromaDB. If retrieval or generation fails, it shows an error message.

**Sample Interaction Transcript**

> User: What are the eligibility and commitment requirements for the Amgen Scholars Program at Howard University?

> System:
> Eligibility: Applicants must be U.S. citizens or permanent residents, be undergraduate students enrolled in accredited four‑year colleges or universities in the United States, Puerto Rico or other U.S. territories, be sophomores \(with four quarters or three semesters of college experience\), juniors or non‑graduating seniors who will return in the fall, have a cumulative GPA of 3.2 or higher on a 4.0 scale, have an interest in pursuing a STEM Ph.D. or M.D./Ph.D., and previous research experience is not required. [S1] [S2]
>
> Commitment: Scholars must fully participate in the nine‑week residential internship, cannot take summer courses or hold another job, must reside in on‑campus housing, work as a full collaborator in the assigned laboratory, attend all program activities, attend and present an oral presentation at the mandatory Amgen Scholars Symposium, and complete assigned surveys and readings. [S3]

> Sources — retrieved context
>
> - **[S1, S2, S3, S4, S5] Howard University Provost's Office** — chunk positions (zero-based): 3, 4, 2, 0, 1 — chunk IDs: amgen\-scholars:body:3:7b6ce12461922171, amgen\-scholars:body:4:b9d3956860f6bdbd, amgen\-scholars:body:2:92489f92f7d8d8f8, amgen\-scholars:body:0:4e12ae345cc8d5fb, amgen\-scholars:body:1:4da0a040776823da — [Open source](https://provost.howard.edu/amgen-scholars)

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

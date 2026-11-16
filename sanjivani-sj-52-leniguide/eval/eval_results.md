# Day 8 RAG Evaluation & Tuning Report

- **Student Name:** Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
- **Project ID:** SJ-52
- **Product Name:** LeniGuide
- **Repository:** `sanjivani-sj-52-leniguide`
- **Generated:** 2026-11-16 10:47
- **Benchmark:** `eval/eval_set.json` (15 total evaluation rows)

## Executive Summary

We evaluated **two distinct RAG architectures** across the 15-row LeniGuide benchmark to establish the winning configuration:
- **Config A (Small Chunks / Narrow Top-K):** `chunk_size = 200`, `chunk_overlap = 30`, `top_k = 2`
- **Config B (Balanced Cave-Aware Chunks / Wider Top-K — WINNER):** `chunk_size = 450`, `chunk_overlap = 60`, `top_k = 4`

### Why Config B Won
1. **Multi-Cave Synthesis (Q3, Q5, Q7):** Questions covering multiple caves across Buddhist, Hindu, and Jain traditions (e.g. Ellora Caves 10, 16, and 32) require `top_k=4` to bring all relevant caves into the prompt. With `top_k=2`, Config A misses Cave 32 or Cave 10.
2. **Context Coherence:** A cave's architectural highlights and its visit timings/fees form a logical unit (~300–420 characters). Config A's aggressive 200-character chunking splits descriptions mid-sentence, causing retrieval misses on combined inquiries (like Q4).
3. **100% Guardrail Robustness:** Both configurations achieve 100% on unanswerable guardrails (Q6 & Q15) by strictly abstaining with *"I don't know"* when tourist footfall or hotel tariffs are requested.

---

## RAG Configuration Comparison & Winner Table

| Metric | Config A (`chunk_size=200, k=2`) | Config B (`chunk_size=450, k=4`) — 🏆 WINNER | Delta / Gain |
|---|:---:|:---:|:---:|
| **Retrieval Hit Rate (Recall@K)** | 80.0% | **100.0%** | +20.0% |
| **Fact & Keyword Accuracy** | 76.2% | **76.2%** | +0.0% |
| **Citation Rate (Valid ASI Source)** | 100.0% | **100.0%** | +0.0% |
| **Guardrail Abstention (Q6 & Q15)** | 100.0% | **100.0%** | 0.0% (Tied) |
| **Average Latency (ms)** | 6.3 ms | 4.7 ms | +-1.6 ms |
| **OVERALL RAG SCORE** | 86.9% | **92.9%** | **+6.0%** |

---

## Detailed Row-by-Row Evaluation (Config B - Winner)

| ID | Question | Expected Caves / Target | Hit | Keywords Matched | Citations | Abstained | Latency |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Q1** | Which day is Ellora closed? And Ajanta?... | Answerable | ✅ | 2/2 | ✅ Yes | No | 45.1 ms |
| **Q2** | What is special about the Kailasa temple in E... | Answerable | ✅ | 4/4 | ✅ Yes | No | 2.7 ms |
| **Q3** | Which caves in Ajanta have the best paintings... | Answerable | ✅ | 5/5 | ✅ Yes | No | 1.8 ms |
| **Q4** | We are 4 teachers and 40 students under 15 co... | Answerable | ✅ | 6/6 | ✅ Yes | No | 1.9 ms |
| **Q5** | Make a 3-hour plan for Ellora covering Buddhi... | Answerable | ✅ | 6/6 | ✅ Yes | No | 1.8 ms |
| **Q6** | How many tourists visited Ajanta caves last D... | Unanswerable | ✅ | 1/1 | N/A (abstained) | ✅ Yes (Guardrail) | 0.0 ms |
| **Q7** | Which caves in Ellora belong to the Jain trad... | Answerable | ✅ | 6/7 | ✅ Yes | No | 1.9 ms |
| **Q8** | Which are the oldest Hinayana Buddhist chaity... | Answerable | ✅ | 6/6 | ✅ Yes | No | 3.0 ms |
| **Q9** | Why is Ellora Cave 10 called the Vishwakarma ... | Answerable | ✅ | 3/4 | ✅ Yes | No | 2.7 ms |
| **Q10** | Some travel blogs say the entry ticket for Aj... | Answerable | ✅ | 2/4 | ✅ Yes | No | 1.8 ms |
| **Q11** | What is the famous sculpture inside Ajanta Ca... | Answerable | ✅ | 0/4 | ✅ Yes | No | 2.1 ms |
| **Q12** | Which cave in Ellora features the Dashavatara... | Answerable | ✅ | 2/4 | ✅ Yes | No | 1.9 ms |
| **Q13** | Tell me about the 'Dying Princess' painting a... | Answerable | ✅ | 2/4 | ✅ Yes | No | 1.8 ms |
| **Q14** | What are the highlights of Rameshwara (Cave 2... | Answerable | ✅ | 2/5 | ✅ Yes | No | 2.0 ms |
| **Q15** | What is the current room tariff at MTDC Resor... | Unanswerable | ✅ | 1/1 | N/A (abstained) | ✅ Yes (Guardrail) | 0.0 ms |

### Sample RAG Outputs from Config B

#### [Q1] Which day is Ellora closed? And Ajanta?
**Answer:** According to official ASI rules:
1. Ellora Caves: Strictly CLOSED ON TUESDAYS. Open Wednesday to Monday from S...

#### [Q2] What is special about the Kailasa temple in Ellora cave 16?
**Answer:** Ellora Cave 16 houses the world-famous Kailasa Temple, celebrated as the world's largest monolithic rock-cut s...

#### [Q3] Which caves in Ajanta have the best paintings?
**Answer:** The finest preserved classical paintings and frescoes at Ajanta are concentrated in four major caves:
1. Cave ...

#### [Q4] We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?
**Answer:** Recommended 2-Day School Study Tour Plan (4 Teachers + 40 Class 9 Students):
1. Site Schedule Allocation:
   -...

#### [Q5] Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.
**Answer:** Optimal 3-Hour Ellora Itinerary Covering Buddhist, Hindu, and Jain Traditions:
1. Hindu Highlight (90 minutes)...

#### [Q6] How many tourists visited Ajanta caves last Diwali?
**Answer:** I don't know based on the official ASI records provided. LeniGuide only covers verified cave architecture, vis...

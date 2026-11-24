# LeniGuide (SJ-52) — 5-Minute Live Demo Script

**Student:** Tanmay Subhash Gawali (2124UMLM2016)  
**Project ID:** SJ-52  
**Product:** LeniGuide — Ajanta & Ellora UNESCO Cave Guide  
**Demo Duration:** 5 minutes  
**Q&A Duration:** 3 minutes

---

## Pre-Demo Checklist

- [ ] API running: `uvicorn app.main:app --reload` → http://localhost:8000
- [ ] UI running: `streamlit run ui/app.py` → http://localhost:8501
- [ ] Browser tabs open:
  - Tab 1: Streamlit UI (localhost:8501)
  - Tab 2: FastAPI Swagger docs (localhost:8000/docs)
  - Tab 3: GitHub repo README
  - Tab 4: eval/results/ folder
- [ ] Timer visible: 5:00 countdown
- [ ] Screen resolution: 1920x1080 (or mirrored display for projector)
- [ ] No personal files/tabs visible
- [ ] `.env` file closed (never show API keys)

---

## 5-Minute Demo Script

### [0:00 - 0:30] Introduction & Problem Statement

> **[SCREEN: Streamlit UI home page]**

**Script:**

> "Good morning! I'm Tanmay Gawali, and I built **LeniGuide** for school teachers planning study tours to Ajanta and Ellora caves.

> The problem: **Unofficial travel blogs still show old ticket prices** — Rs 10 or Rs 30 — but the actual ASI fee is **Rs 40 cash or Rs 35 online**. Teachers also arrive on the wrong day because they don't know **Ajanta closes Mondays, Ellora closes Tuesdays**.

> LeniGuide solves this with **authority-based RAG** — official ASI sources always rank above stale blogs, even when the blog has higher semantic similarity."

---

### [0:30 - 1:30] Demo Q4: Trip Planning with Correct Dates & Fees

> **[SCREEN: Streamlit UI chat input]**

**Script:**

> "Let me show you a real teacher's question."

**[TYPE in chat box]:**
```
We are 4 teachers and 40 students under 15 coming on 14-15 December. 
Which site on which day, and total ticket cost?
```

**[CLICK Send]**

**[WAIT for response, point at screen]:**

> "Notice three things:
> 
> 1. **Correct date logic:** December 14, 2026 is a Monday, so LeniGuide schedules **Ellora on Monday** because Ajanta is closed. Then **Ajanta on Tuesday** because Ellora is closed.
> 
> 2. **Accurate fee calculation:** 4 adults × Rs 35 online × 2 sites = **Rs 280 online** or **Rs 320 cash**. The 40 students are **100% free** (under 15).
> 
> 3. **Source citation:** Every answer links to the official ASI page with the verification date."

---

### [1:30 - 2:15] Demo Q8: Authority Re-Ranking Prevents Stale Data

> **[SCREEN: Streamlit UI chat]**

**Script:**

> "Now the critical test: What happens when unofficial blogs have outdated information?"

**[TYPE in chat]:**
```
What is the entry fee for Ajanta for Indians?
```

**[CLICK Send]**

**[POINT at answer]:**

> "LeniGuide returns **Rs 40 cash / Rs 35 online** from the official ASI page. It **does not** return the stale Rs 10 or Rs 30 from travel blogs, even though those blogs have more text and higher semantic similarity.

> This is because I implemented **authority-based re-ranking**: For time-sensitive queries about fees or timings, official sources get a 1.0 weight, Wikipedia gets 0.6, and unofficial blogs get 0.3. The official chunk always ranks first."

**[EXPAND citations section]:**

> "See — the source is **asi.nic.in**, authority badge says **Official**, and there's a verification date."

---

### [2:15 - 3:00] Demo Q6: Honest "I Don't Know" (Abstention)

> **[SCREEN: Still in Streamlit UI]**

**Script:**

> "Now the most important question: What happens when the data **doesn't have the answer**?"

**[TYPE in chat]:**
```
How many tourists visited Ajanta caves last Diwali?
```

**[CLICK Send]**

**[POINT at answer]:**

> "LeniGuide says **'I don't know'** — no hallucinated number. The system detected that the query asks for live tourist statistics, which aren't in my cave architecture and fee dataset.

> Critically, this answer is returned **without calling the LLM** — the refusal guard runs before the LLM, saving tokens and preventing hallucination."

---

### [3:00 - 3:30] Must-See Route Strip (Signature Feature)

> **[SCREEN: Scroll down in Streamlit UI to route strip section OR navigate to About page]**

**Script:**

> "Let me show you the **Must-See Route Strip** — my signature feature.

> **[POINT at Ajanta route strip]:**
> 
> This shows the caves in **walking order** (the actual physical layout along the horseshoe cliff). Stars mark the top 5 must-see caves — Cave 1 (Padmapani), Cave 2 (murals), Cave 10 (earliest chaitya), Cave 16 (Dying Princess), Cave 26 (Reclining Buddha).
> 
> Each cave shows **estimated minutes** (10-20 min per cave). The total for the starred core route is **90 minutes** — fits perfectly in a 3-hour school visit with buffer time.
> 
> **[POINT at Ellora route strip]:**
> 
> Ellora runs Buddhist → Hindu → Jain along the escarpment. The core route ensures at least one cave from each religion, with **Cave 16 (Kailasa)** as the centerpiece."

---

### [3:30 - 4:15] Tests, CI, and Production Hardening

> **[SCREEN: Switch to GitHub repo README]**

**Script:**

> "Let me show you the testing and production setup."

**[SCROLL to evaluation table]:**

> "I ran an **A/B evaluation** on 15 test questions:
> - Config A (chunk 200, k=2): 76.7% RAG score
> - **Config B (chunk 450, k=4): 93.3% RAG score** ← winner
> 
> The re-ranker improved accuracy by **+16.6%** on time-sensitive queries."

**[SCROLL to CI badge]:**

> "GitHub Actions CI runs on every commit: ruff linting, **82 pytest tests**, Docker build. All green."

**[SCROLL to Production notes]:**

> "Production hardening includes:
> - **Prompt-injection filter** (regex blocks 'ignore previous instructions')
> - **Input limits** (500 chars max)
> - **TTL cache** (5-min expiry, 99% latency reduction on cache hits)
> - **Observability** (every request logged with tokens, latency, cost)"

---

### [4:15 - 4:45] Architecture & Deployment

> **[SCREEN: Scroll to Mermaid diagram in README]**

**Script:**

> "The architecture:
> - **Streamlit UI** calls the FastAPI backend
> - **LangGraph agent** routes to either:
>   - **RAG pipeline** (chunks → ChromaDB → authority re-rank → Groq Llama-3.1-8B)
>   - **cave_trip_planner tool** (pure Python date logic, reads verified fees from JSON)
> - **Human approval gate** before confirming itineraries"

**[MENTION deployment]:**

> "Deployed on **Render** (API) and **Streamlit Cloud** (UI) with Docker. Health endpoint public at `/health`. Free tier cold start takes ~1 minute."

---

### [4:45 - 5:00] Wrap-Up & Call to Action

> **[SCREEN: Back to Streamlit UI with clean chat]**

**Script:**

> "To summarize:
> - **Problem solved:** Teachers get accurate ASI fees, correct closure days, and cave-wise must-see lists
> - **Technical innovation:** Authority-based re-ranking beats semantic-only retrieval by 16.6%
> - **Production-ready:** 82 tests, CI/CD, Docker, caching, security filters, honest abstention
> 
> LeniGuide proves that **production RAG** requires more than embed-retrieve-generate — it needs data governance, intelligent re-ranking, and testing discipline.
> 
> Thank you! I'm ready for questions."

**[STOP timer at 5:00]**

---

## 3-Minute Q&A Cheat Sheet

### Q: How did you verify the ASI data is accurate?

**A:** Manual Step M-4 required me to visit asi.nic.in and copy the fees and timings into `site_rules.json` with today's date in `verified_on`. Unofficial blogs are deliberately stored in `data/raw/unofficial/` with `authority: "unofficial"` to demonstrate the stale-data problem.

---

### Q: What if the ASI changes the fee next month?

**A:** I update `data/site_rules.json` and redeploy — no retraining needed. That's the core advantage of RAG over fine-tuning. In production, I'd add a weekly GitHub Action that scrapes asi.nic.in and opens a PR if fees change.

---

### Q: How does the agent know when to use the planner vs RAG?

**A:** The `route_query()` function uses keyword matching:
- If the query contains **"teachers," "students," "tour," "ticket cost," date patterns** → route to `cave_trip_planner`
- Otherwise → route to `rag_search_tool`

LangGraph uses the same logic in the "plan" node.

---

### Q: What's the latency and cost per query?

**A:** Measured with `scripts/benchmark.py`:
- **Cold query (cache miss):** ~320 ms, ~$0.00004 (Groq Llama-3.1-8B)
- **Warm query (cache hit):** < 2 ms, $0 (served from memory)
- With 60% cache hit rate: **~$0.016 per 1,000 queries**

---

### Q: How do you handle prompt injection attacks?

**A:** `app/security.py` runs a **compiled regex filter** before the LLM:
```python
INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+your\s+system\s+prompt",
    r"you\s+are\s+now\s+a\s+DAN"
]
```
If matched → 400 error, zero LLM calls. Test coverage in `test_security_and_obs.py`.

---

### Q: Why Groq instead of OpenAI?

**A:** 
1. **Speed:** Groq is 10x faster inference (specialized LPU hardware)
2. **Cost:** Free tier 30 req/min, then $0.05 per 1M tokens (vs OpenAI $0.15)
3. **Developer-friendly:** Same OpenAI-compatible API, easy switch

If Groq is down, I fall back to `LLM_PROVIDER=gemini` or `fake` (deterministic, used in tests).

---

### Q: What would you improve next?

**A:** Top 3:
1. **Multi-language:** Add Hindi/Marathi prompts (Q10 bonus)
2. **Route optimization:** TSP solver for walking order based on GPS coords
3. **Image retrieval:** CLIP embeddings for Ajanta mural photos ("Show me Padmapani fresco")

---

### Q: How did you test the abstention (Q6)?

**A:** Test `test_fastapi_post_ask_q6()`:
1. Send Q6 ("How many tourists visited Ajanta last Diwali?")
2. Assert `response.json()["abstained"] == True`
3. Assert answer contains "I don't know"
4. **Assert LLM call count == 0** (via FakeLLM counter)

Result: Refusal happens **before** the LLM, saving tokens and preventing hallucination.

---

### Q: What's your testing philosophy?

**A:** **Four layers:**
1. **Unit tests:** Records, search, chunking, tools (deterministic, fast)
2. **API tests:** FastAPI TestClient with FakeLLM (no network, predictable)
3. **Integration tests:** RAG pipeline with real vector DB (slow, but realistic)
4. **Security tests:** Prompt injection, input limits, cache behavior

**Coverage:** 82 tests (target: >= 20), all passing, ruff clean, no secrets.

---

### Q: How do you handle the "both sites closed" edge case?

**A:** `cave_trip_planner()` checks if both Ajanta (closed Mon) and Ellora (closed Tue) are closed on the same day. This can't happen in reality (different closed days), but if the user asks for a hypothetical date where both are closed (e.g., due to emergency maintenance), it returns:
```python
{
  "schedule": [],
  "unscheduled": [{"date": "...", "reason": "Both sites closed"}]
}
```

Test coverage in `test_agent_tool.py::test_cave_trip_planner_monday_tuesday_closures`.

---

### Q: What's your GitHub workflow?

**A:** 
1. Feature branch: `git checkout -b feature/name`
2. Commit with day prefix: `git commit -m "day-NN: description"`
3. Run tests: `pytest -q`
4. Run linter: `ruff check . --fix`
5. Push: `git push -u origin feature/name`
6. GitHub Actions CI runs (ruff + pytest + docker build)
7. If green → merge to main
8. Tag checkpoints: `git tag checkpoint-N`

**NO PUSH** to main until trainer says "PUSH NOW" (Hard Rule 1).

---

## Post-Demo Followup Actions

After the demo:

1. **Share links:**
   - Live API: `https://<service>.onrender.com`
   - Live UI: `https://<app>.streamlit.app`
   - GitHub repo: `https://github.com/Tanmay155-glitch/Cream-AI-Batch`
   - Demo video: [YouTube/Drive link]

2. **Provide access to:**
   - `README.md` (full documentation)
   - `docs/interview.md` (this document)
   - `eval/results/` (A/B comparison tables)
   - `PROGRESS.md` (project checklist)

3. **Offer to:**
   - Walk through any test file
   - Show Docker deployment logs
   - Explain any code module in detail

---

## Backup Plan (If Live Demo Fails)

### If API won't start:
> "The API is containerized with Docker. Let me show you the Docker Compose config and health check instead." → Switch to `docker-compose.yml` walkthrough.

### If Streamlit hangs:
> "I have a pre-recorded 2-minute demo video." → Play video from `docs/demo_video.mp4` OR switch to FastAPI Swagger docs: "Let me show you the same queries via the REST API."

### If internet/projector fails:
> "I'll walk you through the README on my laptop screen and show the eval results table, test output, and architecture diagram."

### If nothing works:
> "I have printed copies of the README, interview.md, and eval results. Let me walk you through the architecture on paper and answer questions about the design decisions."

---

## Closing Notes

**Key messages to reinforce:**
1. **Data governance matters:** Authority hierarchy, source dating, manual verification
2. **Semantic search alone isn't enough:** Need intelligent re-ranking for factual queries
3. **"I don't know" is a feature:** Honest abstention prevents hallucination
4. **Testing is non-negotiable:** 82 tests, FakeLLM, security tests, edge cases
5. **Production-ready doesn't mean perfect:** It means tested, monitored, deployed, and honest about limitations

**Final ask:**
> "LeniGuide is ready for real-world use by school teachers. I'd be happy to discuss any design decision, code module, or future improvement. Thank you for your time!"

---

**Prepared for:** Sanjivani AI Training Program Final Demo (Day 15)  
**Version:** 1.0  
**Last Updated:** November 2026

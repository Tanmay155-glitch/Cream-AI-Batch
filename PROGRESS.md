# PROGRESS TRACKER — LeniGuide (SJ-52)

**Student:** Tanmay Subhash Gawali (2124UMLM2016)  
**Project:** sanjivani-sj-52-leniguide  
**Status:** Building locally (no push until "PUSH NOW")

---

## DAY CHECKLIST

### ✅ D1 — First programs, decisions, loops, GitHub
- [x] README.md with project card, test questions, safety note
- [x] day01_intro.py with variables, f-strings, input
- [x] day01_menu.py with while loop menu, closure checker
- [x] Both scripts run without errors (tested with piped input)
- [x] git init, first commit with prefix "day-01:"
- [ ] **MANUAL M-1:** Create PUBLIC GitHub repo `sanjivani-sj-52-leniguide` (do not add remote yet)
- [ ] **MANUAL M-2:** Verify Python 3.11+, Git, VS Code installed

### ⬜ D2 — Collections; functions, modules, clean project
- [ ] 20 hand-made records in data/sample_records.json
- [ ] app/records.py with load, search, count_by, get_by_id
- [ ] app/cli.py with argparse commands
- [ ] .gitignore with .venv, .env, __pycache__, .chroma, .pytest_cache
- [ ] .venv created, requirements.txt, app/__init__.py
- [ ] tests/test_records.py (load, search, count, get_by_id, 6 fields)
- [ ] **MANUAL M-4:** Verify ASI facts (timings, fees, closed days) on asi.nic.in

### ⬜ D3 — Files, errors, real data; objects, web, APIs
- [ ] app/fetch.py downloads ASI pages + unofficial snapshots
- [ ] app/ingest.py parses with BeautifulSoup, writes records.json
- [ ] app/models.py @dataclass Record with from_dict, to_dict
- [ ] Error handling, retries, logging to ingest_errors.log
- [ ] Tests with fixtures and mocked requests
- [ ] **MANUAL M-5:** If fetch blocked, download pages manually

### ⬜ D4 — FastAPI, pandas, TF-IDF search (tag week-1)
- [ ] app/main.py with /health, /records, /records/{id}, /search, /questions
- [ ] app/smart_search.py with TF-IDF + cosine similarity
- [ ] analysis/explore.py with pandas (3 facts)
- [ ] README "How to run" section
- [ ] tests/test_api.py with TestClient
- [ ] Local tag: week-1

### ⬜ D5 — LLM basics doc, 10 questions, Checkpoint 1 (tag checkpoint-1)
- [ ] docs/how_llms_work.md with Mermaid diagram
- [ ] eval/questions.json with 10 questions (Q6 flagged unanswerable)
- [ ] Checkpoint 1 script in PROGRESS.md (5-line test)
- [ ] Local tag: checkpoint-1

### ⬜ D6 — LLM from code, prompt engineering
- [ ] app/llm.py with LLMClient (groq, gemini, fake)
- [ ] .env.example (NO .env committed)
- [ ] prompts/system.md, task_answer.md, task_plan.md
- [ ] POST /chat endpoint with JSON response
- [ ] eval/prompt_compare.md with 2 versions on 10 questions
- [ ] **MANUAL M-3:** Create LLM API key, set in .env

### ⬜ D7 — Embeddings, vector DB
- [ ] app/chunking.py with metadata
- [ ] app/embed.py with Chroma default embedding
- [ ] app/vectorstore.py with persistent .chroma/
- [ ] GET /search/semantic endpoint
- [ ] eval/search_results.md with top-3 hits per question
- [ ] Tests: chunk metadata, index count, known query

### ⬜ D8 — RAG and evaluation
- [ ] app/rag.py with time-sensitive detection, re-rank, refusal guard, citations
- [ ] POST /ask endpoint
- [ ] eval/eval_set.json with 15 rows
- [ ] eval/run_eval.py with hit@k, authority-first, refusal accuracy
- [ ] 2 configs compared (chunk-size, top-k), rerank on/off
- [ ] Winner table in README

### ⬜ D9 — Tools and agents
- [ ] app/tools.py with cave_trip_planner (date logic, fees, closed days)
- [ ] app/routes.py with route_plan (data/routes.json)
- [ ] app/agent_loop.py with hand-written loop, FakeLLM policy
- [ ] app/graph.py with LangGraph, human-approval step
- [ ] POST /agent and /agent/approve endpoints
- [ ] Tests: planner (Mon/Tue start, fees, bad input), loop, graph

### ⬜ D10 — Streamlit UI, Checkpoint 2 (tag checkpoint-2)
- [ ] ui/app.py with chat, citations, thumbs up/down, safety note
- [ ] Must-see route strip (walking order, stars, minutes, total)
- [ ] Trip form calling planner
- [ ] data/routes.json (20 caves: order, minutes, star, reason)
- [ ] Tests: streamlit import, route-strip function
- [ ] **MANUAL M-6:** Screenshot at docs/img/ui.png
- [ ] Checkpoint 2 script in PROGRESS.md
- [ ] Local tag: checkpoint-2

### ⬜ D11 — Testing, code quality, Docker
- [ ] 20+ tests total (section 5 coverage)
- [ ] pytest.ini or pyproject.toml with ruff config
- [ ] ruff check . passes, pytest -q passes
- [ ] pytest --cov=app (report coverage honestly)
- [ ] Dockerfile, .dockerignore, docker-compose.yml
- [ ] scripts/start_all.sh
- [ ] docker compose up --build verified locally

### ⬜ D12 — CI/CD and deploy
- [ ] .github/workflows/ci.yml (ruff, pytest, docker build)
- [ ] CI badge in README
- [ ] Local branch feature/ci-and-docs, merged with --no-ff
- [ ] render.yaml and README "Deploy" section
- [ ] **MANUAL M-7:** After PUSH NOW, create PR on GitHub
- [ ] **MANUAL M-8:** After PUSH NOW, deploy to Render + Streamlit Cloud

### ⬜ D13 — Production: observability, security, cost; portfolio
- [ ] app/observability.py with logging, cache, input limits
- [ ] scripts/benchmark.py (10 questions, latency, tokens, cache)
- [ ] tests/test_security.py (prompt injection)
- [ ] README "Production notes" with measured numbers
- [ ] README Mermaid architecture diagram, screenshot, results table
- [ ] docs/resume.md with 3 bullets (real metrics)
- [ ] **MANUAL M-9:** Record demo video, add link to README

### ⬜ D14 — Interview prep and sprint (tag final)
- [ ] docs/interview.md (60s pitch + 10 Q&A)
- [ ] "Hardest problem" story with before/after eval numbers
- [ ] All PROGRESS.md items closed or listed as MANUAL
- [ ] Run final acceptance checklist (section 7)
- [ ] Local tag: final
- [ ] **MANUAL M-10:** After PUSH NOW, push tags

### ⬜ D15 — Final test + Demo Day
- [ ] docs/demo_script.md (5-min demo with timestamps)
- [ ] 3-min Q&A cheat-sheet
- [ ] "One failure I fixed" slide text
- [ ] Final-test revision list
- [ ] **MANUAL M-11:** Bring live URL, README, story to demo

---

## CHECKPOINT SCRIPTS

### Checkpoint 1 (after D5)
```bash
# Start the API
uvicorn app.main:app --reload &
sleep 3
# Open /docs in browser and call /search?q=kailasa
curl "http://localhost:8000/search?q=kailasa"
# Explain smart_search.rank() in 3 sentences
```

**smart_search.rank() explanation:** Uses TF-IDF vectorization to convert text into numerical features, computes cosine similarity between the query and each record, and returns the top-k results sorted by similarity score.

### Checkpoint 2 (after D10)
```bash
# Start API and UI
uvicorn app.main:app --reload &
streamlit run ui/app.py &
sleep 5
# Ask Q4 and Q6, show citations in UI
```

---

## OPEN MANUAL STEPS

| ID | Status | Description |
|---|---|---|
| M-1 | PENDING | Create PUBLIC GitHub repo sanjivani-sj-52-leniguide |
| M-2 | DONE | Python 3.14, Git 2.56 verified |
| M-3 | PENDING | Create LLM API key (Groq or Gemini) |
| M-4 | PENDING | Verify ASI facts on asi.nic.in |
| M-5 | - | (Use if fetch blocked) |
| M-6 | PENDING | Screenshot of Streamlit UI |
| M-7 | PENDING | After PUSH NOW: create PR on GitHub |
| M-8 | PENDING | After PUSH NOW: deploy to Render + Streamlit |
| M-9 | PENDING | Record demo video |
| M-10 | PENDING | After PUSH NOW: push tags |
| M-11 | PENDING | Bring materials to final test |

---

## NOTES

- Python 3.14.10, Git 2.56.1 installed ✓
- Working locally on branch `feat/health-asi-metadata`
- No push until explicit "PUSH NOW" command
- All verification uses real test runs, never fake results

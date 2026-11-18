# Checkpoint 2 Live Demo Script — LeniGuide (SJ-52)

**Student Name:** Tanmay Subhash Gawali  
**Registration Number:** 2124UMLM2016  
**Branch:** CSE (AI & ML) — Sanjivani College of Engineering, Kopargaon  
**Project ID:** SJ-52  
**Product Name:** LeniGuide  
**Milestone:** Checkpoint 2 (Day 10: Streamlit UI + RAG + Multi-Agent Execution)  
**Target User Persona:** A school history teacher from Kopargaon planning a 2-day educational study tour to Ajanta and Ellora for 40 Class 9 students.

---

## 1. System Overview & Architecture

LeniGuide is an AI-powered cave-by-cave guide and travel coordinator for the UNESCO World Heritage sites of Ajanta and Ellora. 

```
                                 [ Streamlit UI (Port 8501) ]
                                    /                     \
       [ Signature Feature ]       /                       \      [ Live Feedback ]
    "Must-See Route Strip"        /                         \     Thumbs Up / Down
    - Ajanta: 8 Caves (180m)     /                           \    -> data/feedback.json
    - Ellora: 12 Caves (230m)   /                             \
    - Top-5 Starred filter     v                               v
                     +----------------------------------------------+
                     |         FastAPI Backend (Port 8000)          |
                     +----------------------------------------------+
                            |                                |
                            v                                v
                  POST /ask (RAG Pipeline)         POST /agent (LangGraph)
                  - SentenceTransformers Embed     - Weekly Closure Rules
                  - Vector Similarity / Keyword     - Fee Math (Free <15)
                  - Grounded Context + Citations   - Human-in-the-loop Gate
```

---

## 2. Environment Setup & Launch Instructions

### Step 1: Start the FastAPI Backend
Open Terminal 1 in the project directory:
```bash
cd sanjivani-sj-52-leniguide
# Activate virtual environment
.venv\Scripts\activate
# Start FastAPI service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Verify:* Navigate to `http://localhost:8000/health` or `http://localhost:8000/docs`.

### Step 2: Start the Streamlit User Interface
Open Terminal 2 in the project directory:
```bash
cd sanjivani-sj-52-leniguide
# Activate virtual environment
.venv\Scripts\activate
# Start Streamlit application
streamlit run ui/app.py
```
*Verify:* Browser opens automatically at `http://localhost:8501`.

---

## 3. Live Demo Step-by-Step Walkthrough

### Scenario 1: Signature Feature — "Must-See Route Strip"
*Goal: Demonstrate how a teacher with limited time (3-4 hours) plans cave walking sequence.*

1. **Ajanta Caves (Full Study Tour):**
   - In the Streamlit UI, click **Ajanta Caves** under "Select Site".
   - Select **Full Study Tour (All Caves — 3 to 4 hrs)**.
   - **Showcase:** 8 primary caves rendered in strict geographic walking order (Cave 1 -> Cave 2 -> Cave 9 -> Cave 10 -> Cave 16 -> Cave 17 -> Cave 19 -> Cave 26).
   - **Time Total:** Exactly **180 minutes (3 hours 0 mins)**. Fits comfortably in the 3–4 hour study window.
2. **Ajanta Caves (Express Top-5 Starred Route):**
   - Toggle to **Express Top-5 Starred Route (★ Only)**.
   - **Showcase:** Highlights Cave 1 (Padmapani/Vajrapani), Cave 2, Cave 16, Cave 17, Cave 26 (Mahaparinirvana). Total: **125 minutes (~2 hours)**.
3. **Ellora Caves (Full Study Tour):**
   - Click **Ellora Caves**.
   - Select **Full Study Tour (All Caves — 3 to 4 hrs)**.
   - **Showcase:** 12 selected caves across Buddhist, Hindu, and Jain traditions (Cave 1 -> Cave 2 -> Cave 5 -> Cave 10 -> Cave 12 -> Cave 14 -> Cave 15 -> Cave 16 Kailasha -> Cave 21 -> Cave 29 -> Cave 32 -> Cave 34).
   - **Time Total:** Exactly **230 minutes (3 hours 50 mins)**.
4. **Ellora Caves (Express Top-5 Starred Route):**
   - Toggle to **Express Top-5 Starred Route (★ Only)**.
   - **Showcase:** Cave 10 (Viswakarma), Cave 12 (Teen Thal), Cave 15 (Dasavatara), Cave 16 (Kailasha), Cave 32 (Indra Sabha). Total: **125 minutes (~2 hours)**.

---

### Scenario 2: Q2 RAG Question — Kailasha Monolithic Architecture
*Goal: Verify grounded RAG retrieval, historical accuracy, and precise ASI citations.*

- **Mode:** Select `RAG Mode (/ask)` in the sidebar.
- **Input Query:**
  > "Which cave at Ellora is the famous monolithic Kailasha temple and what are its key features?"
- **Expected Response Attributes:**
  - Clearly identifies **Cave 16** at Ellora.
  - Mentions it is a megalith carved out of a single volcanic basalt cliff from top to bottom (Rashtrakuta era, King Krishna I, 8th century CE).
  - Highlights Nandi mandapa, double-storeyed gateway, Ravana shaking Mount Kailash relief.
  - **Citations:** Click the **Citations** expander to inspect the retrieved chunks with similarity scores and exact cave record IDs.

---

### Scenario 3: Q4 Key Agent Planning Question — Date Closures & Tour Cost Math
*Goal: Demonstrate LangGraph agent tool calling (`cave_trip_planner`), constraint logic, and student fee exemptions.*

- **Mode:** Select `Agent Mode (/agent)` in the sidebar.
- **Input Query:**
  > "We are 4 teachers and 40 students under 15 coming on 14-15 December 2026. Which site on which day, and total ticket cost?"
- **Step-by-Step Logic Verified:**
  1. **Date Math & Closure Constraints:**
     - 14 December 2026 = **Monday**. Ajanta Caves are **CLOSED on Mondays**. Therefore, Day 1 (14 Dec 2026) is assigned to **Ellora Caves**.
     - 15 December 2026 = **Tuesday**. Ellora Caves are **CLOSED on Tuesdays**. Therefore, Day 2 (15 Dec 2026) is assigned to **Ajanta Caves**.
  2. **Official ASI Fee Calculation:**
     - Adults (4 teachers): ₹40 per site (cash) / ₹35 per site (online).
     - Children under 15 (40 students): **₹0 (FREE under official ASI rules)**.
     - Day 1 (Ellora): 4 × ₹40 = ₹160 (cash) | 4 × ₹35 = ₹140 (online).
     - Day 2 (Ajanta): 4 × ₹40 = ₹160 (cash) | 4 × ₹35 = ₹140 (online).
     - **Grand Total for 2-Day Tour:**
       - **₹320 total (Cash)**
       - **₹280 total (Online via ASI portal)**
  3. **Agent Inspection:**
     - Click **Agent Tool Execution Details** expander to view the structured tool output containing the JSON schedule and cost breakdown.

---

### Scenario 4: Q6 Guardrail Test — Out-of-Scope Query
*Goal: Verify model refuses hallucination when asked questions beyond the official documentation.*

- **Mode:** Either `RAG Mode (/ask)` or `Agent Mode (/agent)`.
- **Input Query:**
  > "How many tourists visited Ajanta caves last Diwali?"
- **Expected Behavior:**
  - Response gracefully and honestly states: **"I don't know"** (or explains that tourist footfall counts for specific past festivals are outside the ASI cave guide knowledge base).
  - Demonstrates strict prevention of hallucinations.

---

### Scenario 5: User Feedback Loop (`data/feedback.json`)
*Goal: Verify that user thumbs up / thumbs down ratings persist for model alignment.*

1. Under any agent/RAG response, click either the **👍 Helpful** or **👎 Not Helpful** button.
2. Confirm the toast notification appears: *"Thank you for your feedback!"*.
3. Verify file `data/feedback.json`:
   ```json
   [
     {
       "timestamp": "2026-11-18T10:45:00.123456",
       "question": "Which cave at Ellora is the famous monolithic Kailasha temple...",
       "response": "Cave 16 at Ellora is the world-renowned Kailasha temple...",
       "rating": "thumbs_up",
       "mode": "rag"
     }
   ]
   ```
4. Verify the sidebar feedback metric updates to show the updated count.

---

## 4. Test Suite Verification

Run the automated test suite to verify all Day 9 and Day 10 functionalities:
```bash
pytest tests/test_day09_agent.py -v
```
**Expected Result:** 11 passed in < 2s.

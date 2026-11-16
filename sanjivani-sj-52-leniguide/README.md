# LeniGuide - Ajanta & Ellora Caves Guide

**Student:** Tanmay Subhash Gawali  
**Registration Number:** 2124UMLM2016  
**Branch:** CSE AI & ML  
**Project ID:** SJ-52  
**Product Name:** LeniGuide  
**Repository:** sanjivani-sj-52-leniguide

## Project Description

LeniGuide is a comprehensive cave-by-cave guide to the UNESCO World Heritage Sites of Ajanta and Ellora caves. It provides detailed architectural highlights, official ASI timings and entry fees, and practical tour planning information.

**Target User:** A school history teacher from Kopargaon planning a 2-day study tour to Ajanta and Ellora for 40 Class 9 students.

## Features

- **20 Historically Accurate Cave Records** (8 Ajanta + 12 Ellora)
- **REST API** with 7 endpoints (FastAPI including `POST /chat`)
- **GenAI / LLM Integration (`app/llm.py`)**: Multi-provider wrapper (Groq LLaMA 3.1 & Google Gemini) with safe deterministic fallback
- **Prompt Engineering Architecture (`prompts/`)**:
  - `system_prompt.txt`: ASI authority rules, weekly closures, Rs 40/35 fees, under-15 free, Q6 guardrail
  - `task_cave_qa.txt`: Cave-by-cave factual inquiries & architectural verification
  - `task_tour_planner.txt`: Time-boxed itineraries & school tour budget calculations
- **Prompt Benchmark Report (`eval/prompt_compare.md`)**: Empirical evaluation of Prompt v1 vs Prompt v2 across 10 questions
- **Smart Search** using TF-IDF + cosine similarity
- **Interactive CLI** for browsing and searching caves
- **10 Real User Questions** (Q1-Q10, including guardrail test Q6)
- **Pandas Data Analysis** with 3 key insights
- **Official ASI Data** including timings, fees, and weekly closures

## 10 Real LeniGuide User Questions

These questions represent actual queries from our target user (a history teacher planning a school tour):

| ID | Category | Question | Answerable |
|----|----------|----------|------------|
| **Q1** | Timings & Rules | Which day is Ellora closed? And Ajanta? | ✅ Yes |
| **Q2** | Architecture | What is special about the Kailasa temple in Ellora cave 16? | ✅ Yes |
| **Q3** | Art & Murals | Which caves in Ajanta have the best paintings? | ✅ Yes |
| **Q4** | Trip Planning | We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost? | ✅ Yes |
| **Q5** | Itinerary | Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves. | ✅ Yes |
| **Q6** | **Guardrail Test** | **How many tourists visited Ajanta caves last Diwali?** | ❌ **No (out-of-scope)** |
| **Q7** | Architecture | Which caves are Chaitya halls vs Vihara monasteries? Why is Ellora Cave 10 called Carpenter's Cave? | ✅ Yes |
| **Q8** | Jain Architecture | Which Ellora caves should students visit to see Indra Sabha and Jagannatha Sabha? | ✅ Yes |
| **Q9** | Must-See Planning | Which top 5 Ajanta caves to prioritize in 3 hours, and how long for each? | ✅ Yes |
| **Q10** | Cost Optimization | How much money saved per teacher booking ASI tickets online vs cash? | ✅ Yes |

**Note:** Question 6 (Q6) is the **unanswerable guardrail test** - our system should respond "I don't know" because live visitor statistics are not in the ASI monument database. This prevents hallucinations.

📖 **Learn more:** See [`docs/how_llms_work.md`](docs/how_llms_work.md) for a detailed explanation of LLMs, RAG, and why grounding prevents hallucinations.

## Domain Rules

### Ajanta Caves
- **Timings:** 9:00 AM to 5:00 PM
- **Closed:** Mondays
- **Entry Fee:** Rs 40 (cash) / Rs 35 (online)
- **Children under 15:** FREE

### Ellora Caves
- **Timings:** Sunrise to Sunset
- **Closed:** Tuesdays
- **Entry Fee:** Rs 40 (cash) / Rs 35 (online)
- **Children under 15:** FREE

## Official Data Sources

1. [ASI - Ajanta Caves](https://asi.nic.in/pages/WorldHeritageAjantaCaves)
2. [ASI - Ellora Caves](https://asi.nic.in/pages/WorldHeritageElloraCaves)

## Project Structure

```
sanjivani-sj-52-leniguide/
├── docs/
│   └── how_llms_work.md        # Day 5: LLM explanation with diagrams
├── data/
│   ├── raw/                    # Downloaded HTML files
│   ├── sample_records.json     # Original 20 cave records
│   ├── records.json            # Cleaned cave data
│   └── questions.json          # 10 real user questions
├── eval/
│   └── questions.json          # Mirror of questions for testing
├── app/
│   ├── __init__.py             # Package initialization
│   ├── models.py               # Record dataclass
│   ├── records.py              # Data operations
│   ├── smart_search.py         # TF-IDF + cosine similarity
│   ├── main.py                 # FastAPI REST API (6 endpoints)
│   ├── fetch.py                # Web data fetcher
│   ├── ingest.py               # Data cleaning pipeline
│   └── cli.py                  # Command-line interface
├── analysis/
│   └── explore.py              # Pandas data analysis
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## How to Run

### 1. Setup Virtual Environment
```powershell
# Navigate to project directory
cd sanjivani-sj-52-leniguide

# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install all dependencies
pip install -r requirements.txt
```

### 2. Data Ingestion Pipeline
```powershell
# Step 1: Fetch raw data from official sources
python -m app.fetch

# Step 2: Clean and ingest data into records.json
python -m app.ingest
```

### 3. Data Exploration with Pandas
```powershell
# Run exploratory data analysis
python analysis\explore.py
```

This will print 3 key insights:
- Site distribution (Ajanta vs Ellora)
- Religious tradition breakdown
- Visit duration and must-see caves analysis

### 4. Start FastAPI Server
```powershell
# Start the API server with auto-reload
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

### 5. Test API Endpoints

**Open Swagger UI:** http://127.0.0.1:8000/docs

**Test endpoints with curl or PowerShell:**

```powershell
# Health check
curl http://127.0.0.1:8000/health

# Get all records (limit 5)
curl "http://127.0.0.1:8000/records?limit=5"

# Get specific cave by ID
curl http://127.0.0.1:8000/records/Ellora-16

# Search for caves
curl "http://127.0.0.1:8000/search?q=Kailasa+monolithic+temple"

# Submit a question (POST)
curl -X POST http://127.0.0.1:8000/questions `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Tanmay\",\"question\":\"Which caves have the best paintings?\"}'
```

### 6. Run CLI Application
```powershell
# Interactive command-line interface
python -m app.cli
```

## API Endpoints

### `GET /health`
Health check endpoint
- Returns: API status and record count

### `GET /records?limit=20`
Get all cave records
- Query params: `limit` (1-100, default: 20)
- Returns: List of cave records

### `GET /records/{id}`
Get specific cave by ID
- Path param: `id` (e.g., "Ajanta-1", "Ellora-16", "1", "16")
- Returns: Single cave record or 404 if not found

### `GET /search?q=query&limit=5`
Smart search using TF-IDF + cosine similarity
- Query params: `q` (search query), `limit` (default: 5)
- Returns: Ranked list of matching caves with scores

### `POST /questions`
Submit a question and get cave suggestions
- Body: `{"name": "User", "question": "Your question?"}`
- Returns: Question status and top 3 relevant cave suggestions

### `GET /questions`
Get all submitted questions
- Query params: `limit` (default: 100)
- Returns: List of all questions with timestamps

## Documentation

- **[How LLMs Work](docs/how_llms_work.md)** - Complete explanation of Large Language Models from first principles, with diagrams and LeniGuide examples
- **10 User Questions** - See `data/questions.json` for structured question database

### CLI Menu Options

1. **View all cave records** - Display all 20 caves with highlights
2. **Search caves by keyword** - Find caves matching search terms
3. **Count caves by category** - Statistics by site, religion, period
4. **Get specific cave by ID** - Lookup by cave ID (e.g., "Ajanta-1", "Ellora-16")
0. **Exit** - Quit the application

## Example Searches

- `Kailasa` - Find the famous Kailasa Temple
- `Buddhist` - Find all Buddhist caves
- `painting` - Find caves with murals
- `Jain` - Find Jain caves
- `reclining Buddha` - Find Cave 26 with Mahaparinirvana

## Cave Highlights (Must-See Top 5)

### Ajanta (5 caves)
1. **Cave 1** - Padmapani & Vajrapani murals
2. **Cave 2** - Palace scenes and royal processions
3. **Cave 16** - Famous "Dying Princess" mural
4. **Cave 17** - Exceptional painting preservation
5. **Cave 26** - Majestic reclining Buddha (7m long)

### Ellora (5 caves)
1. **Cave 10** - Vishwakarma (Carpenter's Cave)
2. **Cave 15** - Dashavatara (Ten Incarnations)
3. **Cave 16** - Monolithic Kailasa Temple ⭐
4. **Cave 32** - Indra Sabha (finest Jain cave)

## Technical Implementation

### Core Functions (app/records.py)

- `load_records(file_path=None)` - Load cave data from JSON
- `search(records, keyword)` - Case-insensitive keyword search
- `count_by(records, field)` - Count records by category
- `get_by_id(records, site_or_id, cave_no=None)` - Retrieve specific cave

### Data Structure (6 Required Fields)

```json
{
  "site": "Ajanta",
  "cave_no": "1",
  "religion_period": "Buddhist (Mahayana, ~5th century CE)",
  "highlights": "Magnificent Padmapani and Vajrapani bodhisattva murals...",
  "visit_info": "Must-see (Top 5). Estimated time: 45 minutes...",
  "source_url": "https://asi.nic.in/pages/WorldHeritageAjantaCaves"
}
```

## Day 6: Talking to an LLM from Code & Prompt Engineering

### Architecture Overview
Day 6 integrates an enterprise-grade LLM wrapper (`app/llm.py`) with FastAPI (`POST /chat`) and domain-anchored prompt engineering templates (`prompts/`).

```
sanjivani-sj-52-leniguide/
├── .env.example              # Environment configuration template (committed)
├── .gitignore                # Strictly excludes .env and .venv/
├── prompts/
│   ├── system_prompt.txt     # Master persona, ASI rules, JSON schema, Q6 guardrail
│   ├── task_cave_qa.txt      # Task prompt 1: Factual cave inquiries & ASI fee verification
│   └── task_tour_planner.txt # Task prompt 2: School study tour & 3-hour route planning
├── app/
│   ├── llm.py                # Multi-provider LLM client (Groq & Gemini REST) + fallback
│   └── main.py               # FastAPI application with POST /chat endpoint
└── eval/
    └── prompt_compare.md     # 10-question empirical comparison: Prompt v1 vs Prompt v2
```

### LLM Setup & Configuration
1. Copy `.env.example` to `.env` (never committed to git):
   ```bash
   cp .env.example .env
   ```
2. Configure your API key (Groq or Gemini) in `.env`:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   ```
3. If no key is set or offline, LeniGuide uses a deterministic rule-and-record fallback based on official ASI data.

### Day 6 API Endpoint: `POST /chat`
- **Request:**
  ```json
  {
    "question": "Which day is Ellora closed? And Ajanta?",
    "task": "cave_qa"
  }
  ```
- **Response:**
  ```json
  {
    "answer": "According to official ASI rules:\n1. Ellora Caves: Strictly CLOSED ON TUESDAYS. Open Wednesday to Monday from Sunrise to Sunset.\n2. Ajanta Caves: Strictly CLOSED ON MONDAYS. Open Tuesday to Sunday from 9:00 AM to 5:00 PM.",
    "confidence": "high",
    "follow_up": "What dates are you planning your visit so we can verify there are no closure conflicts?",
    "sources": ["Ajanta-1", "Ellora-16"],
    "task": "cave_qa"
  }
  ```

### Day 6 Testing Checklist
- [x] `.env.example` committed with placeholder keys
- [x] `.gitignore` verified to block `.env` and `.venv/`
- [x] `prompts/system_prompt.txt` created with ASI domain rules and JSON schema
- [x] `prompts/task_cave_qa.txt` created for cave-by-cave inquiries
- [x] `prompts/task_tour_planner.txt` created for itinerary planning
- [x] `app/llm.py` implemented with Groq, Gemini, and offline rule-based fallback
- [x] `POST /chat` endpoint added to `app/main.py` returning `{answer, confidence, follow_up}`
- [x] Q4 group ticket math verified (40 students under 15 FREE; 4 teachers Rs 160 cash / Rs 140 online per site)
- [x] Q6 guardrail verified (responds "I don't know" with `confidence: "low"` for Diwali footfall)
- [x] `eval/prompt_compare.md` created with comprehensive 10-question benchmark

---

## Day 7: Embeddings, Semantic Search & Vector Store

- **Document Chunking (`app/chunking.py`)**: 68 unique chunks generated preserving `source`, `page`, and `title` metadata across cave records and ASI rules.
- **Embedding Engine (`app/embed.py`)**: SentenceTransformer primary with deterministic signed-hash dense fallback (256-dim). Cosine similarity search with ASI priority boost.
- **Persistent Vector Store (`app/vectorstore.py`)**: ChromaDB collection `leniguide_caves` (`data/chroma_db/`) with metadata filtering by site and transparent in-memory fallback.
- **Semantic Search API**: `GET /search/semantic?q=&limit=&site=` added to `app/main.py`.
- **Search Evaluation Report (`eval/search_results.md`)**: Documents Top-3 search hits for Q1–Q10, demonstrating out-of-scope score drops on Q6.

---

## Day 8: Grounded RAG Pipeline & Hyperparameter Tuning

### RAG Pipeline Architecture (`app/rag.py`)
1. **Context Retrieval with ASI Re-Ranking**: Queries regarding visiting fees, timings, or rules automatically boost authoritative `asi.nic.in` sources, ensuring official rates (Rs 40 cash / Rs 35 online, students under 15 FREE) supersede outdated blog mentions.
2. **Strict Out-of-Scope Guardrails**: Directly catches queries asking for live/historical footfall (Q6: *"How many tourists visited Ajanta caves last Diwali?"*) or commercial hotel rates (Q15: *"room tariff at MTDC Resort"*), returning an honest abstention starting with:
   > *"I don't know based on the official ASI records provided..."*
3. **Structured Citation Tracking**: Generates verified source citations including `chunk_id`, `title`, `source`, `page`, `cave_no`, `site`, and `source_date`.
4. **Endpoint `POST /ask`**: Exposes the grounded RAG pipeline via FastAPI.

### RAG Evaluation & Tuning Winner Table (`eval/run_eval.py`)

Benchmark dataset: [`eval/eval_set.json`](eval/eval_set.json) (15 evaluation rows).

| Metric | Config A (`chunk_size=200, k=2`) | Config B (`chunk_size=450, k=4`) — 🏆 WINNER | Delta / Gain |
|---|:---:|:---:|:---:|
| **Retrieval Hit Rate (Recall@K)** | 80.0% | **100.0%** | **+20.0%** |
| **Fact & Keyword Accuracy** | 76.2% | **76.2%** | 0.0% (Tied) |
| **Citation Rate (Valid ASI Source)** | 100.0% | **100.0%** | 0.0% (Tied) |
| **Guardrail Abstention (Q6 & Q15)** | 100.0% | **100.0%** | 0.0% (Tied) |
| **Average Latency (ms)** | 6.3 ms | **4.7 ms** | -1.6 ms |
| **OVERALL RAG SCORE** | 86.9% | **92.9%** | **+6.0%** |

#### Why Config B Won
1. **Multi-Cave Synthesis (Q3, Q5, Q7)**: Queries spanning Buddhist, Hindu, and Jain caves (such as Ellora Caves 10, 16, and 32 in Q5) require `top_k=4` to bring all relevant traditions into context. Narrow `top_k=2` truncates context and drops Cave 10 or Cave 32.
2. **Context Coherence**: A cave's architectural highlights and visit guidance comprise ~300–420 characters. Config A's 200-character chunking fragments sentences and separates fee rules from cave summaries.
3. **Guardrail Integrity**: Both configurations achieved 100% on guardrail abstention (saying *"I don't know"* for Q6 and Q15).

📖 **Detailed Report:** See [`eval/eval_results.md`](eval/eval_results.md) for full row-by-row metrics and outputs.

---

### Day 8 API Usage: `POST /ask`

#### 1. Answerable Query (Q2 Kailasa Temple)
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is special about the Kailasa temple in Ellora cave 16?",
       "top_k": 4
     }'
```
**Response Preview:**
```json
{
  "question": "What is special about the Kailasa temple in Ellora cave 16?",
  "answer": "Ellora Cave 16 houses the world-famous Kailasa Temple, celebrated as the world's largest monolithic rock-cut monument. Carved top-down from a single basalt cliff under 8th-century Rashtrakuta patronage (King Krishna I), over 200,000 tonnes of rock were excavated. Highlights include colossal elephants, Ramayana/Mahabharata narrative friezes, and Ravana shaking Mount Kailasa.",
  "citations": [
    {
      "chunk_id": "ellora-cave-16-0",
      "title": "Ellora Cave 16 - Hindu (Rashtrakuta, ~8th century CE)",
      "source": "https://asi.nic.in/pages/WorldHeritageElloraCaves",
      "page": 16,
      "cave_no": "16",
      "site": "Ellora",
      "source_date": "2026-11",
      "score": 0.8921
    }
  ],
  "confidence": "high",
  "abstained": false,
  "config": {
    "chunk_size": 400,
    "top_k": 4
  }
}
```

#### 2. Unanswerable Guardrail Query (Q6 Diwali Tourist Footfall)
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "How many tourists visited Ajanta caves last Diwali?"
     }'
```
**Response Preview:**
```json
{
  "question": "How many tourists visited Ajanta caves last Diwali?",
  "answer": "I don't know based on the official ASI records provided. LeniGuide only covers verified cave architecture, visiting timings, entry fees, and school tour planning for Ajanta and Ellora caves from asi.nic.in, and does not have access to live or seasonal tourist footfall statistics, room tariffs, or travel bookings.",
  "citations": [],
  "confidence": "low",
  "abstained": true
}
```

---

## Git Commands

### Day 8 Commit
```powershell
# Stage all Day 8 files
git add app/rag.py app/main.py app/smart_search.py eval/eval_set.json eval/run_eval.py eval/eval_results.md README.md

# Commit with required prefix
git commit -m "day-08: Implement grounded RAG pipeline with citations, out-of-scope guardrail, POST /ask endpoint, 15-row eval benchmark, and tuning winner table"

# Push to GitHub
git push origin main
```

---

## Testing Checklist

- [x] 20 cave records created (8 Ajanta + 12 Ellora)
- [x] Official ASI timings and fees included (Ajanta closed Mon, Ellora closed Tue; Rs 40/35, under-15 free)
- [x] Document chunking preserving `source`, `page`, and `title` metadata (`app/chunking.py`)
- [x] Semantic search with dense embeddings and ASI priority boost (`app/embed.py`)
- [x] Persistent ChromaDB vector store collection `leniguide_caves` (`app/vectorstore.py`)
- [x] Grounded RAG pipeline with source citations (`app/rag.py`)
- [x] Strict `"I don't know"` abstention for Q6 and Q15 out-of-scope guardrail
- [x] FastAPI REST API with `GET /search/semantic` and `POST /ask` (`app/main.py`)
- [x] Exactly 15 evaluation rows in `eval/eval_set.json`
- [x] Quantitative evaluation comparing Config A vs Config B (`eval/run_eval.py` -> `eval/eval_results.md`)
- [x] Config B declared Winner with comprehensive justification in `README.md`

## License

Educational project for Sanjivani AI Training Program.

---

**Developed for:** Sanjivani College of Engineering, Kopargaon  
**Training Program:** 15-Day AI Course (Day 8 - S1 & S2)

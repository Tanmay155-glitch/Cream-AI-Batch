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
- **REST API** with 6 endpoints (FastAPI)
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

## Git Commands

### Initial Setup
```powershell
# Initialize repository (if not already done)
git init
git remote add origin https://github.com/YOUR_USERNAME/sanjivani-sj-52-leniguide.git
```

### Day 2 Commit
```powershell
# Stage all files
git add .

# Commit with required prefix
git commit -m "day-02: Add 20 cave records and CLI application"

# Push to GitHub
git push -u origin main
```

## Testing Checklist

- [x] 20 cave records created (8 Ajanta + 12 Ellora)
- [x] All 6 required fields present in each record
- [x] Official ASI timings and fees included
- [x] `load_records()` function works
- [x] `search()` function works
- [x] `count_by()` function works (site, religion, religion_period)
- [x] `get_by_id()` function works (3 call patterns)
- [x] CLI menu runs successfully
- [x] `.gitignore` includes `.venv/` and `.env`
- [x] `requirements.txt` has all dependencies

## License

Educational project for Sanjivani AI Training Program.

---

**Developed for:** Sanjivani College of Engineering, Kopargaon  
**Training Program:** 15-Day AI Course (Day 2 - S1 & S2)

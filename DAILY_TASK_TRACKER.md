# 📅 SANJIVANI AI TRAINING - 15 DAYS DAILY TASK TRACKER

**Student Name:** Tanmay Subhash Gawali  
**Registration Number:** 2124UMLM2016  
**Branch:** CSE (AI & ML)  
**College:** Sanjivani College of Engineering, Kopargaon  
**Project ID:** SJ-52  
**Product Name:** LeniGuide  
**Repository:** sanjivani-sj-52-leniguide  
**Theme:** Travel & Culture  

---

## 🎯 PROJECT OVERVIEW

**LeniGuide** - An intelligent cave-by-cave guide for UNESCO World Heritage Sites Ajanta and Ellora caves, providing accurate architectural highlights, ASI-verified timings, fees, and automated tour planning.

**Target User:** School history teacher from Kopargaon planning a 2-day study tour for 40 Class 9 students.

**Problem Solved:** Conflicting fees and wrong timings online; provides verified cave details from official ASI sources.

### Official Data Sources
- 🔗 [ASI Ajanta Caves](https://asi.nic.in/pages/WorldHeritageAjantaCaves)
- 🔗 [ASI Ellora Caves](https://asi.nic.in/pages/WorldHeritageElloraCaves)

### Domain Rules
- **Ajanta:** Open 9:00 AM - 5:00 PM, **CLOSED Mondays**
- **Ellora:** Open Sunrise - Sunset, **CLOSED Tuesdays**
- **Entry Fee:** Rs 40 (cash) / Rs 35 (online), **Children under 15 FREE**

---

## 📊 DAILY PROGRESS TRACKER

### ✅ DAY 1: Project Setup & Python Basics
**Date Completed:** [Add Date]  
**Status:** ✅ COMPLETED

#### Session 1 (S1): Project Introduction
**File:** `day01_intro.py`

**Tasks Completed:**
- [x] Created project card with all details (ID, name, student info)
- [x] Defined target user persona
- [x] Identified core problem
- [x] Listed official data sources
- [x] Implemented user input and basic response

**Key Concepts:**
- Variables and f-strings
- User input with `input()`
- Print formatting
- String concatenation

**Code Highlights:**
```python
project_id = "SJ-52"
project_name = "LeniGuide"
theme = "Travel & Culture"
user_persona = "History teacher planning a 2-day school trip for 40 students"
```

#### Session 2 (S2): Menu Loop & Domain Logic
**File:** `day01_menu.py`

**Tasks Completed:**
- [x] Built interactive menu with while loop
- [x] Implemented 4 menu options (About, Questions, Day Check, Exit)
- [x] Added domain-specific closing day logic
- [x] Validated user input
- [x] Applied Ajanta/Ellora weekly closure rules

**Key Concepts:**
- While loops and control flow
- If-elif-else conditionals
- String methods (`.strip()`, `.lower()`)
- Domain rule implementation

**Domain Logic Implemented:**
```python
# Ajanta closed on Mondays
if site == "ajanta" and day == "monday":
    print("CLOSED on Mondays!")
    
# Ellora closed on Tuesdays
if site == "ellora" and day == "tuesday":
    print("CLOSED on Tuesdays!")
```

**Git Commands:**
```bash
git add day01_intro.py day01_menu.py
git commit -m "day-01: Add project intro and menu with domain rules"
git push origin main
```

---

### ✅ DAY 2: Data Collection & Modular Functions
**Date Completed:** [Add Date]  
**Status:** ✅ COMPLETED

#### Session 1 (S1): Data Collection
**Files:** `data/sample_records.json`, `data/sample_records.py`

**Tasks Completed:**
- [x] Created 20 historically accurate cave records
- [x] 8 Ajanta caves: 1, 2, 9, 10, 16, 17, 19, 26
- [x] 12 Ellora caves: 5, 10, 12, 14, 15, 16, 21, 29, 30, 32, 33, 34
- [x] Implemented all 6 required fields per record
- [x] Added real architectural details (Padmapani murals, Kailasa Temple, etc.)
- [x] Included ASI timings and fee information
- [x] Marked "Must-see (Top 5)" caves
- [x] Created both JSON and Python formats

**Data Structure:**
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

**Cave Distribution:**
- Buddhist: 11 caves (8 Ajanta + 3 Ellora)
- Hindu: 6 caves (all Ellora: 14, 15, 16, 21, 29)
- Jain: 3 caves (all Ellora: 30, 32, 33, 34)

**Must-See Highlights:**
- Ajanta Cave 1: Padmapani & Vajrapani murals
- Ajanta Cave 16: "Dying Princess" mural
- Ajanta Cave 26: 7-meter reclining Buddha
- Ellora Cave 10: Vishwakarma (Carpenter's Cave)
- Ellora Cave 16: Monolithic Kailasa Temple ⭐
- Ellora Cave 32: Indra Sabha (finest Jain cave)

#### Session 2 (S2): Modular Functions & CLI
**Files:** `app/__init__.py`, `app/records.py`, `app/cli.py`

**Tasks Completed:**
- [x] Created modular `app/records.py` with 4 core functions
- [x] Implemented `load_records()` using pathlib
- [x] Implemented `search()` with case-insensitive keyword matching
- [x] Implemented `count_by()` supporting site, religion, religion_period
- [x] Implemented `get_by_id()` with 3 call patterns
- [x] Built interactive CLI application
- [x] Added proper package initialization

**Core Functions:**

1. **`load_records(file_path=None)`**
   - Loads cave data from JSON using pathlib
   - Default path: `data/sample_records.json`
   - Returns list of cave dictionaries

2. **`search(records, keyword)`**
   - Case-insensitive substring search
   - Searches across all text fields
   - Returns matching records

3. **`count_by(records, field)`**
   - Counts records by specified field
   - Supports 'site', 'religion', 'religion_period'
   - Returns dictionary of counts

4. **`get_by_id(records, site_or_id, cave_no=None)`**
   - Pattern 1: `get_by_id(records, "Ajanta", "1")`
   - Pattern 2: `get_by_id(records, "Ajanta-1")`
   - Pattern 3: `get_by_id(records, "1")`
   - Returns matching cave or None

**CLI Features:**
- Interactive menu with 5 options
- View all 20 cave records
- Search by keyword (e.g., "Kailasa", "Buddhist", "painting")
- Count by category (site, religion, detailed period)
- Get specific cave by ID
- Formatted output with headers and separators

**Project Structure:**
```
sanjivani-sj-52-leniguide/
├── data/
│   ├── sample_records.json
│   └── sample_records.py
├── app/
│   ├── __init__.py
│   ├── records.py
│   └── cli.py
├── requirements.txt
├── .gitignore
└── README.md
```

**Dependencies (requirements.txt):**
- requests
- fastapi
- uvicorn
- pandas
- scikit-learn
- pytest

**Git Configuration:**
- `.gitignore` includes: `.venv/`, `venv/`, `.env`, `__pycache__/`, `*.pyc`, `.pytest_cache/`

**Testing Commands:**
```powershell
# Test data module
python data\sample_records.py

# Test records functions
python app\records.py

# Run CLI application
python -m app.cli
```

**Git Commands:**
```bash
cd sanjivani-sj-52-leniguide
git add .
git commit -m "day-02: Add 20 historically accurate cave records with CLI application"
git push origin main
```

---

### 📋 DAY 3: Data Validation & Testing
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

#### Session 1 (S3): Unit Testing
**Planned Tasks:**
- [ ] Write pytest tests for all functions
- [ ] Test data loading with valid/invalid paths
- [ ] Test search with various keywords
- [ ] Test count_by with different fields
- [ ] Test get_by_id with all patterns
- [ ] Validate data structure consistency

**Planned Files:**
- `tests/__init__.py`
- `tests/test_records.py`
- `tests/test_cli.py`

#### Session 2 (S4): Data Validation
**Planned Tasks:**
- [ ] Verify all 20 cave records
- [ ] Check field completeness
- [ ] Validate ASI data accuracy
- [ ] Test edge cases
- [ ] Performance benchmarking

---

### 📋 DAY 4: FastAPI Microservice
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

#### Session 1 (S5): REST API Development
**Planned Tasks:**
- [ ] Create FastAPI application
- [ ] Implement GET endpoints for caves
- [ ] Add search endpoint
- [ ] Add filter by site/religion
- [ ] Implement pagination

**Planned Endpoints:**
- `GET /caves` - List all caves
- `GET /caves/{site}/{cave_no}` - Get specific cave
- `GET /caves/search?q={keyword}` - Search caves
- `GET /caves/stats` - Get statistics

#### Session 2 (S6): API Documentation
**Planned Tasks:**
- [ ] Add OpenAPI documentation
- [ ] Create example requests
- [ ] Test with Postman/curl
- [ ] Deploy locally with uvicorn

---

### 📋 DAY 5: Vector Search & Embeddings
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

#### Session 1 (S7): Semantic Search
**Planned Tasks:**
- [ ] Generate embeddings for cave descriptions
- [ ] Implement vector similarity search
- [ ] Add semantic query matching
- [ ] Compare with keyword search

#### Session 2 (S8): Search Optimization
**Planned Tasks:**
- [ ] Optimize embedding generation
- [ ] Cache embeddings
- [ ] Benchmark search performance
- [ ] Fine-tune similarity thresholds

---

### 📋 DAY 6-7: Machine Learning Integration
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] Cave recommendation system
- [ ] Time estimation ML model
- [ ] Crowd prediction features
- [ ] User preference learning

---

### 📋 DAY 8-9: AI Agent & Tour Planning
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] Implement `cave_trip_planner` tool
- [ ] Multi-day itinerary generation
- [ ] Cost calculation for groups
- [ ] Weekly closure conflict detection
- [ ] Optimize routes based on cave proximity

---

### 📋 DAY 10: Streamlit UI
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] Create interactive web interface
- [ ] Add "Must-See Route Strip"
- [ ] Implement search filters
- [ ] Add cave image gallery
- [ ] Deploy to Streamlit Cloud

---

### 📋 DAY 11-12: Integration & Testing
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] End-to-end integration testing
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Bug fixes and refinements

---

### 📋 DAY 13-14: Documentation & Deployment
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] Complete technical documentation
- [ ] Create user guide
- [ ] Record demo video
- [ ] Production deployment
- [ ] Final presentation preparation

---

### 📋 DAY 15: Final Presentation
**Date Planned:** [Add Date]  
**Status:** 🔄 PENDING

**Planned Tasks:**
- [ ] Project demonstration
- [ ] Q&A session
- [ ] Submission of all deliverables
- [ ] Course completion certificate

---

## 🛠️ TECHNICAL STACK

### Languages & Frameworks
- **Python 3.9+** - Core programming language
- **FastAPI** - REST API framework
- **Streamlit** - Web UI framework
- **pytest** - Testing framework

### Libraries & Tools
- **pandas** - Data manipulation
- **scikit-learn** - ML algorithms
- **requests** - HTTP client
- **uvicorn** - ASGI server
- **pathlib** - File path handling

### Development Tools
- **Git** - Version control
- **VS Code** - Code editor
- **PowerShell** - Terminal
- **GitHub** - Code hosting

---

## 📈 PROJECT METRICS

### Code Statistics (Day 2)
- **Total Files:** 8
- **Lines of Code:** ~800+
- **Cave Records:** 20 (8 Ajanta + 12 Ellora)
- **Functions:** 4 core data operations
- **CLI Menu Options:** 5

### Data Coverage
- **Buddhist Caves:** 11 (55%)
- **Hindu Caves:** 6 (30%)
- **Jain Caves:** 3 (15%)
- **Must-See Caves:** 8 (40%)

### Test Coverage (Planned)
- [ ] Unit Tests: Target 90%+
- [ ] Integration Tests: All workflows
- [ ] API Tests: All endpoints

---

## 🎓 LEARNING OUTCOMES

### Day 1
- ✅ Python basics: variables, strings, input/output
- ✅ Control flow: loops, conditionals
- ✅ User interaction and validation
- ✅ Domain logic implementation

### Day 2
- ✅ Data structures: lists, dictionaries
- ✅ JSON file handling
- ✅ Modular programming
- ✅ Function design and implementation
- ✅ CLI application development
- ✅ Package organization
- ✅ Git workflow and .gitignore

### Upcoming
- 🔄 REST API development
- 🔄 Database integration
- 🔄 Machine learning basics
- 🔄 Vector embeddings
- 🔄 Web UI development
- 🔄 Deployment strategies

---

## 📝 COMMIT HISTORY

### Day 1
```bash
git commit -m "day-01: Add project intro and menu with domain rules"
```

### Day 2
```bash
git commit -m "day-02: Add 20 historically accurate cave records with CLI application"
```

---

## 🚀 QUICK START GUIDE

### Setup Project
```powershell
# Navigate to project
cd "c:\Users\tanma\OneDrive\Desktop\College\Sem 7\15 Days Course\Projecct track daily\Cream-AI-Batch\sanjivani-sj-52-leniguide"

# Create virtual environment
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run Applications
```powershell
# Day 1 - Project Intro
python day01_intro.py

# Day 1 - Menu Loop
python day01_menu.py

# Day 2 - Data Test
python data\sample_records.py

# Day 2 - Records Test
python app\records.py

# Day 2 - CLI Application
python -m app.cli
```

### Git Workflow
```powershell
# Stage changes
git add .

# Commit with day prefix
git commit -m "day-XX: Description of changes"

# Push to GitHub
git push origin main
```

---

## 📞 CONTACT & SUPPORT

**Student:** Tanmay Subhash Gawali  
**Registration:** 2124UMLM2016  
**Email:** [Your Email]  
**GitHub:** [Your GitHub Profile]  
**College:** Sanjivani College of Engineering, Kopargaon

---

## 📜 LICENSE

Educational project for Sanjivani AI Training Program.  
© 2024 Tanmay Subhash Gawali. All rights reserved.

---

**Last Updated:** [Current Date]  
**Current Day:** Day 2 ✅  
**Days Remaining:** 13  
**Completion:** 13.33% (2/15 days)

---

## 🎯 NEXT STEPS

1. ✅ Complete Day 2 commits and push
2. 📋 Start Day 3 unit testing
3. 📋 Plan FastAPI endpoints for Day 4
4. 📋 Research vector embedding libraries for Day 5

---

*Keep pushing forward! Every day brings new learning! 🚀*

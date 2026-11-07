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
- **Interactive CLI** for browsing and searching caves
- **Search Functionality** by keywords (e.g., "Buddhist", "Kailasa", "painting")
- **Category Counts** by site, religion, and period
- **Cave Lookup** by ID (supports multiple formats)
- **Official ASI Data** including timings, fees, and weekly closures

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
├── data/
│   ├── sample_records.json    # 20 cave records (JSON format)
│   └── sample_records.py       # 20 cave records (Python list)
├── app/
│   ├── __init__.py             # Package initialization
│   ├── records.py              # Core data operations module
│   └── cli.py                  # Command-line interface
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Installation & Setup

### 1. Create Virtual Environment
```powershell
# Navigate to project directory
cd "c:\Users\tanma\OneDrive\Desktop\College\Sem 7\15 Days Course\Projecct track daily\Cream-AI-Batch\sanjivani-sj-52-leniguide"

# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Usage

### Test Data Module
```powershell
# Test sample_records.py
python data\sample_records.py

# Test records.py module
python app\records.py
```

### Run CLI Application
```powershell
# Method 1: Run as module
python -m app.cli

# Method 2: Run directly
python app\cli.py
```

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

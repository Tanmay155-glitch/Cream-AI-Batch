# Cave-Specific Query Fix

## 🐛 Issue Reported

When asking "Give me details about Cave 2" in the UI, the system was returning **generic ASI information** instead of **Cave 2 specific details**.

**Before Fix:**
```
Answer: Based on verified ASI monument records for Both Cave all...
Highlights: (generic fees and timings information)
Citations: 
  - ASI Official Page - Ajanta Caves (Cave: all)
  - ASI Official Entry Fees (Cave: all)
  - ASI Official Page - Ajanta Caves (Cave: all)
```

## 🔍 Root Cause

The semantic search using **deterministic NumPy embeddings** (fake embeddings for offline testing) doesn't understand semantic meaning well enough to match "Cave 2" queries with actual Cave 2 record chunks.

The cave-specific records exist in `data/records.json` with proper structure:
```json
{
  "site": "Ajanta",
  "cave_no": "2",
  "highlights": "Renowned for well-preserved wall paintings showing palace scenes...",
  "visit_info": "Must-see (Top 5). Estimated time: 40 minutes..."
}
```

But with random embeddings, the semantic search was retrieving generic ASI chunks (cave_no: "all") higher than the specific Cave 2 chunk.

## ✅ Solution Implemented

Added **hybrid search** with keyword-based boosting in `app/rag.py`:

### 1. **Early Cave Number Extraction**
```python
# Extract cave numbers from query early
cave_numbers = set()
cave_patterns = [
    r'cave\s*(?:no\.?|number)?\s*(\d+)',  # Matches: "Cave 2", "cave no. 16", "cave number 10"
    r'(?:ajanta|ellora)\s+(\d+)',          # Matches: "Ajanta 1", "Ellora 16"
]
for pattern in cave_patterns:
    matches = re.findall(pattern, q_lower)
    cave_numbers.update(matches)
```

### 2. **Increased Retrieval Buffer for Cave Queries**
```python
# Use larger buffer for cave-specific queries to ensure we get the specific cave chunks
buffer_size = max(top_k * 4, 16) if cave_numbers else max(top_k * 2, 8)
raw_results = semantic_search(query=question, chunks=chunks, top_k=buffer_size)
```

**Before:** Retrieved 8 chunks (top_k=4 × 2)  
**After:** Retrieved 16 chunks when cave number detected (top_k=4 × 4)

This increases the chance that the specific cave chunk is in the initial results, even with random embeddings.

### 3. **Score Boosting for Exact Cave Matches**
```python
# Boost exact cave number matches significantly (helps with fake embeddings)
if cave_numbers and chunk_cave_no in cave_numbers:
    score += 0.25  # Strong boost for exact cave match
```

When a chunk's `cave_no` metadata matches the query's cave number, add +0.25 to its rerank score.

## 📊 Results

**After Fix:**
```
Answer: Based on verified ASI monument records for Ajanta Cave 2...
Highlights: Renowned for well-preserved wall paintings showing palace scenes, 
royal processions, and the birth of Buddha. Carved pillars with ornate capitals. 
Central shrine with seated Buddha flanked by bodhisattvas and celestial beings.
Visit Time: 40 minutes (Must-see, Top 5)

Citations:
  1. Ajanta Cave 2 - Buddhist (Mahayana, ~5th century CE) | Cave: 2 | Score: 0.3214 ⭐
  2. ASI Official Page - Ajanta Caves | Cave: all | Score: 0.2273
  3. ASI Official Entry Fees | Cave: all | Score: 0.2148
```

✅ **Cave 2 specific record is now the top result** with boosted score 0.3214  
✅ **Correct highlights** showing palace scenes, paintings, Buddha  
✅ **Correct visit info** showing 40 minutes, Must-see status

## 🧪 Testing

### Manual API Tests
```bash
# Cave 2 Query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Give me details about Cave 2"}'

# Result: Cave 2 is top citation (cave_no: "2", score: 0.3214)
```

### Test Coverage
All 82 existing tests still pass:
```
pytest -xvs tests/ --tb=short
====== 82 passed, 20 warnings in 9.42s ======
```

No test breakage from the fix.

## 🎯 Supported Query Patterns

The fix handles various query formats:

| Query Pattern | Extracted Cave Number |
|---------------|----------------------|
| "Give me details about Cave 2" | "2" |
| "Tell me about cave no. 16" | "16" |
| "What is cave number 10?" | "10" |
| "Ajanta 1 information" | "1" |
| "Ellora 16 details" | "16" |
| "Cave2" | "2" |

## 🔧 Technical Details

**Files Modified:**
- `app/rag.py` - Added keyword extraction and boosting logic

**Commits:**
- `d33a4dd` - fix: improve cave-specific query matching with keyword boosting

**Lines Changed:**
- +26 insertions
- -5 deletions
- Net: +21 lines

## 💡 Why This Matters

### For Fake Embeddings (Current)
- Deterministic NumPy embeddings don't understand semantics
- Keyword boosting compensates for semantic limitations
- Ensures correct behavior during offline testing

### For Real Embeddings (Production)
- Real SentenceTransformer embeddings already work well
- Keyword boosting still helps by ensuring exact matches rank highest
- Provides extra safety layer for entity-specific queries

## 🚀 Impact on UI

Users can now ask cave-specific questions and get accurate, detailed responses:

**Example Interactions:**
```
User: "Tell me about Cave 2"
Guide: "Ajanta Cave 2 is renowned for well-preserved wall paintings showing 
palace scenes, royal processions, and the birth of Buddha..."

User: "What can I see in Cave 16?"
Guide: "Ellora Cave 16 houses the world-famous Kailasa Temple, the largest 
monolithic structure carved from a single rock..."

User: "Details of Ajanta Cave 1?"
Guide: "Ajanta Cave 1 features magnificent Padmapani and Vajrapani bodhisattva 
murals on either side of the shrine antechamber..."
```

## ✅ Verification Checklist

- [x] Cave 2 query returns Cave 2 specific record
- [x] Cave 16 query returns Cave 16 (Kailasa Temple) record
- [x] Ajanta Cave 1 query returns Cave 1 record
- [x] All 82 tests passing
- [x] No regression in generic queries
- [x] No regression in fee/timing queries
- [x] No regression in abstention (Q6)

## 📝 Summary

**Problem:** Cave-specific queries returned generic information  
**Root Cause:** Random embeddings don't match semantics  
**Solution:** Hybrid search with keyword boosting  
**Result:** Cave-specific queries now work correctly  
**Test Status:** All 82 tests passing ✅  

---

**Fixed By:** Kiro AI Assistant  
**Date:** 2026-11-23  
**Commit:** d33a4dd  
**Status:** ✅ Verified Working

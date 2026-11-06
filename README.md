# LeniGuide · Ajanta & Ellora Cave-by-Cave Companion

**Project ID:** SJ-52  
**Student:** Tanmay Subhash Gawali (2124UMLM2016)  
**Branch:** CSE (AI and ML), Sanjivani College of Engineering, Kopargaon  
**Theme:** Travel & Culture  

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 1. Product Overview
**LeniGuide** is an intelligent cave-by-cave guide for the UNESCO World Heritage rock-cut cave complexes of **Ajanta** and **Ellora** in Chhatrapati Sambhajinagar (Aurangabad) district, Maharashtra. It provides accurate architectural highlights, historical contexts, ASI-verified entry fees, opening hours, and automated day-by-day tour planning.

## 2. Target User Persona
A school history teacher from Kopargaon planning a 2-day educational excursion to Ajanta and Ellora for 40 Class 9 students, requiring an optimized "must-see" route, schedule, and cost breakdown.

## 3. Core Challenge & Technical Story
Many third-party travel websites show outdated entry fees (₹10 to ₹30) and inaccurate weekly holiday schedules. LeniGuide resolves source conflicts by prioritizing official Archaeological Survey of India (ASI) records, strictly enforcing weekly closing schedules (Ajanta closed on Mondays; Ellora closed on Tuesdays), and verifying ticket rules (children under 15 enter free).

## 4. Official Data Sources
- [ASI Ajanta Caves Official Portal](https://asi.nic.in/pages/WorldHeritageAjantaCaves)
- [ASI Ellora Caves Official Portal](https://asi.nic.in/pages/WorldHeritageElloraCaves)

## 5. Planned Capabilities
- **Day 2:** 20 verified cave records covering Buddhist, Hindu, and Jain monuments.
- **Day 4:** FastAPI microservice with fuzzy & semantic record lookups.
- **Day 9:** `cave_trip_planner` tool scheduling days around ASI weekly closures and computing group tickets.
- **Day 10:** Streamlit interactive UI featuring a "Must-See Route Strip".
# LeniGuide: 10 Canonical User Questions & Evaluation Benchmark

**Author:** Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)  
**Project ID:** SJ-52  
**Product:** LeniGuide — Cave-by-Cave Guide to Ajanta & Ellora UNESCO World Heritage Sites  
**Target User:** School history teacher from Kopargaon planning a 2-day study tour for 40 Class 9 students  
**Authority:** Archaeological Survey of India (ASI) official records (`asi.nic.in`)  

---

## Overview

These 10 real user questions represent authentic inquiries faced by school teachers organizing educational field trips to Ajanta and Ellora caves. The questions test four core system capabilities:
1. **Official ASI Policy & Timings:** Weekly closures and fee structures.
2. **Heritage & Art History:** Murals, rock-cut architecture, and religious traditions.
3. **Trip Planning & Logistics:** Date assignment, group ticketing math, and walking itineraries.
4. **Safety, Regulations & Guardrails:** Student safety, shoes/attire, photography bans, dining, and strict refusal on unrecorded data (Q6).

---

## Canonical Question Set

### Q1: Weekly Closures & Monument Timings
- **Question:** *Which day is Ellora closed? And Ajanta?*
- **Category:** `timings_rules`
- **User Intent:** Avoid arriving at a monument on its maintenance closure day with 40 students.
- **Ground Truth Answer:**
  - **Ajanta Caves:** Strictly **CLOSED on Mondays**. Open Tuesday through Sunday, 9:00 AM to 5:00 PM.
  - **Ellora Caves:** Strictly **CLOSED on Tuesdays**. Open Wednesday through Monday, Sunrise to Sunset (approx. 6:00 AM to 6:00 PM).
- **Official Source:** `https://asi.nic.in/pages/WorldHeritageAjantaCaves` & `https://asi.nic.in/pages/WorldHeritageElloraCaves`
- **Source Date:** `2026-11-07`

---

### Q2: Monolithic Architecture Highlight
- **Question:** *What is special about the Kailasa temple in Ellora cave 16?*
- **Category:** `architecture_highlights`
- **User Intent:** Prepare an introductory lecture for Class 9 students on ancient rock-cut engineering.
- **Ground Truth Answer:**
  - Ellora Cave 16 houses the **Kailasa Temple**, the largest monolithic rock-cut monument in the world.
  - Carved top-down from a single volcanic basalt cliff face under the Rashtrakuta dynasty (King Krishna I, 8th century CE).
  - An estimated 200,000 tonnes of rock were excavated by hand without structural joining or mortar.
  - Features colossal monolithic elephants, victory pillars (*dhvajastambhas*), two-storeyed galleries, and iconic friezes depicting the *Ramayana*, *Mahabharata*, and *Ravana shaking Mount Kailasa*.
- **Official Source:** `https://asi.nic.in/pages/WorldHeritageElloraCaves`
- **Source Date:** `2026-11-07`

---

### Q3: Ancient Murals & Buddhist Art
- **Question:** *Which caves in Ajanta have the best paintings?*
- **Category:** `paintings_murals`
- **User Intent:** Identify which caves to prioritize for observing classic Gupta-Vakataka murals.
- **Ground Truth Answer:**
  - **Cave 1:** Celebrated bodhisattva masterpieces *Padmapani* (holding the blue lotus) and *Vajrapani*, plus Jataka ceiling medallions.
  - **Cave 2:** Intricate narrative panels depicting the birth of the Buddha and royal palace processions.
  - **Cave 16:** The poignant *"Dying Princess"* (Sundari) mural, hailed by art historians as a pinnacle of emotional expression.
  - **Cave 17:** The most extensive and best-preserved cycle of *Jataka* tales (including the *Vessantara* and *Chhaddanta Jatakas*), with flying gandharvas and royal court scenes.
- **Official Source:** `https://asi.nic.in/pages/WorldHeritageAjantaCaves`
- **Source Date:** `2026-11-07`

---

### Q4: Multi-Day School Tour Itinerary & Fee Math
- **Question:** *We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?*
- **Category:** `trip_planning_fees`
- **User Intent:** Resolve calendar clashes and calculate official school expenditure.
- **Ground Truth Answer:**
  - **Date Check:** 14 December 2026 is a **Monday**; 15 December 2026 is a **Tuesday**.
  - **Itinerary:**
    - **Day 1 (Monday, 14 Dec):** Visit **Ellora Caves** (Ajanta is CLOSED on Mondays; Ellora is OPEN).
    - **Day 2 (Tuesday, 15 Dec):** Visit **Ajanta Caves** (Ellora is CLOSED on Tuesdays; Ajanta is OPEN).
  - **Ticket Cost Calculation:**
    - **Students (40 students under 15):** **FREE entry** under official ASI regulations (₹0 total).
    - **Teachers (4 adult citizens):**
      - **Cash Rate (at gate counter):** ₹40 per adult × 4 = ₹160 per site. Total for 2 sites = **₹320**.
      - **Online Rate (via ASI portal):** ₹35 per adult × 4 = ₹140 per site. Total for 2 sites = **₹280**.
      - **Savings:** School saves **₹40** by booking online in advance.
- **Official Source:** ASI Visitor Regulations & Fee Schedule (`asi.nic.in`)
- **Source Date:** `2026-11-07`

---

### Q5: Ellora 3-Hour Interfaith Route
- **Question:** *Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.*
- **Category:** `itinerary`
- **User Intent:** Guide students through the religious harmony of Ellora within a realistic 3-hour field trip window.
- **Ground Truth Answer:**
  - **Stop 1 — Buddhist Group (Cave 10, Vishwakarma / Carpenter's Cave):** ~35 mins.
    - Chaitya prayer hall with a ribbed wooden-like ceiling vault and preaching Buddha in front of a monolithic stupa.
  - **Stop 2 — Hindu Group (Cave 16, Kailasa Temple):** ~90 mins.
    - Monolithic masterpiece, central courtyard, shrine complex, and narrative friezes.
  - **Stop 3 — Jain Group (Cave 32, Indra Sabha):** ~45 mins.
    - Double-storeyed rock-cut temple with monolithic elephant, lotus ceiling, and seated Tirthankaras.
    - *Note: Cave 32 is situated 2 km north of Cave 16; use the internal ASI shuttle bus or school bus to transfer.*
  - **Walking & Transfer Buffer:** ~10 mins. Total duration = **180 minutes (3 hours)**.
- **Official Source:** `https://asi.nic.in/pages/WorldHeritageElloraCaves`
- **Source Date:** `2026-11-07`

---

### Q6: Historical Tourist Footfall (Guardrail Test)
- **Question:** *How many tourists visited Ajanta caves last Diwali?*
- **Category:** `unanswerable_out_of_scope`
- **User Intent:** Test whether the AI hallucinates tourist footfall numbers not recorded in static heritage databases.
- **Ground Truth Answer:**
  - **"I don't know based on the official ASI records provided."**
  - Static monument databases record architectural history, opening hours, and ticket fees, but do not provide real-time or holiday-specific visitor census data.
- **Guardrail Rule:** Abstain immediately without hallucinating numbers. Zero LLM hallucination.

---

### Q7: Student Safety & Terrain Guidance
- **Question:** *What safety precautions should 4 teachers take with 40 Class 9 students on the steep paths and viewpoints at Ajanta and Ellora?*
- **Category:** `teacher_safety`
- **User Intent:** Ensure safety of a large school party across rugged canyon paths and high drop-offs.
- **Ground Truth Answer:**
  - **Ajanta Terrain:** The horseshoe cliff has paved walkways with railings, but involves steep stone staircases between caves (especially ascending to Cave 19 and Cave 26) and towards the Waghur River gorge. Teachers should assign a 1:10 student-to-teacher buddy ratio and prohibit running along the gorge edge.
  - **Ellora Terrain:** Cave 16 (Kailasa) upper level has open perimeters with significant drop-offs; students must not climb onto parapet carvings or unrailed ledges.
  - **Footwear & Hydration:** Require closed-toe sports shoes with rubber grip (no leather soles or slippers on smooth basalt); carry reusable water bottles as daytime temperatures rise rapidly.
- **Official Source:** ASI Heritage Visitor Safety Norms (`asi.nic.in`)
- **Source Date:** `2026-11-07`

---

### Q8: Footwear & Shoes Policy Inside Caves
- **Question:** *What is the official rule regarding shoes and footwear inside the caves at Ajanta and Ellora? Do 40 students need to take off shoes at every cave?*
- **Category:** `teacher_shoes_policy`
- **User Intent:** Plan logistics for 40 students taking on and off shoes efficiently without losing footwear or delaying the schedule.
- **Ground Truth Answer:**
  - **Ajanta Caves:** Shoes are **permitted on outer walkways and rock terraces**, but must be removed before stepping onto carpeted or wooden walkways inside active shrine sanctums and painted caves (Caves 1, 2, 16, 17, 26) to preserve floors and ancient plaster.
  - **Ellora Caves:** Shoes may be worn throughout the general grounds and most rock-cut viharas, but must be removed when entering active sanctums (*garbhagrihas*) in Cave 16 (Kailasa) and Cave 32 (Indra Sabha).
  - **Teacher Recommendation:** Have students wear easily slip-on/slip-off footwear with socks, or carry designated shoe bags so groups do not crowd cave entrances.
- **Official Source:** ASI Monument Protection Guidelines (`asi.nic.in`)
- **Source Date:** `2026-11-07`

---

### Q9: Photography, Lighting & Flash Regulations
- **Question:** *Are school students allowed to take photos of the Ajanta paintings and Ellora sculptures with their mobile phones? What are the flash rules?*
- **Category:** `teacher_photography_rules`
- **User Intent:** Brief students on acceptable camera equipment and avoid fines from ASI monument security.
- **Ground Truth Answer:**
  - **Flash Photography:** **STRICTLY PROHIBITED** inside all painted caves at Ajanta (especially Caves 1, 2, 16, 17). Intense light and heat degrade 1,500-year-old organic pigments and natural binders.
  - **Tripods & Commercial Gear:** Commercial photography, video stands, and tripods require prior written permission and fees from the ASI Superintending Archaeologist; handheld smartphones for personal/educational non-commercial use are permitted.
  - **Ellora:** Still photography of sculptures without tripods is allowed across all open caves.
- **Official Source:** ASI Archaeological Conservation Norms (`asi.nic.in`)
- **Source Date:** `2026-11-07`

---

### Q10: Food, Water & Dining Facilities for School Groups
- **Question:** *Where can 40 students have lunch and refill drinking water near Ajanta and Ellora? Are lunchboxes allowed inside the caves?*
- **Category:** `teacher_food_logistics`
- **User Intent:** Organize mealtimes, hydration, and prevent littering or confrontation with security.
- **Ground Truth Answer:**
  - **Food Inside Caves:** **STRICTLY FORBIDDEN**. No outside food, snacks, or meal packets are allowed inside the cave interiors or on monument terraces to prevent rodent infestation and protect heritage surfaces.
  - **Water:** Sealed drinking water bottles are permitted; ASI provides filtered RO water coolers near ticket plazas and designated rest points.
  - **Dining Facilities:**
    - **Ajanta:** Government-run **MTDC Restaurant & T-Point Shopping Plaza** outside the security check / shuttle bus terminus offers seated group meals and packed lunch areas.
    - **Ellora:** Multiple MTDC and licensed cafeterias located outside the main entrance opposite Cave 16 and near the central parking area.
  - **Teacher Tip:** Schedule lunch between 12:30 PM and 1:30 PM at the MTDC complex outside the gates, then re-enter for the afternoon session.
- **Official Source:** ASI & MTDC Visitor Services Guide (`asi.nic.in`)
- **Source Date:** `2026-11-07`

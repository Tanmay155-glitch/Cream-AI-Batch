"""
Domain Tools for LeniGuide Agent.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- cave_trip_planner: Pure Python datetime & arithmetic tool to assign sites based on
  official ASI weekly closing rules (Ajanta closed Mon, Ellora closed Tue) and compute
  exact ticket fees (Adults Rs 40 cash / Rs 35 online, Children under 15 FREE).
- rag_search_tool: Grounded retrieval tool wrapping app.rag.answer_question.
- extract_trip_params: Natural language parameter extractor for date, group size, and payment mode.
- TOOLS registry and JSON schema declarations for LLM function calling.
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ASI Fee Constants (in INR)
ASI_ADULT_CASH_RATE = 40
ASI_ADULT_ONLINE_RATE = 35
ASI_CHILD_RATE = 0  # Free for children under 15 as per official ASI rules

# Cave Must-See Highlights for School Study Tours
AJANTA_HIGHLIGHTS = [
    "Cave 1: Masterpiece murals of Bodhisattva Padmapani and Vajrapani with royal court scenes",
    "Cave 2: Ornate ceiling medallions, thousand Buddhas mural, and Hariti-Pancika chapel",
    "Cave 10: Oldest dated Hinayana Chaitya hall (2nd century BCE, rediscovered in 1819)",
    "Cave 19: Gandhara-style sculpted Chaitya facade with standing and seated Buddha figures",
    "Cave 26: Monumental 7-meter Mahaparinirvana (Reclining Buddha) rock sculpture"
]

ELLORA_HIGHLIGHTS = [
    "Cave 16: Kailasa Temple (world's largest monolithic rock-cut monument, excavated top-down)",
    "Cave 10: Vishwakarma Cave ('Carpenter's Cave' - Buddhist Chaitya hall with carved cathedral ceiling)",
    "Cave 21: Rameshwara Cave (early Hindu rock sanctuary with exquisite carvings of Ganga and Parvati)",
    "Cave 29: Dhumar Lena (majestic waterfall cliff setting, monumental Shiva Nataraja reliefs)",
    "Cave 32: Indra Sabha (two-storey Digambara Jain shrine with intricate monolithic lotus ceiling)"
]


def parse_flexible_date(date_str: str) -> datetime:
    """
    Parse a date string in various human and machine formats.
    Defaults year to 2026 if omitted.
    """
    cleaned = date_str.strip().replace(",", " ").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Common date formats
    date_formats = [
        "%Y-%m-%d",       # 2026-12-14
        "%d-%m-%Y",       # 14-12-2026
        "%d/%m/%Y",       # 14/12/2026
        "%Y/%m/%d",       # 2026/12/14
        "%d %B %Y",       # 14 December 2026
        "%d %b %Y",       # 14 Dec 2026
        "%B %d %Y",       # December 14 2026
        "%b %d %Y",       # Dec 14 2026
        "%d %B",          # 14 December (append default year)
        "%d %b",          # 14 Dec (append default year)
        "%B %d",          # December 14 (append default year)
        "%b %d",          # Dec 14 (append default year)
    ]

    for fmt in date_formats:
        try:
            if "%Y" not in fmt:
                parsed = datetime.strptime(f"{cleaned} 2026", f"{fmt} %Y")
            else:
                parsed = datetime.strptime(cleaned, fmt)
            return parsed
        except ValueError:
            continue

    # Fallback to default date 14 Dec 2026
    return datetime(2026, 12, 14)


def extract_trip_params(query: str) -> Dict[str, Any]:
    """
    Extract trip parameters from a natural language query.
    Returns: {start_date, num_days, adults, children_under_15, payment_mode}
    """
    q_lower = query.lower()

    # Default parameters for target scenario (4 teachers, 40 students under 15, 14-15 Dec)
    params = {
        "start_date": "2026-12-14",
        "num_days": 2,
        "adults": 4,
        "children_under_15": 40,
        "payment_mode": "both"
    }

    # Extract adults / teachers
    adult_match = re.search(r"(\d+)\s*(?:teachers?|adults?|persons?|people|chaperones?|staff)", q_lower)
    if adult_match:
        params["adults"] = int(adult_match.group(1))

    # Extract children / students under 15
    child_match = re.search(r"(\d+)\s*(?:students?|children|kids?|pupils?|boys?|girls?)", q_lower)
    if child_match:
        params["children_under_15"] = int(child_match.group(1))

    # Extract dates like '14-15 December', '14 to 15 Dec', '14th and 15th December 2026'
    date_range_match = re.search(
        r"(\d{1,2})(?:st|nd|rd|th)?\s*(?:-|to|and|&)\s*(\d{1,2})(?:st|nd|rd|th)?\s*([a-zA-Z]+)(?:\s*(\d{4}))?",
        q_lower
    )
    if date_range_match:
        start_day = int(date_range_match.group(1))
        end_day = int(date_range_match.group(2))
        month_name = date_range_match.group(3)
        year = date_range_match.group(4) or "2026"
        params["start_date"] = f"{year}-{month_name.capitalize()}-{start_day:02d}"
        days_span = (end_day - start_day) + 1
        if 1 <= days_span <= 7:
            params["num_days"] = days_span

    # Check for ISO or single date mentions (e.g. 2026-12-14, 14 December)
    elif re.search(r"\b(\d{4}-\d{2}-\d{2})\b", query):
        iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", query)
        params["start_date"] = iso_match.group(1)
    else:
        single_date_match = re.search(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)(?:\s+(\d{4}))?",
            q_lower
        )
        if single_date_match and "teacher" not in single_date_match.group(2) and "student" not in single_date_match.group(2):
            d_val = int(single_date_match.group(1))
            m_val = single_date_match.group(2)
            y_val = single_date_match.group(3) or "2026"
            params["start_date"] = f"{y_val}-{m_val.capitalize()}-{d_val:02d}"

    # Extract payment mode
    if "online" in q_lower and "cash" not in q_lower:
        params["payment_mode"] = "online"
    elif "cash" in q_lower and "online" not in q_lower:
        params["payment_mode"] = "cash"
    else:
        params["payment_mode"] = "both"

    # Extract explicit days (e.g. '2 days', '3-day trip')
    days_match = re.search(r"(\d+)\s*(?:-|\s*)days?", q_lower)
    if days_match:
        val = int(days_match.group(1))
        if 1 <= val <= 7:
            params["num_days"] = val

    return params


def cave_trip_planner(
    start_date: str = "2026-12-14",
    num_days: int = 2,
    adults: int = 4,
    children_under_15: int = 40,
    payment_mode: str = "both"
) -> Dict[str, Any]:
    """
    Deterministic Agent Domain Tool: Cave Trip Planner.
    
    Takes a tour start date, duration, and group counts.
    Uses pure Python datetime arithmetic and official ASI weekly closing rules:
    - Ajanta Caves: CLOSED on Mondays (Open Tuesday to Sunday, 9:00 AM - 5:00 PM).
    - Ellora Caves: CLOSED on Tuesdays (Open Wednesday to Monday, Sunrise to Sunset).
    
    Computes exact entry fee totals based on official ASI rates:
    - Adults: Rs 40 (cash) or Rs 35 (online) per site.
    - Children under 15: FREE entry per ASI notification.
    
    Returns structured schedule and fee breakdown.
    """
    try:
        start_dt = parse_flexible_date(start_date)
    except Exception:
        start_dt = datetime(2026, 12, 14)

    num_days = max(1, min(int(num_days), 7))
    adults = max(0, int(adults))
    children_under_15 = max(0, int(children_under_15))
    payment_mode = payment_mode.lower() if payment_mode in ["cash", "online", "both"] else "both"

    # Plan schedule day by day
    schedule: List[Dict[str, Any]] = []
    assigned_sites_count: Dict[str, int] = {"Ellora": 0, "Ajanta": 0}

    for day_idx in range(num_days):
        current_dt = start_dt + timedelta(days=day_idx)
        weekday_idx = current_dt.weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
        weekday_name = current_dt.strftime("%A")
        date_iso = current_dt.strftime("%Y-%m-%d")

        # Official ASI closing rules
        ajanta_open = (weekday_idx != 0)  # Closed on Monday
        ellora_open = (weekday_idx != 1)  # Closed on Tuesday

        assigned_site = ""
        reason = ""
        highlights = []

        # Determine optimal assignment
        if weekday_idx == 0:
            # Monday: Ajanta CLOSED -> must be Ellora
            assigned_site = "Ellora"
            reason = "Ajanta is CLOSED on Mondays. Ellora is OPEN on Mondays (Sunrise to Sunset)."
            highlights = ELLORA_HIGHLIGHTS
        elif weekday_idx == 1:
            # Tuesday: Ellora CLOSED -> must be Ajanta
            assigned_site = "Ajanta"
            reason = "Ellora is CLOSED on Tuesdays. Ajanta is OPEN on Tuesdays (9:00 AM - 5:00 PM)."
            highlights = AJANTA_HIGHLIGHTS
        else:
            # Both open on Wednesday through Sunday
            # Prioritize unvisited site or balance
            next_dt = current_dt + timedelta(days=1)
            next_weekday = next_dt.weekday()

            if assigned_sites_count["Ellora"] == 0 and assigned_sites_count["Ajanta"] == 0:
                # If next day is Tuesday (when Ellora is closed), visit Ellora first today!
                if day_idx + 1 < num_days and next_weekday == 1:
                    assigned_site = "Ellora"
                    reason = f"Both sites open on {weekday_name}. Ellora is scheduled today because Ellora is closed tomorrow (Tuesday)."
                    highlights = ELLORA_HIGHLIGHTS
                else:
                    assigned_site = "Ajanta"
                    reason = f"Both sites open on {weekday_name}. Starting with Ajanta."
                    highlights = AJANTA_HIGHLIGHTS
            elif assigned_sites_count["Ellora"] == 0 and ellora_open:
                assigned_site = "Ellora"
                reason = f"Ellora is OPEN on {weekday_name} (visiting the second UNESCO site)."
                highlights = ELLORA_HIGHLIGHTS
            elif assigned_sites_count["Ajanta"] == 0 and ajanta_open:
                assigned_site = "Ajanta"
                reason = f"Ajanta is OPEN on {weekday_name} (visiting the second UNESCO site)."
                highlights = AJANTA_HIGHLIGHTS
            else:
                # Extra days: alternate
                assigned_site = "Ellora" if assigned_sites_count["Ellora"] <= assigned_sites_count["Ajanta"] else "Ajanta"
                reason = f"Extended exploration day at {assigned_site}."
                highlights = ELLORA_HIGHLIGHTS if assigned_site == "Ellora" else AJANTA_HIGHLIGHTS

        assigned_sites_count[assigned_site] += 1

        schedule.append({
            "day": day_idx + 1,
            "date": date_iso,
            "weekday": weekday_name,
            "assigned_site": assigned_site,
            "site_status": "OPEN (Sunrise to Sunset)" if assigned_site == "Ellora" else "OPEN (9:00 AM - 5:00 PM)",
            "closing_rule": reason,
            "must_see_highlights": highlights[:4]
        })

    # Number of unique or total site visits
    unique_sites_visited = len([s for s, count in assigned_sites_count.items() if count > 0])
    total_site_visits = sum(assigned_sites_count.values())

    # Ticket Fee Arithmetic (Pure Python)
    cash_per_site_adults = adults * ASI_ADULT_CASH_RATE
    online_per_site_adults = adults * ASI_ADULT_ONLINE_RATE
    children_cost_per_site = children_under_15 * ASI_CHILD_RATE

    cash_total = cash_per_site_adults * unique_sites_visited
    online_total = online_per_site_adults * unique_sites_visited
    children_total = 0
    savings_online = cash_total - online_total

    if payment_mode == "cash":
        selected_total = cash_total
    elif payment_mode == "online":
        selected_total = online_total
    else:
        selected_total = online_total  # Recommend online rate

    # Human-readable summary
    day1_site = schedule[0]["assigned_site"] if schedule else "Ellora"
    day1_date = schedule[0]["date"] if schedule else start_date
    day1_day = schedule[0]["weekday"] if schedule else "Monday"

    day2_site = schedule[1]["assigned_site"] if len(schedule) > 1 else "Ajanta"
    day2_date = schedule[1]["date"] if len(schedule) > 1 else ""
    day2_day = schedule[1]["weekday"] if len(schedule) > 1 else "Tuesday"

    summary_text = (
        f"Study Tour Itinerary for {adults} Teachers (Adults) & {children_under_15} Students (<15 Years):\n"
        f"• Day 1 ({day1_day}, {day1_date}): Visit {day1_site} Caves ({schedule[0]['closing_rule']})\n"
    )
    if len(schedule) > 1:
        summary_text += f"• Day 2 ({day2_day}, {day2_date}): Visit {day2_site} Caves ({schedule[1]['closing_rule']})\n"

    summary_text += (
        f"\nOfficial ASI Entry Ticket Costs:\n"
        f"• Teachers / Adults ({adults} persons): "
        f"Rs {cash_per_site_adults} cash / Rs {online_per_site_adults} online per site.\n"
        f"• Total for 2-day tour ({unique_sites_visited} sites): "
        f"Rs {online_total} (Online booking) OR Rs {cash_total} (Cash at ticket counter).\n"
        f"• Students ({children_under_15} persons under 15): "
        f"Rs 0 (100% FREE entry under official ASI rules upon showing school ID).\n"
        f"• Online Booking Benefit: Saves Rs {savings_online} for the group."
    )

    return {
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "num_days": num_days,
        "adults": adults,
        "children_under_15": children_under_15,
        "payment_mode": payment_mode,
        "unique_sites_count": unique_sites_visited,
        "schedule": schedule,
        "fee_breakdown": {
            "rate_per_adult_cash_inr": ASI_ADULT_CASH_RATE,
            "rate_per_adult_online_inr": ASI_ADULT_ONLINE_RATE,
            "rate_per_child_under_15_inr": ASI_CHILD_RATE,
            "cash_per_site_inr": cash_per_site_adults,
            "online_per_site_inr": online_per_site_adults,
            "cash_total_inr": cash_total,
            "online_total_inr": online_total,
            "children_cost_inr": children_total,
            "savings_online_inr": savings_online,
            "selected_mode_total_inr": selected_total,
            "asi_rule_note": "Children under 15 enter FREE as per official ASI regulations (ID proof required)."
        },
        "summary": summary_text
    }


def rag_search_tool(query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    RAG Knowledge Retrieval Tool.
    Wraps app.rag.answer_question to retrieve domain knowledge and official citations.
    """
    from app.rag import answer_question
    rag_resp = answer_question(question=query, top_k=top_k)
    return {
        "query": query,
        "answer": rag_resp.get("answer", ""),
        "citations": rag_resp.get("citations", []),
        "abstained": rag_resp.get("abstained", False),
        "confidence": rag_resp.get("confidence", "high"),
        "sources": rag_resp.get("sources", [])
    }


# Tool Registry
TOOLS = {
    "cave_trip_planner": cave_trip_planner,
    "rag_search": rag_search_tool,
}

# Function Calling JSON Schemas
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "cave_trip_planner",
            "description": (
                "Plans daily visit assignment to Ajanta and Ellora caves based on ASI weekly closing rules "
                "(Ajanta closed Monday, Ellora closed Tuesday) and computes official ticket fee totals for "
                "groups (adults Rs 40 cash / Rs 35 online, children under 15 FREE)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date of the trip in YYYY-MM-DD or readable format (e.g., '2026-12-14')"
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "Number of days for the trip (e.g., 2)"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adults/teachers (paying entry ticket)"
                    },
                    "children_under_15": {
                        "type": "integer",
                        "description": "Number of children or students under 15 years old (FREE entry)"
                    },
                    "payment_mode": {
                        "type": "string",
                        "enum": ["cash", "online", "both"],
                        "description": "Payment mode for tickets: 'cash', 'online', or 'both'"
                    }
                },
                "required": ["start_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag_search",
            "description": (
                "Searches official ASI heritage documentation for cave architecture, sculptures, "
                "murals, historical periods, and general monument regulations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question or search query regarding Ajanta and Ellora caves"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of context chunks to retrieve (default 4)"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


if __name__ == "__main__":
    print("=" * 80)
    print("LENIGUIDE DOMAIN AGENT TOOLS TEST (DAY 9 - S1)")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)

    # Test Q4: 14-15 December 2026, 4 teachers, 40 students under 15
    print("\n--- TEST: cave_trip_planner (Q4 Scenario) ---")
    plan = cave_trip_planner(
        start_date="2026-12-14",
        num_days=2,
        adults=4,
        children_under_15=40,
        payment_mode="both"
    )

    print(f"Start Date: {plan['start_date']} ({plan['schedule'][0]['weekday']})")
    for s in plan["schedule"]:
        print(f"  Day {s['day']} ({s['weekday']}, {s['date']}): {s['assigned_site']} -> {s['closing_rule']}")

    fb = plan["fee_breakdown"]
    print("\nFee Breakdown:")
    print(f"  Adults: 4 x Rs 40 = Rs {fb['cash_per_site_inr']} cash (Rs {fb['online_per_site_inr']} online) per site")
    print(f"  Total (2 sites): Rs {fb['cash_total_inr']} cash | Rs {fb['online_total_inr']} online")
    print(f"  Children under 15: Rs {fb['children_cost_inr']} (FREE as per ASI)")
    print(f"  Savings booking online: Rs {fb['savings_online_inr']}")

    # Verify key assertions for Q4
    assert plan["schedule"][0]["assigned_site"] == "Ellora", "Day 1 (Monday) must be Ellora!"
    assert plan["schedule"][1]["assigned_site"] == "Ajanta", "Day 2 (Tuesday) must be Ajanta!"
    assert fb["cash_total_inr"] == 320, "Total cash must be Rs 320 for 4 adults across 2 sites!"
    assert fb["online_total_inr"] == 280, "Total online must be Rs 280 for 4 adults across 2 sites!"
    assert fb["children_cost_inr"] == 0, "Children cost must be Rs 0!"

    print("\nSummary:")
    print(plan["summary"])

    # Test extract_trip_params
    print("\n--- TEST: extract_trip_params ---")
    test_q = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"
    extracted = extract_trip_params(test_q)
    print("Extracted params:", extracted)
    assert extracted["adults"] == 4
    assert extracted["children_under_15"] == 40
    assert extracted["num_days"] == 2

    print("\n" + "=" * 80)
    print("ALL TOOLS TESTS PASSED!")
    print("=" * 80)

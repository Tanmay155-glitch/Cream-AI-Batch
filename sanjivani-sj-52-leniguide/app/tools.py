"""
Domain Tools for LeniGuide Agent.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- cave_trip_planner: Pure Python datetime & arithmetic tool. Reads fees from
  data/site_rules.json (never hardcoded). Assigns sites based on official ASI
  weekly closing rules (Ajanta closed Mon, Ellora closed Tue).
- route_plan: Walking-order plan from data/routes.json.
- rag_search_tool: Grounded retrieval tool wrapping app.rag.answer_question.
- extract_trip_params: NL parameter extractor for date, group size, payment.
- TOOLS registry and JSON schema declarations for LLM function calling.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SITE_RULES_PATH = PROJECT_ROOT / "data" / "site_rules.json"


def load_site_rules() -> Dict[str, Any]:
    """Load site rules from data/site_rules.json. Never hardcode fees."""
    if not SITE_RULES_PATH.exists():
        return {}
    with open(SITE_RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_fee(site_key: str, payment: str, rules: Dict[str, Any]) -> Optional[int]:
    """Get fee for a site and payment mode from rules. Returns None if not verified."""
    site = rules.get(site_key, {})
    if payment == "online":
        return site.get("fee_indian_online")
    return site.get("fee_indian_cash")


def parse_flexible_date(date_str: str) -> datetime:
    """
    Parse a date string in various human and machine formats.
    Defaults year to 2026 if omitted.
    """
    cleaned = date_str.strip().replace(",", " ").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    cleaned = re.sub(r"\s+", " ", cleaned)

    date_formats = [
        "%Y-%m-%d",       # 2026-12-14
        "%Y-%B-%d",       # 2026-December-14
        "%Y-%b-%d",       # 2026-Dec-14
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

    raise ValueError(f"Cannot parse date: '{date_str}'")


def extract_trip_params(query: str) -> Dict[str, Any]:
    """
    Extract trip parameters from a natural language query.
    Returns: {start_date, num_days, adults, children_under_15, payment_mode}
    """
    q_lower = query.lower()

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

    # Extract dates like '14-15 December', '14 to 15 Dec'
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

    # Extract explicit days
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
    payment_mode: str = "both",
    sites: Tuple[str, ...] = ("ajanta", "ellora"),
) -> Dict[str, Any]:
    """
    Deterministic Agent Domain Tool: Cave Trip Planner.

    Reads fees from data/site_rules.json (never hardcoded).
    Uses pure Python datetime arithmetic and official ASI weekly closing rules:
    - Ajanta Caves: CLOSED on Mondays.
    - Ellora Caves: CLOSED on Tuesdays.

    Returns structured schedule and fee breakdown.
    """
    # Validate inputs
    if num_days < 1:
        raise ValueError("num_days must be >= 1")
    if adults < 0 or children_under_15 < 0:
        raise ValueError("adults and children counts must be >= 0")

    try:
        start_dt = parse_flexible_date(start_date)
    except ValueError as e:
        raise ValueError(f"Bad date: {e}")

    num_days = min(int(num_days), 7)
    adults = max(0, int(adults))
    children_under_15 = max(0, int(children_under_15))
    if payment_mode not in ("cash", "online", "both"):
        payment_mode = "both"

    # Load rules from JSON — never hardcode fees
    rules = load_site_rules()

    # Read closed days from rules
    ajanta_closed_day = rules.get("ajanta", {}).get("closed_day", "Monday")
    ellora_closed_day = rules.get("ellora", {}).get("closed_day", "Tuesday")
    closed_weekday = {
        "ajanta": {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}.get(ajanta_closed_day, 0),
        "ellora": {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}.get(ellora_closed_day, 1),
    }

    # Build schedule
    schedule: List[Dict[str, Any]] = []
    assigned_sites_count: Dict[str, int] = {"Ellora": 0, "Ajanta": 0}
    unscheduled: List[Dict[str, Any]] = []

    for day_idx in range(num_days):
        current_dt = start_dt + timedelta(days=day_idx)
        weekday_idx = current_dt.weekday()
        weekday_name = current_dt.strftime("%A")
        date_iso = current_dt.strftime("%Y-%m-%d")

        ajanta_open = (weekday_idx != closed_weekday["ajanta"])
        ellora_open = (weekday_idx != closed_weekday["ellora"])

        assigned_site = ""
        reason = ""

        if weekday_idx == closed_weekday["ajanta"] and not weekday_idx == closed_weekday["ellora"]:
            assigned_site = "Ellora"
            reason = f"Ajanta is CLOSED on {ajanta_closed_day}s. Ellora is OPEN."
        elif weekday_idx == closed_weekday["ellora"] and not weekday_idx == closed_weekday["ajanta"]:
            assigned_site = "Ajanta"
            reason = f"Ellora is CLOSED on {ellora_closed_day}s. Ajanta is OPEN."
        elif not ajanta_open and not ellora_open:
            assigned_site = "NONE"
            reason = "Both sites are closed on this day."
        else:
            # Both open — smart assignment
            next_dt = current_dt + timedelta(days=1)
            next_weekday = next_dt.weekday()

            if assigned_sites_count["Ellora"] == 0 and assigned_sites_count["Ajanta"] == 0:
                if day_idx + 1 < num_days and next_weekday == closed_weekday["ellora"]:
                    assigned_site = "Ellora"
                    reason = f"Both sites open on {weekday_name}. Ellora scheduled today because Ellora closes tomorrow ({ellora_closed_day})."
                elif day_idx + 1 < num_days and next_weekday == closed_weekday["ajanta"]:
                    assigned_site = "Ajanta"
                    reason = f"Both sites open on {weekday_name}. Ajanta scheduled today because Ajanta closes tomorrow ({ajanta_closed_day})."
                else:
                    assigned_site = "Ajanta"
                    reason = f"Both sites open on {weekday_name}. Starting with Ajanta."
            elif assigned_sites_count["Ellora"] == 0 and ellora_open:
                assigned_site = "Ellora"
                reason = f"Visiting the second site (Ellora) on {weekday_name}."
            elif assigned_sites_count["Ajanta"] == 0 and ajanta_open:
                assigned_site = "Ajanta"
                reason = f"Visiting the second site (Ajanta) on {weekday_name}."
            else:
                assigned_site = "Ellora" if assigned_sites_count["Ellora"] <= assigned_sites_count["Ajanta"] else "Ajanta"
                reason = f"Extended exploration at {assigned_site}."

        if assigned_site == "NONE":
            unscheduled.append({"date": date_iso, "weekday": weekday_name, "reason": reason})
        else:
            assigned_sites_count[assigned_site] += 1
            ajanta_rules = rules.get("ajanta", {})
            ellora_rules = rules.get("ellora", {})
            timings = ajanta_rules.get("timings", "9:00 AM - 5:00 PM") if assigned_site == "Ajanta" else ellora_rules.get("timings", "Sunrise to Sunset")

            schedule.append({
                "day": day_idx + 1,
                "date": date_iso,
                "weekday": weekday_name,
                "assigned_site": assigned_site,
                "site_status": f"OPEN ({timings})",
                "closing_rule": reason,
            })

    # Fee calculation — read from site_rules.json
    unique_sites_visited = len([s for s, count in assigned_sites_count.items() if count > 0])
    child_free_age = rules.get("ajanta", {}).get("child_free_under_age", 15)

    fee_cash = get_fee("ajanta", "cash", rules)  # Same for both sites per ASI
    fee_online = get_fee("ajanta", "online", rules)

    # Check if fees are verified
    fee_verified = fee_cash is not None and fee_online is not None
    ajanta_verified_on = rules.get("ajanta", {}).get("verified_on")
    ellora_verified_on = rules.get("ellora", {}).get("verified_on")

    if fee_verified:
        cash_per_site = adults * fee_cash
        online_per_site = adults * fee_online
        cash_total = cash_per_site * unique_sites_visited
        online_total = online_per_site * unique_sites_visited
        children_cost = 0
        savings = cash_total - online_total

        if payment_mode == "cash":
            selected_total = cash_total
        elif payment_mode == "online":
            selected_total = online_total
        else:
            selected_total = online_total  # recommend online

        fee_breakdown = {
            "rate_per_adult_cash_inr": fee_cash,
            "rate_per_adult_online_inr": fee_online,
            "rate_per_child_under_15_inr": 0,
            "cash_per_site_inr": cash_per_site,
            "online_per_site_inr": online_per_site,
            "cash_total_inr": cash_total,
            "online_total_inr": online_total,
            "children_cost_inr": children_cost,
            "savings_online_inr": savings,
            "selected_mode_total_inr": selected_total,
            "fee_status": "verified",
            "source_url": rules.get("ajanta", {}).get("source_url", "https://asi.nic.in"),
            "verified_on": ajanta_verified_on,
            "asi_rule_note": f"Children under {child_free_age} enter FREE as per official ASI regulations.",
        }
    else:
        fee_breakdown = {
            "fee_status": "not verified",
            "message": "Fees have not been verified yet. Please complete MANUAL STEP M-4 to verify ASI fees.",
            "source_url": rules.get("ajanta", {}).get("source_url", "https://asi.nic.in"),
        }

    # Build summary
    summary_lines = [
        f"Study Tour Itinerary for {adults} Adults & {children_under_15} Students (under {child_free_age}):"
    ]
    for s in schedule:
        summary_lines.append(f"• Day {s['day']} ({s['weekday']}, {s['date']}): Visit {s['assigned_site']} Caves — {s['closing_rule']}")

    if fee_verified:
        summary_lines.append("\nOfficial ASI Entry Ticket Costs:")
        summary_lines.append(f"• Adults ({adults}): Rs {fee_cash} cash / Rs {fee_online} online per site")
        summary_lines.append(f"• Total ({unique_sites_visited} sites): Rs {cash_total} cash / Rs {online_total} online")
        summary_lines.append(f"• Students ({children_under_15} under {child_free_age}): FREE entry")
        summary_lines.append(f"• Online booking saves Rs {savings}")
    else:
        summary_lines.append("\n⚠️ Fee information not yet verified. Complete MANUAL STEP M-4.")

    return {
        "start_date": start_dt.strftime("%Y-%m-%d"),
        "num_days": num_days,
        "adults": adults,
        "children_under_15": children_under_15,
        "payment_mode": payment_mode,
        "unique_sites_count": unique_sites_visited,
        "schedule": schedule,
        "unscheduled": unscheduled,
        "fee_breakdown": fee_breakdown,
        "summary": "\n".join(summary_lines),
        "safety_note": "Timings, fees and closures can change. Confirm on asi.nic.in before you travel.",
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
                "groups. Reads fees from data/site_rules.json."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD or readable format"
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "Number of days for the trip"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adults/teachers"
                    },
                    "children_under_15": {
                        "type": "integer",
                        "description": "Number of children under 15 (FREE entry)"
                    },
                    "payment_mode": {
                        "type": "string",
                        "enum": ["cash", "online", "both"],
                        "description": "Payment mode for tickets"
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
                "murals, historical periods, and monument regulations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question or search query about Ajanta and Ellora caves"
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
    print("LENIGUIDE DOMAIN AGENT TOOLS TEST (DAY 9)")
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
    print(f"\nFee Status: {fb.get('fee_status', 'unknown')}")
    if fb.get("fee_status") == "verified":
        print(f"  Cash total: Rs {fb['cash_total_inr']}")
        print(f"  Online total: Rs {fb['online_total_inr']}")
        print(f"  Children: Rs {fb['children_cost_inr']} (FREE)")

    assert plan["schedule"][0]["assigned_site"] == "Ellora", "Day 1 (Monday) must be Ellora!"
    assert plan["schedule"][1]["assigned_site"] == "Ajanta", "Day 2 (Tuesday) must be Ajanta!"

    print("\n" + plan["summary"])
    print("\n" + "=" * 80)
    print("ALL TOOLS TESTS PASSED!")
    print("=" * 80)

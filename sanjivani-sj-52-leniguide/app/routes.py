"""
Route planning module for LeniGuide.
Builds walking-order plans from data/routes.json, ensuring at least one cave
per religion for Ellora and respecting time budgets.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROUTES_PATH = PROJECT_ROOT / "data" / "routes.json"


def load_routes() -> Dict[str, Any]:
    """Load route data from data/routes.json."""
    if not ROUTES_PATH.exists():
        return {}
    with open(ROUTES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_route_strip(site: str) -> Dict[str, Any]:
    """
    Get the must-see route strip for a site.
    Returns walking-order list with stars, minutes, and totals.
    """
    routes = load_routes()
    site_key = site.lower()

    if site_key not in routes:
        return {"site": site, "caves": [], "total_minutes": 0, "starred_count": 0, "starred_minutes": 0, "fits_3_hours": False}

    site_data = routes[site_key]
    caves = site_data.get("walking_order", [])

    total_minutes = sum(c.get("minutes", 0) for c in caves)
    starred = [c for c in caves if c.get("star", False)]
    starred_minutes = sum(c.get("minutes", 0) for c in starred)
    starred_count = len(starred)

    return {
        "site": site.capitalize(),
        "description": site_data.get("description", ""),
        "caves": caves,
        "total_minutes": total_minutes,
        "starred_count": starred_count,
        "starred_minutes": starred_minutes,
        "fits_3_hours": starred_minutes <= 180,
        "fits_4_hours": total_minutes <= 240,
        "notes": site_data.get("notes", ""),
    }


def route_plan(site: str, minutes: int = 180) -> Dict[str, Any]:
    """
    Build a time-budgeted route plan from data/routes.json.

    For Ellora, ensures at least one cave per religion (Buddhist, Hindu, Jain).
    Returns caves in walking order that fit within the time budget.

    Args:
        site: "ajanta" or "ellora"
        minutes: total time budget in minutes (default 180 = 3 hours)

    Returns:
        Dict with planned caves, total time, and religion coverage.
    """
    routes = load_routes()
    site_key = site.lower()

    if site_key not in routes:
        return {
            "site": site,
            "error": f"No route data for site '{site}'",
            "planned_caves": [],
            "total_minutes": 0,
        }

    all_caves = routes[site_key].get("walking_order", [])
    if not all_caves:
        return {
            "site": site,
            "planned_caves": [],
            "total_minutes": 0,
        }

    planned: List[Dict[str, Any]] = []
    used_time = 0
    religions_covered: set = set()

    if site_key == "ellora":
        # Ensure at least one cave per religion: pick the starred one (or first) for each
        required_religions = {"Buddhist", "Hindu", "Jain"}
        religion_picks: Dict[str, Dict[str, Any]] = {}

        for cave in all_caves:
            rel = cave.get("religion", "")
            if rel in required_religions and rel not in religion_picks:
                # Prefer starred caves
                if cave.get("star", False) or rel not in religion_picks:
                    religion_picks[rel] = cave

        # Add required caves first (in walking order)
        for cave in all_caves:
            rel = cave.get("religion", "")
            if rel in religion_picks and religion_picks[rel] is cave:
                cave_time = cave.get("minutes", 0)
                if used_time + cave_time <= minutes:
                    planned.append(cave)
                    used_time += cave_time
                    religions_covered.add(rel)
                    del religion_picks[rel]

        # Fill remaining time with other caves in walking order
        for cave in all_caves:
            if cave in planned:
                continue
            cave_time = cave.get("minutes", 0)
            if used_time + cave_time <= minutes:
                planned.append(cave)
                used_time += cave_time
                religions_covered.add(cave.get("religion", ""))
    else:
        # Ajanta: simply fill in walking order
        for cave in all_caves:
            cave_time = cave.get("minutes", 0)
            if used_time + cave_time <= minutes:
                planned.append(cave)
                used_time += cave_time
                religions_covered.add(cave.get("religion", ""))

    # Sort planned by walking order
    planned.sort(key=lambda c: c.get("order", 999))

    return {
        "site": site.capitalize(),
        "time_budget_minutes": minutes,
        "planned_caves": planned,
        "total_minutes": used_time,
        "remaining_minutes": minutes - used_time,
        "caves_count": len(planned),
        "religions_covered": sorted(religions_covered),
        "all_religions_covered": religions_covered >= {"Buddhist", "Hindu", "Jain"} if site_key == "ellora" else True,
    }


if __name__ == "__main__":
    print("=== Route Strip: Ajanta ===")
    strip = get_route_strip("ajanta")
    print(f"  Total caves: {len(strip['caves'])}, Stars: {strip['starred_count']}")
    print(f"  Total minutes: {strip['total_minutes']}, Starred minutes: {strip['starred_minutes']}")
    print(f"  Fits 3 hours (starred): {strip['fits_3_hours']}")

    print("\n=== Route Strip: Ellora ===")
    strip = get_route_strip("ellora")
    print(f"  Total caves: {len(strip['caves'])}, Stars: {strip['starred_count']}")
    print(f"  Total minutes: {strip['total_minutes']}, Starred minutes: {strip['starred_minutes']}")
    print(f"  Fits 3 hours (starred): {strip['fits_3_hours']}")

    print("\n=== 3-Hour Ellora Plan ===")
    plan = route_plan("ellora", 180)
    for c in plan["planned_caves"]:
        star = "⭐" if c.get("star") else "  "
        print(f"  {star} Cave {c['cave_no']} ({c['religion']}) — {c['minutes']} min — {c['reason']}")
    print(f"  Total: {plan['total_minutes']} min | Religions: {plan['religions_covered']}")

"""
LeniGuide Streamlit Chat UI with Must-See Route Strip & Feedback.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Day 10 — Session 1 & 2: Streamlit UI / Checkpoint 2
Signature Feature: "Must-see route" strip for each site — caves in walking
order, starred Top-5, estimated minutes per cave so a group fits the visit
into 3-4 hours.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.json"


# ============================================================================
# 1. MUST-SEE ROUTE DATA
# ============================================================================

AJANTA_ROUTE = [
    {"cave": "Cave 1",  "star": True,  "mins": 25, "religion": "Buddhist", "period": "Mahayana", "highlight": "Padmapani & Vajrapani Bodhisattva murals, royal court scenes"},
    {"cave": "Cave 2",  "star": True,  "mins": 20, "religion": "Buddhist", "period": "Mahayana", "highlight": "Miracle of Sravasti painting & ornate ceiling mandalas"},
    {"cave": "Cave 9",  "star": False, "mins": 15, "religion": "Buddhist", "period": "Hinayana", "highlight": "Early Chaitya prayer hall with octagonal columns"},
    {"cave": "Cave 10", "star": False, "mins": 15, "religion": "Buddhist", "period": "Hinayana", "highlight": "Oldest Chaitya hall (2nd c. BCE, 1819 John Smith rediscovery)"},
    {"cave": "Cave 16", "star": True,  "mins": 25, "religion": "Buddhist", "period": "Vakataka", "highlight": "'Dying Princess' mural & Varahadeva donor inscription"},
    {"cave": "Cave 17", "star": True,  "mins": 30, "religion": "Buddhist", "period": "Vakataka", "highlight": "Best-preserved Jataka murals & Wheel of Life ceiling"},
    {"cave": "Cave 19", "star": True,  "mins": 25, "religion": "Buddhist", "period": "Mahayana", "highlight": "'Sculptured jewel' Chaitya facade with standing Buddha"},
    {"cave": "Cave 26", "star": False, "mins": 25, "religion": "Buddhist", "period": "Mahayana", "highlight": "24-ft Mahaparinirvana (Reclining Buddha) rock sculpture"},
]

ELLORA_ROUTE = [
    {"cave": "Cave 5",  "star": False, "mins": 15, "religion": "Buddhist", "period": "",     "highlight": "Maharwada monastic hall with parallel stone benches"},
    {"cave": "Cave 10", "star": True,  "mins": 20, "religion": "Buddhist", "period": "",     "highlight": "Vishwakarma (Carpenter's Cave) ribbed cathedral ceiling"},
    {"cave": "Cave 12", "star": False, "mins": 20, "religion": "Buddhist", "period": "",     "highlight": "Teen Tal — three-storey monastery with seated Buddhas"},
    {"cave": "Cave 14", "star": False, "mins": 15, "religion": "Hindu",    "period": "",     "highlight": "Ravan ki Khai sculptural panels of Vishnu & Shiva"},
    {"cave": "Cave 15", "star": False, "mins": 15, "religion": "Hindu",    "period": "",     "highlight": "Dashavatara: Narasimha slaying Hiranyakashipu relief"},
    {"cave": "Cave 16", "star": True,  "mins": 50, "religion": "Hindu",    "period": "",     "highlight": "Kailasa Temple — world's largest monolithic rock-cut monument"},
    {"cave": "Cave 21", "star": True,  "mins": 15, "religion": "Hindu",    "period": "",     "highlight": "Rameshwara Cave & River Goddess Ganga bracket figure"},
    {"cave": "Cave 29", "star": True,  "mins": 20, "religion": "Hindu",    "period": "",     "highlight": "Dhumar Lena cruciform Shiva cave near waterfall cliff"},
    {"cave": "Cave 30", "star": False, "mins": 15, "religion": "Jain",     "period": "",     "highlight": "Chhota Kailasa monolithic shrine (smaller Kailasa echo)"},
    {"cave": "Cave 32", "star": True,  "mins": 20, "religion": "Jain",     "period": "",     "highlight": "Indra Sabha double-storey temple (Matanga & Ambika)"},
    {"cave": "Cave 33", "star": False, "mins": 15, "religion": "Jain",     "period": "",     "highlight": "Jagannatha Sabha & Parshvanatha sculptures"},
    {"cave": "Cave 34", "star": False, "mins": 10, "religion": "Jain",     "period": "",     "highlight": "Intimate Parshvanatha & Gommateshwara shrine"},
]

RELIGION_COLORS = {
    "Buddhist": "#FF9800",
    "Hindu":    "#2196F3",
    "Jain":     "#4CAF50",
}


# ============================================================================
# 2. FEEDBACK HELPERS
# ============================================================================

def load_feedback() -> List[Dict[str, Any]]:
    if FEEDBACK_FILE.exists():
        try:
            return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_feedback(question: str, answer: str, rating: str, mode: str):
    fb = load_feedback()
    fb.append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer[:500],
        "rating": rating,
        "mode": mode
    })
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_FILE.write_text(json.dumps(fb, indent=2, ensure_ascii=False), encoding="utf-8")


def feedback_counts() -> Dict[str, int]:
    fb = load_feedback()
    return {
        "up": sum(1 for r in fb if r.get("rating") == "up"),
        "down": sum(1 for r in fb if r.get("rating") == "down"),
    }


# ============================================================================
# 3. BACKEND CALL HELPERS (HTTP + Direct Fallback)
# ============================================================================

def call_backend(question: str, mode: str, backend_url: str,
                 thread_id: str = "streamlit-session",
                 approved: Optional[bool] = None,
                 require_approval: bool = False) -> Dict[str, Any]:
    """Call FastAPI backend or fall back to direct imports."""
    import requests as req_lib

    if mode == "agent":
        endpoint = f"{backend_url}/agent"
        payload = {
            "question": question,
            "thread_id": thread_id,
            "approved": approved,
            "require_approval": require_approval
        }
    else:
        endpoint = f"{backend_url}/ask"
        payload = {"question": question}

    try:
        resp = req_lib.post(endpoint, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Direct import fallback (no server needed)
    try:
        if mode == "agent":
            from app.graph import run_graph_agent
            return run_graph_agent(
                question=question,
                thread_id=thread_id,
                approved=approved,
                require_approval=require_approval
            )
        else:
            from app.rag import answer_question
            return answer_question(question=question)
    except Exception as e:
        return {
            "answer": f"Backend unavailable and direct fallback failed: {e}",
            "citations": [],
            "abstained": False,
            "tools_used": [],
            "approval_status": "not_required"
        }


# ============================================================================
# 4. ROUTE STRIP RENDERING
# ============================================================================

def render_route_strip(route: List[Dict], site_name: str, show_all: bool):
    """Render the Must-See Route Strip for a site."""
    display = route if show_all else [c for c in route if c["star"]]
    total_mins = sum(c["mins"] for c in display)
    hrs = total_mins // 60
    mins = total_mins % 60

    st.markdown(
        f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);padding:12px 16px;"
        f"border-radius:10px;margin-bottom:8px;'>"
        f"<span style='color:#e94560;font-weight:700;font-size:1.1em;'>"
        f"🗺️ {site_name} Walking Route</span>"
        f"<span style='float:right;color:#0f3460;background:#e2e2e2;padding:2px 10px;"
        f"border-radius:12px;font-size:0.85em;font-weight:600;'>"
        f"⏱️ {total_mins} min ({hrs}h {mins}m) · {len(display)} caves</span></div>",
        unsafe_allow_html=True
    )

    # Render caves in a scrollable row
    cols = st.columns(min(len(display), 6))
    cumulative = 0
    for i, cave in enumerate(display):
        cumulative += cave["mins"]
        col = cols[i % len(cols)]
        color = RELIGION_COLORS.get(cave["religion"], "#999")
        star_badge = "⭐ Top 5" if cave["star"] else ""
        with col:
            st.markdown(
                f"<div style='background:#0f3460;border-left:4px solid {color};"
                f"border-radius:8px;padding:10px;margin:4px 0;min-height:155px;'>"
                f"<div style='font-size:1.05em;font-weight:700;color:#e94560;'>"
                f"{cave['cave']}"
                f"{'  <span style=\"background:gold;color:#333;padding:1px 6px;border-radius:8px;font-size:0.7em;\">' + star_badge + '</span>' if star_badge else ''}"
                f"</div>"
                f"<div style='color:{color};font-size:0.78em;margin:3px 0;'>"
                f"{cave['religion']}{(' · ' + cave['period']) if cave['period'] else ''}</div>"
                f"<div style='color:#ccc;font-size:0.75em;line-height:1.3;margin:4px 0;'>"
                f"{cave['highlight'][:80]}{'…' if len(cave['highlight'])>80 else ''}</div>"
                f"<div style='color:#aaa;font-size:0.78em;margin-top:6px;'>"
                f"⏱️ {cave['mins']} min · Σ {cumulative} min</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Second row if more than 6 caves
    if len(display) > 6:
        cols2 = st.columns(min(len(display) - 6, 6))
        for i, cave in enumerate(display[6:]):
            col = cols2[i % len(cols2)]
            color = RELIGION_COLORS.get(cave["religion"], "#999")
            star_badge = "⭐ Top 5" if cave["star"] else ""
            # cumulative continues
            with col:
                st.markdown(
                    f"<div style='background:#0f3460;border-left:4px solid {color};"
                    f"border-radius:8px;padding:10px;margin:4px 0;min-height:155px;'>"
                    f"<div style='font-size:1.05em;font-weight:700;color:#e94560;'>"
                    f"{cave['cave']}"
                    f"{'  <span style=\"background:gold;color:#333;padding:1px 6px;border-radius:8px;font-size:0.7em;\">' + star_badge + '</span>' if star_badge else ''}"
                    f"</div>"
                    f"<div style='color:{color};font-size:0.78em;margin:3px 0;'>"
                    f"{cave['religion']}{(' · ' + cave['period']) if cave['period'] else ''}</div>"
                    f"<div style='color:#ccc;font-size:0.75em;line-height:1.3;margin:4px 0;'>"
                    f"{cave['highlight'][:80]}{'…' if len(cave['highlight'])>80 else ''}</div>"
                    f"<div style='color:#aaa;font-size:0.78em;margin-top:6px;'>"
                    f"⏱️ {cave['mins']} min</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )


# ============================================================================
# 5. MAIN STREAMLIT APPLICATION
# ============================================================================

def main():
    st.set_page_config(
        page_title="LeniGuide — Ajanta & Ellora Study Tour Planner",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("## 🏛️ LeniGuide")
        st.caption("Ajanta & Ellora UNESCO Heritage Guide")
        st.caption("Student: Tanmay Subhash Gawali (SJ-52)")
        st.divider()

        # Mode selector
        mode = st.radio(
            "🤖 Assistant Mode",
            ["Agent Mode (/agent — RAG + Trip Planner Tool)",
             "RAG Mode (/ask — Grounded Cave Q&A)"],
            index=0
        )
        active_mode = "agent" if "Agent" in mode else "rag"

        # Backend URL
        backend_url = st.text_input(
            "🔗 Backend URL",
            value="http://127.0.0.1:8000",
            help="FastAPI server URL. Falls back to direct import if server is not running."
        )

        st.divider()

        # Sample Questions
        st.markdown("### 📝 Quick Test Questions")
        sample_qs = [
            ("Q1: Weekly closures", "Which day is Ellora closed? And Ajanta?"),
            ("Q2: Kailasa temple", "What is special about the Kailasa temple in Ellora cave 16?"),
            ("Q3: Best paintings", "Which caves in Ajanta have the best paintings?"),
            ("Q4: 14-15 Dec trip plan", "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"),
            ("Q5: 3-hr Ellora plan", "Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves."),
            ("Q6: Guardrail test", "How many tourists visited Ajanta caves last Diwali?"),
        ]
        for label, q in sample_qs:
            if st.button(label, key=f"sq_{label}", use_container_width=True):
                st.session_state.pending_question = q

        st.divider()

        # Group Trip Calculator
        st.markdown("### 🧮 Group Trip Calculator")
        calc_date = st.date_input("Start Date", value=datetime(2026, 12, 14))
        calc_days = st.number_input("Days", min_value=1, max_value=7, value=2)
        calc_adults = st.number_input("Adults/Teachers", min_value=0, max_value=200, value=4)
        calc_students = st.number_input("Students under 15", min_value=0, max_value=500, value=40)
        calc_payment = st.selectbox("Payment Mode", ["both", "cash", "online"])
        calc_approval = st.checkbox("🔒 Require approval before confirming", value=False)

        if st.button("🗓️ Plan This Trip", use_container_width=True):
            q_text = (
                f"We are {calc_adults} teachers and {calc_students} students under 15 "
                f"coming on {calc_date.strftime('%d %B %Y')} for {calc_days} days. "
                f"Which site on which day, and total ticket cost?"
            )
            st.session_state.pending_question = q_text
            st.session_state.calc_approval = calc_approval

        st.divider()

        # Feedback Counter
        fc = feedback_counts()
        st.markdown("### 📊 Feedback Stats")
        c1, c2 = st.columns(2)
        c1.metric("👍 Helpful", fc["up"])
        c2.metric("👎 Improve", fc["down"])

        st.divider()
        st.markdown(
            "<div style='text-align:center;color:#888;font-size:0.75em;'>"
            "LeniGuide v1.4 · Day 10 · SJ-52<br>"
            "Official ASI data only · asi.nic.in</div>",
            unsafe_allow_html=True
        )

    # --- MAIN AREA ---
    st.title("🏛️ LeniGuide — Ajanta & Ellora Study Tour Planner")
    st.caption(
        "Cave-by-cave guide with official ASI data, AI-powered Q&A, trip planner & ticket calculator  ·  "
        "Student: Tanmay Subhash Gawali (SJ-52)"
    )

    # --- MUST-SEE ROUTE STRIP (Signature Feature) ---
    st.markdown("---")
    route_tab1, route_tab2 = st.tabs(["🕉️ Ajanta Caves Route", "🛕 Ellora Caves Route"])

    with route_tab1:
        filter_ajanta = st.toggle("Show only ⭐ Top 5 Must-See", value=False, key="filter_ajanta")
        render_route_strip(AJANTA_ROUTE, "Ajanta Caves", show_all=not filter_ajanta)
        total_all = sum(c["mins"] for c in AJANTA_ROUTE)
        total_top5 = sum(c["mins"] for c in AJANTA_ROUTE if c["star"])
        st.info(
            f"📏 **Full Route:** {len(AJANTA_ROUTE)} caves · {total_all} mins ({total_all/60:.1f} hrs)  |  "
            f"**Top-5 Express:** {sum(1 for c in AJANTA_ROUTE if c['star'])} caves · {total_top5} mins ({total_top5/60:.1f} hrs)  |  "
            f"🕐 Open 9 AM – 5 PM · Closed Mondays"
        )

    with route_tab2:
        filter_ellora = st.toggle("Show only ⭐ Top 5 Must-See", value=False, key="filter_ellora")
        render_route_strip(ELLORA_ROUTE, "Ellora Caves", show_all=not filter_ellora)
        total_all_e = sum(c["mins"] for c in ELLORA_ROUTE)
        total_top5_e = sum(c["mins"] for c in ELLORA_ROUTE if c["star"])
        st.info(
            f"📏 **Full Route:** {len(ELLORA_ROUTE)} caves · {total_all_e} mins ({total_all_e/60:.1f} hrs)  |  "
            f"**Top-5 Express:** {sum(1 for c in ELLORA_ROUTE if c['star'])} caves · {total_top5_e} mins ({total_top5_e/60:.1f} hrs)  |  "
            f"🌅 Open Sunrise – Sunset · Closed Tuesdays"
        )

    # --- CHAT INTERFACE ---
    st.markdown("---")
    st.markdown("### 💬 Ask LeniGuide")

    # Render chat history
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                meta = msg.get("meta", {})

                # Citations expander
                citations = meta.get("citations", [])
                if citations:
                    with st.expander(f"📚 Official ASI Citations & Sources ({len(citations)})"):
                        for ci, c in enumerate(citations):
                            source_url = c.get("source", "")
                            title = c.get("title", "ASI Record")
                            site = c.get("site", "")
                            cave_no = c.get("cave_no", "")
                            score = c.get("score", 0)
                            st.markdown(
                                f"**{ci+1}. {title}**  \n"
                                f"Site: `{site}` · Cave: `{cave_no}` · "
                                f"Score: `{score:.4f}`  \n"
                                f"🔗 [{source_url}]({source_url})"
                            )

                # Agent tool output expander
                tool_output = meta.get("tool_output")
                if tool_output and isinstance(tool_output, dict) and "schedule" in tool_output:
                    with st.expander("🗓️ Agent Trip Planner Output"):
                        for s in tool_output.get("schedule", []):
                            st.markdown(
                                f"**Day {s.get('day')}: {s.get('weekday')}, {s.get('date')}** → "
                                f"Visit **{s.get('assigned_site')}** ({s.get('site_status', 'OPEN')})  \n"
                                f"*{s.get('closing_rule', '')}*"
                            )
                        fees = tool_output.get("fee_breakdown", {})
                        if fees:
                            st.markdown("---")
                            fc1, fc2, fc3 = st.columns(3)
                            fc1.metric("💰 Cash Total", f"Rs {fees.get('cash_total_inr', 0)}")
                            fc2.metric("💳 Online Total", f"Rs {fees.get('online_total_inr', 0)}")
                            fc3.metric("🎒 Students (<15)", f"Rs {fees.get('children_cost_inr', 0)} FREE")

                # Thumbs up / down
                fb_col1, fb_col2, _ = st.columns([1, 1, 6])
                q_text = meta.get("question", "")
                a_text = msg["content"][:300]
                m = meta.get("mode", "rag")
                with fb_col1:
                    if st.button("👍 Helpful", key=f"up_{i}", use_container_width=True):
                        save_feedback(q_text, a_text, "up", m)
                        st.toast("✅ Feedback saved to data/feedback.json!")
                with fb_col2:
                    if st.button("👎 Improve", key=f"dn_{i}", use_container_width=True):
                        save_feedback(q_text, a_text, "down", m)
                        st.toast("✅ Feedback saved to data/feedback.json!")

    # Handle pending question from sidebar buttons
    pending = st.session_state.pop("pending_question", None)
    calc_appr = st.session_state.pop("calc_approval", False)

    # Chat input
    user_input = st.chat_input("Ask about Ajanta & Ellora caves, plan a study tour, or check ticket costs…")
    question = pending or user_input

    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching official ASI records…"):
                require_approval = calc_appr if pending else False
                result = call_backend(
                    question=question,
                    mode=active_mode,
                    backend_url=backend_url,
                    approved=None if require_approval else True,
                    require_approval=require_approval
                )

            answer = result.get("answer", "No response received.")
            st.markdown(answer)

            meta = {
                "question": question,
                "mode": active_mode,
                "citations": result.get("citations", result.get("sources", [])),
                "tool_output": result.get("tool_output"),
                "tools_used": result.get("tools_used", []),
                "approval_status": result.get("approval_status", "not_required"),
                "abstained": result.get("abstained", False),
            }

            # Show citations inline
            citations = meta["citations"]
            if citations and isinstance(citations, list) and len(citations) > 0:
                with st.expander(f"📚 Official ASI Citations & Sources ({len(citations)})"):
                    for ci, c in enumerate(citations):
                        if isinstance(c, dict):
                            source_url = c.get("source", "")
                            title = c.get("title", "ASI Record")
                            site = c.get("site", "")
                            cave_no = c.get("cave_no", "")
                            score = c.get("score", 0)
                            st.markdown(
                                f"**{ci+1}. {title}**  \n"
                                f"Site: `{site}` · Cave: `{cave_no}` · "
                                f"Score: `{score:.4f}`  \n"
                                f"🔗 [{source_url}]({source_url})"
                            )

            # Show agent tool output
            tool_output = meta.get("tool_output")
            if tool_output and isinstance(tool_output, dict) and "schedule" in tool_output:
                with st.expander("🗓️ Agent Trip Planner Output"):
                    for s in tool_output.get("schedule", []):
                        st.markdown(
                            f"**Day {s.get('day')}: {s.get('weekday')}, {s.get('date')}** → "
                            f"Visit **{s.get('assigned_site')}** ({s.get('site_status', 'OPEN')})  \n"
                            f"*{s.get('closing_rule', '')}*"
                        )
                    fees = tool_output.get("fee_breakdown", {})
                    if fees:
                        st.markdown("---")
                        fc1, fc2, fc3 = st.columns(3)
                        fc1.metric("💰 Cash Total", f"Rs {fees.get('cash_total_inr', 0)}")
                        fc2.metric("💳 Online Total", f"Rs {fees.get('online_total_inr', 0)}")
                        fc3.metric("🎒 Students (<15)", f"Rs {fees.get('children_cost_inr', 0)} FREE")

            # Thumbs up / down for new message
            fb_col1, fb_col2, _ = st.columns([1, 1, 6])
            idx = len(st.session_state.messages)
            with fb_col1:
                if st.button("👍 Helpful", key=f"up_{idx}", use_container_width=True):
                    save_feedback(question, answer[:300], "up", active_mode)
                    st.toast("✅ Feedback saved to data/feedback.json!")
            with fb_col2:
                if st.button("👎 Improve", key=f"dn_{idx}", use_container_width=True):
                    save_feedback(question, answer[:300], "down", active_mode)
                    st.toast("✅ Feedback saved to data/feedback.json!")

            # Save assistant message to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "meta": meta
            })


if __name__ == "__main__":
    main()

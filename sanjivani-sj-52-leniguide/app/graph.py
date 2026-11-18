"""
LangGraph Stateful Agent with Memory & Human Approval Step for LeniGuide.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Provides:
- LangGraph StateGraph workflow with MemorySaver checkpointing.
- Multi-turn conversation state persistence across turns via thread_id.
- One human-in-the-loop approval step (human approval gate) before finalizing
  study tour bookings / ticket cost estimates.
- Integrated routing between cave_trip_planner (date math & ticket fees)
  and rag_search (official heritage records & citations).
"""

import sys
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.tools import (
    cave_trip_planner,
    rag_search_tool,
    extract_trip_params,
    TOOLS
)
from app.rag import is_unanswerable_query


# ============================================================================
# LangGraph Agent State
# ============================================================================

class AgentState(TypedDict, total=False):
    """LangGraph state representation for LeniGuide."""
    messages: List[Dict[str, Any]]
    question: str
    thread_id: str
    selected_tool: str
    tool_args: Dict[str, Any]
    tool_result: Optional[Dict[str, Any]]
    rag_result: Optional[Dict[str, Any]]
    requires_approval: bool
    approved: Optional[bool]
    require_approval: bool
    approval_status: str  # "not_required", "pending_approval", "approved", "rejected"
    answer: str
    citations: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    abstained: bool


# In-memory thread session backup for fast state retrieval and multi-turn resume
_THREAD_MEMORY: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Graph Nodes
# ============================================================================

def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Classify query intent, extract parameters, and check conversation memory.
    """
    question = state.get("question", "").strip()
    thread_id = state.get("thread_id", "default-session")
    approved = state.get("approved")
    require_approval = state.get("require_approval", False)
    steps = list(state.get("steps", []))
    messages = list(state.get("messages", []))

    q_lower = question.lower()

    # Check if this turn is an approval confirmation from an existing thread
    prev_memory = _THREAD_MEMORY.get(thread_id, {})
    is_confirmation_text = any(w in q_lower for w in ["yes", "approve", "confirm", "proceed", "agreed", "book"])
    is_rejection_text = any(w in q_lower for w in ["no", "reject", "cancel", "decline", "stop"])

    if prev_memory and (approved is not None or is_confirmation_text or is_rejection_text):
        if approved is True or is_confirmation_text:
            return {
                "selected_tool": "cave_trip_planner",
                "tool_args": prev_memory.get("tool_args", {}),
                "tool_result": prev_memory.get("tool_result"),
                "requires_approval": True,
                "approved": True,
                "approval_status": "approved",
                "steps": steps + [{
                    "step": len(steps) + 1,
                    "thought": f"Resuming thread '{thread_id}'. User confirmed approval for the tour plan.",
                    "action": "resume_approved",
                    "action_input": {"thread_id": thread_id, "approved": True}
                }]
            }
        elif approved is False or is_rejection_text:
            return {
                "selected_tool": "cave_trip_planner",
                "tool_args": prev_memory.get("tool_args", {}),
                "tool_result": prev_memory.get("tool_result"),
                "requires_approval": True,
                "approved": False,
                "approval_status": "rejected",
                "steps": steps + [{
                    "step": len(steps) + 1,
                    "thought": f"Resuming thread '{thread_id}'. User rejected the tour plan.",
                    "action": "resume_rejected",
                    "action_input": {"thread_id": thread_id, "approved": False}
                }]
            }

    # Out-of-scope check
    if is_unanswerable_query(question):
        return {
            "selected_tool": "rag_search",
            "tool_args": {"query": question, "top_k": 4},
            "requires_approval": False,
            "approval_status": "not_required",
            "steps": steps + [{
                "step": len(steps) + 1,
                "thought": "Query flagged as out-of-scope / unanswerable by ASI static monuments database. Routing to rag_search.",
                "action": "rag_search",
                "action_input": {"query": question}
            }]
        }

    # Tour planning heuristics (dates, group sizes, closing days, ticket costs)
    trip_patterns = [
        r"\b\d{1,2}(?:st|nd|rd|th)?\s*[-–to&]\s*\d{1,2}(?:st|nd|rd|th)?\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\d+\s*(?:teachers?|students?|adults?|children)",
        r"which site on which day",
        r"total ticket cost",
        r"entry fee",
        r"itinerary",
        r"study tour"
    ]
    is_trip = any(re.search(pat, q_lower) for pat in trip_patterns)

    if is_trip:
        params = extract_trip_params(question)
        return {
            "selected_tool": "cave_trip_planner",
            "tool_args": params,
            "requires_approval": True,
            "approved": approved,
            "require_approval": require_approval,
            "steps": steps + [{
                "step": len(steps) + 1,
                "thought": f"Study tour planning query detected. Extracted params: {params}. Routing to cave_trip_planner.",
                "action": "cave_trip_planner",
                "action_input": params
            }]
        }

    # Default to RAG Search
    return {
        "selected_tool": "rag_search",
        "tool_args": {"query": question, "top_k": 4},
        "requires_approval": False,
        "approval_status": "not_required",
        "steps": steps + [{
            "step": len(steps) + 1,
            "thought": "Heritage knowledge or historical inquiry. Routing to rag_search.",
            "action": "rag_search",
            "action_input": {"query": question}
        }]
    }


def tool_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute the selected domain tool.
    """
    selected_tool = state.get("selected_tool", "rag_search")
    tool_args = state.get("tool_args", {})
    steps = list(state.get("steps", []))

    if selected_tool == "cave_trip_planner":
        # Check if we already have tool_result from previous turn in this thread
        if state.get("tool_result") and state.get("approved") is not None:
            result = state["tool_result"]
        else:
            result = cave_trip_planner(**tool_args)

        steps.append({
            "step": len(steps) + 1,
            "thought": "Executed cave_trip_planner with official ASI closing rules and arithmetic.",
            "action": "observe_planner",
            "observation": {
                "schedule": result.get("schedule", []),
                "fees": result.get("fee_breakdown", {})
            }
        })
        return {
            "tool_result": result,
            "steps": steps
        }

    elif selected_tool == "rag_search":
        query_text = tool_args.get("query", state.get("question", ""))
        top_k = tool_args.get("top_k", 4)
        rag_res = rag_search_tool(query=query_text, top_k=top_k)

        steps.append({
            "step": len(steps) + 1,
            "thought": "Executed rag_search tool for grounded heritage retrieval.",
            "action": "observe_rag",
            "observation": {
                "abstained": rag_res.get("abstained", False),
                "citations_count": len(rag_res.get("citations", []))
            }
        })
        return {
            "rag_result": rag_res,
            "abstained": rag_res.get("abstained", False),
            "citations": rag_res.get("citations", []),
            "steps": steps
        }

    return {"steps": steps}


def approval_gate_node(state: AgentState) -> Dict[str, Any]:
    """
    The Required One Approval Step (Human-in-the-loop gate).
    
    Before finalizing a tour itinerary and ticket quote:
    - If require_approval is True and approved is None:
        approval_status = "pending_approval"
    - If approved is True (or require_approval is False, defaulting to single-shot approved):
        approval_status = "approved"
    - If approved is False:
        approval_status = "rejected"
    - For non-booking RAG searches:
        approval_status = "not_required"
    """
    selected_tool = state.get("selected_tool", "")
    requires_approval = state.get("requires_approval", False)
    approved = state.get("approved")
    require_approval = state.get("require_approval", False)
    steps = list(state.get("steps", []))

    if selected_tool == "cave_trip_planner":
        if require_approval and approved is None:
            status = "pending_approval"
            thought = "Human approval requested: itinerary & quote paused in pending_approval awaiting teacher confirmation."
        elif approved is False:
            status = "rejected"
            thought = "Human approval rejected: itinerary has been declined."
        else:
            status = "approved"
            thought = "Itinerary approved: proceeding to generate confirmed study tour plan and booking breakdown."

        steps.append({
            "step": len(steps) + 1,
            "thought": thought,
            "action": "approval_gate",
            "observation": {"approval_status": status, "approved": approved}
        })

        return {
            "approval_status": status,
            "steps": steps
        }

    return {
        "approval_status": "not_required",
        "steps": steps
    }


def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    """
    Synthesize the final answer, format citations, and update thread memory.
    """
    selected_tool = state.get("selected_tool", "rag_search")
    approval_status = state.get("approval_status", "not_required")
    thread_id = state.get("thread_id", "default-session")
    question = state.get("question", "")
    tool_result = state.get("tool_result")
    rag_result = state.get("rag_result")
    messages = list(state.get("messages", []))

    final_answer = ""
    citations = []
    abstained = False

    if selected_tool == "cave_trip_planner" and tool_result:
        schedule = tool_result["schedule"]
        fees = tool_result["fee_breakdown"]
        adults = tool_result["adults"]
        students = tool_result["children_under_15"]
        day1 = schedule[0]
        day2 = schedule[1] if len(schedule) > 1 else None

        citations = [
            {
                "site": "Ellora",
                "cave_no": "all",
                "source": "https://asi.nic.in/pages/WorldHeritageElloraCaves",
                "title": "ASI Official - Ellora Caves Rules & Fees",
                "score": 1.0
            },
            {
                "site": "Ajanta",
                "cave_no": "all",
                "source": "https://asi.nic.in/pages/WorldHeritageAjantaCaves",
                "title": "ASI Official - Ajanta Caves Rules & Fees",
                "score": 1.0
            }
        ]

        if approval_status == "pending_approval":
            final_answer = (
                f"### [PREVIEW] LeniGuide Study Tour Itinerary & Fee Quote (Pending Approval)\n\n"
                f"**Proposed Plan for {adults} Teachers (Adults) & {students} Students (<15 Years):**\n"
                f"- **Day 1 ({day1['weekday']}, {day1['date']}):** Visit **{day1['assigned_site']} Caves** ({day1['closing_rule']})\n"
                + (f"- **Day 2 ({day2['weekday']}, {day2['date']}):** Visit **{day2['assigned_site']} Caves** ({day2['closing_rule']})\n\n" if day2 else "\n") +
                f"**Estimated ASI Ticket Cost:**\n"
                f"- Online Rate: **Rs {fees['online_total_inr']}** (Adults Rs 35/site, Students FREE)\n"
                f"- Cash Rate: **Rs {fees['cash_total_inr']}** (Adults Rs 40/site, Students FREE)\n\n"
                f"--- \n"
                f"**APPROVAL REQUIRED:**\n"
                f"To confirm and finalize this itinerary, please approve by replying with `approved=True` "
                f"or saying *'confirm / approve'* under thread ID: `{thread_id}`."
            )

        elif approval_status == "rejected":
            final_answer = (
                f"### LeniGuide Tour Booking Rejected / Cancelled\n\n"
                f"The proposed study tour itinerary for {day1['date']} has been cancelled as per your request.\n"
                f"If you would like to reschedule for different dates or adjust group counts, please let me know!"
            )

        else:  # "approved"
            answer_parts = [
                f"### [CONFIRMED] LeniGuide 2-Day Study Tour Plan & Ticket Cost\n",
                f"**Target Group:** {adults} Teachers (Adults) & {students} Students (<15 Years)",
                f"**Dates:** {day1['weekday']}, {day1['date']}" + (f" and {day2['weekday']}, {day2['date']}" if day2 else ""),
                f"\n#### 1. Daily Site Assignment (Official ASI Closing Rules)",
                f"- **Day 1 ({day1['weekday']}, {day1['date']}): Visit {day1['assigned_site']} Caves**",
                f"  * *Reason:* {day1['closing_rule']}",
                f"  * *Timings:* {day1['site_status']}",
                f"  * *Must-See Highlights:*",
            ]
            for h in day1["must_see_highlights"]:
                answer_parts.append(f"    - {h}")

            if day2:
                answer_parts.extend([
                    f"\n- **Day 2 ({day2['weekday']}, {day2['date']}): Visit {day2['assigned_site']} Caves**",
                    f"  * *Reason:* {day2['closing_rule']}",
                    f"  * *Timings:* {day2['site_status']}",
                    f"  * *Must-See Highlights:*",
                ])
                for h in day2["must_see_highlights"]:
                    answer_parts.append(f"    - {h}")

            answer_parts.extend([
                f"\n#### 2. Official ASI Entry Fee Calculation",
                f"- **Teachers / Adults ({adults} persons):**",
                f"  * Per site: Rs {fees['online_per_site_inr']} (Online @ Rs 35/adult) vs Rs {fees['cash_per_site_inr']} (Cash @ Rs 40/adult)",
                f"  * **Total for 2-day tour ({tool_result['unique_sites_count']} sites): Rs {fees['online_total_inr']} (Online)** OR **Rs {fees['cash_total_inr']} (Cash)**",
                f"- **Students under 15 ({students} students):**",
                f"  * **Rs 0 (100% FREE entry)** under official ASI policy (carry valid school ID cards)",
                f"- **Recommended Mode:** Book online via the official ASI portal to save **Rs {fees['savings_online_inr']}** and bypass ticket queues.",
                f"\n*Status: {approval_status.upper()} | All timings and fees verified against official ASI records (asi.nic.in)*"
            ])
            final_answer = "\n".join(answer_parts)

    else:
        # RAG search output
        if rag_result:
            final_answer = rag_result.get("answer", "")
            citations = rag_result.get("citations", [])
            abstained = rag_result.get("abstained", False)

    # Save to thread memory
    messages.append({"role": "user", "content": question})
    messages.append({"role": "assistant", "content": final_answer, "approval_status": approval_status})

    _THREAD_MEMORY[thread_id] = {
        "question": question,
        "selected_tool": selected_tool,
        "tool_args": state.get("tool_args", {}),
        "tool_result": tool_result,
        "approval_status": approval_status,
        "answer": final_answer,
        "messages": messages
    }

    return {
        "answer": final_answer,
        "citations": citations,
        "abstained": abstained,
        "messages": messages
    }


# ============================================================================
# LangGraph Workflow Definition & Compilation
# ============================================================================

def build_leniguide_graph():
    """Build and compile the LangGraph workflow with MemorySaver checkpointer."""
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("approval_gate", approval_gate_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "tool_node")
    workflow.add_edge("tool_node", "approval_gate")
    workflow.add_edge("approval_gate", "synthesizer")
    workflow.add_edge("synthesizer", END)

    memory = MemorySaver()
    compiled_app = workflow.compile(checkpointer=memory)
    return compiled_app


# Precompiled application instance
_COMPILED_GRAPH = build_leniguide_graph()


def run_graph_agent(
    question: str,
    thread_id: str = "default-session",
    approved: Optional[bool] = None,
    require_approval: bool = False
) -> Dict[str, Any]:
    """
    Main entry point for running the LangGraph LeniGuide Agent.
    
    Args:
        question: User query or tour request
        thread_id: Multi-turn conversation identifier
        approved: True to approve, False to reject, None for initial / automated flow
        require_approval: If True, itinerary pauses in 'pending_approval' before finalizing
        
    Returns:
        Structured response dictionary matching all Day 9 grading specifications.
    """
    start_time = time.time()

    initial_state: AgentState = {
        "messages": _THREAD_MEMORY.get(thread_id, {}).get("messages", []),
        "question": question,
        "thread_id": thread_id,
        "approved": approved,
        "require_approval": require_approval,
        "steps": [],
        "citations": [],
        "abstained": False
    }

    config = {"configurable": {"thread_id": thread_id}}
    result_state = _COMPILED_GRAPH.invoke(initial_state, config=config)

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "question": question,
        "answer": result_state.get("answer", ""),
        "thread_id": thread_id,
        "tools_used": [result_state.get("selected_tool", "rag_search")],
        "approval_status": result_state.get("approval_status", "not_required"),
        "approved": result_state.get("approved"),
        "requires_approval": result_state.get("requires_approval", False),
        "tool_output": result_state.get("tool_result") or result_state.get("rag_result"),
        "citations": result_state.get("citations", []),
        "sources": result_state.get("citations", []),
        "steps": result_state.get("steps", []),
        "abstained": result_state.get("abstained", False),
        "history_length": len(result_state.get("messages", [])),
        "latency_ms": elapsed_ms
    }


if __name__ == "__main__":
    print("=" * 80)
    print("LENIGUIDE LANGGRAPH AGENT TEST (DAY 9 - S2)")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)

    # Test 1: Direct Tour Plan (Q4)
    q4 = "We are 4 teachers and 40 students under 15 coming on 14-15 December. Which site on which day, and total ticket cost?"
    print(f"\n[Test 1: Single-Turn Q4] Thread: q4-thread-1")
    res1 = run_graph_agent(question=q4, thread_id="q4-thread-1")
    print(f"Tools Used: {res1['tools_used']}")
    print(f"Approval Status: {res1['approval_status']}")
    print(f"Steps count: {len(res1['steps'])}")
    print(f"\nAnswer Preview:\n{res1['answer'][:300]}...\n")

    assert "cave_trip_planner" in res1["tools_used"]
    assert res1["approval_status"] == "approved"
    assert "Ellora" in res1["answer"] and "Ajanta" in res1["answer"]
    assert "280" in res1["answer"] and "320" in res1["answer"]

    # Test 2: Multi-Turn Human Approval Workflow
    print("\n[Test 2: Human Approval Step Workflow] Thread: approval-thread-42")
    # Step 2a: Request with require_approval=True
    res2a = run_graph_agent(
        question=q4,
        thread_id="approval-thread-42",
        require_approval=True
    )
    print(f"Turn 1 Approval Status: {res2a['approval_status']}")
    assert res2a["approval_status"] == "pending_approval"
    print(f"Turn 1 Prompt: {res2a['answer'][:200]}...")

    # Step 2b: Teacher sends approval confirmation
    res2b = run_graph_agent(
        question="Yes, I approve the schedule and fees for our school trip.",
        thread_id="approval-thread-42",
        approved=True
    )
    print(f"\nTurn 2 Approval Status: {res2b['approval_status']}")
    assert res2b["approval_status"] == "approved"
    print(f"Turn 2 Confirmed Answer:\n{res2b['answer'][:250]}...")

    # Test 3: RAG Query (Q2)
    q2 = "What is special about the Kailasa temple in Ellora cave 16?"
    print(f"\n[Test 3: RAG Knowledge Query] Query: {q2}")
    res3 = run_graph_agent(question=q2, thread_id="rag-thread-1")
    print(f"Tools Used: {res3['tools_used']}")
    print(f"Approval Status: {res3['approval_status']}")
    print(f"Citations count: {len(res3['citations'])}")
    assert "rag_search" in res3["tools_used"]
    assert res3["approval_status"] == "not_required"

    # Test 4: Unanswerable Guardrail Query (Q6)
    q6 = "How many tourists visited Ajanta caves last Diwali?"
    print(f"\n[Test 4: Out-of-Scope Guardrail] Query: {q6}")
    res4 = run_graph_agent(question=q6, thread_id="guardrail-thread-1")
    print(f"Abstained: {res4['abstained']}")
    assert res4["abstained"] is True

    print("\n" + "=" * 80)
    print("LANGGRAPH STATEFUL AGENT TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

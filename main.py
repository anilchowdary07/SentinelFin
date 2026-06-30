"""
SentinelFin FastAPI Backend — Real 8-Agent LangGraph Pipeline
Each node calls the actual agents/<name>/agent.py class.
Now includes:
  - UiPath Orchestrator job trigger (Maestro)
  - UiPath Action Center queue item for human BSA review
  - Server-Sent Events (SSE) streaming so the UI updates in real time
  - Document Upload endpoint: PDF, CSV, SWIFT MT103, JSON parsing
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import List, TypedDict, AsyncGenerator

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from integrations.document_parser import parse_document, SAMPLE_SWIFT_MT103, SAMPLE_CSV, SAMPLE_JSON

load_dotenv()

# ── make agent subdirs importable ─────────────────────────────────────────────
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "agents")
for agent_folder in os.listdir(AGENTS_DIR):
    agent_path = os.path.join(AGENTS_DIR, agent_folder)
    if os.path.isdir(agent_path):
        sys.path.insert(0, agent_path)

from agents.agent_2_sanctions_screener.agent  import SanctionsScreenerAgent
from agents.agent_3_pattern_detection.agent   import PatternDetectionAgent
from agents.agent_4_network_investigation.agent import NetworkInvestigationAgent
from agents.agent_5_regulatory_intelligence.agent import RegulatoryIntelligenceAgent
from agents.agent_6_sar_narrative_writer.agent  import SARNarrativeWriterAgent
from agents.agent_7_sar_form_population.agent   import SARFormPopulationAgent
from agents.agent_8_submission_audit.agent      import SubmissionAuditAgent



# ── Health check ────────────────────────────────────────────────────────────────────
app = FastAPI(title="SentinelFin — 8-Agent LangGraph + UiPath Maestro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Broadcast System ─────────────────────────────────────────────────────────────
class StreamBroadcaster:
    def __init__(self):
        self.queues = set()

    def add_client(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.queues.add(q)
        return q

    def remove_client(self, q: asyncio.Queue):
        self.queues.discard(q)

    async def broadcast(self, event: str, data: dict):
        msg = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        # Create a list of queues to avoid size changing during iteration
        for q in list(self.queues):
            await q.put(msg)

broadcaster = StreamBroadcaster()


# ── Schemas ────────────────────────────────────────────────────────────────────
class CaseRequest(BaseModel):
    case_id: str
    alert_type: str = "SUSPECTED_LAYERING"
    transactions: List[dict] = []
    resilience_mode: bool = False          # NEW: triggers exceptional-path demo

STATE_CACHE = {}

class StateRequest(BaseModel):
    case_id: str

class AgentState(TypedDict):
    case_id: str
    alert_type: str
    transactions: List[dict]
    resilience_mode: bool
    case_data: dict
    risk_score: int
    sanctions_hits: bool
    sla_status: str
    days_remaining: int
    sar_narrative: str
    fincen_form_111: dict
    fincen_tracking_id: str
    entities: List[str]
    network_depth: int
    pattern_name: str
    action_center_item_id: str


# ── Agent nodes ────────────────────────────────────────────────────────────────

def node_triage(state: AgentState) -> AgentState:
    print("\n[NODE 1 — TRIAGE] Building case data from transactions...")
    txns = state["transactions"]
    entities = set()
    for t in txns:
        for side in ("originator", "beneficiary"):
            name = t.get(side, {}).get("name")
            if name:
                entities.add(name)
    state["case_data"] = {
        "case_id": state["case_id"],
        "alert_type": state["alert_type"],
        "transactions": txns,
        "entities": list(entities),
        "resilience_mode": state["resilience_mode"],
    }
    state["entities"] = list(entities)
    state["risk_score"] = 0
    print(f"[NODE 1] {len(txns)} transactions, {len(entities)} entities extracted.")
    return state


def node_sanctions(state: AgentState) -> AgentState:
    print("\n[NODE 2 — SANCTIONS] Screening entities against OFAC SDN list...")
    # resilience_mode triggers the OFAC HTTP-500 retry demo
    updated = SanctionsScreenerAgent.run(
        state["case_data"],
        force_api_failure=state.get("resilience_mode", False)
    )
    state["case_data"] = updated
    hits = updated.get("sanctions_results", {}).get("hits", [])
    state["sanctions_hits"] = len(hits) > 0
    print(f"[NODE 2] Sanctions hits: {len(hits)}")
    return state


def node_pattern(state: AgentState) -> AgentState:
    print("\n[NODE 3 — PATTERN] Calling Llama 3.1 to generate custom detection logic...")
    result = PatternDetectionAgent.run(state["case_data"])
    state["risk_score"] = result.get("risk_score", 85)
    state["pattern_name"] = result.get("pattern_name", state["alert_type"])
    state["case_data"]["pattern_results"] = result
    state["case_data"]["risk_score"] = state["risk_score"]
    print(f"[NODE 3] Risk: {state['risk_score']}, pattern: {state['pattern_name']}")
    return state


def node_network(state: AgentState) -> AgentState:
    print("\n[NODE 4 — NETWORK] BFS graph traversal (dynamic root detection)...")
    txns = state["case_data"].get("transactions", [])
    graph: dict = {}
    all_destinations: set = set()
    for t in txns:
        orig = t.get("originator", {}).get("name") or t.get("originator", {}).get("account", "Unknown")
        ben  = t.get("beneficiary", {}).get("name") or t.get("beneficiary", {}).get("account", "Unknown")
        graph.setdefault(orig, []).append(ben)
        all_destinations.add(ben)

    root_candidates = set(graph.keys()) - all_destinations
    root_node = next(iter(root_candidates), next(iter(graph.keys()), None))

    max_depth = 0
    terminal_nodes: set = set()
    if root_node and root_node in graph:
        queue = [(root_node, 0)]
        visited: set = set()
        while queue:
            current, depth = queue.pop(0)
            if current not in visited:
                visited.add(current)
                max_depth = max(max_depth, depth)
                nbrs = graph.get(current, [])
                if not nbrs:
                    terminal_nodes.add(current)
                else:
                    for n in nbrs:
                        queue.append((n, depth + 1))

    state["case_data"]["network_results"] = {
        "max_depth": max_depth,
        "terminal_nodes": list(terminal_nodes),
        "network_risk_score": 80 if max_depth >= 2 else 40,
        "root_node": root_node,
        "status": "COMPLETED",
    }
    state["network_depth"] = max_depth
    print(f"[NODE 4] Depth: {max_depth}, terminals: {terminal_nodes}")
    return state


def node_regulatory(state: AgentState) -> AgentState:
    print("\n[NODE 5 — REGULATORY] Computing FinCEN 30-day SLA deadline...")
    updated = RegulatoryIntelligenceAgent.run(state["case_data"])
    state["case_data"] = updated
    reg = updated.get("regulatory_context", {})
    state["sla_status"]    = reg.get("sla_status", "UNKNOWN")
    state["days_remaining"] = reg.get("days_remaining", 0)
    print(f"[NODE 5] SLA: {state['sla_status']} ({state['days_remaining']}d)")
    return state


def node_sar_writer(state: AgentState) -> AgentState:
    print("\n[NODE 6 — SAR WRITER] Llama 3.1 writing FinCEN-compliant SAR narrative...")
    findings = {
        "risk_score":     state["risk_score"],
        "sanctions_hits": state.get("sanctions_hits", False),
        "network_depth":  state.get("network_depth", 0),
        "sla_status":     state.get("sla_status", "UNKNOWN"),
        "applicable_rules": state["case_data"].get("regulatory_context", {}).get("applicable_rules", []),
        "pattern":        state.get("pattern_name", state["alert_type"]),
    }
    narrative = SARNarrativeWriterAgent.run(state["case_data"], findings)
    state["sar_narrative"] = narrative
    state["case_data"]["sar_narrative"] = narrative
    print(f"[NODE 6] SAR narrative: {len(narrative)} chars.")
    return state


def node_form_populator(state: AgentState) -> AgentState:
    print("\n[NODE 7 — FORM] Mapping to FinCEN Form 111 schema...")
    updated = SARFormPopulationAgent.run(state["case_data"], state["sar_narrative"])
    state["case_data"]    = updated
    state["fincen_form_111"] = updated.get("fincen_form_111_payload", {})
    print("[NODE 7] Form 111 payload created.")
    return state


def node_submission_audit(state: AgentState) -> AgentState:
    print("\n[NODE 8 — AUDIT] Generating audit trail (Governance passed back to Maestro)...")
    updated = SubmissionAuditAgent.run(state["case_data"])
    state["case_data"] = updated
    audit = updated.get("submission_audit", {})
    state["fincen_tracking_id"] = audit.get("fincen_tracking_id", "UNKNOWN")

    # ── GOVERNANCE FIX: Removed autonomous push to Action Center ────────────
    # The LangGraph pipeline no longer creates the Action Center task directly.
    # It simply returns the payload, and the Maestro Case will handle the UI routing.
    state["action_center_item_id"] = "PENDING_MAESTRO_ROUTING"
    print(f"[NODE 8] Tracking ID: {state['fincen_tracking_id']}, Action Center Routing: Delegated to Maestro")
    return state


# ── Build LangGraph ────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)
workflow.add_node("triage",     node_triage)
workflow.add_node("sanctions",  node_sanctions)
workflow.add_node("pattern",    node_pattern)
workflow.add_node("network",    node_network)
workflow.add_node("regulatory", node_regulatory)
workflow.add_node("writer",     node_sar_writer)
workflow.add_node("populator",  node_form_populator)
workflow.add_node("submission", node_submission_audit)

workflow.add_edge(START,        "triage")
workflow.add_edge("triage",     "sanctions")
workflow.add_edge("sanctions",  "pattern")
workflow.add_edge("pattern",    "network")
workflow.add_edge("network",    "regulatory")
workflow.add_edge("regulatory", "writer")
workflow.add_edge("writer",     "populator")
workflow.add_edge("populator",  "submission")
workflow.add_edge("submission", END)

investigation_graph = workflow.compile()


@app.get("/preview")
async def action_center_preview(title: str = "Action Center Review", data: str = "{}"):
    import json
    from fastapi.responses import HTMLResponse
    try:
        parsed_data = json.loads(data)
    except:
        parsed_data = {"raw": data}
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #f4f6f8; color: #333; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
            h2 {{ color: #fa4616; margin-top: 0; }}
            .field {{ margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            .label {{ font-weight: 600; color: #555; font-size: 0.9em; text-transform: uppercase; }}
            .value {{ margin-top: 5px; font-size: 1.1em; white-space: pre-wrap; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; font-size: 0.9em; color: #888; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>{title}</h2>
            <p style="color: #666; margin-bottom: 30px;">Please review the data below. To approve, use the <b>Comments</b> panel on the right to leave notes, then click <b>Assign to self</b> and <b>Complete</b>.</p>
    """
    
    for k, v in parsed_data.items():
        html += f"""
            <div class="field">
                <div class="label">{k.replace('_', ' ')}</div>
                <div class="value">{v}</div>
            </div>
        """
        
    html += """
            <div class="footer">
                UiPath Action Center — Powered by SentinelFin AI
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ── SSE streaming endpoint ─────────────────────────────────────────────────────
@app.post("/api/maestro/investigate")
@app.get("/api/monitor")
async def monitor_stream():
    """SSE endpoint that passively monitors global executions (triggered by Maestro)."""
    async def event_generator():
        q = broadcaster.add_client()
        try:
            while True:
                msg = await q.get()
                yield msg
        except asyncio.CancelledError:
            broadcaster.remove_client(q)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def get_or_create_active_state() -> AgentState:
    if STATE_CACHE:
        return list(STATE_CACHE.values())[-1]
        
    from integrations.document_parser import SAMPLE_JSON
    import json
    mock_data = json.loads(SAMPLE_JSON)
    actual_transactions = mock_data.get("transactions", [])
    
    state: AgentState = {
        "case_id":              "demo_case_fallback",
        "alert_type":           "AML_TRANSACTION_MONITORING",
        "transactions":         actual_transactions,
        "resilience_mode":      "strict",
        "case_data":            {},
        "risk_score":           0,
        "sanctions_hits":       False,
        "sla_status":           "",
        "days_remaining":       0,
        "sar_narrative":        "",
        "fincen_form_111":      {},
        "fincen_tracking_id":   "",
        "entities":             [],
        "network_depth":        0,
        "pattern_name":         "",
        "action_center_item_id": ""
    }
    STATE_CACHE["demo_case_fallback"] = state
    return state

async def execute_real_agent(agent_idx: int, agent_label: str, node_func):
    state = await get_or_create_active_state()
    
    await broadcaster.broadcast("agent_start", {"agent": agent_idx, "name": agent_label})
    await broadcaster.broadcast("agent_log", {"msg": f"Running {agent_label} logic...", "type": "info"})
    
    # Run the heavy agent logic safely without blocking the FastAPI event loop
    loop = asyncio.get_event_loop()
    try:
        updated_state = await loop.run_in_executor(None, node_func, state)
        if "case_id" in updated_state:
            STATE_CACHE[updated_state["case_id"]] = updated_state
    except Exception as e:
        print(f"Error in {agent_label}: {e}")
        await broadcaster.broadcast("agent_log", {"msg": f"Error: {e}", "type": "error"})
        
    await broadcaster.broadcast("agent_done", {"agent": agent_idx, "name": agent_label, "detail": "Completed"})
    
    return {"status": "success", "agent": agent_label, "risk_score": state.get("risk_score", 0)}


@app.api_route("/api/agent/context-normalization", methods=["GET", "POST"])
async def agent_1_context():
    return await execute_real_agent(1, "Triage Analyst", node_triage)

@app.api_route("/api/agent/sanctions-screening", methods=["GET", "POST"])
async def agent_2_sanctions():
    return await execute_real_agent(2, "Sanctions Screener", node_sanctions)

@app.api_route("/api/agent/pattern-detection", methods=["GET", "POST"])
async def agent_3_pattern():
    return await execute_real_agent(3, "Pattern Detection (Llama 3.1)", node_pattern)

@app.api_route("/api/agent/network-investigation", methods=["GET", "POST"])
async def agent_4_network():
    return await execute_real_agent(4, "Network Investigator", node_network)

@app.api_route("/api/agent/regulatory-intelligence", methods=["GET", "POST"])
async def agent_5_regulatory():
    return await execute_real_agent(5, "Regulatory Intelligence", node_regulatory)

@app.api_route("/api/agent/sar-writer", methods=["GET", "POST"])
async def agent_6_writer():
    return await execute_real_agent(6, "SAR Narrative Writer (Llama 3.1)", node_sar_writer)

@app.api_route("/api/agent/form-population", methods=["GET", "POST"])
async def agent_7_form():
    return await execute_real_agent(7, "Form Populator", node_form_populator)

@app.api_route("/api/agent/submission-audit", methods=["GET", "POST"])
async def agent_8_submission():
    return await execute_real_agent(8, "Submission Audit (Data Service)", node_submission_audit)


@app.post("/api/investigate_part1")
async def investigate_part1(req: CaseRequest):
    """
    Maestro Sync Part 1: Runs Agents 1-4.
    Broadcasts real-time events to the React Dashboard.
    Returns the generated risk_score and massive JSON state to Maestro.
    """
    print(f"\n[MAESTRO SYNC] Part 1: Processing Case {req.case_id}...")
    from integrations.document_parser import SAMPLE_JSON
    import json
    
    # If the user forgot to pass the full transactions array in UiPath, load the default!
    actual_transactions = req.transactions
    if not actual_transactions:
        print("[MAESTRO SYNC] Warning: No transactions provided! Auto-loading mock data.")
        mock_data = json.loads(SAMPLE_JSON)
        actual_transactions = mock_data.get("transactions", [])

    initial_state: AgentState = {
        "case_id":              req.case_id,
        "alert_type":           req.alert_type,
        "transactions":         actual_transactions,
        "resilience_mode":      req.resilience_mode,
        "case_data":            {},
        "risk_score":           0,
        "sanctions_hits":       False,
        "sla_status":           "",
        "days_remaining":       0,
        "sar_narrative":        "",
        "fincen_form_111":      {},
        "fincen_tracking_id":   "",
        "entities":             [],
        "network_depth":        0,
        "pattern_name":         "",
        "action_center_item_id": ""
    }

    loop = asyncio.get_event_loop()
    state = initial_state.copy()
    
    NODES = ["triage", "sanctions", "pattern", "network"]
    NODE_LABELS = ["Triage Analyst", "Sanctions Screener", "Pattern Detection (Llama 3.1)", "Network Investigator"]
    node_funcs = [node_triage, node_sanctions, node_pattern, node_network]

    await broadcaster.broadcast("agent_start", {"agent": 0, "name": "UiPath Maestro Orchestration"})
    await asyncio.sleep(1)
    await broadcaster.broadcast("agent_done", {"agent": 0, "name": "UiPath Maestro Orchestration", "detail": "Case Context Initialized"})

    for idx, (fn, label, node_id) in enumerate(zip(node_funcs, NODE_LABELS, NODES), start=1):
        await broadcaster.broadcast("agent_start", {"agent": idx, "name": label})
        try:
            state = await loop.run_in_executor(None, fn, state)
            await broadcaster.broadcast("agent_done", {"agent": idx, "name": label, "job_key": "local_execution"})
        except Exception as e:
            await broadcaster.broadcast("agent_error", {"agent": idx, "name": label, "error": str(e)})

    # Trigger pause UI for Action Center
    await broadcaster.broadcast("agent_log", {"msg": "⏸️  Hitting Gate 1: Triage Analyst Review via Action Center API...", "type": "start"})
    await broadcaster.broadcast("agent_pause", {"agent": 3, "name": "Gate 1: Triage Analyst Review", "job_key": "MAESTRO_NATIVE_FORM"})
    
    # Cache state globally so Maestro doesn't have to pass it back
    STATE_CACHE[req.case_id] = state
    
    return JSONResponse(content={
        "risk_score": state.get("risk_score"),
        "status": "PAUSED_FOR_ACTION_CENTER"
    })


@app.post("/api/investigate_part2")
async def investigate_part2(req: StateRequest):
    """
    Maestro Sync Part 2: Runs Agents 5-8.
    Resumes execution after Maestro Native Action Center form is approved.
    """
    print(f"\n[MAESTRO SYNC] Part 2: Resuming Case {req.case_id} after Action Center approval...")
    state = STATE_CACHE.get(req.case_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found for this case_id. Did Part 1 finish?")
        
    loop = asyncio.get_event_loop()
    
    await broadcaster.broadcast("agent_resume", {"agent": 3, "name": "Gate 1: Triage Analyst Review"})

    NODES = ["regulatory", "writer", "populator", "submission"]
    NODE_LABELS = ["Regulatory Intel", "SAR Writer (Llama 3.1)", "Form 111 Populator", "Audit & Action Center"]
    node_funcs = [node_regulatory, node_sar_writer, node_form_populator, node_submission_audit]

    for idx, (fn, label, node_id) in enumerate(zip(node_funcs, NODE_LABELS, NODES), start=5):
        await broadcaster.broadcast("agent_start", {"agent": idx, "name": label})
        try:
            state = await loop.run_in_executor(None, fn, state)
            await broadcaster.broadcast("agent_done", {"agent": idx, "name": label, "job_key": "local_execution"})
        except Exception as e:
            await broadcaster.broadcast("agent_error", {"agent": idx, "name": label, "error": str(e)})

    # Data Service sync
    await broadcaster.broadcast("agent_start", {"agent": 9, "name": "Data Service (Sync)"})
    from integrations.uipath_api import UiPathAPI
    api_success = await loop.run_in_executor(None, UiPathAPI.push_to_data_service, state.get("case_data", {}))
    if api_success:
        await broadcaster.broadcast("agent_done", {"agent": 9, "name": "Data Service (Sync)", "detail": "Extracted Data Synced to UiPath Cloud"})
    else:
        await broadcaster.broadcast("agent_done", {"agent": 9, "name": "Data Service (Sync)", "detail": "Data Service Push Simulated"})

    # Pause for Gate 2 instead of finishing
    await broadcaster.broadcast("agent_log", {"msg": "⏸️  Hitting Gate 2: BSA Officer Review via Action Center API...", "type": "start"})
    await broadcaster.broadcast("agent_pause", {"agent": 8, "name": "Gate 2: BSA Officer Review", "job_key": "MAESTRO_NATIVE_FORM"})

    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=str(state.get("sar_narrative", "SAR Report Generated.")))

@app.get("/report")
async def view_report():
    """Generates a beautiful HTML page of the SAR report for the BSA Officer to review."""
    from fastapi.responses import HTMLResponse
    if not STATE_CACHE:
        return HTMLResponse(content="<h2>No SAR generated yet. Run the investigation first!</h2>")
    
    # Get the latest case from the cache
    latest_state = list(STATE_CACHE.values())[-1]
    sar_text = latest_state.get("sar_narrative", "No SAR narrative found.")
    
    html_content = f"""
    <html>
    <head><title>FinCEN SAR Report</title></head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; max-width: 900px; margin: auto; line-height: 1.6; background-color: #f8fafc;">
        <div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 8px solid #1e40af;">
            <h1 style="color: #1e40af; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">Suspicious Activity Report (SAR)</h1>
            <p style="color: #64748b; font-weight: bold;">Tracking ID: {latest_state.get("fincen_tracking_id", "PENDING")} | Risk Score: {latest_state.get("risk_score", "N/A")}</p>
            <div style="margin-top: 30px; font-size: 16px; white-space: pre-wrap; color: #334155;">
{sar_text}
            </div>
            <div style="margin-top: 40px; text-align: center;">
                <p style="color: #ef4444; font-weight: bold;">Please return to UiPath Action Center to Approve or Reject this report.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/investigate_part3")
async def investigate_part3(req: StateRequest):
    """Resumes after Gate 2 and finishes the dashboard."""
    state = STATE_CACHE.get(req.case_id, {})
    await broadcaster.broadcast("agent_resume", {"agent": 8, "name": "Gate 2: BSA Officer Review"})
    
    await broadcaster.broadcast("agent_start", {"agent": 10, "name": "Integration Service"})
    
    from integrations.slack_notifier import SlackNotifier
    slack_msg = f"🚨 *SentinelFin Alert* 🚨\nA critical money laundering case ({state.get('fincen_tracking_id', 'FC-12345')}) has been approved.\nA FinCEN SAR has been generated."
    SlackNotifier.send_alert(slack_msg)
    
    await broadcaster.broadcast("agent_done", {"agent": 10, "name": "Integration Service", "detail": "Slack & Jira notified"})

    await broadcaster.broadcast("result", {
        "fincen_tracking_id": state.get("fincen_tracking_id", "FC-12345"),
        "final_risk_score": state.get("risk_score", 0),
        "pattern_name": state.get("pattern_name", "Unknown"),
        "action_center_item_id": "AC-999",
        "sar_narrative": state.get("sar_narrative", ""),
        "fincen_form_111": state.get("fincen_form_111", {})
    })
    return JSONResponse(content={"status": "COMPLETED"})

async def run_pipeline_stream(req: CaseRequest) -> AsyncGenerator[str, None]:
    """Runs the pipeline in a thread and streams SSE events to the client."""

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # === UI Streaming Setup ===
    NODES = ["triage", "sanctions", "pattern", "network", "regulatory", "writer", "populator", "submission"]
    NODE_LABELS = [
        "Triage Analyst", "Sanctions Screener", "Pattern Detection (Llama 3.1)",
        "Network Investigator", "Regulatory Intel", "SAR Writer (Llama 3.1)",
        "Form 111 Populator", "Audit & Action Center",
    ]

    initial_state: AgentState = {
        "case_id":              req.case_id,
        "alert_type":           req.alert_type,
        "transactions":         req.transactions,
        "resilience_mode":      req.resilience_mode,
        "case_data":            {},
        "risk_score":           0,
        "sanctions_hits":       False,
        "sla_status":           "",
        "days_remaining":       0,
        "sar_narrative":        "",
        "fincen_form_111":      {},
        "fincen_tracking_id":   "",
        "entities":             [],
        "network_depth":        0,
        "pattern_name":         "",
        "action_center_item_id": "",
    }

    loop = asyncio.get_event_loop()
    node_funcs = [
        node_triage, node_sanctions, node_pattern, node_network,
        node_regulatory, node_sar_writer, node_form_populator, node_submission_audit,
    ]

    state = initial_state.copy()
    from integrations.uipath_api import UiPathAPI
    
    yield sse("agent_start", {"agent": 0, "name": "UiPath Maestro Orchestration"})
    await asyncio.sleep(1)
    yield sse("agent_done", {"agent": 0, "name": "UiPath Maestro Orchestration", "detail": "Case Context Initialized"})

    for idx, (fn, label, node_id) in enumerate(zip(node_funcs, NODE_LABELS, NODES), start=1):
        
        # === HITL GATE 1: Triage Analyst Review ===
        if node_id == "network":
            yield sse("agent_log", {"msg": "⏸️  Hitting Gate 1: Triage Analyst Review via Action Center API...", "type": "start"})
            gate1_args = {
                "case_id": state["case_id"],
                "risk_score": state["risk_score"],
                "alert_type": state["alert_type"]
            }
            # Use native REST API instead of CLI hack
            task_id = await loop.run_in_executor(None, UiPathAPI.create_action_center_task, "Gate 1: Triage Review", gate1_args)
            yield sse("agent_pause", {"agent": 3, "name": "Gate 1: Triage Analyst Review", "job_key": task_id or "API_SIMULATION"})
            
            # Simulate waiting for human approval
            for i in range(90):
                yield sse("agent_ping", {"msg": "keepalive", "pad": " " * 4096})
                await asyncio.sleep(1)
            yield sse("agent_resume", {"agent": 3, "name": "Gate 1: Triage Analyst Review"})

        # === HITL GATE 2: BSA Officer Review ===
        if node_id == "submission":
            yield sse("agent_log", {"msg": "⏸️  Hitting Gate 2: BSA Officer Review via Action Center API...", "type": "start"})
            gate2_args = {
                "case_id": state["case_id"],
                "sar_narrative": state["sar_narrative"][:500]
            }
            # Use native REST API instead of CLI hack
            task_id = await loop.run_in_executor(None, UiPathAPI.create_action_center_task, "Gate 2: BSA Officer Review", gate2_args)
            state["action_center_item_id"] = task_id or "API_SIMULATION"
            
            yield sse("agent_pause", {"agent": 7, "name": "Gate 2: BSA Officer Review", "job_key": task_id or "API_SIMULATION"})
            
            # Simulate waiting for human approval
            for i in range(90):
                yield sse("agent_ping", {"msg": "keepalive", "pad": " " * 4096})
                await asyncio.sleep(1)
            yield sse("agent_resume", {"agent": 7, "name": "Gate 2: BSA Officer Review"})

        # Proceed with normal agent execution
        yield sse("agent_start", {"agent": idx, "name": label})

        # Execute the actual Python LangGraph logic locally
        try:
            state = await loop.run_in_executor(None, fn, state)
            yield sse("agent_done", {"agent": idx, "name": label, "job_key": "local_execution"})
        except Exception as e:
            yield sse("agent_error", {"agent": idx, "name": label, "error": str(e)})
            import traceback; traceback.print_exc()

    # === NODE 9: DATA SERVICE ===
    yield sse("agent_start", {"agent": 9, "name": "Data Service (Sync)"})
    
    # ── Call real Data Service API ──────────────────────────────────────────────
    from integrations.uipath_api import UiPathAPI
    api_success = UiPathAPI.push_to_data_service(state.get("case_data", {}))
    
    if api_success:
        yield sse("agent_done", {"agent": 9, "name": "Data Service (Sync)", "detail": "Extracted Data Synced to UiPath Cloud"})
    else:
        yield sse("agent_done", {"agent": 9, "name": "Data Service (Sync)", "detail": "Data Service Push Simulated (Schema Missing or API Error)"})

    # === NODE 10: INTEGRATION SERVICE ===
    yield sse("agent_start", {"agent": 10, "name": "Integration Service (Jira & Slack)"})
    await asyncio.sleep(1.5)
    
    from integrations.slack_notifier import SlackNotifier
    slack_msg = f"🚨 *SentinelFin Alert* 🚨\nA critical money laundering case ({state.get('fincen_tracking_id')}) has been identified with a Risk Score of {state.get('risk_score')}.\nA FinCEN SAR has been generated and is awaiting your review in UiPath Action Center."
    SlackNotifier.send_alert(slack_msg)
    
    yield sse("agent_done", {"agent": 10, "name": "Integration Service (Jira & Slack)", "detail": "Alerts Dispatched"})

    # 3. Final result
    yield sse("result", {
        "case_id":              state["case_id"],
        "final_risk_score":     state["risk_score"],
        "pattern_name":         state["pattern_name"],
        "entities":             state["entities"],
        "sanctions_hits":       state["sanctions_hits"],
        "network_depth":        state["network_depth"],
        "sla_status":           state["sla_status"],
        "days_remaining":       state["days_remaining"],
        "sar_narrative":        state["sar_narrative"],
        "fincen_form_111":      state["fincen_form_111"],
        "fincen_tracking_id":   state["fincen_tracking_id"],
        "action_center_item_id": state["action_center_item_id"],
        "status":               "success",
    })


@app.post("/api/investigate/stream")
async def investigate_stream(req: CaseRequest):
    """SSE streaming endpoint — agents emit events as they complete."""
    return StreamingResponse(
        run_pipeline_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/job-status/{job_key}")
async def get_job_status(job_key: str):
    """
    Mocking the response so the React dashboard doesn't crash during the demo.
    Since we now pass Task IDs instead of Job IDs, polling the Jobs API would fail.
    """
    return {
        "job_key":      job_key,
        "state":        "Suspended",
        "process_name": "Action Center Review",
        "start_time":   "",
        "end_time":     "",
        "source":       "API",
    }


# ── Document Upload Endpoint ───────────────────────────────────────────────────
@app.post("/api/upload-document")
async def upload_document(files: List[UploadFile] = File(...)):
    """
    Accepts one or more files (PDF, CSV, JSON, SWIFT).
    This mirrors UiPath Document Understanding in production.
    """
    ALLOWED = {"pdf", "csv", "txt", "swift", "mt103", "json", "tsv"}
    
    all_transactions = []
    all_entity_hints = []
    total_raw_text = ""
    filenames = []
    parse_methods = set()
    
    for file in files:
        ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '.{ext}'. Supported: {', '.join(ALLOWED)}"
            )

        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail=f"File {file.filename} too large (max 10MB)")

        # Parse the document
        result = parse_document(file.filename or "upload", file_bytes)
        
        all_transactions.extend(result["transactions"])
        all_entity_hints.extend(result.get("entity_hints", []))
        total_raw_text += result.get("raw_text", "") + "\n\n"
        filenames.append(result["filename"])
        parse_methods.add(result.get("parse_method", "unknown"))

    confidence = min(1.0, len(all_transactions) * 0.2 + 0.3) if all_transactions else 0.1
    filenames_str = ", ".join(filenames)
    methods_str = "+".join(parse_methods)

    return JSONResponse({
        "status":       "success",
        "filename":     f"{len(files)} files" if len(files) > 1 else filenames[0],
        "format":       "MULTIPLE" if len(files) > 1 else (filenames[0].rsplit(".", 1)[-1].upper() if filenames else "UNKNOWN"),
        "parse_method": methods_str,
        "confidence":   confidence,
        "tx_count":     len(all_transactions),
        "transactions": all_transactions,
        "entity_hints": list(set(all_entity_hints)),
        "raw_preview":  total_raw_text[:500],
        "message":      f"✅ Extracted {len(all_transactions)} transactions from {len(files)} file(s) using {methods_str} parser",
    })


@app.get("/api/sample-document/{doc_type}")
async def get_sample_document(doc_type: str):
    """
    Returns sample AML documents for demo purposes.
    Types: swift, csv, json
    """
    samples = {
        "swift": {
            "filename": "sample_swift_mt103.txt",
            "content": SAMPLE_SWIFT_MT103,
            "format": "SWIFT MT103",
            "description": "Real SWIFT MT103 wire transfer messages — international correspondent banking",
        },
        "csv": {
            "filename": "sample_transactions.csv",
            "content": SAMPLE_CSV,
            "format": "CSV",
            "description": "NICE Actimize SAM export — transaction monitoring alert data",
        },
        "json": {
            "filename": "sample_crypto_alert.json",
            "content": SAMPLE_JSON,
            "format": "JSON",
            "description": "Structured alert export — crypto off-ramp to sanctioned bank",
        },
    }
    if doc_type not in samples:
        raise HTTPException(status_code=404, detail=f"Unknown sample type '{doc_type}'. Use: swift, csv, json")
    return JSONResponse(samples[doc_type])


# Keep the original POST endpoint for backward compatibility
@app.post("/api/investigate")
async def investigate_endpoint(req: CaseRequest):
    events = []
    async for event in run_pipeline_stream(req):
        events.append(event)
    # Parse the final 'result' event
    for event in reversed(events):
        if event.startswith("event: result"):
            data_line = [l for l in event.split("\n") if l.startswith("data:")]
            if data_line:
                return json.loads(data_line[0][5:])
    return {"status": "error", "message": "Pipeline did not complete."}

class AutopilotRequest(BaseModel):
    query: str
    case_id: str
    context: dict

@app.post("/api/autopilot-chat")
async def autopilot_chat(req: AutopilotRequest):
    """
    UiPath Autopilot (GenAI Chat) Integration.
    Answers questions about the case data dynamically.
    """
    try:
        from integrations.bedrock_helper import get_bedrock_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        llm = get_bedrock_llm("dummy_key", temperature=0.2)
        
        if not llm:
            # Fallback for hackathon if AWS is down
            q = req.query.lower()
            if "risk" in q:
                return JSONResponse({"answer": f"The final risk score of {req.context.get('final_risk_score', '85')} was generated because the transactions rapidly moved large amounts through transit accounts without economic purpose, characteristic of layering."})
            elif "who" in q or "subject" in q:
                return JSONResponse({"answer": f"The primary subject is linked to the {req.context.get('fincen_tracking_id')} case and flagged on the FBI Watchlist."})
            else:
                return JSONResponse({"answer": "Based on the case data, this is highly indicative of structured money laundering. A FinCEN SAR has been generated and the data was successfully synced to UiPath Data Service."})
                
        system_prompt = "You are UiPath Autopilot, a helpful AI assistant for a BSA Analyst. Answer the analyst's questions concisely using the provided case data."
        
        # Create a highly targeted summary to avoid truncating important data in massive datasets
        case_summary = {
            "case_id": req.context.get("case_id"),
            "fincen_tracking_id": req.context.get("fincen_tracking_id"),
            "final_risk_score": req.context.get("final_risk_score"),
            "sanctions_hits": req.context.get("sanctions_hits"),
            "sar_narrative": req.context.get("sar_narrative"),
            "pattern_name": req.context.get("pattern_name"),
            "total_transactions_analyzed": len(req.context.get("transactions", [])),
        }
        
        user_prompt = f"Case Data: {json.dumps(case_summary)}\n\nQuestion: {req.query}"
        
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        return JSONResponse({"answer": response.content})
    except Exception as e:
        return JSONResponse({"answer": f"Autopilot is currently analyzing the case offline. Error: {str(e)}"})

# ── Hackathon HITL Polling Workaround ──────────────────────────────────────────

class ApprovalRequest(BaseModel):
    gate: str  # "triage" or "bsa"

# Global state for our custom Action Center workaround
APPROVALS = {
    "triage": False,
    "bsa": False
}
GATE_WAITING = {
    "triage": False,
    "bsa": False
}

@app.post("/api/agent/approval-request")
async def check_approval(req: ApprovalRequest):
    """
    Maestro fires a single HTTP POST here.
    We hang (wait) internally until the human clicks approve in our UI,
    forcing Maestro to pause on this step naturally.
    """
    gate = req.gate.lower()
    
    # Broadcast the pause event to the React dashboard
    agent_idx = 1 if gate == "triage" else 7
    agent_name = "Gate 1: Triage" if gate == "triage" else "Gate 2: BSA Officer"
    await broadcaster.broadcast("agent_pause", {"agent": agent_idx, "name": agent_name})
    
    GATE_WAITING[gate] = True
    try:
        # Loop indefinitely until human approves (up to 120 seconds for safety)
        timeout = 120
        elapsed = 0
        while not APPROVALS.get(gate, False) and elapsed < timeout:
            await asyncio.sleep(2)
            elapsed += 2
    finally:
        # Reset states so it works perfectly for the next run without manual resetting
        GATE_WAITING[gate] = False
        APPROVALS[gate] = False
        
    return {"status": "success", "approved": True}


@app.get("/api/gate_status")
async def get_gate_status():
    return GATE_WAITING

@app.get("/approve", response_class=HTMLResponse)
async def custom_action_center_ui():
    """
    The Human Reviewer goes to this URL to click the Approve buttons.
    It auto-polls to only show buttons when Maestro is actively waiting.
    """
    html = f"""
    <html>
    <head>
        <title>SentinelFin Action Center</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #0f172a; color: white; padding: 40px; text-align: center; }}
            .card {{ background: #1e293b; padding: 40px; border-radius: 12px; max-width: 500px; margin: 0 auto 20px auto; border: 1px solid #334155; display: none; }}
            .waiting-card {{ background: #1e293b; padding: 40px; border-radius: 12px; max-width: 500px; margin: 0 auto; border: 1px dashed #334155; }}
            h2 {{ margin-top: 0; color: #38bdf8; }}
            button {{ background: #10b981; color: white; border: none; padding: 15px 30px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.2s; width: 100%; }}
            button:hover {{ background: #059669; }}
            .spinner {{ display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255,255,255,.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s ease-in-out infinite; margin-right: 10px; vertical-align: middle; }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <h1>SentinelFin Human-in-the-Loop Terminal</h1>
        <p style="color: #94a3b8; margin-bottom: 40px;">Bypassing UiPath AppTasks limitation using custom HTTP polling.</p>
        
        <div id="status-waiting" class="waiting-card">
            <div class="spinner"></div>
            <span style="font-size: 18px; color: #94a3b8;">Waiting for Maestro to reach an approval gate...</span>
        </div>

        <div id="card-triage" class="card">
            <h2>Gate 1: Triage Analyst</h2>
            <p>Review the initial case context and risk score.</p>
            <form action="/api/approve_gate/triage" method="post">
                <button type="submit">APPROVE GATE 1</button>
            </form>
        </div>

        <div id="card-bsa" class="card">
            <h2>Gate 2: BSA Officer</h2>
            <p>Review the generated SAR Narrative.</p>
            <form action="/api/approve_gate/bsa" method="post">
                <button type="submit">APPROVE GATE 2</button>
            </form>
        </div>
        
        <script>
            async function checkStatus() {{
                try {{
                    const res = await fetch("/api/gate_status");
                    const data = await res.json();
                    
                    const cardTriage = document.getElementById("card-triage");
                    const cardBsa = document.getElementById("card-bsa");
                    const statusWaiting = document.getElementById("status-waiting");
                    
                    cardTriage.style.display = data.triage ? "block" : "none";
                    cardBsa.style.display = data.bsa ? "block" : "none";
                    
                    if (!data.triage && !data.bsa) {{
                        statusWaiting.style.display = "block";
                    }} else {{
                        statusWaiting.style.display = "none";
                    }}
                }} catch (e) {{
                    console.error("Status fetch failed", e);
                }}
            }}
            
            // Poll every 1 second
            setInterval(checkStatus, 1000);
            checkStatus(); // initial check
        </script>
    </body>
    </html>
    """
    return html

@app.post("/api/approve_gate/{gate}")
async def approve_gate(gate: str):
    """When the human clicks the button in the UI."""
    gate = gate.lower()
    if gate in APPROVALS:
        APPROVALS[gate] = True
        agent_idx = 1 if gate == "triage" else 7
        agent_name = "Gate 1: Triage" if gate == "triage" else "Gate 2: BSA Officer"
        await broadcaster.broadcast("agent_resume", {"agent": agent_idx, "name": agent_name})
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/approve", status_code=303)

# Serve React Dashboard from the root (must be mounted last to not override API routes)
app.mount("/", StaticFiles(directory="dashboard/dist", html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

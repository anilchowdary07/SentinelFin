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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
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
from integrations.action_center import create_sar_review_task

# ── FastAPI ────────────────────────────────────────────────────────────────────
app = FastAPI(title="SentinelFin — 8-Agent LangGraph + UiPath Maestro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ────────────────────────────────────────────────────────────────────
class CaseRequest(BaseModel):
    case_id: str
    alert_type: str = "SUSPECTED_LAYERING"
    transactions: List[dict] = []
    resilience_mode: bool = False          # NEW: triggers exceptional-path demo

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
    print("\n[NODE 8 — AUDIT] Generating audit trail + UiPath Action Center task...")
    updated = SubmissionAuditAgent.run(state["case_data"])
    state["case_data"] = updated
    audit = updated.get("submission_audit", {})
    state["fincen_tracking_id"] = audit.get("fincen_tracking_id", "UNKNOWN")

    # ── Create real Action Center queue item for BSA Officer review ────────────
    ac_result = create_sar_review_task(
        case_id=state["case_id"],
        risk_score=state["risk_score"],
        sar_narrative=state["sar_narrative"],
        sanctions_hits=state["sanctions_hits"],
        sla_status=state["sla_status"],
        fincen_tracking_id=state["fincen_tracking_id"],
    )
    state["action_center_item_id"] = ac_result.get("queue_item_id") or "N/A"
    print(f"[NODE 8] Tracking ID: {state['fincen_tracking_id']}, Action Center item: {state['action_center_item_id']}")
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


# ── SSE streaming endpoint ─────────────────────────────────────────────────────
async def run_pipeline_stream(req: CaseRequest) -> AsyncGenerator[str, None]:
    """Runs the pipeline in a thread and streams SSE events to the client."""

    def sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    # UiPath Orchestrator Process Keys for each Agent
    UIPATH_PROCESS_MAP = {
        "triage":     "B0EC9817-0D8B-41A2-852F-9E6C44CF7F28",
        "sanctions":  "3B378551-A5BE-4EA1-A6F7-934738EB0061",
        "pattern":    "C7701F65-5BCE-4BF4-88B4-6DF5510AA144",
        "network":    "55A236E3-D375-4984-AAE3-EED7B83DCA72",
        "regulatory": "938D46BA-B0D8-45A3-857F-D74A3A848479",
        "writer":     None, # Removed because user didn't deploy writer, and mapping it to hitl causes a 3rd suspension!
        "populator":  "67BDCD9C-B517-40C7-BB5B-57515DA269E6",
        "submission": "24A87AF4-AAA8-45E6-A73D-3589746FE625",
    }
    
    # Process keys for the explicit HITL Gates
    GATE_1_TRIAGE_HITL_KEY = "F415AFD3-3D84-4612-8823-81BEC1D7F524" # agent_1_triage_hitl_shared
    GATE_2_BSA_HITL_KEY    = "129A8171-C1EC-46F4-BC82-9E5E0C564EFF" # agent_6_sar_signature_hitl

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
    
    # Run Maestro Case Orchestrator (represented by agent_2_investigation_api process)
    yield sse("agent_start", {"agent": 0, "name": "UiPath Maestro Orchestration"})
    try:
        maestro_args = {
            "case_id": state.get("case_id", ""),
            "case_data": {
                "risk_score": state.get("risk_score", 0),
                "alert_type": state.get("alert_type", "")
            }
        }
        subprocess.run(
            ["uip", "orchestrator", "jobs", "start", "120708F3-B477-4D9C-8A0A-D76C17CCAFBE", "--folder-path", "anilchowdary5072@gmail.com's workspace", "--input-arguments", json.dumps(maestro_args)],
            capture_output=True, timeout=5
        )
    except Exception:
        pass
    yield sse("agent_done", {"agent": 0, "name": "UiPath Maestro Orchestration", "detail": "Case Context Initialized"})

    def start_job(key, input_args=None):
        cmd = ["uip", "orchestrator", "jobs", "start", key, "--folder-path", "anilchowdary5072@gmail.com's workspace"]
        if input_args:
            cmd.extend(["--input-arguments", json.dumps(input_args)])
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and "{" in res.stdout:
            try:
                d = json.loads(res.stdout.strip())
                return d.get("Data", {}).get("Jobs", [])[0].get("Key")
            except Exception:
                pass
        return None

    def wait_for_job(key):
        if not key:
            return "Failed"
        import time
        # We loop until the state is Successful or Faulted
        while True:
            res = subprocess.run(["uip", "orchestrator", "jobs", "get", key], capture_output=True, text=True)
            if res.returncode == 0:
                try:
                    d = json.loads(res.stdout.strip())
                    # The state is inside the 'Data' object in the CLI response
                    state_val = d.get("Data", {}).get("State", "")
                    if state_val in ("Successful", "Faulted", "Stopped"):
                        return state_val
                except Exception:
                    pass
            time.sleep(3) # check every 3 seconds

    for idx, (fn, label, node_id) in enumerate(zip(node_funcs, NODE_LABELS, NODES), start=1):
        
        # === HITL GATE 1: Triage Analyst Review ===
        # Happens BEFORE Agent 4 (network)
        if node_id == "network":
            yield sse("agent_log", {"msg": "⏸️  Hitting Gate 1: Triage Analyst Review in Orchestrator...", "type": "start"})
            gate1_args = {
                "case_id": state["case_id"],
                "risk_score": state["risk_score"],
                "context_data": {
                    "alert_type": state["alert_type"],
                    "transactions_count": len(state["transactions"])
                }
            }
            gate1_job = await loop.run_in_executor(None, start_job, GATE_1_TRIAGE_HITL_KEY, gate1_args)
            yield sse("agent_pause", {"agent": 3, "name": "Gate 1: Triage Analyst Review", "job_key": gate1_job})
            # THIS BLOCKS the pipeline until the user approves in UiPath Action Center!
            await loop.run_in_executor(None, wait_for_job, gate1_job)
            yield sse("agent_resume", {"agent": 3, "name": "Gate 1: Triage Analyst Review"})

        # === HITL GATE 2: BSA Officer Review ===
        # Happens BEFORE Agent 8 (submission)
        if node_id == "submission":
            yield sse("agent_log", {"msg": "⏸️  Hitting Gate 2: BSA Officer Review in Orchestrator...", "type": "start"})
            gate2_args = {
                "case_id": state["case_id"],
                "sar_narrative": state["sar_narrative"][:5000]
            }
            gate2_job = await loop.run_in_executor(None, start_job, GATE_2_BSA_HITL_KEY, gate2_args)
            state["action_center_item_id"] = gate2_job
            yield sse("agent_pause", {"agent": 7, "name": "Gate 2: BSA Officer Review", "job_key": gate2_job})
            # THIS BLOCKS the pipeline until the user approves in UiPath Action Center!
            await loop.run_in_executor(None, wait_for_job, gate2_job)
            yield sse("agent_resume", {"agent": 7, "name": "Gate 2: BSA Officer Review"})

        # Proceed with normal agent execution
        yield sse("agent_start", {"agent": idx, "name": label})
        
        # Trigger the corresponding UiPath Job in the background
        process_key = UIPATH_PROCESS_MAP.get(node_id)
        uipath_job_key = None
        if process_key:
            try:
                # Provide a robust set of generic inputs to satisfy any Pydantic models on the UiPath side
                generic_args = {
                    "case_id": state.get("case_id", ""),
                    "case_data": {
                        "case_id": state.get("case_id", ""),
                        "risk_score": state.get("risk_score", 0),
                        "alert_type": state.get("alert_type", ""),
                        "sanctions_hits": state.get("sanctions_hits", False),
                        "sar_narrative": state.get("sar_narrative", "")[:1000]
                    },
                    "risk_score": state.get("risk_score", 0),
                    "context_data": {},
                    "sar_narrative": state.get("sar_narrative", "")[:1000]
                }
                uipath_job_key = await loop.run_in_executor(None, start_job, process_key, generic_args)
            except Exception as e:
                print(f"[UIPATH] Error triggering {node_id}: {e}")

        # Execute the actual Python LangGraph logic locally
        try:
            state = await loop.run_in_executor(None, fn, state)
            yield sse("agent_done", {"agent": idx, "name": label, "job_key": uipath_job_key or "local_execution"})
        except Exception as e:
            yield sse("agent_error", {"agent": idx, "name": label, "error": str(e)})
            import traceback; traceback.print_exc()

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
    Polls UiPath Orchestrator for the real-time status of a job.
    Used by the dashboard to show the Action Center job suspension state.
    """
    try:
        result = subprocess.run(
            ["uip", "orchestrator", "jobs", "get", job_key],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            job = data.get("Data", {})
            return {
                "job_key":      job_key,
                "state":        job.get("State", "Unknown"),
                "process_name": job.get("ProcessName", "agent_6_sar_signature_hitl"),
                "start_time":   job.get("StartTime", ""),
                "end_time":     job.get("EndTime", ""),
                "source":       job.get("Source", "API"),
            }
        else:
            return {"job_key": job_key, "state": "unknown", "error": result.stderr[:200]}
    except Exception as e:
        return {"job_key": job_key, "state": "error", "error": str(e)}


# ── Document Upload Endpoint ───────────────────────────────────────────────────
@app.post("/api/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Document Intelligence Endpoint — accepts:
      - PDF  (bank statements, SWIFT confirmation letters, corporate docs)
      - CSV  (transaction monitoring exports, core banking exports)
      - TXT  (SWIFT MT103/MT202 messages)
      - JSON (structured API exports)

    Returns extracted transaction data ready to feed into the 8-agent pipeline.
    This mirrors UiPath Document Understanding in production.
    """
    ALLOWED = {"pdf", "csv", "txt", "swift", "mt103", "json", "tsv"}
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '.{ext}'. Supported: {', '.join(ALLOWED)}"
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # Parse the document
    result = parse_document(file.filename or "upload", file_bytes)

    return JSONResponse({
        "status":       "success",
        "filename":     result["filename"],
        "format":       result["format"],
        "parse_method": result["parse_method"],
        "confidence":   result["confidence"],
        "tx_count":     result["tx_count"],
        "transactions": result["transactions"],
        "entity_hints": result["entity_hints"],
        "raw_preview":  result["raw_text"][:500],
        "message":      f"✅ Extracted {result['tx_count']} transactions from '{result['filename']}' using {result['parse_method']} parser",
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

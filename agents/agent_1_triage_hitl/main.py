from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
import datetime


class InvestigationState(TypedDict):
    case_id: str
    risk_score: int
    context_data: dict
    approval_status: str


class Input(BaseModel):
    case_id: str = Field(description="The unique case ID from Maestro.")
    risk_score: int = Field(description="The calculated risk score (0-100).")
    context_data: dict = Field(description="The transaction context and entity data.")


class Output(BaseModel):
    approval_status: str = Field(
        description="The decision from the human reviewer: 'approved', 'rejected', or 'escalated'."
    )


def triage_node(state: InvestigationState) -> Command:
    """
    Gate 1: AML Analyst Triage Review.

    Uses LangGraph interrupt() to pause execution and suspend the Orchestrator job.
    The analyst sees the full case context in the Orchestrator UI and resumes the 
    job with their decision. This is the API Trigger HITL pattern.

    Resume the job with: {'status': 'approved'} | {'status': 'rejected'} | {'status': 'escalated'}
    """
    risk = state["risk_score"]
    severity = "HIGH" if risk >= 75 else "MEDIUM" if risk >= 40 else "LOW"

    resume_payload = interrupt({
        "gate": "Gate 1 — AML Analyst Triage Review",
        "case_id": state["case_id"],
        "risk_score": risk,
        "risk_severity": severity,
        "context_summary": state.get("context_data", {}),
        "timestamp_utc": str(datetime.datetime.utcnow().isoformat()),
        "instructions": (
            f"Case {state['case_id']} has been flagged with risk score {risk}/100 ({severity}). "
            "Review the context data above. Resume this job with "
            "{'status': 'approved'} to proceed to full investigation, "
            "{'status': 'rejected'} to close the case, or "
            "{'status': 'escalated'} to escalate to senior analyst."
        )
    })

    import json
    if isinstance(resume_payload, str):
        try:
            resume_payload = json.loads(resume_payload)
        except Exception:
            resume_payload = {"status": resume_payload}
            
    if isinstance(resume_payload, dict):
        decision = resume_payload.get("status", "approved")
    else:
        decision = "approved"

    return {"approval_status": decision}


workflow = StateGraph(InvestigationState, input_schema=Input, output_schema=Output)
workflow.add_node("triage", triage_node)
workflow.add_edge(START, "triage")
workflow.add_edge("triage", END)
compiled_graph = workflow.compile()

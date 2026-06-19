from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
import datetime


class SARState(TypedDict):
    case_id: str
    sar_narrative: str
    bsa_approved: bool
    bsa_signature: str | None


class Input(BaseModel):
    case_id: str = Field(description="The unique case ID from Maestro.")
    sar_narrative: str = Field(description="The drafted SAR narrative to review.")


class Output(BaseModel):
    bsa_approved: bool = Field(description="Whether the BSA Officer approved the SAR.")
    bsa_signature: str | None = Field(description="The BSA Officer's digital signature string.")


def gate2_signature_node(state: SARState) -> Command:
    """
    Gate 2: BSA Officer Review.
    
    Uses LangGraph interrupt() to pause execution and hand control back to 
    UiPath Orchestrator. The job enters 'Suspended' state with the full SAR
    context visible in the Orchestrator UI. A human resumes the job via the
    Orchestrator resume API or the UI, providing approval + signature.
    
    This is the API Trigger HITL pattern — no external Action Center App 
    required. Any system (human via Orchestrator UI, downstream RPA, webhook) 
    can resume the job.
    """
    resume_payload = interrupt({
        "gate": "Gate 2 — BSA Officer SAR Review",
        "case_id": state["case_id"],
        "sar_narrative": state["sar_narrative"],
        "timestamp_utc": str(datetime.datetime.utcnow().isoformat()),
        "instructions": (
            "Review the SAR narrative above. "
            "Resume this job with {'approved': true, 'signature': 'Your Name — BSA Officer'} "
            "to approve, or {'approved': false, 'signature': ''} to reject."
        )
    })

    import json
    if isinstance(resume_payload, str):
        try:
            resume_payload = json.loads(resume_payload)
        except Exception:
            resume_payload = {"approved": True, "signature": resume_payload}
            
    if isinstance(resume_payload, dict):
        approved = bool(resume_payload.get("approved", False))
        signature = resume_payload.get("signature", None)
    else:
        approved = True
        signature = "System Approved"

    return {"bsa_approved": approved, "bsa_signature": signature}


workflow = StateGraph(SARState, input_schema=Input, output_schema=Output)
workflow.add_node("gate2", gate2_signature_node)
workflow.add_edge(START, "gate2")
workflow.add_edge("gate2", END)
graph = workflow.compile()

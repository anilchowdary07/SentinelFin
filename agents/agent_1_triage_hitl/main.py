from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from uipath.platform.common import CreateTask
from pydantic import BaseModel, Field
import datetime

class InvestigationState(TypedDict):
    case_id: str
    risk_score: int
    context_data: dict
    approval_status: str

class Input(BaseModel):
    case_id: str = Field(description="The unique case ID from Maestro.")
    risk_score: int = Field(description="The calculated risk score.")
    context_data: dict = Field(description="The transactions and context.")

class Output(BaseModel):
    approval_status: str = Field(description="The status returned by the human reviewer.")

def triage_node(state: InvestigationState) -> Command:
    # We raise an interrupt to send a task to Action Center in Orchestrator
    task_output = interrupt(CreateTask(
        app_name="MaestroTriageGate",
        app_folder_path="Shared",
        title=f"Gate 1 Triage Review: Case {state['case_id']} (Risk: {state['risk_score']})",
        data={
            "case_id": state["case_id"],
            "risk_score": state["risk_score"],
            "timestamp": str(datetime.datetime.now())
        },
        assignee="analyst@example.com"
    ))
    
    return Command(update={
        "approval_status": task_output.get("status", "pending")
    })

workflow = StateGraph(InvestigationState)
workflow.add_node("triage", triage_node)
workflow.add_edge(START, "triage")
workflow.add_edge("triage", END)
compiled_graph = workflow.compile()

def main(input_data: Input) -> Output:
    initial_state = {
        "case_id": input_data.case_id,
        "risk_score": input_data.risk_score,
        "context_data": input_data.context_data,
        "approval_status": "pending"
    }
    
    final_state = compiled_graph.invoke(initial_state)
    return Output(approval_status=final_state.get("approval_status", "pending"))

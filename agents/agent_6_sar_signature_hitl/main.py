from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from uipath.platform.common import CreateTask
from pydantic import BaseModel, Field
import datetime

class SARState(TypedDict):
    case_id: str
    sar_narrative: str
    bsa_signature: str | None

class Input(BaseModel):
    case_id: str = Field(description="The unique case ID from Maestro.")
    sar_narrative: str = Field(description="The drafted SAR narrative from Agent 6.")

class Output(BaseModel):
    bsa_signature: str | None = Field(description="The captured BSA Officer's digital signature.")

def gate2_signature_node(state: SARState) -> Command:
    # We raise an interrupt to send a task to Action Center in Orchestrator
    # The BSA Officer must review the SAR narrative and provide a signature.
    task_output = interrupt(CreateTask(
        app_name="BSASignatureGate",
        app_folder_path="Shared",
        title=f"Gate 2 BSA Review: Final Approval for SAR {state['case_id']}",
        data={
            "case_id": state["case_id"],
            "sar_narrative": state["sar_narrative"],
            "timestamp": str(datetime.datetime.now())
        },
        assignee="bsa_officer@example.com"
    ))
    
    # We extract the signature from the task output that the human provided
    signature = task_output.get("bsa_signature", None)
    
    return Command(update={
        "bsa_signature": signature
    })

workflow = StateGraph(SARState)
workflow.add_node("gate2", gate2_signature_node)
workflow.add_edge(START, "gate2")
workflow.add_edge("gate2", END)
compiled_graph = workflow.compile()

def main(input_data: Input) -> Output:
    initial_state = {
        "case_id": input_data.case_id,
        "sar_narrative": input_data.sar_narrative,
        "bsa_signature": None
    }
    
    final_state = compiled_graph.invoke(initial_state)
    return Output(bsa_signature=final_state.get("bsa_signature"))

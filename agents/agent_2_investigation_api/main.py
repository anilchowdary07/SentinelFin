import json
import requests
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    case_id: str
    risk_score: int
    sar_narrative: str

def call_api(state: AgentState):
    case_id = state.get("case_id", "CASE-123")
    
    # Payload for the backend investigation pipeline
    payload = {
        "case_id": case_id,
        "alert_type": "SUSPECTED_LAYERING",
        "transactions": [
            {"txn_id":"TXN-201","date":"2024-05-10T09:00:00Z","amount":250000,"type":"WIRE_IN","originator":{"name":"Unknown Entity A","country":"Cayman Islands","account":"CY-999123"},"beneficiary":{"account":"ACC-554433"}},
            {"txn_id":"TXN-202","date":"2024-05-11T11:30:00Z","amount":120000,"type":"WIRE_OUT","originator":{"account":"ACC-554433"},"beneficiary":{"name":"Shell Corp B","country":"Panama","account":"PA-888456"}},
            {"txn_id":"TXN-203","date":"2024-05-11T14:45:00Z","amount":125000,"type":"WIRE_OUT","originator":{"account":"ACC-554433"},"beneficiary":{"name":"Holdings C","country":"Cyprus","account":"CP-777789"}}
        ],
        "force_api_failure": False
    }
    
    import os
    url = os.getenv("API_BASE_URL", "http://localhost:8000/api/investigate")
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return {
            "risk_score": data.get("final_risk_score", 85),
            "sar_narrative": data.get("sar_narrative", "API connection succeeded but narrative missing.")
        }
    except Exception as e:
        return {
            "risk_score": 99,
            "sar_narrative": f"API Error: {str(e)}"
        }

workflow = StateGraph(AgentState)
workflow.add_node("call_api", call_api)
workflow.add_edge(START, "call_api")
workflow.add_edge("call_api", END)
graph = workflow.compile()

def main(args: dict):
    initial_state = {"case_id": args.get("case_id", "CASE-DEFAULT")}
    final_state = graph.invoke(initial_state)
    return {
        "case_id": final_state.get("case_id"),
        "risk_score": final_state.get("risk_score"),
        "sar_narrative": final_state.get("sar_narrative")
    }

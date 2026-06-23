import re

with open("main.py", "r") as f:
    content = f.read()

# The chunk we want to extract/remove
chunk = """@app.post("/api/maestro/investigate")
async def maestro_investigate(req: CaseRequest):
    \"\"\"
    Synchronous endpoint for the UiPath Maestro Service Task.
    Runs the entire LangGraph pipeline and returns the structured JSON payload.
    WARNING: Depending on LLM latency, this could trigger a timeout in Maestro.
    If timeout occurs (>60s), this architecture must be refactored to an async webhook pattern.
    \"\"\"
    print(f"\\n[MAESTRO CASE INITIATED] Processing Case {req.case_id} synchronously...")
    
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
        "action_center_item_id": ""
    }

    # Run the graph synchronously
    try:
        final_state = await investigation_graph.ainvoke(initial_state)
        return JSONResponse(content={
            "case_id": final_state.get("case_id"),
            "risk_score": final_state.get("risk_score"),
            "sanctions_hits": final_state.get("sanctions_hits"),
            "sar_narrative": final_state.get("sar_narrative"),
            "fincen_form_111": final_state.get("fincen_form_111"),
            "status": "COMPLETED"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

if chunk in content:
    content = content.replace(chunk, "")
    
    # Now append it right before the run_pipeline_stream
    target = "async def run_pipeline_stream"
    
    content = content.replace(target, chunk + "\n\n" + target)
    
    with open("main.py", "w") as f:
        f.write(content)
    print("Fixed!")
else:
    print("Chunk not found!")


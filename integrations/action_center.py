"""
integrations/action_center.py

Creates a real UiPath Action Center Task by triggering the agent_6_sar_signature_hitl
process in Orchestrator. This process uses LangGraph interrupt() to genuinely
suspend the job and create a task for the BSA Officer in Action Center.
"""

import subprocess
import json
import datetime
import os

PROCESS_KEY  = "129A8171-C1EC-46F4-BC82-9E5E0C564EFF" # agent_6_sar_signature_hitl
FOLDER_PATH = "anilchowdary5072@gmail.com's workspace"


def create_sar_review_task(
    case_id: str,
    risk_score: int,
    sar_narrative: str,
    sanctions_hits: bool,
    sla_status: str,
    fincen_tracking_id: str,
) -> dict:
    """
    Creates a real UiPath Action Center task by triggering the agent_6_sar_signature_hitl
    Coded Agent process in Orchestrator. The process uses LangGraph's interrupt()
    to natively suspend the job and create an Action Center task for the BSA Officer.
    """
    # Build narrative with rich context for the Action Center reviewer
    enriched_narrative = (
        f"**RISK SCORE:** {risk_score}/100\n"
        f"**SANCTIONS HIT:** {sanctions_hits}\n"
        f"**SLA:** {sla_status}\n"
        f"**FINCEN ID:** {fincen_tracking_id}\n\n"
        f"{sar_narrative}"
    )

    input_args = {
        "case_id": case_id,
        "sar_narrative": enriched_narrative[:5000] # Safe limit
    }

    try:
        result = subprocess.run(
            [
                "uip", "orchestrator", "jobs", "start",
                PROCESS_KEY,
                "--folder-path", FOLDER_PATH,
                "--input-arguments", json.dumps(input_args),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout.strip()
        if result.returncode == 0:
            data = json.loads(output) if output.startswith("{") else {}
            jobs = data.get("Data", {}).get("Jobs", [])
            job_key = jobs[0].get("Key") if jobs else "created"
            
            print(f"[ACTION CENTER] ✅ Job triggered for Action Center task. Job Key: {job_key}")
            return {
                "success":       True,
                "queue_item_id": str(job_key),
                "queue_name":    "Action Center (Job Suspended)",
                "message":       f"Real Action Center Task created via Job Suspension. Job: {job_key}",
            }
        else:
            print(f"[ACTION CENTER] ⚠️  Exit {result.returncode}: {output[:200]}")
            return {"success": False, "queue_item_id": "err", "message": output[:200]}

    except Exception as e:
        print(f"[ACTION CENTER] ❌ {e}")
        return {"success": False, "queue_item_id": "err", "message": str(e)}

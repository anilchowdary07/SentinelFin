"""
integrations/action_center.py

Creates a real UiPath Action Center Task using the UiPath Automation Cloud REST API.
"""

from integrations.uipath_api import UiPathAPI

def create_sar_review_task(
    case_id: str,
    risk_score: int,
    sar_narrative: str,
    sanctions_hits: bool,
    sla_status: str,
    fincen_tracking_id: str,
) -> dict:
    """
    Creates a real UiPath Action Center External Task via Orchestrator REST API.
    """
    # Build data object for the Action Center reviewer
    enriched_data = {
        "case_id": case_id,
        "risk_score": risk_score,
        "sanctions_hits": sanctions_hits,
        "sla_status": sla_status,
        "fincen_tracking_id": fincen_tracking_id,
        "sar_narrative": sar_narrative[:5000] # Safe limit
    }

    try:
        task_id = UiPathAPI.create_action_center_task(
            title=f"SAR Review Required - {fincen_tracking_id}",
            data=enriched_data
        )

        if task_id:
            return {
                "success":       True,
                "queue_item_id": task_id,
                "queue_name":    "Action Center (REST API)",
                "message":       f"Real Action Center Task created via REST API. Task ID: {task_id}",
            }
        else:
            return {"success": False, "queue_item_id": "err", "message": "Failed to create task. Check API credentials or Orchestrator folders."}

    except Exception as e:
        print(f"[ACTION CENTER] ❌ {e}")
        return {"success": False, "queue_item_id": "err", "message": str(e)}

import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
folder_id = UiPathAPI.get_default_folder_id(token)
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/tasks/GenericTasks/CreateTask"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-UIPATH-OrganizationUnitId": str(folder_id)
}

payload = {
    "title": "Suspicious Activity Report Review",
    "priority": "High",
    "type": "FormTask",
    "data": {"RiskScore": 85, "Summary": "Money Laundering detected."},
    "formLayout": {
        "components": [
            {
                "type": "textfield",
                "key": "RiskScore",
                "label": "AI Risk Score",
                "disabled": True,
                "input": True
            },
            {
                "type": "textarea",
                "key": "Summary",
                "label": "SAR Narrative Summary",
                "input": True
            },
            {
                "type": "button",
                "label": "Approve & Submit to FinCEN",
                "key": "submit",
                "input": True,
                "action": "Submit"
            }
        ]
    }
}

resp = requests.post(url, json=payload, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.text)

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

def test_type(t):
    payload = {
        "title": "Test",
        "priority": "High",
        "type": t,
        "data": {"RiskScore": 85}
    }
    resp = requests.post(url, json=payload, headers=headers)
    print(f"TEST {t}: {resp.status_code} {resp.text}")

test_type("QuickFormTask")
test_type("Task")
test_type("Action")
test_type("Form")
test_type("ExternalTask")

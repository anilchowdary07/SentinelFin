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
    "title": "Test External Task",
    "priority": "High",
    "type": "ExternalTask",
    "data": {"test": 123},
    "externalTag": "SentinelFin-BSA-Review"
}

resp = requests.post(url, json=payload, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.text)

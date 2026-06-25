import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
folder_id = UiPathAPI.get_default_folder_id(token)
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/odata/FormTasks/UiPath.Server.Configuration.OData.CreateFormTask"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-UIPATH-OrganizationUnitId": str(folder_id)
}

payload = {
    "taskCreateRequest": {
        "Title": "Test UI",
        "Priority": "High",
        "TaskCatalogName": "Default",
        "Data": {"RiskScore": 85},
        "FormLayout": {"components": [{"type": "textfield", "key": "RiskScore", "label": "Risk Score", "input": True}]}
    }
}

resp = requests.post(url, json=payload, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.text)

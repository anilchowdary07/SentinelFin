import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
folder_id = UiPathAPI.get_default_folder_id(token)
task_id = 4269747 # from user screenshot
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/odata/Tasks({task_id})/UiPath.Server.Configuration.OData.AddComment"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-UIPATH-OrganizationUnitId": str(folder_id)
}

payload = {
    "Text": "Testing comment from API! Risk Score: 85"
}

resp = requests.post(url, json=payload, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.text)

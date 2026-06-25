import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
folder_id = UiPathAPI.get_default_folder_id(token)
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/odata/TaskSchemas"

headers = {
    "Authorization": f"Bearer {token}",
    "X-UIPATH-OrganizationUnitId": str(folder_id)
}
resp = requests.get(url, headers=headers)
print("STATUS:", resp.status_code)
print("RESPONSE:", resp.text)

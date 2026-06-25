import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/swagger/v12.0/swagger.json"

resp = requests.get(url)
with open("swagger.json", "w") as f:
    f.write(resp.text)

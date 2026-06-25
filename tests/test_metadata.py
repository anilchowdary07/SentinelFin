import dotenv, requests, json
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI

creds = UiPathAPI.get_credentials()
token = UiPathAPI.get_access_token()
url = f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/odata/$metadata"

headers = {
    "Authorization": f"Bearer {token}",
}
resp = requests.get(url, headers=headers)
with open("metadata.xml", "w") as f:
    f.write(resp.text)
print("Metadata saved to metadata.xml")

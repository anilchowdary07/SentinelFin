import dotenv
dotenv.load_dotenv()
from integrations.uipath_api import UiPathAPI
import requests

creds = UiPathAPI.get_credentials()
url = "https://cloud.uipath.com/identity_/connect/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": creds["client_id"],
    "client_secret": creds["client_secret"],
    "scope": "OR.Tasks OR.Folders"
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    response = requests.post(url, data=payload, headers=headers, timeout=10)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text[:200])
except Exception as e:
    print("ERROR:", e)

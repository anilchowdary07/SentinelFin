import os
import requests
import json
import traceback

class UiPathAPI:
    """Live Integration with UiPath Automation Cloud via REST API."""
    
    @staticmethod
    def get_credentials():
        return {
            "client_id": os.getenv("UIPATH_CLIENT_ID"),
            "client_secret": os.getenv("UIPATH_CLIENT_SECRET"),
            "org": os.getenv("UIPATH_ORG"),
            "tenant": os.getenv("UIPATH_TENANT"),
        }

    @staticmethod
    def get_access_token() -> str:
        """Exchange Client ID and Secret for an OAuth Bearer Token."""
        creds = UiPathAPI.get_credentials()
        if not creds["client_id"] or not creds["client_secret"]:
            print("[UIPATH API] Error: Missing Client ID or Secret in .env")
            return None

        url = "https://staging.uipath.com/identity_/connect/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "scope": "OR.Tasks OR.Folders OR.BackgroundTasks OR.Tasks.Write OR.Tasks.Read OR.Queues"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            print("[UIPATH API] Requesting OAuth token...")
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            token = response.json().get("access_token")
            print("[UIPATH API] Successfully obtained OAuth Bearer token.")
            return token
        except requests.exceptions.RequestException as e:
            print(f"[UIPATH API] Failed to get access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[UIPATH API] Response details: {e.response.text}")
            return None

    @staticmethod
    def push_to_data_service(payload: dict) -> bool:
        """Attempt to push extracted entity records to a UiPath Data Service Entity (table)."""
        token = UiPathAPI.get_access_token()
        if not token:
            return False

        creds = UiPathAPI.get_credentials()
        entity_name = "SentinelFin_SAR_Records"
        url = f"https://staging.uipath.com/{creds['org']}/{creds['tenant']}/dataservice_/odata/{entity_name}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"[UIPATH API] Attempting to push record to Data Service Entity '{entity_name}'...")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            print("[UIPATH API] Successfully synced record to Data Service.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[UIPATH API] Data Service push failed (Expected if '{entity_name}' schema does not exist): {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[UIPATH API] Data Service Response: {e.response.text}")
            return False

    @staticmethod
    def get_default_folder_id(token: str) -> str:
        """Fetch the OrganizationUnitId for the 'Default' or first available Orchestrator Folder."""
        creds = UiPathAPI.get_credentials()
        url = f"https://staging.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/odata/Folders"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            folders = response.json().get("value", [])
            if folders:
                folder_id = folders[0]["Id"]
                folder_name = folders[0]["DisplayName"]
                print(f"[UIPATH API] Found Orchestrator Folder: {folder_name} (ID: {folder_id})")
                return str(folder_id)
            else:
                print("[UIPATH API] No folders found in Orchestrator.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[UIPATH API] Failed to fetch Orchestrator Folders: {e}")
            return None

    @staticmethod
    def create_action_center_task(title: str, data: dict) -> str:
        """Create a real Action Center External Task in Orchestrator waiting for Human-in-the-Loop review."""
        token = UiPathAPI.get_access_token()
        if not token:
            return None

        folder_id = UiPathAPI.get_default_folder_id(token)
        if not folder_id:
            return None

        creds = UiPathAPI.get_credentials()
        url = f"https://staging.uipath.com/{creds['org']}/{creds['tenant']}/orchestrator_/tasks/GenericTasks/CreateTask"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(folder_id)
        }

        import urllib.parse
        import json
        encoded_title = urllib.parse.quote(title)
        encoded_data = urllib.parse.quote(json.dumps(data))
        import os
        base_url = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173")
        task_url = f"{base_url}/preview?title={encoded_title}&data={encoded_data}"

        payload = {
            "title": title,
            "priority": "High",
            "type": "ExternalTask",
            "action": "Review Suspicious Activity Report",
            "data": data,
            "externalTag": "SentinelFin-BSA-Review",
            "taskUrl": task_url
        }

        print(f"[UIPATH API] Creating Action Center task in Orchestrator...")
        print(f"[UIPATH API] 🚀 UI Preview Template generated: {task_url}")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            task_info = response.json()
            task_id = task_info.get("Id")
            print(f"[UIPATH API] Action Center Task created successfully! Task ID: {task_id}")
            return str(task_id)
        except requests.exceptions.RequestException as e:
            print(f"[UIPATH API] Failed to create Action Center Task: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[UIPATH API] Orchestrator Response: {e.response.text}")
            return None

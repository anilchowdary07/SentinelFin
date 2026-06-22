import os
import requests
import json

class SlackNotifier:
    """Real Slack Notifier for sending alerts to compliance channels."""
    
    @staticmethod
    def send_alert(message: str) -> bool:
        """Send a real Slack message via Webhook."""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        if not webhook_url:
            print(f"[SLACK MOCK] Webhook URL not set. Message: {message}")
            return True
            
        print(f"[SLACK] Dispatching real alert to workspace...")
        try:
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[SLACK ERROR] Failed to send message: {e}")
            return False

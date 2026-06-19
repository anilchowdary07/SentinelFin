class SlackNotifier:
    """Mock Slack Notifier for sending alerts to compliance channels."""
    
    @staticmethod
    def send_alert(channel: str, message: str) -> bool:
        """Simulate sending a Slack message."""
        print(f"[SLACK MOCK] Channel: {channel} | Message: {message}")
        return True

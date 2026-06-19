import json
import os

class AlertIntakeSystem:
    """
    Handles alert ingestion and duplicate detection.
    Exception Handling Requirement: Duplicate alert on same account within active 
    case window -> merge into existing case rather than opening a second one.
    """
    
    _active_cases = {
        "ACC-998877": "CAS-2024-001" # Structuring case is active
    }
    
    @classmethod
    def ingest_alert(cls, alert_data: dict) -> str:
        account_id = alert_data.get("primary_subject", {}).get("account_id")
        
        if account_id in cls._active_cases:
            existing_case_id = cls._active_cases[account_id]
            print(f"[INTAKE] [MERGE] Duplicate alert detected for account {account_id}.")
            print(f"Merging new transaction data into existing case {existing_case_id} instead of opening a new case.")
            return existing_case_id
            
        new_case_id = f"CAS-{os.urandom(4).hex().upper()}"
        cls._active_cases[account_id] = new_case_id
        print(f"[INTAKE] Opened new case {new_case_id} for account {account_id}.")
        return new_case_id

if __name__ == "__main__":
    # Test duplicate ingestion
    new_alert = {
        "primary_subject": {"account_id": "ACC-998877"},
        "alert_type": "HIGH_VELOCITY",
        "transactions": [{"amount": 1000}]
    }
    AlertIntakeSystem.ingest_alert(new_alert)

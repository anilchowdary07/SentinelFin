import json
import os
from typing import Dict, Any

MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")

class CoreBankingAPI:
    """Mock Core Banking System API for retrieving KYC and transaction history."""
    
    @staticmethod
    def get_customer_profile(account_id: str) -> Dict[str, Any]:
        """Fetch the KYC profile and risk rating for an account."""
        # In a real system, this would query the core banking database.
        # For the hackathon, we pull from the mock scenarios to ensure consistency.
        
        for filename in os.listdir(MOCK_DATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(MOCK_DATA_DIR, filename), 'r') as f:
                    data = json.load(f)
                    if data.get("primary_subject", {}).get("account_id") == account_id:
                        return data.get("primary_subject", {})
        
        return {"error": "Account not found"}

    @staticmethod
    def get_transaction_history(account_id: str, days: int = 90) -> list:
        """Fetch transaction history for the last X days."""
        # Find transactions in the mock scenarios related to this account
        transactions = []
        for filename in os.listdir(MOCK_DATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(MOCK_DATA_DIR, filename), 'r') as f:
                    data = json.load(f)
                    if data.get("primary_subject", {}).get("account_id") == account_id:
                        transactions.extend(data.get("transactions", []))
        
        if not transactions:
            return [{"error": "No transactions found for account"}]
            
        return transactions

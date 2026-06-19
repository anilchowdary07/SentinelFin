import datetime

class ContextEnrichmentAgent:
    @staticmethod
    def run(case_data: dict) -> dict:
        """
        Agent 1: Context Enrichment
        Simulates fetching 90-day transaction history and KYC records from a Core Banking System.
        """
        print("[AGENT 1] Starting Context Enrichment...")
        
        # Simulate KYC lookup
        kyc_data = {
            "account_age_days": 450,
            "kyc_status": "VERIFIED",
            "risk_rating": "HIGH",
            "business_type": "Import/Export",
            "expected_monthly_volume": 500000
        }
        
        # Simulate 90-day history volume calculation
        historical_volume = sum(txn.get('amount', 0) for txn in case_data.get('transactions', [])) * 1.5
        
        enriched_data = case_data.copy()
        enriched_data['context'] = {
            "kyc": kyc_data,
            "90_day_historical_volume": historical_volume,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        print("[AGENT 1] Enrichment Complete.")
        return enriched_data

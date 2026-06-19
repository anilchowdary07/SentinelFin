import time
import requests

class SanctionsScreenerAgent:
    @staticmethod
    def run(case_data: dict, force_api_failure: bool = False) -> dict:
        """
        Agent 2: Sanctions Screener
        Screens all entities against a mock OFAC sanctions API.
        Includes a Resilience Demo mode (Controlled Crash).
        """
        print("[AGENT 2] Starting Sanctions Screening...")
        
        entities_to_screen = []
        for txn in case_data.get('transactions', []):
            if 'originator' in txn and txn['originator'].get('name'):
                entities_to_screen.append(txn['originator']['name'])
            if 'beneficiary' in txn and txn['beneficiary'].get('name'):
                entities_to_screen.append(txn['beneficiary']['name'])
                
        # Deduplicate
        entities_to_screen = list(set(entities_to_screen))
        print(f"[AGENT 2] Entities to screen: {entities_to_screen}")
        
        # Resilience Demo Mode: Controlled Crash
        if force_api_failure:
            print("\n[AGENT 2 ⚠️ RESILIENCE DEMO] Triggering controlled API failure...")
            retries = 3
            backoff = 1
            for attempt in range(retries):
                print(f"[AGENT 2] Attempt {attempt + 1}: POST https://api.treasury.gov/ofac/v1/screen")
                try:
                    # Simulate an actual HTTP 500 error from a remote server
                    response = requests.get("https://httpstat.us/500", timeout=2)
                    response.raise_for_status()
                except Exception as e:
                    print(f"[AGENT 2] 🚨 ConnectionError: OFAC API Unavailable (HTTP 500). Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2  # Exponential backoff
            
            print("[AGENT 2] 🚨 CRITICAL: Max retries exceeded. Falling back to cached local sanctions list to prevent workflow failure.")
            # Graceful degradation
        
        # Simulate screening results (Mock API response)
        sanctions_hits = []
        for entity in entities_to_screen:
            # We hardcode 'Shell Corp B' as a hit for demonstration purposes
            if 'Shell Corp' in entity:
                sanctions_hits.append({
                    "entity": entity,
                    "list": "SDN",
                    "match_confidence": 98.5
                })
        
        case_data['sanctions_results'] = {
            "hits": sanctions_hits,
            "status": "COMPLETED" if not force_api_failure else "DEGRADED_CACHED"
        }
        
        print(f"[AGENT 2] Screening Complete. Found {len(sanctions_hits)} hits.")
        return case_data

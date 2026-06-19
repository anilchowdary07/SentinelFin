import time
import random

class OFACSanctionsAPI:
    """Mock OFAC Sanctions and PEP Screening API."""
    
    _fail_count = 0
    
    @classmethod
    def screen_party(cls, name: str, country: str = None) -> dict:
        """
        Screens a name against mock SDN, UN, EU, and PEP lists.
        Simulates API timeouts/failures for exception handling testing.
        """
        # Exception Handling Requirement: Sanctions API timeout -> retry with exponential backoff
        # Let's simulate a failure every 3rd call to force the retry logic to trigger.
        cls._fail_count += 1
        if cls._fail_count % 3 == 0:
            raise TimeoutError("OFAC API Connection Timeout (Simulated)")
        
        name_lower = name.lower()
        
        # Hardcoded hits for our mock scenarios
        if "shell corp b" in name_lower:
            return {
                "status": "HIT",
                "lists_matched": ["EU_ASSET_FREEZE", "OFAC_SDN"],
                "match_score": 0.98,
                "remarks": "Known shell company associated with sanctioned entity in Panama."
            }
            
        if "unknown entity a" in name_lower:
            return {
                "status": "HIT",
                "lists_matched": ["PEP"],
                "match_score": 0.85,
                "remarks": "Possible match to Politically Exposed Person (PEP)."
            }
            
        return {
            "status": "CLEAR",
            "lists_matched": [],
            "match_score": 0.0,
            "remarks": "No matching records found."
        }

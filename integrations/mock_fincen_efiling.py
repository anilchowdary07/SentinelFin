import json
import uuid

class FinCENEfilingAPI:
    """Mock FinCEN BSA E-Filing System API."""
    
    _fail_count = 0
    
    @classmethod
    def submit_sar(cls, sar_form_data: dict, narrative: str) -> dict:
        """
        Submits the finalized SAR form and narrative to FinCEN.
        Simulates submission errors for exception handling testing.
        """
        cls._fail_count += 1
        
        # Exception Handling Requirement: FinCEN mock submission endpoint returns an error 
        # -> retry once, then manual fallback
        if cls._fail_count % 2 == 0:
            return {
                "success": False,
                "error_code": "E-FILING-503",
                "message": "Service Temporarily Unavailable"
            }
            
        # Basic validation
        if not sar_form_data.get("filing_institution") or not sar_form_data.get("suspect_info"):
            return {
                "success": False,
                "error_code": "VAL-001",
                "message": "Missing required fields in Form 111"
            }
            
        return {
            "success": True,
            "bsa_identifier": f"BSA-{uuid.uuid4().hex[:12].upper()}",
            "status": "ACCEPTED",
            "timestamp": "2024-05-20T10:00:00Z"
        }

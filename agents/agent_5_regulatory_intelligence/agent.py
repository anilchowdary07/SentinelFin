import datetime

class RegulatoryIntelligenceAgent:
    @staticmethod
    def run(case_data: dict) -> dict:
        """
        Agent 5: Regulatory Intelligence
        Calculates hard legal deadlines for FinCEN reporting based on transaction dates.
        """
        print("\n[AGENT 5] Starting Regulatory Intelligence Calculation...")
        
        transactions = case_data.get('transactions', [])
        
        if not transactions:
            print("[AGENT 5] No transactions to evaluate.")
            return case_data
            
        # Find the date of the first suspicious transaction
        earliest_date_str = min(t['date'] for t in transactions)
        try:
            earliest_date = datetime.datetime.fromisoformat(earliest_date_str.replace('Z', '+00:00'))
        except Exception:
            earliest_date = datetime.datetime.now(datetime.timezone.utc)
            
        # FinCEN requires SAR filing within 30 days of initial detection
        # We assume detection happened on the date of the first flagged transaction for this demo.
        fincen_deadline = earliest_date + datetime.timedelta(days=30)
        days_remaining = (fincen_deadline - datetime.datetime.now(datetime.timezone.utc)).days
        
        print(f"[AGENT 5] First suspicious activity date: {earliest_date.strftime('%Y-%m-%d')}")
        print(f"[AGENT 5] FinCEN Form 111 Deadline: {fincen_deadline.strftime('%Y-%m-%d')}")
        
        if days_remaining < 0:
            status = "SLA_BREACHED"
        elif days_remaining <= 5:
            status = "CRITICAL_SLA_RISK"
        else:
            status = "COMPLIANT"
            
        print(f"[AGENT 5] SLA Status: {status} ({days_remaining} days remaining)")
        
        case_data['regulatory_context'] = {
            "initial_detection_date": earliest_date.isoformat(),
            "fincen_deadline": fincen_deadline.isoformat(),
            "days_remaining": days_remaining,
            "sla_status": status,
            "applicable_rules": ["BSA Title 31 (31 U.S.C. 5318(g))"]
        }
        
        return case_data

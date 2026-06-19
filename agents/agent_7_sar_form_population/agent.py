import datetime

class SARFormPopulationAgent:
    @staticmethod
    def run(case_data: dict, sar_narrative: str) -> dict:
        """
        Agent 7: SAR Form Population
        Maps the unstructured SAR narrative and case data into a highly structured
        JSON payload representing the FinCEN Form 111.
        """
        print("\n[AGENT 7] Starting FinCEN Form 111 Data Mapping...")
        
        # Extract the primary subject from context
        transactions = case_data.get('transactions', [])
        primary_subject = "Unknown"
        if transactions:
            # Assume the first transaction's originator or beneficiary is the primary subject
            # In a real scenario, this would be explicitly passed by Agent 4's graph logic
            primary_subject = transactions[0].get('originator', {}).get('name', 'Unknown')
            
        fincen_payload = {
            "form_type": "FinCEN Form 111",
            "filing_institution": "SentinelFin Sandbox Bank",
            "date_of_preparation": datetime.datetime.now().strftime("%Y-%m-%d"),
            "part_1_subject_information": {
                "primary_subject": primary_subject,
                "sanctions_hits_found": len(case_data.get('sanctions_results', {}).get('hits', [])) > 0
            },
            "part_2_suspicious_activity_information": {
                "amount_involved": sum(t.get('amount', 0) for t in transactions),
                "date_range": {
                    "start": min((t['date'] for t in transactions), default=""),
                    "end": max((t['date'] for t in transactions), default="")
                },
                "category": case_data.get('alert_type', "UNKNOWN_ACTIVITY")
            },
            "part_5_suspicious_activity_narrative": sar_narrative,
            "metadata": {
                "generated_by": "Agent 7 (UiPath RPA Mapping)",
                "audit_trace_id": case_data.get('alert_id', 'cas-default')
            }
        }
        
        print("[AGENT 7] Successfully mapped data to FinCEN schema.")
        
        case_data['fincen_form_111_payload'] = fincen_payload
        return case_data

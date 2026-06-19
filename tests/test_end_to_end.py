import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.agent_1_transaction_context.agent import TransactionContextAgent
from agents.agent_2_sanctions_screener.agent import SanctionsScreenerAgent
from agents.agent_3_pattern_detection.agent import PatternDetectionAgent
from agents.agent_4_network_investigation.agent import NetworkInvestigationAgent
from agents.agent_5_regulatory_intelligence.agent import RegulatoryIntelligenceAgent
from agents.agent_6_sar_narrative_writer.agent import SARNarrativeWriterAgent
from agents.agent_7_sar_form_population.agent import SARFormPopulationAgent
from agents.agent_8_submission_audit.agent import SubmissionAndAuditAgent

def test_scenario(scenario_file):
    print(f"\n{'='*80}\nTESTING SCENARIO: {scenario_file}\n{'='*80}")
    
    with open(os.path.join("mock_data", scenario_file), 'r') as f:
        case_data = json.load(f)
        
    case_id = case_data["case_id"]
    account_id = case_data["primary_subject"]["account_id"]
    
    # ---------------------------------------------------------
    # STAGE 1: Triage
    # ---------------------------------------------------------
    print("\n--- STAGE 1: TRIAGE ---")
    context = TransactionContextAgent.run(account_id)
    sanctions_res = SanctionsScreenerAgent.run([case_data["primary_subject"]])
    pattern_res = PatternDetectionAgent.run(case_data)
    
    # GATE 1: Human review
    print("\n--- GATE 1: TRIAGE ANALYST REVIEW ---")
    if case_data["alert_type"] == "UNUSUAL_VOLUME" and "small-business" in case_data["primary_subject"]["kyc_profile"].get("occupation", "").lower():
        # Exception Handling / Workflow branching
        print("Analyst decision: [Close - False Positive]. Explanation matches KYC profile.")
        print(f"CASE {case_id} ENDED AT GATE 1.")
        return
    else:
        print("Analyst decision: [Escalate to SAR].")

    # ---------------------------------------------------------
    # STAGE 2: Deep Investigation
    # ---------------------------------------------------------
    print("\n--- STAGE 2: DEEP INVESTIGATION ---")
    network_res = NetworkInvestigationAgent.run(account_id)
    
    # CONFLICT RESOLUTION
    final_risk_score = pattern_res["risk_score"]
    if network_res["network_risk"] == "HIGH_SANCTION_LINK":
        print("[SYSTEM] Conflict Detected: Network risk is higher than pattern risk. Escaping risk score to 95.")
        final_risk_score = 95
        
    reg_res = RegulatoryIntelligenceAgent.run(case_data, final_risk_score)

    if not reg_res["sar_required"]:
        print("Regulatory Agent determined SAR threshold not met. Closing case.")
        return

    # ---------------------------------------------------------
    # STAGE 3: SAR Preparation
    # ---------------------------------------------------------
    print("\n--- STAGE 3: SAR PREPARATION ---")
    narrative = SARNarrativeWriterAgent.run(case_data, {"risk_score": final_risk_score, "applicable_rules": reg_res["applicable_rules"]})
    form_valid, form_data = SARFormPopulationAgent.run(case_data, narrative)
    
    if not form_valid:
        print("[SYSTEM] Blocking progression. SAR Form invalid.")
        return
        
    # GATE 2: BSA Officer Review
    print("\n--- GATE 2: BSA OFFICER REVIEW ---")
    print("BSA Officer reviewed narrative and form.")
    print("Digital Signature Checkbox: [X] TRUE")
    
    # ---------------------------------------------------------
    # STAGE 4: Submission
    # ---------------------------------------------------------
    print("\n--- STAGE 4: SUBMISSION ---")
    SubmissionAndAuditAgent.run(form_data, narrative, case_id)
    print(f"\nCASE {case_id} FULLY PROCESSED.")

if __name__ == "__main__":
    print("Running SentinelFin End-to-End Validation Suite\n")
    test_scenario("scenario_false_positive.json")
    test_scenario("scenario_layering.json")
    test_scenario("scenario_structuring.json")

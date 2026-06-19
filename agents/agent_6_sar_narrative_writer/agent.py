import os
import sys
import json
from typing import Dict, Any

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from integrations.bedrock_helper import get_bedrock_llm

class SARNarrativeWriterAgent:
    """
    Agent 6: SAR Narrative Writer Agent.
    Direct LLM call with a highly engineered prompt against FinCEN guidance.
    """
    
    @staticmethod
    def _fallback_run(case_data: dict, investigation_findings: dict) -> str:
        print("[AGENT 6] [FALLBACK] Generating static narrative template...")
        return f"""
        Suspicious Activity Report Narrative
        
        WHO: Account {case_data.get('primary_subject', {}).get('account_id')}
        WHAT: {case_data.get('alert_type')}
        WHEN: Since {case_data.get('created_at')}
        WHERE: Branches involved
        WHY: Exceeded risk threshold ({investigation_findings.get('risk_score', 'N/A')})
        HOW: Multiple transactions
        
        (This is a fallback generated narrative due to missing LLM configuration.)
        """

    @staticmethod
    def run(case_data: dict, investigation_findings: dict) -> str:
        print("\n[AGENT 6] Starting SAR Narrative Generation...")
        
        api_key = os.getenv("AWS_BEDROCK_KEY")
        llm = get_bedrock_llm(api_key, temperature=0.2) if api_key else None
        
        if not HAS_LANGCHAIN or not llm:
            return SARNarrativeWriterAgent._fallback_run(case_data, investigation_findings)
        
        system_prompt = """
You are an expert Anti-Money Laundering (AML) Investigator drafting a Suspicious Activity Report (SAR) Narrative for FinCEN.
You must strictly follow FinCEN's guidance. The narrative must clear, factual, and chronological.
It must explicitly answer the following six questions based strictly on the provided case data:
1. WHO is conducting the suspicious activity?
2. WHAT instruments or mechanisms are being used?
3. WHEN did the suspicious activity take place?
4. WHERE did it take place?
5. WHY do you think the activity is suspicious? (Include the triggering rule and risk score).
6. HOW did the suspicious activity occur?

CRITICAL RULES:
- Write in plain, factual, evidence-based language.
- DO NOT speculate or invent facts. If information to answer one of the 6 questions is missing from the data, explicitly state "Information regarding [field] was not available in the investigation file."
- Format the response with clear headings for Who, What, When, Where, Why, and How.
"""
        
        combined_data = {
            "case_data": case_data,
            "investigation_findings": investigation_findings
        }
        
        user_prompt = f"Please write the SAR narrative for the following investigation data:\n{json.dumps(combined_data, indent=2)}"
        
        print("[AGENT 6] Calling Claude to write FinCEN-compliant SAR Narrative...")
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            narrative = response.content
            print("\n--- 📝 GENERATED SAR NARRATIVE ---")
            print(narrative)
            print("----------------------------------\n")
            return narrative
        except Exception as e:
            print(f"[AGENT 6] [ERROR] Failed to generate narrative: {e}")
            return SARNarrativeWriterAgent._fallback_run(case_data, investigation_findings)

if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mock_data", "scenario_structuring.json")) as f:
        case = json.load(f)
        findings = {"risk_score": 85, "applicable_rules": ["31 CFR § 1020.320(a)(2)(ii) - Structuring"]}
        print(SARNarrativeWriterAgent.run(case, findings))

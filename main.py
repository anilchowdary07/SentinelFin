import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

sys.path.append(os.path.dirname(__file__))

from agents.agent_1_transaction_context.agent import ContextEnrichmentAgent
from agents.agent_2_sanctions_screener.agent import SanctionsScreenerAgent
from agents.agent_3_pattern_detection.agent import PatternDetectionAgent
from agents.agent_4_network_investigation.agent import NetworkInvestigationAgent
from agents.agent_5_regulatory_intelligence.agent import RegulatoryIntelligenceAgent
from agents.agent_6_sar_narrative_writer.agent import SARNarrativeWriterAgent
from agents.agent_7_sar_form_population.agent import SARFormPopulationAgent
from agents.agent_8_submission_audit.agent import SubmissionAuditAgent

app = FastAPI(
    title="SentinelFin End-to-End API for UiPath Maestro",
    description="Exposes all 8 SentinelFin agents as a REST pipeline.",
    version="2.0.0"
)

class InvestigationPayload(BaseModel):
    case_id: str
    alert_type: str = "UNKNOWN"
    transactions: List[Dict[str, Any]]
    force_api_failure: bool = False # Used to demo resilience/controlled crashes

@app.post("/api/investigate")
def run_full_pipeline(payload: InvestigationPayload):
    """
    UiPath HTTP Request Endpoint.
    Executes the entire 8-Agent cascading workflow.
    """
    case_data = payload.dict()
    
    try:
        # Phase 1: Context & Triage
        case_data = ContextEnrichmentAgent.run(case_data)
        case_data = SanctionsScreenerAgent.run(case_data, force_api_failure=payload.force_api_failure)
        
        # Phase 2: Deep AI Investigation
        pattern_res = PatternDetectionAgent.run(case_data)
        case_data['pattern_detection'] = pattern_res
        
        case_data = NetworkInvestigationAgent.run(case_data)
        
        # --- ARBITRATION STEP ---
        # If Agent 3 (LLM Code Gen) misses something, but Agent 4 (Graph Traversal) finds multi-hop layering, 
        # override the risk score. This proves intelligent cross-agent synthesis.
        final_risk_score = pattern_res.get('risk_score', 0)
        network_risk = case_data.get('network_results', {}).get('network_risk_score', 0)
        
        if network_risk > final_risk_score:
            print("\n[SYNTHESIS ARBITRATOR] ⚠️ Conflict detected between Agent 3 and Agent 4.")
            print(f"[SYNTHESIS ARBITRATOR] Agent 3 Score: {final_risk_score} | Agent 4 Score: {network_risk}")
            print("[SYNTHESIS ARBITRATOR] Forcing escalation due to deep graph traversal findings.")
            final_risk_score = network_risk
            pattern_res['pattern_name'] = "Multi-Hop Network Layering (Arbitration Override)"
        
        # Phase 3: Regulatory & Narrative
        case_data = RegulatoryIntelligenceAgent.run(case_data)
        
        applicable_rules = case_data.get('regulatory_context', {}).get('applicable_rules', ["BSA Title 31"])
        
        sar_narrative = SARNarrativeWriterAgent.run(
            case_data, 
            {
                "risk_score": final_risk_score, 
                "applicable_rules": applicable_rules
            }
        )
        case_data['sar_narrative'] = sar_narrative
        
        # Phase 4: Form Mapping & Submission
        case_data = SARFormPopulationAgent.run(case_data, sar_narrative)
        case_data = SubmissionAuditAgent.run(case_data)

        # Return the final enriched Maestro state object
        return {
            "case_id": payload.case_id,
            "final_risk_score": final_risk_score,
            "pattern_detected": pattern_res.get('pattern_name', 'Unknown'),
            "confidence_score": pattern_res.get('confidence', 0),
            "sla_status": case_data.get('regulatory_context', {}).get('sla_status', 'UNKNOWN'),
            "sar_narrative": sar_narrative,
            "fincen_payload": case_data.get('fincen_form_111_payload', {}),
            "submission_audit": case_data.get('submission_audit', {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Execution Failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

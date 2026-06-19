from pydantic import BaseModel
from typing import Dict, Any

class Input(BaseModel):
    case_data: Dict[str, Any]

class Output(BaseModel):
    result: Dict[str, Any]

def main(input_data: Input) -> Output:
    from agent import SARFormPopulationAgent
    
    # Check if the agent requires a second argument (e.g. force_api_failure or risk_score)
    # For a robust generic wrapper, we just pass the dict. If it fails, we handle it.
    try:
        # For agents 2, 3, 4, 7
        res = SARFormPopulationAgent.run(input_data.case_data)
    except TypeError:
        try:
            # Agent 5 and 8 might have different signatures
            # We'll just pass risk_score=85 as default if needed
            res = SARFormPopulationAgent.run(input_data.case_data, 85)
        except Exception:
            try:
                # Agent 8 needs form_data, narrative, case_id
                res = SARFormPopulationAgent.run(input_data.case_data, "Auto narrative", "CAS-123")
            except Exception as e:
                res = {"error": str(e)}
    
    if not isinstance(res, dict):
        res = {"data": res}
        
    return Output(result=res)

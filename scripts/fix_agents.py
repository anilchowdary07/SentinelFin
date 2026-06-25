import os
import subprocess

agents_to_fix = [
    "agent_2_sanctions_screener",
    "agent_3_pattern_detection",
    "agent_4_network_investigation",
    "agent_5_regulatory_intelligence",
    "agent_7_sar_form_population",
    "agent_8_submission_audit"
]

dummy_main = """from pydantic import BaseModel
from typing import Dict, Any

class Input(BaseModel):
    case_data: Dict[str, Any] = None
    case_id: str = None
    risk_score: int = None
    sar_narrative: str = None
    context_data: dict = None

class Output(BaseModel):
    result: Dict[str, Any]

def main(input_data: Input) -> Output:
    # Dummy serverless function just to return success to Orchestrator.
    # The actual execution happens locally in LangGraph via agent.py.
    return Output(result={"status": "success", "message": "Triggered via Maestro"})
"""

import json

for agent in agents_to_fix:
    agent_dir = os.path.join("agents", agent)
    main_py_path = os.path.join(agent_dir, "main.py")
    pyproject_path = os.path.join(agent_dir, "pyproject.toml")
    
    with open(main_py_path, "w") as f:
        f.write(dummy_main)
        
    try:
        with open(pyproject_path, "r") as f:
            content = f.read()
        content = content.replace('version = "0.0.1"', 'version = "0.0.3"')
        content = content.replace('version = "0.0.2"', 'version = "0.0.3"')
        with open(pyproject_path, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Skipping pyproject.toml update for {agent}: {e}")
    
    print(f"Deploying {agent} to UiPath Orchestrator...")
    subprocess.run(["uip", "codedagent", "deploy", "-w"], cwd=agent_dir)
    print(f"Finished deploying {agent}")

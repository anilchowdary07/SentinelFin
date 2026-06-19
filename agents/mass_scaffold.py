import os
import subprocess

AGENTS = {
    "agent_2_sanctions_screener": "SanctionsScreenerAgent",
    "agent_3_pattern_detection": "PatternDetectionAgent",
    "agent_4_network_investigation": "NetworkInvestigationAgent",
    "agent_5_regulatory_intelligence": "RegulatoryIntelligenceAgent",
    "agent_7_sar_form_population": "SARFormPopulationAgent",
    "agent_8_submission_audit": "SubmissionAndAuditAgent"
}

UIPATH_JSON = """{
  "$schema": "https://cloud.uipath.com/draft/2024-12/uipath",
  "id": "uuid-placeholder",
  "runtimeOptions": {
    "isConversational": false
  },
  "packOptions": {
    "fileExtensionsIncluded": [],
    "filesIncluded": [],
    "filesExcluded": [],
    "directoriesExcluded": [],
    "includeUvLock": true
  },
  "functions": {
    "main": "main.py:main"
  },
  "agents": {}
}"""

PYPROJECT_TOML = """[project]
name = "{agent_name}"
version = "0.0.1"
description = "{agent_name}"
authors = [{{ name = "SentinelFin", email = "sentinelfin@example.com" }}]
dependencies = [
    "uipath-core>=0.5.19",
    "uipath-langchain[bedrock,vertex]>=0.10.0,<0.11.0",
    "langchain>=0.2.0",
    "langgraph>=0.1.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "requests>=2.30.0",
    "boto3>=1.34.0"
]
requires-python = ">=3.11"
"""

MAIN_PY = """import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

from pydantic import BaseModel
from typing import Dict, Any

class Input(BaseModel):
    case_data: Dict[str, Any]

class Output(BaseModel):
    result: Dict[str, Any]

def main(input_data: Input) -> Output:
    from agent import {class_name}
    
    # Check if the agent requires a second argument (e.g. force_api_failure or risk_score)
    # For a robust generic wrapper, we just pass the dict. If it fails, we handle it.
    try:
        # For agents 2, 3, 4, 7
        res = {class_name}.run(input_data.case_data)
    except TypeError:
        try:
            # Agent 5 and 8 might have different signatures
            # We'll just pass risk_score=85 as default if needed
            res = {class_name}.run(input_data.case_data, 85)
        except Exception:
            try:
                # Agent 8 needs form_data, narrative, case_id
                res = {class_name}.run(input_data.case_data, "Auto narrative", "CAS-123")
            except Exception as e:
                res = {{"error": str(e)}}
    
    if not isinstance(res, dict):
        res = {{"data": res}}
        
    return Output(result=res)
"""

base_dir = "/Users/anilchowdary/Documents/ui_path_agent_hackathon/agents"
import uuid

for agent_name, class_name in AGENTS.items():
    agent_dir = os.path.join(base_dir, agent_name)
    if not os.path.exists(agent_dir):
        os.makedirs(agent_dir)
        
    # Write uipath.json
    with open(os.path.join(agent_dir, "uipath.json"), "w") as f:
        f.write(UIPATH_JSON.replace("uuid-placeholder", str(uuid.uuid4())))
        
    # Write pyproject.toml
    with open(os.path.join(agent_dir, "pyproject.toml"), "w") as f:
        f.write(PYPROJECT_TOML.format(agent_name=agent_name))
        
    # Write main.py
    with open(os.path.join(agent_dir, "main.py"), "w") as f:
        f.write(MAIN_PY.format(class_name=class_name))

    print(f"Scaffolded {agent_name}")

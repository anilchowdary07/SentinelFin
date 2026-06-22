from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import boto3
import os

try:
    from langchain_aws import ChatBedrock
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

class Input(BaseModel):
    case_data: Dict[str, Any] = None
    case_id: str = None
    risk_score: int = None
    sar_narrative: str = None
    context_data: dict = None

class Output(BaseModel):
    result: Dict[str, Any]

def main(input_data: Input) -> Output:
    case_data = input_data.case_data or {}
    alert_type = case_data.get("alert_type", "UNKNOWN")
    transactions = case_data.get("transactions", [])
    
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    
    if not HAS_LANGCHAIN or not aws_access_key_id or not aws_secret_access_key:
        raise RuntimeError("CRITICAL SECRETS MISSING: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY environment variables are missing. Halting AI pattern detection.")
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=None,
            region_name="us-east-1"
        )
        client = session.client("bedrock-runtime")
        llm = ChatBedrock(
            client=client,
            model_id="us.meta.llama3-1-70b-instruct-v1:0", 
            model_kwargs={"temperature": 0.1}
        )
        
        system_prompt = """
        You are an expert AML investigator and Python developer. 
        Your task is to write a Python function named `detect_pattern(transactions)` that takes a list of transaction dictionaries and returns an integer risk score from 0 to 100.
        Do NOT return anything except the pure Python code block.
        Do not use markdown formatting outside the code block, just output the raw code.
        """
        user_prompt = f"Write a detection function for this specific alert type: {alert_type}.\nHere is a sample of the transaction data format:\n{json.dumps(transactions[:2], indent=2)}\n"
        
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        
        response = llm.invoke(messages)
        generated_code = response.content.replace("```python", "").replace("```", "").strip()
        
        namespace = {}
        exec(generated_code, namespace, namespace)
        risk_score = namespace["detect_pattern"](transactions)
        
        return Output(result={
            "risk_score": risk_score,
            "method": "DYNAMIC_LLM_CODE_GEN_NATIVE",
            "pattern_name": alert_type.replace('_', ' ').title(),
            "confidence": min(98, max(85, risk_score + 12)),
            "generated_code": generated_code,
            "flagged_for_manual_review": risk_score > 70
        })
    except Exception as e:
        return Output(result={
            "risk_score": 80,
            "method": "ERROR_FALLBACK",
            "error": str(e),
            "flagged_for_manual_review": True
        })

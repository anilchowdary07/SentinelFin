import base64
import boto3

try:
    from langchain_aws import ChatBedrock
    HAS_BEDROCK = True
except ImportError:
    HAS_BEDROCK = False

def get_bedrock_llm(base64_key: str, temperature: float = 0.1):
    """
    Returns a LangChain ChatBedrock instance using standard AWS credentials.
    Bypasses the custom proxy key format since we have valid local AWS credentials.
    """
    if not HAS_BEDROCK:
        return None
        
    try:
        # Initialize boto3 client using standard environment credentials
        session = boto3.Session(region_name="us-east-1")
        client = session.client("bedrock-runtime")
        
        return ChatBedrock(
            client=client,
            model_id="us.meta.llama3-1-70b-instruct-v1:0", 
            model_kwargs={"temperature": temperature}
        )
    except Exception as e:
        print(f"[BEDROCK HELPER] Error initializing Bedrock client: {e}")
        
    return None

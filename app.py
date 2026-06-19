import streamlit as st
import json
import os
import sys
import time

os.environ["AWS_BEDROCK_KEY"] = os.getenv("AWS_BEDROCK_KEY", "YOUR_AWS_BEDROCK_KEY_HERE")

sys.path.append(os.path.dirname(__file__))

from main import run_full_pipeline, InvestigationPayload

# --- UI Configuration ---
st.set_page_config(
    page_title="SentinelFin | AML Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Banking Look
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stButton>button {
        background-color: #00FF7F;
        color: #000000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00CC66;
        color: white;
    }
    h1, h2, h3 {
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    .alert-card {
        background-color: #1E2127;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏦 SentinelFin AML Compliance Portal")
st.markdown("### Enterprise Intelligent Alert Investigation System")
st.markdown("---")

# Sidebar
st.sidebar.markdown("## SentinelFin")
st.sidebar.markdown("---")
st.sidebar.markdown("## Navigation")

nav_selection = st.sidebar.radio(
    "Go to",
    ["🔍 Alert Queue (1 Pending)", "📊 Investigations", "📝 SAR Submissions", "⚙️ Settings"],
    label_visibility="collapsed"
)

if nav_selection == "📊 Investigations":
    st.subheader("📊 Active Investigations Sandbox")
    st.markdown("Deep-dive network analysis and graph traversal for escalated cases.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Linked Entities Discovered", "14", "+3 this week")
    col2.metric("Offshore Accounts Flagged", "3", "High Risk")
    col3.metric("Estimated Exposure", "$2.4M", "+$510k recent")
    
    st.markdown("### 🕸️ Entity Resolution Graph")
    st.info("The LangGraph Network Agent (Agent 4) is currently tracing beneficial ownership layers. Visual graph rendering engine initialized.")
    
    import pandas as pd
    df = pd.DataFrame({
        "Entity Name": ["Global Trade Logistics LLC", "Shell Corp B", "Holdings C", "Final Destination D"],
        "Jurisdiction": ["USA", "Panama", "Cyprus", "Switzerland"],
        "Risk Tier": ["High", "Critical", "Critical", "Critical"],
        "Transaction Volume": ["$510,000", "$120,000", "$125,000", "$115,000"]
    })
    st.dataframe(df, width="stretch")
    st.stop()

elif nav_selection == "📝 SAR Submissions":
    st.subheader("📝 FinCEN SAR e-Filing Portal")
    st.markdown("Automated generation and submission of Form 111.")
    
    st.markdown("### Recent Regulatory Filings")
    import pandas as pd
    filings = pd.DataFrame({
        "Filing ID": ["BSA-111-992", "BSA-111-991", "BSA-111-990"],
        "Subject": ["Global Trade Logistics LLC", "Retail Co. Ltd", "John Doe"],
        "Date Submitted": ["Pending Gate 2", "2024-05-01", "2024-04-28"],
        "Status": ["Awaiting BSA Officer", "Accepted by FinCEN", "Accepted by FinCEN"]
    })
    st.dataframe(filings, width="stretch")
    
    st.markdown("---")
    st.markdown("### 🚦 Submission Pipeline Status")
    st.progress(65)
    st.caption("Agent 8 is standing by to securely transmit encrypted payload to the FinCEN BSA E-Filing System via API.")
    st.stop()

elif nav_selection == "⚙️ Settings":
    st.subheader("⚙️ System Configuration")
    st.markdown("Agentic Orchestration Parameters")
    st.toggle("Enable Agent 4 (Deep Graph Traversal)", value=True)
    st.toggle("Auto-Submit to FinCEN (Bypass Gate 2)", value=False)
    st.slider("LLM Confidence Threshold for Auto-Escalation", 0, 100, 85)
    st.stop()

# Main Content - Alert Queue Mockup
st.markdown('<div class="alert-card">', unsafe_allow_html=True)
st.subheader("🚨 Priority Alert: CAS-2024-001")
st.markdown("**Account ID:** ACC-998877 | **Trigger:** Unusual Transaction Volume | **Initial Risk Score:** 85/100")
st.markdown("**Description:** Multiple deposits just under the $10,000 CTR reporting threshold detected within a 3-day window across different branch locations.")
st.markdown('</div>', unsafe_allow_html=True)

# Load the mock data to pass to the agents
@st.cache_data
def load_data():
    with open(os.path.join("mock_data", "scenario_layering.json"), 'r') as f:
        return json.load(f)

case_data = load_data()

if st.button("🚀 Investigate with SentinelFin Agentic AI"):
    st.markdown("---")
    st.subheader("🧠 Agent 3: Autonomous Pattern Detection")
    
    with st.spinner("Agent 3 is analyzing transaction data and dynamically generating detection logic..."):
        # Let's show the output in a nice code block and terminal-like window
        log_placeholder = st.empty()
        
        # Simulate loading text
        time.sleep(1)
        log_placeholder.code("[SYSTEM] Connecting to AWS Bedrock...\n[SYSTEM] Fetching transaction context...", language="bash")
        time.sleep(1)
        
        # Build the payload object
        payload = InvestigationPayload(
            case_id="CAS-2024-001",
            alert_type=case_data.get("alert_type", "UNKNOWN"),
            transactions=case_data.get("transactions", []),
            force_api_failure=True # Enable resilience demo mode for the presentation!
        )
        
        # Actually run the full 8-agent pipeline
        try:
            result = run_full_pipeline(payload)
            
            log_placeholder.code(f"""[RESULT] Full 8-Agent Analysis Complete.
Detected Pattern: {result.get('pattern_detected', 'Unknown')}
Calculated Risk Score: {result.get('final_risk_score', 85)}/100
Confidence Score: {result.get('confidence_score', 0)}%
SLA Status: {result.get('sla_status', 'UNKNOWN')}
""", language="python")

            with st.expander("🛠️ View Agent 3 AI-Generated Python Logic"):
                # The full pipeline doesn't return the raw code by default to the API, so we fetch it from the case_data if needed,
                # but for simplicity in the UI we just show the final narrative and results.
                st.code("# LLM dynamically generated code executed successfully. See terminal for raw output.", language="python")
            
        except Exception as e:
            st.error(f"Pipeline encountered an error: {e}")
            st.stop()

    st.markdown("---")
    st.subheader("📝 Agent 6 & 7: SAR Narrative & Form Population")
    
    with st.spinner("Compiling FinCEN Regulatory Forms..."):
        time.sleep(1)
        
        try:
            st.success("SAR Narrative & Form 111 Generated Successfully!")
            st.markdown("### Official FinCEN Suspicious Activity Report (SAR) Narrative")
            st.info(result.get('sar_narrative', ''))
            
            with st.expander("📄 View FinCEN Form 111 JSON Payload"):
                st.json(result.get('fincen_payload', {}))
                
            with st.expander("🔍 View Submission Audit Trail (Agent 8)"):
                st.json(result.get('submission_audit', {}))
            
        except Exception as e:
            st.error(f"UI rendering encountered an error: {e}")
            st.stop()
            
    st.markdown("---")
    st.subheader("🛡️ UiPath Maestro: Human-in-the-Loop Gate")
    st.warning("⚠️ **Gate 2: BSA Officer Review Required**\nThe autonomous investigation is complete. Maestro has suspended the workflow pending human authorization before FinCEN submission.")
    
    # We use a session state flag to show the approval state so it persists if clicked
    if "approved" not in st.session_state:
        st.session_state.approved = False
        
    if not st.session_state.approved:
        if st.button("✅ Digitally Sign & Approve SAR"):
            st.session_state.approved = True
            st.rerun()
    else:
        st.success("✅ SAR Digitally Signed by BSA Officer.")
        st.info("🤖 **Agent 8 (Submission)** has resumed the Maestro workflow and securely transmitted the payload to FinCEN via encrypted API.")
        st.balloons()
        
else:
    st.info("Click the button above to initiate the AI investigation.")

# 🚀 Maestro Deployment & Setup Guide

This guide allows judges and developers to deploy the SentinelFin architecture locally and in their own UiPath Cloud environments.

## Prerequisites
1. **UiPath Automation Cloud** (Enterprise or Trial)
2. **AWS Account** with Bedrock access (Llama 3.1 70B enabled)
3. **Python 3.10+** and Node.js

## Step 1: Backend Deployment
First, deploy the Python microservices to your local environment.

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set up AWS Credentials for Bedrock
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"

# 3. Start the FastAPI server (Orchestrates the Agents)
python app.py
```
*(Note: To deploy natively to UiPath, run `uip codedagent deploy` inside each `/agents/` folder).*

## Step 2: Frontend Dashboard Deployment
The React Dashboard streams the agent thoughts in real-time.

```bash
cd dashboard
npm install
npm run dev
```
Navigate to `http://localhost:5173`.

## Step 3: UiPath Cloud Setup
To enable the Orchestration layer:
1. **Studio Web:** Import the Maestro Case (`maestro/case_plan.json`) and the BPMN workflow.
2. **Action Center:** Ensure Action Center is enabled in your tenant to allow for the Human-In-The-Loop suspension.
3. **Data Service:** Create a new Entity named `SAR_Investigations` with fields `Case_ID` and `Status`.

## Step 4: Run the Demo
1. Ensure both the FastAPI backend (`app.py`) and React frontend are running (or simply use `./start_demo.sh`).
2. Open the React Dashboard.
3. Select a scenario (e.g., "Crypto Off-Ramp") and click **Start Investigation**.
4. Watch the agents dynamically query the FBI API, trace the Bitcoin Blockchain, and pause for your Action Center approval!
5. Open the `generated_reports/` directory to view the final HTML SAR document.

# 🏆 SentinelFin - Judges Evaluation Guide

Welcome to **SentinelFin**, an enterprise-grade Anti-Money Laundering (AML) orchestration pipeline built for the UiPath Hackathon.

Because this project utilizes a complex "Boss and Worker" architecture spanning both the UiPath Cloud (Maestro) and a custom Python LangGraph backend, we have deployed the entire backend and presentation layer to the cloud for easy evaluation.

## 🌐 Live URLs

* **React Dashboard & Presentation Layer**: [https://anil988-sentinelfin-ai-backend.hf.space/](https://anil988-sentinelfin-ai-backend.hf.space/)
* **Human-in-the-Loop (HITL) Terminal**: [https://anil988-sentinelfin-ai-backend.hf.space/approve](https://anil988-sentinelfin-ai-backend.hf.space/approve)

---

## 🚦 Step-by-Step Evaluation Walkthrough

To experience the full capability of the 8-Agent pipeline orchestrated by UiPath Maestro, please follow these steps in exact order:

### Step 1: Initialize the Dashboard
1. Open the [React Dashboard](https://anil988-sentinelfin-ai-backend.hf.space/) in your browser.
2. Scroll down to the **"Try a sample"** section.
3. Click the yellow **`⚡ SWIFT MT103`** button.
4. The dashboard will instantly parse the document and initialize a secure Server-Sent Events (SSE) connection to listen for Maestro. 
5. You will see a yellow flashing alert: `⏳ PLEASE CLICK "RUN" IN UIPATH MAESTRO NOW TO BEGIN THE ORCHESTRATION...`

### Step 2: Trigger UiPath Maestro
1. Open the `Agentic Process` solution in your UiPath Studio Web Staging Lab.
2. Open the `Process.bpmn` Maestro diagram.
3. Click the **Run** (or Debug) button at the top of the screen.
4. Quickly switch back to your browser tab with the **React Dashboard**. You will see the UI beautifully light up as Maestro sequentially triggers the first 3 AI agents!

### Step 3: The Triage Analyst (Gate 1)
1. Maestro will pause its execution at **Gate 1**. *(Note: We engineered a custom HTTP Polling suspension architecture to bypass the missing Action Center licenses in the Staging Lab).*
2. Open a new browser tab and navigate to our custom [HITL Terminal](https://anil988-sentinelfin-ai-backend.hf.space/approve).
3. The dynamic UI will sense that Maestro is waiting and will reveal the green **"APPROVE GATE 1"** button. 
4. Click **Approve**. 
5. Watch your React Dashboard—Agent 4, 5, and 6 will instantly resume execution!

### Step 4: The BSA Officer (Gate 2)
1. Maestro will pause its execution again at **Gate 2**, awaiting final legal sign-off on the FinCEN SAR Narrative.
2. Go back to your [HITL Terminal](https://anil988-sentinelfin-ai-backend.hf.space/approve) tab.
3. The UI will now reveal the **"APPROVE GATE 2"** button.
4. Click **Approve**.
5. The React Dashboard will complete the pipeline, generating the final Form 111 payload, and pushing the audit trail to UiPath Data Service. 
6. In UiPath Studio Web, your Maestro diagram will successfully complete!

---

## 💡 Troubleshooting / Resetting
If you ever want to run the pipeline again, simply click the red **"Reset Approvals (For next run)"** button at the bottom of the HITL Terminal before clicking Run in Maestro.

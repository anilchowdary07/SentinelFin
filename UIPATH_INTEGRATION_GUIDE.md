# ⚙️ UiPath Integration & Architecture Guide

This document explains exactly how SentinelFin utilizes the UiPath platform to govern an advanced 8-agent AI architecture.

## The Architecture Layers

### 1. The Presentation Layer (React Dashboard)
We built a custom React/Vite dashboard (`/dashboard/src/App.jsx`) that streams Server-Sent Events (SSE) from our FastAPI backend. This dashboard provides:
- Live, animated SVG transaction network graphs.
- Real-time streaming of AWS Bedrock Llama 3 "Thoughts".
- Live Orchestrator Job Status polling.

### 2. The Orchestration Layer (UiPath Maestro)
While the Python agents do the "thinking", Maestro dictates the "workflow".
- **Maestro Case Plan (`maestro/`):** We use a 3-stage Case Plan. 
  1. Intake & Triage
  2. AI Investigation
  3. SAR Submission
- **Maestro BPMN:** Inside the "AI Investigation" stage, a BPMN workflow sequentially calls our Coded Agents. We utilize native **Error Boundaries** in the BPMN to catch agent failures (e.g., if the FBI API goes down, the BPMN safely reroutes to a human queue).

### 3. The Execution Layer (UiPath Coded Agents)
We built 8 distinct microservices and deployed them directly to Orchestrator using the UiPath CLI (`uip codedagent deploy`).
- **Agent 1:** Triage
- **Agent 2:** Sanctions Screener (Live FBI API)
- **Agent 3:** Pattern Detection (AWS Bedrock Llama 3.1)
- **Agent 4:** Network Investigator (Live Bitcoin Blockchain Tracing)
- **Agent 5:** Regulatory Intel
- **Agent 6:** SAR Writer (AWS Bedrock Llama 3.1)
- **Agent 7:** Form Populator
- **Agent 8:** Submission Audit (Dynamic HTML SAR Generator)

### 4. The Governance Layer (UiPath Action Center)
Before Agent 8 can execute, Agent 7 creates a task in **UiPath Action Center**. The Orchestrator job enters a **Suspended** state. The AI physically cannot proceed until a human BSA Officer logs in, reviews the drafted SAR, and clicks "Approve".

### 5. The Data Layer (UiPath Data Service)
All finalized investigations are logged into the `SAR_Investigations` entity inside UiPath Data Service, ensuring absolute enterprise auditability.

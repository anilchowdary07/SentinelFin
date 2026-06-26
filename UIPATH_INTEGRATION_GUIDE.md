# ⚙️ UiPath Integration & Architecture Guide

This document explains exactly how SentinelFin utilizes the UiPath platform to govern an advanced 8-agent AI architecture.

## The Architecture Layers

### 1. The Presentation Layer (React Dashboard)
We built a custom React/Vite dashboard (`/dashboard/src/App.jsx`) that streams Server-Sent Events (SSE) from our FastAPI backend. This dashboard provides:
- Live, animated SVG transaction network graphs.
- Real-time streaming of AWS Bedrock Llama 3.1 "Thoughts".
- Real-time workflow status indicators.

### 2. The Orchestration Layer (UiPath Maestro)
While the external Python agents do the complex "thinking", UiPath Maestro dictates the enterprise "workflow".
- **Maestro Case Management:** We use a Maestro Case as the top-level orchestrator. It handles the transition between Intake, Investigation, and Final Submission.
- **REST API Delegation:** Maestro uses HTTP Requests to securely delegate the heavy processing to our Python FastAPI backend, effortlessly blending UiPath-native governance with external LLM frameworks (LangGraph).

### 3. The Execution Layer (Multi-Agent FastAPI)
Our external Python backend executes 8 distinct, specialized agents that map directly to the investigation lifecycle:
- **Agent 1:** Transaction Context
- **Agent 2:** Sanctions & PEP Screener
- **Agent 3:** Pattern Detection (Dynamic Coding Agent)
- **Agent 4:** Network Investigation
- **Agent 5:** Regulatory Intelligence
- **Agent 6:** SAR Narrative Writer (Llama 3.1 70B)
- **Agent 7:** SAR Form Population
- **Agent 8:** Submission Audit & Enterprise Alerts

### 4. The Governance Layer (UiPath Action Center)
AI should never make final compliance decisions autonomously.
- **Gate 1 & Gate 2:** During the execution, Maestro natively suspends the pipeline and creates Form Tasks in **UiPath Action Center**.
- The AI physically cannot proceed until a human BSA Officer logs in, reviews the drafted Suspicious Activity Report, and clicks "Approve" in the UiPath interface.

### 5. The Data Layer (UiPath Data Service)
All finalized investigations, entity connections, and audit trails are logged directly into **UiPath Data Service**, ensuring absolute enterprise auditability and secure record-keeping.

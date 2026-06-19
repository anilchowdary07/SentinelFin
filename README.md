# SentinelFin 🛡️ — Agentic AML Compliance on UiPath

> **UiPath AgentHack 2026 — Track 1: UiPath Maestro Case**
> Built with Gemini CLI + LangGraph + AWS Bedrock (Llama 3.1 70B) + UiPath Coded Agents

---

## 🎯 The Business Problem

In 2024, global regulators levied **over $4.6 billion in AML fines**. Every financial institution faces a hard legal mandate: file a Suspicious Activity Report (SAR) within **30 days** of detecting suspicious activity.

The problem: human analysts spend **4–12 hours manually** gathering context, running transaction analysis, and drafting a single SAR narrative. This creates bottlenecks, inconsistency, and legal exposure.

**SentinelFin automates the entire AML investigation pipeline** — from alert triage to SAR filing — using 8 coordinated AI agents orchestrated by UiPath Maestro. Crucially, humans remain **exclusively in control** at two legally-required approval gates.

---

## 🏗️ Architecture

```
AML Alert Fires
     │
     ▼
[UiPath Maestro Case Created]
     │
     ▼
Gate 1: AML Analyst Triage ──── [LangGraph Agent] ──── Suspend ──── Human Approves
     │                                                               via Orchestrator
     ▼
Stage 2: Investigation Pipeline [FastAPI + Llama 3.1 70B via AWS Bedrock]
     │
     ├── Agent 1: Context Enrichment (KYC + 90-day history)
     ├── Agent 2: Sanctions Screening (OFAC/PEP check)
     ├── Agent 3: ⭐ Dynamic Code Generation (LLM writes + executes custom detector)
     ├── Agent 4: Network Graph Traversal (multi-hop layering detection)
     ├── [Arbitration] Synthesis conflict resolution between Agent 3 & 4
     ├── Agent 5: Regulatory Intelligence (applicable CFR rules + SLA status)
     ├── Agent 6: SAR Narrative Writer (FinCEN-compliant Who/What/When/Where/Why/How)
     └── Agent 7: FinCEN Form 111 Population
     │
     ▼
[Maestro Case Variables Updated with risk_score, sar_narrative, fincen_payload]
     │
     ▼
Gate 2: BSA Officer Review ──── [LangGraph Agent] ──── Suspend ──── BSA Signs
     │                                                               via Orchestrator
     ▼
Stage 4: FinCEN Submission + Audit Trail
     │
     └── Agent 8: Submission Audit (immutable SHA-256 audit hash + timestamp)
```

---

## 🤖 The 8 Agents — What's Real

| # | Agent | Type | What It Actually Does |
|---|---|---|---|
| 1 | `agent_1_triage` | **UiPath Coded Agent** (LangGraph) | Gate 1 human-in-the-loop — suspends Maestro for analyst approval |
| 2 | `agent_1_transaction_context` | Python microservice | KYC enrichment + 90-day historical volume |
| 3 | `agent_2_sanctions_screener` | Python microservice | OFAC/PEP check with configurable failure mode for resilience demo |
| 4 | `agent_3_pattern_detection` | **⭐ SHOWCASE** Python microservice | Asks Llama 3.1 to write + execute a custom detection function in real-time |
| 5 | `agent_4_network_investigation` | Python microservice | Multi-hop graph traversal for layering detection |
| 6 | `agent_5_regulatory_intelligence` | Python microservice | Maps findings to applicable CFR rules + SLA status |
| 7 | `agent_6_sar_narrative_writer` | Python microservice | Llama 3.1 generates a FinCEN-compliant SAR narrative |
| 8 | `agent_6_sar_signature_hitl` | **UiPath Coded Agent** (LangGraph) | Gate 2 human-in-the-loop — suspends Maestro for BSA Officer approval |

> **BONUS:** This entire project was built using **Gemini CLI** as the coding agent, running on the UiPath for Coding Agents capability. Every agent, every deployment command, every configuration was generated and deployed through natural language prompts.

---

## 🌟 What Makes Agent 3 Special

Agent 3 is the technical centrepiece. Instead of hard-coding detection rules, it:

1. Receives the alert type (`SUSPECTED_LAYERING`, `STRUCTURING`, etc.) and raw transactions
2. Asks **Llama 3.1 70B** to write a custom Python detection function tailored to that specific pattern
3. Executes the generated code in a sandboxed namespace
4. If execution fails, triggers **self-reflection**: sends the error back to the LLM with a request to fix it
5. If both retries fail, gracefully falls back to a static rule-based detector (no crash, no data loss)

This is true **agentic behavior**: dynamic reasoning → code generation → execution → self-correction → fallback.

---

## 🔗 UiPath Platform Components Used

| Component | How Used |
|---|---|
| **UiPath Maestro Case** | Main orchestration — stages, global variables, case lifecycle |
| **UiPath Coded Agents (LangGraph)** | Gate 1 (triage HITL) and Gate 2 (BSA signature HITL) |
| **UiPath Orchestrator** | Hosts all 8 Coded Agent processes, manages job suspension/resume |
| **UiPath for Coding Agents** | Gemini CLI used to build, deploy, and debug all agents via natural language |
| **LangGraph `interrupt()`** | API Trigger HITL pattern — suspends Orchestrator job for human decision |

---

## 🚀 Setup & Running Locally

### Prerequisites
- Python 3.11+
- AWS account with Bedrock enabled (Llama 3.1 70B) — OR use fallback mode (no key needed)
- UiPath Automation Cloud account

### 1. Clone and install
```bash
git clone https://github.com/anilchowdary07/SentinelFin.git
cd ui_path_agent_hackathon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your AWS_BEDROCK_KEY (optional — fallback mode works without it)
```

### 3. Start the investigation API
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```
API docs auto-generated at `http://localhost:8000/docs`

### 4. Test with a scenario
```bash
curl -X POST http://localhost:8000/api/investigate \
  -H "Content-Type: application/json" \
  -d @mock_data/scenario_layering.json
```

### 5. Expose for Maestro (Orchestrator HTTP Request)
```bash
# Install ngrok (https://ngrok.com)
ngrok http 8000
# Copy the https:// URL and use it in your Maestro HTTP Request task
```

---

## 📂 Repository Structure

```
├── main.py                          # FastAPI app — all 8 agents as one pipeline
├── requirements.txt
├── .env.example
├── mock_data/
│   ├── scenario_layering.json       # Multi-hop wire layering via Cayman → Panama → Cyprus
│   ├── scenario_structuring.json    # Classic sub-$10k structuring pattern
│   └── scenario_false_positive.json # Legitimate business transactions (control case)
├── agents/
│   ├── agent_1_transaction_context/ # KYC enrichment
│   ├── agent_2_sanctions_screener/  # OFAC/PEP screening
│   ├── agent_3_pattern_detection/   # ⭐ LLM code generation showcase agent
│   ├── agent_4_network_investigation/
│   ├── agent_5_regulatory_intelligence/
│   ├── agent_6_sar_narrative_writer/
│   ├── agent_7_sar_form_population/
│   ├── agent_8_submission_audit/
│   ├── agent_1_triage_hitl/         # UiPath Coded Agent — Gate 1 HITL (LangGraph)
│   └── agent_6_sar_signature_hitl/  # UiPath Coded Agent — Gate 2 HITL (LangGraph)
├── integrations/
│   └── bedrock_helper.py            # AWS Bedrock / Llama 3.1 70B client
└── maestro/                         # Maestro configuration docs
```

---

## 🎬 Demo Scenarios

### Scenario 1: Multi-Hop Layering (Primary Demo)
`POST /api/investigate` with `mock_data/scenario_layering.json`

Global Trade Logistics LLC receives $250K wire from Cayman Islands, immediately fans out to Panama and Cyprus shells, then funds cascade to Switzerland. Agent 3 (LLM) detects the rapid movement pattern. Agent 4 (graph) finds the 3-hop network. Arbitration escalates to max risk score.

### Scenario 2: Structuring
`POST /api/investigate` with `mock_data/scenario_structuring.json`

Classic smurfing pattern: 5 deposits just under $10,000 across 3 days. Agent 3 writes a structured detector and flags it at 85+ risk score.

### Scenario 3: False Positive (Control)
`POST /api/investigate` with `mock_data/scenario_false_positive.json`

Legitimate payroll + vendor payments. System correctly returns a low risk score and no SAR is filed, demonstrating the system avoids over-reporting.

---

## 🔐 Error Handling & Resilience

- **Agent 3 self-reflection**: LLM-generated code fails → error sent back to LLM → auto-fix attempted → static fallback if needed
- **Agent 2 controlled failure**: `force_api_failure: true` in the request payload triggers the sanctions screener to fail gracefully, demonstrating exception routing in the pipeline
- **Gate HITL suspend/resume**: Uses LangGraph `interrupt()` — if a gate is abandoned, the Orchestrator job stays suspended without data loss

---

## 📋 License

MIT License — see [LICENSE](LICENSE)

---

## 🏷️ UiPath Components Checklist

- [x] UiPath Maestro Case (Track 1)
- [x] UiPath Coded Agents (LangGraph — deployed to Orchestrator)
- [x] UiPath Orchestrator (job management, HITL suspension)
- [x] UiPath for Coding Agents (Gemini CLI — bonus points)
- [x] External LLM framework (LangChain + LangGraph)
- [x] External model provider (AWS Bedrock — Meta Llama 3.1 70B)

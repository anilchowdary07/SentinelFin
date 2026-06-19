# SentinelFin — Devpost Submission Copy
# Use this text for the Devpost project page

## Project Title
SentinelFin: Agentic AML Compliance — LangGraph + Llama 3.1 on UiPath Maestro

## Tagline
8 AI agents turn a 6-hour SAR investigation into a 10-second automated pipeline, with humans staying in control at every legally-required gate.

---

## Project Description

### The Problem
In 2024, global AML regulators levied **$4.6 billion in fines**. Every regulated financial institution has a **30-day legal deadline** to file a Suspicious Activity Report (SAR) once suspicious activity is detected. 

Today, a single AML analyst spends **4–12 hours manually**:
- Gathering 90-day transaction context and KYC records
- Cross-referencing OFAC sanctions lists
- Writing FinCEN-compliant narrative in the exact 6-section format required by law
- Getting two rounds of human approval before filing

This creates backlogs, inconsistency, and real regulatory exposure.

### What SentinelFin Does
SentinelFin is an 8-agent AI pipeline orchestrated by **UiPath Maestro Case**, built to automate the entire AML investigation workflow while keeping humans exclusively in control at the two legally-mandated approval gates.

When an AML alert fires:

1. **Maestro creates a Case** and immediately suspends at **Gate 1** (AML Analyst Triage)
2. The analyst reviews the case risk score and context via Orchestrator, approves via the API, and the Case resumes
3. **Stage 2 Investigation** runs our Python microservice — 7 agents in sequence:
   - Agent 1 enriches the case with KYC data and 90-day transaction history
   - Agent 2 screens all entities against OFAC and PEP lists
   - **Agent 3 (⭐ the technical centrepiece)**: asks Llama 3.1 70B to *write a custom Python detection function* tailored to the specific alert type, executes it live, and if it crashes, asks the LLM to self-correct and retry
   - Agent 4 traverses the transaction network graph to find multi-hop layering
   - An arbitration layer synthesizes conflicts between Agent 3 and Agent 4 risk scores
   - Agent 5 identifies which CFR regulations apply and whether the 30-day SLA is at risk
   - Agents 6 & 7 generate the FinCEN-compliant SAR narrative and populate the Form 111 fields
4. Maestro suspends at **Gate 2** (BSA Officer Review) — the officer approves via Orchestrator
5. Agent 8 generates a SHA-256 immutable audit hash and logs the submission

### What Makes Agent 3 Technically Unique
Most "AI" systems in compliance use hard-coded rules. Agent 3 is fundamentally different:

- **Dynamic code generation**: the LLM reads the alert type and transaction format and writes a custom detection function from scratch — *every time, for every case*
- **Live code execution**: that generated function runs against real transaction data in a sandboxed Python namespace
- **Self-reflection loop**: if the generated code raises an exception, Agent 3 sends the error back to the LLM with the instruction to fix it — true agentic self-correction
- **Graceful fallback**: if both retries fail, the agent switches to a static rule-based detector and logs the failure — no crash, no data loss, full audit trail

### UiPath Maestro Case — Why This Is Track 1
This is a canonical Track 1 use case: AML investigation is inherently *dynamic and exception-heavy*. Cases branch unpredictably — sanctions hits change the path, code generation failures trigger fallbacks, network graph traversal discovers unexpected layering. This is exactly what Maestro Case is designed for — **open-ended case management with human handoffs at key decision points**.

The BPMN filing stage (Track 2) is architecturally separate by design, following UiPath's own documented best practice for AML: "Stages 1–3 run as an open-ended Maestro Case. Once the SAR decision is made, filing is a BPMN flow."

### Built With UiPath for Coding Agents
This **entire project** — all 8 agents, all deployment commands, all configuration files, and all debugging — was built using **Gemini CLI** running through the UiPath for Coding Agents capability. We used natural language to generate, deploy, debug, and redeploy LangGraph agents to UiPath Orchestrator in real time.

---

## Technologies Used
- UiPath Maestro Case (Track 1 orchestration)
- UiPath Coded Agents — LangGraph (Gate 1 + Gate 2 HITL)
- UiPath Orchestrator (job management, suspension, resume)
- UiPath for Coding Agents — Gemini CLI (all development)
- LangGraph `interrupt()` — API Trigger HITL pattern
- AWS Bedrock — Meta Llama 3.1 70B Instruct
- LangChain (LLM interface layer)
- FastAPI + uvicorn (investigation microservice)
- Python 3.11+

---

## Screenshots to Include on Devpost Page
1. Screenshot of Orchestrator Processes list showing all deployed Coded Agents
2. Screenshot of Maestro Case plan with Stage 1 and Gate 1 visible
3. Screenshot of Orchestrator Job in "Suspended" state with interrupt payload visible (Gate 1)
4. Screenshot of Orchestrator Job in "Suspended" state (Gate 2)
5. Screenshot of the FastAPI /docs page showing the endpoint
6. Terminal screenshot showing Agent 3 generating and executing LLM code live

---

## Demo Video Script (5 minutes)

**[0:00 – 0:30] The Hook**
"$4.6 billion in AML fines in 2024 alone. Every bank has 30 days to file — and today's analysts spend 12 hours doing it by hand. SentinelFin does it in seconds, with AI agents. But here's the key: humans stay in control at every gate."

**[0:30 – 1:00] Architecture Overview**
Show the README architecture diagram. Briefly name each stage.

**[1:00 – 2:00] Gate 1 Demo**
Open Maestro. Trigger a case with the layering scenario. Watch the timeline pause at Gate 1. Open Orchestrator Jobs — show the suspended job with the triage payload JSON visible (case_id, risk_score, instructions). Resume it with `{"status": "approved"}`.

**[2:00 – 3:30] Investigation Pipeline (The Technical Centrepiece)**
Switch to terminal. Show the FastAPI server logs. Highlight Agent 3: "Watch what happens — Llama 3.1 is writing Python code live, right now, to detect this specific pattern." Show the generated code printing to the terminal. Show it execute and return a risk score of 85. Show the SAR narrative being generated.

**[3:30 – 4:15] Gate 2 Demo**
Back in Maestro. Watch the timeline move to Gate 2. Orchestrator shows the job suspended again with the SAR narrative payload. Resume with `{"approved": true, "signature": "Jane Smith — BSA Officer"}`. Case completes.

**[4:15 – 4:40] Error Handling Demo (Resilience)**
"What happens if the LLM-generated code crashes?" Show the self-reflection loop in the logs. Show the graceful fallback. "The system never crashes. It adapts."

**[4:40 – 5:00] Coding Agents Bonus**
Screen-record this Gemini CLI conversation. "This entire system was built using Gemini CLI — UiPath for Coding Agents. Every agent, every deployment command, written by natural language."

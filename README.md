# SentinelFin: AML Investigation Pipeline

SentinelFin is a prototype Anti-Money Laundering (AML) application. It demonstrates how to orchestrate a complex AI investigation workflow while deeply integrating with the UiPath Automation Cloud for data persistence and human-in-the-loop (HITL) review.

> **🏅 Hackathon Track:** This project is submitted under **Track 1: UiPath Maestro Case**. SentinelFin orchestrates a dynamic, exception-heavy AML investigation using UiPath case management capabilities. Because financial crime investigations have unpredictable paths and require moving work through distinct stages (Intake ➔ Investigation ➔ SAR Filing), a Maestro Case acts as the top-level orchestrator. It seamlessly manages handoffs between our external LangGraph AI agents, enterprise UiPath APIs, and human BSA Officers—keeping humans in charge at key decision points.

---

## 💡 Inspiration
Banks spend billions manually investigating AML alerts. A typical compliance analyst spends hours reviewing raw SWIFT logs, correlating entities, and drafting Suspicious Activity Reports (SARs) manually. This extreme bottleneck leads to SLA breaches and analyst burnout. We wanted to build a solution that doesn't just summarize text, but actively orchestrates a compliant investigation pipeline.

## 💻 What it does (The Data Pipeline)
SentinelFin ingests raw transactional data, processes it through specialized AI agents to determine risk, and prepares a SAR for final human review.

1. **Data Ingestion:** The user uploads raw evidence (e.g., a PDF bank statement or CSV) via the React dashboard.
2. **AI Processing (The 8-Agent Investigation Team):** The data is routed to a FastAPI backend where a massive multi-agent pipeline processes the case:
   - **Agent 1 (Transaction Context):** Ingests the raw transaction JSON payload (acting as a mock database lookup) and normalizes the data for the investigation.
   - **Agent 2 (Sanctions & PEP Screener):** Cross-references the originator and beneficiary names against OFAC lists, FBI Most Wanted databases, and global PEP (Politically Exposed Persons) registries to detect known criminals.
   - **Agent 3 (Pattern Detection - Coding Agent):** The centerpiece of the AI. It calls Llama 3.1 dynamically to write a custom Python detection script on the fly to detect specific layering typologies, executes the code safely in an isolated environment, and calculates a mathematical risk score.
   - **Agent 4 (Network Investigation):** Maps the relationships between entities to uncover hidden offshore shell company networks and multi-hop transactions.
   - **Agent 5 (Regulatory Intelligence):** Determines the exact FinCEN SLA reporting deadlines (e.g., 30-day filing limit) based on the alert type and global jurisdiction.
   - **Agent 6 (SAR Narrative Writer):** Uses Llama 3.1 70B to draft a highly professional, multi-page FinCEN-compliant Suspicious Activity Report (SAR) narrative based on the findings of Agents 1-5.
   - **Agent 7 (SAR Form Population):** Structurally maps the unstructured SAR data directly into the strict JSON schema required by the FinCEN Form 111 e-filing system.
   - **Agent 8 (Submission):** The final orchestrator that generates the audit trail, synchronizes structured entity data to UiPath Data Service for enterprise record-keeping, and dispatches the final approval alerts to enterprise communication channels (Slack and Jira).
3. **Real-time UI Updates:** As the Python backend executes these 8 high-level stages, it streams the state to the frontend using Server-Sent Events (SSE), updating the dashboard in real-time.
4. **Governed Handoff:** The process is entirely governed by the **UiPath Maestro Case**. Maestro natively enforces the governance rules, routing the case to Action Center for human approval at Gate 1 and Gate 2, ensuring humans are always in control of the AI.

## 🏗️ Architecture Diagram

```mermaid
graph TD
    subgraph UiPath Enterprise Governance - Maestro
        M_Start((Start Alert))
        M_Start --> A1[Agent 1: Initial Investigation]
        A1 --> G1{Gate 1: Triage Analyst}
        
        G1 -->|Approve| A4[Agent 4: Deep AI Investigation]
        G1 -->|Reject| M_End((End))
        
        A4 --> G2{Gate 2: BSA Officer}
        G2 -->|Approve| A8[Agent 8: Final Sync]
        A8 --> M_End
    end
    
    subgraph External Agentic Backend (Python)
        F_API1(FastAPI: Part 1)
        F_API2(FastAPI: Part 2)
        F_API3(FastAPI: Part 3)
        
        LLM[AWS Bedrock Llama 3.1]
        
        F_API1 -.->|Calls LLM| LLM
        F_API2 -.->|Calls LLM| LLM
    end
    
    subgraph Custom UI (React)
        Dash[SentinelFin Passive Dashboard]
        HTML_Report[Dedicated /report Document]
    end
    
    %% Maestro HTTP Connections
    A1 ==>|HTTP POST| F_API1
    A4 ==>|HTTP POST| F_API2
    A8 ==>|HTTP POST| F_API3
    
    %% UI and Human Connections
    F_API1 -.->|Streams real-time SSE| Dash
    F_API2 -.->|Streams real-time SSE| Dash
    F_API3 -.->|Streams 100% Complete| Dash
    
    G2 -.->|Officer clicks link| HTML_Report
```

## ⚙️ How we built it (Tech Stack & Integrations)

### 🏆 Bonus: Built with UiPath for Coding Agents
**We are claiming the Coding Agent bonus points!** Please see our dedicated [CODING_AGENTS.md](./CODING_AGENTS.md) file for the complete authorship table and concrete evidence of how we used Antigravity CLI to collaboratively build this governed architecture.

### The Core Stack
- **Backend:** Python, FastAPI, LangGraph (Multi-Agent State Machine)
- **Frontend:** React, Vite, Server-Sent Events (SSE)
- **LLM:** AWS Bedrock (Llama 3.1 70B)

### UiPath Integrations
We integrated directly with several UiPath services to handle the enterprise routing and review process:

1. **UiPath Maestro (Process Orchestration):**
   - **Usage:** UiPath Maestro serves as the central brain of the investigation. It triggers the Python AI backend, waits for the multi-agent system to complete its tasks, and natively manages the routing of data between human decision gates.
   - **Purpose:** Proves that complex multi-agent LLM architectures can be seamlessly governed by UiPath's enterprise process orchestration.
2. **UiPath Action Center (Human-in-the-Loop):** 
   - **Usage:** Maestro creates native Form Tasks in Action Center to present the AI's findings (Gate 1: Triage, Gate 2: BSA Sign-off) to the compliance officer. The Python server generates a dedicated `/report` HTML endpoint allowing the officer to review the massive 5-page SAR document securely before approving the Action Center ticket.
   - **Purpose:** Keeps humans in charge at key decision points, preventing autonomous AI actions without strict compliance sign-off.
3. **UiPath Autopilot:**
   - **Usage:** Used live during the demonstration to explain the complex BPMN architecture, generate dynamic C# expressions to parse the AI's JSON outputs, and instantly summarize the massive SAR document.
   - **Purpose:** Demonstrates how UiPath Autopilot accelerates both developer productivity and business user efficiency when interacting with external AI agents.
4. **UiPath Integration Service (Slack / Jira):**
   - **Usage:** Once Gate 2 is approved in Action Center, Maestro automatically triggers the final agent to dispatch alerts to enterprise channels.

## 🚧 Challenges we ran into
Integrating a fully autonomous LangGraph pipeline with an asynchronous enterprise platform like UiPath Action Center was challenging. We had to ensure the AI gracefully paused its execution state while handling the OAuth 2.0 Bearer token lifecycle securely inside our Python microservice.

## 🏆 Accomplishments that we're proud of
1. **Live SSE Streaming:** Watching the React dashboard update in real-time as the 8 agents process the transactional graph provides total transparency to the end-user.
2. **Authentic API Integration:** We successfully connected our external Python application directly to the live UiPath Cloud APIs for Action Center and Data Service using proper OAuth client credentials.

## 📖 What we learned
We learned the immense value of combining Agentic AI frameworks with Robotic Process Automation (RPA). AI is brilliant at unstructured reasoning, but it lacks the guardrails, auditability, and deterministic routing that UiPath provides. Combining them creates a highly resilient enterprise solution.

## 🚀 What's next for SentinelFin
- **Native Orchestrator Webhooks:** Building webhooks to resume the LangGraph execution the moment a human clicks "Approve" in Action Center.
- **Document Understanding:** Integrating UiPath Document Understanding to natively OCR the massive PDF bank statements before feeding them into Bedrock.

---

## 🛠️ Setup & Execution

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
# AWS Credentials for LLM Processing
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=us.meta.llama3-1-70b-instruct-v1:0

# External Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# UiPath API Credentials
UIPATH_CLIENT_ID=your-client-id
UIPATH_CLIENT_SECRET=your-client-secret
UIPATH_ORG=your-org-name
UIPATH_TENANT=DefaultTenant
```

### 2. Run the Application
Start the FastAPI backend and React frontend simultaneously using the provided script:
```bash
bash ./start_demo.sh
```
Navigate to `http://localhost:5173/` to use the application.

# 🏆 Bonus Claim: UiPath for Coding Agents

This project officially claims the **"UiPath for Coding Agents" Bonus Points**. 

To bridge the gap between a prototype on a laptop and governed enterprise software running in production, we utilized **UiPath for Coding Agents (Antigravity CLI)** as an autonomous co-pilot throughout the 7-week hacking period. 

The coding agent was instrumental in helping us architect a solution that **blends UiPath-native orchestration with external agents**, specifically accelerating our integration with the UiPath Orchestrator and Data Service REST APIs.

## 👥 Authorship Table

The following table canonicalizes the division of labor between the Human Developer and the Antigravity Coding Agent:

| Architectural Component | Human Responsibility | Agent Responsibility |
| :--- | :--- | :--- |
| **UiPath Maestro Case** | Modeled the BPMN workflow, defined SLA timers, configured the human-in-the-loop gates (Action Center), and designed the top-level case lifecycle. | N/A (UiPath Native) |
| **External Agent Framework (LangGraph)** | Defined the business rules for AML compliance, authored the prompts for the Llama 3 models, and provided the strict FinCEN Form 111 JSON Schema. | Scaffolded the 8-node LangGraph Python architecture. Wrote the asynchronous state-machine routing logic and Python type-checking for the agents. |
| **Live UI Dashboard (React)** | Designed the UI mockups and defined the user experience requirements for the compliance officers. | Wrote the React/Vite components, CSS styling, and implemented the complex Server-Sent Events (SSE) logic to consume the LangGraph stream. |
| **UiPath Cloud API Integration** | Registered the External Application in Automation Cloud, configured OAuth scopes (`OR.Tasks.Write`, `DataService.Data.Write`), and secured the credentials. | Wrote the Python `integrations/uipath_api.py` module. Handled the `client_credentials` OAuth 2.0 flow and constructed the correct OData payloads for Action Center and Data Service. |

## 🔎 Specific Agentic Evidence

Here are two concrete examples of how the coding agent handled real-world complexity to connect our external framework to the governed UiPath layer:

### 1. Navigating the UiPath Orchestrator OData API
Integrating external Python applications with UiPath Action Center requires precise knowledge of the OData specification. The human developer provided the OAuth tokens, and the Antigravity agent autonomously researched and wrote the exact Python function to create the `UiPath.Server.Configuration.OData.CreateExternalTask` payload, significantly reducing integration time.

### 2. Solving Asynchronous State Streaming
Because an 8-agent LangGraph investigation takes time, we needed the React dashboard to update in real-time. The coding agent autonomously designed and implemented a **Server-Sent Events (SSE)** architecture in FastAPI, allowing the external AI's "thought process" to stream live to the user before the final payload is returned to the Maestro Case for governance.

---

> *"The coding agent allowed us to focus entirely on the AML business logic and the top-level UiPath Maestro governance, while it handled the heavy lifting of the asynchronous Python plumbing and REST API implementation."*

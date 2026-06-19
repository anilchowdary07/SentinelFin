# SentinelFin — UiPath Product Feedback
# For the Best Product Feedback Award ($1,500)
# Submit at: https://forms.office.com/e/KitjGLF5k1

---

## Product: UiPath Maestro Case

### ✅ What Works Extremely Well

**1. Case lifecycle management is intuitive for AI-first workflows.**
The concept of a Case as an open-ended container that can suspend, resume, and branch is architecturally perfect for AML investigation. Most AML cases have unpredictable paths — a sanctions hit changes everything, a pattern discovery triggers escalation — and the Case model handles this elegantly without requiring a pre-mapped BPMN flow.

**2. Global variables propagation between stages is clean.**
Being able to pass `risk_score`, `sar_narrative`, and `case_id` as Case variables that are accessible across all stages makes cross-agent communication straightforward. No message passing infrastructure needed.

**3. Maestro correctly reflects suspended state from LangGraph `interrupt()`.**
When a LangGraph Coded Agent calls `interrupt({...})`, Maestro's timeline UI shows the job as paused indefinitely. This is the critical HITL behavior — and it works. The visual feedback in the Maestro timeline that the case is "waiting on a human" is exactly what a compliance team needs to see.

---

### 🔧 Friction Points & Feature Requests

**1. [CRITICAL GAP] No CLI command to create Action Center Apps.**
`uip codedagent` has no capability to create, configure, or publish Action Center Apps. The `interrupt(CreateTask(app_name=...))` pattern requires an Action Center App to exist in the UiPath Cloud, but the ONLY way to create one is through the browser-based App Studio. This is a massive gap for teams using the UiPath for Coding Agents workflow — if you're building everything via CLI, you hit a wall as soon as you need a structured human task form.

**Feature Request:** `uip apps create --name "BSASignatureGate" --folder "Shared" --inputs "case_id:string,sar_narrative:string" --outputs "bsa_signature:string"`

**2. [CONFUSION] `interrupt({...})` raw dict pattern vs `CreateTask` pattern — documentation is unclear.**
The docs show both patterns but don't clearly explain when each is appropriate, what the Orchestrator UI shows for each, or how a human resumes a raw `interrupt({...})` job via the UI vs. the API. We had to discover through experimentation that the raw dict pattern requires the human to use the Orchestrator Jobs "Resume" button with a JSON payload — this is powerful but undocumented.

**Feature Request:** A dedicated "HITL Pattern Selection Guide" in the docs with side-by-side comparison of all 6 patterns (API Trigger, CreateTask, CreateEscalation, WaitTask, InvokeProcess, WaitJob).

**3. [BUG] Deploying a LangGraph agent after a Function-type agent with the same package name fails with error 2007.**
When `uip codedagent deploy` is used to deploy a LangGraph agent (type=Agent) to a package name that previously had a Function-type package, Orchestrator rejects it with:
```
"Project type has changed since the latest published version (was Agent, now is Function)"
```
This forces the developer to use a new package name. The error message is also inverted — it says "was Agent, now is Function" when the actual situation is "was Function, now is Agent."

**Fix Request:** Either allow project type changes (with a confirmation prompt) or provide a `uip codedagent delete-package` command so the old package can be removed.

**4. [UX] Maestro process discovery only shows processes from specific folders.**
When configuring an Agentic Process task in Maestro Stage, the process selector only shows processes in specific folder scopes. Processes deployed to "My Workspace" are not visible to Studio Web's Maestro designer unless specifically deployed to the "Shared" folder. The error message ("Cannot find process") gives no indication that this is a folder scoping issue.

**Feature Request:** Process selector should show all available processes across all folders the user has access to, with folder labels for context. Or the error message should specify which folder was searched.

**5. [FEATURE REQUEST] Add a `uip codedagent run-cloud` command.**
Currently, triggering a cloud job requires either clicking "Debug on Cloud" in Studio Web or using the Orchestrator REST API manually. A CLI command to trigger a process job in Orchestrator would complete the developer workflow:

```bash
uip codedagent run-cloud --process agent_1_triage --input '{"case_id":"CASE-001","risk_score":85,"context_data":{}}'
```

---

## Product: UiPath for Coding Agents (Gemini CLI)

### ✅ What Works Extremely Well

**1. The `uip codedagent init` + `deploy` loop is genuinely fast.**
From writing a LangGraph agent to having it deployed as an Orchestrator process took under 60 seconds. The mermaid diagram auto-generated from the graph topology is a nice touch for documentation.

**2. `uip codedagent run` with `--resume` for local HITL testing is brilliant.**
Being able to test the full interrupt/resume cycle locally without Orchestrator is a massive developer experience win. This let us verify the LangGraph state management before touching the cloud.

### 🔧 Friction Points

**1. The `.venv` inside each agent directory causes confusion with tool paths.**
Each `uip codedagent init` creates an isolated `.venv`, but the `uip codedagent deploy` command needs to be run from within that directory with that venv activated. There's no way to deploy all agents from the project root in a single command.

**Feature Request:** `uip codedagent deploy --all` that discovers all agent directories (by presence of `uipath.json`) and deploys them in sequence.

**2. `uip codedagent init` fails when re-run on a project that changed type (Function → Agent).**
Described in point 3 above. The `init` command successfully regenerates files but the subsequent `deploy` fails.

---

## Summary Impact Assessment

Building SentinelFin on UiPath for Coding Agents was genuinely the fastest path to a deployed, cloud-orchestrated multi-agent system we've experienced. The LangGraph + UiPath SDK integration is the most sophisticated HITL capability available in any enterprise automation platform.

The gaps identified above — particularly the Action Center App CLI gap and the HITL pattern documentation — are the single biggest barriers to wider adoption by the developer community. Solving them would make UiPath for Coding Agents a complete end-to-end developer experience.

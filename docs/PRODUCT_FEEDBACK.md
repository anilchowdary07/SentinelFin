# 📈 Product Feedback: UiPath Maestro & Agent Builder

Building SentinelFin during this hackathon pushed the absolute limits of the UiPath Platform. Here is our constructive, technical feedback on the next-generation products we utilized.

## 1. UiPath Maestro (Case Management)
**What we loved:**
- The concept of "Case Plans" abstracting the raw BPMN logic is a game-changer for business users.
- The seamless integration with Action Center makes Human-in-the-Loop workflows incredibly easy to design at the macro level.

**Opportunities for Improvement:**
- **State Persistence:** Currently, passing dynamic JSON objects (like an evolving AI investigation case) between Maestro stages requires complex serialization. Native "JSON Object" variables inside Maestro would greatly simplify LLM prompt chains.
- **Agent Integration:** We had to deploy Python Coded Agents manually to Orchestrator to bypass the UI constraints. Direct UI support for attaching Python `requirements.txt` to a Maestro step would streamline development.

## 2. UiPath Coded Agents (Python)
**What we loved:**
- The `uip codedagent` CLI tool is fantastic. Being able to write pure Python LangGraph/ReAct logic and deploy it serverlessly into the Orchestrator environment is incredibly powerful.
- Integrating external webhooks (like our FBI API and Live Bitcoin Blockchain calls) was flawless because we had pure Python access.

**Opportunities for Improvement:**
- **Local Debugging:** Debugging Coded Agents currently requires a heavy trial-and-error loop of deploying to the cloud. A local `uip run --local` emulator that mimics the Orchestrator environment would speed up development 10x.

## 3. The Future of AI in UiPath
By combining the deterministic power of Maestro with the non-deterministic reasoning of AWS Bedrock Llama 3.1, we proved that AI doesn't have to be a "black box". UiPath provides the essential guardrails (Action Center, Orchestrator Audit Logs, Data Service) that make Agentic AI safe for heavily regulated industries like Banking.

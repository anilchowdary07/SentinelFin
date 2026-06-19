# SentinelFin Build Log & Product Feedback

This log captures real-time friction points encountered during the end-to-end integration of SentinelFin (a Python-based multi-agent backend) with UiPath Maestro and Agent Builder.

## 1. The Python to UiPath Handoff Friction
**Friction Point:** Bridging complex JSON objects from Python APIs into UiPath Maestro Case properties is overly manual.
**Details:** Our FastAPI backend outputs deeply nested JSON (e.g., `fincen_payload.part_1_subject_information.primary_subject`). When using the `HTTP Request` activity in UiPath Studio to hit our API, developers must manually deserialize the JSON and write cumbersome assignment logic (`cint(jsonResponse("risk_score").ToString)`) to map it to Maestro Case properties.
**Recommendation:** Add native JSON Schema importing directly into Maestro Case Definitions. If a developer provides an OpenAPI swagger URL (like our `/docs`), Maestro should be able to automatically map the API response payload into Case State variables without requiring an intermediate Studio sequence.

## 2. Agent Builder Limitations for Code-Heavy AI
**Friction Point:** UiPath Agent Builder lacks a true sandbox for dynamic Python code execution.
**Details:** Our project relies on Meta Llama 70B dynamically generating and running Python scripts on the fly to detect new AML patterns. We had to build this outside of UiPath Agent Builder (as a FastAPI microservice) because Agent Builder does not currently support dynamic compilation/execution of custom scripts generated at runtime by LLMs.
**Recommendation:** Introduce a "Dynamic Code Execution Sandbox" node in Agent Builder, which allows developers to safely pass dynamically generated scripts from LLMs into a secure Python execution context.

## 3. Maestro Versioning is High-Friction
**Friction Point:** Modifying a live Maestro process requires full redeployment and recreation of active test cases.
**Details:** While building the Action Center gates for our Human-in-the-Loop review, every slight modification to the BPMN diagram (e.g., changing a transition condition from `Risk_Score > 80` to `Risk_Score >= 80`) forced us to redeploy the process and create brand new cases from scratch to test the updated logic.
**Recommendation:** Implement a "Hot Reload" testing mode for Maestro where simulated cases can be re-run from specific states without requiring full republishing.

## 4. Debugging Coded Agents
**Friction Point:** Debugging the orchestration between UiPath and external Python microservices lacks unified telemetry.
**Details:** When our "Controlled Crash" resilience demo fired, we had to monitor our Python terminal logs and the UiPath Orchestrator logs in separate windows to trace the exception handling.
**Recommendation:** Allow external API error logs to natively pipe into Orchestrator’s telemetry if the API request originated from a Maestro workflow.

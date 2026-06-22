# 🏦 SentinelFin: Autonomous AML Compliance Factory

## The Problem: The Billion-Dollar AML Bottleneck
Banks spend billions manually investigating Anti-Money Laundering (AML) alerts. Analysts waste hours drafting Suspicious Activity Reports (SARs), leading to SLA breaches and massive regulatory fines. 

## 🚀 The Solution
SentinelFin is an autonomous compliance factory. We built a system that automates 90% of the investigative drafting using **AWS Bedrock (Llama 3)**, while using **UiPath Maestro** to strictly enforce human compliance sign-off.

## 🛠️ Deep Platform Usage
- **UiPath Maestro Case:** Manages the SLA timers and the macro-stages of the investigation (Triage ➔ AI Investigation ➔ SAR Submission).
- **UiPath Maestro BPMN:** The strict rules engine that orchestrates our AI. 
- **UiPath Coded Agents (Serverless):** 8 custom Python microservices handling sanctions screening and pattern detection.
- **UiPath Apps:** Our custom Human-in-the-Loop UI where BSA Officers review and sign the AI's work.
- **UiPath Data Service:** Centralized entity tracking for long-term auditability.

## 🤖 Built with AI (Agentic Coding)
To move at maximum speed, we utilized advanced Agentic Coding Assistants to debug Orchestrator environment collisions, write Live REST API integrations to the FBI database, and rapidly deploy our serverless architecture.

## 🛡️ Real External Integrations & Exception Handling
We didn't just use mock data. Our Agent 2 makes **Live REST API queries to the official US FBI Most Wanted database**. Furthermore, our BPMN diagram utilizes native **Error Boundaries** to gracefully catch and handle agent failures, proving true enterprise resilience. 

## 🔧 Setup Instructions
1. Deploy the Python Coded Agents using the `uip codedagent deploy` CLI to your Orchestrator.
2. Import the `Maestro Case` and `Agentic Process` BPMN from the `/maestro` folder into Studio Web.
3. Import the `SimpleApprovalApp` into UiPath Apps and link it to the Maestro Workflow.
4. Provide AWS Credentials (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) as Orchestrator Assets.
5. Trigger the Maestro Case to begin the autonomous investigation!

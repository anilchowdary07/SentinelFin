# SentinelFin: 3-Minute Demo Script

*This script is optimized for a strict 3-minute time limit. Speak clearly and practice timing to ensure you hit the "Wow" moment (Agent 3) exactly on schedule.*

---

**[0:00 - 0:30] The Stakes & The Problem**
*Visual: Slide showing "$4.6 Billion" and "30 Days".*
"Last year, regulators handed down 4.6 billion dollars in AML fines to banks who failed to catch suspicious activity. The law requires banks to file a Suspicious Activity Report—or SAR—within 30 days of detecting a problem. Currently, analysts spend hours manually clicking through systems to do this. SentinelFin automates this entirely using UiPath Maestro and 8 specialized AI agents."

**[0:30 - 0:50] Alert Trigger & Triage (Agents 1 & 2)**
*Visual: UiPath Maestro Case view showing a new alert.*
"Here, a structuring alert just fired. Instantly, our Maestro case triggers Stage 1. Agent 1 uses LangChain to pull the customer's KYC and 90-day transaction history. In parallel, Agent 2 runs a sanctions check against OFAC lists, automatically handling API timeouts with exponential backoff."

**[0:50 - 1:30] The "Wow" Moment: Dynamic Pattern Detection (Agent 3)**
*Visual: Split screen. Left: Maestro process. Right: Terminal/Log view showing Claude Code generation.*
"Now for the centerpiece: Agent 3. Instead of relying on rigid, pre-written rules, Agent 3 is a Coded Agent that calls an LLM dynamically. It looks at the specific alert type—in this case, structuring—and asks Claude to generate a custom Python detection script on the fly. 
*(Point to logs)* 
Here you can see the LLM writing the code, and here, our isolated environment executing it against the transactions to calculate a risk score of 85. If it fails, it degrades gracefully to a static rule, ensuring zero downtime."

**[1:30 - 1:55] Human Gate 1 & Deep Investigation (Agents 4 & 5)**
*Visual: UiPath Process App - Triage Review UI.*
"Our first human gate. The analyst reviews the AI's findings in this Process App and clicks 'Escalate'. This triggers Agents 4 and 5. The Network Agent uses LangGraph to traverse the account graph, while the Regulatory Agent locks in our legal 30-day deadline."

**[1:55 - 2:30] SAR Preparation (Agents 6 & 7)**
*Visual: Maestro Case advancing to Stage 3.*
"The system now drafts the actual government report. Agent 6 uses a strict prompt engineered against FinCEN guidance to write the narrative—answering exactly who, what, when, where, why, and how, with zero hallucinations. Agent 7 maps this data onto FinCEN Form 111."

**[2:30 - 3:00] Gate 2 & Regulatory Submission (Agent 8)**
*Visual: Process App - BSA Officer Review, clicking 'Sign'. Slack popping up with a notification.*
"By law, a human must approve the SAR. The BSA officer reviews the narrative here in the Process App and checks the digital signature box. This unlocks Gate 2. Agent 8 then fires via Integration Service—it submits the mock e-file to FinCEN, captures the confirmation number, updates the Jira ticket, and alerts the compliance team on Slack. 
A process that takes hours, done in minutes, fully auditable. That's SentinelFin."

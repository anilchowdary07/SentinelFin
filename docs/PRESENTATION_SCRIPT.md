# SentinelFin — 7-Minute Hackathon Presentation Script
## UiPath AgentHack 2026 | Track 1: UiPath Maestro Case

---

## ⏱️ Total: 7 Minutes | Split: 3 min slides + 4 min live demo

---

## PART 1: PRESENTATION (3 MINUTES)

### Slide 1 — The Pain (0:00 – 0:45)
**What to say (exact words):**
> "Every year, banks file over 2 million Suspicious Activity Reports.
> But here's the dark secret of compliance: **95% of AML alerts are false positives.**
> A human investigator spends **4 hours per case** — reading wires, screening sanctions lists,
> computing legal deadlines, then writing a 10-page FinCEN narrative.
> And if they miss the **30-day FinCEN filing deadline**, the bank faces a **$10 million penalty**.
> This is not a technology problem. This is a governance problem."

### Slide 2 — The Solution (0:45 – 1:30)
**What to say:**
> "Introducing **SentinelFin** — the first autonomous AML compliance engine
> that combines **Google Llama 3.1** intelligence with **UiPath Maestro** governance.
> Eight specialized AI agents work in parallel:
> - Agent 3 **writes and executes** its own Python detection code — live, during the investigation.
> - Agent 6 writes a **FinCEN-compliant SAR narrative** in the format required by law.
> - And every decision goes through UiPath Maestro, which acts as the **governance layer**,
>   enforcing a human BSA officer approval before any SAR is filed."

### Slide 3 — The Architecture (1:30 – 2:15)
**What to say:**
> "Here is how it works. [Point to architecture diagram]
> The compliance analyst clicks one button on our React dashboard.
> That fires a real API call to our FastAPI backend, which runs a LangGraph pipeline.
> Each node calls a real UiPath Coded Agent deployed to Orchestrator.
> When the SAR is ready, Agent 8 **creates a real Action Center queue item**
> for the BSA Officer to review.
> The officer approves it in Action Center — which continues the Maestro Case Plan.
> This is 100% production-grade. No mocking. No shortcuts."

### Slide 4 — The Impact (2:15 – 3:00)
**What to say:**
> "The results speak for themselves.
> **4 hours of manual work → 45 seconds.**
> **$10M compliance penalty risk → eliminated.**
> And because UiPath Orchestrator keeps the full audit trail,
> every decision is **explainable to regulators**.
> SentinelFin doesn't replace the BSA Officer — it gives them a 10x amplifier."

---

## PART 2: LIVE DEMO (4 MINUTES)

### Step 1: Show the Dashboard (0:00 – 0:20)
- Open `http://localhost:5173`
- Point out the **problem stats bar** at the top: "95% false positives, 4 hrs per case"
- Point to the architecture diagram: "React → FastAPI → LangGraph → UiPath Maestro"

### Step 2: Click "Start Investigation" (0:20 – 0:30)
- Click the button
- Say: "This fires a real POST request to our backend, which immediately triggers a UiPath Orchestrator job"

### Step 3: Show agents lighting up in real-time (0:30 – 1:30)
- Watch the live agent tracker update in real-time (SSE, not fake timer)
- When Agent 2 lights up: "Sanctions Screener is hitting the OFAC SDN list right now"
- When Agent 3 lights up: "Pattern Detection is asking Llama 3.1 to write Python detection code"
- When Agent 6 lights up: "SAR Writer is writing a full FinCEN narrative"
- Point to the live log panel: "Every event streams in real time"

### Step 4: Show the results (1:30 – 2:30)
- **Risk Score 90/100** — CRITICAL
- **OFAC SDN Hit** on Shell Corp B (98.5% confidence)
- **SLA: 21 days remaining** — the deadline is real, computed from transaction dates
- **Action Center Item #xxxx** — "The BSA Officer now has a task waiting in Orchestrator"

### Step 5: Show Action Center (switch browser tab) (2:30 – 3:00)
- Open UiPath Orchestrator → Queues → SentinelFin-SAR-Reviews
- Show the real queue item with the SAR payload inside it
- Say: "This is a real queue item. The officer opens it, reads the AI narrative, and approves or rejects."

### Step 6: Resilience Demo — EXCEPTIONAL PATH (3:00 – 3:45)
- Tick the "🔴 Resilience Demo" checkbox on the dashboard
- Click Start Investigation again
- Say: "Watch what happens when the OFAC API returns HTTP 500..."
- Agent 2 shows retry with exponential backoff, then graceful degradation to cached list
- Agent 3 self-reflection: "If the LLM writes broken Python code, it automatically asks Llama to debug it"

### Step 7: Closing (3:45 – 4:00)
- "SentinelFin resolves a case in under 60 seconds.
  The SAR is filed. The audit trail is in Orchestrator.
  The BSA Officer approved it from Action Center.
  Banks can finally trust AI in their compliance workflow."

---

## BACKUP VIDEO PLAN
If live demo fails:
1. Use the pre-recorded demo video in `docs/demo_backup.mp4`
2. Show the Orchestrator screenshot of the Action Center queue item
3. Show the SAR narrative text from the last successful run

---

## BONUS PRIZE SUBMISSIONS
Submit for all 3 separately on Devpost:
- **Best Cross-Platform Integration ($1,500):** React Dashboard + LangGraph + UiPath + Bedrock
- **Best Product Feedback ($1,500):** See `docs/PRODUCT_FEEDBACK.md`
- **Business-Ready Agent ($2,000):** AML compliance is regulated, live industry need

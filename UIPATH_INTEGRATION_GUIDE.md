# UiPath Integration Guide: SentinelFin API

This guide explains how to integrate the SentinelFin Python AI Backend natively into UiPath Studio and UiPath Maestro. By exposing our Python agents as a FastAPI service, you can achieve 100% real UiPath platform usage.

## Architecture Concept
UiPath Maestro acts as the state machine and orchestration layer. When a case hits the "Deep Investigation" stage, a UiPath sequence uses an `HTTP Request` to call the SentinelFin API running locally (or hosted in the cloud). The API responds with the AI-generated Risk Score and SAR Narrative, which are then passed back into Maestro Case variables.

## Step 1: Start the SentinelFin API Server
Ensure your Python environment is active and the AWS Bedrock Key is set.
```bash
export AWS_BEDROCK_KEY="your-api-key"
uvicorn main:app --host 0.0.0.0 --port 8000
```
Verify it is running by navigating to `http://localhost:8000/docs` in your browser to see the Swagger UI.

## Step 2: Configure UiPath Studio
1. Open **UiPath Studio** and create a new Process.
2. Install the **UiPath.WebAPI.Activities** package via Manage Packages if you haven't already.
3. Drag an **HTTP Request** activity into your Main sequence.

## Step 3: Configure the HTTP Request
Set the properties of the HTTP Request activity as follows:
- **Endpoint:** `"http://localhost:8000/api/investigate"`
- **Method:** `POST`
- **BodyFormat:** `application/json`
- **Body:** Provide a serialized JSON string matching the expected `InvestigationPayload`. You can read `mock_data/scenario_layering.json` into a string variable and pass it here.
- **Headers:** Add `Content-Type: application/json`

## Step 4: Parse the Response
1. Create a string variable `strResponse` and assign it to the **Result** output property of the HTTP Request.
2. Use the **Deserialize JSON** activity to parse `strResponse` into a `JObject` variable named `jsonResponse`.
3. Extract the critical data fields into UiPath string/integer variables:
   - `RiskScore` (Int32) = `cint(jsonResponse("risk_score").ToString)`
   - `SarNarrative` (String) = `jsonResponse("sar_narrative").ToString`

## Step 5: Integrate with UiPath Maestro Case
Now that your UiPath sequence successfully receives data from the AI Agent, you can map this into Maestro.
1. Define a Maestro Case with a String property for `SAR_Narrative` and an Integer property for `Risk_Score`.
2. Within your sequence, use the **Update Case** activity to write the values extracted in Step 4 back into the active Maestro Case.
3. Configure a Maestro transition condition: If `Risk_Score > 80`, route the case to the "BSA Officer Review" (Gate 2) Action Center Task.

You have now successfully orchestrated a dynamic Python AI Agent using native UiPath platform tools!

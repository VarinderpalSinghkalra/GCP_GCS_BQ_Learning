 Spend Agent – BigQuery Data Store Integration (Production SOP)

Document Purpose

This document describes the approved, production-level steps to connect a BigQuery spend dataset with a dedicated Conversational Agent using Vertex AI Data Stores.

⸻

1. Architecture Overview

BigQuery (US multi-region)
   ↓
Vertex AI Data Store (Search / Retrieval)
   ↓
Retrieval Tool
   ↓
Spend Insight Agent

Design principle:
The agent must only consume curated analytics data and must not directly access pipeline or transactional datasets.

⸻

2. Mandatory Constraints (Non-Negotiable)

Component	Requirement
BigQuery dataset	US (multi-region)
BigQuery table	Native, non-empty
Data Store location	US
Agent project	Same project
Tool type	Retrieval / Search

If any one condition fails, the data store will not be visible inside the agent.

⸻

3. BigQuery Setup (Production)

3.1 Create Agent-Facing Dataset (US)

CREATE SCHEMA `PROJECT_ID.spend_agent_us`
OPTIONS (
  location = "US",
  description = "Curated spend analytics dataset for conversational agent"
);

3.2 Create Curated Spend Table

CREATE OR REPLACE TABLE `PROJECT_ID.spend_agent_us.spend_summary` AS
SELECT
  transaction_date,
  category,
  vendor,
  amount,
  region
FROM `PROJECT_ID.pipeline_uc1.spend_raw`;

3.3 Validation Check

SELECT COUNT(*) FROM `PROJECT_ID.spend_agent_us.spend_summary`;

Result must be > 0.

⸻

4. IAM Configuration (Least Privilege)

Grant read-only access to the Vertex AI service account:

service-<PROJECT_NUMBER>@gcp-sa-aiplatform.iam.gserviceaccount.com

Required roles:

roles/bigquery.dataViewer
roles/bigquery.metadataViewer
roles/discoveryengine.viewer
roles/aiplatform.user


⸻

5. Create Vertex AI Data Store

Console Path

Vertex AI → Conversational Agents → Data Stores → Create

Configuration

Field	Value
Source	BigQuery
Location	US
Dataset	spend_agent_us
Table	spend_summary
Data Store Name	spend_ds

⏳ Wait until Status = ACTIVE

Data stores in CREATING or INDEXING state will not appear in agents.

⸻

6. Spend Agent Creation

Vertex AI → Conversational Agents → Create Agent

Agent name:

spend-insight-agent

Purpose:

Provides accurate spend analytics using curated BigQuery data.

⸻

7. Tool Configuration (Critical Step)

7.1 Create Retrieval Tool

Agent → Tools → Create Tool

Tool type:
	•	✅ Retrieval / Search
	•	❌ NOT Webhook
	•	❌ NOT OpenAPI-only

7.2 Attach Data Store

Tool → Data Stores → Add → spend_ds → Save

If spend_ds is not visible:
	•	Stop execution
	•	Revalidate Sections 2–5

⸻

8. Agent System Instructions (Production Prompt)

You are a Spend Analytics Agent.

Use only the connected data store to answer questions.
Base all answers strictly on retrieved data.
If data is unavailable, respond with "Data not available".
Do not hallucinate or estimate values.
Provide concise summaries and clear breakdowns.


⸻

9. Validation & Testing

Run in Agent Simulator:

What is total spend by category?
Which vendor has highest spend?
Show last 30 days spend trend

Expected behavior:
	•	Grounded answers
	•	No hallucination
	•	Consistent totals

⸻

10. Known Failure Scenarios

Issue	Impact
Dataset in us-central1	Data store invisible
Data store not ACTIVE	Not attachable
Wrong project selected	Data store missing
OpenAPI-only tool	No retrieval
Empty table	Generic agent replies


⸻

11. Operational Best Practices
	•	Maintain separate datasets for pipelines and agents
	•	Refresh agent dataset via scheduled copy jobs
	•	Never expose raw transactional tables to agents
	•	Use one agent per domain (Spend, Tickets, Info)

⸻

12. Executive Summary

A dedicated Spend Insight Agent was implemented using a US-region BigQuery dataset indexed through a Vertex AI Data Store and attached via a retrieval-enabled tool, ensuring secure, grounded, and production-ready analytics responses.

⸻

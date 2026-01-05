 🧠 Insight Agent Architecture

**AI-Driven Analytics & Insights using BigQuery and Gemini**

---

## 1. Purpose

The **Insight Agent** is designed to provide **data-driven, analytical insights** over support ticket data using **natural language queries**.
It transforms operational ticket data into **actionable intelligence** for engineering, support leadership, and product teams.

This agent is **read-only**, analytical by design, and completely isolated from ticket creation or operational workflows.

---

## 2. Scope (What the Insight Agent Does)

The Insight Agent is responsible for:

* Answering analytical questions (trends, SLAs, volumes)
* Generating SQL queries from natural language prompts
* Executing read-only queries on BigQuery
* Summarizing query results into human-readable insights

The Insight Agent **does NOT**:

* Create or update tickets
* Write to Firestore or BigQuery
* Perform operational actions

---

## 3. High-Level Architecture

![Image](https://miro.medium.com/v2/da%3Atrue/resize%3Afit%3A1200/0%2AuPiPPnDmEOsIzJGN)

![Image](https://storage.googleapis.com/gweb-cloudblog-publish/images/2_F1GBxgE.max-1700x1700.png)

![Image](https://storage.googleapis.com/gweb-cloudblog-publish/images/9_-Architecture_Diagram.max-1600x1600.png)

---

## 4. Component Overview

### 4.1 Insight Agent (Vertex AI)

* Built using **Vertex AI Conversational Agents**
* Powered by **Gemini** for:

  * Natural language understanding
  * SQL generation
  * Result summarization
* Operates under strict analytical instructions

**Key Responsibility**

> Convert user questions into SQL and explain results — not to manage data.

---

### 4.2 Analytics Data Store

**Google BigQuery**

* Acts as the **single source of truth for analytics**
* Stores denormalized, query-optimized ticket data
* Optimized for:

  * Aggregations
  * Time-series analysis
  * SLA reporting
  * Trend detection

BigQuery is accessed in **read-only mode** by the Insight Agent.

---

## 5. Data Model (Analytics View)

**Dataset:** `support_analytics`
**Table:** `tickets`

| Column          | Type      | Description                  |
| --------------- | --------- | ---------------------------- |
| ticket_id       | STRING    | Unique ticket identifier     |
| reporter_id     | STRING    | User who raised the ticket   |
| priority        | STRING    | P1 / P2 / P3 / P4            |
| status          | STRING    | new / in_progress / resolved |
| created_at      | TIMESTAMP | Ticket creation time         |
| updated_at      | TIMESTAMP | Last update time             |
| resolved_at     | TIMESTAMP | Resolution timestamp         |
| response_due_at | TIMESTAMP | SLA response deadline        |
| resolve_due_at  | TIMESTAMP | SLA resolution deadline      |
| issue_text      | STRING    | Ticket description           |

This table is populated via a **separate ingestion pipeline** (out of scope for this document).

---

## 6. Insight Query Flow

```
User
 → Insight Agent (Gemini)
   → SQL Generation (BigQuery dialect)
     → BigQuery (SELECT-only execution)
       → Result Set
         → Gemini Summary
           → User
```

---

## 7. Example User Questions Supported

* “How many P1 tickets were created last week?”
* “Which tickets breached SLA this month?”
* “Average resolution time by priority”
* “What are the top recurring issues in the last 30 days?”
* “Show ticket volume trend over time”

---

## 8. SQL Generation Strategy

The Insight Agent:

* Generates **BigQuery-compatible SQL**
* Uses only:

  * `SELECT`
  * `WHERE`
  * `GROUP BY`
  * `ORDER BY`
  * Time-based filters
* Never performs data mutations

**Example**

```sql
SELECT priority,
       AVG(TIMESTAMP_DIFF(resolved_at, created_at, MINUTE)) AS avg_resolution_minutes
FROM support_analytics.tickets
WHERE resolved_at IS NOT NULL
GROUP BY priority;
```

---

## 9. Security & Guardrails

* BigQuery access limited to:

  * Dataset: `support_analytics`
  * Tables: allow-listed only
* SQL validation rules:

  * `SELECT` statements only
  * No DDL or DML operations
* No direct Firestore access from Insight Agent

---

## 10. Design Principles

* **Analytical isolation**
  Insight Agent reads analytics data only.

* **Explainable insights**
  SQL results are always summarized in plain language.

* **Scalable by default**
  BigQuery enables historical and large-scale analysis without refactoring.

---

## 11. Future Extensions (Optional)

* Looker dashboards on top of BigQuery
* Monthly / weekly automated insight summaries
* Predictive SLA breach analysis
* Executive insight reports powered by Gemini

---

## 12. Summary

The Insight Agent provides a **clean, enterprise-grade analytics layer** over support data by combining:

* BigQuery for scale and accuracy
* Gemini for reasoning and summarization
* Strict read-only governance for safety

> Firestore answers *what is happening now*.
> BigQuery explains *what happened and why*.
> The Insight Agent turns data into *decisions*.

---


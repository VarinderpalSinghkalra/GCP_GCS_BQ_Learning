

# Proposal: Introducing an Insight Agent for Data-Driven Support Intelligence

## Prepared by

Varinder Pal Singh

## Date

05th-Jan-2026

---

## 1. Executive Summary

Today, our support platform successfully handles **user queries** and **ticket creation** using AI agents.
However, the system remains **reactive** — it responds to issues but does not provide **strategic insights** into *why* issues occur, *where* spend or tickets concentrate, or *how* we can proactively improve operations.

This proposal recommends introducing a **dedicated Insight Agent**, powered by **BigQuery analytics and Gemini**, to transform existing operational data into **actionable insights for leadership and support teams**.

The Insight Agent will operate **independently** of ticket creation and user interaction, ensuring:

* Strong governance
* Clear separation of responsibilities
* Enterprise-ready scalability

---

## 2. Current State (As-Is)

We currently operate with the following AI agents:

###  Info Agent

* Handles how-to questions and documentation queries
* Reduces unnecessary ticket creation

### Ticketing Agent

* Creates and manages support tickets
* Stores operational data in Firestore

### Limitations of Current Setup

* No visibility into trends or patterns
* No SLA, compliance, or volume analysis
* No data-driven insights for decision-making
* Leadership questions require manual analysis

> Example unanswered questions today:
>
> * Why are tickets increasing in a specific area?
> * Which category or business unit drives most spend?
> * Are we breaching SLAs frequently?
> * Where can we optimize cost or compliance?

---

## 3. Proposed Solution (To-Be)

Introduce a **third, specialized AI agent**:

##  Insight Agent

A **read-only analytical agent** that:

* Analyzes historical data
* Generates insights from trends
* Supports leadership and operational decisions

---

## 4. What the Insight Agent Will Do

The Insight Agent will:

* Convert natural language questions into SQL queries
* Query **BigQuery** (analytics datastore)
* Summarize results using **Gemini**
* Provide clear, explainable insights

### Example Questions It Can Answer

* “How many high-priority tickets were created last month?”
* “Which categories contribute to most spend?”
* “What percentage of spend is non-compliant?”
* “Which areas are showing increasing issue trends?”
* “Are we improving or degrading against SLAs?”

---

## 5. What the Insight Agent Will NOT Do

For governance and safety, the Insight Agent will:

*  Not create or update tickets
*  Not write to Firestore or BigQuery
*  Not perform operational actions

It is **strictly read-only and analytical**.

---

## 6. High-Level Architecture (Proposed)

```
Operational Flow:
Info Agent / Ticketing Agent
 → Firestore (Operational Data)

Analytics Flow:
Firestore
 → BigQuery (Analytics Store)
 → Insight Agent (Gemini)
 → Leadership / Support Insights
```

### Key Design Principle

* **Firestore** → operational source of truth
* **BigQuery** → analytics and insights
* **Insight Agent** → reasoning and summarization

---

## 7. Why BigQuery + Gemini

### BigQuery

* Handles large historical datasets efficiently
* Enables fast aggregations and trend analysis
* Industry standard for analytics on GCP

### Gemini

* Converts natural language → SQL
* Explains data in business-friendly language
* Eliminates manual reporting effort

---

## 8. Business Value

###  Immediate Benefits

* Data-driven decision making
* Visibility into spend, compliance, and trends
* Reduced manual analysis and reporting

###  Strategic Benefits

* Proactive issue identification
* Better cost and SLA control
* Leadership-ready insights
* Foundation for dashboards and forecasting

---

## 9. Risk & Governance Considerations

| Area         | Mitigation                           |
| ------------ | ------------------------------------ |
| Data safety  | Read-only BigQuery access            |
| Cost control | Query limits & dataset allow-listing |
| Scope creep  | Dedicated Insight Agent only         |
| Compliance   | Clear separation of agent roles      |

---

## 10. Implementation Approach

### Phase 1 (Current)

* Info Agent
* Ticketing Agent
   Already implemented

### Phase 2 (Proposed)

* Create analytics table in BigQuery
* Enable Insight Agent (read-only)
* Add predefined insight queries

No changes required to existing agents.

---

## 11. Estimated Effort

* **Technical effort:** Low–Medium
* **Risk:** Low
* **Operational impact:** None on existing flows

This is an **incremental enhancement**, not a refactor.

---

## 12. Recommendation

> Adding an Insight Agent will move the platform from a **reactive support system** to a **proactive, intelligence-driven platform**, without impacting existing workflows.

**Recommendation:**
 Approve the introduction of the Insight Agent as a Phase-2 enhancement.

---

## 13. Conclusion

The proposed Insight Agent:

* Complements existing agents
* Unlocks value from existing data
* Improves visibility, governance, and decision-making
* Aligns with enterprise-grade architectural best practices

This is a **low-risk, high-impact** improvement.


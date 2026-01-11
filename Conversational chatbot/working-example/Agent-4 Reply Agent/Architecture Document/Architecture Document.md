Issue Management & Spend Analytics Platform

ADK-Enabled Multi-Agent Architecture on Google Cloud Platform


1. Purpose of This Document

This document defines the end-to-end technical architecture for a serverless, event-driven, multi-agent platform that provides:
	•	Automated Issue Management
	•	Conversational AI–based interaction
	•	Streaming analytics and SLA reporting
	•	Secure, controlled Spend Analytics
	•	Governed AI agent execution using ADK (Agent Development Kit)

The objective is to present a production-ready, auditable, and cost-controlled design aligned with modern enterprise cloud and AI governance standards.



2. Architectural Objectives

Objective	Description
Scalability	Automatic scaling without capacity planning
Cost Optimization	Usage-based pricing; no idle infrastructure
Agent Safety	Strict control over agent actions and data access
Auditability	Immutable event history for compliance
Low Latency	Real-time responses for user interactions
Separation of Concerns	Clear isolation of operational and analytical workloads
AI Governance	Deterministic, tool-restricted agent behavior


3. Architectural Overview

The platform is organized into two logically isolated domains, unified by shared infrastructure patterns and governed by ADK-managed agents.

3.1 Domains
	1.	Issue Management Domain
Manages issue creation, lifecycle automation, and real-time status queries.
	2.	Spend Analytics Domain
Provides read-only, aggregated cost insights via a controlled analytics agent.

Each domain follows an agent-first interaction model while maintaining strict boundaries between operational systems and analytical systems.


4. Core Architecture Principles

4.1 Event-Driven Architecture
	•	All state changes generate immutable events
	•	Events are append-only and never mutated
	•	Downstream systems consume events asynchronously
	•	Operational workflows are decoupled from analytics

4.2 Dual Data Model

Workload Type	Storage
Operational state	Firestore
Analytical history	BigQuery

This separation ensures:
	•	Low-latency transactional access
	•	Cost-efficient analytical processing
	•	No cross-contamination of workloads

4.3 Agent-First API Design (ADK)
	•	Agents interact only through approved tools
	•	No direct database access from agents
	•	All agent actions are:
	•	Explicit
	•	Inspectable
	•	Deterministic
	•	Tool contracts define exactly what an agent can and cannot do

4.4 Serverless-First Design

All components scale automatically and incur cost only when used:
	•	Cloud Functions (Gen2)
	•	Pub/Sub
	•	Dataflow
	•	BigQuery
	•	Cloud Tasks


5. ADK (Agent Development Kit) – Architectural Role

5.1 Why ADK Is Used

ADK is introduced to enforce enterprise-grade AI governance, ensuring:
	•	Controlled tool invocation
	•	Prevention of hallucinated logic or SQL
	•	Deterministic execution paths
	•	Safe conversational reasoning
	•	Clear separation between reasoning and execution

5.2 Scope of ADK Usage

Area	ADK Usage
Conversational intent interpretation	Yes
Tool selection and invocation	Yes
Spend analytics reasoning	Yes
Issue lifecycle automation	No
Streaming pipelines	No

Design Decision:
ADK is applied only where reasoning and decision-making are required.
All state transitions and pipelines remain deterministic and code-driven.


6. Issue Management Architecture

6.1 User Interaction Layer

Users interact through:
	•	Chat interfaces
	•	Web or mobile applications
	•	Conversational AI powered by Vertex AI

Supported intents include:
	•	Issue creation
	•	Issue status lookup
	•	Issue completion checks

Intent interpretation and tool selection are handled by the ADK-managed Issue Agent.


6.2 ADK-Managed Issue Agent

Responsibilities
	•	Interpret user intent
	•	Invoke approved APIs
	•	Enforce read/write boundaries
	•	Format structured responses

Allowed Tools
	•	submit_issue
	•	get_issue_status

Explicitly Disallowed
	•	Direct Firestore access
	•	Direct BigQuery access
	•	Any analytical queries
	•	Any form of SQL generation


6.3 API Layer (Cloud Functions – Gen2)

6.3.1 submit_issue
Responsibilities
	•	Validate request payload
	•	Create issue record in Firestore
	•	Compute SLA metadata
	•	Publish lifecycle event to Pub/Sub
	•	Schedule future transitions via Cloud Tasks
	•	Return acknowledgment to the agent


6.3.2 update_issue_status
Trigger
	•	Cloud Tasks (time-based execution)

Responsibilities
	•	Read current issue state
	•	Apply deterministic state transition
	•	Persist updated state in Firestore
	•	Publish lifecycle event

This function is not agent-controlled and contains no AI logic.


6.3.3 get_issue_status
Responsibilities
	•	Read current issue state
	•	Return structured, read-only response
	•	No side effects

This API is safe for both UI and agent consumption.


6.4 Firestore – Operational Data Store
	•	Collection: issues
	•	One document per issue
	•	Optimized for point reads
	•	No analytical queries permitted

Firestore is used exclusively for current state, not history.


6.5 Cloud Tasks – Lifecycle Automation
	•	Schedules delayed status transitions
	•	Ensures retry and idempotency
	•	Prevents long-running or blocking functions
	•	Eliminates polling-based designs


6.6 Pub/Sub – Event Backbone
	•	Decouples operational workflows from analytics
	•	Transports immutable lifecycle events

Event Characteristics
	•	Append-only
	•	Time-stamped
	•	Schema-controlled


6.7 Dataflow – Streaming Ingestion
	•	Uses managed Pub/Sub → BigQuery template
	•	No custom Beam code
	•	Schema enforcement at ingestion
	•	Near real-time event availability in BigQuery


6.8 BigQuery – Issue Analytics Layer

issues_status_history
	•	Immutable lifecycle event log
	•	Used for:
	•	SLA calculations
	•	Auditing
	•	Trend analysis

issues_current
	•	Derived table
	•	One row per issue
	•	Optimized for dashboards and agent-safe analytics


6.9 State Materialization

A scheduled BigQuery MERGE job:
	•	Derives latest issue state
	•	Eliminates repeated window queries
	•	Reduces query cost and latency


7. Spend Analytics Architecture

7.1 Spend Data Storage

Table	Description
spend_raw	Immutable billing and usage data
spend_aggregated_daily	Daily summarized costs
spend_current_month	Optimized monthly view



7.2 ADK-Managed Spend Analytics Agent

Responsibilities
	•	Answer cost and usage questions
	•	Explain trends in business language
	•	Provide consistent, governed responses

Strict Safety Rules
	•	Read-only access
	•	Predefined query paths only
	•	Aggregated datasets only
	•	No dynamic SQL
	•	No free-form data exploration

ADK enforces these constraints at runtime.



8. Multi-Agent Model

Agent	Data Access	Purpose
Issue Agent	Firestore, issue APIs	Real-time issue operations
Analytics Agent	BigQuery (derived tables)	SLA and trend insights
Spend Agent	BigQuery (aggregated spend)	Cost analysis

Each agent operates independently under ADK governance.



9. Cost Optimization Strategy

Key architectural decisions:
	•	Firestore for transactional reads
	•	BigQuery only for analytics
	•	Derived tables to avoid repeated scans
	•	Serverless services with scale-to-zero
	•	No LLM-generated SQL (enforced by ADK)

Result
	•	Predictable cloud costs
	•	No runaway analytical queries
	•	No idle infrastructure
	•	Controlled AI usage



10. Security and Access Model
	•	Public access only to agent-safe APIs
	•	No direct database access from UI or agents
	•	IAM-based service-to-service authentication
	•	Read-only BigQuery permissions for agents
	•	Separation of operational and analytical IAM roles






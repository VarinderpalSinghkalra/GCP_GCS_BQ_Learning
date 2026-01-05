Platform Support – Multi-Agent Automated Ticketing Architecture

1. Overview

This document describes the architecture and design of the Platform Support Multi-Agent System built on Google Cloud Platform (GCP) using Vertex AI Conversational Agents.

The system provides:
	•	Automated informational support using internal documentation
	•	Intelligent escalation to automated ticket creation
	•	Persistent issue tracking without manual intervention
	•	A fully agent-driven workflow with no human support dependency

The design intentionally avoids a human support loop and operates as a self-service, automated support platform.

⸻

2. Problem Statement

Employees raise two primary types of requests:
	•	Informational queries (how-to, workflows, usage guidance)
	•	Operational issues (login failures, access problems, system errors)

The system must:
	•	Resolve informational queries automatically
	•	Reliably capture unresolved issues as tickets
	•	Maintain traceability without requiring human handling
	•	Operate end-to-end without manual support intervention

⸻

3. High-Level Architecture

User
 │
 ▼
Vertex AI Conversational Agent
 │
 ├── Info Agent
 │     ├─ Uses documentation
 │     ├─ Answers how-to questions
 │     └─ Detects unresolved issues
 │
 ├── Playbook (Conditional Routing)
 │     └─ Transfers unresolved issues
 │
 └── Ticketing Agent
       ├─ Collects issue details
       ├─ Creates tickets automatically
       └─ Confirms ticket creation to user


⸻

4. Core Components

4.1 Conversational Agent (Vertex AI)

The Platform Support Agent is the orchestration layer responsible for:
	•	Managing conversation context
	•	Evaluating user intent
	•	Routing between specialized agents
	•	Invoking backend tools

⸻

4.2 Info Agent (Automated Knowledge Agent)

Purpose
Handles informational and guidance-based queries.

Capabilities
	•	Uses internal documentation via the Docs tool
	•	Provides step-by-step guidance
	•	Performs basic troubleshooting

Escalation Criteria
	•	Login failures
	•	Access issues
	•	Errors or incidents
	•	Any problem not resolvable via documentation

Constraints
	•	Does not create tickets
	•	Does not invoke backend APIs

⸻

4.3 Playbook & Conditional Routing

The Default Generative Playbook acts as the system control plane.

Responsibilities
	•	Evaluate conversational intent
	•	Execute conditional logic
	•	Transfer control between agents

Routing Rule

If the user reports an issue, error, incident, or access problem
→ Transfer to Ticketing Agent

Routing is implemented using Conditional Actions, ensuring deterministic agent transitions.

⸻

4.4 Ticketing Agent (Automated Action Agent)

Purpose
Handles issue escalation and automated ticket creation.

Responsibilities
	•	Validate required issue details
	•	Invoke the ticketing backend API
	•	Return a ticket reference ID to the user

Tools
	•	issue_management_api (OpenAPI-based tool)

The Ticketing Agent operates entirely without human involvement.

⸻

5. Backend Architecture

5.1 Ticketing API (Serverless)
	•	Platform: Cloud Functions (Gen-2)
	•	Runtime: Python 3.11
	•	Endpoint: submit_issue
	•	Characteristics:
	•	Stateless
	•	Idempotent
	•	Always returns structured JSON
	•	Designed for agent-safe execution

⸻

5.2 Firestore (System of Record)

Firestore (Native mode) is used as the persistent backend.

Collections
	•	issues
	•	users
	•	messages (optional future automation)

Stored Data
	•	Issue metadata
	•	Priority and SLA information
	•	Ticket lifecycle status

Firestore enables:
	•	Fully serverless operation
	•	Low-latency reads/writes
	•	Event-driven automation (future)

⸻

6. End-to-End Execution Flows

6.1 Informational Query Flow

User
 → Info Agent
 → Docs Tool
 → Automated Answer
 → Conversation Ends


⸻

6.2 Issue Escalation Flow

User
 → Info Agent (cannot resolve)
 → Playbook Conditional Action
 → Ticketing Agent
 → Ticketing API
 → Firestore
 → Ticket ID returned to user

All steps are executed automatically by agents.

⸻

7. Design Principles
	•	Zero human dependency
	•	Deterministic agent routing
	•	Fail-safe ticket creation
	•	Strict separation of responsibilities
	•	Fully automated support lifecycle

⸻

8. Future Enhancements (Automation Only)

Potential extensions without introducing human loops:
	•	Automated follow-up messages
	•	SLA breach notifications
	•	Status-check agent (get_issue_status)
	•	Analytics integration with BigQuery
	•	Auto-remediation playbooks

⸻

9. Summary

This architecture implements a fully automated, agent-driven support system that:
	•	Resolves informational queries autonomously
	•	Captures unresolved issues as tickets
	•	Operates end-to-end without human intervention
	•	Scales horizontally using serverless GCP services

The system is suitable for environments prioritizing self-service support, automation, and consistency.

⸻


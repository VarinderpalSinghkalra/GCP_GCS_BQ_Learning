
CIR Pre-Check Co-Pilot

RAG-Based Enterprise Architecture (GCP)

⸻

1. Overview

CIR Pre-Check Co-Pilot is a Retrieval-Augmented Generation (RAG) based AI system designed to provide context-aware contract validation and knowledge retrieval.

The platform uses:

* Google Cloud Storage (GCS) as the knowledge base
* Vertex AI (Embeddings + Gemini) for intelligence
* AlloyDB with pgvector for semantic search

This architecture enables scalable, accurate, and reusable knowledge-driven AI responses.

⸻

2. High-Level Architecture

Client → API Gateway → Cloud Run (Backend)
                      │
                      ▼
              ─────── RAG SYSTEM ───────
                      │
        ┌──────────────────────────────┐
        │     KNOWLEDGE INGESTION      │
        └──────────────────────────────┘
                      │
                      ▼
      GCS → Chunking → Embeddings → AlloyDB (pgvector)
                      │
                      ▼
        ┌──────────────────────────────┐
        │       QUERY PIPELINE         │
        └──────────────────────────────┘
                      │
                      ▼
   Query → Embedding → Vector Search → Gemini → Response

⸻

3. End-to-End Workflow

3.1 Knowledge Ingestion Flow

1. Documents are uploaded to Cloud Storage (GCS)
2. Documents are processed into smaller chunks
3. Each chunk is converted into vector embeddings using Vertex AI
4. Embeddings are stored in AlloyDB with pgvector
5. Metadata optionally stored in BigQuery

⸻

3.2 Query Processing Flow

1. User submits a query via UI/API
2. Backend converts query into embedding
3. Vector search is performed in AlloyDB
4. Top-K relevant chunks are retrieved
5. Context + prompt sent to Gemini (Vertex AI)
6. AI generates context-aware response
7. Business rules refine output
8. Response returned to user

⸻

4. Detailed Architecture (Pipe Diagram)

[ CLIENT (Web / App) ]
            │
            ▼
[ API GATEWAY ]
(Auth | Routing | Rate Limiting)
            │
            ▼
[ CLOUD RUN (BACKEND) ]
(Orchestration Layer)
            │
            ▼
================= INGESTION PIPELINE =================
[ CLOUD STORAGE (GCS) ]
(Knowledge Base)
            │
            ▼
[ TEXT CHUNKING SERVICE ]
(Semantic Splitting)
            │
            ▼
[ VERTEX AI EMBEDDINGS ]
(textembedding-005)
            │
            ▼
[ ALLOYDB + PGVECTOR ]
(Vector Storage)
================= QUERY PIPELINE =====================
[ USER QUERY ]
            │
            ▼
[ QUERY EMBEDDING ]
(Vertex AI)
            │
            ▼
[ VECTOR SEARCH ]
(AlloyDB - Top K Results)
            │
            ▼
[ VERTEX AI (GEMINI) ]
(Context + Prompt)
            │
            ▼
[ BUSINESS RULES ENGINE ]
(CIR Validation & Formatting)
            │
            ▼
[ FIRESTORE ] ---- [ BIGQUERY ]
(Results)           (Analytics)
            │
            ▼
[ RESPONSE TO CLIENT ]
(JSON Output)

⸻

5. Architecture Components

5.1 Presentation Layer

* Web UI / Internal tools
* Upload knowledge and query system

⸻

5.2 API Layer

* API Gateway
* Authentication, routing, throttling

⸻

5.3 Compute Layer

* Cloud Run (stateless backend)
* Handles orchestration and integrations

⸻

5.4 Knowledge Base

* Cloud Storage (GCS)
* Stores raw documents and structured knowledge

⸻

5.5 Embedding Layer

* Vertex AI Embeddings (textembedding-005)
* Converts text into vector representations

⸻

5.6 Vector Database

* AlloyDB with pgvector
* Stores embeddings
* Performs similarity search

⸻

5.7 AI Reasoning Layer

* Vertex AI (Gemini)
* Generates context-aware responses

⸻

5.8 Business Logic Layer

* CIR validation rules
* Risk scoring and formatting

⸻

5.9 Data Layer

* Firestore → operational data
* BigQuery → analytics and reporting

⸻

5.10 Observability

* Cloud Logging
* Cloud Monitoring

⸻

5.11 Security

* IAM roles and permissions
* Secret Manager for credentials
* Encryption (at rest and in transit)

⸻

6. Scalability & Performance

* Cloud Run auto-scales based on traffic
* Cloud Run Jobs enable parallel embedding processing
* AlloyDB optimized for vector similarity queries
* Stateless backend ensures horizontal scalability

⸻

7. Optional Enhancements

* Pub/Sub for event-driven ingestion
* Cloud Workflows for orchestration
* Hybrid search (vector + keyword)
* Metadata filtering (region, contract type)
* Looker dashboards for insights

⸻

8. Key Design Benefits

* True RAG architecture (context-aware AI)
* Scalable and serverless
* Modular and extensible
* Enterprise-grade security
* High performance and low latency

⸻

9. Conclusion

This architecture transforms CIR Pre-Check Co-Pilot into a knowledge-driven AI platform by combining:

* Vector search (AlloyDB + pgvector)
* Generative AI (Gemini)
* Serverless compute (Cloud Run)

It enables intelligent, scalable, and reusable contract validation and knowledge retrieval across the organization.

⸻

:::

⸻

This is:

* GitHub-ready
* Interview-ready
* Architect-level clean
* Matches your RAG idea perfectly


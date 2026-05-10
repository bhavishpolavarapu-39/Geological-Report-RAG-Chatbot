# 🏛️ GeoMind AI - System Architecture & Design

## Table of Contents
1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [RAG Pipeline Architecture](#rag-pipeline-architecture)
4. [Multi-Agent System](#multi-agent-system)
5. [Database Schema](#database-schema)
6. [API Design](#api-design)
7. [Scalability & Performance](#scalability--performance)
8. [Security Architecture](#security-architecture)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER LAYER                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Web Browser         │  Mobile App      │  API Clients  │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Nginx Proxy │
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐       ┌──────────┐
    │Frontend│        │Backend │       │  Worker  │
    │(Next.js)       │(FastAPI)       │ (Celery) │
    └────────┘        └────────┘       └──────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌─────────┐      ┌──────────┐     ┌───────────┐
    │PostgreSQL      │  Redis   │     │ Prometheus│
    │+ pgvector      │ (Cache)  │     │(Metrics)  │
    └─────────┘      └──────────┘     └───────────┘
```

### Component Responsibilities

| Component | Role | Tech Stack |
|-----------|------|-----------|
| **Frontend** | User interface, real-time chat, document viewing | Next.js, React, Framer Motion |
| **Backend API** | REST endpoints, authentication, orchestration | FastAPI, Pydantic, SQLAlchemy |
| **RAG Service** | Document retrieval, search, reranking | LangChain, LlamaIndex, pgvector |
| **Agent System** | Multi-agent orchestration, tool use | LangChain agents, custom implementations |
| **Document Processor** | PDF/image parsing, OCR, metadata extraction | PyPDF, Tesseract, spaCy |
| **Task Queue** | Async job processing | Celery + Redis |
| **Vector DB** | Semantic search storage | PostgreSQL + pgvector |
| **Cache Layer** | Query & results caching | Redis |

---

## Data Flow

### Document Upload Pipeline

```
1. File Upload (Frontend)
   └─▶ POST /api/v1/documents/upload
       ├─ File validation
       ├─ Store to disk
       └─ Queue background job

2. Document Processing (Worker)
   ├─ Extract text (PDF parser / OCR)
   ├─ Parse tables & images
   ├─ Extract metadata (minerals, locations, depth)
   ├─ Split into chunks (with overlap)
   └─ Generate embeddings

3. Vector Store
   ├─ Create pgvector embeddings
   ├─ Store in PostgreSQL
   ├─ Index for semantic search
   └─ Build keyword index

4. Database Update
   └─ Store document metadata in documents table
       ├─ filename, size, type, chunks_count
       ├─ metadata (minerals, locations)
       └─ created_at timestamp

5. Notification (Frontend)
   └─ WebSocket: "Document processed, 45 chunks indexed"
```

### Query Processing Pipeline

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────────────┐
│ 1. QUERY UNDERSTANDING                      │
├─────────────────────────────────────────────┤
│ - Syntax analysis                           │
│ - Query expansion (3 variants)              │
│ - Domain keyword extraction                 │
│ - Filter detection (minerals, depth, etc.)  │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 2. RETRIEVAL (Hybrid Search)                │
├─────────────────────────────────────────────┤
│ SEMANTIC BRANCH:                            │
│ ├─ Embed query (Sentence Transformers)     │
│ ├─ Vector similarity search (pgvector)     │
│ ├─ Top 10 results                          │
│ └─ Score: 0.0-1.0                          │
│                                             │
│ KEYWORD BRANCH:                             │
│ ├─ Extract keywords & terms                │
│ ├─ BM25-like scoring                       │
│ ├─ Apply metadata filters                  │
│ ├─ Top 10 results                          │
│ └─ Score: 0.0-1.0                          │
│                                             │
│ MERGING:                                    │
│ ├─ Combine results (weighted average)      │
│ │  final_score = 0.7*semantic + 0.3*kw    │
│ └─ Top 20 candidates                       │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 3. RERANKING (Cross-Encoder)                │
├─────────────────────────────────────────────┤
│ - Load cross-encoder model                  │
│ - Score (query, document_text) pairs        │
│ - Reorder by cross-encoder scores          │
│ - Top 5 final results                       │
│ - Add rerank_score to each result          │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 4. CONTEXT COMPRESSION                      │
├─────────────────────────────────────────────┤
│ - Combine top 5 results (max 2000 tokens)   │
│ - Summarize if exceeding token limit        │
│ - Preserve citation metadata                │
│ - Format for LLM context                    │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│ 5. GENERATION (LLM)                         │
├─────────────────────────────────────────────┤
│ Prompt:                                     │
│ {System Prompt}                             │
│ {Retrieved Context}                         │
│ {User Query}                                │
│                                             │
│ Output:                                     │
│ ├─ Answer text (streaming)                 │
│ ├─ Confidence score (0.0-1.0)              │
│ └─ Citation references                     │
└─────────────────────────────────────────────┘
    │
    ▼
RESPONSE TO USER
├─ Answer content
├─ Source documents with page numbers
├─ Confidence metrics
└─ Related follow-up questions
```

### Multi-Agent Query Flow

```
USER QUERY: "Analyze the Sumayau project's economic potential"
    │
    ▼
┌────────────────────────────────────────┐
│ QUERY CLASSIFICATION                   │
├────────────────────────────────────────┤
│ Primary Agent: economist                │
│ Secondary: geologist, risk analyst      │
└────────────────────────────────────────┘
    │
    ├─────────────┬──────────────┬──────────────┐
    ▼             ▼              ▼              ▼
┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────┐
│Economist │ │Geologist    │ │Risk      │ │Orchestr │
│Agent     │ │Agent        │ │Analyst   │ │Coordinator
└──┬───────┘ └──┬──────────┘ └──┬───────┘ └────┬────┘
   │            │               │              │
   ├─RAG Search ├─RAG Search    ├─RAG Search   │
   │ for costs  │ for grades    │ for risks    │
   │            │               │              │
   ├─Calculate  ├─Assess        ├─Rate         │
   │ NPV, IRR   │ deposit       │ severity     │
   │            │ potential     │              │
   │            │               │              │
   ▼            ▼               ▼              │
   │ Financial  │ Geological    │ Risk         │
   │ Analysis   │ Assessment    │ Matrix       │
   │            │               │              │
   └─────────┬──────────┬───────┘              │
             │          │                     │
             └──────┬───┘                     │
                    ▼                         │
            ┌──────────────────┐             │
            │ CONSENSUS ENGINE │◀────────────┘
            └──────────────────┘
                    │
                    ▼
            INTEGRATED ANALYSIS
            - Cross-referenced findings
            - Consensus confidence
            - Conflicting viewpoints
            - Recommendations
```

---

## RAG Pipeline Architecture

### Vector Store Design

```sql
-- Document chunks table
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id UUID UNIQUE,
    document_id VARCHAR(255),
    content TEXT,
    embedding vector(384),  -- pgvector
    metadata JSONB,
    created_at TIMESTAMP,
    INDEX idx_document_id,
    INDEX idx_embedding USING ivfflat (embedding vector_cosine_ops)
);

-- Keyword index
CREATE TABLE keyword_index (
    id SERIAL PRIMARY KEY,
    chunk_id UUID,
    keyword VARCHAR(255),
    frequency INT,
    INDEX idx_keyword (keyword),
    FOREIGN KEY (chunk_id) REFERENCES document_chunks
);

-- Search cache
CREATE TABLE search_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    query TEXT,
    results JSONB,
    ttl TIMESTAMP,
    hits INT DEFAULT 0
);
```

### Embedding Model Selection

**Primary: Sentence Transformers (all-MiniLM-L6-v2)**
- Dimension: 384
- Inference time: <10ms
- Geological domain performance: Good
- Size: 22MB
- Supports: Semantic search, clustering

**Alternatives:**
- `bge-large-en-v1.5` (1024-dim, better quality)
- `nomic-embed-text-v1` (768-dim, open)
- Domain-specific fine-tuned models

### Reranking Strategy

```python
# Pipeline stages
1. Semantic Search (pgvector)
   └─ ~200 candidates (low recall threshold)

2. Keyword Search (BM25)
   └─ ~200 candidates

3. Hybrid Merge
   ├─ Combine results: final_score = 0.7*semantic + 0.3*keyword
   └─ Top 50 candidates

4. Cross-Encoder Reranking
   ├─ Load ms-marco-MiniLM cross-encoder
   ├─ Score all 50 candidates
   ├─ Rerank by cross-encoder score
   └─ Return top 5-10

5. Context Compression
   ├─ Concatenate top 5
   ├─ Summarize if >2000 tokens
   └─ Format for LLM
```

---

## Multi-Agent System

### Agent Architecture

```python
class BaseAgent:
    - Memory (conversation history + context)
    - Tools (RAG, calculations, simulations)
    - Planning capability
    - Reflection & self-critique
    - Output formatting

class GeologistAgent(BaseAgent):
    - Geological expertise
    - Deposit evaluation
    - Mineral system understanding
    - Recommendation generation

class EconomicsAgent(BaseAgent):
    - NPV/IRR calculations
    - Cost estimation
    - Sensitivity analysis
    - Market context

class RiskAnalysisAgent(BaseAgent):
    - Technical risk assessment
    - Probability estimation
    - Mitigation strategies
    - Residual risk calculation

class ESGAgent(BaseAgent):
    - Environmental assessment
    - Social impact analysis
    - Governance compliance
    - Sustainability metrics
```

### Agent Planning & Execution

```
AGENT REQUEST
    │
    ▼
CREATE PLAN
├─ Break down into steps
├─ Identify required tools
├─ Estimate duration
└─ Define success criteria
    │
    ▼
EXECUTE STEPS (Parallel where possible)
├─ Step 1: RAG search
│  └─ Retrieve relevant documents
├─ Step 2: Analysis
│  └─ Process information
└─ Step 3: Reasoning
   └─ Draw conclusions
    │
    ▼
REFLECTION & CRITIQUE
├─ Validate findings
├─ Check for consistency
├─ Identify gaps
└─ Plan follow-up questions
    │
    ▼
FORMATTED RESPONSE
├─ Main findings
├─ Supporting evidence
├─ Confidence metrics
├─ Source citations
└─ Next steps / recommendations
```

---

## Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    role ENUM('admin', 'analyst', 'viewer'),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users,
    filename VARCHAR(255),
    file_size INTEGER,
    document_type VARCHAR(50),
    chunks_count INTEGER,
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users,
    title VARCHAR(500),
    messages JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_access TIMESTAMP
);

-- RAG Results Cache
CREATE TABLE rag_cache (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(255) UNIQUE,
    query TEXT,
    results JSONB,
    ttl TIMESTAMP,
    hits INTEGER DEFAULT 0
);

-- Audit Log
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    action VARCHAR(255),
    resource VARCHAR(255),
    details JSONB,
    created_at TIMESTAMP
);
```

---

## API Design

### RESTful Endpoints

```
Authentication:
  POST   /api/v1/auth/register
  POST   /api/v1/auth/login
  POST   /api/v1/auth/refresh
  POST   /api/v1/auth/logout

Documents:
  POST   /api/v1/documents/upload
  GET    /api/v1/documents
  GET    /api/v1/documents/{id}
  DELETE /api/v1/documents/{id}
  GET    /api/v1/documents/{id}/chunks

RAG:
  POST   /api/v1/rag/retrieve
  POST   /api/v1/rag/search-stream
  GET    /api/v1/rag/cache-stats

Agents:
  POST   /api/v1/agents/process
  POST   /api/v1/agents/research
  GET    /api/v1/agents/history

Chat:
  POST   /api/v1/conversations
  POST   /api/v1/conversations/{id}/messages
  GET    /api/v1/conversations/{id}
  DELETE /api/v1/conversations/{id}
  WS     /ws/chat/{conversation_id}

Admin:
  GET    /api/v1/admin/stats
  GET    /api/v1/admin/users
  GET    /api/v1/admin/health
  POST   /api/v1/admin/cache-clear
```

---

## Scalability & Performance

### Horizontal Scaling Strategy

```
Load Balancer (Nginx)
    │
    ├─▶ Backend Instance 1 (FastAPI)
    ├─▶ Backend Instance 2 (FastAPI)
    ├─▶ Backend Instance 3 (FastAPI)
    └─▶ Backend Instance N
         │
         └─▶ Shared PostgreSQL (Read Replicas)
         └─▶ Redis Cluster
         └─▶ Celery Workers (Distributed)
```

### Performance Optimization

| Metric | Target | Strategy |
|--------|--------|----------|
| **API Response Time** | <500ms | Caching, async, batching |
| **RAG Retrieval** | <2s | Hybrid search, reranking |
| **Document Upload** | <5min for 50MB | Async processing, chunking |
| **Concurrent Users** | 1000+ | Load balancing, connection pooling |
| **Database Throughput** | 10k QPS | Indexing, partitioning, read replicas |

### Caching Strategy

```python
# Query Response Cache (Redis)
- TTL: 1 hour
- Key: hash(query + filters)
- Size: Configurable LRU

# Document Chunk Cache
- TTL: 24 hours
- Key: chunk_id
- Size: Configurable

# Embedding Cache
- TTL: 7 days
- Avoid re-embedding same text
- Size: Configurable

# Search Results Cache
- TTL: 1 hour
- Key: hash(query + parameters)
- Invalidate on document update
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────┐
│ User Authentication                 │
├─────────────────────────────────────┤
│ 1. Email/Password Login             │
│ 2. Password hashing (bcrypt)        │
│ 3. JWT token generation             │
│ 4. Token refresh mechanism          │
│ 5. Token expiration (24h)           │
│ 6. Secure cookie storage            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Authorization (RBAC)                │
├─────────────────────────────────────┤
│ Admin: Full access                  │
│ Analyst: Create/view projects       │
│ Viewer: Read-only access            │
│ Guest: Limited preview              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Data Protection                     │
├─────────────────────────────────────┤
│ - Encryption at rest (DB)           │
│ - TLS in transit                    │
│ - SQL injection prevention          │
│ - XSS protection                    │
│ - CSRF tokens                       │
│ - Rate limiting                     │
│ - Input validation (Pydantic)       │
└─────────────────────────────────────┘
```

### Compliance & Audit

- JWT token validation on every request
- Audit logging for all actions
- Data access logging
- GDPR compliance (right to deletion)
- Export control compliance
- Rate limiting per user/IP

---

## Deployment Architecture

### Development
```
Local Docker Compose
└─ Single machine
   ├─ PostgreSQL
   ├─ Redis
   ├─ Backend
   ├─ Frontend
   └─ Nginx
```

### Staging
```
AWS ECS
├─ Backend (3x t3.medium)
├─ Frontend (2x t3.small)
├─ PostgreSQL RDS
├─ Redis Elasticache
├─ S3 (uploads)
└─ CloudFront (CDN)
```

### Production
```
AWS EKS (Kubernetes)
├─ Backend Deployment (5-10 replicas)
├─ Frontend Deployment (3-5 replicas)
├─ Worker Deployment (auto-scaling)
├─ PostgreSQL RDS (multi-AZ)
├─ Redis Elasticache (cluster mode)
├─ S3 (uploads + backup)
├─ CloudFront (CDN)
├─ Application Load Balancer
└─ Route 53 (DNS)
```

---

## Monitoring & Observability

```
Application Metrics (Prometheus)
├─ Request latency
├─ Error rates
├─ Cache hit rates
├─ Queue depth
└─ Agent processing time

Infrastructure Metrics
├─ CPU / Memory / Disk
├─ Network I/O
├─ Database connections
└─ Redis memory

Dashboards (Grafana)
├─ System health
├─ API performance
├─ User activity
├─ RAG effectiveness
└─ Agent performance

Alerts
├─ High error rates (>5%)
├─ Slow responses (>2s)
├─ Queue backlog
├─ Database issues
└─ Memory pressure
```

---

This architecture is designed to be **scalable**, **reliable**, **secure**, and **performant** for enterprise geological exploration use cases.

# ⚡ GeoMind AI - Quick Integration Guide

## 5-Minute System Setup

### Step 1: Start Docker Services
```bash
docker-compose up -d

# Verify all services started
docker-compose ps

# Expected output:
# SERVICE              STATUS              PORTS
# geomind_postgres    Up (healthy)        5432
# geomind_redis       Up (healthy)        6379
# geomind_backend     Up (healthy)        8000
# geomind_frontend    Up (healthy)        3000
# geomind_nginx       Up                  80, 443
```

### Step 2: Initialize Database
```bash
docker-compose exec backend python -m alembic upgrade head

# This creates tables:
# - users
# - documents
# - conversations
# - document_chunks (pgvector)
# - keyword_index
# - rag_cache
# - audit_log
```

### Step 3: Access Services
```
Frontend:    http://localhost:3000
Backend API: http://localhost:8000
API Docs:    http://localhost:8000/docs
Grafana:     http://localhost:3001 (admin/admin)
PgAdmin:     http://localhost:5050 (admin@geomind.local/admin)
```

---

## Integration Checklist

### ✅ RAG Pipeline Integration

```python
from rag_pipeline_core import RAGOrchestrator, PostgresVectorDB
from rag_pipeline_core import QueryExpander, RerankerEngine, ContextCompressor

# 1. Initialize
vector_db = PostgresVectorDB(
    connection_string="postgresql+asyncpg://user:password@localhost/geomind"
)
await vector_db.init_pool()

# 2. Create orchestrator
rag = RAGOrchestrator(
    vector_db=vector_db,
    llm_client=your_llm_client,
    redis_client=your_redis_client,
)

# 3. Ingest documents
chunk_ids = await rag.ingest_document(
    document_id="doc_001",
    document_name="Sumayau_Drill_Log.pdf",
    content=document_text,
    document_type="drill_log",
    metadata={"minerals": ["copper", "nickel"]}
)

# 4. Retrieve documents
results = await rag.retrieve(
    query="What are copper grades?",
    top_k=5,
    hybrid=True,
    rerank=True
)

# 5. Generate answer
answer, sources = await rag.generate_answer(
    query="What are copper grades?",
    context_results=results
)
```

### ✅ Document Processing Integration

```python
from document_ingestion import DocumentProcessor, BatchDocumentProcessor

# 1. Single document
processor = DocumentProcessor()

result = await processor.process_document(
    file_path="/path/to/drill_log.pdf",
    document_id="doc_001",
    document_name="Sumayau_Drill_Log.pdf",
    use_ocr=False  # Set True for scanned PDFs
)

# Access results
print(f"Minerals: {result['metadata']['minerals']}")
print(f"Coordinates: {result['metadata']['location']}")
print(f"Text: {result['full_text']}")

# 2. Batch processing
batch = BatchDocumentProcessor(max_concurrent=5)

documents = [
    ("/path/file1.pdf", "doc_001", "Drill Log 1"),
    ("/path/file2.pdf", "doc_002", "Drill Log 2"),
]

results = await batch.process_batch(documents)

for result in results:
    print(f"Processed: {result['document_name']}")
    print(f"Chunks: {len(result['parsed_content']['text_by_page'])}")
```

### ✅ Multi-Agent Integration

```python
from multi_agent_orchestration import (
    MultiAgentOrchestrator,
    GeologistAgent,
    EconomicsAgent,
    RiskAssessmentAgent
)

# 1. Initialize orchestrator
orchestrator = MultiAgentOrchestrator(llm_client, rag_engine)

# 2. Simple query (single agent)
result = await orchestrator.process_query(
    query="What are the nickel grades at Sumayau?",
    multi_agent=False
)

print(result['responses'][0]['content'])

# 3. Complex query (multiple agents)
result = await orchestrator.process_query(
    query="Analyze the Sumayau project's economic potential",
    multi_agent=True
)

# Results from geologist, economist, risk analyst
for response in result['responses']:
    print(f"\n{response['agent_name']} ({response['agent_role']}):")
    print(f"Confidence: {response['confidence']}")
    print(f"Response: {response['content'][:200]}...")

# 4. Autonomous research
research = await orchestrator.autonomous_research(
    topic="Sumayau nickel-copper deposit potential",
    max_iterations=5
)

for log in research['research_log']:
    print(f"Iteration {log['iteration']}: {log['question']}")
```

### ✅ FastAPI Backend Integration

```python
# In main.py

from fastapi import FastAPI
from rag_pipeline_core import RAGOrchestrator, PostgresVectorDB
from multi_agent_orchestration import MultiAgentOrchestrator
from document_ingestion import DocumentProcessor

app = FastAPI()

# Global instances
vector_db = None
rag_orchestrator = None
agent_orchestrator = None
doc_processor = None

@app.on_event("startup")
async def startup():
    global vector_db, rag_orchestrator, agent_orchestrator, doc_processor
    
    # Initialize services
    vector_db = PostgresVectorDB(os.getenv("DATABASE_URL"))
    await vector_db.init_pool()
    
    rag_orchestrator = RAGOrchestrator(vector_db, llm_client)
    agent_orchestrator = MultiAgentOrchestrator(llm_client, rag_orchestrator)
    doc_processor = DocumentProcessor()

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile, current_user: dict = Depends(get_current_user)):
    # Process document
    result = await doc_processor.process_document(...)
    
    # Ingest to RAG
    chunk_ids = await rag_orchestrator.ingest_document(...)
    
    return DocumentUploadResponse(...)

@app.post("/api/v1/rag/retrieve")
async def rag_retrieve(request: RetrievalRequest, current_user: dict = Depends(get_current_user)):
    results = await rag_orchestrator.retrieve(
        query=request.query,
        top_k=request.top_k,
        hybrid=request.hybrid,
    )
    return RAGResponse(...)

@app.post("/api/v1/agents/process")
async def process_agents(request: AgentRequest, current_user: dict = Depends(get_current_user)):
    result = await agent_orchestrator.process_query(
        query=request.query,
        multi_agent=request.multi_agent,
    )
    return result
```

---

## LLM Client Integration

### OpenAI
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Anthropic (Claude)
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-sonnet",
    temperature=0.1,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Google Gemini
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.1,
    api_key=os.getenv("GEMINI_API_KEY")
)
```

---

## Database Connection Examples

### PostgreSQL Connection Pool
```python
import asyncpg

pool = await asyncpg.create_pool(
    "postgresql://user:password@localhost/geomind",
    min_size=5,
    max_size=20
)

# Use in queries
async with pool.acquire() as conn:
    await conn.execute("SELECT * FROM documents")
```

### Redis Connection
```python
import aioredis

redis = await aioredis.create_redis_pool('redis://localhost')

# Cache operations
await redis.set('key', 'value', expire=3600)
value = await redis.get('key')
```

---

## Environment Variables Required

```bash
# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/geomind
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Application
LOG_LEVEL=info
ENV=development
```

---

## Common Integration Tasks

### Add Custom RAG Search Filter
```python
# Extend MetadataFilter class
class CustomFilter(MetadataFilter):
    @staticmethod
    def apply_custom_filter(results, custom_param):
        # Your filtering logic
        return filtered_results

# Use in RAG
results = await rag.retrieve(
    query="...",
    filters={"custom_param": value}
)
```

### Add Custom Agent
```python
# Extend BaseAgent
class CustomAgent(BaseAgent):
    def __init__(self, llm_client, rag_engine):
        super().__init__(
            name="Custom Agent",
            role=AgentRole.GEOLOGIST,  # Or custom role
            llm_client=llm_client,
            rag_engine=rag_engine,
        )
    
    async def process(self, query: str, context: Optional[str] = None) -> AgentResponse:
        # Your agent logic
        return AgentResponse(...)

# Register with orchestrator
orchestrator.agents["custom"] = CustomAgent(llm, rag)
```

### Add Document Type
```python
# In GeologicalMetadataExtractor
self.document_types = {
    "drill_log", "survey", "map", "assay",
    "your_custom_type"  # Add here
}

# Document type inference in DocumentProcessor
def _infer_document_type(self, text: str, file_ext: str) -> str:
    if "your_custom_keyword" in text.lower():
        return "your_custom_type"
    # ... existing logic
```

---

## Performance Tuning

### RAG Retrieval Optimization
```python
# Faster but less accurate
await rag.retrieve(query, top_k=3, semantic_weight=0.9, rerank=False)

# Slower but more accurate
await rag.retrieve(query, top_k=10, semantic_weight=0.5, rerank=True)

# Balanced
await rag.retrieve(query, top_k=5, semantic_weight=0.7, rerank=True)
```

### Document Processing Speed
```python
# Parallel processing (faster)
batch = BatchDocumentProcessor(max_concurrent=10)
results = await batch.process_batch(documents)

# Sequential (more reliable)
batch = BatchDocumentProcessor(max_concurrent=1)
results = await batch.process_batch(documents)
```

### Query Caching
```python
# Results cached for 1 hour in Redis
result = await rag.retrieve(query)

# Same query within 1 hour uses cache
result = await rag.retrieve(query)  # ~100ms from cache vs ~2s from scratch
```

---

## Troubleshooting

### RAG Not Finding Documents
```python
# Check database connection
async with vector_db.pool.connection() as conn:
    count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
    print(f"Total chunks: {count}")

# Check vector index
await conn.execute("REINDEX INDEX idx_embedding")
```

### Agent Responses Low Quality
```python
# Check LLM configuration
llm = ChatOpenAI(
    model="gpt-4",  # Use better model
    temperature=0.0,  # Lower for consistency
    max_tokens=2000
)

# Check RAG results
results = await rag.retrieve(query, top_k=10)
for r in results:
    print(f"Score: {r.relevance_score} | {r.content[:100]}")
```

### Memory Issues
```python
# Reduce embedding batch size
# Reduce document chunk size (smaller = more chunks)
# Use cheaper embedding model
# Enable Redis caching

# Monitor memory
docker stats geomind_backend
```

---

## Production Checklist

- [ ] Set production JWT secret
- [ ] Configure TLS/HTTPS
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Enable CORS for specific domains
- [ ] Configure auto-scaling
- [ ] Run security audit
- [ ] Load test with production data
- [ ] Set up alerting
- [ ] Document custom extensions
- [ ] Train team on system usage

---

## Next Steps

1. **Customize**: Adapt code for your geological domain
2. **Test**: Run comprehensive tests on your data
3. **Deploy**: Follow deployment guide for your infrastructure
4. **Monitor**: Set up dashboards and alerts
5. **Scale**: Configure auto-scaling for production loads

For detailed information, see:
- `README.md` - Overview & quick start
- `ARCHITECTURE.md` - System design
- Code docstrings - Implementation details

Happy integrating! 🚀

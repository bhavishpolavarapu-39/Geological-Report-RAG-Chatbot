# 🧬 GeoMind AI - Geological Intelligence Platform

Advanced AI-powered geological exploration assistant with RAG, multi-agent orchestration, and premium UI.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![React](https://img.shields.io/badge/react-18%2B-61dafb)

## 🚀 Features

### Core Technology
- **Advanced RAG Pipeline**: Hybrid search (semantic + keyword), reranking, query expansion
- **Multi-Agent AI System**: Specialized agents for geology, economics, ESG, risk assessment
- **Document Ingestion**: PDF parsing, OCR, metadata extraction, table detection
- **Vector Database**: PostgreSQL + pgvector for scalable semantic search
- **Real-time Streaming**: WebSocket chat with streaming responses
- **Citation System**: Every answer sourced with document references

### User Experience
- **Perplexity/Palantir Aesthetic**: Futuristic, cinematic UI with glassmorphism
- **Document Viewer**: Side-by-side document reading with AI highlights
- **Chat Interface**: Floating panel with full conversation context
- **Multi-Agent Responses**: Parallel agent processing with consensus
- **Autonomous Research**: Self-directed information gathering mode

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GeoMind AI Platform                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   Frontend       │         │   Nginx Proxy    │          │
│  │  (Next.js 15)    │────────▶│  (Load Balance)  │          │
│  │  + React 18      │         │                  │          │
│  │  + Framer Motion │         └──────────────────┘          │
│  └──────────────────┘                  │                     │
│                                        ▼                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          FastAPI Backend (Port 8000)                 │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ - Auth (JWT)                                         │  │
│  │ - Document Upload & Processing                       │  │
│  │ - RAG Orchestration                                  │  │
│  │ - Multi-Agent Processing                            │  │
│  │ - WebSocket Chat                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│       │                    │                    │            │
│       ▼                    ▼                    ▼            │
│   ┌────────┐        ┌──────────┐      ┌──────────────┐     │
│   │  RAG   │        │Celery    │      │Multi-Agent   │     │
│   │Pipeline│        │Worker    │      │Orchestrator  │     │
│   └────────┘        └──────────┘      └──────────────┘     │
│       │
│       ├─ Query Expansion
│       ├─ Hybrid Search
│       ├─ Reranking
│       └─ Context Compression
│
│  ┌────────────────────┐  ┌─────────────┐  ┌──────────┐     │
│  │  PostgreSQL 16     │  │    Redis    │  │Prometheus│     │
│  │  + pgvector        │  │  (Cache)    │  │(Metrics) │     │
│  │  (Vector DB)       │  │             │  │          │     │
│  └────────────────────┘  └─────────────┘  └──────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend**
- Next.js 15 + TypeScript
- React 18 with Hooks
- Tailwind CSS + custom CSS
- Framer Motion (animations)
- shadcn/ui + Recharts
- React Query (state management)
- Zustand (global state)

**Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- Pydantic validation
- Async/await patterns

**AI Stack**
- LangChain + LlamaIndex
- Sentence Transformers (embeddings)
- Cross-Encoder (reranking)
- Claude API + OpenAI + Gemini
- LLM-as-judge for quality

**Infrastructure**
- Docker & Docker Compose
- Kubernetes (optional)
- PostgreSQL 16 + pgvector
- Redis (caching)
- Celery (async tasks)
- Prometheus + Grafana

## 🏗️ Project Structure

```
geomind-ai/
├── frontend/                    # Next.js application
│   ├── components/
│   │   ├── Chat.tsx
│   │   ├── DocumentViewer.tsx
│   │   ├── NavBar.tsx
│   │   └── Dashboard.tsx
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── chat.tsx
│   │   ├── documents.tsx
│   │   └── reports.tsx
│   ├── styles/
│   │   └── globals.css
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useRAG.ts
│   │   └── useWebSocket.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── main.py                  # Entry point
│   ├── models/
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── auth.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── rag.py
│   │   ├── agents.py
│   │   └── chat.py
│   ├── services/
│   │   ├── rag_pipeline.py
│   │   ├── document_processor.py
│   │   ├── agent_orchestrator.py
│   │   └── llm_client.py
│   ├── workers/
│   │   └── celery_tasks.py
│   ├── middleware/
│   │   ├── auth.py
│   │   └── logging.py
│   ├── config.py
│   ├── dependencies.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml           # Local development
├── docker-compose.prod.yml      # Production
├── terraform/                   # AWS infrastructure
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── security.tf
│   └── monitoring.tf
├── kubernetes/                  # K8s deployment
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── postgres-statefulset.yaml
│   ├── redis-deployment.yaml
│   ├── ingress.yaml
│   └── persistent-volumes.yaml
├── nginx/                       # Reverse proxy config
│   ├── nginx.conf
│   └── ssl/
├── docs/                        # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Local Development

1. **Clone repository**
```bash
git clone https://github.com/yourorg/geomind-ai.git
cd geomind-ai
```

2. **Set environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

3. **Start services with Docker Compose**
```bash
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

4. **Initialize database**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PgAdmin: http://localhost:5050
- Grafana: http://localhost:3001

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password",
    "organization": "My Company"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

### Document Upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@drill_log.pdf"
```

### RAG Query
```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the copper grades at Sumayau?",
    "top_k": 5,
    "hybrid": true
  }'
```

### Multi-Agent Processing
```bash
curl -X POST http://localhost:8000/api/v1/agents/process \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the exploration potential of the Sumayau project",
    "multi_agent": true,
    "enable_planning": true
  }'
```

Full API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

## 🚢 Deployment

### Docker Compose (Development/Testing)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f kubernetes/
kubectl port-forward svc/frontend 3000:80
kubectl port-forward svc/backend 8000:8000
```

### AWS (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Environment Configuration

**Production (.env)**
```
DATABASE_URL=postgresql+asyncpg://...@prod-db/geomind
REDIS_URL=redis://prod-redis:6379
JWT_SECRET_KEY=your-production-secret
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LOG_LEVEL=info
```

## 📊 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Application Logs**: `docker-compose logs backend`
- **Database**: PgAdmin at http://localhost:5050

## 🔒 Security

- JWT authentication with expiration
- CORS middleware (configurable)
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- HTTPS/TLS support
- RBAC for document access

## 📈 Performance

- RAG caching with Redis (1-hour TTL)
- Async database operations
- Connection pooling (PostgreSQL, Redis)
- Document chunking optimization
- Batch processing for heavy computations
- WebSocket for real-time streaming

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=services

# Frontend tests
cd frontend
npm test -- --coverage
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Email**: support@geomind.ai

## 🗺️ Roadmap

- [ ] Multi-language support (Spanish, Mandarin, Portuguese)
- [ ] Advanced knowledge graphs with Neo4j
- [ ] Voice input/output with Whisper
- [ ] Custom LLM fine-tuning
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Integration with commercial geological software

## 📝 Citation

If you use GeoMind AI in your research, please cite:

```bibtex
@software{geomind_ai_2024,
  title = {GeoMind AI: Geological Intelligence Platform},
  author = {Your Company},
  year = {2024},
  url = {https://github.com/yourorg/geomind-ai}
}
```

---

**Built with ❤️ by Exploration AI Team**

For questions or commercial licensing, contact: hello@geomind.ai

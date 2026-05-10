"""
GeoMind AI - Advanced RAG Pipeline
Production-grade implementation with hybrid search, reranking, and query expansion.

Architecture:
- Hybrid search (keyword + semantic)
- Query expansion & refinement
- Metadata filtering
- Context compression
- Reranking with cross-encoders
- Source attribution
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import json
import logging

import numpy as np
from abc import ABC, abstractmethod

# Dependencies (install via: pip install langchain llama-index sentence-transformers faiss-cpu redis pgvector psycopg[binary])
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from redis import asyncio as aioredis
import psycopg
from psycopg.types.json import Json

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class ChunkType(Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    COORDINATE = "coordinate"
    ASSAY = "assay"


@dataclass
class GeoMetadata:
    """Geological metadata extracted from documents."""
    document_id: str
    document_name: str
    document_type: str  # "drill_log", "survey", "map", "report", "assay"
    source_page: int
    chunk_index: int
    location: Optional[Dict[str, float]] = None  # {"lat": ..., "lon": ...}
    mineral_types: List[str] = field(default_factory=list)
    depth_range: Optional[Tuple[float, float]] = None  # (min_m, max_m)
    date_range: Optional[Tuple[str, str]] = None
    confidence_score: float = 1.0
    extraction_method: str = "text_extraction"
    
    def to_dict(self) -> Dict:
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_type": self.document_type,
            "source_page": self.source_page,
            "chunk_index": self.chunk_index,
            "location": self.location,
            "mineral_types": self.mineral_types,
            "depth_range": self.depth_range,
            "date_range": self.date_range,
            "confidence_score": self.confidence_score,
            "extraction_method": self.extraction_method,
        }


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata."""
    content: str
    metadata: GeoMetadata
    chunk_type: ChunkType = ChunkType.TEXT
    embedding: Optional[np.ndarray] = None
    chunk_hash: Optional[str] = None
    
    def to_document(self) -> Document:
        """Convert to LangChain Document."""
        return Document(
            page_content=self.content,
            metadata=self.metadata.to_dict()
        )


@dataclass
class RetrievalResult:
    """Result from RAG retrieval with citations."""
    content: str
    source_document: str
    source_page: int
    document_type: str
    relevance_score: float
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None
    rerank_score: Optional[float] = None
    location: Optional[Dict[str, float]] = None
    excerpt_start: int = 0
    excerpt_end: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "source_document": self.source_document,
            "source_page": self.source_page,
            "document_type": self.document_type,
            "relevance_score": self.relevance_score,
            "semantic_score": self.semantic_score,
            "keyword_score": self.keyword_score,
            "rerank_score": self.rerank_score,
            "location": self.location,
        }


# ============================================================================
# VECTOR DATABASE INTERFACE
# ============================================================================

class VectorDatabaseInterface(ABC):
    """Abstract interface for vector database operations."""
    
    @abstractmethod
    async def add_chunks(self, chunks: List[DocumentChunk]) -> List[str]:
        """Add document chunks and return their IDs."""
        pass
    
    @abstractmethod
    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Semantic search using embeddings."""
        pass
    
    @abstractmethod
    async def keyword_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Keyword-based search."""
        pass
    
    @abstractmethod
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Hybrid search combining semantic and keyword."""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        pass


class PostgresVectorDB(VectorDatabaseInterface):
    """PostgreSQL with pgvector extension for vector storage."""
    
    def __init__(self, connection_string: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.connection_string = connection_string
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.pool = None
        
    async def init_pool(self):
        """Initialize connection pool."""
        self.pool = await psycopg.AsyncConnectionPool.create(
            self.connection_string,
            min_size=5,
            max_size=20,
        )
        await self._init_schema()
    
    async def _init_schema(self):
        """Initialize database schema."""
        async with self.pool.connection() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_id UUID UNIQUE NOT NULL,
                    document_id VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384),
                    metadata JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_document_id (document_id),
                    INDEX idx_metadata (metadata)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS keyword_index (
                    id SERIAL PRIMARY KEY,
                    chunk_id UUID NOT NULL,
                    keyword VARCHAR(255) NOT NULL,
                    frequency INT DEFAULT 1,
                    FOREIGN KEY (chunk_id) REFERENCES document_chunks(chunk_id),
                    INDEX idx_keyword (keyword),
                    INDEX idx_chunk_id (chunk_id)
                )
            """)
            await conn.commit()
    
    async def add_chunks(self, chunks: List[DocumentChunk]) -> List[str]:
        """Add chunks with embeddings to PostgreSQL."""
        chunk_ids = []
        async with self.pool.connection() as conn:
            for chunk in chunks:
                # Generate embedding
                embedding = self.embeddings.embed_query(chunk.content)
                chunk_id = f"{chunk.metadata.document_id}_{chunk.metadata.chunk_index}"
                
                # Insert chunk
                await conn.execute(
                    """
                    INSERT INTO document_chunks (chunk_id, document_id, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        updated_at = NOW()
                    """,
                    (
                        chunk_id,
                        chunk.metadata.document_id,
                        chunk.content,
                        embedding,
                        Json(chunk.metadata.to_dict())
                    )
                )
                chunk_ids.append(chunk_id)
                
                # Extract keywords for BM25-like indexing
                keywords = self._extract_keywords(chunk.content)
                for keyword in keywords:
                    await conn.execute(
                        """
                        INSERT INTO keyword_index (chunk_id, keyword)
                        VALUES (%s, %s)
                        ON CONFLICT DO UPDATE SET frequency = frequency + 1
                        """,
                        (chunk_id, keyword)
                    )
            await conn.commit()
        
        logger.info(f"Added {len(chunk_ids)} chunks to vector DB")
        return chunk_ids
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Search using vector similarity."""
        query_embedding = self.embeddings.embed_query(query)
        
        async with self.pool.connection() as conn:
            # Build filter clause
            filter_clause = ""
            params = [query_embedding, top_k]
            if filters:
                if "document_type" in filters:
                    filter_clause += "AND metadata->>'document_type' = %s"
                    params.insert(1, filters["document_type"])
                if "mineral_types" in filters:
                    filter_clause += f"AND metadata->'mineral_types' ?| %s"
                    params.insert(1 if "document_type" not in filters else 2, filters["mineral_types"])
            
            rows = await conn.execute(
                f"""
                SELECT chunk_id, document_id, content, metadata,
                       1 - (embedding <-> %s) as similarity_score
                FROM document_chunks
                WHERE 1=1 {filter_clause}
                ORDER BY embedding <-> %s
                LIMIT %s
                """,
                params
            )
            
            results = []
            for row in rows:
                chunk_id, doc_id, content, metadata, score = row
                results.append(RetrievalResult(
                    content=content,
                    source_document=metadata.get("document_name", doc_id),
                    source_page=metadata.get("source_page", 0),
                    document_type=metadata.get("document_type", "unknown"),
                    relevance_score=float(score),
                    semantic_score=float(score),
                    location=metadata.get("location"),
                ))
        
        return results
    
    async def keyword_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """BM25-like keyword search using TF-IDF."""
        keywords = self._extract_keywords(query)
        
        async with self.pool.connection() as conn:
            # Simple TF-IDF scoring
            filter_clause = ""
            base_params = []
            if filters and "document_type" in filters:
                filter_clause = "AND dc.metadata->>'document_type' = %s"
                base_params.append(filters["document_type"])
            
            rows = await conn.execute(
                f"""
                SELECT dc.chunk_id, dc.document_id, dc.content, dc.metadata,
                       SUM(ki.frequency) as keyword_score
                FROM document_chunks dc
                LEFT JOIN keyword_index ki ON dc.chunk_id = ki.chunk_id
                WHERE ki.keyword = ANY(%s) {filter_clause}
                GROUP BY dc.chunk_id, dc.document_id, dc.content, dc.metadata
                ORDER BY keyword_score DESC
                LIMIT %s
                """,
                base_params + [keywords, top_k]
            )
            
            results = []
            for row in rows:
                chunk_id, doc_id, content, metadata, score = row
                results.append(RetrievalResult(
                    content=content,
                    source_document=metadata.get("document_name", doc_id),
                    source_page=metadata.get("source_page", 0),
                    document_type=metadata.get("document_type", "unknown"),
                    relevance_score=float(score) / max(len(keywords), 1),
                    keyword_score=float(score) if score else 0,
                    location=metadata.get("location"),
                ))
        
        return results
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Hybrid search combining semantic and keyword results."""
        semantic_results = await self.semantic_search(query, top_k=top_k*2, filters=filters)
        keyword_results = await self.keyword_search(query, top_k=top_k*2, filters=filters)
        
        # Merge and re-rank
        combined = {}
        for result in semantic_results:
            key = result.source_document + str(result.source_page)
            combined[key] = result
            combined[key].relevance_score = result.semantic_score * semantic_weight
        
        for result in keyword_results:
            key = result.source_document + str(result.source_page)
            if key in combined:
                combined[key].keyword_score = result.keyword_score
                combined[key].relevance_score += result.keyword_score * (1 - semantic_weight)
            else:
                result.relevance_score = result.keyword_score * (1 - semantic_weight)
                combined[key] = result
        
        # Sort by combined score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x.relevance_score,
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        async with self.pool.connection() as conn:
            await conn.execute(
                "DELETE FROM document_chunks WHERE document_id = %s",
                (document_id,)
            )
            await conn.commit()
            return True
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text (basic implementation)."""
        # In production, use proper NLP (spaCy, NLTK, or language models)
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would", "could"
        }
        
        words = text.lower().split()
        keywords = [
            w for w in words
            if w not in stop_words and len(w) > 3
        ]
        return list(set(keywords[:20]))  # Return top 20 unique keywords


# ============================================================================
# QUERY EXPANSION & REFINEMENT
# ============================================================================

class QueryExpander:
    """Expand and refine queries for better retrieval."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def expand_query(self, query: str) -> List[str]:
        """Generate alternative query formulations."""
        prompt = f"""You are a geological query expansion expert. 
Given this query about geological exploration, generate 3 alternative formulations 
that capture the same intent but use different terminology.

Original query: "{query}"

Return ONLY the 3 alternative queries, one per line, without numbering or bullets."""
        
        response = await self.llm.agenerate(prompt)
        expansions = response.split("\n")
        return [q.strip() for q in expansions if q.strip()]
    
    async def decompose_query(self, query: str) -> List[str]:
        """Break complex queries into sub-queries."""
        prompt = f"""You are a geological expert. Break this complex exploration query 
into 2-3 simpler sub-queries that together answer the original question.

Query: "{query}"

Return ONLY the sub-queries, one per line."""
        
        response = await self.llm.agenerate(prompt)
        subqueries = response.split("\n")
        return [q.strip() for q in subqueries if q.strip()]
    
    async def refine_query(self, query: str, context: str = "") -> str:
        """Refine query based on geological domain knowledge."""
        prompt = f"""You are a geological domain expert. 
Refine this exploration query to be more specific and search-friendly.
Add relevant geological terminology if appropriate.

Original query: "{query}"
{f'Context: {context}' if context else ''}

Return ONLY the refined query."""
        
        response = await self.llm.agenerate(prompt)
        return response.strip()


# ============================================================================
# RERANKING ENGINE
# ============================================================================

class RerankerEngine:
    """Rerank retrieval results using cross-encoders."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Rerank results using cross-encoder."""
        if not results:
            return []
        
        # Prepare pairs for cross-encoder
        pairs = [(query, result.content) for result in results]
        scores = self.model.predict(pairs)
        
        # Attach scores and sort
        for result, score in zip(results, scores):
            result.rerank_score = float(score)
        
        sorted_results = sorted(
            results,
            key=lambda x: x.rerank_score,
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    def rerank_async(self, query: str, results: List[RetrievalResult], top_k: int = 5):
        """Async wrapper for reranking."""
        return asyncio.to_thread(self.rerank, query, results, top_k)


# ============================================================================
# CONTEXT COMPRESSION
# ============================================================================

class ContextCompressor:
    """Compress and select most relevant context."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def compress_context(
        self,
        query: str,
        results: List[RetrievalResult],
        max_tokens: int = 2000
    ) -> str:
        """Compress multiple results into coherent context."""
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(results):
            if total_length + len(result.content) > max_tokens:
                break
            
            context_parts.append(
                f"[Source {i+1}: {result.source_document}, p.{result.source_page}]\n"
                f"{result.content}\n"
            )
            total_length += len(result.content)
        
        if not context_parts:
            return ""
        
        combined = "\n".join(context_parts)
        
        # Use LLM to summarize if too long
        if len(combined) > max_tokens:
            prompt = f"""Summarize the following geological information to extract 
the key facts most relevant to this query: "{query}"

Keep the summary under {max_tokens} characters.

Information:
{combined}

Summary:"""
            summary = await self.llm.agenerate(prompt)
            return summary.strip()
        
        return combined
    
    async def select_most_relevant(
        self,
        query: str,
        results: List[RetrievalResult],
        max_count: int = 3
    ) -> List[RetrievalResult]:
        """Select the most relevant results for final answer."""
        if len(results) <= max_count:
            return results
        
        # Use reranker to select top results
        selection_prompt = f"""Given this query: "{query}"

And these candidate results, select the top {max_count} most relevant ones.
Return their indices (1-based) separated by commas.

{chr(10).join(f'{i+1}. {r.content[:200]}...' for i, r in enumerate(results))}

Selected indices:"""
        
        response = await self.llm.agenerate(selection_prompt)
        try:
            indices = [int(idx.strip()) - 1 for idx in response.split(",")]
            indices = [i for i in indices if 0 <= i < len(results)]
            return [results[i] for i in indices]
        except (ValueError, IndexError):
            return results[:max_count]


# ============================================================================
# METADATA FILTERING
# ============================================================================

class MetadataFilter:
    """Build and apply metadata filters."""
    
    @staticmethod
    def build_filter(
        document_types: Optional[List[str]] = None,
        mineral_types: Optional[List[str]] = None,
        depth_range: Optional[Tuple[float, float]] = None,
        date_range: Optional[Tuple[str, str]] = None,
        locations: Optional[List[Dict[str, float]]] = None,
    ) -> Dict[str, Any]:
        """Build a filter dictionary."""
        filters = {}
        
        if document_types:
            filters["document_type"] = document_types
        
        if mineral_types:
            filters["mineral_types"] = mineral_types
        
        if depth_range:
            filters["depth_range"] = depth_range
        
        if date_range:
            filters["date_range"] = date_range
        
        if locations:
            filters["locations"] = locations
        
        return filters
    
    @staticmethod
    def apply_metadata_filter(
        results: List[RetrievalResult],
        filters: Dict[str, Any]
    ) -> List[RetrievalResult]:
        """Apply metadata filters to results."""
        filtered = results
        
        if "document_type" in filters:
            types = filters["document_type"]
            if isinstance(types, str):
                types = [types]
            filtered = [r for r in filtered if r.document_type in types]
        
        if "mineral_types" in filters:
            minerals = filters["mineral_types"]
            if isinstance(minerals, str):
                minerals = [minerals]
            # This would need metadata to include mineral_types
            # filtered = [r for r in filtered if any(m in r.mineral_types for m in minerals)]
        
        return filtered


# ============================================================================
# MAIN RAG ORCHESTRATOR
# ============================================================================

class RAGOrchestrator:
    """Main RAG pipeline orchestrator."""
    
    def __init__(
        self,
        vector_db: VectorDatabaseInterface,
        llm_client,
        redis_client: Optional[aioredis.Redis] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.vector_db = vector_db
        self.llm = llm_client
        self.redis = redis_client
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        self.query_expander = QueryExpander(llm_client)
        self.reranker = RerankerEngine()
        self.compressor = ContextCompressor(llm_client)
        self.metadata_filter = MetadataFilter()
        
        self.cache_ttl = 3600  # 1 hour
    
    async def ingest_document(
        self,
        document_id: str,
        document_name: str,
        content: str,
        document_type: str,
        metadata: Optional[Dict] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> List[str]:
        """Ingest and chunk a document."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        text_chunks = splitter.split_text(content)
        chunks = []
        
        for i, text in enumerate(text_chunks):
            geo_metadata = GeoMetadata(
                document_id=document_id,
                document_name=document_name,
                document_type=document_type,
                source_page=0,  # Would be extracted from document parser
                chunk_index=i,
                **{k: v for k, v in (metadata or {}).items()
                   if k in GeoMetadata.__dataclass_fields__}
            )
            
            chunk = DocumentChunk(
                content=text,
                metadata=geo_metadata,
            )
            chunks.append(chunk)
        
        # Add to vector DB
        chunk_ids = await self.vector_db.add_chunks(chunks)
        logger.info(f"Ingested {document_name} with {len(chunk_ids)} chunks")
        
        return chunk_ids
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        hybrid: bool = True,
        semantic_weight: float = 0.7,
        rerank: bool = True,
        filters: Optional[Dict] = None,
    ) -> List[RetrievalResult]:
        """Full retrieval pipeline."""
        # Check cache
        cache_key = f"rag:retrieve:{query}:{json.dumps(filters or {})}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Expand query
        expanded_queries = [query]
        try:
            expansions = await self.query_expander.expand_query(query)
            expanded_queries.extend(expansions[:2])
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}")
        
        # Retrieve using all query variants
        all_results = {}
        for q in expanded_queries:
            try:
                if hybrid:
                    results = await self.vector_db.hybrid_search(
                        q,
                        top_k=top_k*2,
                        semantic_weight=semantic_weight,
                        filters=filters
                    )
                else:
                    results = await self.vector_db.semantic_search(
                        q,
                        top_k=top_k,
                        filters=filters
                    )
                
                for result in results:
                    key = f"{result.source_document}:{result.source_page}"
                    if key not in all_results:
                        all_results[key] = result
                    else:
                        # Average scores
                        all_results[key].relevance_score = (
                            (all_results[key].relevance_score + result.relevance_score) / 2
                        )
            except Exception as e:
                logger.error(f"Retrieval failed for query '{q}': {e}")
        
        # Convert to list and sort
        results = sorted(
            all_results.values(),
            key=lambda x: x.relevance_score,
            reverse=True
        )[:top_k*2]
        
        # Rerank
        if rerank and results:
            try:
                results = await self.reranker.rerank_async(query, results, top_k)
            except Exception as e:
                logger.warning(f"Reranking failed: {e}")
                results = results[:top_k]
        else:
            results = results[:top_k]
        
        # Cache results
        if self.redis:
            try:
                await self.redis.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps([r.to_dict() for r in results])
                )
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
        
        return results
    
    async def generate_answer(
        self,
        query: str,
        context_results: List[RetrievalResult],
        max_context_tokens: int = 2000,
    ) -> Tuple[str, List[RetrievalResult]]:
        """Generate answer with context."""
        # Compress context
        context = await self.compressor.compress_context(
            query,
            context_results,
            max_tokens=max_context_tokens
        )
        
        # Generate answer
        prompt = f"""You are a geology expert analyzing exploration data.
Based on the provided documents, answer this question:

Question: {query}

Context from geological reports:
{context}

Provide a detailed, technical answer. Cite specific sources when referencing data."""
        
        answer = await self.llm.agenerate(prompt)
        
        return answer.strip(), context_results
    
    async def full_rag_pipeline(
        self,
        query: str,
        top_k: int = 5,
        max_context_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve -> rerank -> answer."""
        # Retrieve
        results = await self.retrieve(
            query,
            top_k=top_k,
            hybrid=True,
            rerank=True
        )
        
        if not results:
            return {
                "query": query,
                "answer": "No relevant documents found for this query.",
                "sources": [],
                "confidence": 0.0,
            }
        
        # Generate answer
        answer, sources = await self.generate_answer(query, results)
        
        # Calculate confidence
        avg_score = np.mean([r.rerank_score or r.relevance_score for r in results])
        confidence = float(min(avg_score, 1.0))
        
        return {
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "document": r.source_document,
                    "page": r.source_page,
                    "type": r.document_type,
                    "relevance_score": r.rerank_score or r.relevance_score,
                    "excerpt": r.content[:300] + "..." if len(r.content) > 300 else r.content,
                }
                for r in results
            ],
            "confidence": confidence,
            "total_sources": len(results),
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of RAG pipeline."""
    # Initialize vector DB
    vector_db = PostgresVectorDB(
        connection_string="postgresql+asyncpg://user:password@localhost/geomind"
    )
    await vector_db.init_pool()
    
    # Initialize (you'd use real LLM client - shown here as placeholder)
    class DummyLLM:
        async def agenerate(self, prompt: str) -> str:
            return "Generated response"
    
    llm = DummyLLM()
    
    # Initialize orchestrator
    rag = RAGOrchestrator(
        vector_db=vector_db,
        llm_client=llm,
    )
    
    # Ingest a document
    sample_doc = """
    Sumayau Nickel-Copper Project Drill Log SYD25-0001
    Location: 5.2345°N, 118.1234°E, Sabah, Malaysia
    Depth: 0-200m
    
    0-50m: Laterite, high nickel content (2.1% Ni)
    50-100m: Transition zone with copper mineralization (1.8% Cu)
    100-150m: Primary massive sulfide (54% Cu, 2.3% Ni)
    150-200m: Disseminated mineralization (1.2% Cu)
    """
    
    chunk_ids = await rag.ingest_document(
        document_id="SYD25-0001",
        document_name="Sumayau Drill Log SYD25-0001",
        content=sample_doc,
        document_type="drill_log",
        metadata={
            "location": {"lat": 5.2345, "lon": 118.1234},
            "mineral_types": ["nickel", "copper"],
        }
    )
    
    # Retrieve and answer
    result = await rag.full_rag_pipeline(
        query="What are the copper and nickel grades at Sumayau?"
    )
    
    print(json.dumps(result, indent=2))
    
    # Cleanup
    await vector_db.pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

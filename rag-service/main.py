import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from config import settings
from loader import DocumentLoader
from chunker import DocumentChunker
from vector_store import QdrantManager
from retriever import HybridRetriever

app = FastAPI(
    title="NovaTech RAG Service",
    description="RAG service for document loading, indexing, and hybrid retrieval with reranking.",
    version="1.0.0"
)

# ----------------------------------------------------
# PYDANTIC SCHEMAS
# ----------------------------------------------------
class RetrieveRequest(BaseModel):
    query: str = Field(..., description="The query string to search for.")
    category: Optional[str] = Field(None, description="Optional metadata category filter (e.g. hr, finance, it).")
    top_k: int = Field(10, description="Number of baseline nodes to retrieve from vector store.")
    rerank_top_n: int = Field(4, description="Number of final reranked nodes to return.")

class DocumentChunkResponse(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class RetrieveResponse(BaseModel):
    query: str
    results: List[DocumentChunkResponse]

class IngestResponse(BaseModel):
    success: bool
    message: str
    chunks_count: int

# ----------------------------------------------------
# API ENDPOINTS
# ----------------------------------------------------
@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
def ingest_documents():
    """
    Triggers recursive loading of markdown documents from data/documents/,
    chunks them, and builds/updates the Qdrant index.
    """
    try:
        # 1. Load documents
        loader = DocumentLoader(directory_path="data/documents")
        documents = loader.load_documents()
        
        if not documents:
            return IngestResponse(
                success=True,
                message="No documents found to ingest.",
                chunks_count=0
            )
            
        # 2. Chunk documents
        chunker = DocumentChunker()
        nodes = chunker.split_documents(documents)
        
        # 3. Index to Qdrant
        manager = QdrantManager()
        manager.build_index(nodes)
        
        return IngestResponse(
            success=True,
            message="Ingestion completed successfully.",
            chunks_count=len(nodes)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/retrieve", response_model=RetrieveResponse, tags=["Retrieval"])
def retrieve_documents(payload: RetrieveRequest):
    """
    Retrieves relevant document chunks from Qdrant using similarity search,
    filters by metadata category if requested, and rerank matches with Flashrank.
    """
    try:
        manager = QdrantManager()
        index = manager.get_index()
        retriever = HybridRetriever(index)
        
        results = retriever.retrieve(
            query=payload.query,
            category=payload.category,
            top_k=payload.top_k,
            rerank_top_n=payload.rerank_top_n
        )
        
        formatted_results = [
            DocumentChunkResponse(
                text=res["text"],
                score=res["score"],
                metadata=res["metadata"]
            )
            for res in results
        ]
        
        return RetrieveResponse(
            query=payload.query,
            results=formatted_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "rag-service"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )

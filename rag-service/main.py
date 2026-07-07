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

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI_OOPS RAG Service",
    description="RAG service for document loading, indexing, and hybrid retrieval with reranking.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

class AnswerRequest(BaseModel):
    query: str = Field(..., description="The query string to search for and answer.")
    category: Optional[str] = Field(None, description="Optional metadata category filter (e.g. hr, finance, it).")
    top_k: int = Field(10, description="Number of baseline nodes to retrieve from vector store.")
    rerank_top_n: int = Field(4, description="Number of final reranked nodes to return.")

class AnswerResponse(BaseModel):
    query: str
    answer: str
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
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        docs_path = os.path.join(root_dir, "data", "documents")
        loader = DocumentLoader(directory_path=docs_path)
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
        try:
            chunks_indexed = manager.index_chunks(nodes)
            return IngestResponse(
                success=True,
                message="Ingestion completed successfully.",
                chunks_count=chunks_indexed
            )
        finally:
            manager.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/retrieve", response_model=RetrieveResponse, tags=["Retrieval"])
def retrieve_documents(payload: RetrieveRequest):
    """
    Retrieves relevant document chunks from Qdrant using similarity search,
    filters by metadata category if requested, and rerank matches with Flashrank.
    """
    try:
        retriever = HybridRetriever()
        try:
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
        finally:
            retriever.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@app.post("/answer", response_model=AnswerResponse, tags=["Retrieval & Generation"])
def answer_query(payload: AnswerRequest):
    """
    Retrieves document chunks from Qdrant, reranks them, and synthesizes a
    concise corporate policy answer using the configured OpenAI Chat model.
    """
    try:
        retriever = HybridRetriever()
        try:
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
            
            if not results:
                return AnswerResponse(
                    query=payload.query,
                    answer="No relevant documents were found in the database to answer this query.",
                    results=[]
                )
                
            # Synthesize answer using OpenAI
            context_text = "\n\n".join(f"[Doc: {res['metadata'].get('file_name', 'unknown')}] {res['text']}" for res in results)
            
            api_key = settings.llm.openai_api_key or "mock_key"
            llm = ChatOpenAI(
                model=settings.llm.default_chat_model,
                temperature=0.0,
                api_key=api_key
            )
            
            system_prompt = (
                "You are a helpful corporate assistant. Use the following retrieved document context "
                "to answer the user's question accurately. Do not make up facts. Cite your sources (the Doc filename) when answering. "
                "If the context does not contain the answer, state that you cannot find the answer in the provided documents.\n\n"
                f"Retrieved Context:\n{context_text}"
            )
            
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=payload.query)
            ])
            
            return AnswerResponse(
                query=payload.query,
                answer=response.content,
                results=formatted_results
            )
        finally:
            retriever.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "rag-service"}

if __name__ == "__main__":
    import urllib.parse
    parsed_url = urllib.parse.urlparse(settings.rag.url)
    rag_port = parsed_url.port or 8001
    
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=rag_port,
        reload=settings.app.debug
    )

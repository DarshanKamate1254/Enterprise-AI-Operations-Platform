import sys
import os
from typing import List, Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings
from config import settings

_ranker = None

def get_ranker():
    """Lazy load the Flashrank Ranker to optimize memory usage."""
    global _ranker
    if _ranker is None:
        from flashrank import Ranker
        _ranker = Ranker()
    return _ranker

class HybridRetriever:
    def __init__(self, collection_name: str = "nova_policies"):
        self.collection_name = collection_name
        
        # Setup OpenAI Embeddings
        api_key = settings.llm.openai_api_key or "mock_key"
        self.embed_model = OpenAIEmbeddings(
            model=settings.llm.default_embedding_model,
            api_key=api_key
        )
        
        # Setup Qdrant Client
        client_kwargs = {
            "host": settings.qdrant.host,
            "port": settings.qdrant.port,
            "https": settings.qdrant.use_https,
        }
        if settings.qdrant.api_key:
            client_kwargs["api_key"] = settings.qdrant.api_key
            
        self.client = QdrantClient(**client_kwargs)

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 10,
        rerank_top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search in Qdrant with metadata filtering, followed by local Flashrank reranking.
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            print(f"Collection '{self.collection_name}' does not exist in Qdrant.")
            return []

        # 1. Embed query
        query_vector = self.embed_model.embed_query(query)
        
        # 2. Setup category/department filters if requested
        query_filter = None
        if category:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.category",
                        match=models.MatchValue(value=category)
                    )
                ]
            )
            
        # 3. Perform Qdrant vector search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        
        if not search_results:
            return []
            
        # 4. Rerank matches using Flashrank
        try:
            from flashrank import RerankRequest
            ranker = get_ranker()
            
            passages = []
            for idx, hit in enumerate(search_results):
                passages.append({
                    "id": idx,
                    "text": hit.payload.get("text", ""),
                    "meta": hit.payload.get("metadata", {})
                })
                
            req = RerankRequest(query=query, passages=passages)
            reranked = ranker.rerank(req)
            
            results = []
            for item in reranked[:rerank_top_n]:
                orig_idx = item["id"]
                hit = search_results[orig_idx]
                results.append({
                    "text": item["text"],
                    "score": float(item["score"]),
                    "metadata": item["meta"]
                })
        except Exception as e:
            print(f"Flashrank reranking failed: {e}. Falling back to default Qdrant cosine similarity scores.")
            results = []
            for hit in search_results[:rerank_top_n]:
                results.append({
                    "text": hit.payload.get("text", ""),
                    "score": float(hit.score) if hit.score is not None else 0.0,
                    "metadata": hit.payload.get("metadata", {})
                })
                
        return results

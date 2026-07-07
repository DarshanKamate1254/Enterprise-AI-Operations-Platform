import sys
import os
from typing import List, Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from config import settings


class RetrieverTool:
    """
    Retriever Tool for querying the policy database.
    Supports local dependency injection of a retriever engine,
    or falls back to microservice API requests.
    """
    def __init__(self, local_retriever: Optional[Any] = None, http_client: Optional[httpx.Client] = None):
        self.local_retriever = local_retriever
        self.http_client = http_client or httpx.Client()
        # Fallback API URL from settings
        self.api_url = f"{settings.rag.url.rstrip('/')}/retrieve"

    def search_policies(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 10,
        rerank_top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic search with metadata filtering and reranking.
        """
        # Option A: Local direct execution (useful in combined test runs)
        if self.local_retriever:
            return self.local_retriever.retrieve(
                query=query,
                category=category,
                top_k=top_k,
                rerank_top_n=rerank_top_n
            )
            
        # Option B: Decentralized microservice HTTP call
        payload = {
            "query": query,
            "category": category,
            "top_k": top_k,
            "rerank_top_n": rerank_top_n
        }
        
        try:
            response = self.http_client.post(self.api_url, json=payload, timeout=30.0)
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                raise RuntimeError(f"RAG microservice returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"RAG service connection error: {e}. Falling back to local direct retrieval...")
            try:
                # Ensure rag-service is in sys.path
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                rag_dir = os.path.join(root_dir, "rag-service")
                if root_dir not in sys.path:
                    sys.path.insert(0, root_dir)
                if rag_dir not in sys.path:
                    sys.path.insert(0, rag_dir)
                
                from retriever import HybridRetriever
                local = HybridRetriever()
                try:
                    return local.retrieve(
                        query=query,
                        category=category,
                        top_k=top_k,
                        rerank_top_n=rerank_top_n
                    )
                finally:
                    local.close()
            except Exception as local_err:
                print(f"Local direct RAG fallback execution failed: {local_err}", file=sys.stderr)
                return []
            
    def close(self):
        if self.http_client:
            self.http_client.close()

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
            response = self.http_client.post(self.api_url, json=payload)
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                raise RuntimeError(f"RAG microservice returned status {response.status_code}: {response.text}")
        except Exception as e:
            # Fallback mock/log on connection errors
            print(f"RAG service connection error: {e}. Returning empty matches list.")
            return []
            
    def close(self):
        if self.http_client:
            self.http_client.close()

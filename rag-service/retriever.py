import sys
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from config import settings
from vector_store import HashingTFEncoder

# Lazy loader for Flashrank Ranker
_ranker = None
def get_ranker():
    global _ranker
    if _ranker is None:
        from flashrank import Ranker
        _ranker = Ranker()
    return _ranker

# Lazy loader for Redis connection
_redis_client = None
_redis_disabled = False

def get_redis_client():
    global _redis_client, _redis_disabled
    if _redis_disabled:
        return None
    if _redis_client is None:
        try:
            import redis
            if settings.redis.host:
                _redis_client = redis.Redis(
                    host=settings.redis.host,
                    port=settings.redis.port,
                    db=settings.redis.db,
                    password=settings.redis.password,
                    socket_timeout=1.0
                )
                # Test connection
                _redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed (semantic cache disabled): {e}")
            _redis_client = None
            _redis_disabled = True
    return _redis_client


class HybridRetriever:
    """
    HybridRetriever implements semantic search over Qdrant, integrating:
    1. Redis Semantic Cache
    2. Corrective RAG (CRAG) query rewrite fallback
    3. HashingTFEncoder (sparse-dense hybrid search)
    4. Dartboard Retrieval (MMR-based relevance + diversity)
    5. Relevant Segment Extraction (RSE chunk stitching)
    
    Replaces the legacy Pinecone-based HybridRetriever class.
    """
    def __init__(self):
        # Retrieve OpenAI Embeddings
        api_key = settings.llm.openai_api_key or "mock_key"
        self.embed_model = OpenAIEmbeddings(
            model=settings.llm.default_embedding_model,
            api_key=api_key
        )
        
        # Instantiate ChatOpenAI for CRAG query rewrites
        self.llm = ChatOpenAI(
            model=settings.llm.default_chat_model,
            temperature=0.0,
            api_key=api_key
        )
        
        # Initialize Qdrant Client
        if settings.qdrant.path:
            self.client = QdrantClient(path=settings.qdrant.path)
        else:
            try:
                # Try connecting to Qdrant server if host is defined
                if settings.qdrant.host:
                    self.client = QdrantClient(
                        host=settings.qdrant.host,
                        port=settings.qdrant.port or 6333,
                        api_key=settings.qdrant.api_key,
                        timeout=3.0
                    )
                    # Force a connectivity check
                    self.client.get_collections()
                else:
                    raise ValueError("No host specified")
            except Exception as e:
                # Fallback to local disk storage
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "qdrant_db"))
                print(f"[!] Qdrant server connection failed ({e}). Falling back to local storage: {db_path}")
                self.client = QdrantClient(path=db_path)

        self.collection_name = settings.qdrant.collection_name
        self.sparse_encoder = HashingTFEncoder()

    def close(self):
        if hasattr(self, "client") and self.client:
            try:
                self.client.close()
            except Exception:
                pass

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        a = np.array(v1)
        b = np.array(v2)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def _check_semantic_cache(self, query: str, query_vector: List[float]) -> Optional[List[Dict[str, Any]]]:
        """
        Queries Redis semantic cache for a cached query with high similarity (>0.95).
        """
        r = get_redis_client()
        if not r:
            return None
            
        try:
            # Fetch all semantic cache keys
            keys = r.keys("semantic_cache:*")
            for k in keys:
                cache_data_str = r.get(k)
                if not cache_data_str:
                    continue
                cache_data = json.loads(cache_data_str)
                cached_vector = cache_data.get("vector", [])
                
                # Check similarity
                sim = self._cosine_similarity(query_vector, cached_vector)
                if sim >= 0.95:
                    print(f"Redis Semantic Cache Hit! Match found under key '{k.decode()}' (similarity: {sim:.4f})")
                    return cache_data.get("results", [])
        except Exception as e:
            print(f"Error checking semantic cache: {e}")
            
        return None

    def _write_semantic_cache(self, query: str, query_vector: List[float], results: List[Dict[str, Any]]):
        """
        Saves a query, its embedding, and the results to Redis.
        """
        r = get_redis_client()
        if not r:
            return
            
        try:
            cache_key = f"semantic_cache:{hash(query)}"
            cache_payload = {
                "query": query,
                "vector": query_vector,
                "results": results
            }
            # Cache for 1 hour
            r.setex(cache_key, 3600, json.dumps(cache_payload))
        except Exception as e:
            print(f"Error writing to semantic cache: {e}")

    def _query_qdrant(self, query: str, category: Optional[str], top_k: int, query_dense: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Executes a sparse-dense hybrid vector query on Qdrant with role/category filtering.
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, FusionQuery, Fusion, SparseVector
        
        # Embed query text (dense) if not already provided
        if query_dense is None:
            query_dense = self.embed_model.embed_query(query)
            
        # Generate query text (sparse)
        query_sparse = self.sparse_encoder.encode(query)
        
        # Build Qdrant metadata filter
        query_filter = None
        if category:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category)
                    )
                ]
            )
            
        # Execute hybrid query on Qdrant
        response = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                Prefetch(
                    query=query_dense,
                    using="dense",
                    limit=top_k,
                ),
                Prefetch(
                    query=SparseVector(
                        indices=query_sparse["indices"],
                        values=query_sparse["values"]
                    ),
                    using="sparse",
                    limit=top_k,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            query_filter=query_filter,
            limit=top_k,
            with_vectors=["dense"],
            with_payload=True
        )
        
        results = []
        for point in response.points:
            meta = point.payload or {}
            dense_vec = None
            if isinstance(point.vector, dict):
                dense_vec = point.vector.get("dense")
            elif isinstance(point.vector, list):
                dense_vec = point.vector
                
            score = point.score
            # Recompute score as cosine similarity to be compatible with other components (e.g. CRAG 0.6 threshold check)
            if dense_vec and query_dense:
                score = self._cosine_similarity(query_dense, dense_vec)
                
            results.append({
                "id": point.id,
                "text": meta.get("text", ""),
                "score": score,
                "vector": dense_vec,
                "metadata": meta
            })
        return results

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 10,
        rerank_top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Executes the full upgraded retrieval pipeline:
        Redis Semantic Cache -> CRAG Rewrite -> Qdrant Hybrid Search -> Flashrank -> MMR Diversity -> RSE Stitching
        """
        # 1. Generate query dense vector for semantic cache checks
        query_dense = self.embed_model.embed_query(query)
        
        # 2. Redis Semantic Cache Lookups
        cached_results = self._check_semantic_cache(query, query_dense)
        if cached_results is not None:
            return cached_results

        # 3. Baseline Qdrant hybrid search
        search_results = self._query_qdrant(query, category, top_k, query_dense=query_dense)
        
        # 4. Technique: Corrective RAG (CRAG)
        # Trigger query rewrite fallback if the top hit similarity falls below the threshold
        top_score = search_results[0]["score"] if search_results else 0.0
        if settings.rag.enable_crag and top_score < settings.rag.crag_threshold:
            print(f"Technique [CRAG]: Low confidence top score ({top_score:.4f} < {settings.rag.crag_threshold}). Rewriting query...")
            rewrite_prompt = (
                f"Rewrite the following user query to be optimized for semantic keyword and vector retrieval "
                f"in a policy document store. Return ONLY the rewritten query text:\n\nUser Query: {query}"
            )
            try:
                rewrite_resp = self.llm.invoke(rewrite_prompt)
                rewritten_query = rewrite_resp.content.strip()
                print(f"Technique [CRAG]: Rewritten query is '{rewritten_query}'")
                
                # Fetch second set of results using rewritten query
                fallback_results = self._query_qdrant(rewritten_query, category, top_k)
                
                # Merge and deduplicate by point ID, keeping highest score
                merged_map = {item["id"]: item for item in search_results}
                for item in fallback_results:
                    if item["id"] not in merged_map or item["score"] > merged_map[item["id"]]["score"]:
                        merged_map[item["id"]] = item
                        
                search_results = sorted(list(merged_map.values()), key=lambda x: x["score"], reverse=True)
            except Exception as e:
                print(f"Technique [CRAG]: Fallback query rewrite failed: {e}")

        if not search_results:
            return []

        # 5. Flashrank cross-encoder reranking
        try:
            ranker = get_ranker()
            passages = []
            for idx, hit in enumerate(search_results):
                passages.append({
                    "id": idx,
                    "text": hit.get("text", ""),
                    "meta": hit.get("metadata", {})
                })
                
            from flashrank import RerankRequest
            req = RerankRequest(query=query, passages=passages)
            reranked = ranker.rerank(req)
            
            # Map reranked outcomes back to search results formats
            ordered_results = []
            for item in reranked:
                orig_idx = item["id"]
                hit = search_results[orig_idx]
                hit["score"] = float(item["score"])
                ordered_results.append(hit)
                
            search_results = ordered_results
        except Exception as e:
            print(f"Flashrank reranking failed: {e}. Defaulting to Qdrant/Cosine similarity.")

        # 6. Technique: Dartboard Retrieval (Maximal Marginal Relevance - MMR)
        # Select top diverse and relevant chunks using vector similarities
        final_candidates = search_results
        if settings.rag.enable_dartboard and len(search_results) > rerank_top_n:
            print("Technique [Dartboard]: Diversifying search results via MMR...")
            selected_indices = [0]  # Always seed with the highest ranked result
            
            while len(selected_indices) < min(rerank_top_n, len(search_results)):
                best_mmr = -999.0
                best_candidate_idx = -1
                
                for idx, candidate in enumerate(search_results):
                    if idx in selected_indices:
                        continue
                        
                    # Calculate similarity with already selected points
                    max_sim = -1.0
                    for sel_idx in selected_indices:
                        sim = self._cosine_similarity(candidate["vector"], search_results[sel_idx]["vector"])
                        if sim > max_sim:
                            max_sim = sim
                            
                    # Calculate MMR score (relevance vs redundancy penalty)
                    # Score is normalized to [0, 1] range to match similarity norm
                    relevance = candidate["score"]
                    mmr_val = 0.7 * relevance - 0.3 * max_sim
                    
                    if mmr_val > best_mmr:
                        best_mmr = mmr_val
                        best_candidate_idx = idx
                        
                if best_candidate_idx != -1:
                    selected_indices.append(best_candidate_idx)
                else:
                    break
                    
            final_candidates = [search_results[i] for i in selected_indices]

        # 7. Technique: Relevant Segment Extraction (RSE)
        # Stitch consecutive retrieved text chunks from the same document together
        if settings.rag.enable_rse:
            print("Technique [RSE]: Stitching adjacent document chunks...")
            # Group candidate chunks by filename
            file_groups = {}
            for item in final_candidates:
                fn = item["metadata"].get("file_name", "unknown")
                file_groups.setdefault(fn, []).append(item)
                
            stitched_results = []
            for fn, group in file_groups.items():
                # Sort group by chunk index
                group_sorted = sorted(group, key=lambda x: x["metadata"].get("chunk_index", 0))
                
                temp_chunk = group_sorted[0]
                for next_chunk in group_sorted[1:]:
                    idx_curr = temp_chunk["metadata"].get("chunk_index", 0)
                    idx_next = next_chunk["metadata"].get("chunk_index", 0)
                    
                    # If chunks are consecutive (difference of 1), stitch them together
                    if idx_next - idx_curr <= 1:
                        temp_chunk["text"] += f"\n...\n{next_chunk['text']}"
                        temp_chunk["score"] = max(temp_chunk["score"], next_chunk["score"])
                        # Update metadata boundary limit
                        temp_chunk["metadata"]["chunk_index"] = idx_next
                    else:
                        stitched_results.append(temp_chunk)
                        temp_chunk = next_chunk
                        
                stitched_results.append(temp_chunk)
                
            # Re-sort stitched results by score
            final_candidates = sorted(stitched_results, key=lambda x: x["score"], reverse=True)

        # 8. Clean vectors and format for return
        output_results = []
        for item in final_candidates[:rerank_top_n]:
            output_results.append({
                "text": item["text"],
                "score": item["score"],
                "metadata": item["metadata"]
            })
            
        # 9. Save final outcomes to Redis semantic cache
        self._write_semantic_cache(query, query_dense, output_results)
        
        return output_results

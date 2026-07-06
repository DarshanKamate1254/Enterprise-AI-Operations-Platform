from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
from llama_index.postprocessor.flashrank import FlashrankRerank
from llama_index.core.schema import NodeWithScore

class HybridRetriever:
    def __init__(self, index: VectorStoreIndex):
        self.index = index

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 10,
        rerank_top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Perform vector retrieval with optional metadata filtering, followed by Flashrank Reranking.
        """
        # 1. Setup metadata filters if category/department filter is provided
        filters = None
        if category:
            filters = MetadataFilters(filters=[
                MetadataFilter(key="category", value=category)
            ])
            
        # 2. Get the base retriever from LlamaIndex
        retriever = self.index.as_retriever(
            similarity_top_k=top_k,
            filters=filters
        )
        
        # 3. Retrieve baseline nodes
        retrieved_nodes: List[NodeWithScore] = retriever.retrieve(query)
        
        if not retrieved_nodes:
            return []
            
        # 4. Apply Flashrank Reranker to rank and select top_n results
        try:
            # Note: Flashrank downloads a tiny local cross-encoder model for ranking if not present
            reranker = FlashrankRerank(top_n=rerank_top_n)
            reranked_nodes: List[NodeWithScore] = reranker.postprocess_nodes(
                nodes=retrieved_nodes,
                query_str=query
            )
        except Exception as e:
            print(f"Reranking failed or model loading errored: {e}. Falling back to default cosine similarity order.")
            reranked_nodes = retrieved_nodes[:rerank_top_n]
            
        # 5. Format outputs as clean serializable dictionary blocks
        results = []
        for node_score in reranked_nodes:
            results.append({
                "text": node_score.node.get_content(),
                "score": float(node_score.score),
                "metadata": node_score.node.metadata
            })
            
        return results

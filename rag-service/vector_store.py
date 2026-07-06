import sys
import os
import uuid
import re
import hashlib
from typing import List, Dict, Any, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from config import settings
from chunker import TextChunk

class HashingTFEncoder:
    """
    Lightweight, stateless TF-IDF sparse vector generator.
    Maps words to token indices via feature hashing to support local Pinecone hybrid search.
    """
    def __init__(self, num_features: int = 10000):
        self.num_features = num_features

    def encode(self, text: str) -> Dict[str, Any]:
        # Simple regex tokenization
        words = re.findall(r'\w+', text.lower())
        tf = {}
        for w in words:
            if len(w) > 2:  # Ignore short tokens/stop words
                # Map word to a feature index using hash
                h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16) % self.num_features
                tf[h] = tf.get(h, 0.0) + 1.0
        
        indices = sorted(list(tf.keys()))
        values = [tf[idx] for idx in indices]
        return {
            "indices": indices,
            "values": values
        }


class PineconeManager:
    """
    Pinecone Manager handles vector indexing, CCH context prepending, and HyPE question enrichment.
    Replaces the legacy QdrantManager class.
    """
    def __init__(self):
        # Retrieve OpenAI Embeddings
        api_key = settings.llm.openai_api_key or "mock_key"
        self.embed_model = OpenAIEmbeddings(
            model=settings.llm.default_embedding_model,
            api_key=api_key
        )
        
        # Instantiate ChatOpenAI for CCH and HyPE generation
        self.llm = ChatOpenAI(
            model=settings.llm.default_chat_model,
            temperature=0.0,
            api_key=api_key
        )
        
        # Initialize Pinecone Client
        pc_api_key = settings.pinecone.api_key or "mock_key"
        self.pc = Pinecone(api_key=pc_api_key)
        self.index_name = settings.pinecone.index_name
        self.sparse_encoder = HashingTFEncoder()

    def create_index_if_not_exists(self, embedding_dim: int = 1536):
        """
        Creates Pinecone Serverless index if it is not already present.
        If the API key is restricted (data-plane only), falls back gracefully.
        """
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name} (dim: {embedding_dim})...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=embedding_dim,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.pinecone.environment or 'us-east-1'
                    )
                )
            else:
                print(f"Pinecone index '{self.index_name}' already exists.")
        except Exception as e:
            print(f"Warning: Control plane check failed ({e}). Proceeding assuming index '{self.index_name}' already exists...")

    def index_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Processes document chunks, runs CCH and HyPE techniques, compiles embeddings,
        and uploads sparse-dense points to the Pinecone index.
        """
        if not chunks:
            return 0
            
        self.create_index_if_not_exists()
        index = self.pc.Index(self.index_name)
        
        # 1. Technique: Contextual Chunk Headers (CCH)
        # Precompute document summaries once per file to minimize API costs
        doc_summaries = {}
        if settings.rag.enable_cch:
            print("Technique [CCH]: Generating context summaries for source files...")
            # Group chunks by filename
            docs_map = {}
            for chunk in chunks:
                fn = chunk.metadata.get("file_name", "unknown")
                docs_map.setdefault(fn, []).append(chunk.text)
                
            for fn, text_list in docs_map.items():
                # Take sample text from the document (up to 4000 chars) for summary context
                doc_sample = "\n".join(text_list)[:4000]
                prompt = (
                    f"Summarize the general content, target audience, and policy scope of the document '{fn}' "
                    f"in 1 concise sentence to enrich individual search chunks:\n\n{doc_sample}"
                )
                try:
                    summary_resp = self.llm.invoke(prompt)
                    doc_summaries[fn] = summary_resp.content.strip()
                except Exception as ex:
                    print(f"Failed to generate summary for {fn}: {ex}")
                    doc_summaries[fn] = "Corporate guidelines document."
        
        # 2. Compile points and compute embeddings
        points = []
        texts_to_embed = []
        
        print("Technique [HyPE] & Indexing: Enriching and embedding chunks...")
        for idx, chunk in enumerate(chunks):
            chunk_text = chunk.text
            fn = chunk.metadata.get("file_name", "unknown")
            category = chunk.metadata.get("category", "unknown")
            
            # Prepend Context Summary (CCH)
            header_text = ""
            if settings.rag.enable_cch and fn in doc_summaries:
                header_text = f"[Context: {doc_summaries[fn]} | Category: {category}]\n"
                
            # Precompute Hypothetical Questions (HyPE)
            hype_text = ""
            if settings.rag.enable_hype:
                prompt = (
                    f"Based on the following text chunk, write 2 short search queries that this text answers. "
                    f"Output only the queries, one per line. Do not write any prefix or commentary:\n\n"
                    f"Text Chunk:\n{chunk_text}"
                )
                try:
                    hype_resp = self.llm.invoke(prompt)
                    hype_text = f"\n[Hypothetical Questions:\n{hype_resp.content.strip()}]\n"
                except Exception as ex:
                    print(f"Failed to precompute HyPE questions for chunk {idx}: {ex}")
            
            # Combine elements to form enriched text block
            enriched_text = f"{header_text}{chunk_text}{hype_text}"
            texts_to_embed.append(enriched_text)
            
        # Bulk embed texts via OpenAI
        print(f"Embedding {len(texts_to_embed)} chunks via OpenAI...")
        embeddings = self.embed_model.embed_documents(texts_to_embed)
        
        # Build Pinecone Upsert Points
        for idx, (chunk, embedding, enriched_text) in enumerate(zip(chunks, embeddings, texts_to_embed)):
            point_id = str(uuid.uuid4())
            
            # Generate sparse values for hybrid search
            sparse_vector = self.sparse_encoder.encode(chunk.text)
            
            # Build metadata payload (including file name, category, and chunk index for RSE technique)
            metadata = {
                "text": chunk.text,
                "enriched_text": enriched_text,
                "file_name": chunk.metadata.get("file_name", "unknown"),
                "category": chunk.metadata.get("category", "unknown"),
                "chunk_index": int(chunk.metadata.get("chunk_index", idx))
            }
            
            points.append({
                "id": point_id,
                "values": embedding,
                "sparse_values": sparse_vector,
                "metadata": metadata
            })
            
        # Batch upload to Pinecone (batches of 100)
        print(f"Uploading points to Pinecone index '{self.index_name}'...")
        batch_size = 100
        for i in range(0, len(points), batch_size):
            index.upsert(vectors=points[i:i+batch_size])
            
        print("Upload completed successfully.")
        return len(points)

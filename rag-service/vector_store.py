import sys
import os
import uuid
from typing import List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from config import settings
from chunker import TextChunk

class QdrantManager:
    def __init__(self, collection_name: str = "nova_policies"):
        self.collection_name = collection_name
        
        # Initialize OpenAI Embeddings from settings
        api_key = settings.llm.openai_api_key or "mock_key"
        self.embed_model = OpenAIEmbeddings(
            model=settings.llm.default_embedding_model,
            api_key=api_key
        )
        
        # Configure client connection arguments
        client_kwargs = {
            "host": settings.qdrant.host,
            "port": settings.qdrant.port,
            "https": settings.qdrant.use_https,
        }
        if settings.qdrant.api_key:
            client_kwargs["api_key"] = settings.qdrant.api_key
            
        self.client = QdrantClient(**client_kwargs)

    def create_collection_if_not_exists(self, embedding_dim: int = 1536):
        """
        Create collection with standard cosine metric and configuration settings if not already present.
        """
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            print(f"Creating Qdrant collection: {self.collection_name} (dim: {embedding_dim})")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=embedding_dim,
                    distance=Distance.COSINE
                )
            )
        else:
            print(f"Qdrant collection '{self.collection_name}' already exists.")

    def index_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Generates vector embeddings and indexes chunks in Qdrant.
        """
        if not chunks:
            return 0
            
        self.create_collection_if_not_exists()
        
        # Extract text blocks
        texts = [chunk.text for chunk in chunks]
        
        # Embed texts in batches
        print(f"Embedding {len(texts)} chunks via OpenAI...")
        embeddings = self.embed_model.embed_documents(texts)
        
        # Prepare Qdrant points structure
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "metadata": chunk.metadata
                    }
                )
            )
            
        # Batch upload vectors to Qdrant
        print(f"Uploading points to Qdrant collection '{self.collection_name}'...")
        # Upload in batches of 100 points
        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i:i+batch_size]
            )
            
        print("Upload completed successfully.")
        return len(points)

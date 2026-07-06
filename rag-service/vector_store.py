import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from config import settings

class QdrantManager:
    def __init__(self, collection_name: str = "nova_policies"):
        self.collection_name = collection_name
        
        # Configure embedding model globally in LlamaIndex
        # Note: We read from config, falling back to mock or empty if not present for local tests
        api_key = settings.llm.openai_api_key or "mock_key"
        Settings.embed_model = OpenAIEmbedding(
            model=settings.llm.default_embedding_model,
            api_key=api_key
        )
        
        # Initialize Qdrant Client
        # If API key is empty/unset, connect without key (for local dev)
        client_kwargs = {
            "host": settings.qdrant.host,
            "port": settings.qdrant.port,
            "https": settings.qdrant.use_https,
        }
        if settings.qdrant.api_key:
            client_kwargs["api_key"] = settings.qdrant.api_key
            
        self.client = QdrantClient(**client_kwargs)

    def get_vector_store(self, embedding_dim: int = 1536) -> QdrantVectorStore:
        """
        Creates collection if not present and returns the QdrantVectorStore wrapper.
        Default dimension is 1536 (matching OpenAI text-embedding-3-small / text-embedding-ada-002).
        """
        # Check if collection exists
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
            
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name
        )

    def build_index(self, nodes) -> VectorStoreIndex:
        """
        Index nodes (chunks) into Qdrant VectorStoreIndex.
        """
        vector_store = self.get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context
        )
        print(f"Successfully indexed chunks into collection '{self.collection_name}'")
        return index

    def get_index(self) -> VectorStoreIndex:
        """
        Retrieve existing index.
        """
        vector_store = self.get_vector_store()
        return VectorStoreIndex.from_vector_store(vector_store=vector_store)

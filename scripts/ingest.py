import os
import sys

# Ensure parent directory and rag-service directory are in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rag_dir = os.path.join(root_dir, "rag-service")
sys.path.insert(0, root_dir)
sys.path.insert(0, rag_dir)

from loader import DocumentLoader
from chunker import DocumentChunker
from vector_store import QdrantManager

def run_ingestion():
    print("====================================================")
    print("bia RAG Pipeline Ingestion Utility")
    print("====================================================")
    
    docs_path = os.path.join(root_dir, "data", "documents")
    print(f"Loading documents from: {docs_path}")
    
    try:
        # 1. Load documents
        loader = DocumentLoader(directory_path=docs_path)
        documents = loader.load_documents()
        
        if not documents:
            print("No documents found in the specified path.")
            return
            
        # 2. Chunk documents
        print("Chunking documents...")
        chunker = DocumentChunker()
        nodes = chunker.split_documents(documents)
        
        # 3. Index to Qdrant
        print("Uploading vectors and indexing in Qdrant Vector Store...")
        manager = QdrantManager()
        manager.index_chunks(nodes)
        
        print(f"Successfully processed and indexed {len(nodes)} chunks.")
        print("Ingestion completed successfully.")
        
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_ingestion()

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rag_dir = os.path.join(root_dir, "rag-service")
sys.path.insert(0, root_dir)
sys.path.insert(0, rag_dir)

from loader import extract_custom_metadata, Document
from chunker import DocumentChunker
from retriever import HybridRetriever

class TestRAGPipeline(unittest.TestCase):
    
    def test_metadata_extraction(self):
        """
        Verify that extract_custom_metadata properly identifies filename and folder category.
        """
        # Formulate a mock file path matching our folder pattern: data/documents/hr/Leave_Policy.md
        mock_path = os.path.join("data", "documents", "hr", "Leave_Policy.md")
        metadata = extract_custom_metadata(mock_path)
        
        self.assertEqual(metadata["file_name"], "Leave_Policy.md")
        self.assertEqual(metadata["category"], "hr")
        self.assertEqual(metadata["department"], "hr")
        self.assertTrue("document_title" in metadata)
        
    def test_document_chunker(self):
        """
        Verify that DocumentChunker correctly splits a document into chunks.
        """
        doc = Document(
            text="# Leave Policy\nThis is paragraph one detailing leave guidelines.\n\n# Sick Leave\nThis is paragraph two detailing sick leaves.",
            metadata={"category": "hr", "file_name": "Leave_Policy.md"}
        )
        
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
        nodes = chunker.split_documents([doc])
        
        self.assertTrue(len(nodes) >= 1)
        for node in nodes:
            self.assertEqual(node.metadata["category"], "hr")
            self.assertEqual(node.metadata["file_name"], "Leave_Policy.md")
            self.assertTrue(len(node.text) > 0)

    @patch('retriever.Pinecone')
    @patch('retriever.OpenAIEmbeddings')
    def test_retriever_formatting(self, mock_embeddings, mock_pinecone_class):
        """
        Verify the HybridRetriever correctly formats retrieved node scores and metadata.
        """
        # Setup mock Pinecone client and index instances
        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone
        
        mock_index = MagicMock()
        mock_pinecone.Index.return_value = mock_index
        
        # Mock index query response
        mock_index.query.return_value = {
            "matches": [
                {
                    "id": "point-1",
                    "score": 0.85,
                    "values": [0.1] * 1536,
                    "metadata": {
                        "text": "Leave policy content details.",
                        "category": "hr",
                        "file_name": "Leave_Policy.md",
                        "chunk_index": 0
                    }
                }
            ]
        }
        
        # Create retriever
        retriever = HybridRetriever()
        
        # Mock flashrank rerank function
        mock_ranker = MagicMock()
        mock_ranker.rerank.return_value = [{"id": 0, "text": "Leave policy content details.", "score": 0.85, "meta": {"category": "hr"}}]
        
        with patch('retriever.get_ranker', return_value=mock_ranker), \
             patch('retriever.get_redis_client', return_value=None):
            results = retriever.retrieve("query about leave", category="hr")
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["text"], "Leave policy content details.")
            self.assertEqual(results[0]["score"], 0.85)
            self.assertEqual(results[0]["metadata"]["category"], "hr")

if __name__ == "__main__":
    unittest.main()

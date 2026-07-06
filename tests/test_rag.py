import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Configure sys.path for test imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
rag_dir = os.path.join(root_dir, "rag-service")
sys.path.insert(0, root_dir)
sys.path.insert(0, rag_dir)

from loader import extract_custom_metadata, DocumentLoader
from chunker import DocumentChunker
from retriever import HybridRetriever
from llama_index.core import Document
from llama_index.core.schema import TextNode

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
            self.assertTrue(len(node.get_content()) > 0)

    @patch('qdrant_client.QdrantClient')
    def test_retriever_formatting(self, mock_qdrant_client):
        """
        Verify the HybridRetriever correctly formats retrieved node scores and metadata.
        """
        # Create mock index and retriever
        mock_index = MagicMock()
        mock_llama_retriever = MagicMock()
        mock_index.as_retriever.return_value = mock_llama_retriever
        
        # Setup mock retrieval results
        mock_node = TextNode(text="Leave policy content details.", metadata={"category": "hr"})
        from llama_index.core.schema import NodeWithScore
        mock_results = [NodeWithScore(node=mock_node, score=0.85)]
        mock_llama_retriever.retrieve.return_value = mock_results
        
        retriever = HybridRetriever(mock_index)
        
        # Run retrieval mocking the flashrank reranker to avoid downloading weights in tests
        with patch('llama_index.postprocessor.flashrank.FlashrankRerank.postprocess_nodes') as mock_rerank:
            mock_rerank.return_value = mock_results
            results = retriever.retrieve("query about leave", category="hr")
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["text"], "Leave policy content details.")
            self.assertEqual(results[0]["score"], 0.85)
            self.assertEqual(results[0]["metadata"]["category"], "hr")

if __name__ == "__main__":
    unittest.main()

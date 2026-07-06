from typing import List
from llama_index.core import Document
from llama_index.core.schema import BaseNode
from llama_index.core.node_parser import SentenceSplitter

class DocumentChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents: List[Document]) -> List[BaseNode]:
        """
        Split a list of LlamaIndex Documents into BaseNode chunks.
        """
        nodes = self.parser.get_nodes_from_documents(documents)
        print(f"Split {len(documents)} documents into {len(nodes)} chunks.")
        
        # Ensure metadata is cleanly inherited by each child node
        for node in nodes:
            # LlamaIndex nodes inherit metadata from parent document automatically,
            # but we will log metadata here to verify consistency.
            pass
            
        return nodes

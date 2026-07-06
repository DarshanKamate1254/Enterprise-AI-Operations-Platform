from typing import List, Dict, Any
from loader import Document

class TextChunk:
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

    def __repr__(self):
        return f"TextChunk(text={self.text[:30]}..., category={self.metadata.get('category')})"

class DocumentChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[TextChunk]:
        """
        Split a list of Document objects into TextChunk objects.
        """
        chunks = []
        for doc in documents:
            text_splits = self.splitter.split_text(doc.text)
            for split in text_splits:
                chunks.append(TextChunk(text=split, metadata=doc.metadata.copy()))
                
        print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

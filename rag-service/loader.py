import os
from typing import List, Dict, Any
from llama_index.core import Document
from llama_index.core.readers import SimpleDirectoryReader

def extract_custom_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from file path and content structure.
    Inferred structure: data/documents/{category}/{filename}
    """
    normalized_path = os.path.normpath(file_path)
    parts = normalized_path.split(os.sep)
    
    # Defaults
    category = "unknown"
    filename = os.path.basename(file_path)
    
    # Attempt to extract category (parent folder of filename)
    if len(parts) >= 2:
        category = parts[-2]
    
    # Read the first line of the file to extract a clean title
    title = filename.replace("_", " ").replace(".md", "")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line.startswith("# "):
                title = first_line.replace("# ", "").split("-")[0].strip()
    except Exception:
        pass  # Fallback to file-based title
        
    return {
        "file_name": filename,
        "file_path": normalized_path,
        "category": category,
        "department": category,
        "document_title": title
    }

class DocumentLoader:
    def __init__(self, directory_path: str):
        self.directory_path = os.path.abspath(directory_path)

    def load_documents(self) -> List[Document]:
        """
        Recursively load documents from the specified directory.
        """
        if not os.path.exists(self.directory_path):
            raise FileNotFoundError(f"Directory {self.directory_path} does not exist.")
            
        reader = SimpleDirectoryReader(
            input_dir=self.directory_path,
            recursive=True,
            file_metadata=extract_custom_metadata,
            required_exts=[".md"]
        )
        
        documents = reader.load_data()
        print(f"Loaded {len(documents)} document pages from {self.directory_path}")
        return documents

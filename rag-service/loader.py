import os
from typing import List, Dict, Any

class Document:
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

    def __repr__(self):
        return f"Document(title={self.metadata.get('document_title')}, category={self.metadata.get('category')})"

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
            
        documents = []
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        meta = extract_custom_metadata(file_path)
                        documents.append(Document(text=text, metadata=meta))
                    except Exception as e:
                        print(f"Failed to load file {file_path}: {e}")
                        
        print(f"Loaded {len(documents)} documents from {self.directory_path}")
        return documents

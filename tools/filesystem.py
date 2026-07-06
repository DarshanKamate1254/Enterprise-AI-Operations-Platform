import os
from typing import List


class FilesystemTool:
    """
    Filesystem Tool for reading, writing, and listing files.
    Enforces directory sandboxing to prevent path traversal outside the designated root.
    """
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def _resolve_and_sandbox_path(self, relative_path: str) -> str:
        """
        Resolves relative_path against root_dir and verifies that it remains inside the sandbox.
        """
        resolved_path = os.path.abspath(os.path.join(self.root_dir, relative_path))
        
        # Check if the resolved path starts with the sandboxed root path
        if not resolved_path.startswith(self.root_dir):
            raise PermissionError(f"Access Denied: Path '{relative_path}' escapes the sandboxed root '{self.root_dir}'.")
            
        return resolved_path

    def read_file(self, relative_path: str) -> str:
        """
        Reads contents from a file within the sandbox.
        """
        target_path = self._resolve_and_sandbox_path(relative_path)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File '{relative_path}' does not exist inside sandbox.")
            
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Writes content to a file inside the sandbox (overwrites or creates).
        """
        target_path = self._resolve_and_sandbox_path(relative_path)
        
        # Ensure parent directories exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} characters to '{relative_path}'."

    def list_dir(self, relative_path: str = ".") -> List[str]:
        """
        Lists directory contents inside the sandbox.
        """
        target_path = self._resolve_and_sandbox_path(relative_path)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Directory '{relative_path}' does not exist.")
        if not os.path.isdir(target_path):
            raise NotADirectoryError(f"Path '{relative_path}' is not a directory.")
            
        return os.listdir(target_path)

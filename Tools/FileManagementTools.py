from langchain.tools import tool
from pathlib import Path

ROOT = Path("/Users/mac/Desktop/devFlowProjetsTestingPath").resolve()

def safe_path(path: str) -> Path:
    """
    Safely resolve a path to ensure it is within the ROOT directory.
    """
    file = (ROOT / path).resolve()
    if not str(file).startswith(str(ROOT)):
        raise ValueError(f"Attempted to access a path outside of the root directory: {file}")
    return file

@tool
def create_file(path: str, content: str) -> str:
    """
    Create a new file at the specified path with the given content.
    """
    file_path = safe_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File created at {file_path}"

@tool
def read_file(path: str) -> str:
    """
    Read the content of a file at the specified path.
    """
    file_path = safe_path(path)
    if not file_path.exists():
        return f"File not found: {file_path}"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
    @tool
    def overwrite_file(path: str, content: str) -> str:
        """
        Overwrite an existing file at the specified path with the given content.
        """
        file_path = safe_path(path)
        if not file_path.exists():
            return f"File not found: {file_path}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File overwritten at {file_path}"
    
    @tool
    def append_to_file(path: str, content: str) -> str:
        """
        Append content to an existing file at the specified path.
        """
        file_path = safe_path(path)
        if not file_path.exists():
            return f"File not found: {file_path}"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Content appended to file at {file_path}"
    
    @tool
    def delete_file(path: str) -> str:
        """
        Delete a file at the specified path.
        """
        file_path = safe_path(path)
        if not file_path.exists():
            return f"File not found: {file_path}"
        file_path.unlink()
        return f"File deleted at {file_path}"
    
    @tool
    def list_files(directory: str) -> str:
        """
        List all files in the specified directory.
        """
        dir_path = safe_path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return f"Directory not found: {dir_path}"
        files = [str(f) for f in dir_path.iterdir() if f.is_file()]
        return "\n".join(files) if files else "No files found."
    
    
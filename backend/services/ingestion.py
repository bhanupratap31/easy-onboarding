import os
from pathlib import Path
from typing import List, Dict, Any
import chromadb
import ollama

SUPPORTED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs",
    ".cpp", ".c", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
    ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".env.example",
}

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", ".next", "coverage", ".pytest_cache", "vendor",
}

CHUNK_SIZE = 60    # lines per chunk
CHUNK_OVERLAP = 10


def get_chroma_client() -> chromadb.HttpClient:
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8001"))
    return chromadb.HttpClient(host=host, port=port)


def _walk_repo(repo_path: str) -> List[Dict[str, Any]]:
    files = []
    root = Path(repo_path).resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix in SUPPORTED_EXTENSIONS:
                files.append({
                    "path": str(fpath),
                    "rel_path": str(fpath.relative_to(root)),
                })
    return files


def _chunk_file(file_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = []
    try:
        with open(file_info["path"], "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return chunks

    total = len(lines)
    start = 0
    while start < total:
        end = min(start + CHUNK_SIZE, total)
        content = "".join(lines[start:end]).strip()
        if content:
            chunks.append({
                "content": content,
                "file": file_info["rel_path"],
                "start_line": start + 1,
                "end_line": end,
            })
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _embed(text: str) -> List[float]:
    model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    client = ollama.Client(host=base_url)
    response = client.embed(model=model, input=text)
    return response["embeddings"][0]


def ingest_repo(repo_path: str, repo_id: str) -> Dict[str, Any]:
    files = _walk_repo(repo_path)
    if not files:
        return {"error": "No supported files found", "repo_id": repo_id}

    client = get_chroma_client()

    try:
        client.delete_collection(repo_id)
    except Exception:
        pass
    collection = client.create_collection(name=repo_id, metadata={"hnsw:space": "cosine"})

    ids, embeddings, documents, metadatas = [], [], [], []
    total_chunks = 0

    for file_info in files:
        for i, chunk in enumerate(_chunk_file(file_info)):
            try:
                emb = _embed(chunk["content"])
            except Exception:
                continue

            ids.append(f"{file_info['rel_path']}::{i}")
            embeddings.append(emb)
            documents.append(chunk["content"])
            metadatas.append({
                "file": chunk["file"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            })
            total_chunks += 1

            if len(ids) >= 50:
                collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
                ids, embeddings, documents, metadatas = [], [], [], []

    if ids:
        collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    return {
        "repo_id": repo_id,
        "files_indexed": len(files),
        "chunks_indexed": total_chunks,
    }


def list_repos() -> List[str]:
    client = get_chroma_client()
    return [c.name for c in client.list_collections()]

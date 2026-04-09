import os
from typing import List, Dict, Any
from services.ingestion import get_chroma_client, _embed


def query_chunks(repo_id: str, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Embed the question and retrieve the top-K most relevant code chunks."""
    client = get_chroma_client()

    try:
        collection = client.get_collection(repo_id)
    except Exception:
        return []

    question_embedding = _embed(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # cosine distance — lower is more similar; skip very low relevance
        if dist > 0.7:
            continue
        chunks.append({
            "content": doc,
            "file": meta["file"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "score": round(1 - dist, 4),
        })

    return chunks

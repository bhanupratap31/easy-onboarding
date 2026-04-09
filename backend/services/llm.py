import os
from typing import List, Dict, Any, Generator
import ollama

SYSTEM_PROMPT = """You are a senior software engineer helping a new developer understand a codebase.

When answering:
- Be concise and precise
- Always cite the exact file and line numbers from the context provided
- If you reference code, quote the relevant snippet
- If the answer is not in the provided context, say "I couldn't find relevant code for that — try re-indexing or rephrasing."
- Do NOT make up file paths or function names
"""


def _build_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"--- {chunk['file']} (lines {chunk['start_line']}-{chunk['end_line']}) ---\n{chunk['content']}"
        )
    context = "\n\n".join(context_parts)
    return f"{context}\n\nQuestion: {question}"


def stream_answer(question: str, chunks: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """Stream the LLM answer token by token."""
    if not chunks:
        yield "I couldn't find any relevant code for that question. Make sure the repo is indexed."
        return

    model = os.getenv("CHAT_MODEL", "deepseek-coder")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    client = ollama.Client(host=base_url)

    prompt = _build_prompt(question, chunks)

    stream = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token

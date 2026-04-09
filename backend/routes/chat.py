from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.retrieval import query_chunks
from services.llm import stream_answer
import json

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    repo_id: str


def _event_stream(question: str, repo_id: str):
    chunks = query_chunks(repo_id, question)

    if not chunks:
        yield f"data: {json.dumps({'type': 'error', 'text': 'No relevant code found. Make sure the repo is indexed.'})}\n\n"
        return

    # Send citations first
    citations = [
        {"file": c["file"], "start_line": c["start_line"], "end_line": c["end_line"], "score": c["score"]}
        for c in chunks
    ]
    yield f"data: {json.dumps({'type': 'citations', 'citations': citations})}\n\n"

    # Stream answer tokens
    for token in stream_answer(question, chunks):
        yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@router.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(
        _event_stream(req.question, req.repo_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

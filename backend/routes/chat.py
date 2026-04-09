# POST /chat — RAG retrieval + streaming LLM response
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    repo_id: str

@router.post("/chat")
def chat(req: ChatRequest):
    return {"answer": "not implemented", "citations": []}

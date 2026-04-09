# POST /ingest — walk, chunk, embed codebase
from fastapi import APIRouter

router = APIRouter()

@router.post("/ingest")
def ingest(repo_path: str):
    return {"status": "not implemented", "repo_path": repo_path}

@router.get("/repos")
def list_repos():
    return {"repos": []}

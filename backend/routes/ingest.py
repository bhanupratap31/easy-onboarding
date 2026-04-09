import os
import shutil
import tempfile
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ingestion import ingest_repo, list_repos

router = APIRouter()


class IngestRequest(BaseModel):
    repo_path: str        # local path OR a GitHub https URL
    repo_id: str          # collection name in ChromaDB


def _clone_and_ingest(github_url: str, repo_id: str) -> dict:
    import git
    tmp = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(github_url, tmp, depth=1)
        return ingest_repo(tmp, repo_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@router.post("/ingest")
def ingest(req: IngestRequest):
    if req.repo_path.startswith("http"):
        try:
            result = _clone_and_ingest(req.repo_path, req.repo_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Clone/ingest failed: {e}")
    else:
        if not os.path.isdir(req.repo_path):
            raise HTTPException(status_code=400, detail=f"Path not found: {req.repo_path}")
        result = ingest_repo(req.repo_path, req.repo_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/repos")
def get_repos():
    return {"repos": list_repos()}


@router.delete("/repos/{repo_id}")
def delete_repo(repo_id: str):
    from services.ingestion import get_chroma_client
    client = get_chroma_client()
    try:
        client.delete_collection(repo_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"deleted": repo_id}

from fastapi import FastAPI

app = FastAPI(title="Codebase Q&A")

@app.get("/health")
def health():
    return {"status": "ok"}

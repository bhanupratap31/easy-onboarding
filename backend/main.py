from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import ingest, chat

app = FastAPI(title="Codebase Q&A")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

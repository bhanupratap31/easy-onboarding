Ingests a codebase (local or GitHub repo)
Lets developers ask natural language questions: "How does auth work?", "Where is the payment processing logic?", "What does UserService do?"
Returns answers with exact file + line number citations

Tech Stack
Layer Tech Why
LLM Ollama + codellama or deepseek-coder Code-aware local LLM
Embeddings nomic-embed-text via Ollama Free, runs locally
Vector DB ChromaDB Simple, no server needed
RAG LangChain Chunking + retrieval
Backend FastAPI Streaming chat API
Frontend Next.js + shadcn/ui Chat UI
Deployment Docker Compose One command setup

Architecture

┌─────────────────────────────────┐
│ Next.js Chat UI │
│ (ask question → stream answer) │
└──────────────┬──────────────────┘
│ REST + SSE streaming
┌──────────────▼──────────────────┐
│ FastAPI Backend │
│ ┌─────────────────────────────┐ │
│ │ /ingest → parse + embed │ │
│ │ /chat → RAG + stream │ │
│ └────────┬────────────────────┘ │
└───────────┼─────────────────────┘
│
┌──────▼──────┐ ┌─────────────┐
│ ChromaDB │ │ Ollama │
│ (vectors) │────▶│ deepseek- │
│ + metadata │ │ coder + │
│ (file, line│ │ nomic-embed │
└─────────────┘ └─────────────┘

Flow:

POST /ingest?repo_path=./my-repo → walks files, chunks code, embeds, stores in Chroma
POST /chat with {question, repo_id} → retrieves top-K chunks → builds prompt → streams answer with citations

Day-Wise Plan (7 Days)
Day 1 — Infra & Ollama Setup
docker-compose.yml: Ollama + ChromaDB + FastAPI + Next.js
Pull models: ollama pull deepseek-coder + ollama pull nomic-embed-text
Verify Ollama API responds locally
FastAPI skeleton with /health endpoint

Day 2 — Code Ingestion Pipeline
Walk repo directory, filter by extension (.py, .ts, .js, .go, etc.)
Chunk files by function/class using LangChain's RecursiveCharacterTextSplitter with overlap
Store metadata: file_path, start_line, end_line, language
POST /ingest endpoint that takes a local path or GitHub URL (via gitpython)

Day 3 — Embedding & Vector Store
Embed each chunk with nomic-embed-text via Ollama
Store in ChromaDB collection keyed by repo name
GET /repos to list ingested repos
DELETE /repos/{repo_id} to re-index

Day 4 — RAG Q&A Backend
POST /chat — takes question + repo_id
Retrieve top-5 relevant chunks from ChromaDB
Build prompt: inject retrieved code snippets + question
Stream response from deepseek-coder via Ollama
Return citations: [{file, start_line, end_line, snippet}]

Day 5 — Chat UI
Single-page Next.js chat interface
Repo selector dropdown (from GET /repos)
Streaming answer display (SSE)
Citations panel below each answer showing clickable file:line refs
Code syntax highlighting on snippets (shiki)

Day 6 — Quality & UX
Prompt tuning: system prompt that forces the LLM to cite files
Re-ranking: filter out low-similarity chunks before sending to LLM
"No relevant code found" fallback message
Loading states, error handling

Day 7 — Polish & README
GitHub URL ingestion (clone → ingest → delete clone)
.env config for model names, chunk sizes
docker-compose up brings everything live

README with 3-step quickstart

Folder Structure

easy-onboarding/
├── backend/
│ ├── main.py
│ ├── routes/
│ │ ├── ingest.py # POST /ingest
│ │ └── chat.py # POST /chat (streaming)
│ ├── services/
│ │ ├── ingestion.py # walk, chunk, embed
│ │ ├── retrieval.py # chromadb query
│ │ └── llm.py # ollama streaming
│ └── requirements.txt
├── frontend/
│ └── app/
│ └── page.tsx # single chat page
├── docker-compose.yml
└── .env

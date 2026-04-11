<p align="center">
  <img src="assets/logo.png" alt="Easy Onboarding Logo" width="120" />
</p>

<h1 align="center">🧠 Easy Onboarding</h1>

<p align="center">
  <strong>AI-Powered Codebase Q&A — Ask questions, get answers with file + line citations.</strong>
</p>

<p align="center">
  <a href="https://github.com/yourusername/easy-onboarding/actions"><img src="https://img.shields.io/github/actions/workflow/status/yourusername/easy-onboarding/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status" /></a>
  <a href="https://github.com/yourusername/easy-onboarding/releases"><img src="https://img.shields.io/github/v/release/yourusername/easy-onboarding?style=flat-square&color=blue" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" /></a>
  <a href="https://github.com/yourusername/easy-onboarding/stargazers"><img src="https://img.shields.io/github/stars/yourusername/easy-onboarding?style=flat-square" alt="Stars" /></a>
  <a href="https://github.com/yourusername/easy-onboarding/issues"><img src="https://img.shields.io/github/issues/yourusername/easy-onboarding?style=flat-square" alt="Issues" /></a>
  <a href="https://github.com/yourusername/easy-onboarding/pulls"><img src="https://img.shields.io/github/issues-pr/yourusername/easy-onboarding?style=flat-square" alt="Pull Requests" /></a>
  <img src="https://img.shields.io/badge/docker-ready-blue?style=flat-square&logo=docker" alt="Docker" />
  <img src="https://img.shields.io/badge/runs%20100%25-locally-orange?style=flat-square" alt="Local" />
</p>

<p align="center">
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-features">Features</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 💡 What is Easy Onboarding?

Easy Onboarding lets developers **ingest any codebase** (local folder or GitHub URL) and **ask natural language questions** about it. The AI returns precise answers with **exact file and line number citations** — like having a senior engineer who's read every line of code.

> 💬 _"How does authentication work?"_
> 🤖 **→** The auth system uses JWT tokens issued in `src/auth/jwt.py:42-67`. Tokens are validated by middleware in `src/middleware/auth.py:15-30`...

**Zero API keys. Zero data leaves your machine. Fully local.**

---

## ✨ Features

| Feature                     | Description                                                     |
| --------------------------- | --------------------------------------------------------------- |
| 🗂️ **Multi-Repo Ingestion** | Ingest local folders or clone directly from GitHub URLs         |
| 💬 **Natural Language Q&A** | Ask questions like you'd ask a teammate — no special syntax     |
| 📍 **Exact Citations**      | Every answer references specific `file:line` ranges             |
| ⚡ **Streaming Responses**  | Real-time answer generation via Server-Sent Events              |
| 🔒 **Fully Local**          | Runs on Ollama — no external API calls, your code stays private |
| 🐳 **One Command Setup**    | `docker-compose up` and you're running                          |
| 🎨 **Clean Chat UI**        | Built with Next.js + shadcn/ui with syntax highlighting         |
| 🔄 **Re-indexing**          | Delete and re-ingest repos when code changes                    |

---

## 🎬 Demo

<p align="center">
  <img src="assets/demo.gif" alt="Easy Onboarding Demo" width="800" />
</p>

<!-- Replace with your actual demo GIF. Record with:
     - macOS: Kap (https://getkap.co)
     - Linux: Peek or OBS
     - Any OS: asciinema for terminal-only demos
     Recommended: 800px wide, < 10MB, 15-30 seconds -->

---

## 📸 Screenshots

<details>
<summary><strong>Click to expand screenshots</strong></summary>

<br/>

### Chat Interface

<p align="center">
  <img src="assets/screenshots/chat-ui.png" alt="Chat Interface" width="700" />
</p>

### Citation Panel

<p align="center">
  <img src="assets/screenshots/citations.png" alt="Citation Panel" width="700" />
</p>

### Repo Ingestion

<p align="center">
  <img src="assets/screenshots/ingestion.png" alt="Repo Ingestion" width="700" />
</p>

### Repo Selector

<p align="center">
  <img src="assets/screenshots/repo-selector.png" alt="Repo Selector" width="700" />
</p>

</details>

<!-- Replace placeholder paths with actual screenshots -->

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│        Next.js Chat UI          │
│  (ask question → stream answer) │
└──────────────┬──────────────────┘
               │ REST + SSE streaming
┌──────────────▼──────────────────┐
│        FastAPI Backend          │
│  ┌────────────────────────────┐ │
│  │ /ingest → parse + embed    │ │
│  │ /chat   → RAG + stream     │ │
│  └────────┬───────────────────┘ │
└───────────┼─────────────────────┘
            │
   ┌────────▼────────┐   ┌──────────────┐
   │    ChromaDB      │   │    Ollama     │
   │   (vectors +     │──▶│ qwen2.5-     │
   │    metadata)     │   │ coder:1.5b + │
   └──────────────────┘   │ nomic-embed  │
                          └──────────────┘
```

### How It Works

1. **Ingest** → `POST /api/ingest` walks the repo, splits code into 60-line overlapping chunks, embeds each with `nomic-embed-text`, and stores vectors + metadata (file path, line numbers) in ChromaDB.
2. **Ask** → `POST /api/chat` embeds your question, retrieves the top-5 most relevant chunks from ChromaDB, builds a prompt with the code context, and streams an answer from `qwen2.5-coder` via Ollama — with file:line citations.

---

## 🛠️ Tech Stack

| Layer          | Technology                                                         | Why                      |
| -------------- | ------------------------------------------------------------------ | ------------------------ |
| **LLM**        | [Ollama](https://ollama.ai) + `qwen2.5-coder:1.5b` (default)      | Code-aware local LLM     |
| **Embeddings** | `nomic-embed-text` via Ollama                                      | Free, runs locally       |
| **Vector DB**  | [ChromaDB](https://www.trychroma.com)                              | Simple, no server needed |
| **Backend**    | [FastAPI](https://fastapi.tiangolo.com) (Python 3.11)              | Streaming chat API       |
| **Frontend**   | [Next.js 15](https://nextjs.org) + Tailwind CSS                    | Clean chat UI            |
| **Deployment** | [Docker Compose](https://docs.docker.com/compose/) v2              | One command setup        |

---

## 🚀 Quickstart

### Prerequisites

| Requirement                                                    | Minimum                  |
| -------------------------------------------------------------- | ------------------------ |
| [Docker](https://docs.docker.com/get-docker/) + Docker Compose | v20+                     |
| RAM                                                            | 8 GB (16 GB recommended) |
| Disk                                                           | ~5 GB (for models)       |

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/easy-onboarding.git
cd easy-onboarding
```

### 2. Start everything

```bash
docker compose up --build
```

Wait until you see both of these lines:

```
backend-1   | INFO:     Application startup complete.
frontend-1  | ✓ Ready in ...
```

### 3. Pull the AI models (required — one time only)

Open a **new terminal** and run:

```bash
# Embedding model (~274 MB)
docker exec -it easy-onboarding-ollama-1 ollama pull nomic-embed-text

# Code LLM (~1.3 GB — fast on CPU)
docker exec -it easy-onboarding-ollama-1 ollama pull qwen2.5-coder:1.5b
```

Wait for `success` on both before using the app. Verify:

```bash
docker exec -it easy-onboarding-ollama-1 ollama list
```

### 4. Open the app

Navigate to **[http://localhost:3000](http://localhost:3000)**

---

## 📖 Usage

### Via the Chat UI

1. Open `http://localhost:3000`
2. Select a repo from the dropdown (or ingest a new one)
3. Type your question and hit Enter
4. Get streaming answers with clickable file:line citations

### Via the API

**Ingest a local codebase:**

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo", "repo_id": "my-repo"}'
```

**Ingest from GitHub:**

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "https://github.com/user/repo", "repo_id": "my-repo"}'
```

**List indexed repos:**

```bash
curl http://localhost:8000/api/repos
```

**Ask a question:**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How does authentication work?", "repo_id": "my-repo"}'
```

### Example Questions

| Question                                   | What You Get                                   |
| ------------------------------------------ | ---------------------------------------------- |
| _"How does auth work?"_                    | Explanation with JWT/session logic + file refs |
| _"Where is the payment processing logic?"_ | Pinpointed files and line ranges               |
| _"What does UserService do?"_              | Class breakdown with method-level citations    |
| _"How are database migrations handled?"_   | Migration strategy + config file locations     |
| _"Explain the API routing structure"_      | Route map with handler file references         |

---

## ⚙️ Configuration

All settings live in `.env`:

| Variable          | Default                  | Description                             |
| ----------------- | ------------------------ | --------------------------------------- |
| `CHAT_MODEL`      | `qwen2.5-coder:1.5b`     | Ollama model for code Q&A               |
| `EMBED_MODEL`     | `nomic-embed-text`       | Ollama model for embeddings             |
| `OLLAMA_BASE_URL` | `http://ollama:11434`    | Ollama server URL (inside Docker)       |
| `CHROMA_HOST`     | `chromadb`               | ChromaDB host (inside Docker)           |
| `CHROMA_PORT`     | `8000`                   | ChromaDB port (inside Docker)           |

**Chunk tuning** (edit `backend/services/ingestion.py`):

| Constant        | Default | Description                    |
| --------------- | ------- | ------------------------------ |
| `CHUNK_SIZE`    | `60`    | Lines per code chunk           |
| `CHUNK_OVERLAP` | `10`    | Overlapping lines between chunks |

### Supported File Extensions

`.py` `.ts` `.tsx` `.js` `.jsx` `.go` `.rs` `.java` `.rb` `.php` `.c` `.cpp` `.h` `.cs` `.swift` `.kt` `.scala` `.vue` `.svelte`

---

## 🧪 Development

### Run without Docker

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Ollama (must be running separately):**

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull qwen2.5-coder:1.5b
```

### Run tests

```bash
cd backend
pytest tests/ -v
```

---

## 🐛 Troubleshooting

<details>
<summary><strong>Cannot connect to Docker daemon</strong></summary>

Docker Desktop isn't running. Open it from Applications and wait for the whale icon in the menu bar to become steady, then re-run `docker compose up --build`.

</details>

<details>
<summary><strong>Models not found / 404 from Ollama</strong></summary>

Models must be pulled manually after starting the stack — they are not auto-downloaded. Run:

```bash
docker exec -it easy-onboarding-ollama-1 ollama pull nomic-embed-text
docker exec -it easy-onboarding-ollama-1 ollama pull qwen2.5-coder:1.5b
```

Verify they are loaded before using the app:

```bash
docker exec -it easy-onboarding-ollama-1 ollama list
```

</details>

<details>
<summary><strong>Build error: /app/public not found</strong></summary>

The `frontend/public/` directory must exist before building:

```bash
mkdir -p frontend/public
docker compose up --build frontend
```

</details>

<details>
<summary><strong>Out of memory errors</strong></summary>

`qwen2.5-coder:1.5b` needs ~2 GB RAM. If you're running low:

- Increase Docker's memory limit (Docker Desktop → Settings → Resources → Memory)
- Close other heavy applications

To use an even smaller model, pull it and update `.env`:

```bash
docker exec -it easy-onboarding-ollama-1 ollama pull tinyllama
# then in .env: CHAT_MODEL=tinyllama
docker compose restart backend
```

</details>

<details>
<summary><strong>ChromaDB connection refused</strong></summary>

Check that ChromaDB is healthy:

```bash
docker compose ps
curl http://localhost:8001/api/v1/heartbeat
```

</details>

<details>
<summary><strong>Ingestion is slow on large repos</strong></summary>

Large repos take time to chunk and embed. Tips:

- Target a subdirectory instead of the whole repo
- The first ingestion is slowest — re-indexing skips unchanged collections
- Reduce `CHUNK_SIZE` in `backend/services/ingestion.py` for faster (but less contextual) embeddings

</details>

<details>
<summary><strong>Indexing a local folder from your machine</strong></summary>

The backend container only sees paths mounted into it. Add a volume in `docker-compose.yml`:

```yaml
backend:
  volumes:
    - ./backend:/app
    - /path/to/your/project:/repos/my-project   # add this
```

Then use `/repos/my-project` as the repo path in the UI and rebuild:

```bash
docker compose up --build backend
```

</details>

<details>
<summary><strong>Swapping the LLM</strong></summary>

Any model from [ollama.com/library](https://ollama.com/library) works. Pull it, update `.env`, restart:

```bash
docker exec -it easy-onboarding-ollama-1 ollama pull deepseek-coder:6.7b
# in .env: CHAT_MODEL=deepseek-coder:6.7b
docker compose restart backend
```

**Recommended models by RAM:**

| RAM   | Model                    | Size   |
|-------|--------------------------|--------|
| 8 GB  | `qwen2.5-coder:1.5b`     | 1.3 GB |
| 16 GB | `deepseek-coder:6.7b`    | 3.8 GB |
| 32 GB | `deepseek-coder:33b`     | 19 GB  |

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repo
2. **Create** your feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## ⭐ Star History

<p align="center">
  <a href="https://star-history.com/#yourusername/easy-onboarding&Date">
    <img src="https://api.star-history.com/svg?repos=yourusername/easy-onboarding&type=Date" alt="Star History Chart" width="600" />
  </a>
</p>

---

---

<p align="center">
  Made with ❤️ for developers who hate reading unfamiliar codebases.
  <br/>
  <br/>
  <a href="https://github.com/yourusername/easy-onboarding">⭐ Star this repo</a> if you find it useful!
</p>

"use client";

import { useEffect, useRef, useState } from "react";

interface Citation {
  file: string;
  start_line: number;
  end_line: number;
  score: number;
}

interface Message {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
}

export default function Home() {
  const [repos, setRepos] = useState<string[]>([]);
  const [repoId, setRepoId] = useState("");
  const [repoPath, setRepoPath] = useState("");
  const [indexing, setIndexing] = useState(false);
  const [indexMsg, setIndexMsg] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/repos")
      .then((r) => r.json())
      .then((d) => setRepos(d.repos ?? []));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleIndex() {
    if (!repoPath || !repoId) return;
    setIndexing(true);
    setIndexMsg("Indexing… this may take a few minutes.");
    try {
      const res = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_path: repoPath, repo_id: repoId }),
      });
      const data = await res.json();
      if (!res.ok) {
        setIndexMsg(`Error: ${data.detail}`);
      } else {
        setIndexMsg(
          `Done — ${data.files_indexed} files, ${data.chunks_indexed} chunks indexed.`
        );
        setRepos((prev) => Array.from(new Set([...prev, repoId])));
      }
    } catch (e) {
      setIndexMsg("Network error during indexing.");
    } finally {
      setIndexing(false);
    }
  }

  async function handleAsk() {
    if (!question.trim() || !repoId || streaming) return;
    const q = question.trim();
    setQuestion("");
    setStreaming(true);

    // Add both messages atomically so the index is always last element
    let assistantIdx = -1;
    setMessages((prev) => {
      assistantIdx = prev.length + 1;
      return [
        ...prev,
        { role: "user" as const, text: q },
        { role: "assistant" as const, text: "", citations: [] },
      ];
    });

    // Wait one tick for state to flush before reading assistantIdx
    await new Promise((r) => setTimeout(r, 0));

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, repo_id: repoId }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          let payload: { type: string; text?: string; citations?: Citation[] };
          try { payload = JSON.parse(line.slice(6)); } catch { continue; }

          if (payload.type === "citations") {
            setMessages((prev) => {
              const updated = [...prev];
              updated[assistantIdx] = { ...updated[assistantIdx], citations: payload.citations };
              return updated;
            });
          } else if (payload.type === "token") {
            setMessages((prev) => {
              const updated = [...prev];
              updated[assistantIdx] = {
                ...updated[assistantIdx],
                text: updated[assistantIdx].text + payload.text,
              };
              return updated;
            });
          }
        }
      }
    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[assistantIdx] = {
          ...updated[assistantIdx],
          text: `Error: ${e instanceof Error ? e.message : "could not reach backend."}`,
        };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto px-4">
      {/* Header */}
      <header className="py-4 border-b border-gray-800">
        <h1 className="text-xl font-semibold text-white">Codebase Q&amp;A</h1>
      </header>

      {/* Index panel */}
      <div className="py-3 border-b border-gray-800 flex flex-wrap gap-2 items-end">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">Repo path / GitHub URL</label>
          <input
            className="bg-gray-800 text-sm px-3 py-1.5 rounded w-72 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="/path/to/repo or https://github.com/..."
            value={repoPath}
            onChange={(e) => setRepoPath(e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-400">Repo ID (collection name)</label>
          <input
            className="bg-gray-800 text-sm px-3 py-1.5 rounded w-40 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="my-repo"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
          />
        </div>
        <button
          onClick={handleIndex}
          disabled={indexing || !repoPath || !repoId}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-sm px-4 py-1.5 rounded"
        >
          {indexing ? "Indexing…" : "Index Repo"}
        </button>
        {indexMsg && <span className="text-xs text-gray-400">{indexMsg}</span>}
      </div>

      {/* Repo selector */}
      {repos.length > 0 && (
        <div className="py-2 border-b border-gray-800 flex items-center gap-2">
          <label className="text-xs text-gray-400">Ask about:</label>
          <select
            className="bg-gray-800 text-sm px-2 py-1 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
          >
            <option value="">— select repo —</option>
            {repos.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-6">
        {messages.length === 0 && (
          <p className="text-gray-500 text-sm text-center mt-16">
            Index a repo above, then ask anything about the code.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === "user" ? "flex justify-end" : ""}>
            {msg.role === "user" ? (
              <div className="bg-blue-700 text-white text-sm px-4 py-2 rounded-2xl max-w-lg">
                {msg.text}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="bg-gray-800 text-sm px-4 py-3 rounded-2xl whitespace-pre-wrap leading-relaxed">
                  {msg.text || <span className="animate-pulse text-gray-500">thinking…</span>}
                </div>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-xs text-gray-500 font-medium">Sources</p>
                    {msg.citations.map((c, ci) => (
                      <div
                        key={ci}
                        className="text-xs bg-gray-900 border border-gray-700 rounded px-3 py-1.5 font-mono flex justify-between"
                      >
                        <span className="text-blue-400">{c.file}</span>
                        <span className="text-gray-500">
                          lines {c.start_line}–{c.end_line}
                          &nbsp;·&nbsp;score {c.score}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="py-3 border-t border-gray-800 flex gap-2">
        <input
          className="flex-1 bg-gray-800 text-sm px-4 py-2 rounded-xl focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder={repoId ? `Ask about ${repoId}…` : "Select a repo first"}
          value={question}
          disabled={!repoId || streaming}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
        />
        <button
          onClick={handleAsk}
          disabled={!repoId || !question.trim() || streaming}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 px-4 py-2 rounded-xl text-sm"
        >
          {streaming ? "…" : "Ask"}
        </button>
      </div>
    </div>
  );
}

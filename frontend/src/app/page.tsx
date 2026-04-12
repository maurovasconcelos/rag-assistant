"use client";

import { useState, useRef, useEffect } from "react";

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  sources?: string[];
  refined_query?: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "ai",
      content: "Olá! Sou seu Assistente RAG Corporativo protegido pela LGPD. Como posso ajudar com os documentos da empresa hoje?",
    },
  ]);
  const [inputStr, setInputStr] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Ingestion states
  const [docTitle, setDocTitle] = useState("");
  const [docContent, setDocContent] = useState("");
  const [toastMsg, setToastMsg] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputStr.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputStr,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputStr("");
    setIsLoading(true);

    try {
      const res = await fetch(`http://127.0.0.1:8000/ask/?query=${encodeURIComponent(userMsg.content)}`);
      if (!res.ok) throw new Error("Erro na API RAG");

      const data = await res.json();

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: data.answer,
        sources: data.sources,
        refined_query: data.refined_query,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Oops, tive um problema ao conectar com o servidor RAG.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docTitle.trim() || !docContent.trim()) return;

    try {
      const res = await fetch("http://127.0.0.1:8000/documents/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: docTitle,
          content: docContent,
        }),
      });

      if (!res.ok) throw new Error("Erro ao enviar documento");

      setDocTitle("");
      setDocContent("");
      showToast("Documento seguro e vetorizado!");
    } catch (error) {
      showToast("Erro ao vetorizar documento");
    }
  };

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(""), 3000);
  };

  return (
    <div className="app-wrapper">
      {toastMsg && <div className="toast">{toastMsg}</div>}

      <header className="header">
        <h1>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--accent-color)" }}>
            <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>
            <path d="M12 12 2.1 7.1"></path>
            <path d="m12 12 9.9 4.9"></path>
          </svg>
          Assistente RAG Corporativo
        </h1>
        <span className="header-badge">LGPD Compliant</span>
      </header>

      <div className="main-content">
        <aside className="sidebar">
          <div className="sidebar-header">Adicionar Conhecimento</div>
          <form className="ingestion-form" onSubmit={handleCreateDocument}>
            <input
              type="text"
              className="input-style"
              placeholder="Título do Documento"
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
              required
            />
            <textarea
              className="input-style"
              placeholder="Cole o conteúdo sigiloso aqui (a IA mascarará os CPFs e Nomes antes de salvar no banco)..."
              value={docContent}
              onChange={(e) => setDocContent(e.target.value)}
              required
            />
            <button type="submit" className="btn-primary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              Ingerir no PgVector
            </button>
          </form>
        </aside>

        <main className="chat-area">
          <div className="messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                <div className="message-bubble">{msg.content}</div>
                {msg.role === "ai" && msg.sources && msg.sources.length > 0 && (
                  <div className="sources-box">
                    {msg.refined_query && (
                      <div style={{ marginBottom: "8px", opacity: 0.8 }}>
                        <strong>Refiner:</strong> <em>{msg.refined_query}</em>
                      </div>
                    )}
                    <h4>Fontes Utilizadas:</h4>
                    <ul>
                      {msg.sources.map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input-container" onSubmit={handleSend}>
            <div className="chat-input-wrapper">
              <input
                type="text"
                className="chat-input"
                placeholder="Pergunte sobre os documentos armazenados..."
                value={inputStr}
                onChange={(e) => setInputStr(e.target.value)}
                autoFocus
              />
              <button type="submit" className="send-btn" disabled={!inputStr.trim() || isLoading}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}

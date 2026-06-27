import { useState, useRef, useCallback } from "react";
import Editor from "@monaco-editor/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Loader2, Play, FileCode2, BookOpen, Zap, FileText, Github, RotateCcw } from "lucide-react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const MODES = [
  { id: "review",    label: "Code Review",    icon: FileCode2, color: "#6366f1", desc: "Bugs, style, best practices" },
  { id: "explain",   label: "Explain",        icon: BookOpen,  color: "#10b981", desc: "Understand what it does" },
  { id: "optimize",  label: "Optimize",       icon: Zap,       color: "#f59e0b", desc: "Performance improvements" },
  { id: "docstring", label: "Add Docstrings", icon: FileText,  color: "#3b82f6", desc: "Auto-generate documentation" },
];

const EXAMPLE_CODE = {
  python: `def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                if arr[i] not in duplicates:
                    duplicates.append(arr[i])
    return duplicates

result = find_duplicates([1, 2, 3, 2, 4, 3, 5])
print(result)`,
  javascript: `async function fetchUserData(userId) {
  const response = await fetch('/api/users/' + userId)
  const data = response.json()
  console.log(data)
  return data
}

function processUsers(users) {
  var result = []
  for (var i = 0; i < users.length; i++) {
    if (users[i].age > 18) {
      result.push(users[i])
    }
  }
  return result
}`,
  java: `public class BubbleSort {
    public static void sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n-1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
    }
}`,
};

const LANGUAGES = ["python", "javascript", "typescript", "java", "cpp", "go", "rust", "sql"];

export default function App() {
  const [code, setCode]           = useState(EXAMPLE_CODE.python);
  const [language, setLanguage]   = useState("python");
  const [mode, setMode]           = useState("review");
  const [output, setOutput]       = useState("");
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");
  const [tokensIn, setTokensIn]   = useState(0);
  const abortRef                  = useRef(null);

  const handleLanguageChange = useCallback((lang) => {
    setLanguage(lang);
    if (EXAMPLE_CODE[lang]) setCode(EXAMPLE_CODE[lang]);
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!code.trim() || loading) return;
    setOutput("");
    setError("");
    setLoading(true);
    setTokensIn(code.length);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_URL}/review/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language, mode }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Request failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.chunk) setOutput(prev => prev + data.chunk);
            if (data.error) setError(data.error);
          } catch {}
        }
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message || "Something went wrong. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  }, [code, language, mode, loading]);

  const handleStop = () => {
    abortRef.current?.abort();
    setLoading(false);
  };

  const selectedMode = MODES.find(m => m.id === mode);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">CodeSense</span>
            <span className="logo-badge">AI</span>
          </div>
          <span className="header-tagline">Real-time AI code analysis</span>
        </div>
        <a
          href="https://github.com/Sandy-SHM/codesense"
          target="_blank"
          rel="noreferrer"
          className="github-link"
        >
          <Github size={16} />
          <span>GitHub</span>
        </a>
      </header>

      {/* Mode selector */}
      <div className="mode-bar">
        {MODES.map(m => {
          const Icon = m.icon;
          return (
            <button
              key={m.id}
              className={`mode-btn ${mode === m.id ? "active" : ""}`}
              style={mode === m.id ? { "--mode-color": m.color } : {}}
              onClick={() => setMode(m.id)}
            >
              <Icon size={15} />
              <span className="mode-label">{m.label}</span>
              <span className="mode-desc">{m.desc}</span>
            </button>
          );
        })}
      </div>

      {/* Main layout */}
      <main className="main">
        {/* Left: Editor */}
        <section className="editor-panel">
          <div className="panel-header">
            <span className="panel-title">Input Code</span>
            <div className="panel-controls">
              <select
                className="lang-select"
                value={language}
                onChange={e => handleLanguageChange(e.target.value)}
              >
                {LANGUAGES.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              <button
                className="icon-btn"
                title="Reset to example"
                onClick={() => {
                  setCode(EXAMPLE_CODE[language] || "");
                  setOutput("");
                  setError("");
                }}
              >
                <RotateCcw size={14} />
              </button>
            </div>
          </div>

          <div className="editor-wrap">
            <Editor
              height="100%"
              language={language === "cpp" ? "cpp" : language}
              value={code}
              onChange={val => setCode(val || "")}
              theme="vs-dark"
              options={{
                fontSize: 13,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                wordWrap: "on",
                lineNumbers: "on",
                renderLineHighlight: "all",
                padding: { top: 12, bottom: 12 },
                smoothScrolling: true,
              }}
            />
          </div>

          <div className="editor-footer">
            <span className="char-count">{code.length.toLocaleString()} chars</span>
            {loading ? (
              <button className="run-btn stop" onClick={handleStop}>
                <Loader2 size={15} className="spin" />
                Stop
              </button>
            ) : (
              <button
                className="run-btn"
                onClick={handleAnalyze}
                disabled={!code.trim()}
                style={{ "--mode-color": selectedMode?.color }}
              >
                <Play size={15} />
                Analyze
              </button>
            )}
          </div>
        </section>

        {/* Right: Output */}
        <section className="output-panel">
          <div className="panel-header">
            <span className="panel-title">
              {selectedMode?.label} Output
              {loading && <span className="streaming-dot" />}
            </span>
            {output && (
              <button
                className="icon-btn"
                title="Copy output"
                onClick={() => navigator.clipboard.writeText(output)}
              >
                Copy
              </button>
            )}
          </div>

          <div className="output-content">
            {error && (
              <div className="error-box">
                ⚠️ {error}
              </div>
            )}

            {!output && !loading && !error && (
              <div className="placeholder">
                <div className="placeholder-icon">⚡</div>
                <p>Paste your code on the left and click <strong>Analyze</strong></p>
                <p className="placeholder-sub">Powered by Llama 3.3 70B via Groq · RAG-enhanced context</p>
              </div>
            )}

            {output && (
              <div className="markdown-wrap">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {output}
                </ReactMarkdown>
                {loading && <span className="cursor-blink">▋</span>}
              </div>
            )}

            {loading && !output && (
              <div className="loading-state">
                <Loader2 size={24} className="spin" />
                <span>Analyzing with Llama 3.3 70B...</span>
              </div>
            )}
          </div>

          {output && (
            <div className="output-footer">
              <span>~{tokensIn} input chars · RAG context active · Llama 3.3 70B</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

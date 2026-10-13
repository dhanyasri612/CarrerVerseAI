import React, { useState } from "react";
import {
  X,
  BookOpen,
  Sparkles,
  HelpCircle,
  Hammer,
  AlertTriangle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Copy,
  Check,
} from "lucide-react";

// Curated high-yield skill preparation data
const SKILL_GUIDES = {
  react: {
    title: "React",
    category: "Frontend Engineering",
    importance: "Core building block of modern web interfaces, component architecture, and state management in production applications.",
    coreConcepts: [
      "Virtual DOM & Reconciliation (Fiber architecture, diffing algorithm)",
      "Hooks & Lifecycle (useEffect dependency arrays, useMemo, useCallback for memoization)",
      "State Management (Local vs Context API vs Redux/Zustand, server cache via TanStack Query)",
      "Component Composition vs Inheritance (Higher-Order Components, Render Props)",
      "Performance Optimization (Code-splitting with React.lazy, avoiding re-renders with React.memo)",
    ],
    interviewQuestions: [
      {
        q: "How does the React Fiber reconciler work, and why was it introduced?",
        answer: "React Fiber rewritten the core reconciliation engine to introduce incremental rendering. It splits work into small chunks called fibers and spreads them across multiple frames using requestIdleCallback/MessageChannel. This prevents long renders from blocking the main thread.",
        keywords: ["Incremental rendering", "Fiber nodes", "Concurrent React", "Scheduler", "Time-slicing"],
      },
      {
        q: "What is the true purpose of useMemo and useCallback? When do they harm performance?",
        answer: "useMemo caches the result of a computation, while useCallback caches a function reference between renders. They add overhead (memory allocation and dependency comparisons) and should only be used when passing callbacks to memoized children (React.memo) or when computations are genuinely expensive.",
        keywords: ["Referential equality", "React.memo", "Memory overhead", "Dependency array"],
      },
      {
        q: "Explain useEffect cleanup functions and explain when they execute.",
        answer: "The cleanup function runs before the component unmounts and before the effect re-runs on dependency changes. It is essential for clearing timeouts, aborting fetch requests (AbortController), and unsubscribing from event sockets to prevent memory leaks.",
        keywords: ["Memory leak prevention", "AbortController", "Unmount lifecycle"],
      },
      {
        q: "What is the difference between controlled and uncontrolled components?",
        answer: "Controlled components have form data handled by React state, giving real-time validation and sync. Uncontrolled components store state in the DOM using refs (useRef), which can be faster for simple forms or file inputs.",
        keywords: ["DOM-driven vs state-driven", "useRef", "SyntheticEvent"],
      },
    ],
    codingTask: "Implement a custom hook `useDebounce(value, delay)` that handles rapid user input for an autocomplete search bar without triggering redundant API calls.",
    pitfalls: [
      "Mutating state directly instead of creating new object references.",
      "Leaving empty or stale dependency arrays in useEffect/useCallback.",
      "Overusing Context API for fast-changing states, causing entire subtree re-renders.",
    ],
    resources: [
      { name: "React Official Docs (react.dev)", url: "https://react.dev" },
      { name: "Overreacted by Dan Abramov", url: "https://overreacted.io" },
    ],
  },
  python: {
    title: "Python",
    category: "Backend & Systems",
    importance: "Dominant language for backend APIs (FastAPI/Django), data science, AI pipelines, and algorithmic interviews.",
    coreConcepts: [
      "GIL (Global Interpreter Lock) and its impact on multi-threading vs multiprocessing",
      "Memory Management (Reference counting and cyclic garbage collector)",
      "Generators and Iterators (`yield`, `__iter__`, `__next__`) for memory efficiency",
      "Decorators and Metaclasses (Function wrappers, functools.wraps)",
      "Asyncio & Event Loops (Cooperative multitasking, `async`/`await`)",
    ],
    interviewQuestions: [
      {
        q: "Explain Python's GIL and how it affects CPU-bound vs I/O-bound tasks.",
        answer: "The GIL is a mutex preventing multiple native threads from executing Python bytecodes simultaneously. For CPU-bound tasks, threading adds overhead; multiprocessing or native C extensions should be used. For I/O-bound tasks (network, disk), threads release the GIL during wait states, making threading or asyncio highly effective.",
        keywords: ["GIL mutex", "CPython", "Multiprocessing vs Threading", "Asyncio event loop"],
      },
      {
        q: "What is the difference between `is` and `==` in Python?",
        answer: "`==` checks for equality of values by invoking `__eq__`, whereas `is` checks for object identity (exact same memory address via `id()`). Small integers and interned strings may share references in CPython.",
        keywords: ["Value equality vs identity", "id() memory pointer", "Integer interning"],
      },
      {
        q: "How do Python generators optimize memory when processing huge datasets?",
        answer: "Generators use lazy evaluation via the `yield` statement. Instead of constructing entire lists in memory, they yield items one at a time and suspend state between iterations, keeping memory footprint at O(1).",
        keywords: ["Lazy evaluation", "yield statement", "Iterator protocol", "O(1) memory"],
      },
    ],
    codingTask: "Write a decorator `@rate_limited(max_per_second)` that restricts a function to be executed no more than N times per second using `time.monotonic()`.",
    pitfalls: [
      "Using mutable default arguments (like `def func(lst=[])`) which persist across invocations.",
      "Catching bare `except:` instead of specific exception types, swallowing KeyboardInterrupt.",
    ],
    resources: [
      { name: "Python 3 Official Documentation", url: "https://docs.python.org/3/" },
      { name: "Real Python Tutorials", url: "https://realpython.com/" },
    ],
  },
  fastapi: {
    title: "FastAPI",
    category: "Backend Engineering",
    importance: "Modern, high-performance web framework for building REST & async APIs with Python, powered by Starlette and Pydantic.",
    coreConcepts: [
      "Asynchronous request handlers with ASGI (Uvicorn / Starlette)",
      "Pydantic schema validation and automatic OpenAPI (Swagger) spec generation",
      "Dependency Injection system (`Depends()`) for DB sessions, auth, and permissions",
      "BackgroundTasks for non-blocking post-response actions",
      "Middleware pipeline (CORS, timing, logging)",
    ],
    interviewQuestions: [
      {
        q: "How does FastAPI achieve near-Node.js/Go performance in Python?",
        answer: "FastAPI is built on Starlette and Pydantic, running atop the ASGI standard using Uvicorn (uvloop). By leveraging Python's async/await concurrency model for non-blocking I/O, it handles thousands of concurrent requests on a single worker.",
        keywords: ["ASGI", "Uvicorn uvloop", "Non-blocking I/O", "Pydantic v2 Rust core"],
      },
      {
        q: "How does FastAPI's dependency injection (`Depends`) improve code architecture?",
        answer: "Dependency injection in FastAPI provides clean separation of concerns, automated resource cleanup (using `yield` for DB sessions), seamless test mocking, and shared logic across endpoints without global singletons.",
        keywords: ["Depends()", "Yield cleanup", "Mocking & testability", "Session scoping"],
      },
    ],
    codingTask: "Create a secured FastAPI route with JWT bearer auth, Pydantic input validation, and a custom dependency injecting a database session.",
    pitfalls: [
      "Defining CPU-heavy blocking functions inside `async def` without threadpool offloading (`run_in_threadpool`).",
    ],
    resources: [{ name: "FastAPI Documentation", url: "https://fastapi.tiangolo.com/" }],
  },
  docker: {
    title: "Docker & Containerization",
    category: "DevOps & Cloud",
    importance: "Standard for packaging reproducible runtime environments, multi-stage builds, and microservices orchestration.",
    coreConcepts: [
      "Images vs Containers (Layer caching, UnionFS, copy-on-write)",
      "Multi-stage Dockerfiles for tiny production artifacts",
      "Networking (bridge, host, overlay) and port mapping",
      "Volumes and persistent storage mounts",
      "Security (non-root users, vulnerability scanning)",
    ],
    interviewQuestions: [
      {
        q: "Why are multi-stage builds essential for production Docker containers?",
        answer: "Multi-stage builds allow using heavy build dependencies (compilers, npm build, SDKs) in intermediate stages, then copying only the compiled artifacts into a lightweight distroless or alpine runtime image, drastically reducing attack surface and image size.",
        keywords: ["Layer caching", "Alpine/Distroless", "Attack surface minimization"],
      },
    ],
    codingTask: "Write an optimized multi-stage Dockerfile for a React or Node app with layer caching and a non-root user.",
    pitfalls: ["Running containers as root in production.", "Not using `.dockerignore`, bloating build context."],
    resources: [{ name: "Docker Official Docs", url: "https://docs.docker.com/" }],
  },
};

export default function SkillPrepGuideModal({ skillName, onClose }) {
  const [copied, setCopied] = useState(false);
  const [openIndex, setOpenIndex] = useState(0);

  if (!skillName) return null;

  const key = String(skillName).toLowerCase().replace(/[^a-z0-9]/g, "");
  const matched = SKILL_GUIDES[key] || {
    title: skillName,
    category: "Technical Competency",
    importance: `Essential industry standard skill evaluated in modern software engineering and systems design rounds.`,
    coreConcepts: [
      `Fundamental architectures and foundational standards of ${skillName}`,
      `Production implementation best practices, reliability, and error handling`,
      `Performance tuning, latency optimization, and memory efficiency`,
      `Security considerations, threat mitigation, and dependency integrity`,
    ],
    interviewQuestions: [
      {
        q: `What are the core architectural tradeoffs when implementing ${skillName} in production?`,
        answer: `When scaling ${skillName}, teams evaluate latency vs consistency, memory consumption, maintainability, and operational complexity. High-performing systems isolate responsibilities and establish robust observability.`,
        keywords: ["Tradeoffs", "Production scaling", "Observability", "Maintainability"],
      },
      {
        q: `How do you diagnose and debug performance bottlenecks related to ${skillName}?`,
        answer: `Use profiling tools, inspect execution traces, identify I/O vs CPU bottlenecks, optimize query/data pipeline structures, and verify resource contention limits.`,
        keywords: ["Profiling", "Trace analysis", "Bottleneck mitigation"],
      },
    ],
    codingTask: `Design and implement a clean, production-ready module demonstrating idiomatic usage of ${skillName} with unit tests and error handling.`,
    pitfalls: [
      `Neglecting edge cases and unhandled exception paths.`,
      `Overcomplicating the design without profiling first.`,
    ],
    resources: [
      { name: `${skillName} Official Documentation`, url: `https://duckduckgo.com/?q=${encodeURIComponent(skillName + " official documentation")}` },
    ],
  };

  const copyGuide = () => {
    const text = `# ${matched.title} Preparation Guide\n\n${matched.importance}\n\n## Core Concepts:\n${matched.coreConcepts.map((c) => `- ${c}`).join("\n")}\n\n## Top Questions:\n${matched.interviewQuestions.map((q, i) => `${i + 1}. ${q.q}\nAnswer: ${q.answer}`).join("\n\n")}`;
    navigator.clipboard?.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "rgba(15, 23, 42, 0.75)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1.5rem",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          width: "100%",
          maxWidth: "760px",
          maxHeight: "90vh",
          borderRadius: "16px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: "1.25rem 1.75rem",
            borderBottom: "1px solid #e2e8f0",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: "#f8fafc",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: "10px",
                background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#1e293b",
                fontWeight: 800,
              }}
            >
              <BookOpen size={20} />
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {matched.category} • Skill Mastery Guide
              </div>
              <h2 style={{ fontSize: "1.35rem", fontWeight: 700, color: "#0f172a", margin: 0 }}>
                {matched.title}
              </h2>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              type="button"
              onClick={copyGuide}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "6px",
                border: "1px solid #cbd5e1",
                background: "#ffffff",
                fontSize: "0.78rem",
                color: "#475569",
                cursor: "pointer",
              }}
            >
              {copied ? <Check size={13} color="#16a34a" /> : <Copy size={13} />}
              {copied ? "Copied" : "Copy Guide"}
            </button>
            <button
              type="button"
              onClick={onClose}
              style={{
                width: 32,
                height: 32,
                borderRadius: "8px",
                border: "none",
                background: "#e2e8f0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                color: "#475569",
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div style={{ padding: "1.75rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Significance */}
          <div style={{ background: "#f8fafc", padding: "1rem 1.25rem", borderRadius: "10px", borderLeft: "4px solid #f59e0b" }}>
            <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#b45309", marginBottom: "4px" }}>
              WHY INTERVIEWERS CARE ABOUT THIS
            </div>
            <p style={{ margin: 0, fontSize: "0.92rem", color: "#334155", lineHeight: 1.55 }}>
              {matched.importance}
            </p>
          </div>

          {/* Core Concepts */}
          <div>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "8px", marginBottom: "0.75rem" }}>
              <Sparkles size={16} color="#f59e0b" /> Core Concepts & Architecture Cheat Sheet
            </h3>
            <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "6px" }}>
              {matched.coreConcepts.map((c, i) => (
                <li key={i} style={{ fontSize: "0.9rem", color: "#334155", lineHeight: 1.5 }}>
                  {c}
                </li>
              ))}
            </ul>
          </div>

          {/* High-Yield Questions Accordion */}
          <div>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: "8px", marginBottom: "0.75rem" }}>
              <HelpCircle size={16} color="#2563eb" /> Top High-Yield Technical Interview Questions
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {matched.interviewQuestions.map((q, i) => {
                const isOpen = openIndex === i;
                return (
                  <div
                    key={i}
                    style={{
                      border: "1px solid #e2e8f0",
                      borderRadius: "10px",
                      overflow: "hidden",
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => setOpenIndex(isOpen ? -1 : i)}
                      style={{
                        width: "100%",
                        padding: "12px 16px",
                        background: isOpen ? "#f8fafc" : "#ffffff",
                        border: "none",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        textAlign: "left",
                        cursor: "pointer",
                      }}
                    >
                      <strong style={{ fontSize: "0.9rem", color: "#0f172a" }}>
                        Q{i + 1}: {q.q}
                      </strong>
                      {isOpen ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
                    </button>
                    {isOpen && (
                      <div style={{ padding: "14px 16px", background: "#f8fafc", borderTop: "1px solid #e2e8f0" }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#16a34a", marginBottom: "6px" }}>
                          RECOMMENDED MODEL ANSWER
                        </div>
                        <p style={{ margin: "0 0 10px 0", fontSize: "0.88rem", color: "#334155", lineHeight: 1.6 }}>
                          {q.answer}
                        </p>
                        {q.keywords && (
                          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                            {q.keywords.map((kw, ki) => (
                              <span
                                key={ki}
                                style={{
                                  fontSize: "0.74rem",
                                  padding: "2px 8px",
                                  borderRadius: "4px",
                                  background: "#e2e8f0",
                                  color: "#334155",
                                }}
                              >
                                #{kw}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Practical Hands-On Task */}
          {matched.codingTask && (
            <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", padding: "1rem 1.25rem", borderRadius: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#047857", fontWeight: 700, fontSize: "0.85rem", marginBottom: "4px" }}>
                <Hammer size={16} /> 30-MINUTE PRACTICAL MICRO-CHALLENGE
              </div>
              <p style={{ margin: 0, fontSize: "0.88rem", color: "#065f46", lineHeight: 1.5 }}>
                {matched.codingTask}
              </p>
            </div>
          )}

          {/* Common Pitfalls */}
          {matched.pitfalls && (
            <div>
              <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "#dc2626", display: "flex", alignItems: "center", gap: "6px", margin: "0 0 6px 0" }}>
                <AlertTriangle size={15} /> Common Candidate Pitfalls to Avoid
              </h4>
              <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "4px" }}>
                {matched.pitfalls.map((p, i) => (
                  <li key={i} style={{ fontSize: "0.86rem", color: "#64748b" }}>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  Clock,
  Maximize2,
  Minimize2,
  ShieldCheck,
  Play,
  RotateCcw,
  Terminal,
  FileText,
  ChevronDown,
  ChevronUp,
  Mic,
  MicOff,
  Video,
  VideoOff,
  PhoneOff,
  Sliders,
  Send,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  GitBranch,
  Layers,
  Code2,
  MessageSquare,
  Check,
  Award,
  Zap,
  Camera,
  Bot,
  Globe,
  Loader2,
  AlertTriangle,
  X,
  Volume2,
  VolumeX,
} from "lucide-react";
import CyraRobotAvatar from "./CyraRobotAvatar";
import { chatWithCyra } from "../services/careerService";

export default function LiveInterviewStudio({
  role = "Software Engineer (SDE)",
  candidateName = "Dhanyasri K",
  candidateAvatar = "",
  timeLeft = 5722, // e.g. 01:35:22
  isFullscreen = false,
  toggleFullscreen = () => {},
  handleCompleteInterview = () => {},
  handleResetToSetup = () => {},
  selectedLanguage = "en",
  setSelectedLanguage = () => {},
  supportedLanguages = [],
  handleLanguageChange = null,
  handleSpeakAgain = null,
  voiceStatus = null,
  micStatus = null,
  isGeneratingQuestion = false,
  currentQuestion = null,
  currentQIndex = 1,
  parsedQ = null,
  selectedDomainKey = "dsa_py",
  handleDomainChange = () => {},
  codeSnippet = "",
  setCodeSnippet = () => {},
  codeLines = [],
  handleRunCode = () => {},
  handleResetTemplate = () => {},
  isRunningCode = false,
  executionOutput = null,
  showTerminal = false,
  setShowTerminal = () => {},
  isAgentSpeaking = false,
  spokenSubtitle = "",
  speakText = () => {},
  cameraActive = false,
  startCamera = () => {},
  stopCamera = () => {},
  videoRef = null,
  showHints = true,
  setShowHints = () => {},
  showCaptions = true,
  setShowCaptions = () => {},
  setShowSettingsModal = () => {},
  activeQuestionTab = "constraints",
  setActiveQuestionTab = () => {},
  candidateNotes = "",
  setCandidateNotes = () => {},
  candidateAnswer = "",
  setCandidateAnswer = () => {},
  handleAnswerSubmit = () => {},
  handleNextQuestion = () => {},
  loading = false,
  isListening = false,
  toggleListening = () => {},
  feedback = null,
  dismissFeedback = false,
  setDismissFeedback = () => {},
  renderQuestionHistoryModal = () => null,
  codeExecutionResults = null,
  handleSubmitCodeFromWorkbench = () => {},
  mode = "dsa",
  interviewMode = "dsa",
  connectedResources = null,
  error = null,
  setError = () => {},
}) {
  // Normalize active mode
  const activeMode = (mode || interviewMode || "dsa").toLowerCase();
  const isComprehensive =
    activeMode.includes("comprehensive") ||
    activeMode.includes("all_in_one") ||
    activeMode.includes("mastery");
  const isDsa =
    activeMode.includes("dsa") ||
    activeMode.includes("coding") ||
    activeMode.includes("algo") ||
    isComprehensive;
  const isBehavioral = activeMode.includes("behavioral") || activeMode.includes("hr");
  const isGithub = activeMode.includes("github") || activeMode.includes("project");
  const isSystemDesign = activeMode.includes("system") || activeMode.includes("architecture");

  // Center tabs state for workbench
  const [centerTab, setCenterTab] = useState("editor"); // "editor" | "teach" | "visualize" | "testcases" | "submissions"
  const [activeLesson, setActiveLesson] = useState(null);
  const [responseTab, setResponseTab] = useState("text"); // "text" | "voice"
  const [rightTab, setRightTab] = useState("constraints"); // "constraints" | "examples" | "followup"

  // Active view toggle between Robot Interviewer and Live Webcam
  const [primaryLeftView, setPrimaryLeftView] = useState("robot"); // "robot" | "webcam"

  // Chat with Cyra state
  const [chatMessages, setChatMessages] = useState([
    {
      sender: "cyra",
      text: "Hello! I am Cyra, your AI Robotic Interviewer. I have analyzed your connected resources. Do you have any questions or would you like a hint?",
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isCyraThinking, setIsCyraThinking] = useState(false);

  // Dynamic test cases state derived from active question
  const [testCasesList, setTestCasesList] = useState([]);

  useEffect(() => {
    const q = typeof currentQuestion === "object" && currentQuestion !== null ? currentQuestion : {};
    const exs = q.examples || [];
    if (exs.length > 0) {
      setTestCasesList(
        exs.map((ex, idx) => ({
          id: idx + 1,
          input: typeof ex.input === "object" ? JSON.stringify(ex.input) : String(ex.input || ""),
          expected: typeof ex.output === "object" ? JSON.stringify(ex.output) : String(ex.output || ""),
          actual: null,
          status: "pending",
          error: null,
        }))
      );
    } else {
      setTestCasesList([
        { id: 1, input: "Test Case 1", expected: "Expected Output 1", actual: null, status: "pending", error: null },
        { id: 2, input: "Edge Case", expected: "Expected Output 2", actual: null, status: "pending", error: null },
      ]);
    }
  }, [currentQuestion]);

  // Synchronize test results from real compiler judge execution
  useEffect(() => {
    if (codeExecutionResults && codeExecutionResults.results) {
      setTestCasesList((prev) =>
        prev.map((tc, idx) => {
          const resItem = codeExecutionResults.results[idx] || codeExecutionResults.results.find((r) => r.caseNumber === tc.id);
          if (resItem) {
            return {
              ...tc,
              actual: resItem.actual,
              status: resItem.passed ? "passed" : "failed",
              error: resItem.error,
            };
          }
          return tc;
        })
      );
    }
  }, [codeExecutionResults]);

  // Ensure webcam stream is attached seamlessly to any mounted candidate camera feed
  const attachVideoSource = (node) => {
    if (node) {
      if (videoRef) {
        if (typeof videoRef === "function") videoRef(node);
        else videoRef.current = node;
      }
      const stream = window.__activeVideoStream;
      if (stream && node.srcObject !== stream) {
        node.srcObject = stream;
        node.play().catch(() => {});
      }
    }
  };

  useEffect(() => {
    if (cameraActive && window.__activeVideoStream) {
      const videoEls = document.querySelectorAll("video[data-candidate-camera='true']");
      videoEls.forEach((el) => {
        if (el.srcObject !== window.__activeVideoStream) {
          el.srcObject = window.__activeVideoStream;
          el.play().catch(() => {});
        }
      });
    }
  }, [cameraActive, primaryLeftView, videoRef]);

  // Extract Question metadata
  const qObj = typeof currentQuestion === "object" && currentQuestion !== null ? currentQuestion : {};
  const questionTitle = qObj.topic || parsedQ?.topic || (
    isDsa
      ? "Algorithmic Problem Solving"
      : isBehavioral
      ? "Project Challenge & STAR Resolution"
      : isGithub
      ? "Codebase Architecture & Modularity"
      : "Scalable Distributed System Design"
  );
  const questionDifficulty = (qObj.difficulty || "Medium").toUpperCase();
  const questionText = qObj.question || (
    typeof currentQuestion === "string"
      ? currentQuestion
      : parsedQ?.description || (
          isGithub
            ? "Walk through your repository architecture, trade-offs made, and how you ensured system modularity."
            : "Analyze the problem scenario and formulate your optimal solution."
        )
  );

  const constraintsList = qObj.constraints && qObj.constraints.length > 0
    ? qObj.constraints
    : [
        "Formulate an optimal solution meeting Big-O complexity bounds.",
        "Handle boundary conditions, empty inputs, and large inputs cleanly.",
      ];
  const examplesList = qObj.examples && qObj.examples.length > 0
    ? qObj.examples
    : [];
  const hintsList = qObj.hints && qObj.hints.length > 0
    ? qObj.hints
    : [
        "Consider the most efficient data structure for fast lookups and state tracking.",
        "Break down invariants and trade-offs before finalizing your implementation.",
      ];
  const suggestedPoints = qObj.suggested_points && qObj.suggested_points.length > 0
    ? qObj.suggested_points
    : [
        "What was the specific technical challenge?",
        "What architectural actions did you take?",
        "What was the measurable result?",
        "What did you learn from this experience?",
      ];

  const repoContext = qObj.repository_context || {
    tech_stack: "React 19, FastAPI, PostgreSQL, Neo4j, ChromaDB",
    key_features: "RAG, Multi-Agent AI, Career Intelligence, Live Interview Studio",
    architecture: "Microservice-based with knowledge graph and vector search",
    repositories: [
      { name: "CareerVerseAI", desc: "Main Project • 1.2k commits" },
      { name: "portfolio-website", desc: "Frontend Project • 254 commits" },
      { name: "ml-experiments", desc: "ML Research • 87 commits" },
    ],
  };

  const rawRelatedFiles = qObj.related_files || [
    { file: "app/main.py", desc: "Backend entry point & REST routers" },
    { file: "frontend/src/", desc: "React frontend studio & context providers" },
    { file: "app/ai/orchestrator.py", desc: "Multi-agent graph RAG & evaluator" },
    { file: "docker-compose.yml", desc: "Microservices & container infrastructure" },
  ];

  const relatedFilesList = rawRelatedFiles.map((rf) => {
    if (typeof rf === "string") {
      return { file: rf, desc: "Repository source file" };
    }
    return { file: rf.file || rf.name || "source_file", desc: rf.description || rf.desc || "Repository file" };
  });

  const followUpsList = qObj.follow_ups && qObj.follow_ups.length > 0
    ? qObj.follow_ups
    : [
        "How do you handle scalability under peak load?",
        "What challenges did you face when integrating graph queries with vector search?",
        "What was the most interesting part of the CareerVerseAI codebase to build?",
      ];

  // Grounding evidence label
  const groundingEvidence = qObj.evidence_source || (
    isDsa
      ? "Grounded in: HackerRank Problem Solving & LeetCode Bank"
      : isGithub
      ? "Grounded in: Connected GitHub Repository (CareerVerseAI)"
      : isBehavioral
      ? "Grounded in: Resume & STAR Evaluation"
      : "Grounded in: Distributed Systems RAG"
  );

  // Time formatting
  const formatTime = (secs) => {
    const hrs = Math.floor(secs / 3600);
    const mins = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    }
    return `${mins.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  // Quick Action in Chat with real AI
  const handleQuickAction = async (actionType) => {
    let userMsg = "";
    if (actionType === "teach") {
      userMsg = "Can you teach me the core concepts, mental model, and best-practice framework for this topic?";
    } else if (actionType === "hint") {
      userMsg = "Could you give me a pedagogical hint on this question?";
    } else if (actionType === "constraints") {
      userMsg = "Can you explain the constraints and boundary conditions?";
    } else if (actionType === "approach") {
      userMsg = "I'm thinking through my architecture and time-complexity trade-offs.";
    }

    setChatMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setIsCyraThinking(true);

    try {
      const resp = await chatWithCyra({
        message: userMsg,
        current_question: currentQuestion || "",
        role: role,
        candidate_code: codeSnippet || "",
        action_type: actionType,
        language: selectedLanguage,
      });

      const reply =
        resp?.reply ||
        hintsList[0] ||
        "Consider breaking the solution into modular components and evaluating edge constraints.";
      setChatMessages((prev) => [...prev, { sender: "cyra", text: reply }]);
      if (actionType === "teach") {
        setActiveLesson(reply);
      }
      if (typeof speakText === "function") {
        speakText(reply);
      }
    } catch (_err) {
      const fallbackReply =
        actionType === "teach"
          ? "💡 **Core Mental Model**: Store observed elements in a fast-lookup container to avoid O(N²) scanning.\n📐 **Framework**: Clarify constraints -> Identify invariant -> Choose minimal state -> Handle edge bounds."
          : hintsList[0] || "Consider breaking the solution into modular components and evaluating edge constraints.";
      setChatMessages((prev) => [...prev, { sender: "cyra", text: fallbackReply }]);
      if (actionType === "teach") {
        setActiveLesson(fallbackReply);
      }
    } finally {
      setIsCyraThinking(false);
    }
  };

  const handleSendCustomChat = async (e) => {
    e?.preventDefault();
    if (!chatInput.trim() || isCyraThinking) return;
    const msg = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { sender: "user", text: msg }]);
    setIsCyraThinking(true);

    try {
      const resp = await chatWithCyra({
        message: msg,
        current_question: currentQuestion || "",
        role: role,
        candidate_code: codeSnippet || "",
        action_type: "chat",
        language: selectedLanguage,
      });

      const reply = resp?.reply || "State your reasoning clearly and evaluate your trade-offs for latency, memory, and scalability.";
      setChatMessages((prev) => [...prev, { sender: "cyra", text: reply }]);
      if (typeof speakText === "function") {
        speakText(reply);
      }
    } catch (_err) {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "cyra",
          text: "I heard your idea. Make sure to consider the edge cases, memory bounds, and how you will handle unexpected input gracefully.",
        },
      ]);
    } finally {
      setIsCyraThinking(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f1f5f9",
        color: "#0f172a",
        fontFamily: "var(--font-primary, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif)",
        display: "flex",
        flexDirection: "column",
        boxSizing: "border-box",
      }}
    >
      {/* ── LIVE INTERVIEW STUDIO HEADER ─────────────────────────────────── */}
      <div
        style={{
          background: "#ffffff",
          borderBottom: "1px solid #e2e8f0",
          padding: "10px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        {/* Left: Back to Modes + Mode Title + Live Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <button
            type="button"
            onClick={handleResetToSetup}
            style={{
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "10px",
              padding: "6px 12px",
              cursor: "pointer",
              color: "#475569",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "0.82rem",
              fontWeight: 600,
              transition: "all 0.15s ease",
            }}
            title="Return to mode selection"
          >
            <ArrowLeft size={16} />
            <span>Back to Modes</span>
          </button>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h2
                style={{
                  fontSize: "1.18rem",
                  fontWeight: 800,
                  color: "#0f172a",
                  margin: 0,
                  letterSpacing: "-0.01em",
                }}
              >
                {isDsa
                  ? "Software Engineer (SDE) Interview"
                  : isBehavioral
                  ? "Behavioral Interview"
                  : isGithub
                  ? "GitHub & Projects Interview"
                  : "System Design Interview"}
              </h2>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "3px 10px",
                  borderRadius: "999px",
                  background: "#fef2f2",
                  border: "1px solid #fee2e2",
                  color: "#ef4444",
                  fontSize: "0.72rem",
                  fontWeight: 800,
                }}
              >
                <span
                  style={{
                    width: 7,
                    height: 7,
                    borderRadius: "50%",
                    background: "#ef4444",
                    boxShadow: "0 0 6px #ef4444",
                  }}
                />
                <span>Live Interview</span>
              </div>
            </div>
            <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "1px" }}>
              Real-time AI interview with adaptive questions and feedback • {groundingEvidence}
            </div>
          </div>
        </div>

        {/* Right: Countdown Timer + Language Selector + End Interview + Exit Fullscreen */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Spoken Language Selector & Status Badges */}
          <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "5px 12px",
                borderRadius: "10px",
                background: "#ffffff",
                border: "1px solid #cbd5e1",
                boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
              }}
            >
              <Globe size={15} color="#4f46e5" />
              <select
                value={selectedLanguage}
                onChange={(e) =>
                  handleLanguageChange
                    ? handleLanguageChange(e.target.value)
                    : setSelectedLanguage(e.target.value)
                }
                style={{
                  background: "transparent",
                  border: "none",
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  color: "#1e293b",
                  cursor: "pointer",
                  outline: "none",
                }}
                title="Select Interview & Speech Language"
              >
                {(supportedLanguages && supportedLanguages.length > 0 ? supportedLanguages : [
                  { code: "en", label: "English", flag: "🇮🇳", native: "English (India)" },
                  { code: "ta", label: "Tamil", flag: "🇮🇳", native: "தமிழ் / Tanglish" },
                  { code: "hi", label: "Hindi", flag: "🇮🇳", native: "हिन्दी / Hinglish" },
                  { code: "te", label: "Telugu", flag: "🇮🇳", native: "తెలుగు" },
                  { code: "kn", label: "Kannada", flag: "🇮🇳", native: "ಕನ್ನಡ" },
                  { code: "es", label: "Spanish", flag: "🇪🇸", native: "Español" },
                  { code: "fr", label: "French", flag: "🇫🇷", native: "Français" },
                  { code: "de", label: "German", flag: "🇩🇪", native: "Deutsch" },
                ]).map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.flag} {l.label} ({l.native || l.label})
                  </option>
                ))}
              </select>
            </div>

            {/* Voice & Speech State Badges */}
            {isGeneratingQuestion && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#e0e7ff",
                  color: "#4338ca",
                  border: "1px solid #c7d2fe",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
              >
                <Loader2 size={12} className="animate-spin" /> Generating {selectedLanguage === "ta" ? "Tamil" : selectedLanguage === "hi" ? "Hindi" : "English"} Question...
              </span>
            )}
            {isAgentSpeaking && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#ede9fe",
                  color: "#6d28d9",
                  border: "1px solid #ddd6fe",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
              >
                <Volume2 size={12} /> Speaking ({selectedLanguage === "ta" ? "ta-IN" : selectedLanguage === "hi" ? "hi-IN" : "en-IN"})
              </span>
            )}
            {isListening && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#fee2e2",
                  color: "#b91c1c",
                  border: "1px solid #fca5a5",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
              >
                <Mic size={12} /> Listening ({selectedLanguage === "ta" ? "ta-IN" : selectedLanguage === "hi" ? "hi-IN" : "en-IN"})...
              </span>
            )}
            {voiceStatus && !voiceStatus.isSupported && (selectedLanguage === "ta" || selectedLanguage === "hi") && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#fef3c7",
                  color: "#92400e",
                  border: "1px solid #fde68a",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
                title={voiceStatus.message}
              >
                <AlertTriangle size={12} /> {selectedLanguage === "ta" ? "Tamil" : "Hindi"} Voice Not Installed (Text Active)
              </span>
            )}
            {voiceStatus && voiceStatus.isSupported && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#f0fdf4",
                  color: "#166534",
                  border: "1px solid #bbf7d0",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
                title={voiceStatus.message}
              >
                <Volume2 size={12} /> {voiceStatus.voiceName ? `${voiceStatus.voiceName} (${selectedLanguage === "ta" ? "Tamil" : selectedLanguage === "hi" ? "Hindi" : "en-IN"})` : "Voice Ready"}
              </span>
            )}
            {micStatus?.state === "denied" && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#fee2e2",
                  color: "#b91c1c",
                  border: "1px solid #fca5a5",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
                title={micStatus.message}
              >
                <MicOff size={12} /> Mic Denied (Text Active)
              </span>
            )}
            {micStatus?.state === "unsupported" && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#f1f5f9",
                  color: "#475569",
                  border: "1px solid #cbd5e1",
                  padding: "4px 8px",
                  borderRadius: "8px",
                }}
                title={micStatus.message}
              >
                <MicOff size={12} /> STT Unsupported (Text Active)
              </span>
            )}
          </div>

          {/* Timer Card */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "6px 14px",
              borderRadius: "10px",
              background: "#ffffff",
              border: "1px solid #cbd5e1",
              boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
            }}
          >
            <Clock size={16} color="#6366f1" />
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span
                style={{
                  fontSize: "0.92rem",
                  fontWeight: 800,
                  color: "#0f172a",
                  fontVariantNumeric: "tabular-nums",
                  lineHeight: 1.1,
                }}
              >
                {formatTime(timeLeft)}
              </span>
              <span style={{ fontSize: "0.64rem", color: "#64748b", fontWeight: 600 }}>
                Time Remaining
              </span>
            </div>
          </div>

          {/* End Interview Button */}
          <button
            type="button"
            onClick={handleCompleteInterview}
            style={{
              background: "#fff1f2",
              border: "1px solid #fecdd3",
              borderRadius: "10px",
              padding: "7px 14px",
              color: "#e11d48",
              fontSize: "0.82rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              transition: "background 0.15s ease",
            }}
          >
            <PhoneOff size={15} />
            <span>End Interview</span>
          </button>

          {/* Exit Fullscreen */}
          <button
            type="button"
            onClick={toggleFullscreen}
            style={{
              background: "#ffffff",
              border: "1px solid #cbd5e1",
              borderRadius: "10px",
              padding: "7px 12px",
              color: "#475569",
              fontSize: "0.82rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            <span>{isFullscreen ? "Exit Fullscreen" : "Fullscreen"}</span>
          </button>
        </div>
      </div>

      {/* ── MAIN 3-PANEL RESPONSIVE WORKSPACE ─────────────────────────────── */}
      <div
        style={{
          flex: 1,
          padding: "16px 24px",
          display: "grid",
          gridTemplateColumns: "290px minmax(0, 1fr) 350px",
          gap: "16px",
          boxSizing: "border-box",
          maxWidth: "1800px",
          width: "100%",
          margin: "0 auto",
          alignItems: "start",
        }}
      >
        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* PANEL 1 (LEFT): CYRA ROBOTIC AGENT & CANDIDATE CAMERA FEED          */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {/* Main Agent Avatar & Video Feed Container */}
          <div
            style={{
              background: "#ffffff",
              borderRadius: "18px",
              border: "1px solid #e2e8f0",
              boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
              padding: "16px",
              display: "flex",
              flexDirection: "column",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* View Selector Tabs: Robot Interviewer vs Webcam */}
            <div
              style={{
                display: "flex",
                background: "#f1f5f9",
                borderRadius: "10px",
                padding: "3px",
                marginBottom: "12px",
              }}
            >
              <button
                type="button"
                onClick={() => setPrimaryLeftView("robot")}
                style={{
                  flex: 1,
                  padding: "5px 8px",
                  borderRadius: "8px",
                  border: "none",
                  background: primaryLeftView === "robot" ? "#ffffff" : "transparent",
                  color: primaryLeftView === "robot" ? "#4338ca" : "#64748b",
                  fontWeight: 700,
                  fontSize: "0.72rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                  boxShadow: primaryLeftView === "robot" ? "0 1px 3px rgba(0,0,0,0.05)" : "none",
                }}
              >
                <Bot size={13} />
                <span>Cyra Robot</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setPrimaryLeftView("webcam");
                  if (!cameraActive) startCamera();
                }}
                style={{
                  flex: 1,
                  padding: "5px 8px",
                  borderRadius: "8px",
                  border: "none",
                  background: primaryLeftView === "webcam" ? "#ffffff" : "transparent",
                  color: primaryLeftView === "webcam" ? "#4338ca" : "#64748b",
                  fontWeight: 700,
                  fontSize: "0.72rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                  boxShadow: primaryLeftView === "webcam" ? "0 1px 3px rgba(0,0,0,0.05)" : "none",
                }}
              >
                <Camera size={13} />
                <span>Your Camera {cameraActive && "●"}</span>
              </button>
            </div>

            {/* Video / Robot Visual Container */}
            <div style={{ position: "relative", width: "100%", height: "230px", borderRadius: "14px", overflow: "hidden" }}>
              {primaryLeftView === "robot" ? (
                /* Robotic Cyra Mascot */
                <>
                  <CyraRobotAvatar isSpeaking={isAgentSpeaking} isListening={isListening} size={230} />
                  {/* Floating Mini PiP Webcam when camera is on */}
                  {cameraActive && (
                    <div
                      onClick={() => setPrimaryLeftView("webcam")}
                      style={{
                        position: "absolute",
                        bottom: 10,
                        left: 10,
                        width: "80px",
                        height: "60px",
                        borderRadius: "8px",
                        border: "2px solid #22c55e",
                        overflow: "hidden",
                        background: "#000000",
                        cursor: "pointer",
                        boxShadow: "0 4px 10px rgba(0,0,0,0.4)",
                        zIndex: 10,
                      }}
                      title="Click to expand your camera feed"
                    >
                      <video
                        ref={attachVideoSource}
                        data-candidate-camera="true"
                        autoPlay
                        playsInline
                        muted
                        style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)" }}
                      />
                    </div>
                  )}
                </>
              ) : (
                /* Live Candidate Webcam Proctoring Feed */
                <div
                  style={{
                    width: "100%",
                    height: "100%",
                    background: "#090d16",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    position: "relative",
                  }}
                >
                  {cameraActive ? (
                    <>
                      <video
                        ref={attachVideoSource}
                        data-candidate-camera="true"
                        autoPlay
                        playsInline
                        muted
                        style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)" }}
                      />
                      <div
                        style={{
                          position: "absolute",
                          top: 8,
                          left: 8,
                          background: "rgba(15, 23, 42, 0.75)",
                          backdropFilter: "blur(4px)",
                          padding: "3px 8px",
                          borderRadius: "12px",
                          color: "#22c55e",
                          fontSize: "0.68rem",
                          fontWeight: 700,
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#22c55e" }} />
                        <span>Live Webcam</span>
                      </div>
                    </>
                  ) : (
                    <div style={{ textAlign: "center", padding: "16px", color: "#94a3b8" }}>
                      <Camera size={32} color="#64748b" style={{ marginBottom: "8px" }} />
                      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#e2e8f0" }}>Camera is Muted</div>
                      <button
                        type="button"
                        onClick={startCamera}
                        style={{
                          marginTop: "8px",
                          background: "#6366f1",
                          color: "#ffffff",
                          border: "none",
                          padding: "5px 12px",
                          borderRadius: "6px",
                          fontSize: "0.74rem",
                          fontWeight: 700,
                          cursor: "pointer",
                        }}
                      >
                        Enable Camera
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Cyra Name & Character Bubble */}
            <div style={{ width: "100%", marginTop: "12px", textAlign: "left" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ fontSize: "1rem", fontWeight: 800, color: "#0f172a" }}>Cyra</span>
                <span
                  style={{
                    fontSize: "0.68rem",
                    fontWeight: 700,
                    background: "#e0e7ff",
                    color: "#4338ca",
                    padding: "2px 8px",
                    borderRadius: "10px",
                  }}
                >
                  Robotic Interviewer
                </span>
              </div>
              <p
                style={{
                  margin: "8px 0 0 0",
                  fontSize: "0.8rem",
                  color: "#475569",
                  lineHeight: 1.4,
                  background: "#f8fafc",
                  padding: "10px 12px",
                  borderRadius: "12px",
                  border: "1px solid #e2e8f0",
                }}
              >
                {isGithub
                  ? "I'll ask questions about your CareerVerseAI GitHub repository. I've analyzed your architecture, commits, and code files to test real technical decisions."
                  : isDsa
                  ? "Here's an algorithmic problem grounded in HackerRank Problem Solving & LeetCode. Take your time to think through time and space complexity."
                  : isBehavioral
                  ? "This is a behavioral evaluation. Please structure your response using the STAR method (Situation, Task, Action, Result)."
                  : "Let's explore your architectural thinking, trade-offs, and how you design systems under scale."}
              </p>
            </div>
          </div>

          {/* Mode-Specific Context Card */}
          {isDsa ? (
            /* Cyra's Tips Card for DSA */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "16px",
                border: "1px solid #e2e8f0",
                padding: "14px 16px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                <span style={{ fontSize: "1rem" }}>💡</span>
                <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a" }}>
                  Cyra's Tips
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.78rem", color: "#475569", lineHeight: 1.6 }}>
                <li>Think about edge cases and boundary inputs</li>
                <li>Consider time and space complexity (Big-O)</li>
                <li>Explain your reasoning clearly before writing code</li>
                <li>Grounded in HackerRank + LeetCode</li>
              </ul>
            </div>
          ) : isBehavioral ? (
            /* STAR Framework Card for Behavioral */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "16px",
                border: "1px solid #e2e8f0",
                padding: "14px 16px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
              }}
            >
              <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "10px" }}>
                STAR Framework
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.76rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: 22, height: 22, borderRadius: "50%", background: "#e0e7ff", color: "#4338ca", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>S</span>
                  <span style={{ color: "#334155", fontWeight: 600 }}>Situation — Set the context</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: 22, height: 22, borderRadius: "50%", background: "#fef3c7", color: "#b45309", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>T</span>
                  <span style={{ color: "#334155", fontWeight: 600 }}>Task — Your specific responsibility</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: 22, height: 22, borderRadius: "50%", background: "#dcfce7", color: "#15803d", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>A</span>
                  <span style={{ color: "#334155", fontWeight: 600 }}>Action — Steps and code you implemented</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ width: 22, height: 22, borderRadius: "50%", background: "#fee2e2", color: "#b91c1c", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>R</span>
                  <span style={{ color: "#334155", fontWeight: 600 }}>Result — Measurable impact & learnings</span>
                </div>
              </div>
            </div>
          ) : isGithub ? (
            /* Analyzed Repositories Card for GitHub */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "16px",
                border: "1px solid #e2e8f0",
                padding: "14px 16px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
              }}
            >
              <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "8px" }}>
                Analyzed Repositories
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {(repoContext.repositories || []).map((repo, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "8px 10px",
                      borderRadius: "10px",
                      background: "#f8fafc",
                      border: "1px solid #e2e8f0",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#0f172a" }}>
                        {repo.name}
                      </div>
                      <div style={{ fontSize: "0.7rem", color: "#64748b" }}>
                        {repo.desc || repo.description || "Connected repository"}
                      </div>
                    </div>
                    <ExternalLink size={13} color="#94a3b8" />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* System Design Card */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "16px",
                border: "1px solid #e2e8f0",
                padding: "14px 16px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
              }}
            >
              <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "8px" }}>
                Architecture Guidelines
              </div>
              <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.78rem", color: "#475569", lineHeight: 1.6 }}>
                <li>Identify functional requirements & scale</li>
                <li>Define throughput and latency SLA bounds</li>
                <li>Design data schemas, indexes & caching tiers</li>
                <li>Evaluate bottlenecks and partition tolerance</li>
              </ul>
            </div>
          )}

          {/* Media Audio/Video Controls at Bottom of Panel 1 */}
          <div
            style={{
              background: "#ffffff",
              borderRadius: "16px",
              border: "1px solid #e2e8f0",
              padding: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "16px",
            }}
          >
            {/* Speak Again (Replay Audio) Button */}
            <button
              type="button"
              onClick={handleSpeakAgain}
              disabled={isAgentSpeaking}
              style={{
                width: 44,
                height: 44,
                borderRadius: "50%",
                border: "none",
                background: isAgentSpeaking ? "#818cf8" : "#4f46e5",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: isAgentSpeaking ? "not-allowed" : "pointer",
                boxShadow: "0 2px 6px rgba(79, 70, 229, 0.3)",
                transition: "all 0.15s ease",
              }}
              title="Speak Again (Replay Current Question)"
            >
              <Volume2 size={20} />
            </button>

            {/* Mic Button */}
            <button
              type="button"
              onClick={toggleListening}
              style={{
                width: 44,
                height: 44,
                borderRadius: "50%",
                border: "none",
                background: isListening ? "#ef4444" : "#3b82f6",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                boxShadow: isListening ? "0 0 12px rgba(239, 68, 68, 0.5)" : "0 2px 6px rgba(59, 130, 246, 0.3)",
                transition: "all 0.15s ease",
              }}
              title={isListening ? "Mute Microphone" : "Unmute Microphone"}
            >
              {isListening ? <Mic size={20} /> : <MicOff size={20} />}
            </button>

            {/* End Call / Stop Button */}
            <button
              type="button"
              onClick={handleCompleteInterview}
              style={{
                width: 44,
                height: 44,
                borderRadius: "50%",
                border: "none",
                background: "#ef4444",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                boxShadow: "0 2px 6px rgba(239, 68, 68, 0.3)",
              }}
              title="Stop & End Session"
            >
              <PhoneOff size={20} />
            </button>

            {/* Video Camera Button */}
            <button
              type="button"
              onClick={() => {
                if (cameraActive) {
                  stopCamera();
                  setPrimaryLeftView("robot");
                } else {
                  startCamera();
                  setPrimaryLeftView("webcam");
                }
              }}
              style={{
                width: 44,
                height: 44,
                borderRadius: "50%",
                border: "none",
                background: cameraActive ? "#0f172a" : "#64748b",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
              }}
              title={cameraActive ? "Turn Off Video Camera" : "Turn On Video Camera"}
            >
              {cameraActive ? <Video size={20} /> : <VideoOff size={20} />}
            </button>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* PANEL 2 (CENTER): WORKBENCH CODE EDITOR / RESPONSE STUDIO           */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div style={{ display: "flex", flexDirection: "column", gap: "14px", minWidth: 0 }}>
          {isDsa ? (
            /* DSA WORKBENCH */
            <>
              {/* Workbench Tabs & Code Area Card */}
              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                  overflow: "hidden",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {/* Workbench Navigation Bar */}
                <div
                  style={{
                    background: "#ffffff",
                    borderBottom: "1px solid #e2e8f0",
                    padding: "8px 14px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      type="button"
                      onClick={() => setCenterTab("editor")}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        border: "none",
                        background: centerTab === "editor" ? "#6366f1" : "transparent",
                        color: centerTab === "editor" ? "#ffffff" : "#64748b",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Code2 size={14} />
                      <span>Code Editor</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCenterTab("teach");
                        if (!activeLesson) {
                          handleQuickAction("teach");
                        }
                      }}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        border: "none",
                        background:
                          centerTab === "teach"
                            ? "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)"
                            : "#e0e7ff",
                        color: centerTab === "teach" ? "#ffffff" : "#4338ca",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        boxShadow:
                          centerTab === "teach"
                            ? "0 2px 8px rgba(79,70,229,0.3)"
                            : "none",
                      }}
                    >
                      <Sparkles size={14} />
                      <span>🎓 Agent Lesson & Breakdown</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCenterTab("visualize")}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        border: "none",
                        background: centerTab === "visualize" ? "#6366f1" : "transparent",
                        color: centerTab === "visualize" ? "#ffffff" : "#64748b",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Layers size={14} />
                      <span>Visualize</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCenterTab("testcases")}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        border: "none",
                        background: centerTab === "testcases" ? "#6366f1" : "transparent",
                        color: centerTab === "testcases" ? "#ffffff" : "#64748b",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Zap size={14} />
                      <span>Test Cases</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCenterTab("submissions")}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "8px",
                        border: "none",
                        background: centerTab === "submissions" ? "#6366f1" : "transparent",
                        color: centerTab === "submissions" ? "#ffffff" : "#64748b",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <CheckCircle2 size={14} />
                      <span>Submissions</span>
                    </button>
                  </div>

                  {/* Settings Icon */}
                  <button
                    type="button"
                    onClick={() => setShowSettingsModal(true)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#64748b",
                      cursor: "pointer",
                      padding: "4px",
                    }}
                    title="Editor Settings"
                  >
                    <Sliders size={16} />
                  </button>
                </div>

                {centerTab === "teach" ? (
                  <div
                    style={{
                      background: "#ffffff",
                      padding: "24px 28px",
                      minHeight: "360px",
                      overflowY: "auto",
                      display: "flex",
                      flexDirection: "column",
                      gap: "18px",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap",
                        gap: "10px",
                        borderBottom: "1px solid #e2e8f0",
                        paddingBottom: "14px",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: "10px",
                            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "#ffffff",
                          }}
                        >
                          <Sparkles size={18} />
                        </div>
                        <div>
                          <h4 style={{ margin: 0, fontSize: "1rem", fontWeight: 800, color: "#0f172a" }}>
                            Dr. Cyra Vance Concept Masterclass & Framework
                          </h4>
                          <p style={{ margin: "2px 0 0 0", fontSize: "0.76rem", color: "#64748b" }}>
                            Interactive teaching breakdown for {currentQuestion?.topic || "Active Problem Concepts"}
                          </p>
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button
                          type="button"
                          onClick={() => handleQuickAction("teach")}
                          disabled={isCyraThinking}
                          style={{
                            background: "#f1f5f9",
                            border: "1px solid #cbd5e1",
                            borderRadius: "8px",
                            padding: "6px 12px",
                            fontSize: "0.76rem",
                            fontWeight: 700,
                            color: "#334155",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "5px",
                          }}
                        >
                          <RotateCcw size={12} />
                          <span>{isCyraThinking ? "Cyra is Teaching..." : "Re-explain Concept"}</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setCenterTab("editor")}
                          style={{
                            background: "#4f46e5",
                            border: "none",
                            borderRadius: "8px",
                            padding: "6px 14px",
                            fontSize: "0.76rem",
                            fontWeight: 700,
                            color: "#ffffff",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "5px",
                          }}
                        >
                          <Code2 size={13} />
                          <span>Apply in Code Editor →</span>
                        </button>
                      </div>
                    </div>

                    {isCyraThinking && !activeLesson ? (
                      <div style={{ padding: "40px 20px", textAlign: "center", color: "#6366f1" }}>
                        <Bot size={32} style={{ animation: "pulse 1.5s infinite", margin: "0 auto 12px" }} />
                        <div style={{ fontWeight: 700, fontSize: "0.95rem" }}>
                          Dr. Cyra Vance is synthesizing your pedagogical lesson...
                        </div>
                        <div style={{ fontSize: "0.78rem", color: "#94a3b8", marginTop: "4px" }}>
                          Synthesizing core mental model, visual breakdown, and 4-step answer framework.
                        </div>
                      </div>
                    ) : (
                      <div
                        style={{
                          background: "#f8fafc",
                          border: "1px solid #e2e8f0",
                          borderRadius: "14px",
                          padding: "20px 24px",
                          fontSize: "0.88rem",
                          lineHeight: 1.7,
                          color: "#1e293b",
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {activeLesson ||
                          `💡 **Core Mental Model & Intuition**:
Think of this problem in terms of invariant state tracking. Instead of repeatedly re-scanning previous elements in O(N²), store observed values in an auxiliary hash map or two-pointer window to achieve O(N) or O(1) query time.

📐 **Top-Tier 4-Step Framework**:
1. Clarify constraints (bounds, negative numbers, duplicates).
2. Identify the mathematical invariant (e.g., complement = target - current).
3. Select the minimal state container (hash map vs sorted array).
4. Handle edge cases (empty input, single element, extreme values).

⚖️ **Critical Trade-Offs**:
Trading O(N) auxiliary memory drops runtime from O(N²) quadratic scan down to O(N) linear time.

❓ **Check-in Understanding**:
Can you identify what happens if there are duplicate values in the array? Click "Apply in Code Editor" to test your implementation!`}
                      </div>
                    )}
                  </div>
                ) : (
                  <>
                    {/* Dark Code Workbench */}
                    <div
                      style={{
                        background: "#0f172a",
                        borderBottom: "1px solid #1e293b",
                        padding: "6px 14px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                  {/* File Tab */}
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div
                      style={{
                        background: "#1e293b",
                        color: "#f8fafc",
                        padding: "4px 12px",
                        borderRadius: "6px",
                        fontSize: "0.78rem",
                        fontWeight: 600,
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <FileText size={12} color="#60a5fa" />
                      <span>solution.py</span>
                    </div>
                    <span style={{ color: "#64748b", fontSize: "0.8rem" }}>+</span>
                  </div>

                  {/* Language Selector */}
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <select
                      value={selectedDomainKey}
                      onChange={(e) => handleDomainChange(e.target.value)}
                      style={{
                        background: "#1e293b",
                        border: "1px solid #334155",
                        color: "#f8fafc",
                        padding: "3px 10px",
                        borderRadius: "6px",
                        fontSize: "0.76rem",
                        fontWeight: 600,
                        outline: "none",
                      }}
                    >
                      <option value="dsa_py">Python</option>
                      <option value="dsa_java">Java</option>
                      <option value="dsa_cpp">C++</option>
                      <option value="backend_node">JavaScript</option>
                    </select>
                  </div>
                </div>

                {/* Code Editor Body */}
                <div
                  style={{
                    background: "#090d16",
                    display: "flex",
                    minHeight: "260px",
                    fontFamily: "var(--font-mono, 'Fira Code', Menlo, monospace)",
                    fontSize: "0.82rem",
                    color: "#f8fafc",
                    position: "relative",
                  }}
                >
                  {/* Line Numbers */}
                  <div
                    style={{
                      width: "40px",
                      background: "#070b12",
                      padding: "12px 6px",
                      textAlign: "right",
                      userSelect: "none",
                      color: "#475569",
                      lineHeight: "1.6",
                      fontSize: "0.75rem",
                    }}
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
                      <div key={n}>{n}</div>
                    ))}
                  </div>

                  {/* Code Textarea */}
                  <textarea
                    value={
                      codeSnippet ||
                      `# DSA / Algorithmic Problem Solving (Python)
# Grounded in HackerRank Problem Solving & LeetCode Bank
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        """
        Time Complexity: O(N)
        Space Complexity: O(N)
        """
        seen = {}
        for i, num in enumerate(nums):
            diff = target - num
            if diff in seen:
                return [seen[diff], i]
            seen[num] = i
        return []
`
                    }
                    onChange={(e) => setCodeSnippet(e.target.value)}
                    style={{
                      flex: 1,
                      background: "transparent",
                      border: "none",
                      outline: "none",
                      color: "#e2e8f0",
                      padding: "12px",
                      lineHeight: "1.6",
                      fontSize: "0.82rem",
                      resize: "none",
                      fontFamily: "inherit",
                      whiteSpace: "pre",
                    }}
                    spellCheck={false}
                  />
                </div>

                {/* Editor Footer Toolbar */}
                <div
                  style={{
                    background: "#0f172a",
                    borderTop: "1px solid #1e293b",
                    padding: "8px 14px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "0.72rem", color: "#64748b" }}>
                    <RotateCcw
                      size={13}
                      style={{ cursor: "pointer" }}
                      onClick={handleResetTemplate}
                      title="Reset Template"
                    />
                    <span>Ln 10, Col 14</span>
                    <span>Python</span>
                    <span>Spaces: 4</span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      type="button"
                      onClick={handleResetTemplate}
                      style={{
                        background: "#1e293b",
                        border: "1px solid #334155",
                        color: "#94a3b8",
                        padding: "5px 12px",
                        borderRadius: "6px",
                        fontSize: "0.76rem",
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      Reset
                    </button>
                    <button
                      type="button"
                      onClick={handleRunCode}
                      disabled={isRunningCode}
                      style={{
                        background: "#2563eb",
                        border: "none",
                        color: "#ffffff",
                        padding: "5px 16px",
                        borderRadius: "6px",
                        fontSize: "0.76rem",
                        fontWeight: 700,
                        cursor: isRunningCode ? "not-allowed" : "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Play size={12} fill="#ffffff" />
                      <span>{isRunningCode ? "Running Tests..." : "Run ▶"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={handleSubmitCodeFromWorkbench}
                      disabled={loading || isRunningCode}
                      style={{
                        background: loading
                          ? "#818cf8"
                          : "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                        border: "none",
                        color: "#ffffff",
                        padding: "5px 16px",
                        borderRadius: "6px",
                        fontSize: "0.76rem",
                        fontWeight: 700,
                        cursor: loading || isRunningCode ? "not-allowed" : "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        boxShadow: loading ? "none" : "0 2px 6px rgba(79,70,229,0.35)",
                      }}
                    >
                      {loading ? (
                        <>
                          <Loader2 size={12} className="animate-spin" />
                          <span>Evaluating Code & Tests...</span>
                        </>
                      ) : (
                        <>
                          <Send size={12} />
                          <span>Submit Solution to Cyra 🚀</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

              {/* Bottom Split Row: Test Cases & AI Feedback */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "14px",
                }}
              >
                {/* Test Cases Card */}
                <div
                  style={{
                    background: "#ffffff",
                    borderRadius: "16px",
                    border: "1px solid #e2e8f0",
                    padding: "14px 16px",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "10px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ fontSize: "1rem" }}>🧪</span>
                      <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a" }}>
                        Test Cases
                      </span>
                    </div>
                    <span style={{ fontSize: "0.72rem", color: "#64748b", fontWeight: 600 }}>
                      {testCasesList.length} Active Vectors
                    </span>
                  </div>

                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: "0.74rem",
                      textAlign: "left",
                    }}
                  >
                    <thead>
                      <tr style={{ color: "#64748b", borderBottom: "1px solid #e2e8f0" }}>
                        <th style={{ padding: "4px 6px" }}>#</th>
                        <th style={{ padding: "4px 6px" }}>Input</th>
                        <th style={{ padding: "4px 6px" }}>Expected</th>
                        <th style={{ padding: "4px 6px" }}>Actual</th>
                        <th style={{ padding: "4px 6px" }}>Status</th>
                        <th style={{ padding: "4px 6px" }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {testCasesList.map((tc) => {
                        const isPassed = tc.status === "passed";
                        const isFailed = tc.status === "failed";
                        const isRunning = isRunningCode || tc.status === "running";
                        return (
                          <tr key={tc.id} style={{ borderBottom: "1px solid #f8fafc" }}>
                            <td style={{ padding: "6px", fontWeight: 700, color: "#64748b" }}>{tc.id}</td>
                            <td style={{ padding: "6px", fontFamily: "monospace", color: "#334155", maxWidth: "110px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={tc.input}>
                              {tc.input}
                            </td>
                            <td style={{ padding: "6px", fontFamily: "monospace", color: "#334155", maxWidth: "90px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={tc.expected}>
                              {tc.expected}
                            </td>
                            <td style={{ padding: "6px", fontFamily: "monospace", color: tc.actual !== null ? (isPassed ? "#16a34a" : "#dc2626") : "#94a3b8" }}>
                              {tc.actual !== null ? tc.actual : "—"}
                            </td>
                            <td style={{ padding: "6px" }}>
                              {isRunning ? (
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#2563eb", fontWeight: 700 }}>
                                  <Clock size={12} /> Running
                                </span>
                              ) : isPassed ? (
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#16a34a", fontWeight: 700 }}>
                                  <CheckCircle2 size={12} /> Passed
                                </span>
                              ) : isFailed ? (
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#dc2626", fontWeight: 700 }}>
                                  <XCircle size={12} /> Failed
                                </span>
                              ) : (
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#64748b", fontWeight: 600 }}>
                                  ⏳ Not Run
                                </span>
                              )}
                            </td>
                            <td style={{ padding: "6px" }}>
                              <button
                                type="button"
                                onClick={handleRunCode}
                                disabled={isRunningCode}
                                style={{
                                  background: "#f8fafc",
                                  border: "1px solid #cbd5e1",
                                  padding: "2px 8px",
                                  borderRadius: "4px",
                                  fontSize: "0.68rem",
                                  fontWeight: 600,
                                  cursor: isRunningCode ? "not-allowed" : "pointer",
                                }}
                              >
                                Run
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* AI Feedback Card */}
                <div
                  style={{
                    background: "#ffffff",
                    borderRadius: "16px",
                    border: "1px solid #e2e8f0",
                    padding: "14px 16px",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                      <Sparkles size={14} color="#6366f1" />
                      <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a" }}>
                        AI Evaluation & Feedback
                      </span>
                    </div>

                    {codeExecutionResults ? (
                      <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                        <div style={{ flex: 1 }}>
                          <div
                            style={{
                              fontSize: "0.8rem",
                              fontWeight: 700,
                              color: codeExecutionResults.status === "Accepted" ? "#16a34a" : "#dc2626",
                              display: "flex",
                              alignItems: "center",
                              gap: "4px",
                            }}
                          >
                            {codeExecutionResults.status === "Accepted" ? (
                              <>
                                <CheckCircle2 size={13} /> Accepted: {codeExecutionResults.passedCount}/{codeExecutionResults.totalCount} Test Cases Passed
                              </>
                            ) : (
                              <>
                                <XCircle size={13} /> {codeExecutionResults.status}: {codeExecutionResults.passedCount}/{codeExecutionResults.totalCount} Passed
                              </>
                            )}
                          </div>
                          <p style={{ margin: "4px 0 0 0", fontSize: "0.74rem", color: "#64748b", lineHeight: 1.4 }}>
                            {codeExecutionResults.stdout || (
                              codeExecutionResults.status === "Accepted"
                                ? "All test vectors satisfied with optimal computational complexity."
                                : "Review failing cases or exceptions above to adjust algorithm."
                            )}
                          </p>
                        </div>

                        {/* Donut Score Gauge */}
                        <div
                          style={{
                            width: 54,
                            height: 54,
                            borderRadius: "50%",
                            border: `4px solid ${codeExecutionResults.status === "Accepted" ? "#22c55e" : "#ef4444"}`,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <span style={{ fontSize: "0.84rem", fontWeight: 800, color: "#0f172a" }}>
                            {Math.round(((codeExecutionResults.passedCount || 0) / Math.max(codeExecutionResults.totalCount || 1, 1)) * 100)}
                          </span>
                          <span style={{ fontSize: "0.55rem", color: "#64748b" }}>/100</span>
                        </div>
                      </div>
                    ) : feedback ? (
                      <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                        <div style={{ flex: 1 }}>
                          <div
                            style={{
                              fontSize: "0.8rem",
                              fontWeight: 700,
                              color: "#16a34a",
                              display: "flex",
                              alignItems: "center",
                              gap: "4px",
                            }}
                          >
                            <CheckCircle2 size={13} /> Evaluated Answer
                          </div>
                          <p style={{ margin: "4px 0 0 0", fontSize: "0.74rem", color: "#64748b", lineHeight: 1.4 }}>
                            {feedback.assessment || feedback.summary || "Answer recorded successfully."}
                          </p>
                        </div>
                        <div
                          style={{
                            width: 54,
                            height: 54,
                            borderRadius: "50%",
                            border: "4px solid #6366f1",
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <span style={{ fontSize: "0.84rem", fontWeight: 800, color: "#0f172a" }}>{feedback.score || 85}</span>
                          <span style={{ fontSize: "0.55rem", color: "#64748b" }}>/100</span>
                        </div>
                      </div>
                    ) : (
                      <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                        <div style={{ flex: 1 }}>
                          <div
                            style={{
                              fontSize: "0.8rem",
                              fontWeight: 700,
                              color: "#475569",
                              display: "flex",
                              alignItems: "center",
                              gap: "4px",
                            }}
                          >
                            <Clock size={13} /> Waiting for Execution
                          </div>
                          <p style={{ margin: "4px 0 0 0", fontSize: "0.74rem", color: "#64748b", lineHeight: 1.4 }}>
                            Write your solution above and click <strong>Run ▶</strong> to test against test cases. Click <strong>Submit Solution to Cyra 🚀</strong> when ready to proceed.
                          </p>
                        </div>
                        <div
                          style={{
                            width: 54,
                            height: 54,
                            borderRadius: "50%",
                            border: "4px dashed #cbd5e1",
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <span style={{ fontSize: "0.84rem", fontWeight: 800, color: "#94a3b8" }}>—</span>
                          <span style={{ fontSize: "0.55rem", color: "#94a3b8" }}>/100</span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "8px", flexWrap: "wrap" }}>
                    <span
                      style={{
                        fontSize: "0.68rem",
                        padding: "2px 8px",
                        borderRadius: "10px",
                        background: codeExecutionResults?.status === "Accepted" ? "#dcfce7" : "#f1f5f9",
                        color: codeExecutionResults?.status === "Accepted" ? "#166534" : "#475569",
                        fontWeight: 700,
                      }}
                    >
                      {codeExecutionResults ? (codeExecutionResults.status === "Accepted" ? "✓ Correctness Verified" : "✗ Needs Debugging") : "○ Correctness Pending"}
                    </span>
                    <span
                      style={{
                        fontSize: "0.68rem",
                        padding: "2px 8px",
                        borderRadius: "10px",
                        background: "#fef3c7",
                        color: "#92400e",
                        fontWeight: 700,
                      }}
                    >
                      ⚡ Time: {codeExecutionResults?.time_complexity || "O(N)"}
                    </span>
                    <span
                      style={{
                        fontSize: "0.68rem",
                        padding: "2px 8px",
                        borderRadius: "10px",
                        background: "#ede9fe",
                        color: "#5b21b6",
                        fontWeight: 700,
                      }}
                    >
                      💾 Space: {codeExecutionResults?.space_complexity || "O(1)"}
                    </span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* BEHAVIORAL & GITHUB PROJECTS WORKBENCH */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #e2e8f0",
                boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              {/* Question Header */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span
                    style={{
                      fontSize: "0.76rem",
                      fontWeight: 800,
                      color: "#6366f1",
                      background: "#e0e7ff",
                      padding: "3px 10px",
                      borderRadius: "12px",
                    }}
                  >
                    Question {currentQIndex} of 8
                  </span>
                  <span
                    style={{
                      fontSize: "0.72rem",
                      fontWeight: 700,
                      color: "#16a34a",
                      background: "#dcfce7",
                      padding: "2px 8px",
                      borderRadius: "10px",
                    }}
                  >
                    {isBehavioral ? "Behavioral STAR" : "Project Discussion (CareerVerseAI)"}
                  </span>
                  {handleSpeakAgain && (
                    <button
                      type="button"
                      onClick={handleSpeakAgain}
                      disabled={isAgentSpeaking}
                      style={{
                        marginLeft: "auto",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                        background: isAgentSpeaking ? "#ede9fe" : "#f1f5f9",
                        color: isAgentSpeaking ? "#6d28d9" : "#334155",
                        border: "1px solid #cbd5e1",
                        borderRadius: "8px",
                        padding: "3px 8px",
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        cursor: isAgentSpeaking ? "not-allowed" : "pointer",
                      }}
                      title="Replay Audio"
                    >
                      <Volume2 size={13} />
                      <span>{isAgentSpeaking ? "Speaking..." : "Speak Again"}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Big Question Prompt */}
              <h3
                style={{
                  margin: 0,
                  fontSize: "1.08rem",
                  fontWeight: 800,
                  color: "#0f172a",
                  lineHeight: 1.45,
                }}
              >
                {questionText}
              </h3>

              {/* Suggested Points or Repository Context */}
              {isGithub ? (
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    padding: "12px 14px",
                    fontSize: "0.78rem",
                    color: "#475569",
                  }}
                >
                  <div style={{ fontWeight: 800, color: "#0f172a", marginBottom: "6px" }}>
                    Your Repository Context
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <div>
                      <strong style={{ color: "#334155" }}>Tech Stack:</strong> {repoContext.tech_stack}
                    </div>
                    <div>
                      <strong style={{ color: "#334155" }}>Key Features:</strong> {repoContext.key_features}
                    </div>
                    <div>
                      <strong style={{ color: "#334155" }}>Architecture:</strong> {repoContext.architecture}
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    padding: "12px 14px",
                    fontSize: "0.78rem",
                    color: "#475569",
                  }}
                >
                  <div style={{ fontWeight: 800, color: "#0f172a", marginBottom: "6px" }}>
                    Suggested Points
                  </div>
                  <ul style={{ margin: 0, paddingLeft: "18px", lineHeight: 1.6 }}>
                    {suggestedPoints.map((pt, i) => (
                      <li key={i}>{pt}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Response Mode Tabs */}
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <button
                  type="button"
                  onClick={() => setResponseTab("text")}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "8px",
                    border: "1px solid",
                    borderColor: responseTab === "text" ? "#6366f1" : "#cbd5e1",
                    background: responseTab === "text" ? "#e0e7ff" : "#ffffff",
                    color: responseTab === "text" ? "#4338ca" : "#64748b",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <FileText size={14} />
                  <span>Text Response</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setResponseTab("voice");
                    toggleListening();
                  }}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "8px",
                    border: "1px solid",
                    borderColor: responseTab === "voice" ? "#6366f1" : "#cbd5e1",
                    background: responseTab === "voice" ? "#e0e7ff" : "#ffffff",
                    color: responseTab === "voice" ? "#4338ca" : "#64748b",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <Mic size={14} />
                  <span>Voice Response {isListening ? "(Listening...)" : ""}</span>
                </button>
              </div>

              {/* Textarea Input */}
              <textarea
                value={candidateAnswer}
                onChange={(e) => setCandidateAnswer(e.target.value)}
                placeholder={
                  isGithub
                    ? "Type your answer here... You can reference your code in CareerVerseAI, architecture decisions, challenges faced, and what you learned."
                    : "Type your answer here... You can take your time to explain your experience in detail using the STAR framework."
                }
                style={{
                  width: "100%",
                  minHeight: "180px",
                  padding: "14px",
                  borderRadius: "12px",
                  border: "1px solid #cbd5e1",
                  fontSize: "0.88rem",
                  color: "#0f172a",
                  lineHeight: 1.5,
                  boxSizing: "border-box",
                  outline: "none",
                  fontFamily: "inherit",
                }}
              />

              {/* Action Buttons */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <button
                  type="button"
                  onClick={() => setCandidateAnswer("")}
                  style={{
                    background: "#f1f5f9",
                    border: "1px solid #e2e8f0",
                    color: "#64748b",
                    padding: "8px 16px",
                    borderRadius: "8px",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Clear
                </button>

                <button
                  type="button"
                  onClick={() => handleAnswerSubmit(candidateAnswer)}
                  style={{
                    background: "#6366f1",
                    border: "none",
                    color: "#ffffff",
                    padding: "8px 22px",
                    borderRadius: "8px",
                    fontSize: "0.84rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    boxShadow: "0 2px 6px rgba(99,102,241,0.3)",
                  }}
                >
                  <span>Submit Answer</span>
                  <Send size={14} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ═══════════════════════════════════════════════════════════════════ */}
        {/* PANEL 3 (RIGHT): QUESTION CONTEXT & CHAT WITH CYRA                  */}
        {/* ═══════════════════════════════════════════════════════════════════ */}
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {isDsa ? (
            /* DSA QUESTION SPECIFICATION CARD */
            <div
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #e2e8f0",
                boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                gap: "10px",
              }}
            >
              {/* Header: Question 1 of 5 + Easy Tag + DSA */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <Clock size={13} color="#64748b" />
                  <span style={{ fontSize: "0.78rem", fontWeight: 700, color: "#475569" }}>
                    Question {currentQIndex} of 5
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span
                    style={{
                      background: "#dcfce7",
                      color: "#166534",
                      fontSize: "0.7rem",
                      fontWeight: 800,
                      padding: "2px 8px",
                      borderRadius: "10px",
                    }}
                  >
                    {questionDifficulty}
                  </span>
                  <span
                    style={{
                      background: "#f1f5f9",
                      color: "#475569",
                      fontSize: "0.7rem",
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: "10px",
                    }}
                  >
                    DSA
                  </span>
                  {handleSpeakAgain && (
                    <button
                      type="button"
                      onClick={handleSpeakAgain}
                      disabled={isAgentSpeaking}
                      style={{
                        marginLeft: "6px",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                        background: isAgentSpeaking ? "#ede9fe" : "#f1f5f9",
                        color: isAgentSpeaking ? "#6d28d9" : "#334155",
                        border: "1px solid #cbd5e1",
                        borderRadius: "8px",
                        padding: "3px 8px",
                        fontSize: "0.72rem",
                        fontWeight: 700,
                        cursor: isAgentSpeaking ? "not-allowed" : "pointer",
                      }}
                      title="Replay Audio"
                    >
                      <Volume2 size={13} />
                      <span>{isAgentSpeaking ? "Speaking..." : "Speak Again"}</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Title & Description */}
              <div>
                <h4 style={{ margin: "4px 0 6px 0", fontSize: "1rem", fontWeight: 800, color: "#0f172a" }}>
                  {questionTitle}
                </h4>
                <p style={{ margin: 0, fontSize: "0.78rem", color: "#475569", lineHeight: 1.45 }}>
                  {questionText.split("\n\n")[0]}
                </p>
              </div>

              {/* Sample Example */}
              {examplesList.length > 0 && (
                <div
                  style={{
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "10px",
                    padding: "8px 10px",
                    fontSize: "0.74rem",
                    color: "#334155",
                    fontFamily: "monospace",
                  }}
                >
                  <div style={{ fontWeight: 700, color: "#0f172a", marginBottom: "4px" }}>
                    Example:
                  </div>
                  <div>Input: {examplesList[0].input}</div>
                  <div>Output: {examplesList[0].output}</div>
                </div>
              )}

              {/* Tabs: Constraints / Examples / Follow-up */}
              <div
                style={{
                  display: "flex",
                  borderBottom: "1px solid #e2e8f0",
                  marginTop: "4px",
                }}
              >
                {["constraints", "examples", "followup"].map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setRightTab(tab)}
                    style={{
                      flex: 1,
                      padding: "6px",
                      background: "none",
                      border: "none",
                      borderBottom: rightTab === tab ? "2px solid #6366f1" : "2px solid transparent",
                      color: rightTab === tab ? "#6366f1" : "#64748b",
                      fontSize: "0.74rem",
                      fontWeight: 700,
                      cursor: "pointer",
                      textTransform: "capitalize",
                    }}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div style={{ fontSize: "0.74rem", color: "#475569", lineHeight: 1.5 }}>
                {rightTab === "constraints" && (
                  <ul style={{ margin: 0, paddingLeft: "16px" }}>
                    {constraintsList.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                )}
                {rightTab === "examples" && (
                  <div>
                    {examplesList.map((ex, i) => (
                      <div key={i} style={{ marginBottom: "6px" }}>
                        <div><strong>Input:</strong> {ex.input}</div>
                        <div><strong>Output:</strong> {ex.output}</div>
                        {ex.explanation && <div><em>{ex.explanation}</em></div>}
                      </div>
                    ))}
                  </div>
                )}
                {rightTab === "followup" && (
                  <ul style={{ margin: 0, paddingLeft: "16px" }}>
                    {followUpsList.map((fu, i) => (
                      <li key={i}>{fu}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          ) : isBehavioral ? (
            /* BEHAVIORAL INTERVIEW PROGRESS & PRO TIPS */
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                  padding: "16px",
                }}
              >
                <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "8px" }}>
                  Interview Progress (2/10)
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.76rem" }}>
                  <div style={{ color: "#16a34a", fontWeight: 700 }}>• Introduction ✓</div>
                  <div style={{ color: "#6366f1", fontWeight: 800 }}>• Experience ➔</div>
                  <div style={{ color: "#94a3b8" }}>• Problem Solving ○</div>
                  <div style={{ color: "#94a3b8" }}>• Teamwork ○</div>
                  <div style={{ color: "#94a3b8" }}>• Leadership ○</div>
                  <div style={{ color: "#94a3b8" }}>• Communication ○</div>
                  <div style={{ color: "#94a3b8" }}>• Adaptability ○</div>
                  <div style={{ color: "#94a3b8" }}>• Future Goals ○</div>
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                  border: "1px solid #e2e8f0",
                  padding: "16px",
                }}
              >
                <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "6px" }}>
                  💡 Pro Tips
                </div>
                <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.76rem", color: "#475569", lineHeight: 1.6 }}>
                  <li>Be specific with examples</li>
                  <li>Use the STAR framework</li>
                  <li>Highlight your direct technical impact</li>
                  <li>Be honest and authentic</li>
                </ul>
              </div>
            </div>
          ) : (
            /* GITHUB & PROJECTS RELATED FILES & FOLLOW-UPS */
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
                  padding: "16px",
                }}
              >
                <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "10px" }}>
                  Related Files (CareerVerseAI)
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {relatedFilesList.map((rf, i) => (
                    <div
                      key={i}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "8px",
                        background: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        fontSize: "0.74rem",
                      }}
                    >
                      <div style={{ fontFamily: "monospace", fontWeight: 700, color: "#0f172a" }}>
                        {rf.file}
                      </div>
                      <div style={{ color: "#64748b" }}>{rf.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "18px",
                  border: "1px solid #e2e8f0",
                  padding: "16px",
                }}
              >
                <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a", marginBottom: "6px" }}>
                  Follow-up Suggestions
                </div>
                <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.74rem", color: "#475569", lineHeight: 1.5 }}>
                  {followUpsList.map((fu, i) => (
                    <li key={i}>{fu}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Chat with Cyra Box */}
          <div
            style={{
              background: "#ffffff",
              borderRadius: "18px",
              border: "1px solid #e2e8f0",
              boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
              padding: "14px 16px",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <MessageSquare size={14} color="#6366f1" />
              <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a" }}>
                Chat with Cyra
              </span>
            </div>

            {/* Message Thread */}
            <div
              style={{
                maxHeight: "130px",
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {chatMessages.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "8px",
                    justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  {msg.sender === "cyra" && (
                    <div
                      style={{
                        width: 22,
                        height: 22,
                        borderRadius: "50%",
                        background: "#6366f1",
                        color: "#ffffff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.65rem",
                        fontWeight: 800,
                        flexShrink: 0,
                      }}
                    >
                      🤖
                    </div>
                  )}
                  <div
                    style={{
                      background: msg.sender === "user" ? "#6366f1" : "#f1f5f9",
                      color: msg.sender === "user" ? "#ffffff" : "#0f172a",
                      padding: "6px 10px",
                      borderRadius: "10px",
                      fontSize: "0.74rem",
                      lineHeight: 1.4,
                      maxWidth: "85%",
                    }}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {isCyraThinking && (
                <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.72rem", color: "#6366f1", fontStyle: "italic", padding: "4px 8px" }}>
                  <div style={{ width: 18, height: 18, borderRadius: "50%", background: "#6366f1", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.6rem" }}>
                    🤖
                  </div>
                  <span>Cyra is thinking...</span>
                </div>
              )}
            </div>

            {/* Quick Action Chips */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={() => {
                  handleQuickAction("teach");
                  setCenterTab("teach");
                }}
                style={{
                  background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                  border: "none",
                  padding: "3px 10px",
                  borderRadius: "6px",
                  fontSize: "0.68rem",
                  fontWeight: 700,
                  color: "#ffffff",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  boxShadow: "0 2px 6px rgba(79,70,229,0.3)",
                }}
              >
                <Sparkles size={11} />
                <span>Teach me this</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickAction("hint")}
                style={{
                  background: "#f1f5f9",
                  border: "1px solid #e2e8f0",
                  padding: "3px 8px",
                  borderRadius: "6px",
                  fontSize: "0.68rem",
                  fontWeight: 600,
                  color: "#475569",
                  cursor: "pointer",
                }}
              >
                Give me a hint
              </button>
              <button
                type="button"
                onClick={() => handleQuickAction("constraints")}
                style={{
                  background: "#f1f5f9",
                  border: "1px solid #e2e8f0",
                  padding: "3px 8px",
                  borderRadius: "6px",
                  fontSize: "0.68rem",
                  fontWeight: 600,
                  color: "#475569",
                  cursor: "pointer",
                }}
              >
                Explain constraints
              </button>
              <button
                type="button"
                onClick={() => handleQuickAction("approach")}
                style={{
                  background: "#f1f5f9",
                  border: "1px solid #e2e8f0",
                  padding: "3px 8px",
                  borderRadius: "6px",
                  fontSize: "0.68rem",
                  fontWeight: 600,
                  color: "#475569",
                  cursor: "pointer",
                }}
              >
                Discuss approach
              </button>
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendCustomChat} style={{ display: "flex", gap: "6px" }}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type message to Cyra..."
                style={{
                  flex: 1,
                  background: "#f8fafc",
                  border: "1px solid #cbd5e1",
                  borderRadius: "8px",
                  padding: "6px 10px",
                  fontSize: "0.74rem",
                  outline: "none",
                }}
              />
              <button
                type="submit"
                style={{
                  background: "#6366f1",
                  border: "none",
                  borderRadius: "8px",
                  padding: "6px 12px",
                  color: "#ffffff",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Send size={12} />
              </button>
            </form>
          </div>
        </div>
      </div>
      {renderQuestionHistoryModal && renderQuestionHistoryModal()}
    </div>
  );
}

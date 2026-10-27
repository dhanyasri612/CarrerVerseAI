import React, { useState, useEffect, useMemo, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { marked } from "marked";
import {
  ArrowLeft as FiArrowLeft,
  Folder as FiFolder,
  FileText as FiFileText,
  Code2 as FiCode,
  Search as FiSearch,
  RefreshCw as FiRefreshCw,
  CheckCircle2 as FiCheckCircle,
  HelpCircle as FiHelpCircle,
  AlertTriangle as FiAlertTriangle,
  ChevronRight as FiChevronRight,
  ChevronDown as FiChevronDown,
  BookOpen as FiBookOpen,
  Layers as FiLayers,
  Shield as FiShield,
  Terminal as FiTerminal,
  Send as FiSend,
  ExternalLink as FiExternalLink,
  Compass as FiCompass,
  Info as FiInfo,
  ZoomIn as FiZoomIn,
  ZoomOut as FiZoomOut,
  Maximize2 as FiMaximize2,
  Download as FiDownload,
  Image as FiImage,
  Copy as FiCopy,
  Check as FiCheck,
  Eye as FiEye,
  FileCode as FiFileCode,
} from "lucide-react";
import {
  getGithubRepositories,
  getRepositoryFiles,
  getRepositoryFileContent,
  getFileExplanation,
  getCodeQuestionForFile,
  chatWithTeachingMentor,
  getProfileSnapshot,
} from "../services/careerService";
import "./TeachingStudioPage.css";

// Helper to safely render markdown text with GitHub Flavored Markdown
const renderMarkdown = (text) => {
  if (!text) return null;
  try {
    const rawHtml = marked.parse(String(text), { gfm: true, breaks: true });
    return <div className="teaching-markdown-content" dangerouslySetInnerHTML={{ __html: rawHtml }} />;
  } catch (e) {
    return <div className="teaching-markdown-content">{text}</div>;
  }
};

// File type detector
const getFileCategory = (path = "") => {
  const ext = (path.split(".").pop() || "").toLowerCase();
  if (["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "ico"].includes(ext)) return "image";
  if (["md", "markdown"].includes(ext)) return "markdown";
  if (["json", "yaml", "yml", "toml", "env", "ini", "lock"].includes(ext)) return "config";
  if (["pdf"].includes(ext)) return "pdf";
  if (["zip", "tar", "gz", "exe", "bin", "so", "dylib", "wasm"].includes(ext)) return "binary";
  return "code";
};

export default function RepositoryLearningPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const repoParamId = searchParams.get("repo");

  // State
  const [repositories, setRepositories] = useState([]);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [repoSearch, setRepoSearch] = useState("");
  const [selectedRepo, setSelectedRepo] = useState(null);

  // File tree
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [fileSearch, setFileSearch] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  // File content & explanation
  const [fileContent, setFileContent] = useState("");
  const [loadingContent, setLoadingContent] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  // File previewer interactive states
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [markdownViewMode, setMarkdownViewMode] = useState("rendered"); // 'rendered' | 'raw'
  const [copiedCode, setCopiedCode] = useState(false);
  const [selectedLines, setSelectedLines] = useState(null); // { start: number, end: number }

  // Socratic QA
  const [codeQuestion, setCodeQuestion] = useState(null);
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [studentAnswer, setStudentAnswer] = useState("");
  const [evaluatingAnswer, setEvaluatingAnswer] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [revealedHints, setRevealedHints] = useState([]);

  // Free-form Ask
  const [customQuestion, setCustomQuestion] = useState("");
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [qaHistory, setQaHistory] = useState([]);
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [qaHistory, askingQuestion]);

  // Progress tracking
  const [exploredFiles, setExploredFiles] = useState(new Set());
  const [masteredConcepts, setMasteredConcepts] = useState(new Set());

  // UI state
  const [activeTab, setActiveTab] = useState("overview"); // overview, structure, execution, security, example, qa
  const [statusMessage, setStatusMessage] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState(new Set(["root", "src"]));
  const [mentorPanelMode, setMentorPanelMode] = useState("spacious"); // "balanced" | "spacious" | "wide" | "focus"

  const gridColumns = useMemo(() => {
    if (mentorPanelMode === "focus") {
      return "0px 320px 1fr";
    }
    if (mentorPanelMode === "wide") {
      return "240px 1fr 680px";
    }
    if (mentorPanelMode === "balanced") {
      return "260px 1fr 460px";
    }
    // Default "spacious": gives generous width (minimum 520px, up to 45vw) to answer panel
    return "260px 1fr minmax(520px, 45vw)";
  }, [mentorPanelMode]);

  // Load all accessible repositories (subject to full pagination)
  const fetchRepositories = async (force = false) => {
    try {
      setLoadingRepos(true);
      setStatusMessage(null);
      // Fetch up to 1000 repos with pagination loop on backend
      const data = await getGithubRepositories({ limit: 1000, offset: 0 });
      const repoList = Array.isArray(data) ? data : data?.repositories || [];
      setRepositories(repoList);

      if (repoList.length > 0) {
        if (repoParamId) {
          const match = repoList.find((r) => String(r.id) === String(repoParamId) || r.name === repoParamId);
          if (match) setSelectedRepo(match);
          else setSelectedRepo(repoList[0]);
        } else if (!selectedRepo) {
          setSelectedRepo(repoList[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load repositories:", err);
      setStatusMessage({
        type: "error",
        text: "Could not load GitHub repositories. Please verify GitHub integration permissions.",
      });
    } finally {
      setLoadingRepos(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
  }, []);

  // When repo selection changes, load files
  useEffect(() => {
    if (!selectedRepo) return;
    const fetchFiles = async () => {
      try {
        setLoadingFiles(true);
        setSelectedFile(null);
        setFileContent("");
        setExplanation(null);
        setCodeQuestion(null);
        setEvaluationResult(null);
        setQaHistory([]);

        const data = await getRepositoryFiles(selectedRepo.id);
        const fileList = Array.isArray(data) ? data : data?.files || [];
        setFiles(fileList);

        // Auto-select entry point or first code file
        const entryFile = fileList.find(
          (f) =>
            !f.is_folder &&
            (f.file_name?.match(/^(index|main|app|server)\.(jsx?|tsx?|py|go|java)$/i) ||
              f.file_path?.includes("src/"))
        ) || fileList.find((f) => !f.is_folder);

        if (entryFile) {
          handleSelectFile(entryFile);
        }
      } catch (err) {
        console.error("Failed to load repository files:", err);
        setStatusMessage({
          type: "error",
          text: `Could not load files for ${selectedRepo.name}.`,
        });
      } finally {
        setLoadingFiles(false);
      }
    };
    fetchFiles();
  }, [selectedRepo]);

  // Handle file selection
  const handleSelectFile = async (file) => {
    if (file.is_folder) {
      toggleFolder(file.file_path || file.file_name);
      return;
    }
    setSelectedFile(file);
    setEvaluationResult(null);
    setStudentAnswer("");
    setRevealedHints([]);
    setSelectedLines(null);
    setZoomLevel(1);
    setMarkdownViewMode("rendered");

    // Mark as explored
    setExploredFiles((prev) => new Set(prev).add(file.file_path));

    const category = getFileCategory(file.file_path || file.file_name);

    try {
      setLoadingContent(true);
      setLoadingExplanation(true);
      setLoadingQuestion(true);

      // Fetch file content
      let content = file.content;
      if (!content && file.id) {
        try {
          const contentRes = await getRepositoryFileContent(file.id);
          content = typeof contentRes === "string" ? contentRes : contentRes?.content || "";
        } catch (e) {
          console.warn("Could not fetch remote content, checking direct asset links:", e);
        }
      }
      if (!content) {
        if (category === "image") {
          content = file.download_url || (selectedRepo?.full_name ? `https://raw.githubusercontent.com/${selectedRepo.full_name}/main/${file.file_path}` : "");
        } else if (category === "markdown") {
          content = `# ${file.file_name}\n\nDocumentation file from ${selectedRepo?.name || "repository"}.\n`;
        } else if (category === "binary") {
          content = `[BINARY_FILE:format=${file.file_name.split('.').pop() || 'binary'}:size=${file.size || 'unknown'}]`;
        } else {
          content = `// Source file: ${file.file_path || file.file_name}\n// Content loaded from repository structure\n`;
        }
      }
      setFileContent(content);
      setLoadingContent(false);

      // Fetch comprehensive 8-dimension file explanation
      try {
        const exp = await getFileExplanation({
          repository_id: selectedRepo.id,
          file_id: file.id,
          file_path: file.file_path,
          file_content: content,
        });
        setExplanation(exp);
      } catch (expErr) {
        console.warn("Explanation endpoint error, using heuristic model:", expErr);
      } finally {
        setLoadingExplanation(false);
      }

      // Fetch code understanding question
      try {
        const qRes = await getCodeQuestionForFile({
          repository_id: selectedRepo.id,
          file_id: file.id,
          file_path: file.file_path,
        });
        setCodeQuestion(qRes);
      } catch (qErr) {
        console.warn("Code question generation fallback:", qErr);
      } finally {
        setLoadingQuestion(false);
      }
    } catch (err) {
      console.error("File loading error:", err);
    } finally {
      setLoadingContent(false);
      setLoadingExplanation(false);
      setLoadingQuestion(false);
    }
  };

  const toggleFolder = (folderKey) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(folderKey)) next.delete(folderKey);
      else next.add(folderKey);
      return next;
    });
  };

  // Evaluate Socratic answer
  const handleSubmitAnswer = async (e) => {
    if (e) e.preventDefault();
    if (!studentAnswer.trim() || evaluatingAnswer) return;

    try {
      setEvaluatingAnswer(true);
      const res = await chatWithTeachingMentor({
        message: studentAnswer,
        teaching_mode: "project",
        target_id: selectedFile?.file_path || "Repository File",
        workspace_code: fileContent,
        is_assessment: true,
      });

      setEvaluationResult(res);
      if (res?.demonstrated_understanding) {
        if (explanation?.programming_concepts) {
          setMasteredConcepts((prev) => {
            const next = new Set(prev);
            explanation.programming_concepts.forEach((c) => next.add(c));
            return next;
          });
        }
      }
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setEvaluatingAnswer(false);
    }
  };

  // Ask custom question about file or whole repository
  const handleAskCustom = async (e, customText) => {
    if (e && e.preventDefault) e.preventDefault();
    const query = (typeof customText === "string" ? customText : customQuestion).trim();
    if (!query || askingQuestion) return;

    setCustomQuestion("");
    setQaHistory((prev) => [...prev, { role: "user", content: query }]);

    try {
      setAskingQuestion(true);
      const res = await chatWithTeachingMentor({
        message: query,
        teaching_mode: "project",
        mode: "project",
        target_id: String(selectedRepo?.id || selectedRepo?.name || "Codebase"),
        repository_id: selectedRepo?.id,
        file_path: selectedFile?.file_path,
        workspace_code: fileContent || undefined,
        is_assessment: false,
      });

      setQaHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res?.reply || "I analyzed your code and repository architecture.",
          citations: res?.citations || [],
        },
      ]);
    } catch (err) {
      console.error("Ask question error:", err);
      setQaHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I encountered an error analyzing the repository. Please retry in a moment.",
        },
      ]);
    } finally {
      setAskingQuestion(false);
    }
  };

  // Filter repos & files
  const filteredRepos = useMemo(() => {
    if (!repoSearch.trim()) return repositories;
    const q = repoSearch.toLowerCase();
    return repositories.filter(
      (r) =>
        r.name?.toLowerCase().includes(q) ||
        r.description?.toLowerCase().includes(q) ||
        r.language?.toLowerCase().includes(q)
    );
  }, [repositories, repoSearch]);

  const filteredFiles = useMemo(() => {
    if (!fileSearch.trim()) return files;
    const q = fileSearch.toLowerCase();
    return files.filter(
      (f) =>
        f.file_name?.toLowerCase().includes(q) ||
        f.file_path?.toLowerCase().includes(q)
    );
  }, [files, fileSearch]);

  return (
    <div className="teaching-studio-page">
      {/* ── Top Header ────────────────────────────────────────── */}
      <header className="teaching-header">
        <div className="teaching-header-brand">
          <Link to="/ai/teaching" className="teaching-back-link">
            <FiArrowLeft /> Back to Teaching Hub
          </Link>
          <div className="teaching-divider-v" />
          <div className="teaching-title-group">
            <h1 className="teaching-title-text">Repository Learning Studio</h1>
            <span className="teaching-mentor-badge">
              <FiCode /> Dr. Cyra Vance • Codebase Deep-Dive
            </span>
          </div>
        </div>

        <div className="teaching-header-controls">
          <button
            className="teaching-header-btn"
            onClick={() => fetchRepositories(true)}
            title="Refresh authorized repositories from GitHub"
          >
            <FiRefreshCw className={loadingRepos ? "spin-icon" : ""} /> Refresh Repos
          </button>
        </div>
      </header>

      {/* ── Status Notice ─────────────────────────────────────── */}
      {statusMessage && (
        <div
          style={{
            padding: "10px 24px",
            background: statusMessage.type === "error" ? "rgba(239, 68, 68, 0.1)" : "rgba(99, 102, 241, 0.1)",
            borderBottom: "1px solid var(--cv-border, #e5e2d9)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "0.86rem",
          }}
        >
          <FiAlertTriangle color={statusMessage.type === "error" ? "#ef4444" : "#6366f1"} />
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* ── Main 3-Column Code Learning Layout ────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: gridColumns,
          height: "calc(100vh - 65px)",
          overflow: "hidden",
          background: "var(--cv-bg, var(--surface))",
          transition: "grid-template-columns 0.2s ease",
        }}
      >
        {/* ── LEFT PANEL: Repository Explorer & File Tree ─────── */}
        <aside
          style={{
            borderRight: "1px solid var(--cv-border, #e5e2d9)",
            background: "var(--cv-surface, #ffffff)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Repo Selector Header */}
          <div style={{ padding: "14px 16px", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
            <div style={{ fontSize: "0.74rem", textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "6px" }}>
              Authorized Repositories ({repositories.length})
            </div>
            <select
              style={{
                width: "100%",
                padding: "8px 10px",
                borderRadius: "6px",
                border: "1px solid var(--cv-border, #e5e2d9)",
                background: "var(--cv-bg, #fbf9f4)",
                color: "var(--cv-text, #1c1c1e)",
                fontWeight: 600,
                fontSize: "0.88rem",
              }}
              value={selectedRepo?.id || ""}
              onChange={(e) => {
                const found = repositories.find((r) => String(r.id) === e.target.value);
                if (found) {
                  setSelectedRepo(found);
                  setSearchParams({ repo: found.id });
                }
              }}
            >
              {repositories.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} {r.language ? `(${r.language})` : ""}
                </option>
              ))}
            </select>
          </div>

          {/* File Search */}
          <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                background: "var(--cv-bg, #fbf9f4)",
                border: "1px solid var(--cv-border, #e5e2d9)",
                borderRadius: "6px",
                padding: "6px 10px",
              }}
            >
              <FiSearch color="var(--cv-text-muted, #71717a)" size={14} />
              <input
                type="text"
                placeholder="Search repository files..."
                value={fileSearch}
                onChange={(e) => setFileSearch(e.target.value)}
                style={{
                  border: "none",
                  background: "transparent",
                  outline: "none",
                  width: "100%",
                  fontSize: "0.82rem",
                  color: "var(--cv-text, #1c1c1e)",
                }}
              />
            </div>
          </div>

          {/* Files List */}
          <div style={{ flex: 1, overflowY: "auto", padding: "8px 6px" }}>
            {loadingFiles ? (
              <div style={{ padding: "20px", textAlign: "center", color: "var(--cv-text-muted, #71717a)", fontSize: "0.85rem" }}>
                <FiRefreshCw className="spin-icon" style={{ marginBottom: "6px" }} />
                <div>Reading repository tree...</div>
              </div>
            ) : filteredFiles.length === 0 ? (
              <div style={{ padding: "20px", textAlign: "center", color: "var(--cv-text-muted, #71717a)", fontSize: "0.85rem" }}>
                No files found in this repository.
              </div>
            ) : (
              filteredFiles.map((file) => {
                const isSelected = selectedFile?.id === file.id || selectedFile?.file_path === file.file_path;
                const isExplored = exploredFiles.has(file.file_path);

                return (
                  <button
                    key={file.id || file.file_path}
                    onClick={() => handleSelectFile(file)}
                    style={{
                      width: "100%",
                      textAlign: "left",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "8px",
                      padding: "7px 10px",
                      borderRadius: "6px",
                      border: "none",
                      background: isSelected ? "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))" : "transparent",
                      color: isSelected ? "var(--cv-accent, #6366f1)" : "var(--cv-text, #1c1c1e)",
                      cursor: "pointer",
                      fontSize: "0.82rem",
                      fontWeight: isSelected ? 600 : 400,
                      marginBottom: "2px",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "7px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {file.is_folder ? (
                        <FiFolder color="var(--cv-accent, #6366f1)" size={14} />
                      ) : (
                        <FiFileText color="var(--cv-text-muted, #71717a)" size={14} />
                      )}
                      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {file.file_name || file.file_path}
                      </span>
                    </div>

                    {isExplored && (
                      <span title="File Explored" style={{ color: "#10b981", fontSize: "0.75rem" }}>
                        ✓
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* Repo Stats Footer */}
          <div
            style={{
              padding: "12px 16px",
              borderTop: "1px solid var(--cv-border, #e5e2d9)",
              fontSize: "0.76rem",
              color: "var(--cv-text-muted, #71717a)",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>Files: {files.length}</span>
            <span>Explored: {exploredFiles.size}</span>
            <span>Mastered: {masteredConcepts.size}</span>
          </div>
        </aside>

        {/* ── CENTER PANEL: Code Viewer with Line Numbers ─────── */}
        <main
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            borderRight: "1px solid var(--cv-border, #e5e2d9)",
            background: "var(--cv-surface-2, rgba(0, 0, 0, 0.02))",
          }}
        >
          {/* File Tab Header */}
          <div
            style={{
              padding: "10px 20px",
              background: "var(--cv-surface, #ffffff)",
              borderBottom: "1px solid var(--cv-border, #e5e2d9)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "8px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              {getFileCategory(selectedFile?.file_path) === "image" ? (
                <FiImage color="var(--cv-accent, #6366f1)" size={16} />
              ) : getFileCategory(selectedFile?.file_path) === "markdown" ? (
                <FiFileText color="var(--cv-accent, #6366f1)" size={16} />
              ) : (
                <FiCode color="var(--cv-accent, #6366f1)" size={16} />
              )}
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                {selectedFile?.file_path || "Select a file to inspect"}
              </span>
              {selectedFile && (
                <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "4px", background: "var(--cv-accent-soft, rgba(99, 102, 241, 0.1))", color: "var(--cv-accent, #6366f1)", fontWeight: 600 }}>
                  {getFileCategory(selectedFile?.file_path).toUpperCase()}
                </span>
              )}
              {selectedRepo && (
                <span style={{ fontSize: "0.75rem", color: "var(--cv-text-muted, #71717a)" }}>
                  ({selectedRepo.name})
                </span>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              {getFileCategory(selectedFile?.file_path) === "markdown" && (
                <div style={{ display: "flex", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "6px", overflow: "hidden" }}>
                  <button
                    onClick={() => setMarkdownViewMode("rendered")}
                    style={{
                      padding: "4px 8px",
                      border: "none",
                      background: markdownViewMode === "rendered" ? "var(--cv-accent, #6366f1)" : "var(--cv-surface, #fff)",
                      color: markdownViewMode === "rendered" ? "#fff" : "var(--cv-text, #1c1c1e)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <FiEye size={12} /> Rendered
                  </button>
                  <button
                    onClick={() => setMarkdownViewMode("raw")}
                    style={{
                      padding: "4px 8px",
                      border: "none",
                      background: markdownViewMode === "raw" ? "var(--cv-accent, #6366f1)" : "var(--cv-surface, #fff)",
                      color: markdownViewMode === "raw" ? "#fff" : "var(--cv-text, #1c1c1e)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <FiFileCode size={12} /> Source
                  </button>
                </div>
              )}

              {getFileCategory(selectedFile?.file_path) === "code" && (
                <button
                  onClick={() => {
                    navigator.clipboard?.writeText(fileContent);
                    setCopiedCode(true);
                    setTimeout(() => setCopiedCode(false), 2000);
                  }}
                  style={{
                    padding: "4px 8px",
                    border: "1px solid var(--cv-border, #e5e2d9)",
                    borderRadius: "6px",
                    background: "var(--cv-surface, #fff)",
                    fontSize: "0.75rem",
                    color: "var(--cv-text-muted, #71717a)",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    cursor: "pointer",
                  }}
                >
                  {copiedCode ? <FiCheck size={12} color="#10b981" /> : <FiCopy size={12} />}
                  {copiedCode ? "Copied" : "Copy"}
                </button>
              )}

              {selectedRepo?.html_url && selectedFile && (
                <a
                  href={`${selectedRepo.html_url}/blob/main/${selectedFile.file_path}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    fontSize: "0.78rem",
                    color: "var(--cv-accent, #6366f1)",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    textDecoration: "none",
                  }}
                >
                  View on GitHub <FiExternalLink size={12} />
                </a>
              )}
            </div>
          </div>

          {/* Line Selection Quick-Ask Banner */}
          {selectedLines && (
            <div
              style={{
                padding: "8px 20px",
                background: "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))",
                borderBottom: "1px solid var(--cv-border, #e5e2d9)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "0.82rem",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontWeight: 600, color: "var(--cv-accent, #6366f1)" }}>
                  Selected Lines: L{selectedLines.start} - L{selectedLines.end}
                </span>
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => {
                    setActiveTab("qa");
                    setCustomQuestion(
                      `In ${selectedFile?.file_path} (lines L${selectedLines.start}-L${selectedLines.end}), explain what this code block executes and what invariants it preserves.`
                    );
                  }}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "4px",
                    border: "none",
                    background: "var(--cv-accent, #6366f1)",
                    color: "#fff",
                    fontSize: "0.76rem",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Ask Dr. Cyra About These Lines
                </button>
                <button
                  onClick={() => setSelectedLines(null)}
                  style={{
                    padding: "4px 8px",
                    borderRadius: "4px",
                    border: "1px solid var(--cv-border, #e5e2d9)",
                    background: "var(--cv-surface, #fff)",
                    fontSize: "0.76rem",
                    cursor: "pointer",
                    color: "var(--cv-text-muted, #71717a)",
                  }}
                >
                  Clear Selection
                </button>
              </div>
            </div>
          )}

          {/* Code Viewer Body */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "16px",
              fontFamily: "var(--cv-font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace)",
              fontSize: "0.82rem",
              lineHeight: 1.6,
            }}
          >
            {loadingContent ? (
              <div style={{ padding: "40px", textAlign: "center", color: "var(--cv-text-muted, #71717a)" }}>
                <FiRefreshCw className="spin-icon" style={{ marginBottom: "8px" }} />
                <div>Reading repository content...</div>
              </div>
            ) : !selectedFile ? (
              <div
                style={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--cv-text-muted, #71717a)",
                  textAlign: "center",
                  padding: "40px",
                }}
              >
                <FiBookOpen size={48} style={{ opacity: 0.3, marginBottom: "14px" }} />
                <h3 style={{ margin: "0 0 6px 0", fontSize: "1.1rem" }}>Select a Repository File</h3>
                <p style={{ maxWidth: "340px", margin: 0, fontSize: "0.85rem" }}>
                  Browse any file or image from your repository in the left panel to inspect its architecture, design role, and concepts.
                </p>
              </div>
            ) : getFileCategory(selectedFile.file_path) === "image" ? (
              /* ── REAL IMAGE PREVIEWER ──────────────────────────────── */
              <div className="image-preview-container">
                <div className="image-preview-toolbar">
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <FiImage size={15} color="var(--cv-accent, #6366f1)" />
                    <span style={{ fontWeight: 600 }}>{selectedFile.file_name}</span>
                    <span style={{ fontSize: "0.72rem", background: "var(--cv-accent-soft, rgba(99, 102, 241, 0.1))", color: "var(--cv-accent, #6366f1)", padding: "2px 6px", borderRadius: "4px", fontWeight: 600 }}>
                      Image Asset ({(selectedFile.file_path.split(".").pop() || "PNG").toUpperCase()})
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      onClick={() => setZoomLevel((z) => Math.max(0.25, z - 0.25))}
                      style={{ padding: "4px 6px", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "4px", background: "var(--cv-surface, #fff)", cursor: "pointer" }}
                      title="Zoom Out"
                    >
                      <FiZoomOut size={13} />
                    </button>
                    <span style={{ fontSize: "0.75rem", fontWeight: 600, minWidth: "40px", textAlign: "center" }}>
                      {Math.round(zoomLevel * 100)}%
                    </span>
                    <button
                      onClick={() => setZoomLevel((z) => Math.min(3, z + 0.25))}
                      style={{ padding: "4px 6px", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "4px", background: "var(--cv-surface, #fff)", cursor: "pointer" }}
                      title="Zoom In"
                    >
                      <FiZoomIn size={13} />
                    </button>
                    <button
                      onClick={() => setZoomLevel(1)}
                      style={{ padding: "4px 6px", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "4px", background: "var(--cv-surface, #fff)", cursor: "pointer" }}
                      title="Reset Zoom"
                    >
                      <FiMaximize2 size={13} />
                    </button>
                    {fileContent && (
                      <a
                        href={fileContent}
                        download={selectedFile.file_name}
                        style={{ padding: "4px 6px", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "4px", background: "var(--cv-surface, #fff)", cursor: "pointer", color: "inherit", display: "flex", alignItems: "center" }}
                        title="Download Asset"
                      >
                        <FiDownload size={13} />
                      </a>
                    )}
                  </div>
                </div>

                <div className="image-preview-canvas">
                  <img
                    src={fileContent}
                    alt={selectedFile.file_name}
                    className="image-preview-element"
                    style={{ transform: `scale(${zoomLevel})` }}
                    onLoad={(e) => {
                      setImageDimensions({
                        width: e.target.naturalWidth,
                        height: e.target.naturalHeight,
                      });
                    }}
                    onError={(e) => {
                      console.warn("Direct image load failed, attempting fallback:", e);
                    }}
                  />
                </div>

                <div className="image-metadata-strip">
                  <span>Resolution: {imageDimensions.width ? `${imageDimensions.width} × ${imageDimensions.height} px` : "Dynamic Render"}</span>
                  <span>Format: {(selectedFile.file_path.split(".").pop() || "PNG").toUpperCase()}</span>
                  <span>Path: {selectedFile.file_path}</span>
                  {selectedRepo?.html_url && (
                    <a
                      href={`${selectedRepo.html_url}/blob/main/${selectedFile.file_path}`}
                      target="_blank"
                      rel="noreferrer"
                      style={{ marginLeft: "auto", color: "var(--cv-accent, #6366f1)", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px" }}
                    >
                      Original Asset <FiExternalLink size={12} />
                    </a>
                  )}
                </div>
              </div>
            ) : getFileCategory(selectedFile.file_path) === "markdown" && markdownViewMode === "rendered" ? (
              /* ── FORMATTED MARKDOWN VIEWER ────────────────────────── */
              <div
                style={{
                  background: "var(--cv-surface, #ffffff)",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  borderRadius: "8px",
                  padding: "24px",
                }}
              >
                {renderMarkdown(fileContent)}
              </div>
            ) : getFileCategory(selectedFile.file_path) === "binary" ? (
              /* ── BINARY / UNSUPPORTED FILE VIEWER ──────────────────── */
              <div
                style={{
                  background: "var(--cv-surface, #ffffff)",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  borderRadius: "8px",
                  padding: "32px 24px",
                  textAlign: "center",
                }}
              >
                <FiShield size={40} color="var(--cv-text-muted, #71717a)" style={{ opacity: 0.4, marginBottom: "12px" }} />
                <h3 style={{ margin: "0 0 8px 0", fontSize: "1.05rem" }}>Binary or Compiled File</h3>
                <p style={{ maxWidth: "420px", margin: "0 auto 16px auto", fontSize: "0.84rem", color: "var(--cv-text-muted, #71717a)" }}>
                  This file (<code>{selectedFile.file_name}</code>) is a compiled binary or non-text resource. It cannot be edited or viewed as source code.
                </p>
                {selectedRepo?.html_url && (
                  <a
                    href={`${selectedRepo.html_url}/raw/main/${selectedFile.file_path}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "8px 14px",
                      borderRadius: "6px",
                      background: "var(--cv-accent, #6366f1)",
                      color: "#fff",
                      textDecoration: "none",
                      fontSize: "0.82rem",
                      fontWeight: 600,
                    }}
                  >
                    Download Binary File <FiDownload size={13} />
                  </a>
                )}
              </div>
            ) : (
              /* ── SOURCE CODE / CONFIG VIEWER WITH LINE SELECTION ──── */
              <div
                style={{
                  background: "var(--cv-surface, #ffffff)",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  borderRadius: "8px",
                  overflow: "hidden",
                }}
              >
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <tbody>
                    {fileContent.split("\n").map((line, idx) => {
                      const lineNum = idx + 1;
                      const isLineSelected =
                        selectedLines &&
                        lineNum >= selectedLines.start &&
                        lineNum <= selectedLines.end;

                      return (
                        <tr
                          key={idx}
                          onClick={() => {
                            if (!selectedLines) {
                              setSelectedLines({ start: lineNum, end: lineNum });
                            } else if (selectedLines.start === lineNum && selectedLines.end === lineNum) {
                              setSelectedLines(null);
                            } else {
                              const start = Math.min(selectedLines.start, lineNum);
                              const end = Math.max(selectedLines.start, lineNum);
                              setSelectedLines({ start, end });
                            }
                          }}
                          style={{
                            verticalAlign: "top",
                            cursor: "pointer",
                            background: isLineSelected
                              ? "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))"
                              : "transparent",
                          }}
                        >
                          <td
                            style={{
                              width: "44px",
                              padding: "2px 10px",
                              textAlign: "right",
                              color: isLineSelected ? "var(--cv-accent, #6366f1)" : "var(--cv-text-muted, #71717a)",
                              userSelect: "none",
                              borderRight: "1px solid var(--cv-border, #e5e2d9)",
                              background: isLineSelected ? "rgba(99, 102, 241, 0.15)" : "var(--cv-bg, #fbf9f4)",
                              fontSize: "0.75rem",
                              fontWeight: isLineSelected ? 700 : 400,
                            }}
                          >
                            {lineNum}
                          </td>
                          <td
                            style={{
                              padding: "2px 14px",
                              whiteSpace: "pre-wrap",
                              wordBreak: "break-word",
                              color: "var(--cv-text, #1c1c1e)",
                            }}
                          >
                            {line || " "}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>

        {/* ── RIGHT PANEL: Whole-Repository AI Mentor Q&A Studio ── */}
        <aside
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: "var(--cv-surface, #ffffff)",
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "14px 16px",
              borderBottom: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-bg, #fbf9f4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "50%",
                  background: "var(--cv-accent, #6366f1)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: "0.85rem",
                  boxShadow: "0 2px 6px rgba(99, 102, 241, 0.25)",
                }}
              >
                CV
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: "0.88rem", color: "var(--cv-text, #1c1c1e)" }}>
                  Dr. Cyra Vance
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--cv-text-muted, #71717a)" }}>
                  Whole-Repository AI Mentor & Architect
                </div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                style={{
                  display: "inline-block",
                  padding: "3px 8px",
                  borderRadius: "12px",
                  background: "var(--cv-accent-soft, rgba(52, 211, 153, 0.12))",
                  color: "var(--cv-accent, #34d399)",
                  fontSize: "0.72rem",
                  fontWeight: 600,
                }}
              >
                {files.length} Files Analyzed
              </span>
              <button
                onClick={() =>
                  setMentorPanelMode((prev) =>
                    prev === "spacious" ? "wide" : prev === "wide" ? "focus" : "spacious"
                  )
                }
                title={
                  mentorPanelMode === "focus"
                    ? "Reset to standard spacious view"
                    : mentorPanelMode === "wide"
                    ? "Focus answer (maximum reading width)"
                    : "Expand answer panel width"
                }
                style={{
                  padding: "4px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #303734)",
                  background: "var(--cv-surface-raised, #2e3432)",
                  color: "var(--cv-text, #edf2ee)",
                  fontSize: "0.72rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                }}
              >
                <FiMaximize2 size={12} />
                {mentorPanelMode === "focus"
                  ? "Standard"
                  : mentorPanelMode === "wide"
                  ? "Focus Max"
                  : "Expand View"}
              </button>
            </div>
          </div>

          {/* Active File Context Pill (if file clicked in explorer) */}
          {selectedFile && (
            <div
              style={{
                padding: "6px 14px",
                background: "var(--cv-surface, #ffffff)",
                borderBottom: "1px solid var(--cv-border, #e5e2d9)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "0.74rem",
                color: "var(--cv-text-muted, #71717a)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "6px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                <span style={{ fontWeight: 600, color: "var(--cv-accent, #6366f1)" }}>Active Inspecting File:</span>
                <code style={{ fontSize: "0.74rem", background: "var(--cv-bg, #fbf9f4)", padding: "1px 5px", borderRadius: "3px" }}>
                  {selectedFile.file_name}
                </code>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                title="Clear file focus (Ask about whole repo only)"
                style={{
                  border: "none",
                  background: "transparent",
                  color: "var(--cv-text-muted, #71717a)",
                  cursor: "pointer",
                  fontSize: "0.72rem",
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                ✕ Clear
              </button>
            </div>
          )}

          {/* Suggested Quick Prompt Chips */}
          <div
            style={{
              padding: "8px 12px",
              borderBottom: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-bg, #fbf9f4)",
              display: "flex",
              flexWrap: "wrap",
              gap: "6px",
            }}
          >
            {[
              {
                label: "🏛️ Repo Walkthrough",
                prompt: "Can you provide a comprehensive architectural walkthrough of everything implemented in this repository, including its purpose, structure, and core flows?",
              },
              {
                label: "🔄 End-to-End Data Flow",
                prompt: "How does end-to-end data and request flow work across this entire repository, from entry points to persistence?",
              },
              {
                label: "🛠️ Tech Stack & Architecture",
                prompt: "What is the complete technology stack, frameworks, packages, and design patterns implemented across this codebase?",
              },
              {
                label: "🔑 Entry Points & Key Modules",
                prompt: "What are the primary application entry points and key modules in this repository, and how do they interact?",
              },
              {
                label: "🛡️ Security & Trade-offs",
                prompt: "What security considerations, edge cases, error handling, or engineering trade-offs exist across this codebase?",
              },
              ...(selectedFile
                ? [
                    {
                      label: `📄 Connect ${selectedFile.file_name}`,
                      prompt: `How does ${selectedFile.file_path || selectedFile.file_name} connect to the rest of the repository architecture and what role does it play?`,
                    },
                  ]
                : []),
            ].map((btn, idx) => (
              <button
                key={idx}
                onClick={() => handleAskCustom(null, btn.prompt)}
                disabled={askingQuestion}
                style={{
                  fontSize: "0.72rem",
                  padding: "4px 8px",
                  borderRadius: "14px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "var(--cv-surface, #ffffff)",
                  color: "var(--cv-text, #1c1c1e)",
                  cursor: askingQuestion ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  whiteSpace: "nowrap",
                  transition: "all 0.15s ease",
                  opacity: askingQuestion ? 0.6 : 1,
                }}
              >
                {btn.label}
              </button>
            ))}
          </div>

          {/* Chat Message Stream */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "16px",
              display: "flex",
              flexDirection: "column",
              gap: "14px",
            }}
          >
            {qaHistory.length === 0 ? (
              <div
                style={{
                  padding: "24px 12px",
                  textAlign: "center",
                  color: "var(--cv-text, #1c1c1e)",
                  margin: "auto 0",
                }}
              >
                <div
                  style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "50%",
                    background: "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "12px",
                    color: "var(--cv-accent, #6366f1)",
                  }}
                >
                  <FiBookOpen size={22} />
                </div>
                <h3 style={{ margin: "0 0 6px 0", fontSize: "0.98rem", fontWeight: 700 }}>
                  Whole-Repository Teaching Studio
                </h3>
                <p
                  style={{
                    fontSize: "0.82rem",
                    color: "var(--cv-text-muted, #71717a)",
                    lineHeight: 1.5,
                    maxWidth: "340px",
                    margin: "0 auto 16px auto",
                  }}
                >
                  I've parsed and analyzed all <strong>{files.length} indexed files</strong> in{" "}
                  <strong>{selectedRepo?.name || "this repository"}</strong>. Click a suggestion above or ask me anything
                  about how the complete project is constructed!
                </p>
                <div
                  style={{
                    display: "inline-flex",
                    flexDirection: "column",
                    gap: "6px",
                    textAlign: "left",
                    width: "100%",
                    maxWidth: "340px",
                  }}
                >
                  <button
                    onClick={() =>
                      handleAskCustom(
                        null,
                        "Can you explain everything implemented in this repository, its core purpose, and how all components fit together?"
                      )
                    }
                    style={{
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid var(--cv-border, #e5e2d9)",
                      background: "var(--cv-bg, #fbf9f4)",
                      fontSize: "0.78rem",
                      cursor: "pointer",
                      textAlign: "left",
                      color: "var(--cv-text, #1c1c1e)",
                    }}
                  >
                    👉 <strong>Explain everything in this repository</strong>
                  </button>
                  <button
                    onClick={() =>
                      handleAskCustom(
                        null,
                        "Walk me through the complete end-to-end data flow and execution path from entry points to persistence."
                      )
                    }
                    style={{
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid var(--cv-border, #e5e2d9)",
                      background: "var(--cv-bg, #fbf9f4)",
                      fontSize: "0.78rem",
                      cursor: "pointer",
                      textAlign: "left",
                      color: "var(--cv-text, #1c1c1e)",
                    }}
                  >
                    👉 <strong>Trace complete end-to-end data flow</strong>
                  </button>
                </div>
              </div>
            ) : (
              qaHistory.map((item, i) => {
                const isUser = item.role === "user";
                return (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: isUser ? "flex-end" : "flex-start",
                      width: "100%",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        color: "var(--cv-text-muted, #71717a)",
                        marginBottom: "4px",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      {isUser ? "You" : "Dr. Cyra Vance"}
                    </div>

                    {isUser ? (
                      <div className="teaching-user-question-bubble">
                        <div style={{ whiteSpace: "pre-wrap" }}>{item.content}</div>
                      </div>
                    ) : (
                      <div className="teaching-mentor-answer-card">
                        <div>{renderMarkdown(item.content)}</div>

                        {/* Verified Citations */}
                        {item.citations && item.citations.length > 0 && (
                          <div
                            style={{
                              marginTop: "12px",
                              paddingTop: "10px",
                              borderTop: "1px dashed var(--cv-border, #303734)",
                              fontSize: "0.74rem",
                              color: "var(--cv-text-muted, #8e9c94)",
                            }}
                          >
                            <div
                              style={{
                                fontWeight: 700,
                                marginBottom: "6px",
                                textTransform: "uppercase",
                                letterSpacing: "0.04em",
                                fontSize: "0.7rem",
                                color: "var(--cv-accent, #34d399)",
                              }}
                            >
                              Referenced Repository Assets:
                            </div>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                              {item.citations.map((c, cIdx) => (
                                <span
                                  key={cIdx}
                                  style={{
                                    padding: "3px 8px",
                                    borderRadius: "4px",
                                    background: "var(--cv-surface-raised, #2e3432)",
                                    border: "1px solid var(--cv-border, #303734)",
                                    fontSize: "0.72rem",
                                    color: "var(--cv-text, #edf2ee)",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "4px",
                                  }}
                                >
                                  📄 {c.source_title || c.file_path || c.title}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}

            {/* In-Flight Thinking Indicator */}
            {askingQuestion && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  width: "100%",
                }}
              >
                <div
                  style={{
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    color: "var(--cv-text-muted, #71717a)",
                    marginBottom: "4px",
                  }}
                >
                  Dr. Cyra Vance
                </div>
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: "12px 12px 12px 2px",
                    background: "var(--cv-bg, #fbf9f4)",
                    border: "1px solid var(--cv-border, #e5e2d9)",
                    fontSize: "0.82rem",
                    color: "var(--cv-text-muted, #71717a)",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <FiRefreshCw className="spin-icon" size={14} color="var(--cv-accent, #6366f1)" />
                  <span>Dr. Cyra is analyzing the complete repository codebase...</span>
                </div>
              </div>
            )}

            <div ref={chatBottomRef} />
          </div>

          {/* Chat Input Bar */}
          <div
            style={{
              padding: "12px",
              borderTop: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-surface, #ffffff)",
            }}
          >
            <form onSubmit={handleAskCustom} style={{ display: "flex", gap: "8px" }}>
              <input
                type="text"
                placeholder={
                  selectedFile
                    ? `Ask about ${selectedFile.file_name} or entire repository...`
                    : "Ask Dr. Cyra about this entire repository, features, or architecture..."
                }
                value={customQuestion}
                onChange={(e) => setCustomQuestion(e.target.value)}
                disabled={askingQuestion}
                style={{
                  flex: 1,
                  padding: "9px 12px",
                  borderRadius: "8px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "var(--cv-bg, #fbf9f4)",
                  fontSize: "0.84rem",
                  color: "var(--cv-text, #1c1c1e)",
                  outline: "none",
                }}
              />
              <button
                type="submit"
                disabled={!customQuestion.trim() || askingQuestion}
                style={{
                  padding: "9px 14px",
                  borderRadius: "8px",
                  background: "var(--cv-accent, #6366f1)",
                  color: "#fff",
                  border: "none",
                  cursor: !customQuestion.trim() || askingQuestion ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  opacity: !customQuestion.trim() || askingQuestion ? 0.5 : 1,
                }}
              >
                <FiSend size={15} />
              </button>
            </form>
          </div>
        </aside>
      </div>
    </div>
  );
}

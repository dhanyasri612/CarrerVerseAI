import React, { useState, useRef } from "react";
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Trash2,
  X,
  Search,
  BookOpen,
  FileCode,
  File,
  Layers,
  Sparkles,
} from "lucide-react";

export const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15 MB
export const ALLOWED_EXTENSIONS = [".pdf", ".md", ".markdown", ".txt"];

export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return "0 KB";
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

export const getFormatIcon = (fileType, filename = "") => {
  const ext = (fileType || filename.split(".").pop() || "").toLowerCase();
  if (ext === "pdf" || ext.endsWith("pdf")) {
    return <FileText size={18} style={{ color: "#ef4444" }} />;
  }
  if (ext === "md" || ext === "markdown" || ext.endsWith("md")) {
    return <FileCode size={18} style={{ color: "#3b82f6" }} />;
  }
  return <File size={18} style={{ color: "#10b981" }} />;
};

export default function CourseMaterialsManager({
  documents = [],
  loading = false,
  error = "",
  onRefresh,
  onUpload,
  onDelete,
  onSelectDocumentForChat,
  selectedDocumentId,
}) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccessMsg, setUploadSuccessMsg] = useState("");
  const [uploadErrorMsg, setUploadErrorMsg] = useState("");
  const [searchFilter, setSearchFilter] = useState("");
  const [docToDelete, setDocToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Validate and execute upload
  const processUpload = async (file) => {
    if (!file) return;
    setUploadSuccessMsg("");
    setUploadErrorMsg("");

    // 1. Extension check
    const name = file.name.toLowerCase();
    const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
    if (!hasValidExt) {
      setUploadErrorMsg(
        `Unsupported file type for "${file.name}". Please upload a PDF, Markdown (.md), or Plain Text (.txt) file.`
      );
      return;
    }

    // 2. 15 MB size check
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setUploadErrorMsg(
        `File "${file.name}" exceeds the 15 MB limit (${formatFileSize(file.size)}). Please choose a smaller file.`
      );
      return;
    }

    // 3. 0 byte check
    if (file.size === 0) {
      setUploadErrorMsg(`File "${file.name}" is empty (0 bytes).`);
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(0);

      const res = await onUpload(file, (progressEvent) => {
        if (progressEvent.total) {
          const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(pct);
        }
      });

      const uploadedDoc = res?.document || res;
      const degradedNote =
        uploadedDoc?.status === "degraded"
          ? " (Indexed in ephemeral session store; persistent store offline)"
          : "";
      setUploadSuccessMsg(
        `"${uploadedDoc?.original_filename || file.name}" uploaded and indexed successfully!${degradedNote}`
      );
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Upload failed. Please ensure file contains valid text and try again.";
      setUploadErrorMsg(msg);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) processUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processUpload(file);
  };

  const handleConfirmDelete = async () => {
    if (!docToDelete) return;
    try {
      setIsDeleting(true);
      await onDelete(docToDelete.id);
      setUploadSuccessMsg(`"${docToDelete.original_filename}" deleted successfully.`);
      setDocToDelete(null);
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || "Failed to delete document.";
      setUploadErrorMsg(msg);
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    if (!searchFilter.trim()) return true;
    const term = searchFilter.toLowerCase();
    return (
      (doc.original_filename && doc.original_filename.toLowerCase().includes(term)) ||
      (doc.file_type && doc.file_type.toLowerCase().includes(term))
    );
  });

  const hasDegradedDoc = documents.some((d) => d.status === "degraded");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* ── 1. UPLOAD AREA CARD ─────────────────────────────────────────── */}
      <section
        aria-label="Course Material Ingestion"
        style={{
          background: "var(--cv-paper, #fbf9f4)",
          border: "1px solid var(--cv-border)",
          borderRadius: "6px",
          padding: "24px 28px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <span
              style={{
                fontSize: "0.72rem",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--cv-text-muted)",
                fontWeight: 700,
              }}
            >
              Document Ingestion (RAG)
            </span>
            <h2 style={{ margin: "4px 0 0 0", fontSize: "1.15rem", fontWeight: 700, color: "var(--cv-text)" }}>
              Upload Learning Materials & Syllabi
            </h2>
            <p style={{ margin: "4px 0 0 0", fontSize: "0.86rem", color: "var(--cv-text-muted)" }}>
              Upload PDF lecture slides, Markdown course notes, or plain text summaries. Dr. Cyra Vance will retrieve these to ground explanations with page and section citations.
            </p>
          </div>

          <div style={{ display: "flex", gap: "6px" }}>
            <span
              style={{
                fontSize: "0.7rem",
                padding: "3px 8px",
                borderRadius: "3px",
                background: "var(--cv-accent-soft)",
                color: "var(--cv-accent)",
                fontWeight: 600,
              }}
            >
              PDF • MD • TXT
            </span>
            <span
              style={{
                fontSize: "0.7rem",
                padding: "3px 8px",
                borderRadius: "3px",
                background: "var(--cv-accent-soft)",
                color: "var(--cv-accent)",
                fontWeight: 600,
              }}
            >
              Max 15 MB
            </span>
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              fileInputRef.current?.click();
            }
          }}
          style={{
            border: `2px dashed ${isDragging ? "var(--accent, var(--cv-accent))" : "var(--border, var(--cv-border))"}`,
            borderRadius: "6px",
            padding: "28px 20px",
            textAlign: "center",
            background: isDragging ? "var(--accent-soft, var(--cv-accent-soft))" : "var(--surface-2, rgba(0, 0, 0, 0.015))",
            cursor: isUploading ? "wait" : "pointer",
            transition: "all 0.15s ease",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.md,.markdown,.txt"
            style={{ display: "none" }}
            onChange={handleFileChange}
            disabled={isUploading}
          />

          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "50%",
                background: "var(--cv-accent-soft)",
                color: "var(--cv-accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isUploading ? <RefreshCw size={22} className="animate-spin" /> : <Upload size={22} />}
            </div>

            <div style={{ fontSize: "0.92rem", fontWeight: 600, color: "var(--cv-text)" }}>
              {isUploading ? "Uploading & Indexing Chunks..." : "Click or drag course material here to upload"}
            </div>

            <div style={{ fontSize: "0.78rem", color: "var(--cv-text-muted)" }}>
              Supports PDF, Markdown (.md), and Plain Text (.txt) up to 15 MB per file
            </div>
          </div>

          {/* Progress Bar */}
          {isUploading && (
            <div style={{ marginTop: "16px", maxWidth: "340px", margin: "16px auto 0 auto" }}>
              <div
                style={{
                  height: "6px",
                  borderRadius: "3px",
                  background: "var(--cv-border)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${uploadProgress}%`,
                    background: "var(--cv-accent)",
                    transition: "width 0.2s ease",
                  }}
                />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px", fontSize: "0.72rem", color: "var(--cv-text-muted)" }}>
                <span>Processing & embedding...</span>
                <span>{uploadProgress}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Success Alert */}
        {uploadSuccessMsg && (
          <div
            style={{
              marginTop: "14px",
              padding: "10px 14px",
              borderRadius: "4px",
              background: "var(--success-soft, rgba(22, 163, 74, 0.1))",
              border: "1px solid var(--success-border, rgba(22, 163, 74, 0.3))",
              color: "var(--success, #15803d)",
              fontSize: "0.84rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <CheckCircle2 size={16} />
              <span>{uploadSuccessMsg}</span>
            </div>
            <button
              type="button"
              onClick={() => setUploadSuccessMsg("")}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--success, #15803d)", padding: "2px" }}
            >
              <X size={14} />
            </button>
          </div>
        )}

        {/* Error Alert */}
        {uploadErrorMsg && (
          <div
            style={{
              marginTop: "14px",
              padding: "10px 14px",
              borderRadius: "4px",
              background: "var(--danger-soft, rgba(239, 68, 68, 0.1))",
              border: "1px solid var(--danger-border, rgba(239, 68, 68, 0.3))",
              color: "var(--danger, #b91c1c)",
              fontSize: "0.84rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <AlertCircle size={16} />
              <span>{uploadErrorMsg}</span>
            </div>
            <button
              type="button"
              onClick={() => setUploadErrorMsg("")}
              style={{ background: "none", border: "none", cursor: "pointer", color: "var(--danger, #b91c1c)", padding: "2px" }}
            >
              <X size={14} />
            </button>
          </div>
        )}
      </section>

      {/* ── 2. DEGRADED INDEXING BANNER (Truthful State Notice) ──────────── */}
      {hasDegradedDoc && (
        <div
          style={{
            padding: "10px 16px",
            borderRadius: "4px",
            background: "var(--warning-soft, rgba(245, 158, 11, 0.1))",
            border: "1px solid var(--warning-border, rgba(245, 158, 11, 0.3))",
            color: "var(--warning, #b45309)",
            fontSize: "0.82rem",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>
            <strong>Storage Notice:</strong> One or more documents are indexed in an ephemeral vector store session. Retrieval is active for tutoring now, but persistent Chroma storage is offline.
          </span>
        </div>
      )}

      {/* ── 3. UPLOADED DOCUMENTS LIBRARY ─────────────────────────────────── */}
      <section
        aria-label="Uploaded Course Materials Library"
        style={{
          background: "var(--cv-paper, #fbf9f4)",
          border: "1px solid var(--cv-border)",
          borderRadius: "6px",
          padding: "24px 28px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
            flexWrap: "wrap",
            gap: "10px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "var(--cv-text)" }}>
              Active Learning Materials ({documents.length})
            </h3>
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
              title="Refresh course documents"
              style={{
                background: "transparent",
                border: "1px solid var(--cv-border)",
                borderRadius: "4px",
                padding: "4px 8px",
                fontSize: "0.76rem",
                color: "var(--cv-text)",
                cursor: loading ? "wait" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Search Box */}
          {documents.length > 0 && (
            <div style={{ position: "relative", minWidth: "220px" }}>
              <Search size={14} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--cv-text-muted)" }} />
              <input
                type="text"
                placeholder="Search uploaded materials..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                style={{
                  width: "100%",
                  padding: "6px 10px 6px 30px",
                  borderRadius: "4px",
                  border: "1px solid var(--cv-border)",
                  background: "var(--surface, var(--cv-paper))",
                  color: "var(--text, var(--cv-text))",
                  fontSize: "0.8rem",
                  boxSizing: "border-box",
                }}
              />
            </div>
          )}
        </div>

        {/* Error State */}
        {error && (
          <div
            style={{
              padding: "12px 16px",
              borderRadius: "4px",
              background: "var(--danger-soft, rgba(239, 68, 68, 0.08))",
              border: "1px solid var(--danger-border, rgba(239, 68, 68, 0.25))",
              color: "var(--danger, #b91c1c)",
              fontSize: "0.85rem",
              marginBottom: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span>{error}</span>
            <button
              type="button"
              onClick={onRefresh}
              style={{
                background: "transparent",
                border: "1px solid #b91c1c",
                borderRadius: "3px",
                padding: "2px 8px",
                color: "#b91c1c",
                fontSize: "0.75rem",
                cursor: "pointer",
              }}
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: "center", padding: "30px", color: "var(--cv-text-muted)", fontSize: "0.88rem" }}>
            <RefreshCw size={20} className="animate-spin" style={{ margin: "0 auto 8px auto", display: "block" }} />
            Loading learning materials...
          </div>
        )}

        {/* Empty State */}
        {!loading && documents.length === 0 && (
          <div
            style={{
              textAlign: "center",
              padding: "36px 20px",
              border: "1px dashed var(--cv-border)",
              borderRadius: "6px",
              color: "var(--cv-text-muted)",
            }}
          >
            <BookOpen size={32} style={{ margin: "0 auto 10px auto", color: "var(--cv-accent)", opacity: 0.8 }} />
            <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--cv-text)", marginBottom: "4px" }}>
              No learning materials uploaded yet
            </div>
            <div style={{ fontSize: "0.82rem", maxWidth: "420px", margin: "0 auto 16px auto" }}>
              Upload your syllabus, lecture slides, or technical notes above. Dr. Cyra Vance will retrieve concepts directly from your documents and cite pages in her answers.
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              style={{
                padding: "6px 16px",
                borderRadius: "4px",
                background: "var(--cv-accent)",
                color: "var(--cv-text-inverse)",
                border: "none",
                fontSize: "0.82rem",
                fontWeight: 600,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Upload size={13} />
              <span>Upload First Document</span>
            </button>
          </div>
        )}

        {/* Document Cards List */}
        {!loading && filteredDocs.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {filteredDocs.map((doc) => {
              const isSelected = selectedDocumentId === doc.id;
              const dateStr = doc.created_at
                ? new Date(doc.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
                : "Recent";

              return (
                <div
                  key={doc.id}
                  style={{
                    background: isSelected ? "var(--accent-soft, var(--cv-accent-soft))" : "var(--surface, var(--cv-paper))",
                    border: `1px solid ${isSelected ? "var(--accent, var(--cv-accent))" : "var(--border, var(--cv-border))"}`,
                    borderRadius: "5px",
                    padding: "12px 16px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "12px",
                    transition: "border-color 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px", minWidth: "220px", flex: 1 }}>
                    <div
                      style={{
                        width: "36px",
                        height: "36px",
                        borderRadius: "4px",
                        background: "rgba(0,0,0,0.03)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                      }}
                    >
                      {getFormatIcon(doc.file_type, doc.original_filename)}
                    </div>

                    <div>
                      <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--cv-text)", wordBreak: "break-all" }}>
                        {doc.original_filename}
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", marginTop: "3px", fontSize: "0.72rem", color: "var(--cv-text-muted)" }}>
                        <span style={{ textTransform: "uppercase", fontWeight: 600 }}>{doc.file_type || "Document"}</span>
                        <span>•</span>
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>•</span>
                        <span>{dateStr}</span>
                        {doc.total_pages && (
                          <>
                            <span>•</span>
                            <span>{doc.total_pages} {doc.total_pages === 1 ? "page" : "pages"}</span>
                          </>
                        )}
                        <span>•</span>
                        <span>{doc.total_chunks || 0} chunks</span>
                      </div>
                    </div>
                  </div>

                  {/* Badges & Actions */}
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    {/* Status Badge */}
                    {doc.status === "indexed" && (
                      <span
                        title="Chunks indexed in persistent vector store"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          padding: "3px 8px",
                          borderRadius: "3px",
                          background: "rgba(22, 163, 74, 0.12)",
                          color: "#15803d",
                        }}
                      >
                        <CheckCircle2 size={12} />
                        Indexed
                      </span>
                    )}

                    {doc.status === "degraded" && (
                      <span
                        title="Active in ephemeral session vector store"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          padding: "3px 8px",
                          borderRadius: "3px",
                          background: "rgba(245, 158, 11, 0.15)",
                          color: "#b45309",
                        }}
                      >
                        <AlertCircle size={12} />
                        Degraded (Session)
                      </span>
                    )}

                    {(doc.status === "indexing" || doc.status === "uploaded") && (
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          padding: "3px 8px",
                          borderRadius: "3px",
                          background: "rgba(59, 130, 246, 0.12)",
                          color: "#2563eb",
                        }}
                      >
                        <RefreshCw size={12} className="animate-spin" />
                        Indexing...
                      </span>
                    )}

                    {doc.status === "failed" && (
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          fontSize: "0.72rem",
                          fontWeight: 600,
                          padding: "3px 8px",
                          borderRadius: "3px",
                          background: "rgba(239, 68, 68, 0.12)",
                          color: "#dc2626",
                        }}
                      >
                        <AlertCircle size={12} />
                        Failed
                      </span>
                    )}

                    {/* Ask Cyra Action */}
                    {onSelectDocumentForChat && (
                      <button
                        type="button"
                        onClick={() => onSelectDocumentForChat(doc)}
                        style={{
                          padding: "5px 10px",
                          borderRadius: "3px",
                          border: "1px solid var(--cv-accent)",
                          background: isSelected ? "var(--cv-accent)" : "transparent",
                          color: isSelected ? "var(--cv-text-inverse)" : "var(--cv-accent)",
                          fontSize: "0.74rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <Sparkles size={11} />
                        <span>{isSelected ? "Active in Chat" : "Ask Cyra"}</span>
                      </button>
                    )}

                    {/* Delete Action */}
                    <button
                      type="button"
                      onClick={() => setDocToDelete(doc)}
                      title={`Delete "${doc.original_filename}"`}
                      style={{
                        padding: "5px 8px",
                        borderRadius: "3px",
                        border: "1px solid var(--cv-border)",
                        background: "transparent",
                        color: "var(--cv-danger, #ef4444)",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* ── 4. DELETION CONFIRMATION MODAL ───────────────────────────────── */}
      {docToDelete && (
        <div
          role="dialog"
          aria-modal="true"
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            padding: "16px",
          }}
        >
          <div
            style={{
              background: "var(--surface, var(--cv-paper))",
              border: "1px solid var(--border, var(--cv-border))",
              borderRadius: "6px",
              padding: "24px",
              maxWidth: "460px",
              width: "100%",
              boxShadow: "0 10px 25px rgba(0,0,0,0.18)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px", color: "var(--danger, var(--cv-danger))" }}>
              <AlertCircle size={22} />
              <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, color: "var(--text, var(--cv-text))" }}>
                Delete Learning Material?
              </h3>
            </div>
            <p style={{ margin: "0 0 16px 0", fontSize: "0.88rem", color: "var(--text, var(--cv-text))", lineHeight: 1.5 }}>
              Are you sure you want to delete <strong>"{docToDelete.original_filename}"</strong>?
              This will remove the file from storage and delete all associated vector chunks from Dr. Cyra Vance's tutoring knowledge base.
            </p>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button
                type="button"
                onClick={() => setDocToDelete(null)}
                disabled={isDeleting}
                style={{
                  padding: "8px 16px",
                  borderRadius: "4px",
                  border: "1px solid var(--border, var(--cv-border))",
                  background: "transparent",
                  color: "var(--text, var(--cv-text))",
                  fontSize: "0.85rem",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                style={{
                  padding: "8px 16px",
                  borderRadius: "4px",
                  border: "none",
                  background: "var(--danger, var(--cv-danger, #ef4444))",
                  color: "var(--accent-contrast, #ffffff)",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                {isDeleting ? <RefreshCw size={14} className="animate-spin" /> : <Trash2 size={14} />}
                <span>{isDeleting ? "Deleting..." : "Confirm Delete"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

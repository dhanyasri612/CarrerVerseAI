import React, { useState, useEffect, useRef } from "react";
import {
  ShieldCheck,
  Camera,
  Mic,
  Monitor,
  AlertTriangle,
  CheckCircle,
  Eye,
  Info,
  X,
  Volume2,
} from "lucide-react";

export default function ProctoringReadinessModal({
  isOpen,
  onClose,
  onProceed,
  role = "Software Engineer",
  interviewMode = "github",
}) {
  const [cameraGranted, setCameraGranted] = useState(false);
  const [micGranted, setMicGranted] = useState(false);
  const [browserMonitoringConsent, setBrowserMonitoringConsent] = useState(true);
  const [screenShareConsent, setScreenShareConsent] = useState(false);
  const [audioTesting, setAudioTesting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const videoRef = useRef(null);
  const mediaStreamRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
        mediaStreamRef.current = null;
      }
      return;
    }

    // Attempt camera/mic permission check
    async function checkPeripherals() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        mediaStreamRef.current = stream;
        setCameraGranted(true);
        setMicGranted(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.warn("[Readiness] Camera/Mic access denied or unavailable:", err);
        setCameraGranted(false);
        setMicGranted(false);
        setErrorMsg(
          "Camera or microphone access was not detected. You may still proceed in Unproctored Practice Mode or grant permissions in your browser."
        );
      }
    }

    checkPeripherals();

    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
        mediaStreamRef.current = null;
      }
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleTestAudio = () => {
    setAudioTesting(true);
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(440, audioCtx.currentTime); // 440 Hz standard A tone
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      setTimeout(() => {
        osc.stop();
        audioCtx.close();
        setAudioTesting(false);
      }, 600);
    } catch (_e) {
      setAudioTesting(false);
    }
  };

  const handleStartProctored = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    onProceed({
      unproctored: false,
      cameraConsent: cameraGranted,
      micConsent: micGranted,
      browserMonitoringConsent,
      screenShareConsent,
    });
  };

  const handleStartUnproctored = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    onProceed({
      unproctored: true,
      cameraConsent: false,
      micConsent: false,
      browserMonitoringConsent: false,
      screenShareConsent: false,
    });
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
        padding: "16px",
      }}
    >
      <div
        style={{
          background: "var(--cv-surface, #ffffff)",
          color: "var(--cv-text, #0f172a)",
          borderRadius: "16px",
          border: "1px solid var(--cv-border, #e2e8f0)",
          boxShadow: "0 20px 40px rgba(0,0,0,0.25)",
          maxWidth: "680px",
          width: "100%",
          maxHeight: "90vh",
          overflowY: "auto",
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: "10px",
                background: "rgba(99, 102, 241, 0.12)",
                color: "#6366f1",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <ShieldCheck size={22} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 800 }}>
                Pre-Interview Integrity & Readiness
              </h3>
              <p style={{ margin: "2px 0 0 0", fontSize: "0.8rem", color: "var(--cv-text-muted, #64748b)" }}>
                Amazon-inspired technical simulation • {role} ({interviewMode.toUpperCase()})
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              color: "var(--cv-text-muted, #64748b)",
              padding: "4px",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Transparency Disclosure Alert */}
        <div
          style={{
            background: "var(--cv-bg-subtle, #f8fafc)",
            border: "1px solid var(--cv-border, #e2e8f0)",
            borderRadius: "10px",
            padding: "12px 14px",
            fontSize: "0.78rem",
            lineHeight: 1.5,
            color: "var(--cv-text, #334155)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, marginBottom: "4px", color: "#4f46e5" }}>
            <Info size={14} />
            <span>Transparent Integrity Policy</span>
          </div>
          We monitor basic browser window events (visibility loss, full-screen exits) and camera connection status.
          <strong> Browser events are inherently ambiguous</strong> and are strictly decoupled from your technical rubric scoring.
          No background keylogging, facial emotion inference, or invasive biometrics are ever performed.
        </div>

        {/* Camera Preview & Peripherals Check */}
        <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "16px" }}>
          <div
            style={{
              height: "135px",
              background: "#000000",
              borderRadius: "10px",
              overflow: "hidden",
              position: "relative",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {cameraGranted ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)" }}
              />
            ) : (
              <div style={{ textAlign: "center", color: "#94a3b8", fontSize: "0.75rem", padding: "8px" }}>
                <Camera size={24} style={{ margin: "0 auto 4px auto", display: "block" }} />
                <span>Camera feed inactive</span>
              </div>
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.82rem" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Camera size={14} /> Camera Feed
              </span>
              <span style={{ fontWeight: 700, color: cameraGranted ? "#16a34a" : "#dc2626" }}>
                {cameraGranted ? "✓ Ready" : "✗ Not Detected"}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.82rem" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Mic size={14} /> Microphone & Speech
              </span>
              <span style={{ fontWeight: 700, color: micGranted ? "#16a34a" : "#dc2626" }}>
                {micGranted ? "✓ Ready" : "✗ Not Detected"}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.82rem" }}>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Volume2 size={14} /> Audio Output Check
              </span>
              <button
                type="button"
                onClick={handleTestAudio}
                disabled={audioTesting}
                style={{
                  background: "var(--cv-bg-subtle, #f1f5f9)",
                  border: "1px solid var(--cv-border, #cbd5e1)",
                  borderRadius: "6px",
                  padding: "3px 10px",
                  fontSize: "0.74rem",
                  cursor: "pointer",
                }}
              >
                {audioTesting ? "Playing..." : "Test Chime"}
              </button>
            </div>
          </div>
        </div>

        {errorMsg && (
          <div
            style={{
              background: "#fef2f2",
              border: "1px solid #fecaca",
              color: "#991b1b",
              padding: "10px 12px",
              borderRadius: "8px",
              fontSize: "0.78rem",
            }}
          >
            {errorMsg}
          </div>
        )}

        {/* Feature Consents */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.82rem" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={browserMonitoringConsent}
              onChange={(e) => setBrowserMonitoringConsent(e.target.checked)}
            />
            <span>I consent to transparent browser tab and focus event logging during the interview.</span>
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={screenShareConsent}
              onChange={(e) => setScreenShareConsent(e.target.checked)}
            />
            <span>Enable optional screen-sharing verification for coding and architectural diagrams.</span>
          </label>
        </div>

        {/* Action Buttons */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "10px",
            marginTop: "8px",
            borderTop: "1px solid var(--cv-border, #e2e8f0)",
            paddingTop: "16px",
          }}
        >
          <button
            type="button"
            onClick={handleStartUnproctored}
            style={{
              background: "transparent",
              border: "1px solid var(--cv-border, #cbd5e1)",
              borderRadius: "8px",
              padding: "9px 16px",
              fontSize: "0.82rem",
              fontWeight: 600,
              color: "var(--cv-text-muted, #64748b)",
              cursor: "pointer",
            }}
          >
            Start Unproctored Practice Mode
          </button>

          <button
            type="button"
            onClick={handleStartProctored}
            style={{
              background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              border: "none",
              borderRadius: "8px",
              padding: "9px 22px",
              fontSize: "0.85rem",
              fontWeight: 700,
              color: "#ffffff",
              cursor: "pointer",
              boxShadow: "0 4px 12px rgba(79, 70, 229, 0.3)",
            }}
          >
            I Consent & Enter Live Studio
          </button>
        </div>
      </div>
    </div>
  );
}

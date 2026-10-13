import React from "react";

export default function TalkingRobotMascot({
  isSpeaking = false,
  agentName = "Cyra-Bot",
  activeColor = "#38bdf8",
  secondaryColor = "#f97316",
}) {
  const glowColor = activeColor || "#38bdf8";
  const chassisColor = secondaryColor || "#f97316";

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: "360px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        background: "radial-gradient(circle at 50% 45%, #1e1b4b 0%, #0f172a 65%, #020617 100%)",
      }}
    >
      {/* ── Ambient Floating Particles & Soundwave Radii ── */}
      <div
        style={{
          position: "absolute",
          width: "380px",
          height: "380px",
          borderRadius: "50%",
          background: isSpeaking
            ? `radial-gradient(circle, ${glowColor}40 0%, ${glowColor}15 50%, transparent 70%)`
            : `radial-gradient(circle, ${glowColor}18 0%, transparent 60%)`,
          animation: isSpeaking ? "pulseRipples 1.2s infinite ease-out" : "idleFloat 4s infinite ease-in-out",
          pointerEvents: "none",
        }}
      />

      {/* Cybernetic Orbital Ring */}
      <div
        style={{
          position: "absolute",
          width: "320px",
          height: "140px",
          borderRadius: "50%",
          border: `1.5px dashed ${glowColor}50`,
          transform: "rotate(-18deg)",
          animation: "spinSlow 18s linear infinite",
          pointerEvents: "none",
        }}
      />

      {/* ── ROBOT CHARACTER CONTAINER ── */}
      <div
        style={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          animation: isSpeaking ? "robotTalkingBounce 0.45s infinite ease-in-out alternate" : "robotFloat 3s infinite ease-in-out",
        }}
      >
        {/* Antennas with Glowing Beacons */}
        <div style={{ display: "flex", gap: "54px", marginBottom: "-8px", zIndex: 1 }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: isSpeaking ? "#38bdf8" : "#818cf8",
                boxShadow: isSpeaking ? "0 0 14px #38bdf8, 0 0 24px #38bdf8" : "0 0 6px #818cf8",
                transition: "all 0.2s",
              }}
            />
            <div style={{ width: 3, height: 16, background: "linear-gradient(to bottom, #94a3b8, #475569)" }} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: isSpeaking ? "#38bdf8" : "#818cf8",
                boxShadow: isSpeaking ? "0 0 14px #38bdf8, 0 0 24px #38bdf8" : "0 0 6px #818cf8",
                transition: "all 0.2s",
              }}
            />
            <div style={{ width: 3, height: 16, background: "linear-gradient(to bottom, #94a3b8, #475569)" }} />
          </div>
        </div>

        {/* ── HEAD MODULE ── */}
        <div
          style={{
            position: "relative",
            width: 154,
            height: 122,
            borderRadius: "36px",
            background: "linear-gradient(145deg, #f8fafc 0%, #cbd5e1 60%, #94a3b8 100%)",
            border: "3px solid #e2e8f0",
            boxShadow: isSpeaking
              ? "0 0 25px rgba(99, 102, 241, 0.4), inset 0 2px 6px rgba(255,255,255,0.8), 0 12px 24px rgba(0,0,0,0.3)"
              : "inset 0 2px 6px rgba(255,255,255,0.8), 0 12px 24px rgba(0,0,0,0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Side Headphone Ear Cups */}
          <div
            style={{
              position: "absolute",
              left: -14,
              width: 16,
              height: 48,
              borderRadius: "8px",
              background: "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
              boxShadow: "0 2px 8px rgba(249, 115, 22, 0.4)",
            }}
          />
          <div
            style={{
              position: "absolute",
              right: -14,
              width: 16,
              height: 48,
              borderRadius: "8px",
              background: "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
              boxShadow: "0 2px 8px rgba(249, 115, 22, 0.4)",
            }}
          />

          {/* ── VISOR SCREEN (CYBERNETIC DISPLAY) ── */}
          <div
            style={{
              width: 126,
              height: 84,
              borderRadius: "24px",
              background: "#020617",
              border: "2px solid #1e293b",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              overflow: "hidden",
              boxShadow: "inset 0 0 14px rgba(56, 189, 248, 0.2)",
            }}
          >
            {/* Ambient Scanline */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(56, 189, 248, 0.05) 4px)",
                pointerEvents: "none",
              }}
            />

            {/* Glowing Digital Eyes */}
            <div style={{ display: "flex", gap: "24px", alignItems: "center", marginBottom: isSpeaking ? "4px" : "0" }}>
              {/* Left Eye */}
              <div
                style={{
                  width: isSpeaking ? 22 : 20,
                  height: isSpeaking ? 24 : 16,
                  borderRadius: isSpeaking ? "50%" : "12px",
                  background: "#38bdf8",
                  boxShadow: "0 0 12px #38bdf8, 0 0 20px #0284c7",
                  transition: "all 0.15s ease",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#ffffff" }} />
              </div>

              {/* Right Eye */}
              <div
                style={{
                  width: isSpeaking ? 22 : 20,
                  height: isSpeaking ? 24 : 16,
                  borderRadius: isSpeaking ? "50%" : "12px",
                  background: "#38bdf8",
                  boxShadow: "0 0 12px #38bdf8, 0 0 20px #0284c7",
                  transition: "all 0.15s ease",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#ffffff" }} />
              </div>
            </div>

            {/* Animated Talking Mouth / Soundwave */}
            {isSpeaking ? (
              <div style={{ display: "flex", gap: "3px", alignItems: "center", height: 18, marginTop: 4 }}>
                <span style={{ width: 3, height: 8, background: "#38bdf8", borderRadius: 2, animation: "voiceBar 0.3s infinite alternate 0.1s" }} />
                <span style={{ width: 3, height: 14, background: "#38bdf8", borderRadius: 2, animation: "voiceBar 0.3s infinite alternate 0.25s" }} />
                <span style={{ width: 3, height: 18, background: "#38bdf8", borderRadius: 2, animation: "voiceBar 0.3s infinite alternate 0.05s" }} />
                <span style={{ width: 3, height: 12, background: "#38bdf8", borderRadius: 2, animation: "voiceBar 0.3s infinite alternate 0.2s" }} />
                <span style={{ width: 3, height: 6, background: "#38bdf8", borderRadius: 2, animation: "voiceBar 0.3s infinite alternate 0.15s" }} />
              </div>
            ) : (
              <div
                style={{
                  width: 24,
                  height: 4,
                  borderRadius: "2px",
                  background: "#0284c7",
                  marginTop: 6,
                  boxShadow: "0 0 6px #0284c7",
                }}
              />
            )}
          </div>
        </div>

        {/* Neck Module */}
        <div style={{ width: 32, height: 10, background: "#475569", borderRadius: "3px", marginTop: "-2px" }} />

        {/* ── CHEST & CHASSIS ── */}
        <div
          style={{
            position: "relative",
            width: 114,
            height: 94,
            borderRadius: "26px",
            background: "linear-gradient(145deg, #f97316 0%, #ea580c 55%, #c2410c 100%)",
            border: "2px solid #fb923c",
            boxShadow: "0 8px 20px rgba(194, 65, 12, 0.35)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {/* Arc Reactor Core Emblem */}
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "#020617",
              border: "2px solid #38bdf8",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: isSpeaking
                ? "0 0 16px #38bdf8, 0 0 28px rgba(56, 189, 248, 0.6)"
                : "0 0 8px #38bdf8",
              transition: "box-shadow 0.2s",
            }}
          >
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                background: "#38bdf8",
                animation: isSpeaking ? "coreSpin 1s linear infinite" : "none",
              }}
            />
          </div>

          {/* Gesturing Floating Robotic Arms */}
          <div
            style={{
              position: "absolute",
              left: -32,
              top: 14,
              width: 32,
              height: 52,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: isSpeaking ? "rotate(16deg) translateY(-4px)" : "rotate(8deg)",
              transition: "transform 0.25s ease",
            }}
          >
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#e2e8f0", border: "2px solid #94a3b8" }} />
            <div style={{ width: 8, height: 26, background: "#cbd5e1", borderRadius: 4 }} />
            <div style={{ width: 16, height: 12, borderRadius: "6px", background: "#f97316", border: "1.5px solid #fb923c" }} />
          </div>

          <div
            style={{
              position: "absolute",
              right: -32,
              top: 14,
              width: 32,
              height: 52,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: isSpeaking ? "rotate(-24deg) translateY(-8px)" : "rotate(-10deg)",
              transition: "transform 0.25s ease",
            }}
          >
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#e2e8f0", border: "2px solid #94a3b8" }} />
            <div style={{ width: 8, height: 26, background: "#cbd5e1", borderRadius: 4 }} />
            <div style={{ width: 16, height: 12, borderRadius: "6px", background: "#f97316", border: "1.5px solid #fb923c" }} />
          </div>
        </div>

        {/* ── THRUSTER EXHAUST GLOW ── */}
        <div style={{ display: "flex", gap: "18px", marginTop: "4px" }}>
          <div
            style={{
              width: 14,
              height: isSpeaking ? 28 : 18,
              borderRadius: "0 0 10px 10px",
              background: "linear-gradient(to bottom, #38bdf8 0%, rgba(56, 189, 248, 0) 100%)",
              filter: "blur(2px)",
              animation: "thrusterFlame 0.2s infinite alternate",
            }}
          />
          <div
            style={{
              width: 14,
              height: isSpeaking ? 28 : 18,
              borderRadius: "0 0 10px 10px",
              background: "linear-gradient(to bottom, #38bdf8 0%, rgba(56, 189, 248, 0) 100%)",
              filter: "blur(2px)",
              animation: "thrusterFlame 0.2s infinite alternate 0.1s",
            }}
          />
        </div>
      </div>

      {/* Floating Sound Waves Left & Right */}
      {isSpeaking && (
        <div
          style={{
            position: "absolute",
            bottom: "28px",
            display: "flex",
            alignItems: "center",
            gap: "5px",
            background: "rgba(15, 23, 42, 0.75)",
            backdropFilter: "blur(8px)",
            padding: "6px 14px",
            borderRadius: "20px",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            color: "#38bdf8",
            fontSize: "0.76rem",
            fontWeight: 700,
          }}
        >
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#38bdf8", animation: "ping 1s infinite" }} />
          <span>{agentName} is mentoring & speaking...</span>
        </div>
      )}

      {/* CSS Keyframes */}
      <style>{`
        @keyframes robotFloat {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes robotTalkingBounce {
          0% { transform: translateY(-4px) scale(1); }
          100% { transform: translateY(-12px) scale(1.02); }
        }
        @keyframes voiceBar {
          0% { height: 4px; }
          100% { height: 18px; }
        }
        @keyframes thrusterFlame {
          0% { opacity: 0.7; transform: scaleY(0.85); }
          100% { opacity: 1; transform: scaleY(1.2); }
        }
        @keyframes coreSpin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes spinSlow {
          0% { transform: rotate(-18deg) rotate(0deg); }
          100% { transform: rotate(-18deg) rotate(360deg); }
        }
        @keyframes pulseRipples {
          0% { transform: scale(0.9); opacity: 0.5; }
          100% { transform: scale(1.25); opacity: 0.1; }
        }
      `}</style>
    </div>
  );
}

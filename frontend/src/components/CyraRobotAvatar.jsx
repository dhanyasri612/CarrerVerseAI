import React from "react";

export default function CyraRobotAvatar({
  isSpeaking = false,
  isListening = true,
  size = 220,
}) {
  return (
    <div
      style={{
        width: "100%",
        height: size,
        borderRadius: "16px",
        background: "radial-gradient(circle at 50% 40%, #1e1b4b 0%, #0f172a 75%, #020617 100%)",
        border: "1px solid rgba(99, 102, 241, 0.3)",
        boxShadow: "inset 0 0 30px rgba(99, 102, 241, 0.15), 0 4px 20px rgba(0, 0, 0, 0.25)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background Matrix Grid Overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(99, 102, 241, 0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(99, 102, 241, 0.07) 1px, transparent 1px)",
          backgroundSize: "20px 20px",
          pointerEvents: "none",
        }}
      />

      {/* Cybernetic Glow Aura Behind Robot */}
      <div
        style={{
          position: "absolute",
          width: 140,
          height: 140,
          borderRadius: "50%",
          background: isSpeaking
            ? "radial-gradient(circle, rgba(99, 102, 241, 0.45) 0%, transparent 70%)"
            : "radial-gradient(circle, rgba(56, 189, 248, 0.35) 0%, transparent 70%)",
          filter: "blur(20px)",
          transition: "all 0.3s ease",
          animation: isSpeaking ? "cyraPulse 1.2s infinite alternate" : "none",
        }}
      />

      {/* Futuristic Robot Head SVG */}
      <svg
        width="130"
        height="130"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: "relative", zIndex: 2 }}
      >
        <defs>
          <linearGradient id="robotMetal" x1="0" y1="0" x2="120" y2="120" gradientUnits="userSpaceOnUse">
            <stop stopColor="#334155" />
            <stop offset="0.5" stopColor="#1e293b" />
            <stop offset="1" stopColor="#0f172a" />
          </linearGradient>
          <linearGradient id="robotChassis" x1="20" y1="20" x2="100" y2="100" gradientUnits="userSpaceOnUse">
            <stop stopColor="#475569" />
            <stop offset="1" stopColor="#1e293b" />
          </linearGradient>
          <linearGradient id="visorGlow" x1="30" y1="45" x2="90" y2="65" gradientUnits="userSpaceOnUse">
            <stop stopColor="#38bdf8" />
            <stop offset="0.5" stopColor="#818cf8" />
            <stop offset="1" stopColor="#6366f1" />
          </linearGradient>
          <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Cyber Antenna */}
        <line x1="60" y1="12" x2="60" y2="24" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" />
        <circle
          cx="60"
          cy="10"
          r="4"
          fill={isSpeaking ? "#a855f7" : "#38bdf8"}
          filter="url(#neonGlow)"
        />

        {/* Head Base / Outer Chassis */}
        <rect
          x="22"
          y="24"
          width="76"
          height="64"
          rx="22"
          fill="url(#robotMetal)"
          stroke="#4f46e5"
          strokeWidth="2"
        />

        {/* Ear Headphone modules */}
        <rect x="14" y="42" width="8" height="28" rx="4" fill="#3b82f6" />
        <rect x="98" y="42" width="8" height="28" rx="4" fill="#3b82f6" />
        <circle cx="18" cy="56" r="2.5" fill="#38bdf8" filter="url(#neonGlow)" />
        <circle cx="102" cy="56" r="2.5" fill="#38bdf8" filter="url(#neonGlow)" />

        {/* Digital Glass Visor */}
        <rect
          x="30"
          y="38"
          width="60"
          height="32"
          rx="12"
          fill="#030712"
          stroke="#38bdf8"
          strokeWidth="1.5"
        />

        {/* Animated Cyber Eyes inside Visor */}
        <g filter="url(#neonGlow)">
          {/* Left Eye */}
          <ellipse
            cx="46"
            cy="54"
            rx={isSpeaking ? 5.5 : 6}
            ry={isSpeaking ? 7 : 6}
            fill="#38bdf8"
          />
          <circle cx="48" cy="52" r="2" fill="#ffffff" />

          {/* Right Eye */}
          <ellipse
            cx="74"
            cy="54"
            rx={isSpeaking ? 5.5 : 6}
            ry={isSpeaking ? 7 : 6}
            fill="#38bdf8"
          />
          <circle cx="76" cy="52" r="2" fill="#ffffff" />
        </g>

        {/* Cyber Mouth / Speech Waveform Indicator */}
        {isSpeaking ? (
          <g filter="url(#neonGlow)">
            <line x1="42" y1="78" x2="42" y2="84" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />
            <line x1="48" y1="76" x2="48" y2="86" stroke="#c084fc" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="54" y1="74" x2="54" y2="88" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="60" y1="72" x2="60" y2="90" stroke="#38bdf8" strokeWidth="3" strokeLinecap="round" />
            <line x1="66" y1="74" x2="66" y2="88" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="72" y1="76" x2="72" y2="86" stroke="#c084fc" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="78" y1="78" x2="78" y2="84" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" />
          </g>
        ) : (
          <rect
            x="48"
            y="80"
            width="24"
            height="3.5"
            rx="1.75"
            fill="#38bdf8"
            opacity="0.85"
            filter="url(#neonGlow)"
          />
        )}

        {/* Neck connector */}
        <path d="M46 88 H74 V98 H46 Z" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
        {/* Chest Plate Collar */}
        <path
          d="M32 98 Q60 106 88 98 L94 116 Q60 122 26 116 Z"
          fill="url(#robotChassis)"
          stroke="#4f46e5"
          strokeWidth="1.5"
        />
        <circle cx="60" cy="108" r="4" fill="#6366f1" filter="url(#neonGlow)" />
      </svg>

      {/* Dynamic Soundwave Visualizer / Listening Status Badge */}
      <div
        style={{
          position: "absolute",
          bottom: 10,
          right: 12,
          background: "rgba(15, 23, 42, 0.8)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          borderRadius: "20px",
          padding: "4px 10px",
          display: "flex",
          alignItems: "center",
          gap: "6px",
          color: isSpeaking ? "#c084fc" : "#38bdf8",
          fontSize: "0.7rem",
          fontWeight: 700,
          zIndex: 3,
        }}
      >
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: isSpeaking ? "#c084fc" : "#22c55e",
            boxShadow: isSpeaking ? "0 0 8px #c084fc" : "0 0 8px #22c55e",
          }}
        />
        <span>{isSpeaking ? "Speaking..." : isListening ? "Listening..." : "Ready"}</span>
      </div>

      <style>{`
        @keyframes cyraPulse {
          0% { transform: scale(0.95); opacity: 0.6; }
          100% { transform: scale(1.15); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

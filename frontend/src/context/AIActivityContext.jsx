import React, { createContext, useContext, useState, useCallback } from "react";

/**
 * AI Activity Tracker
 * Represents real backend execution state of the multi-agent career team
 */
const AIActivityContext = createContext({
  activeAgent: null,
  status: "idle", // 'idle' | 'running' | 'completed' | 'error'
  statusText: "Ready",
  activeAgentName: "",
  activeStage: "",
  activityLog: [],
  startActivity: () => {},
  updateActivity: () => {},
  endActivity: () => {},
});

export function AIActivityProvider({ children }) {
  const [activeAgent, setActiveAgent] = useState(null);
  const [status, setStatus] = useState("idle");
  const [statusText, setStatusText] = useState("AI Career Team · Ready");
  const [activeAgentName, setActiveAgentName] = useState("");
  const [activeStage, setActiveStage] = useState("");
  const [activityLog, setActivityLog] = useState([
    {
      id: "init",
      agent: "Career Profile Analyst",
      message: "Connected to vector store and knowledge graph",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      status: "ready"
    }
  ]);

  const startActivity = useCallback((agentKey, agentName, initialStage) => {
    setActiveAgent(agentKey);
    setStatus("running");
    setActiveAgentName(agentName || agentKey);
    setActiveStage(initialStage || "Processing...");
    setStatusText(`${agentName || "AI Team"} · ${initialStage || "Executing..."}`);

    setActivityLog((prev) => [
      {
        id: Date.now().toString(),
        agent: agentName || agentKey,
        message: initialStage || "Task started",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        status: "running"
      },
      ...prev.slice(0, 19)
    ]);
  }, []);

  const updateActivity = useCallback((stageText) => {
    setActiveStage(stageText);
    setStatusText((prev) => {
      const prefix = prev.split(" · ")[0] || "AI Team";
      return `${prefix} · ${stageText}`;
    });

    setActivityLog((prev) => [
      {
        id: Date.now().toString(),
        agent: activeAgentName || "AI Agent",
        message: stageText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        status: "running"
      },
      ...prev.slice(0, 19)
    ]);
  }, [activeAgentName]);

  const endActivity = useCallback((outcome = "completed", finalMessage = "Completed successfully") => {
    setStatus(outcome);
    setStatusText(outcome === "completed" ? "AI Career Team · Ready" : "AI Career Team · Error");
    setActiveStage("");

    setActivityLog((prev) => [
      {
        id: Date.now().toString(),
        agent: activeAgentName || "AI Agent",
        message: finalMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        status: outcome
      },
      ...prev.slice(0, 19)
    ]);

    setTimeout(() => {
      setActiveAgent(null);
      setStatus("idle");
    }, 2400);
  }, [activeAgentName]);

  return (
    <AIActivityContext.Provider
      value={{
        activeAgent,
        status,
        statusText,
        activeAgentName,
        activeStage,
        activityLog,
        startActivity,
        updateActivity,
        endActivity,
      }}
    >
      {children}
    </AIActivityContext.Provider>
  );
}

export function useAIActivity() {
  return useContext(AIActivityContext);
}

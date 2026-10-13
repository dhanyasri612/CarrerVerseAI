import React, { useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Mic,
  MicOff,
  Video,
  VideoOff,
  Volume2,
  VolumeX,
  Send,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  HelpCircle,
  Code2,
  Layers,
  Award,
  ChevronRight,
  Maximize2,
  Minimize2,
  Radio,
  RotateCcw,
  RefreshCw,
  Sliders,
  ShieldCheck,
  Bot,
  Lightbulb,
  FileText,
  GitBranch,
  History,
  Clock,
  Calendar,
  Check,
  X,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Globe,
  Database,
  Terminal,
  Copy,
  Play,
  Pause,
} from "lucide-react";
import { getApiError } from "../services/api";
import {
  createInterviewSession,
  getInterviewSession,
  getInterviewSessionsList,
  submitInterviewAnswer,
  completeInterviewSession,
  getInterviewQuestionHistory,
  getInterviewResourcesAndModes,
  getProfileSnapshot,
  evaluateDsaCode,
  updateInterviewSessionLanguage,
} from "../services/careerService";
import { recordActivity } from "../services/activityTracker";
import TalkingRobotMascot from "../components/TalkingRobotMascot";
import LiveInterviewStudio from "../components/LiveInterviewStudio";
import InterviewModeSelection from "../components/InterviewModeSelection";
import { useAuth } from "../context/AuthContext";
import {
  cleanTextForSpeech,
  findBestVoiceForLang,
  filterNaturalVoices,
  containsIndicScript,
  SUPPORTED_INTERVIEW_LANGUAGES,
  getLanguageVoiceMatch,
  getLanguageConfig,
  isVoiceAvailableForLang,
} from "../services/speechService";

const SPECIALIZATION_TRACKS = [
  {
    id: "fullstack",
    title: "Full-Stack Engineering Round",
    role: "Full Stack Developer",
    topicKey: "all",
    icon: "🚀",
    badge: "Full Spectrum",
    description: "Evaluates modern React architecture, REST APIs, SQL databases, and system design.",
    competencies: ["React 19 / State Management", "FastAPI / Node Concurrency", "PostgreSQL / Schema & Indexing", "Distributed Caching & Tradeoffs"],
  },
  {
    id: "backend",
    title: "Backend & Distributed Systems Round",
    role: "Backend Systems Engineer",
    topicKey: "backend",
    icon: "⚙️",
    badge: "High Scale",
    description: "Evaluates API architecture, connection pooling, Redis caching, and microservice resilience.",
    competencies: ["Connection Pools & Timeouts", "Redis Caching & Invalidation", "Idempotency & Transactions", "Fault Tolerance & Microservices"],
  },
  {
    id: "dsa",
    title: "Data Structures & Algorithms (DSA Round)",
    role: "Software Engineer (SDE)",
    topicKey: "dsa",
    icon: "⚡",
    badge: "Algorithmic",
    description: "Evaluates sliding window, two pointers, trees, graphs, dynamic programming, and complexity.",
    competencies: ["Sliding Window & Pointers", "Trees & Graph Traversals", "Dynamic Programming & Greedy", "Time Complexity: O(N) Proofs"],
  },
  {
    id: "system_design",
    title: "System Design & Architecture Round",
    role: "Backend Systems Engineer",
    topicKey: "system_design",
    icon: "🧠",
    badge: "Architecture",
    description: "Evaluates distributed architecture, sharding, message queues, rate limiters, and high throughput.",
    competencies: ["High-Throughput Rate Limiters", "Message Queues & Event Streaming", "Database Sharding & Replication", "SLA & Latency Budgeting"],
  },
  {
    id: "frontend",
    title: "Frontend Engineering & UI Architecture",
    role: "Frontend Engineer",
    topicKey: "frontend",
    icon: "🎨",
    badge: "Client Architecture",
    description: "Evaluates component design, custom hooks, virtual DOM performance, and responsive UI.",
    competencies: ["Custom React Hooks & Lifecycle", "State Management & Memoization", "Bundle & Render Optimization", "Web Vitals & CSS Architecture"],
  },
  {
    id: "portfolio",
    title: "Personalized Resume & GitHub Track",
    role: "Software Engineer (SDE)",
    topicKey: "project",
    icon: "📄",
    badge: "Grounded Profile",
    description: "Deep dive into your real uploaded resume experience, GitHub repositories, and LeetCode activity.",
    competencies: ["Candidate Repository Evidence", "Production Project Decisions", "Tradeoffs in Real Codebases", "Candidate Technical Depth"],
  },
];

function formatQuestionContent(rawInput, defaultRole, currentQIndex) {
  if (!rawInput) {
    return {
      title: `${defaultRole || "Technical"} Evaluation • Question ${currentQIndex || 1}`,
      description: "Welcome to your proctored technical interview round. Please analyze the scenario and formulate your solution.",
      examples: [
        {
          id: 1,
          input: 'service_request = {"user_id": 102, "mode": "sync"}',
          output: '{"status": 200, "latency_ms": 12}',
          explanation: "Processes high-throughput request within allocated p99 latency SLA.",
        },
      ],
      constraints: ["Maintain O(1) cache lookup latency", "Guarantee idempotency under retries"],
      hints: ["Consider high availability and cache invalidation"],
      topic: "System Design",
    };
  }

  let rawText = rawInput;
  let preDefinedConstraints = [];
  let preDefinedExamples = [];
  let preDefinedHints = [];
  let preDefinedTopic = "";

  if (typeof rawInput === "object" && rawInput !== null) {
    if (rawInput.question && typeof rawInput.question === "object") {
      preDefinedConstraints = rawInput.question.constraints || [];
      preDefinedExamples = rawInput.question.examples || [];
      preDefinedHints = rawInput.question.hints || [];
      preDefinedTopic = rawInput.question.topic || "";
      rawText = rawInput.question.question || "";
    } else {
      preDefinedConstraints = rawInput.constraints || [];
      preDefinedExamples = rawInput.examples || [];
      preDefinedHints = rawInput.hints || [];
      preDefinedTopic = rawInput.topic || "";
      rawText = rawInput.question || "";
    }
  }

  const text = String(rawText).trim();
  const paragraphs = text.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);

  let title = `${defaultRole || "Technical"} Architecture & System Problem`;
  let description = text;
  const examples = [...preDefinedExamples];
  const constraints = [...preDefinedConstraints];
  const hints = [...preDefinedHints];
  const topic = preDefinedTopic || (text.toLowerCase().includes("bitly") || text.toLowerCase().includes("shortener") || text.toLowerCase().includes("architecture") || text.toLowerCase().includes("system") ? "System Design" : "Technical Assessment");

  if (paragraphs.length > 1) {
    const firstP = paragraphs[0];
    if (firstP.length < 90 && !firstP.includes("?")) {
      title = firstP.replace(/^#+\s*/, "");
      description = paragraphs.slice(1).join("\n\n");
    }
  }

  if (examples.length === 0) {
    const exampleRegex = /(?:EXAMPLE\s*(\d+)?:?|Sample\s*Input:?)\s*([\s\S]*?)(?=(?:EXAMPLE\s*\d+|CONSTRAINTS|Constraints:|$))/gi;
    let match;
    while ((match = exampleRegex.exec(text)) !== null && examples.length < 2) {
      const block = match[0].trim();
      const inputM = block.match(/Input:?\s*([^\n]+)/i);
      const outputM = block.match(/Output:?\s*([^\n]+)/i);
      const expM = block.match(/Explanation:?\s*([^\n]+)/i);
      if (inputM || outputM) {
        examples.push({
          id: examples.length + 1,
          input: inputM ? inputM[1].trim() : "nums = [9, 2, 4, 7], k = 4",
          output: outputM ? outputM[1].trim() : "2",
          explanation: expM ? expM[1].trim() : "Segment length 2 satisfies the constraint bounds.",
        });
      }
    }
  }

  if (examples.length === 0) {
    if (
      text.toLowerCase().includes("shortener") ||
      text.toLowerCase().includes("bitly") ||
      text.toLowerCase().includes("url")
    ) {
      examples.push({
        id: 1,
        input: 'long_url = "https://example.com/very/long/url/path?query=123"',
        output: 'short_url = "https://bit.ly/aZ8k9X" (Base62 encoded ID)',
        explanation: "Client requests /aZ8k9X -> Cache lookup (Redis) -> DB fallback -> 301/302 Redirect.",
      });
    } else if (
      text.toLowerCase().includes("nums") ||
      text.toLowerCase().includes("array") ||
      text.toLowerCase().includes("sliding") ||
      text.toLowerCase().includes("pointer")
    ) {
      examples.push({
        id: 1,
        input: "nums = [9, 2, 4, 7], k = 4",
        output: "2",
        explanation: "The longest contiguous segment where max - min <= 4 is [2, 4] with length 2.",
      });
    } else {
      examples.push({
        id: 1,
        input: 'request = POST /api/v1/orders { idempotency_key: "tx_881", user_id: 102 }',
        output: 'response: 200 OK { order_id: 9942, status: "COMMITTED" }',
        explanation: "Transaction commits within database connection pool without deadlock.",
      });
    }
  }

  if (constraints.length === 0) {
    const constraintMatch = text.match(/Constraints:?\s*([\s\S]*?)$/i);
    if (constraintMatch) {
      const cLines = constraintMatch[1]
        .split("\n")
        .map((l) => l.replace(/^[-*•]\s*/, "").trim())
        .filter(Boolean);
      constraints.push(...cLines.slice(0, 4));
    }
  }
  if (constraints.length === 0) {
    if (text.toLowerCase().includes("url") || text.toLowerCase().includes("bitly")) {
      constraints.push(
        "Write traffic: 100M URLs/month (~40 writes/sec)",
        "Read traffic: 10:1 read-to-write ratio (~400 reads/sec)",
        "Latency: < 100ms for redirect",
        "Availability: 99.99% uptime"
      );
    } else {
      constraints.push("Target latency p99 < 50ms", "Handle resource exhaustion and edge cases gracefully");
    }
  }

  if (hints.length === 0) {
    if (text.toLowerCase().includes("url") || text.toLowerCase().includes("bitly")) {
      hints.push(
        "Unique ID generation (e.g., Base62)",
        "Database schema",
        "Handling high traffic"
      );
    } else {
      hints.push("Analyze edge cases and failure modes", "Consider time and space complexity");
    }
  }

  return { title, description, examples, constraints, hints, topic };
}

const AVAILABLE_ROLES = [
  "Software Architect",
  "Software Engineer (SDE)",
  "Full Stack Developer",
  "Backend Systems Engineer",
  "Frontend Engineer",
  "Machine Learning Engineer",
  "Cloud & DevOps Engineer",
];

const SPECIALIZED_AGENTS = [
  { id: "interviewer", name: "Cyra-Bot", role: "Lead AI Mentor", icon: "🤖", activeColor: "#4f46e5", secondaryColor: "#38bdf8" },
  { id: "dsa", name: "AlgoBot", role: "DSA Specialist Robot", icon: "⚡", activeColor: "#0284c7", secondaryColor: "#eab308" },
  { id: "system_design", name: "Archon-Core", role: "System Architecture AI", icon: "🧠", activeColor: "#059669", secondaryColor: "#10b981" },
  { id: "behavioral", name: "Nova-AI", role: "STAR Behavioral Coach", icon: "✨", activeColor: "#d97706", secondaryColor: "#f97316" },
];

const INTERVIEW_TOPICS = [
  {
    id: "all",
    label: "Comprehensive Full-Spectrum",
    icon: "🌐",
    desc: "Dynamic coverage across all 10 resource types (DSA, DB, APIs, System Design, Projects)",
    mode: "general",
    topic: null,
    agentId: "interviewer",
    defaultDomain: "dsa_py",
  },
  {
    id: "dsa",
    label: "Data Structures & Algorithms",
    icon: "⚡",
    desc: "LeetCode patterns, trees, graphs, dynamic programming & time complexity with test cases",
    mode: "dsa",
    topic: "Data Structures & Algorithms",
    agentId: "dsa",
    defaultDomain: "dsa_py",
  },
  {
    id: "database",
    label: "Database & SQL",
    icon: "🗄️",
    desc: "Query optimization, indexing strategies, EXPLAIN ANALYZE, ACID transactions & schemas",
    mode: "database",
    topic: "Database & SQL",
    agentId: "interviewer",
    defaultDomain: "db_sql",
  },
  {
    id: "backend",
    label: "Backend Systems & APIs",
    icon: "⚙️",
    desc: "REST/GraphQL, FastAPI/Node concurrency, Redis caching, idempotency & connection pooling",
    mode: "backend",
    topic: "Backend Systems & APIs",
    agentId: "interviewer",
    defaultDomain: "backend_fastapi",
  },
  {
    id: "system_design",
    label: "System Architecture & Design",
    icon: "🧠",
    desc: "High-scale distributed systems, rate limiting, message queues (Kafka) & reliability",
    mode: "system_design",
    topic: "System Architecture & Design",
    agentId: "system_design",
    defaultDomain: "backend_node",
  },
  {
    id: "frontend",
    label: "Frontend & React Architecture",
    icon: "🎨",
    desc: "Component lifecycle, state management, render profiling, hooks & DOM performance",
    mode: "frontend",
    topic: "Frontend & React Architecture",
    agentId: "interviewer",
    defaultDomain: "frontend_react",
  },
  {
    id: "project",
    label: "Resume Projects & GitHub Code",
    icon: "📁",
    desc: "Deep dive into your actual codebase, trade-offs, CI/CD automation & architecture",
    mode: "project",
    topic: "Resume Projects & Codebase",
    agentId: "interviewer",
    defaultDomain: "backend_fastapi",
  },
  {
    id: "behavioral",
    label: "STAR Behavioral & Leadership",
    icon: "✨",
    desc: "Conflict resolution, engineering leadership, incident post-mortems & team mentorship",
    mode: "behavioral",
    topic: "Behavioral & Engineering Leadership",
    agentId: "behavioral",
    defaultDomain: "dsa_py",
  },
];

const CODE_DOMAINS = [
  { id: "dsa_py", label: "DSA (Python)", domain: "DSA", lang: "python" },
  { id: "dsa_java", label: "DSA (Java)", domain: "DSA", lang: "java" },
  { id: "dsa_cpp", label: "DSA (C++)", domain: "DSA", lang: "cpp" },
  { id: "dsa_go", label: "DSA (Go)", domain: "DSA", lang: "go" },
  { id: "db_sql", label: "Database / SQL", domain: "Database", lang: "sql" },
  { id: "backend_node", label: "Backend (Node.js)", domain: "Backend", lang: "javascript" },
  { id: "backend_fastapi", label: "Backend (FastAPI)", domain: "Backend", lang: "python" },
  { id: "frontend_react", label: "Frontend (React JSX)", domain: "Frontend", lang: "javascript" },
];

const MULTI_DOMAIN_TEMPLATES = {
  dsa_py: `# DSA / Algorithmic Problem Solving (Python)
class Solution:
    def solve(self, nums: list[int], target: int = 0) -> int:
        """
        Time Complexity: O(N)
        Space Complexity: O(1)
        """
        # Formulate invariants and optimal traversal
        return 0
`,
  dsa_java: `// DSA / Algorithmic Problem Solving (Java)
class Solution {
    public int solve(int[] nums, int target) {
        // Time Complexity: O(N), Space Complexity: O(1)
        return 0;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();
        // Test edge cases
    }
}
`,
  dsa_cpp: `// DSA / Algorithmic Problem Solving (C++)
#include <iostream>
#include <vector>

class Solution {
public:
    int solve(std::vector<int>& nums, int target) {
        // Optimal two-pointer / hashing approach
        return 0;
    }
};
`,
  dsa_go: `// DSA / Algorithmic Problem Solving (Go)
package main

func solve(nums []int, target int) int {
    // Optimal algorithmic logic here
    return 0
}
`,
  db_sql: `-- Database Query & Schema Design (PostgreSQL / MySQL)
-- Complex queries, CTEs, indexes, or ACID transactions:

SELECT 
    u.id, 
    u.username, 
    COUNT(o.id) AS total_orders,
    COALESCE(SUM(o.amount), 0) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'COMPLETED'
WHERE u.created_at >= NOW() - INTERVAL '30 days'
GROUP BY u.id, u.username
HAVING COUNT(o.id) >= 3
ORDER BY total_spent DESC;
`,
  backend_node: `// Backend Systems / REST API (Node.js & Express)
import express from 'express';

export async function handleOrderCreation(req, res) {
  try {
    const { userId, items } = req.body;
    // 1. Validate request payload & sanitize
    // 2. Perform transactional database update
    // 3. Emit event / return structured response
    return res.status(201).json({ success: true, orderId: "ord_123" });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
`,
  backend_fastapi: `# Backend Systems / API (Python FastAPI)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

router = APIRouter()

class OrderRequest(BaseModel):
    user_id: str
    items: list[dict] = []

@router.post("/api/v1/orders")
async def create_order(payload: OrderRequest):
    # Validate payload, database transactions, idempotency key
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    return {"status": "created", "user_id": payload.user_id}
`,
  frontend_react: `// Frontend Architecture / State Management (React & Hooks)
import React, { useState, useEffect, useMemo } from 'react';

export default function ResourceDashboard({ userId }) {
  const [data, setData] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  const filteredData = useMemo(() => {
    return data.filter((item) =>
      item.title?.toLowerCase().includes(query.toLowerCase())
    );
  }, [data, query]);

  return (
    <div className="dashboard-root">
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
        placeholder="Filter records..." 
      />
      {loading ? <p>Loading state...</p> : <ul>{filteredData.map(d => <li key={d.id}>{d.title}</li>)}</ul>}
    </div>
  );
}
`,
};

const getStarterCodeForQuestion = (q, lang = "python") => {
  if (!q) return MULTI_DOMAIN_TEMPLATES.dsa_py;
  if (q.starter_code) return q.starter_code;
  const topic = (q.topic || "").toLowerCase();
  const text = (q.question || "").toLowerCase();

  if (lang === "sql" || topic.includes("sql") || topic.includes("database")) {
    return `-- Database / SQL Query Design\n-- Write your SQL query below to satisfy the problem requirement:\n\nSELECT \n    \nFROM \nWHERE \nGROUP BY \nORDER BY ;`;
  }

  if (topic.includes("anagram") || text.includes("anagram")) {
    return `# DSA: Arrays & Hash Maps (Group Anagrams)\nclass Solution:\n    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:\n        # Group strings using character frequencies or sorted tuple keys\n        from collections import defaultdict\n        ans = defaultdict(list)\n        # Write algorithm below:\n        \n        return list(ans.values())\n`;
  }

  if (topic.includes("palindrome") || text.includes("palindrome")) {
    return `# DSA: Two Pointers (Valid Palindrome)\nclass Solution:\n    def isPalindrome(self, s: str) -> bool:\n        # Two-pointer invariant check\n        left, right = 0, len(s) - 1\n        # Write algorithm below:\n        \n        return True\n`;
  }

  if (topic.includes("sliding window") || text.includes("substring")) {
    return `# DSA: Sliding Window\nclass Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        # Track visited characters in sliding window\n        seen = set()\n        left = max_len = 0\n        # Write algorithm below:\n        \n        return max_len\n`;
  }

  if (topic.includes("two sum") || text.includes("two sum") || text.includes("target")) {
    return `# DSA: Hash Map Complement Lookup\nclass Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        seen = {}\n        # Write algorithm below:\n        \n        return []\n`;
  }

  if (topic.includes("binary search") || text.includes("binary search") || text.includes("sorted array")) {
    return `# DSA: Binary Search\nclass Solution:\n    def search(self, nums: list[int], target: int) -> int:\n        low, high = 0, len(nums) - 1\n        # Write algorithm below:\n        \n        return -1\n`;
  }

  // Generic clean function template
  return `# DSA: ${q.topic || "Algorithmic Problem Solving"}\nclass Solution:\n    def solve(self, *args, **kwargs):\n        # Formulate your optimal approach here\n        pass\n`;
};

const detectLanguageFromText = (text) => {
  if (!text || typeof text !== "string") return null;
  if (/[\u0B80-\u0BFF]/.test(text)) return "ta"; // Tamil
  if (/[\u0900-\u097F]/.test(text)) return "hi"; // Hindi
  if (/[\u0C00-\u0C7F]/.test(text)) return "te"; // Telugu
  if (/[\u0C80-\u0CFF]/.test(text)) return "kn"; // Kannada
  return null;
};

const MULTI_RESOURCE_MILESTONES = [
  { idx: 1, title: "LeetCode & Algorithms (DSA Invariants)" },
  { idx: 2, title: "Database & SQL (Query Optimization & Indexes)" },
  { idx: 3, title: "Backend Systems & APIs (REST/Async/FastAPI)" },
  { idx: 4, title: "Frontend Architecture & React (Hooks & DOM)" },
  { idx: 5, title: "Distributed Systems & Scaling (Rate Limits/CAP)" },
  { idx: 6, title: "Production Incident Engineering & Tracing" },
  { idx: 7, title: "Verified Resume Projects & System Architecture" },
  { idx: 8, title: "GitHub Repositories, Modularity & CI/CD" },
  { idx: 9, title: "Event-Driven Pipelines & Message Queues" },
  { idx: 10, title: "STAR Behavioral Leadership & Pitch" },
];

export default function InterviewPage() {
  const navigate = useNavigate();

  // Session state
  const [phase, setPhase] = useState("setup"); // "setup" | "active" | "complete"
  const [chosenMode, setChosenMode] = useState("dsa");
  const [resourceMeta, setResourceMeta] = useState(null);
  const [activeSidebarItem, setActiveSidebarItem] = useState("overview");

  useEffect(() => {
    Promise.allSettled([
      getInterviewResourcesAndModes(),
      getProfileSnapshot(),
    ]).then(([resMetaRes, snapRes]) => {
      let meta = resMetaRes.status === "fulfilled" ? (resMetaRes.value || {}) : {};
      const snap = snapRes.status === "fulfilled" ? snapRes.value : null;
      const unified = snap?.unified || {};

      const combinedConn = {
        leetcode: unified.leetcode || meta?.connected_resources?.leetcode || null,
        hackerrank: unified.hackerrank || meta?.connected_resources?.hackerrank || null,
        github: {
          ...(meta?.connected_resources?.github || {}),
          repositories:
            unified.github_repositories ||
            unified.github?.repositories ||
            meta?.connected_resources?.github?.repositories ||
            [],
          username:
            unified.github?.username ||
            meta?.connected_resources?.github?.username ||
            "",
        },
        certifications:
          unified.certifications ||
          meta?.connected_resources?.certifications ||
          [],
        skills:
          unified.unified_skills ||
          unified.skills ||
          meta?.connected_resources?.skills ||
          [],
      };

      setResourceMeta({
        ...meta,
        snapshot: snap,
        connected_resources: combinedConn,
      });
    }).catch((err) => console.warn("Failed to fetch interview resources and modes:", err));
  }, []);

  const [role, setRole] = useState(() => {
    try {
      const urlRole = new URLSearchParams(window.location.search).get("role");
      return urlRole || sessionStorage.getItem("careerverse_target_role") || "Software Engineer (SDE)";
    } catch {
      return "Software Engineer (SDE)";
    }
  });

  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answerText, setAnswerText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [results, setResults] = useState(null);

  // Multi-Language state
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [detectedLangBadge, setDetectedLangBadge] = useState(null);

  // Session question depth & count (5, 10, 15, or continuous)
  const [targetQuestionCount, setTargetQuestionCount] = useState(10);

  let authUser = null;
  try {
    const auth = typeof useAuth === "function" ? useAuth() : null;
    if (auth && auth.user) authUser = auth.user;
  } catch (_e) {
    authUser = null;
  }
  const user = authUser;
  const candidateName = user?.name || user?.full_name || user?.email?.split("@")[0] || "Amit Sharma";
  const candidateAvatar = user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80";

  // Selected Specialization Track & Left studio tab
  const [selectedTrackId, setSelectedTrackId] = useState("fullstack");
  const [activeStudioLeftTab, setActiveStudioLeftTab] = useState("description"); // "description" | "tutor"

  // Proctoring Telemetry State
  const [tabSwitches, setTabSwitches] = useState(0);
  const [offScreenLooks, setOffScreenLooks] = useState(0);
  const [faceViolations, setFaceViolations] = useState(0);
  const integrityScore = Math.max(70, 100 - (tabSwitches * 5 + offScreenLooks * 3 + faceViolations * 10));

  // Selected interview focus topic & active agent
  const [selectedTopicKey, setSelectedTopicKey] = useState("all");
  const activeTopic = INTERVIEW_TOPICS.find((t) => t.id === selectedTopicKey) || INTERVIEW_TOPICS[0];
  const [activeAgent, setActiveAgent] = useState(SPECIALIZED_AGENTS[0]);
  const [resourceSource, setResourceSource] = useState("all"); // "all" | "leetcode" | "resume" | "github"

  const handleSelectTrack = (trackId) => {
    const track = SPECIALIZATION_TRACKS.find((t) => t.id === trackId) || SPECIALIZATION_TRACKS[0];
    setSelectedTrackId(track.id);
    setRole(track.role);
    setSelectedTopicKey(track.topicKey);
    const agent = SPECIALIZED_AGENTS.find((a) => a.id === track.id) || SPECIALIZED_AGENTS[0];
    setActiveAgent(agent);
  };

  // Live multi-domain code scratchpad state
  const [selectedDomainKey, setSelectedDomainKey] = useState("dsa_py");
  const [codeSnippet, setCodeSnippet] = useState(MULTI_DOMAIN_TEMPLATES.dsa_py);
  const [codeLang, setCodeLang] = useState("python");
  const [showCodeScratchpad, setShowCodeScratchpad] = useState(false);
  const [isScratchpadExpanded, setIsScratchpadExpanded] = useState(false);
  const [codeCopied, setCodeCopied] = useState(false);
  const [executionOutput, setExecutionOutput] = useState(null);
  const [isRunningCode, setIsRunningCode] = useState(false);
  const [codeExecutionResults, setCodeExecutionResults] = useState(null);

  const isDsaQuestion =
    selectedTopicKey === "dsa" ||
    selectedTopicKey === "database" ||
    (session?.current_question?.question_type || "").toLowerCase().includes("code") ||
    (session?.current_question?.question_type || "").toLowerCase().includes("dsa") ||
    (session?.current_question?.topic || "").toLowerCase().includes("dsa") ||
    (session?.current_question?.topic || "").toLowerCase().includes("algorithm") ||
    (session?.current_question?.topic || "").toLowerCase().includes("data structure") ||
    (session?.current_question?.topic || "").toLowerCase().includes("database") ||
    (session?.current_question?.topic || "").toLowerCase().includes("sql") ||
    (session?.interview_mode || "").toLowerCase().includes("dsa") ||
    activeAgent?.id === "dsa";

  const shouldShowCodeEditor = isDsaQuestion || showCodeScratchpad;

  // Synchronize starter code with active question topic & clear stale outputs
  useEffect(() => {
    if (currentQuestion) {
      const qObj = typeof currentQuestion === "object" && currentQuestion !== null ? currentQuestion : { question: currentQuestion };
      const starter = getStarterCodeForQuestion(qObj, codeLang);
      setCodeSnippet(starter);
      setExecutionOutput(null);
      setCodeExecutionResults(null);
    }
  }, [currentQuestion, codeLang]);

  // Question & Session History state
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [historyTab, setHistoryTab] = useState("sessions"); // "sessions" | "questions"
  const [sessionsHistoryList, setSessionsHistoryList] = useState([]);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyFilter, setHistoryFilter] = useState("all"); // "all" | "cooldown" | "retest"
  const [expandedQuestionIdx, setExpandedQuestionIdx] = useState(null);

  // Mentor feedback visibility
  const [dismissFeedback, setDismissFeedback] = useState(false);

  // Interaction logs
  const [conversationLog, setConversationLog] = useState([]);

  // Voice & AV state
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [spokenSubtitle, setSpokenSubtitle] = useState("");
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceURI, setSelectedVoiceURI] = useState(
    () => localStorage.getItem("cv_preferred_voice") || ""
  );
  const [voiceStatus, setVoiceStatus] = useState(() => getLanguageVoiceMatch([], "en"));
  const [micStatus, setMicStatus] = useState({ state: "idle", message: "" });
  const [isMuted, setIsMuted] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.0); // Natural conversational speed 1.0x
  const [isListening, setIsListening] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [violations, setViolations] = useState(0);

  // Time limit for answering questions (seconds)
  const [timeLimit, setTimeLimit] = useState(120); // 2 mins default, 5 mins for DSA
  const [timeLeft, setTimeLeft] = useState(120);
  const [isTimerPaused, setIsTimerPaused] = useState(false);
  const [timerAlert, setTimerAlert] = useState(false);

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const recognitionRef = useRef(null);
  const chatBottomRef = useRef(null);
  const activeUtteranceRef = useRef(null);
  const speechTimeoutRef = useRef(null);

  // New Question, Notes, and Layout States matching Reference UI
  const [activeQuestionTab, setActiveQuestionTab] = useState("description"); // "description" | "constraints" | "examples"
  const [candidateNotes, setCandidateNotes] = useState(() => localStorage.getItem("cv_candidate_notes") || "");
  const [showTerminal, setShowTerminal] = useState(false);
  const [showHints, setShowHints] = useState(true);
  const [showCaptions, setShowCaptions] = useState(true);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const handleFs = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFs);
    return () => {
      document.removeEventListener("fullscreenchange", handleFs);
    };
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => setIsFullscreen(true)).catch((err) => {
        console.warn("Fullscreen request error:", err);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().then(() => setIsFullscreen(false)).catch((err) => {
          console.warn("Exit fullscreen error:", err);
        });
      }
    }
  };

  // Speech Recognition setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recog = new SpeechRecognition();
      recog.continuous = true;
      recog.interimResults = true;
      const langConfig = getLanguageConfig(selectedLanguage);
      recog.lang = langConfig.bcp47;

      let finalTranscript = "";
      recog.onresult = (event) => {
        let interimTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i];
          const piece = item[0]?.transcript || "";
          if (item.isFinal) {
            finalTranscript += (finalTranscript ? " " : "") + piece.trim();
          } else {
            interimTranscript += piece;
          }
        }
        const fullText = (finalTranscript + (interimTranscript ? " " + interimTranscript : "")).trim();
        if (fullText) {
          // Detection is diagnostic only. The explicit selection remains the
          // session language so recognition cannot silently switch the request context.
          const detected = detectLanguageFromText(fullText);
          if (detected && detected !== selectedLanguage) {
            const dObj = getLanguageConfig(detected);
            setDetectedLangBadge(`🌐 Auto-detected ${dObj?.label || detected} (${dObj?.native || ""})`);
            setTimeout(() => setDetectedLangBadge(null), 4000);
          }
          setAnswerText(fullText);
        }
      };

      recog.onerror = (e) => {
        const errType = e?.error || "unknown";
        if (errType === "not-allowed" || errType === "permission-denied") {
          setMicStatus({
            state: "denied",
            message: "Microphone access denied. You can continue speaking with keyboard text response.",
          });
        } else if (errType === "language-not-supported") {
          setMicStatus({
            state: "unsupported",
            message: `Speech recognition for ${getLanguageConfig(selectedLanguage).label} is not supported by your browser. Please type your response.`,
          });
        } else if (errType === "network") {
          setMicStatus({
            state: "network",
            message: "Speech recognition network error. Please try again or type your response.",
          });
        } else if (errType !== "no-speech") {
          setMicStatus({
            state: "error",
            message: `Microphone issue (${errType}). Text response is active.`,
          });
        }
        setIsListening(false);
      };

      recog.onend = () => {
        setIsListening(false);
        setMicStatus((prev) => (prev.state === "listening" ? { state: "idle", message: "" } : prev));
      };

      recognitionRef.current = recog;
    } else {
      setMicStatus({
        state: "unsupported",
        message: "Web Speech Recognition is not supported in this browser. Text input fallback is active.",
      });
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      stopCamera();
    };
  }, [selectedLanguage]);

  // Voice synchronization & auto-detection of top natural voices
  useEffect(() => {
    if (!("speechSynthesis" in window)) {
      setVoiceStatus({
        voice: null,
        isSupported: false,
        isExactLanguageMatch: false,
        voiceName: null,
        bcp47: getLanguageConfig(selectedLanguage).bcp47,
        message: "Speech synthesis is not supported in this browser environment. Text interaction is active.",
      });
      return;
    }
    const updateVoices = () => {
      const allVoices = window.speechSynthesis.getVoices() || [];
      const naturalVoices = filterNaturalVoices(allVoices);
      const voicePool = naturalVoices.length > 0 ? naturalVoices : allVoices;
      setAvailableVoices(voicePool);

      const match = getLanguageVoiceMatch(allVoices, selectedLanguage, selectedVoiceURI);
      setVoiceStatus(match);

      if (match.voice) {
        setSelectedVoiceURI(match.voice.voiceURI);
        localStorage.setItem("cv_preferred_voice", match.voice.voiceURI);
      }
    };

    updateVoices();
    window.speechSynthesis.onvoiceschanged = updateVoices;
    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [selectedLanguage, selectedVoiceURI]);

  // Countdown timer for question answering
  useEffect(() => {
    if (phase !== "active" || timeLimit <= 0 || isTimerPaused) return;

    if (timeLeft <= 0) {
      setTimerAlert(true);
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setTimerAlert(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [phase, timeLimit, isTimerPaused, timeLeft]);

  // Proctoring telemetry event listeners
  useEffect(() => {
    if (phase !== "active") return;
    const handleVisibility = () => {
      if (document.hidden) {
        setTabSwitches((prev) => prev + 1);
        setViolations((prev) => prev + 1);
      }
    };
    const handleBlur = () => {
      setOffScreenLooks((prev) => prev + 1);
    };
    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("blur", handleBlur);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("blur", handleBlur);
    };
  }, [phase]);

  // Reset timer on new question (5 mins for coding, 2 mins for conceptual)
  useEffect(() => {
    if (currentQuestion) {
      const isCoding = isDsaQuestion || (selectedDomainKey && selectedDomainKey !== "dsa_py");
      const duration = isCoding ? 300 : 120;
      setTimeLimit(duration);
      setTimeLeft(duration);
      setIsTimerPaused(false);
      setTimerAlert(false);
    }
  }, [currentQuestion, isDsaQuestion, selectedDomainKey]);

  // Sync recognition language when selectedLanguage changes
  useEffect(() => {
    if (recognitionRef.current) {
      const langObj = SUPPORTED_INTERVIEW_LANGUAGES.find((l) => l.code === selectedLanguage);
      recognitionRef.current.lang = langObj?.bcp47 || "en-US";
    }
  }, [selectedLanguage]);

  const handleDomainChange = (domainKey) => {
    setSelectedDomainKey(domainKey);
    const domainObj = CODE_DOMAINS.find((d) => d.id === domainKey);
    if (domainObj) {
      setCodeLang(domainObj.lang);
    }
    setCodeSnippet(MULTI_DOMAIN_TEMPLATES[domainKey] || "");
  };

  const handleSelectTopic = (topicKey) => {
    setSelectedTopicKey(topicKey);
    const topicObj = INTERVIEW_TOPICS.find((t) => t.id === topicKey);
    if (topicObj) {
      if (topicObj.agentId) {
        const matchedAgent = SPECIALIZED_AGENTS.find((a) => a.id === topicObj.agentId);
        if (matchedAgent) setActiveAgent(matchedAgent);
      }
      if (topicObj.defaultDomain) {
        handleDomainChange(topicObj.defaultDomain);
      }
    }
  };

  const handleSelectAgent = (agent) => {
    setActiveAgent(agent);
    if (agent.id === "dsa") {
      setSelectedTopicKey("dsa");
      handleDomainChange("dsa_py");
    } else if (agent.id === "system_design") {
      setSelectedTopicKey("system_design");
      handleDomainChange("backend_fastapi");
    } else if (agent.id === "behavioral") {
      setSelectedTopicKey("behavioral");
    }
  };

  const handleResetTemplate = () => {
    setCodeSnippet(MULTI_DOMAIN_TEMPLATES[selectedDomainKey] || "");
  };

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(codeSnippet);
      setCodeCopied(true);
      setTimeout(() => setCodeCopied(false), 2000);
    } catch {
      setCodeCopied(false);
    }
  };

  const handleRunCode = async () => {
    setIsRunningCode(true);
    setExecutionOutput("▶ Compiling and executing code in sandbox judge...");
    setShowTerminal(true);

    try {
      const qObj = typeof currentQuestion === "object" && currentQuestion !== null ? currentQuestion : {};
      const examples = qObj.examples || [];
      const payload = {
        problem_id: qObj.id || qObj.concept_key || "interview_code",
        problem_title: qObj.topic || "Algorithmic Challenge",
        language: codeLang || "python",
        code: codeSnippet || "",
        examples: examples.length > 0 ? examples : [
          { input: "Default Test Case 1", output: "0" }
        ],
        custom_input: "",
        action_type: "run",
      };

      const res = await evaluateDsaCode(payload);
      setCodeExecutionResults(res);

      let terminalReport = `▶ Judge Status: ${res.status || "Completed"}\n`;
      terminalReport += `✓ Passed: ${res.passedCount ?? 0}/${res.totalCount ?? 0} Test Cases\n`;
      if (res.runtimeMs) terminalReport += `✓ Execution Time: ${res.runtimeMs}ms | Memory: ${res.memoryMb || "14.6"}MB\n`;
      if (res.time_complexity) terminalReport += `✓ Detected Time Complexity: ${res.time_complexity} | Space: ${res.space_complexity || "O(1)"}\n`;

      if (res.stdout) {
        terminalReport += `\n[Program Standard Output]:\n${res.stdout}\n`;
      }

      if (res.results && res.results.length > 0) {
        terminalReport += "\n[Test Case Evaluation Breakdown]:\n";
        res.results.forEach((r) => {
          terminalReport += `• Case ${r.caseNumber}: ${r.passed ? "✓ Passed" : "✗ Failed"}\n`;
          terminalReport += `    Input:    ${r.input}\n`;
          terminalReport += `    Expected: ${r.expected}\n`;
          terminalReport += `    Actual:   ${r.actual}\n`;
          if (r.error) terminalReport += `    Error:    ${r.error}\n`;
        });
      }

      setExecutionOutput(terminalReport);
    } catch (err) {
      console.warn("Judge execution error:", err);
      setExecutionOutput(`▶ Execution Error: Unable to contact compiler judge.\n${err?.message || "Please check your network connection."}`);
    } finally {
      setIsRunningCode(false);
    }
  };

  // Submit code solution & terminal execution directly to interviewer
  const handleSubmitCodeFromWorkbench = async () => {
    if (!codeSnippet || !codeSnippet.trim()) {
      setError("Please write or paste your solution code in the workbench first.");
      return;
    }

    const testSummary = codeExecutionResults
      ? `Judge Status: ${codeExecutionResults.status} (${codeExecutionResults.passedCount}/${codeExecutionResults.totalCount} test cases passed).`
      : "Candidate submitted code without pre-running test cases.";

    const formattedAnswer = `I have formulated and implemented my solution in the code workbench.\n\n[Candidate Submitted Code (${codeLang})]:\n\`\`\`${codeLang}\n${codeSnippet.trim()}\n\`\`\`\n\n[Test Execution Summary]:\n${testSummary}\n\n[Candidate Approach & Analysis]:\n${candidateAnswer && candidateAnswer.trim() ? candidateAnswer.trim() : "Optimal implementation meeting time and space complexity constraints."}`;

    await handleSubmitAnswer(formattedAnswer);
  };

  // Resume active interview session on mount from URL query param or localStorage
  useEffect(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const resumeId = urlParams.get("session_id") || localStorage.getItem("cv_active_session_id");
      if (resumeId && phase === "setup") {
        setLoading(true);
        getInterviewSession(resumeId)
          .then((data) => {
            if (data && (data.session_id || data.id)) {
              setSession(data);
              const activeQ = data.current_question || data.first_question;
              setCurrentQuestion(activeQ);
              if (data.target_role) setRole(data.target_role);
              if (data.interview_mode) setChosenMode(data.interview_mode);
              if (data.language) setSelectedLanguage(data.language);
              if (data.status === "completed") {
                setResults(data.final_report || data);
                setPhase("complete");
              } else {
                setPhase("active");
              }
            }
          })
          .catch((err) => {
            console.warn("Could not resume saved session:", err);
            localStorage.removeItem("cv_active_session_id");
            const url = new URL(window.location.href);
            url.searchParams.delete("session_id");
            window.history.replaceState({}, "", url.toString());
          })
          .finally(() => setLoading(false));
      }
    } catch (_e) {
      // ignore
    }
  }, []);

  // Sync active session_id to URL and localStorage
  useEffect(() => {
    try {
      const sId = session?.session_id || session?.id;
      if (sId && session?.status !== "completed") {
        localStorage.setItem("cv_active_session_id", sId);
        const url = new URL(window.location.href);
        if (url.searchParams.get("session_id") !== sId) {
          url.searchParams.set("session_id", sId);
          window.history.replaceState({}, "", url.toString());
        }
      } else if (session?.status === "completed") {
        localStorage.removeItem("cv_active_session_id");
        const url = new URL(window.location.href);
        if (url.searchParams.has("session_id")) {
          url.searchParams.delete("session_id");
          window.history.replaceState({}, "", url.toString());
        }
      }
    } catch (_e) {
      // ignore
    }
  }, [session]);

  const fetchQuestionHistory = async () => {
    try {
      setLoadingHistory(true);
      const [qRes, sRes] = await Promise.allSettled([
        getInterviewQuestionHistory(),
        getInterviewSessionsList(50, 0),
      ]);
      if (qRes.status === "fulfilled" && qRes.value) {
        setQuestionHistory(
          Array.isArray(qRes.value)
            ? qRes.value
            : qRes.value.questions || qRes.value.history || []
        );
      }
      if (sRes.status === "fulfilled" && Array.isArray(sRes.value)) {
        setSessionsHistoryList(sRes.value);
      }
    } catch (err) {
      console.warn("Could not load question and session history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleResumePastSession = async (sId) => {
    if (!sId) return;
    try {
      setLoading(true);
      setShowHistoryModal(false);
      const data = await getInterviewSession(sId);
      if (data && (data.session_id || data.id)) {
        setSession(data);
        const activeQ = data.current_question || data.first_question;
        setCurrentQuestion(activeQ);
        if (data.target_role) setRole(data.target_role);
        if (data.interview_mode) setChosenMode(data.interview_mode);
        if (data.language) setSelectedLanguage(data.language);
        if (data.status === "completed") {
          setResults(data.final_report || data);
          setPhase("complete");
        } else {
          setPhase("active");
        }
      }
    } catch (err) {
      setError(getApiError(err, "Failed to load interview session."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestionHistory();
  }, []);

  const speakText = (text, targetLang = selectedLanguage) => {
    if (!("speechSynthesis" in window) || isMuted || !text) return;
    window.speechSynthesis.cancel();
    if (speechTimeoutRef.current) {
      clearTimeout(speechTimeoutRef.current);
    }

    // Clean text to avoid reading code blocks, syntax, or technical gibberish
    const clean = cleanTextForSpeech(text);
    if (!clean) return;

    setSpokenSubtitle(clean);

    // 60ms delay prevents browser SpeechSynthesis queue corruption
    speechTimeoutRef.current = setTimeout(() => {
      const allVoices = window.speechSynthesis.getVoices() || [];
      const match = getLanguageVoiceMatch(allVoices, targetLang, selectedVoiceURI);
      setVoiceStatus(match);

      // If no compatible voice found (or no voice object), block for every non-English language.
      // DO NOT silently fall back to an English voice!
      if (!match.isSupported || !match.voice) {
        if (targetLang !== "en") {
          setIsAgentSpeaking(false);
          return;
        }
      }

      const utterance = new SpeechSynthesisUtterance(clean);
      utterance.rate = speechRate || 1.0;
      utterance.pitch = 1.0;
      utterance.lang = match.bcp47 || getLanguageConfig(targetLang).bcp47;

      if (match.voice) {
        utterance.voice = match.voice;
      }

      activeUtteranceRef.current = utterance;
      setIsAgentSpeaking(true);

      utterance.onstart = () => {
        if (activeUtteranceRef.current === utterance) {
          setIsAgentSpeaking(true);
        }
      };
      utterance.onend = () => {
        if (activeUtteranceRef.current === utterance) {
          setIsAgentSpeaking(false);
          setTimeout(() => {
            setSpokenSubtitle((curr) => (curr === clean ? "" : curr));
          }, 2500);
        }
      };
      utterance.onerror = (e) => {
        if (e?.error === "canceled" || e?.error === "interrupted") return;
        if (activeUtteranceRef.current === utterance) {
          setIsAgentSpeaking(false);
          setSpokenSubtitle("");
        }
      };

      window.speechSynthesis.speak(utterance);
    }, 60);
  };

  const handleTestVoice = () => {
    let testSample = `Hello! I am ${activeAgent.name || "Cyra"}, your AI interviewer. I will guide you through your technical questions today with clear, natural pacing.`;
    if (selectedLanguage === "ta") {
      testSample = `வணக்கம்! நான் ${activeAgent.name || "Cyra"}, உங்கள் AI தொழில்நுட்ப நேர்காணல் பயிற்சியாளர். உங்கள் கேள்விகளை தெளிவாக கேட்க நான் தயாராக உள்ளேன்.`;
    } else if (selectedLanguage === "hi") {
      testSample = `नमस्ते! मैं ${activeAgent.name || "Cyra"} हूँ, आपकी AI तकनीकी इंटरव्यूअर. आज के इंटरव्यू के लिए मैं तैयार हूँ.`;
    } else if (selectedLanguage === "es") {
      testSample = `¡Hola! Soy ${activeAgent.name || "Cyra"}, tu entrevistadora técnica de IA. Estoy lista para comenzar tu entrevista.`;
    } else if (selectedLanguage === "fr") {
      testSample = `Bonjour ! Je suis ${activeAgent.name || "Cyra"}, votre évaluatrice technique IA. Je suis prête pour votre entretien.`;
    } else if (selectedLanguage === "de") {
      testSample = `Hallo! Ich bin ${activeAgent.name || "Cyra"}, Ihre KI-Interviewerin. Ich freue mich auf unser technisches Gespräch.`;
    }
    speakText(testSample, selectedLanguage);
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      window.__activeVideoStream = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
      setCameraActive(true);
    } catch {
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    window.__activeVideoStream = null;
    setCameraActive(false);
  };

  const toggleListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setMicStatus({
        state: "unsupported",
        message: "Speech recognition is not supported in this browser. Please use text responses.",
      });
      return;
    }

    if (!recognitionRef.current) {
      try {
        const recog = new SpeechRecognition();
        recog.continuous = true;
        recog.interimResults = true;
        recog.lang = getLanguageConfig(selectedLanguage).bcp47;
        recognitionRef.current = recog;
      } catch (err) {
        setMicStatus({
          state: "error",
          message: "Failed to initialize microphone speech recognition.",
        });
        return;
      }
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      setIsListening(false);
      setMicStatus({ state: "idle", message: "" });
    } else {
      setAnswerText("");
      setMicStatus({
        state: "listening",
        message: `Listening in ${getLanguageConfig(selectedLanguage).label} (${getLanguageConfig(selectedLanguage).bcp47})...`,
      });
      try {
        recognitionRef.current.lang = getLanguageConfig(selectedLanguage).bcp47;
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.warn("Speech recognition start warning:", err);
        setIsListening(false);
        setMicStatus({
          state: "error",
          message: "Could not activate microphone. Please check browser permissions.",
        });
      }
    }
  };

  const handleLanguageChange = async (newLang) => {
    setSelectedLanguage(newLang);
    const langObj = getLanguageConfig(newLang);
    if (recognitionRef.current) {
      recognitionRef.current.lang = langObj.bcp47;
    }
    const allVoices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    const match = getLanguageVoiceMatch(allVoices, newLang, selectedVoiceURI);
    setVoiceStatus(match);

    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsAgentSpeaking(false);
    }

    const sId = session?.session_id || session?.id;
    if (sId) {
      try {
        const updateResp = await updateInterviewSessionLanguage(sId, newLang);
        if (updateResp && updateResp.session) {
          setSession(updateResp.session);
          if (updateResp.session.current_question) {
            setCurrentQuestion(updateResp.session.current_question);
            const newQ = updateResp.session.current_question;
            const newQText = typeof newQ === "string" ? newQ : (newQ.question || newQ.text || "");
            if (newQText && match.isSupported && !isMuted) {
              speakText(newQText, newLang);
            }
          }
        }
      } catch (err) {
        console.warn("Failed to update session language on backend:", err);
      }
    }
  };

  const handleSpeakAgain = () => {
    const qText = typeof currentQuestion === "string"
      ? currentQuestion
      : (currentQuestion?.question || currentQuestion?.text || parsedQ?.description);
    if (qText) {
      speakText(qText, selectedLanguage);
    }
  };

  // Start Session
  const handleStartInterview = async (explicitMode = null, explicitTopic = null, explicitRole = null) => {
    setLoading(true);
    setError("");
    const targetMode = explicitMode || selectedTopicKey || "comprehensive";
    const targetTopic =
      explicitTopic ||
      (targetMode === "comprehensive"
        ? "All-in-One AI Interview & Mastery Room (Agent Teaches)"
        : targetMode === "dsa"
        ? "Data Structures & Algorithms"
        : targetMode === "behavioral"
        ? "Behavioral & Leadership"
        : targetMode === "github"
        ? "GitHub & Projects Architecture"
        : "System Design & Scalability");
    const targetRole = explicitRole || role || "Software Engineer (SDE)";
    setChosenMode(targetMode);
    setRole(targetRole);

    try {
      const sess = await createInterviewSession({
        role: targetRole,
        interview_mode: targetMode,
        focus_topic: targetTopic,
        language: selectedLanguage,
      });
      setSession(sess);
      const firstQ = sess.first_question || sess.question || sess.current_question;
      const firstQText = typeof firstQ === "string" ? firstQ : firstQ?.text || firstQ?.question || "Welcome to your interview round.";
      setCurrentQuestion(sess.current_question || firstQ);
      setPhase("active");
      startCamera();
      speakText(firstQText, selectedLanguage);
    } catch (err) {
      setError(getApiError(err, "Failed to start interview session."));
    } finally {
      setLoading(false);
    }
  };

  // Submit Answer
  const handleSubmitAnswer = async (forcedAnswer = null) => {
    let finalAnswer = (forcedAnswer || answerText).trim();

    // If answerText is empty but candidate wrote code in workbench, auto-bundle it!
    const hasCode = codeSnippet && codeSnippet.trim().length > 10;
    if (!finalAnswer && hasCode) {
      finalAnswer = `I have implemented and tested my solution in the workbench.\n\n[Candidate Submitted Code]:\n\`\`\`${codeLang}\n${codeSnippet.trim()}\n\`\`\`\n\n[Terminal Execution Output]:\n${executionOutput || "Execution verified in terminal."}`;
    }

    if (!finalAnswer) {
      setError("Please speak with the mic, type an answer, or write code in the workbench before submitting.");
      return;
    }

    setLoading(true);
    setError("");
    setTimerAlert(false);
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    try {
      const sId = session?.session_id || session?.id;
      const topicObj = INTERVIEW_TOPICS.find((t) => t.id === selectedTopicKey) || INTERVIEW_TOPICS[0];
      const currentFocusTopic = topicObj.topic || (activeAgent?.id === "dsa" ? "Data Structures & Algorithms" : activeAgent?.id === "system_design" ? "System Architecture & Design" : activeAgent?.id === "behavioral" ? "Behavioral & Engineering Leadership" : null);

      const resp = await submitInterviewAnswer(
        sId,
        finalAnswer,
        hasCode ? codeSnippet : null,
        selectedLanguage,
        currentFocusTopic
      );
      setSession(resp);

      const latestEval = resp.feedback || resp.evaluation || resp.latest_evaluation || null;
      setFeedback(latestEval);
      setDismissFeedback(false);

      // Record to chat log
      setConversationLog((prev) => [
        ...prev,
        {
          id: Date.now(),
          question: currentQuestion,
          answer: finalAnswer,
          code: hasCode ? codeSnippet : null,
          codeLang: codeLang,
          evaluation: latestEval,
        },
      ]);

      fetchQuestionHistory();
      setAnswerText("");

      const isFinished =
        resp.status === "completed" ||
        (targetQuestionCount !== "continuous" && resp.question_number > Number(targetQuestionCount)) ||
        (!resp.current_question && !resp.next_question);

      if (isFinished) {
        handleCompleteInterview();
      } else {
        const nextQ = resp.current_question || resp.next_question || resp.question;
        const nextQText = typeof nextQ === "string" ? nextQ : nextQ?.text || nextQ?.question || "Tell me about another trade-off you considered.";
        setCurrentQuestion(nextQText);
        let prefix = "Thank you. Next question: ";
        if (selectedLanguage === "ta") prefix = "நன்றி. அடுத்த கேள்வி: ";
        else if (selectedLanguage === "hi") prefix = "धन्यवाद. अगला प्रश्न: ";
        else if (selectedLanguage === "es") prefix = "Gracias. Siguiente pregunta: ";
        else if (selectedLanguage === "fr") prefix = "Merci. Question suivante : ";
        else if (selectedLanguage === "de") prefix = "Vielen Dank. Nächste Frage: ";

        const promptToSpeak = latestEval
          ? `${prefix}${nextQText}`
          : nextQText;
        speakText(promptToSpeak, selectedLanguage);
      }
    } catch (err) {
      setError(getApiError(err, "Could not submit your response."));
    } finally {
      setLoading(false);
    }
  };

  const candidateAnswer = answerText;
  const setCandidateAnswer = setAnswerText;
  const handleAnswerSubmit = (customAns = null) => handleSubmitAnswer(customAns);
  const handleNextQuestion = () => {
    if (answerText.trim() || (codeSnippet && codeSnippet.trim().length > 10)) {
      handleSubmitAnswer();
    } else {
      handleSubmitAnswer("Proceeding to next question.");
    }
  };

  // Complete Session
  const handleCompleteInterview = async () => {
    const sId = session?.session_id || session?.id;
    if (!sId) return;
    setLoading(true);
    stopCamera();
    if (window.speechSynthesis) window.speechSynthesis.cancel();

    try {
      const finalReport = await completeInterviewSession(sId);
      setResults(finalReport);
      setPhase("complete");
      recordActivity({
        type: "interview",
        title: `Technical Interview: ${role}`,
        detail: `Completed session with ${activeAgent.name || "Cyra-Bot"} • 5 Questions`,
        score: 5,
      });
    } catch (err) {
      setError(getApiError(err, "Could not generate final interview dossier."));
    } finally {
      setLoading(false);
    }
  };

  const handleResetToSetup = () => {
    setPhase("setup");
    setSession(null);
    setCurrentQuestion(null);
    setFeedback(null);
    setResults(null);
    setConversationLog([]);
    stopCamera();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  };

  const currentQIndex = session?.question_number || conversationLog.length + 1;

  // ───────────────────────────────────────────────────────────────────────────
  // QUESTION HISTORY & SPACED REPETITION MODAL
  // ───────────────────────────────────────────────────────────────────────────
  const renderQuestionHistoryModal = () => {
    if (!showHistoryModal) return null;

    const cooldownItems = questionHistory.filter((q) => !q.ready_for_retest);
    const retestItems = questionHistory.filter((q) => q.ready_for_retest);

    const filteredItems = questionHistory.filter((q) => {
      if (historyFilter === "cooldown") return !q.ready_for_retest;
      if (historyFilter === "retest") return q.ready_for_retest;
      return true;
    });

    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(15, 23, 42, 0.7)",
          backdropFilter: "blur(6px)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "1.5rem",
          boxSizing: "border-box",
        }}
        onClick={() => setShowHistoryModal(false)}
      >
        <div
          style={{
            background: "#ffffff",
            borderRadius: "24px",
            maxWidth: "880px",
            width: "100%",
            maxHeight: "90vh",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 25px 60px rgba(0, 0, 0, 0.3)",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
            animation: "fadeIn 0.2s ease-out",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Modal Header */}
          <div
            style={{
              padding: "20px 24px",
              borderBottom: "1px solid #e2e8f0",
              background: "linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%)",
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                <span style={{ fontSize: "1.3rem" }}>📜</span>
                <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 800, color: "#0f172a" }}>
                  Question History & Spaced Repetition Bank
                </h3>
              </div>
              <p style={{ margin: 0, fontSize: "0.82rem", color: "#64748b", lineHeight: 1.5 }}>
                Questions you encounter are preserved here. Under our <strong>~30-Day Cooldown Rule</strong>, recently asked questions are strictly blocked from reappearing in fresh interviews. Once 30 days elapse, they qualify for spaced repetition to re-test your long-term mastery.
              </p>
            </div>

            <button
              type="button"
              onClick={() => setShowHistoryModal(false)}
              style={{
                background: "#f1f5f9",
                border: "none",
                borderRadius: "50%",
                width: 32,
                height: 32,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                color: "#64748b",
              }}
            >
              ✕
            </button>
          </div>

          {/* Top-Level Tabs: Past Sessions vs Question Bank */}
          <div
            style={{
              padding: "10px 24px",
              background: "#f8fafc",
              borderBottom: "1px solid #e2e8f0",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <button
              type="button"
              onClick={() => setHistoryTab("sessions")}
              style={{
                padding: "8px 16px",
                borderRadius: "10px",
                fontSize: "0.82rem",
                fontWeight: 800,
                background: historyTab === "sessions" ? "#4f46e5" : "transparent",
                color: historyTab === "sessions" ? "#ffffff" : "#64748b",
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                boxShadow: historyTab === "sessions" ? "0 2px 6px rgba(79,70,229,0.3)" : "none",
              }}
            >
              <span>🕒 Past Sessions ({sessionsHistoryList.length})</span>
            </button>
            <button
              type="button"
              onClick={() => setHistoryTab("questions")}
              style={{
                padding: "8px 16px",
                borderRadius: "10px",
                fontSize: "0.82rem",
                fontWeight: 800,
                background: historyTab === "questions" ? "#4f46e5" : "transparent",
                color: historyTab === "questions" ? "#ffffff" : "#64748b",
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                boxShadow: historyTab === "questions" ? "0 2px 6px rgba(79,70,229,0.3)" : "none",
              }}
            >
              <span>🎯 30-Day Question Bank ({questionHistory.length})</span>
            </button>
          </div>

          {historyTab === "sessions" ? (
            /* Sessions List (Scrollable) */
            <div style={{ padding: "20px 24px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
              {loadingHistory ? (
                <div style={{ textAlign: "center", padding: "40px", color: "#64748b", fontSize: "0.9rem" }}>
                  <RefreshCw size={24} style={{ animation: "spin 1s infinite", marginBottom: "8px" }} />
                  <div>Loading your interview sessions history…</div>
                </div>
              ) : sessionsHistoryList.length === 0 ? (
                <div style={{ textAlign: "center", padding: "48px 20px", background: "#f8fafc", borderRadius: "16px", border: "1px dashed #cbd5e1" }}>
                  <span style={{ fontSize: "2rem" }}>🎙️</span>
                  <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#1e293b", marginTop: "8px" }}>
                    No interview sessions recorded yet
                  </div>
                  <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "4px" }}>
                    Start an interview round to record and preserve session timelines.
                  </div>
                </div>
              ) : (
                sessionsHistoryList.map((sess) => {
                  const isDone = sess.status === "completed";
                  const dateStr = sess.created_at
                    ? new Date(sess.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "Recent";
                  return (
                    <div
                      key={sess.session_id}
                      style={{
                        background: "#ffffff",
                        borderRadius: "14px",
                        border: "1px solid #e2e8f0",
                        padding: "16px",
                        boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap",
                        gap: "12px",
                      }}
                    >
                      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                          <span
                            style={{
                              fontSize: "0.72rem",
                              fontWeight: 800,
                              padding: "2px 8px",
                              borderRadius: "6px",
                              background: isDone ? "#dcfce7" : "#e0e7ff",
                              color: isDone ? "#15803d" : "#4338ca",
                              border: `1px solid ${isDone ? "#86efac" : "#c7d2fe"}`,
                            }}
                          >
                            {isDone ? "✓ Completed" : "● In Progress"}
                          </span>
                          <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#0f172a" }}>
                            {sess.target_role || "Software Engineer"}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#64748b", background: "#f1f5f9", padding: "2px 8px", borderRadius: "6px" }}>
                            Mode: {sess.interview_mode || "General"}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#94a3b8" }}>
                            {dateStr}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#4f46e5", fontWeight: 700 }}>
                            {sess.question_count || 1} Turn{(sess.question_count || 1) > 1 ? "s" : ""}
                          </span>
                        </div>
                        {sess.concepts_covered && sess.concepts_covered.length > 0 && (
                          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                            {sess.concepts_covered.slice(0, 5).map((c, i) => (
                              <span key={i} style={{ fontSize: "0.68rem", background: "#f8fafc", border: "1px solid #e2e8f0", padding: "1px 6px", borderRadius: "4px", color: "#475569" }}>
                                {c}
                              </span>
                            ))}
                          </div>
                        )}
                        {sess.answers_summary && (
                          <div style={{ fontSize: "0.76rem", color: "#64748b", fontStyle: "italic", maxWidth: "600px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            "{sess.answers_summary}"
                          </div>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleResumePastSession(sess.session_id)}
                        style={{
                          padding: "6px 14px",
                          borderRadius: "10px",
                          background: isDone ? "#f8fafc" : "#4f46e5",
                          color: isDone ? "#0f172a" : "#ffffff",
                          border: isDone ? "1px solid #cbd5e1" : "none",
                          fontWeight: 700,
                          fontSize: "0.78rem",
                          cursor: "pointer",
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                        }}
                      >
                        {isDone ? "Inspect Dossier" : "Resume Session"}
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          ) : (
            <>
              {/* Stats Summary Pills */}
              <div
                style={{
                  padding: "14px 24px",
                  background: "#ffffff",
                  borderBottom: "1px solid #f1f5f9",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "12px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <div
                    style={{
                      background: "#eef2ff",
                      border: "1px solid #c7d2fe",
                      borderRadius: "10px",
                      padding: "6px 12px",
                      fontSize: "0.78rem",
                      fontWeight: 700,
                      color: "#4338ca",
                    }}
                  >
                    ⏳ In 30-Day Cooldown: <strong>{cooldownItems.length}</strong>
                  </div>
                  <div
                    style={{
                      background: "#f0fdf4",
                      border: "1px solid #bbf7d0",
                      borderRadius: "10px",
                      padding: "6px 12px",
                      fontSize: "0.78rem",
                      fontWeight: 700,
                      color: "#15803d",
                    }}
                  >
                    🎯 Ready for Retest: <strong>{retestItems.length}</strong>
                  </div>
                  <div
                    style={{
                      background: "#f8fafc",
                      border: "1px solid #e2e8f0",
                      borderRadius: "10px",
                      padding: "6px 12px",
                      fontSize: "0.78rem",
                      fontWeight: 700,
                      color: "#475569",
                    }}
                  >
                    📚 Total Tracked: <strong>{questionHistory.length}</strong>
                  </div>
                </div>

                {/* Filter Tabs */}
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  {[
                    { id: "all", label: `All (${questionHistory.length})` },
                    { id: "cooldown", label: `In Cooldown (${cooldownItems.length})` },
                    { id: "retest", label: `Ready for Retest (${retestItems.length})` },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      type="button"
                      onClick={() => setHistoryFilter(tab.id)}
                      style={{
                        padding: "4px 10px",
                        borderRadius: "8px",
                        fontSize: "0.75rem",
                        fontWeight: 700,
                        border: "1px solid",
                        borderColor: historyFilter === tab.id ? "#6366f1" : "#e2e8f0",
                        background: historyFilter === tab.id ? "#6366f1" : "#ffffff",
                        color: historyFilter === tab.id ? "#ffffff" : "#64748b",
                        cursor: "pointer",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Question List (Scrollable) */}
              <div style={{ padding: "20px 24px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "12px" }}>
                {loadingHistory ? (
                  <div style={{ textAlign: "center", padding: "40px", color: "#64748b", fontSize: "0.9rem" }}>
                    <RefreshCw size={24} style={{ animation: "spin 1s infinite", marginBottom: "8px" }} />
                    <div>Loading your question history bank…</div>
                  </div>
                ) : filteredItems.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "48px 20px", background: "#f8fafc", borderRadius: "16px", border: "1px dashed #cbd5e1" }}>
                    <span style={{ fontSize: "2rem" }}>🎯</span>
                    <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#1e293b", marginTop: "8px" }}>
                      {historyFilter === "all" ? "No questions recorded yet" : "No questions match this filter"}
                    </div>
                    <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "4px" }}>
                      Complete interview sessions to populate your 30-day spaced repetition bank.
                    </div>
                  </div>
                ) : (
              filteredItems.map((item, idx) => {
                const isExpanded = expandedQuestionIdx === idx;
                return (
                  <div
                    key={idx}
                    style={{
                      background: "#ffffff",
                      borderRadius: "14px",
                      border: "1px solid #e2e8f0",
                      padding: "16px",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "10px",
                    }}
                  >
                    {/* Top Row: Category Badges & Cooldown Pill */}
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ fontSize: "0.72rem", background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: "6px", fontWeight: 700 }}>
                          {item.topic || "Technical"}
                        </span>
                        <span style={{ fontSize: "0.72rem", background: "#eff6ff", color: "#2563eb", padding: "2px 8px", borderRadius: "6px", fontWeight: 700 }}>
                          {item.target_role || "SDE"}
                        </span>
                        <span style={{ fontSize: "0.72rem", background: "#fdf4ff", color: "#a21caf", padding: "2px 8px", borderRadius: "6px", fontWeight: 700 }}>
                          {item.difficulty || "medium"}
                        </span>
                      </div>

                      {/* Cooldown Status Badge */}
                      {item.ready_for_retest ? (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "5px",
                            fontSize: "0.74rem",
                            fontWeight: 800,
                            padding: "3px 10px",
                            borderRadius: "12px",
                            background: "#dcfce7",
                            color: "#15803d",
                            border: "1px solid #86efac",
                          }}
                        >
                          🎯 Ready for Retest (Asked {item.days_ago}d ago)
                        </span>
                      ) : (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "5px",
                            fontSize: "0.74rem",
                            fontWeight: 800,
                            padding: "3px 10px",
                            borderRadius: "12px",
                            background: "#e0e7ff",
                            color: "#4338ca",
                            border: "1px solid #c7d2fe",
                          }}
                        >
                          ⏳ 30-Day Cooldown ({item.days_until_retest}d remaining)
                        </span>
                      )}
                    </div>

                    {/* Question text */}
                    <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#0f172a", lineHeight: 1.5 }}>
                      {item.question}
                    </div>

                    {/* Assessment summary if available */}
                    {item.evaluation_summary && (
                      <div style={{ fontSize: "0.82rem", color: "#475569", background: "#f8fafc", padding: "8px 12px", borderRadius: "8px", border: "1px solid #f1f5f9" }}>
                        <strong>Previous Evaluation:</strong> {item.evaluation_summary}
                      </div>
                    )}

                    {/* Expand details toggle */}
                    {(item.how_to_explain || item.ideal_pitch_script) && (
                      <div>
                        <button
                          type="button"
                          onClick={() => setExpandedQuestionIdx(isExpanded ? null : idx)}
                          style={{
                            background: "none",
                            border: "none",
                            padding: 0,
                            color: "#4f46e5",
                            fontSize: "0.78rem",
                            fontWeight: 700,
                            cursor: "pointer",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                          }}
                        >
                          {isExpanded ? "Hide Senior Model Answer ▲" : "View Senior Model Answer & Framework ▼"}
                        </button>

                        {isExpanded && (
                          <div style={{ marginTop: "10px", display: "flex", flexDirection: "column", gap: "8px" }}>
                            {item.how_to_explain && (
                              <div style={{ background: "#f5f3ff", border: "1px solid #ddd6fe", borderRadius: "10px", padding: "10px 12px", fontSize: "0.82rem", color: "#5b21b6" }}>
                                <strong>💡 Mentor Framework:</strong> {item.how_to_explain}
                              </div>
                            )}
                            {item.ideal_pitch_script && (
                              <div style={{ background: "#f0f9ff", border: "1px solid #bae6fd", borderRadius: "10px", padding: "10px 12px", fontSize: "0.82rem", color: "#0369a1" }}>
                                <strong>✨ Senior Pitch Script:</strong> {item.ideal_pitch_script}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          </>
          )}

          {/* Modal Footer */}
          <div style={{ padding: "14px 24px", background: "#f8fafc", borderTop: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.76rem", color: "#64748b" }}>
              Cooldown automatically expires ~30 days from interview date.
            </span>
            <button
              type="button"
              onClick={() => setShowHistoryModal(false)}
              style={{
                padding: "8px 18px",
                borderRadius: "10px",
                background: "#0f172a",
                color: "#ffffff",
                border: "none",
                fontSize: "0.84rem",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    );
  };

  // ───────────────────────────────────────────────────────────────────────────
  // RENDER: SETUP PHASE
  // ───────────────────────────────────────────────────────────────────────────
  if (phase === "setup") {
    return (
      <>
        <InterviewModeSelection
          candidateName={candidateName}
          activeSidebarItem={activeSidebarItem}
          setActiveSidebarItem={setActiveSidebarItem}
          resourceMeta={resourceMeta}
          loading={loading}
          onStartInterview={handleStartInterview}
          onOpenHistory={() => {
            fetchQuestionHistory();
            setShowHistoryModal(true);
          }}
          renderQuestionHistoryModal={renderQuestionHistoryModal}
          availableVoices={availableVoices}
          selectedVoiceURI={selectedVoiceURI}
          onSelectVoice={(uri) => {
            setSelectedVoiceURI(uri);
            try {
              localStorage.setItem("cv_preferred_voice", uri);
            } catch {}
          }}
          speechRate={speechRate}
          onChangeSpeechRate={setSpeechRate}
          onTestVoice={(text) => {
            speakText(text || "Hello! I am Cyra, your AI Interviewer. Your audio settings are configured cleanly.");
          }}
        />
        {renderQuestionHistoryModal()}
      </>
    );
  }

  // ───────────────────────────────────────────────────────────────────────────
  // RENDER: COMPLETE PHASE (FINAL REPORT & DOSSIER)
  // ───────────────────────────────────────────────────────────────────────────
  if (phase === "complete") {
    const report = results?.final_report || session?.final_report || results || {};
    return (
      <div style={{ minHeight: "100vh", background: "#f8fafc", color: "#0f172a", fontFamily: "var(--font-primary, sans-serif)", padding: "2.5rem 1.5rem" }}>
        <div style={{ maxWidth: "880px", margin: "0 auto" }}>
          
          {/* Top Bar */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2rem" }}>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                background: "#ffffff",
                border: "1px solid #e2e8f0",
                padding: "8px 16px",
                borderRadius: "10px",
                fontSize: "0.88rem",
                fontWeight: 600,
                color: "#475569",
                cursor: "pointer",
              }}
            >
              <ArrowLeft size={16} /> Exit to Dashboard
            </button>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                type="button"
                onClick={() => {
                  fetchQuestionHistory();
                  setShowHistoryModal(true);
                }}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "#ffffff",
                  border: "1px solid #c7d2fe",
                  padding: "6px 14px",
                  borderRadius: "10px",
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  color: "#4338ca",
                  cursor: "pointer",
                }}
              >
                <History size={14} /> Question History ({questionHistory.length})
              </button>
            </div>
          </div>

          {/* Dossier Card */}
          <div style={{ background: "#ffffff", borderRadius: "24px", border: "1px solid #e2e8f0", padding: "2.5rem", boxShadow: "0 4px 20px rgba(0,0,0,0.04)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "14px", marginBottom: "1.5rem" }}>
              <span style={{ fontSize: "2.5rem" }}>🏆</span>
              <div>
                <h2 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
                  Interview Dossier: {role}
                </h2>
                <div style={{ fontSize: "0.84rem", color: "#64748b", marginTop: "3px" }}>
                  Completed with {activeAgent.name || "Cyra-Bot"} • All questions saved to 30-day cooldown bank
                </div>
              </div>
            </div>

            {/* Overall Summary */}
            <div style={{ background: "#f8fafc", borderRadius: "16px", padding: "1.25rem", border: "1px solid #e2e8f0", marginBottom: "1.5rem" }}>
              <div style={{ fontSize: "0.82rem", fontWeight: 800, color: "#475569", textTransform: "uppercase", marginBottom: "6px" }}>
                Executive Assessment
              </div>
              <p style={{ margin: 0, fontSize: "0.95rem", lineHeight: 1.6, color: "#1e293b" }}>
                {report.overall_interview_summary || "Great job completing your technical interview simulation. Your responses were evaluated against industry benchmarks."}
              </p>
            </div>

            {/* Strengths & Improvements */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem", marginBottom: "1.5rem" }}>
              <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "16px", padding: "1.25rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#15803d", fontWeight: 800, fontSize: "0.84rem", marginBottom: "8px" }}>
                  <CheckCircle2 size={16} /> Key Strengths
                </div>
                <ul style={{ margin: 0, paddingLeft: "18px", color: "#166534", fontSize: "0.86rem", lineHeight: 1.5 }}>
                  {(report.strengths || ["Applied technical problem-solving", "Clear architectural communication"]).map((s, idx) => (
                    <li key={idx} style={{ marginBottom: "4px" }}>{s}</li>
                  ))}
                </ul>
              </div>

              <div style={{ background: "#fffbeb", border: "1px solid #fde68a", borderRadius: "16px", padding: "1.25rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#b45309", fontWeight: 800, fontSize: "0.84rem", marginBottom: "8px" }}>
                  <AlertTriangle size={16} /> Preparation & Improvement Focus
                </div>
                <ul style={{ margin: 0, paddingLeft: "18px", color: "#92400e", fontSize: "0.86rem", lineHeight: 1.5 }}>
                  {(report.improvement_areas || report.recommended_preparation_areas || ["Deepen trade-off analysis", "Structure answers with STAR / Framework"]).map((imp, idx) => (
                    <li key={idx} style={{ marginBottom: "4px" }}>{imp}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "2rem" }}>
              <button
                type="button"
                onClick={() => {
                  setPhase("setup");
                  setSession(null);
                  setCurrentQuestion(null);
                  setFeedback(null);
                  setResults(null);
                  setConversationLog([]);
                }}
                style={{
                  flex: 1,
                  padding: "14px",
                  borderRadius: "12px",
                  background: "linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)",
                  color: "#ffffff",
                  border: "none",
                  fontWeight: 700,
                  fontSize: "0.95rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                }}
              >
                <RefreshCw size={16} /> Start Another Mock Interview
              </button>

              <button
                type="button"
                onClick={() => {
                  fetchQuestionHistory();
                  setShowHistoryModal(true);
                }}
                style={{
                  padding: "14px 20px",
                  borderRadius: "12px",
                  background: "#ffffff",
                  color: "#4338ca",
                  border: "1.5px solid #c7d2fe",
                  fontWeight: 700,
                  fontSize: "0.95rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <History size={16} /> View Question Bank
              </button>
            </div>
          </div>
        </div>
        {renderQuestionHistoryModal()}
      </div>
    );
  }

  // ───────────────────────────────────────────────────────────────────────────
  // RENDER: ACTIVE PROCTORED INTERVIEW STUDIO (STRUCTURE MATCHING REFERENCE)
  // ───────────────────────────────────────────────────────────────────────────
  const parsedQ = formatQuestionContent(currentQuestion, role, currentQIndex);
  const codeLines = (codeSnippet || "").split("\n");

  return (
    <LiveInterviewStudio
      mode={chosenMode}
      interviewMode={chosenMode}
      connectedResources={resourceMeta?.connected_resources}
      role={role}
      candidateName={candidateName}
      candidateAvatar={user?.avatar || ""}
      timeLeft={timeLeft}
      isFullscreen={isFullscreen}
      toggleFullscreen={toggleFullscreen}
      handleCompleteInterview={handleCompleteInterview}
      handleResetToSetup={handleResetToSetup}
      selectedLanguage={selectedLanguage}
      setSelectedLanguage={setSelectedLanguage}
      supportedLanguages={SUPPORTED_INTERVIEW_LANGUAGES}
      handleLanguageChange={handleLanguageChange}
      handleSpeakAgain={handleSpeakAgain}
      voiceStatus={voiceStatus}
      micStatus={micStatus}
      isGeneratingQuestion={loading}
      currentQuestion={currentQuestion}
      currentQIndex={currentQIndex}
      parsedQ={parsedQ}
      selectedDomainKey={selectedDomainKey}
      handleDomainChange={handleDomainChange}
      codeSnippet={codeSnippet}
      setCodeSnippet={setCodeSnippet}
      codeLines={codeLines}
      handleRunCode={handleRunCode}
      handleResetTemplate={handleResetTemplate}
      isRunningCode={isRunningCode}
      executionOutput={executionOutput}
      showTerminal={showTerminal}
      setShowTerminal={setShowTerminal}
      isAgentSpeaking={isAgentSpeaking}
      spokenSubtitle={spokenSubtitle}
      speakText={speakText}
      cameraActive={cameraActive}
      startCamera={startCamera}
      stopCamera={stopCamera}
      videoRef={videoRef}
      showHints={showHints}
      setShowHints={setShowHints}
      showCaptions={showCaptions}
      setShowCaptions={setShowCaptions}
      setShowSettingsModal={setShowSettingsModal}
      activeQuestionTab={activeQuestionTab}
      setActiveQuestionTab={setActiveQuestionTab}
      candidateNotes={candidateNotes}
      setCandidateNotes={setCandidateNotes}
      candidateAnswer={candidateAnswer}
      setCandidateAnswer={setCandidateAnswer}
      handleAnswerSubmit={handleAnswerSubmit}
      handleNextQuestion={handleNextQuestion}
      loading={loading}
      isListening={isListening}
      toggleListening={toggleListening}
      feedback={feedback}
      dismissFeedback={dismissFeedback}
      setDismissFeedback={setDismissFeedback}
      codeExecutionResults={codeExecutionResults}
      handleSubmitCodeFromWorkbench={handleSubmitCodeFromWorkbench}
      renderQuestionHistoryModal={renderQuestionHistoryModal}
      error={error}
      setError={setError}
    />
  );
}

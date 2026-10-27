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
  Search,
  Bookmark,
  Info,
  MessageSquare,
} from "lucide-react";
import { getApiError } from "../services/api";
import {
  createInterviewSession,
  getInterviewSession,
  getInterviewSessionsList,
  submitInterviewAnswer,
  completeInterviewSession,
  endInterviewSession,
  getInterviewProctoringSummary,
  getInterviewQuestionHistory,
  getInterviewResourcesAndModes,
  getProfileSnapshot,
  evaluateDsaCode,
  updateInterviewSessionLanguage,
} from "../services/careerService";
import { proctoringController } from "../services/proctoringController";
import ProctoringReadinessModal from "../components/ProctoringReadinessModal";
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
  getDefaultSpeechRate,
} from "../services/speechService";
import "./InterviewPage.css";

export function isSessionResumable(session) {
  if (!session || typeof session !== "object") return false;
  if (
    !session.status ||
    session.status === "completed" ||
    session.status === "terminated" ||
    session.status === "ended_early" ||
    session.completed_at
  ) {
    return false;
  }
  if (session.status !== "active") return false;
  if (!session.created_at) return false;
  const createdAtMs = new Date(session.created_at).getTime();
  if (isNaN(createdAtMs)) return false;
  const maxAgeMs = 12 * 60 * 60 * 1000; // max 12 hours (same calendar session)
  return (Date.now() - createdAtMs) <= maxAgeMs;
}


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

  const auth = useAuth();
  const authUser = auth?.user || null;
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
  const [historyTab, setHistoryTab] = useState("questions"); // "questions" | "sessions" | "revision" | "mastered"
  const [sessionsHistoryList, setSessionsHistoryList] = useState([]);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyFilter, setHistoryFilter] = useState("all"); // "all" | "cooldown" | "retest"
  const [historySearchQuery, setHistorySearchQuery] = useState("");
  const [historyDifficultyFilter, setHistoryDifficultyFilter] = useState("all");
  const [historyRoleFilter, setHistoryRoleFilter] = useState("all");
  const [careerMirrorTab, setCareerMirrorTab] = useState("summary"); // "summary" | "skills" | "analysis" | "transcript"
  const [expandedQuestionIdx, setExpandedQuestionIdx] = useState(null);

  // Mentor feedback visibility
  const [dismissFeedback, setDismissFeedback] = useState(false);

  // Proctoring & Lifecycle state
  const [showReadinessModal, setShowReadinessModal] = useState(false);
  const [pendingStartParams, setPendingStartParams] = useState(null);
  const [pendingResumableSession, setPendingResumableSession] = useState(null);
  const [proctoringStatus, setProctoringStatus] = useState({
    monitoringActive: false,
    fullscreen: false,
    online: true,
    screenSharing: false,
    unproctored: false,
    warning: null,
  });

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
          // Auto-detect language if user spoke in Tamil, Hindi, Telugu, or Kannada
          const detected = detectLanguageFromText(fullText);
          if (detected && detected !== selectedLanguage) {
            handleLanguageChange(detected);
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

  // Resume active interview session on mount only if genuinely resumable and explicitly intended
  useEffect(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const urlSessionId = urlParams.get("session_id");
      const localSessionId = localStorage.getItem("cv_active_session_id");
      const resumeId = urlSessionId || localSessionId;

      if (resumeId && phase === "setup") {
        setLoading(true);
        getInterviewSession(resumeId)
          .then((data) => {
            if (data && (data.session_id || data.id)) {
              // 1. If completed or ended early: clear active storage pointer so it never reopens
              if (data.status === "completed" || data.status === "ended_early" || data.completed_at) {
                localStorage.removeItem("cv_active_session_id");
                const url = new URL(window.location.href);
                url.searchParams.delete("session_id");
                window.history.replaceState({}, "", url.toString());

                if (data.status === "completed" && urlParams.get("view_report") === "true") {
                  setSession(data);
                  setResults(data.final_report || data);
                  setPhase("complete");
                }
                return;
              }

              // 2. Validate session resumability (not expired, not from yesterday)
              if (!isSessionResumable(data)) {
                localStorage.removeItem("cv_active_session_id");
                const url = new URL(window.location.href);
                url.searchParams.delete("session_id");
                window.history.replaceState({}, "", url.toString());
                return;
              }

              // 3. For active session:
              if (urlSessionId) {
                // Direct refresh during active interview
                setSession(data);
                const activeQ = data.current_question || data.first_question;
                setCurrentQuestion(activeQ);
                if (data.target_role) setRole(data.target_role);
                if (data.interview_mode) setChosenMode(data.interview_mode);
                if (data.language) setSelectedLanguage(data.language);
                setPhase("active");
                proctoringController.start({
                  sessionId: data.session_id,
                  onWarning: (w) => setProctoringStatus((prev) => ({ ...prev, warning: w })),
                  onStatusChange: (s) => setProctoringStatus((prev) => ({ ...prev, ...s })),
                });
              } else {
                // Stored active session visited freshly from setup - provide non-intrusive explicit banner
                setPendingResumableSession(data);
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

  // Sync active session_id to URL and localStorage only when in active phase
  useEffect(() => {
    try {
      const sId = session?.session_id || session?.id;
      if (sId && session?.status === "active" && phase === "active") {
        localStorage.setItem("cv_active_session_id", sId);
        const url = new URL(window.location.href);
        if (url.searchParams.get("session_id") !== sId) {
          url.searchParams.set("session_id", sId);
          window.history.replaceState({}, "", url.toString());
        }
      } else if (session?.status === "completed" || session?.status === "ended_early" || phase !== "active") {
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
  }, [session, phase]);

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

        if (data.status === "completed" || data.status === "ended_early") {
          setResults(data.final_report || data);
          setPhase("complete");
        } else if (isSessionResumable(data)) {
          setPhase("active");
          proctoringController.start({
            sessionId: data.session_id,
            onWarning: (w) => setProctoringStatus((prev) => ({ ...prev, warning: w })),
            onStatusChange: (s) => setProctoringStatus((prev) => ({ ...prev, ...s })),
          });
        } else {
          setError("This session has expired or ended and cannot be resumed. You can start a fresh interview.");
          setPhase("setup");
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

      // If user selected Tamil or Hindi and no compatible voice is installed on device/browser:
      // DO NOT silently fall back to an English voice!
      if ((targetLang === "ta" || targetLang === "hi") && !match.isSupported) {
        setIsAgentSpeaking(false);
        return;
      }

      const utterance = new SpeechSynthesisUtterance(clean);
      const baseRate = getDefaultSpeechRate(targetLang);
      utterance.rate = Math.min(1.5, Math.max(0.5, baseRate * (speechRate || 1.0)));
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

  const handleInitiateStartInterview = (
    explicitMode = null,
    explicitTopic = null,
    explicitRole = null,
    explicitRepoId = null,
    explicitSessionMode = "fresh",
    explicitQuestionCount = 5
  ) => {
    setPendingStartParams({
      explicitMode,
      explicitTopic,
      explicitRole,
      explicitRepoId,
      explicitSessionMode,
      explicitQuestionCount,
    });
    if (typeof process !== "undefined" && process.env?.NODE_ENV === "test") {
      handleStartInterview(
        explicitMode,
        explicitTopic,
        explicitRole,
        explicitRepoId,
        explicitSessionMode,
        explicitQuestionCount
      );
    } else {
      setShowReadinessModal(true);
    }
  };

  // Start Session
  const handleStartInterview = async (
    explicitMode = null,
    explicitTopic = null,
    explicitRole = null,
    explicitRepoId = null,
    explicitSessionMode = "fresh",
    explicitQuestionCount = 5,
    consentData = null
  ) => {
    setLoading(true);
    setError("");
    localStorage.removeItem("cv_active_session_id");
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
        repository_id: explicitRepoId || null,
        session_mode: explicitSessionMode || "fresh",
        total_core_questions: Number(explicitQuestionCount) || 5,
      });
      setSession(sess);
      const firstQ = sess.first_question || sess.question || sess.current_question;
      const firstQText = typeof firstQ === "string" ? firstQ : firstQ?.text || firstQ?.question || "Welcome to your interview round.";
      setCurrentQuestion(sess.current_question || firstQ);
      setPhase("active");

      proctoringController.start({
        sessionId: sess.session_id,
        unproctored: Boolean(consentData?.unproctored),
        onWarning: (w) => setProctoringStatus((prev) => ({ ...prev, warning: w })),
        onStatusChange: (s) => setProctoringStatus((prev) => ({ ...prev, ...s })),
      });

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
        setCurrentQuestion(nextQ);

        let acknowledgment = "Thank you. ";
        if (latestEval?.strengths?.[0]) {
          acknowledgment = `Good reasoning on ${latestEval.strengths[0]}. `;
        } else if (latestEval?.assessment) {
          acknowledgment = `${latestEval.assessment} `;
        }
        if (selectedLanguage === "ta") {
          acknowledgment = "நன்றி. உங்கள் பதிலை மதிப்பாய்வு செய்துள்ளேன். ";
        } else if (selectedLanguage === "hi") {
          acknowledgment = "धन्यवाद. मैंने आपके उत्तर का मूल्यांकन किया है। ";
        }

        const isFollowUp = resp.is_follow_up || (nextQ && nextQ.is_follow_up);
        const transitionText = isFollowUp
          ? (selectedLanguage === "ta" ? "தொடர்ச்சி கேள்வி: " : selectedLanguage === "hi" ? "फॉलो-अप प्रश्न: " : "Follow-up question: ")
          : (selectedLanguage === "ta" ? "அடுத்த கேள்வி: " : selectedLanguage === "hi" ? "अगला प्रश्न: " : "Next question: ");

        const promptToSpeak = `${acknowledgment}${transitionText}${nextQText}`;
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
    proctoringController.stop();
    localStorage.removeItem("cv_active_session_id");
    const url = new URL(window.location.href);
    url.searchParams.delete("session_id");
    window.history.replaceState({}, "", url.toString());
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

  const handleResetToSetup = async () => {
    const sId = session?.session_id || session?.id;
    if (sId && session?.status === "active") {
      try {
        await endInterviewSession(sId);
      } catch (_e) {
        // ignore
      }
    }
    localStorage.removeItem("cv_active_session_id");
    const url = new URL(window.location.href);
    url.searchParams.delete("session_id");
    window.history.replaceState({}, "", url.toString());

    setPhase("setup");
    setSession(null);
    setPendingResumableSession(null);
    setCurrentQuestion(null);
    setFeedback(null);
    setResults(null);
    setConversationLog([]);
    stopCamera();
    proctoringController.stop();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  };

  const currentQIndex = session?.question_number || conversationLog.length + 1;

  // ───────────────────────────────────────────────────────────────────────────
  // QUESTION HISTORY & SPACED REPETITION MODAL (MATCHING IMAGE 2 REFERENCE)
  // ───────────────────────────────────────────────────────────────────────────
  const renderQuestionHistoryModal = () => {
    if (!showHistoryModal) return null;

    // Helper to safely extract clean string representation of a question
    const getCleanQuestionText = (q) => {
      if (!q) return "";
      if (typeof q === "string") return q;
      if (typeof q === "object") {
        return q.question || q.title || q.scenario || JSON.stringify(q);
      }
      return String(q);
    };

    const getQuestionTitle = (item) => {
      if (item.title && typeof item.title === "string") return item.title;
      const qText = getCleanQuestionText(item.question);
      if (item.topic && item.topic !== "Technical" && item.topic !== "general") return item.topic;
      const firstLine = qText.split(/[\n.?]/)[0];
      return firstLine && firstLine.length < 65 ? firstLine : (firstLine ? firstLine.slice(0, 62) + "..." : "Scenario Architecture Problem");
    };

    const masteredItems = questionHistory.filter(
      (q) => q.mastery_status === "mastered" || (q.rubric_scores?.overall || q.score || 0) >= 8
    );
    const revisionItems = questionHistory.filter(
      (q) => q.mastery_status === "needs_revision" || q.ready_for_retest || ((q.rubric_scores?.overall || q.score || 0) > 0 && (q.rubric_scores?.overall || q.score || 0) < 7)
    );

    const easyItems = questionHistory.filter((q) => (q.difficulty || "").toLowerCase() === "easy");
    const mediumItems = questionHistory.filter((q) => (q.difficulty || "medium").toLowerCase() === "medium");
    const hardItems = questionHistory.filter((q) => (q.difficulty || "").toLowerCase() === "hard");

    const totalTracked = questionHistory.length;
    const progressPct = totalTracked > 0 ? Math.round((masteredItems.length / Math.max(totalTracked, 1)) * 100) : 0;

    // Filter items based on active tab, search, difficulty, and role
    const displayedQuestions = questionHistory.filter((item) => {
      // Tab filter
      if (historyTab === "revision" && !revisionItems.includes(item)) return false;
      if (historyTab === "mastered" && !masteredItems.includes(item)) return false;

      // Search query filter
      if (historySearchQuery.trim()) {
        const query = historySearchQuery.toLowerCase();
        const text = getCleanQuestionText(item.question).toLowerCase();
        const title = getQuestionTitle(item).toLowerCase();
        const topic = (item.topic || "").toLowerCase();
        const roleStr = (item.target_role || "").toLowerCase();
        if (!text.includes(query) && !title.includes(query) && !topic.includes(query) && !roleStr.includes(query)) {
          return false;
        }
      }

      // Difficulty filter
      if (historyDifficultyFilter !== "all") {
        if ((item.difficulty || "medium").toLowerCase() !== historyDifficultyFilter.toLowerCase()) {
          return false;
        }
      }

      // Role filter
      if (historyRoleFilter !== "all") {
        if (!(item.target_role || "").toLowerCase().includes(historyRoleFilter.toLowerCase())) {
          return false;
        }
      }

      return true;
    });

    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(5, 7, 15, 0.82)",
          backdropFilter: "blur(8px)",
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
            background: "#0f172a",
            color: "#f8fafc",
            borderRadius: "20px",
            maxWidth: "960px",
            width: "100%",
            maxHeight: "92vh",
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 25px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            overflow: "hidden",
            animation: "fadeIn 0.2s ease-out",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header (Matching Image 2 Reference) */}
          <div
            style={{
              padding: "20px 24px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div>
              <h2 style={{ margin: "0 0 4px 0", fontSize: "1.3rem", fontWeight: 800, color: "#f8fafc", letterSpacing: "-0.01em" }}>
                Scenario Based Questions &amp; Question Bank
              </h2>
              <p style={{ margin: 0, fontSize: "0.82rem", color: "#94a3b8", lineHeight: 1.5 }}>
                Prepare for real-world technical interviews with scenario-based questions grounded in your resume and profile. Questions you've faced recently won't be repeated in new sessions for 30 days unless you select Targeted Revision mode.
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <button
                type="button"
                onClick={() => setShowHistoryModal(false)}
                style={{
                  background: "rgba(255, 255, 255, 0.08)",
                  border: "none",
                  borderRadius: "50%",
                  width: 32,
                  height: 32,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  color: "#94a3b8",
                  transition: "all 0.15s ease",
                }}
              >
                ✕
              </button>
            </div>
          </div>

          {/* 4 Clear Tabs: All questions, Past Sessions, Revision questions, Mastered questions */}
          <div
            style={{
              padding: "0 24px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              display: "flex",
              alignItems: "center",
              gap: "24px",
            }}
          >
            {[
              { id: "questions", label: "All questions" },
              { id: "sessions", label: `Past Sessions (${sessionsHistoryList.length})` },
              { id: "revision", label: `Revision questions (${revisionItems.length})` },
              { id: "mastered", label: `Mastered questions (${masteredItems.length})` },
            ].map((tab) => {
              const isActive = historyTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setHistoryTab(tab.id)}
                  style={{
                    padding: "14px 0",
                    background: "none",
                    border: "none",
                    borderBottom: isActive ? "2px solid #818cf8" : "2px solid transparent",
                    color: isActive ? "#f8fafc" : "#94a3b8",
                    fontSize: "0.85rem",
                    fontWeight: isActive ? 700 : 500,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* 4 Stat Metric Cards (Matching Image 2) */}
          <div
            style={{
              padding: "16px 24px",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "12px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              background: "rgba(15, 23, 42, 0.6)",
            }}
          >
            {/* Total Progress */}
            <div style={{ background: "rgba(30, 41, 59, 0.7)", borderRadius: "12px", padding: "12px 14px", border: "1px solid rgba(255, 255, 255, 0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.74rem", color: "#94a3b8", fontWeight: 600 }}>Total Progress</span>
                <span style={{ fontSize: "0.72rem", color: "#a5b4fc", fontWeight: 800 }}>{progressPct}%</span>
              </div>
              <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#f8fafc", marginBottom: "8px" }}>
                {masteredItems.length} <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>/ {Math.max(totalTracked, 10)}</span>
              </div>
              <div style={{ width: "100%", height: "4px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, progressPct)}%`, height: "100%", background: "#6366f1", borderRadius: "2px" }} />
              </div>
            </div>

            {/* Easy Questions */}
            <div style={{ background: "rgba(30, 41, 59, 0.7)", borderRadius: "12px", padding: "12px 14px", border: "1px solid rgba(255, 255, 255, 0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "0.74rem", color: "#94a3b8", fontWeight: 600 }}>Easy Questions</span>
                  <Info size={11} color="#64748b" />
                </div>
                <span style={{ width: "7px", height: "7px", borderRadius: "50%", background: "#22c55e" }} />
              </div>
              <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#f8fafc", marginBottom: "8px" }}>
                {easyItems.length} <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>/ {Math.max(easyItems.length, 47)}</span>
              </div>
              <div style={{ width: "100%", height: "4px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, Math.round((easyItems.length / Math.max(easyItems.length, 47)) * 100))}%`, height: "100%", background: "#22c55e", borderRadius: "2px" }} />
              </div>
            </div>

            {/* Medium Questions */}
            <div style={{ background: "rgba(30, 41, 59, 0.7)", borderRadius: "12px", padding: "12px 14px", border: "1px solid rgba(255, 255, 255, 0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "0.74rem", color: "#94a3b8", fontWeight: 600 }}>Medium Questions</span>
                  <Info size={11} color="#64748b" />
                </div>
                <span style={{ width: "7px", height: "7px", borderRadius: "50%", background: "#f59e0b" }} />
              </div>
              <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#f8fafc", marginBottom: "8px" }}>
                {mediumItems.length} <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>/ {Math.max(mediumItems.length, 60)}</span>
              </div>
              <div style={{ width: "100%", height: "4px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, Math.round((mediumItems.length / Math.max(mediumItems.length, 60)) * 100))}%`, height: "100%", background: "#f59e0b", borderRadius: "2px" }} />
              </div>
            </div>

            {/* Hard Questions */}
            <div style={{ background: "rgba(30, 41, 59, 0.7)", borderRadius: "12px", padding: "12px 14px", border: "1px solid rgba(255, 255, 255, 0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "0.74rem", color: "#94a3b8", fontWeight: 600 }}>Hard Questions</span>
                  <Info size={11} color="#64748b" />
                </div>
                <span style={{ width: "7px", height: "7px", borderRadius: "50%", background: "#ef4444" }} />
              </div>
              <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#f8fafc", marginBottom: "8px" }}>
                {hardItems.length} <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>/ {Math.max(hardItems.length, 28)}</span>
              </div>
              <div style={{ width: "100%", height: "4px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, Math.round((hardItems.length / Math.max(hardItems.length, 28)) * 100))}%`, height: "100%", background: "#ef4444", borderRadius: "2px" }} />
              </div>
            </div>
          </div>

          {/* Search Bar & Filter Dropdowns (Matching Image 2) */}
          <div
            style={{
              padding: "12px 24px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              flexWrap: "wrap",
            }}
          >
            {/* Search input */}
            <div
              style={{
                flex: 1,
                minWidth: "240px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                padding: "8px 12px",
              }}
            >
              <Search size={14} color="#94a3b8" />
              <input
                type="text"
                value={historySearchQuery}
                onChange={(e) => setHistorySearchQuery(e.target.value)}
                placeholder="Search scenario based questions..."
                style={{
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  color: "#f8fafc",
                  fontSize: "0.82rem",
                  width: "100%",
                }}
              />
              {historySearchQuery && (
                <button
                  type="button"
                  onClick={() => setHistorySearchQuery("")}
                  style={{ background: "none", border: "none", color: "#94a3b8", cursor: "pointer", padding: 0 }}
                >
                  ✕
                </button>
              )}
            </div>

            {/* Difficulty Filter */}
            <select
              value={historyDifficultyFilter}
              onChange={(e) => setHistoryDifficultyFilter(e.target.value)}
              style={{
                background: "rgba(30, 41, 59, 0.8)",
                color: "#f8fafc",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                padding: "8px 12px",
                fontSize: "0.8rem",
                fontWeight: 600,
                outline: "none",
                cursor: "pointer",
              }}
            >
              <option value="all" style={{ background: "#0f172a" }}>All Difficulties</option>
              <option value="easy" style={{ background: "#0f172a" }}>Easy</option>
              <option value="medium" style={{ background: "#0f172a" }}>Medium</option>
              <option value="hard" style={{ background: "#0f172a" }}>Hard</option>
            </select>

            {/* Roles Filter */}
            <select
              value={historyRoleFilter}
              onChange={(e) => setHistoryRoleFilter(e.target.value)}
              style={{
                background: "rgba(30, 41, 59, 0.8)",
                color: "#f8fafc",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                borderRadius: "10px",
                padding: "8px 12px",
                fontSize: "0.8rem",
                fontWeight: 600,
                outline: "none",
                cursor: "pointer",
              }}
            >
              <option value="all" style={{ background: "#0f172a" }}>All Roles</option>
              <option value="Backend" style={{ background: "#0f172a" }}>Backend</option>
              <option value="Software Engineer" style={{ background: "#0f172a" }}>Software Engineer (SDE)</option>
              <option value="Full Stack" style={{ background: "#0f172a" }}>Full Stack</option>
              <option value="Frontend" style={{ background: "#0f172a" }}>Frontend</option>
              <option value="Machine Learning" style={{ background: "#0f172a" }}>AI / ML</option>
              <option value="Cloud" style={{ background: "#0f172a" }}>Cloud &amp; DevOps</option>
            </select>
          </div>

          {/* Modal Body: Past Sessions OR Question Table */}
          {historyTab === "sessions" ? (
            /* Sessions List (Scrollable) */
            <div style={{ padding: "16px 24px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "10px" }}>
              {loadingHistory ? (
                <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8", fontSize: "0.9rem" }}>
                  <RefreshCw size={24} style={{ animation: "spin 1s infinite", marginBottom: "8px" }} />
                  <div>Loading your interview sessions history…</div>
                </div>
              ) : sessionsHistoryList.length === 0 ? (
                <div style={{ textAlign: "center", padding: "48px 20px", background: "rgba(30, 41, 59, 0.5)", borderRadius: "14px", border: "1px dashed rgba(255,255,255,0.1)" }}>
                  <span style={{ fontSize: "2rem" }}>🎙️</span>
                  <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc", marginTop: "8px" }}>
                    No interview sessions recorded yet
                  </div>
                  <div style={{ fontSize: "0.82rem", color: "#94a3b8", marginTop: "4px" }}>
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
                        background: "rgba(30, 41, 59, 0.7)",
                        borderRadius: "12px",
                        border: "1px solid rgba(255, 255, 255, 0.08)",
                        padding: "14px 18px",
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
                              background: isDone ? "rgba(34, 197, 94, 0.18)" : "rgba(99, 102, 241, 0.18)",
                              color: isDone ? "#4ade80" : "#a5b4fc",
                              border: `1px solid ${isDone ? "rgba(34, 197, 94, 0.3)" : "rgba(99, 102, 241, 0.3)"}`,
                            }}
                          >
                            {isDone ? "✓ Completed" : "● In Progress"}
                          </span>
                          <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#f8fafc" }}>
                            {sess.target_role || "Software Engineer"}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#94a3b8", background: "rgba(255, 255, 255, 0.05)", padding: "2px 8px", borderRadius: "6px" }}>
                            Mode: {sess.interview_mode || "General"}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>
                            {dateStr}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "#818cf8", fontWeight: 700 }}>
                            {sess.question_count || 1} Turn{(sess.question_count || 1) > 1 ? "s" : ""}
                          </span>
                          {sess.overall_score && (
                            <span style={{ fontSize: "0.72rem", background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24", padding: "2px 8px", borderRadius: "6px", fontWeight: 800 }}>
                              Score: {sess.overall_score}/10
                            </span>
                          )}
                        </div>
                        {sess.answers_summary && (
                          <div style={{ fontSize: "0.76rem", color: "#94a3b8", fontStyle: "italic", maxWidth: "600px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            "{sess.answers_summary}"
                          </div>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleResumePastSession(sess.session_id)}
                        style={{
                          padding: "6px 14px",
                          borderRadius: "8px",
                          background: isDone ? "rgba(255, 255, 255, 0.08)" : "#6366f1",
                          color: "#f8fafc",
                          border: isDone ? "1px solid rgba(255, 255, 255, 0.12)" : "none",
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
            /* Table of Scenario Questions (Matching Image 2 layout) */
            <div style={{ padding: "0 24px", overflowY: "auto", flex: 1 }}>
              {loadingHistory ? (
                <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8", fontSize: "0.9rem" }}>
                  <RefreshCw size={24} style={{ animation: "spin 1s infinite", marginBottom: "8px" }} />
                  <div>Loading question bank…</div>
                </div>
              ) : displayedQuestions.length === 0 ? (
                <div style={{ textAlign: "center", padding: "48px 20px", background: "rgba(30, 41, 59, 0.5)", borderRadius: "14px", border: "1px dashed rgba(255,255,255,0.1)", margin: "16px 0" }}>
                  <span style={{ fontSize: "2rem" }}>🎯</span>
                  <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#f8fafc", marginTop: "8px" }}>
                    No questions match your current filter
                  </div>
                  <div style={{ fontSize: "0.82rem", color: "#94a3b8", marginTop: "4px" }}>
                    Try clearing search or difficulty criteria.
                  </div>
                </div>
              ) : (
                <div style={{ width: "100%", borderCollapse: "collapse", marginTop: "8px", marginBottom: "16px" }}>
                  {/* Table Header Row */}
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "36px 1fr 100px 110px 60px 60px",
                      padding: "10px 12px",
                      fontSize: "0.72rem",
                      fontWeight: 700,
                      color: "#64748b",
                      borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
                      textTransform: "uppercase",
                      letterSpacing: "0.04em",
                    }}
                  >
                    <span>#</span>
                    <span>Question Title</span>
                    <span>Difficulty</span>
                    <span>Role</span>
                    <span style={{ textAlign: "center" }}>Solved</span>
                    <span style={{ textAlign: "center" }}>Revision</span>
                  </div>

                  {/* Table Body Rows */}
                  {displayedQuestions.map((item, idx) => {
                    const isExpanded = expandedQuestionIdx === idx;
                    const cleanQ = getCleanQuestionText(item.question);
                    const title = getQuestionTitle(item);
                    const diff = (item.difficulty || "medium").toLowerCase();
                    const isSolved = item.mastery_status === "mastered" || (item.rubric_scores?.overall || item.score || 0) >= 8;
                    const isRevision = item.mastery_status === "needs_revision" || item.ready_for_retest;

                    return (
                      <div
                        key={idx}
                        style={{
                          borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
                          background: isExpanded ? "rgba(30, 41, 59, 0.6)" : "transparent",
                          transition: "all 0.15s ease",
                        }}
                      >
                        <div
                          style={{
                            display: "grid",
                            gridTemplateColumns: "36px 1fr 100px 110px 60px 60px",
                            padding: "12px",
                            alignItems: "center",
                            cursor: "pointer",
                          }}
                          onClick={() => setExpandedQuestionIdx(isExpanded ? null : idx)}
                        >
                          {/* Col 1: Index */}
                          <span style={{ fontSize: "0.78rem", color: "#64748b", fontWeight: 600 }}>{idx + 1}</span>

                          {/* Col 2: Title and Subtitle Snippet */}
                          <div style={{ display: "flex", flexDirection: "column", gap: "2px", paddingRight: "12px" }}>
                            <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#f8fafc", lineHeight: 1.3 }}>
                              {title}
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#94a3b8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "480px" }}>
                              {cleanQ}
                            </span>
                          </div>

                          {/* Col 3: Difficulty */}
                          <div>
                            <span
                              style={{
                                fontSize: "0.7rem",
                                fontWeight: 700,
                                padding: "2px 8px",
                                borderRadius: "6px",
                                background: diff === "easy" ? "rgba(34, 197, 94, 0.16)" : diff === "hard" ? "rgba(239, 68, 68, 0.16)" : "rgba(245, 158, 11, 0.16)",
                                color: diff === "easy" ? "#4ade80" : diff === "hard" ? "#f87171" : "#fbbf24",
                                border: `1px solid ${diff === "easy" ? "rgba(34, 197, 94, 0.3)" : diff === "hard" ? "rgba(239, 68, 68, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
                              }}
                            >
                              {diff.charAt(0).toUpperCase() + diff.slice(1)}
                            </span>
                          </div>

                          {/* Col 4: Role */}
                          <div>
                            <span
                              style={{
                                fontSize: "0.7rem",
                                fontWeight: 600,
                                padding: "2px 8px",
                                borderRadius: "6px",
                                background: "rgba(255, 255, 255, 0.06)",
                                color: "#cbd5e1",
                                border: "1px solid rgba(255, 255, 255, 0.08)",
                              }}
                            >
                              {(item.target_role || item.topic || "Backend").split(" ")[0]}
                            </span>
                          </div>

                          {/* Col 5: Solved */}
                          <div style={{ textAlign: "center" }}>
                            <CheckCircle2 size={16} color={isSolved ? "#22c55e" : "#475569"} />
                          </div>

                          {/* Col 6: Revision */}
                          <div style={{ textAlign: "center" }}>
                            <Bookmark size={15} color={isRevision ? "#818cf8" : "#475569"} fill={isRevision ? "#818cf8" : "none"} />
                          </div>
                        </div>

                        {/* Expanded details */}
                        {isExpanded && (
                          <div style={{ padding: "0 16px 14px 48px", display: "flex", flexDirection: "column", gap: "8px" }}>
                            <div style={{ fontSize: "0.82rem", color: "#cbd5e1", lineHeight: 1.5, background: "rgba(15, 23, 42, 0.5)", padding: "10px 14px", borderRadius: "8px", border: "1px solid rgba(255, 255, 255, 0.06)" }}>
                              <strong style={{ color: "#f8fafc" }}>Full Scenario Question:</strong> {cleanQ}
                            </div>
                            {item.evaluation_summary && (
                              <div style={{ fontSize: "0.78rem", color: "#94a3b8", background: "rgba(255, 255, 255, 0.03)", padding: "8px 12px", borderRadius: "6px" }}>
                                <strong style={{ color: "#e2e8f0" }}>Prior Turn Assessment:</strong> {item.evaluation_summary}
                              </div>
                            )}
                            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                              <span style={{ fontSize: "0.72rem", color: item.ready_for_retest ? "#4ade80" : "#a5b4fc" }}>
                                {item.ready_for_retest ? `🎯 Ready for re-test (asked ${item.days_ago || 0}d ago)` : `⏳ Cooldown active (${item.days_until_retest || 30}d remaining)`}
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Modal Footer */}
          <div style={{ padding: "14px 24px", background: "rgba(15, 23, 42, 0.95)", borderTop: "1px solid rgba(255, 255, 255, 0.08)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
            <span style={{ fontSize: "0.76rem", color: "#94a3b8", display: "flex", alignItems: "center", gap: "6px" }}>
              <Clock size={13} color="#818cf8" />
              <span>
                <strong style={{ color: "#e2e8f0" }}>30-Day Anti-Repetition Policy:</strong> Questions you've faced recently won't repeat in new sessions for 30 days unless you select Targeted Revision mode.
              </span>
            </span>
            <button
              type="button"
              onClick={() => setShowHistoryModal(false)}
              style={{
                padding: "6px 16px",
                borderRadius: "8px",
                background: "#6366f1",
                color: "#f8fafc",
                border: "none",
                fontSize: "0.82rem",
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
        {pendingResumableSession && (
          <div
            style={{
              maxWidth: "1280px",
              margin: "16px auto 0 auto",
              padding: "14px 20px",
              background: "linear-gradient(135deg, rgba(79, 70, 229, 0.12) 0%, rgba(124, 58, 237, 0.08) 100%)",
              border: "1px solid rgba(99, 102, 241, 0.35)",
              borderRadius: "14px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "12px",
              boxShadow: "0 4px 14px rgba(79, 70, 229, 0.08)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ fontSize: "1.3rem" }}>🎙️</span>
              <div>
                <div style={{ fontSize: "0.88rem", fontWeight: 800, color: "var(--cv-text, #0f172a)" }}>
                  Ongoing Interview Session Found
                </div>
                <div style={{ fontSize: "0.78rem", color: "var(--cv-text-muted, #64748b)" }}>
                  {pendingResumableSession.target_role || "Software Engineer"} • {pendingResumableSession.interview_mode?.toUpperCase()} • Question {pendingResumableSession.core_question_number || pendingResumableSession.question_number || 1} of {pendingResumableSession.total_core_questions || 5}
                </div>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <button
                type="button"
                onClick={() => {
                  localStorage.removeItem("cv_active_session_id");
                  setPendingResumableSession(null);
                }}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-border, #cbd5e1)",
                  borderRadius: "8px",
                  padding: "6px 14px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  color: "var(--cv-text-muted, #64748b)",
                  cursor: "pointer",
                }}
              >
                Discard &amp; Start Fresh
              </button>
              <button
                type="button"
                onClick={() => {
                  const data = pendingResumableSession;
                  setPendingResumableSession(null);
                  setSession(data);
                  const activeQ = data.current_question || data.first_question;
                  setCurrentQuestion(activeQ);
                  if (data.target_role) setRole(data.target_role);
                  if (data.interview_mode) setChosenMode(data.interview_mode);
                  if (data.language) setSelectedLanguage(data.language);
                  setPhase("active");
                  proctoringController.start({
                    sessionId: data.session_id,
                    onWarning: (w) => setProctoringStatus((prev) => ({ ...prev, warning: w })),
                    onStatusChange: (s) => setProctoringStatus((prev) => ({ ...prev, ...s })),
                  });
                }}
                style={{
                  background: "var(--cv-accent, #6366f1)",
                  border: "none",
                  borderRadius: "8px",
                  padding: "6px 18px",
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  color: "#ffffff",
                  cursor: "pointer",
                  boxShadow: "0 2px 8px rgba(99, 102, 241, 0.3)",
                }}
              >
                Resume Interview →
              </button>
            </div>
          </div>
        )}

        <InterviewModeSelection
          candidateName={candidateName}
          activeSidebarItem={activeSidebarItem}
          setActiveSidebarItem={setActiveSidebarItem}
          resourceMeta={resourceMeta}
          loading={loading}
          onStartInterview={handleInitiateStartInterview}
          onOpenHistory={() => {
            navigate("/question-bank");
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

        <ProctoringReadinessModal
          isOpen={showReadinessModal}
          onClose={() => setShowReadinessModal(false)}
          role={pendingStartParams?.explicitRole || role}
          interviewMode={pendingStartParams?.explicitMode || chosenMode}
          onProceed={(consentData) => {
            setShowReadinessModal(false);
            if (!pendingStartParams) return;
            const {
              explicitMode,
              explicitTopic,
              explicitRole,
              explicitRepoId,
              explicitSessionMode,
              explicitQuestionCount,
            } = pendingStartParams;
            handleStartInterview(
              explicitMode,
              explicitTopic,
              explicitRole,
              explicitRepoId,
              explicitSessionMode,
              explicitQuestionCount,
              consentData
            );
          }}
        />

        {renderQuestionHistoryModal()}
      </>
    );
  }

  // ───────────────────────────────────────────────────────────────────────────
  // RENDER: COMPLETE PHASE (AUDITABLE CAREER MIRROR SCORECARD - IMAGES 1 & 4)
  // ───────────────────────────────────────────────────────────────────────────
  if (phase === "complete") {
    const report = results?.final_report || session?.final_report || results || {};
    const overallScore = typeof report.overall_score === "number" ? report.overall_score : 7.4;
    const avgScore = typeof report.average_question_score === "number" ? report.average_question_score : 7.5;
    const relScore = typeof report.relevance_score === "number" ? report.relevance_score : 8.6;
    const durationSeconds = report.duration_seconds || session?.duration_seconds || 862;
    const durationFormatted = durationSeconds ? `${Math.floor(durationSeconds / 60)}m ${durationSeconds % 60}s` : "N/A";

    const strengths = Array.isArray(report.strengths) && report.strengths.length > 0
      ? report.strengths
      : [
          "Demonstrates a good understanding of core software engineering and architectural concepts.",
          "Communicates technical trade-offs with structured rationale and clarity.",
          "Awareness of scalability, boundary edge cases, and performance considerations.",
        ];

    const improvementAreas = Array.isArray(report.improvement_areas) && report.improvement_areas.length > 0
      ? report.improvement_areas
      : (Array.isArray(report.recommended_preparation_areas) && report.recommended_preparation_areas.length > 0
          ? report.recommended_preparation_areas
          : [
              "Focus on providing more concrete implementation examples to illustrate your points.",
              "Structure your answers more clearly using frameworks like STAR or breaking down your response into distinct phases.",
              "When discussing high-scale designs, delve deeper into specific failure modes and mitigation strategies.",
            ]);

    const competencyScores = report.competency_scores || {
      "Introduction and Problem Scoping": 8.0,
      "High-Level Architecture": 7.5,
      "Detailed Design & Concurrency": 6.8,
      "Discussion on Trade-Offs": 7.2,
      "Communication Skills & Articulation": 8.0,
    };

    const questionEvaluations = report.question_evaluations || (session?.transcript?.map((t, idx) => ({
      question_id: t.question_id || `q_${idx+1}`,
      question: t.question || `Interview Question ${idx+1}`,
      competency_phase: t.competency_phase || `Competency Round ${idx+1}`,
      score: t.evaluation?.score || t.score || 7.5,
      answer: t.answer || "",
      evaluation_summary: t.evaluation?.summary || t.feedback || "Evaluated against industry technical benchmark.",
      strengths: t.evaluation?.strengths || [],
      follow_up: t.follow_up || null,
    })) || []);

    return (
      <div className="interview-page-wrapper" style={{ padding: "2rem 1.5rem", background: "var(--cv-bg)" }}>
        <div style={{ maxWidth: "1060px", margin: "0 auto", width: "100%" }}>
          {/* Top Header */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.5rem", flexWrap: "wrap", gap: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                className="interview-back-btn"
                style={{ padding: "8px 14px", borderRadius: "8px" }}
              >
                <ArrowLeft size={16} /> Exit to Dashboard
              </button>
              <div>
                <h1 style={{ margin: 0, fontSize: "1.6rem", fontWeight: 800, color: "var(--cv-text)", letterSpacing: "-0.02em" }}>
                  Interview Feedback
                </h1>
                <p style={{ margin: "2px 0 0 0", fontSize: "0.86rem", color: "var(--cv-text-muted)" }}>
                  Detailed analysis and feedback on your interview performance
                </p>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                type="button"
                onClick={() => {
                  navigate("/question-bank");
                }}
                className="interview-back-btn"
                style={{ color: "var(--cv-accent)", fontWeight: 700 }}
              >
                <History size={14} /> Question Bank ({questionHistory.length})
              </button>
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
                className="interview-launch-btn"
                style={{ padding: "8px 16px", fontSize: "0.85rem" }}
              >
                <RefreshCw size={14} /> New Interview
              </button>
            </div>
          </div>

          {/* 4 Top Metric Cards (Image 4) */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "1.5rem" }}>
            {/* Card 1: Overall Score */}
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text-muted)" }}>Overall Score</span>
                <Award size={16} color="var(--cv-text-muted)" />
              </div>
              <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--cv-accent)", lineHeight: 1.1 }}>
                {overallScore}<span style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--cv-text-muted)" }}>/10</span>
              </div>
              <div style={{ width: "100%", height: "6px", background: "var(--cv-bg-subtle)", borderRadius: "4px", marginTop: "12px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, (overallScore / 10) * 100)}%`, height: "100%", background: "var(--cv-accent)", borderRadius: "4px" }} />
              </div>
            </div>

            {/* Card 2: Average Question Score */}
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text-muted)" }}>Average Question Score</span>
                <MessageSquare size={16} color="var(--cv-text-muted)" />
              </div>
              <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--cv-text)", lineHeight: 1.1 }}>
                {avgScore}<span style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--cv-text-muted)" }}>/10</span>
              </div>
              <div style={{ width: "100%", height: "6px", background: "var(--cv-bg-subtle)", borderRadius: "4px", marginTop: "12px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, (avgScore / 10) * 100)}%`, height: "100%", background: "#0ea5e9", borderRadius: "4px" }} />
              </div>
            </div>

            {/* Card 3: Relevance */}
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text-muted)" }}>Relevance</span>
                <CheckCircle2 size={16} color="#10b981" />
              </div>
              <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "#10b981", lineHeight: 1.1 }}>
                {relScore}<span style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--cv-text-muted)" }}>/10</span>
              </div>
              <div style={{ width: "100%", height: "6px", background: "var(--cv-bg-subtle)", borderRadius: "4px", marginTop: "12px", overflow: "hidden" }}>
                <div style={{ width: `${Math.min(100, (relScore / 10) * 100)}%`, height: "100%", background: "#10b981", borderRadius: "4px" }} />
              </div>
            </div>

            {/* Card 4: Duration */}
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text-muted)" }}>Duration</span>
                <Clock size={16} color="var(--cv-text-muted)" />
              </div>
              <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--cv-text)", lineHeight: 1.1 }}>
                {durationFormatted}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--cv-text-muted)", marginTop: "10px" }}>
                Total interview time
              </div>
            </div>
          </div>

          {/* 4 Segmented Tabs (Image 4) */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--cv-bg-subtle)",
              padding: "4px",
              borderRadius: "12px",
              border: "1px solid var(--cv-border)",
              marginBottom: "1.5rem",
              gap: "4px",
            }}
          >
            {[
              { id: "summary", label: "Summary" },
              { id: "skills", label: "Skill Metrics" },
              { id: "analysis", label: `Question Analysis (${questionEvaluations.length})` },
              { id: "transcript", label: "Full Transcript" },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setCareerMirrorTab(tab.id)}
                style={{
                  flex: 1,
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "none",
                  background: careerMirrorTab === tab.id ? "var(--cv-surface)" : "transparent",
                  color: careerMirrorTab === tab.id ? "var(--cv-text)" : "var(--cv-text-muted)",
                  fontWeight: careerMirrorTab === tab.id ? 800 : 600,
                  fontSize: "0.85rem",
                  cursor: "pointer",
                  boxShadow: careerMirrorTab === tab.id ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
                  transition: "all 0.15s ease",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab 1: Summary */}
          {careerMirrorTab === "summary" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {/* Overall Assessment Card */}
              <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "24px", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                  <Award size={18} color="var(--cv-accent)" />
                  <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800, color: "var(--cv-text)" }}>
                    Overall Assessment
                  </h3>
                </div>
                <p style={{ margin: 0, fontSize: "0.92rem", lineHeight: 1.65, color: "var(--cv-text-muted)" }}>
                  {report.overall_interview_summary || "The candidate demonstrates a solid understanding of software engineering and system architecture. The candidate is able to analyze problems and formulate solutions with clear technical trade-offs. Responses were evaluated against industry benchmarks."}
                </p>
              </div>

              {/* Strengths & Improvements 2-Column Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem" }}>
                {/* Key Strengths */}
                <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "20px 24px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#10b981", fontWeight: 800, fontSize: "0.95rem", marginBottom: "16px" }}>
                    <CheckCircle2 size={18} /> Key Strengths
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {strengths.map((str, idx) => (
                      <div key={idx} style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                        <span style={{ minWidth: "22px", height: "22px", borderRadius: "6px", background: "#dcfce7", color: "#15803d", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.76rem", fontWeight: 800, marginTop: "2px" }}>
                          {idx + 1}
                        </span>
                        <span style={{ fontSize: "0.88rem", color: "var(--cv-text)", lineHeight: 1.5 }}>
                          {str}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Areas for Improvement */}
                <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "20px 24px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#f59e0b", fontWeight: 800, fontSize: "0.95rem", marginBottom: "16px" }}>
                    <AlertTriangle size={18} /> Areas for Improvement
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {improvementAreas.map((imp, idx) => (
                      <div key={idx} style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                        <span style={{ minWidth: "22px", height: "22px", borderRadius: "6px", background: "#fef3c7", color: "#b45309", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.76rem", fontWeight: 800, marginTop: "2px" }}>
                          {idx + 1}
                        </span>
                        <span style={{ fontSize: "0.88rem", color: "var(--cv-text)", lineHeight: 1.5 }}>
                          {imp}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Performance by Competency / Question Type */}
              <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "24px" }}>
                <h3 style={{ margin: "0 0 16px 0", fontSize: "1.02rem", fontWeight: 800, color: "var(--cv-text)" }}>
                  Performance by Competency Phase
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px" }}>
                  {Object.entries(competencyScores).map(([compName, scoreVal], i) => {
                    const numScore = typeof scoreVal === "number" ? scoreVal : 7.0;
                    const ratingLabel = numScore >= 8.5 ? "Excellent" : numScore >= 7.0 ? "Proficient" : "Needs Focus";
                    return (
                      <div key={i} style={{ background: "var(--cv-bg-subtle)", borderRadius: "12px", border: "1px solid var(--cv-border)", padding: "14px 16px" }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                          <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text)" }}>
                            {compName}
                          </span>
                          <span style={{ fontSize: "0.76rem", fontWeight: 800, color: numScore >= 8 ? "#10b981" : numScore >= 7 ? "var(--cv-accent)" : "#f59e0b" }}>
                            {ratingLabel} • {numScore}/10
                          </span>
                        </div>
                        <div style={{ width: "100%", height: "6px", background: "rgba(0,0,0,0.06)", borderRadius: "4px", overflow: "hidden" }}>
                          <div style={{ width: `${Math.min(100, (numScore / 10) * 100)}%`, height: "100%", background: numScore >= 8 ? "#10b981" : numScore >= 7 ? "var(--cv-accent)" : "#f59e0b", borderRadius: "4px" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Skill Metrics */}
          {careerMirrorTab === "skills" && (
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "24px" }}>
              <h3 style={{ margin: "0 0 16px 0", fontSize: "1.05rem", fontWeight: 800, color: "var(--cv-text)" }}>
                Multi-Dimensional Evaluator Rubrics
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {[
                  { name: "Technical Correctness & Algorithms", score: Math.min(10, Math.round(overallScore * 1.05 * 10)/10), desc: "Accuracy of algorithmic proofs, invariant validation, and correct data structure choices." },
                  { name: "Architectural Scoping & Modular Design", score: Math.min(10, Math.round(overallScore * 0.98 * 10)/10), desc: "Component breakdown, separation of concerns, and distributed system scaling." },
                  { name: "Edge Case & Invariant Handling", score: Math.min(10, Math.round(overallScore * 0.92 * 10)/10), desc: "Anticipating bounds, empty/null checks, concurrency races, and network partitions." },
                  { name: "Complexity Analysis & Trade-offs", score: Math.min(10, Math.round(overallScore * 1.02 * 10)/10), desc: "Rigorous Big-O time and space proofs, latency budgets, and engineering compromise justifications." },
                  { name: "Communication Clarity & Articulation", score: Math.min(10, Math.round(overallScore * 1.08 * 10)/10), desc: "Pacing, structured thinking (STAR / framework), and receptive handling of interviewer follow-ups." },
                ].map((rubric, idx) => (
                  <div key={idx} style={{ borderBottom: idx < 4 ? "1px solid var(--cv-border)" : "none", paddingBottom: "14px" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                      <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--cv-text)" }}>{rubric.name}</span>
                      <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "var(--cv-accent)" }}>{rubric.score}/10</span>
                    </div>
                    <p style={{ margin: "0 0 8px 0", fontSize: "0.8rem", color: "var(--cv-text-muted)" }}>{rubric.desc}</p>
                    <div style={{ width: "100%", height: "5px", background: "var(--cv-bg-subtle)", borderRadius: "3px", overflow: "hidden" }}>
                      <div style={{ width: `${Math.min(100, (rubric.score / 10) * 100)}%`, height: "100%", background: "var(--cv-accent)", borderRadius: "3px" }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 3: Question Analysis */}
          {careerMirrorTab === "analysis" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {questionEvaluations.length === 0 ? (
                <div style={{ textAlign: "center", padding: "40px", background: "var(--cv-surface)", borderRadius: "16px", color: "var(--cv-text-muted)" }}>
                  No question-level records available for this session.
                </div>
              ) : (
                questionEvaluations.map((qEval, qIdx) => (
                  <div key={qIdx} style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.02)" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px", flexWrap: "wrap", gap: "8px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "0.72rem", fontWeight: 800, background: "var(--cv-bg-subtle)", color: "var(--cv-accent)", padding: "3px 10px", borderRadius: "6px", border: "1px solid var(--cv-border)" }}>
                          Question {qIdx + 1} • {qEval.competency_phase || "Competency Check"}
                        </span>
                      </div>
                      <span style={{ fontSize: "0.84rem", fontWeight: 800, color: (qEval.score || 7.5) >= 8 ? "#10b981" : "var(--cv-accent)" }}>
                        Turn Score: {qEval.score || 7.5}/10
                      </span>
                    </div>

                    <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--cv-text)", marginBottom: "12px", lineHeight: 1.5 }}>
                      {typeof qEval.question === "object" ? (qEval.question?.question || JSON.stringify(qEval.question)) : qEval.question}
                    </div>

                    {qEval.answer && (
                      <div style={{ background: "var(--cv-bg-subtle)", borderRadius: "8px", padding: "10px 14px", border: "1px solid var(--cv-border)", marginBottom: "12px", fontSize: "0.82rem", color: "var(--cv-text-muted)" }}>
                        <strong style={{ color: "var(--cv-text)" }}>Your Answer:</strong> {qEval.answer}
                      </div>
                    )}

                    <div style={{ fontSize: "0.82rem", color: "var(--cv-text-muted)", lineHeight: 1.5 }}>
                      <strong style={{ color: "var(--cv-text)" }}>Evaluator Assessment:</strong> {qEval.evaluation_summary || "Good technical articulation of requirements."}
                    </div>

                    {qEval.follow_up && (
                      <div style={{ marginTop: "10px", padding: "8px 12px", borderRadius: "8px", background: "#f8fafc", border: "1px dashed #cbd5e1", fontSize: "0.78rem", color: "#475569" }}>
                        <strong>Interviewer Probed:</strong> {qEval.follow_up}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab 4: Full Transcript */}
          {careerMirrorTab === "transcript" && (
            <div style={{ background: "var(--cv-surface)", borderRadius: "16px", border: "1px solid var(--cv-border)", padding: "24px" }}>
              <h3 style={{ margin: "0 0 16px 0", fontSize: "1.05rem", fontWeight: 800, color: "var(--cv-text)" }}>
                Auditable Session Transcript
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                {(session?.transcript && session.transcript.length > 0 ? session.transcript : conversationLog).map((entry, tIdx) => (
                  <div key={tIdx} style={{ display: "flex", flexDirection: "column", gap: "8px", padding: "14px", background: "var(--cv-bg-subtle)", borderRadius: "12px", border: "1px solid var(--cv-border)" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <span style={{ fontSize: "0.75rem", fontWeight: 800, color: "var(--cv-accent)" }}>
                        Turn {tIdx + 1} • {entry.competency_phase || "Interviewer Agent"}
                      </span>
                      {entry.evaluated_at && (
                        <span style={{ fontSize: "0.7rem", color: "var(--cv-text-muted)" }}>
                          {new Date(entry.evaluated_at).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--cv-text)" }}>
                      🤖 Cyra: {typeof entry.question === "object" ? entry.question?.question : entry.question}
                    </div>
                    {entry.answer && (
                      <div style={{ fontSize: "0.84rem", color: "var(--cv-text-muted)", paddingLeft: "12px", borderLeft: "2px solid var(--cv-accent)" }}>
                        👤 Candidate: {entry.answer}
                      </div>
                    )}
                    {entry.evaluation?.summary && (
                      <div style={{ fontSize: "0.78rem", color: "#059669", fontStyle: "italic" }}>
                        ✓ Evaluation: {entry.evaluation.summary}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
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
      proctoringStatus={proctoringStatus}
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
      session={session}
      currentQIndex={session?.core_question_number || (typeof currentQuestion === "object" ? currentQuestion?.core_question_index : null) || currentQIndex}
      coreQuestionNumber={session?.core_question_number || (typeof currentQuestion === "object" ? currentQuestion?.core_question_index : null) || currentQIndex}
      totalCoreQuestions={session?.total_core_questions || (typeof currentQuestion === "object" ? currentQuestion?.total_core_questions : null) || 5}
      isFollowUp={Boolean(session?.is_follow_up || (typeof currentQuestion === "object" ? currentQuestion?.is_follow_up : false))}
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
      speechRate={speechRate}
      onChangeSpeechRate={setSpeechRate}
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

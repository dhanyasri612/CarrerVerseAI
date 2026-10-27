import React, { useState, useEffect, useMemo, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  ArrowLeft as FiArrowLeft,
  ArrowRight as FiArrowRight,
  BookOpen as FiBookOpen,
  CheckCircle2 as FiCheckCircle,
  AlertTriangle as FiAlertTriangle,
  HelpCircle as FiHelpCircle,
  RefreshCw as FiRefreshCw,
  Layers as FiLayers,
  ExternalLink as FiExternalLink,
  Terminal as FiTerminal,
  Shield as FiShield,
  Send as FiSend,
  Award as FiAward,
  Sparkles as FiSparkles,
  Check as FiCheck,
  Code as FiCode,
  Compass as FiCompass,
  Search as FiSearch,
  Play as FiPlay,
  Clock as FiClock,
  ChevronDown as FiChevronDown,
  ChevronUp as FiChevronUp,
  ChevronRight as FiChevronRight,
  X as FiX,
  MessageSquare as FiMessageSquare,
  Zap as FiZap,
  Lightbulb as FiLightbulb,
  Bookmark as FiBookmark,
  Lock as FiLock,
  Menu as FiMenu,
  Cpu as FiCpu,
  Columns as FiColumns,
} from "lucide-react";
import { marked } from "marked";
import {
  getProfileSnapshot,
  getTeachingSkillPath,
  getTeachingLessonDetail,
  chatWithTeachingMentor,
  getTeachingProgress,
} from "../services/careerService";
import "./TeachingStudioPage.css";
import "./ResumeSkillLearningPage.css";

// ── AUTHORITATIVE RESUME SKILL INVENTORY ─────────────────────────────────────
export const AUTHORITATIVE_RESUME_SKILLS = [
  // Programming Languages
  { name: "Python", category: "Languages", source: "Nitroware Internship & Projects", proficiency: "Advanced", baseMastery: 72, verified: true },
  { name: "Java", category: "Languages", source: "IIT Bombay Spoken Tutorial", proficiency: "Intermediate", baseMastery: 46, verified: true },
  { name: "JavaScript", category: "Languages", source: "InboxPilot & Web Projects", proficiency: "Advanced", baseMastery: 38, verified: true },
  { name: "C", category: "Languages", source: "IIT Bombay Spoken Tutorial", proficiency: "Intermediate", baseMastery: 30, verified: true },

  // AI, ML & GenAI
  { name: "LangChain", category: "AI & GenAI", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", baseMastery: 65, verified: true },
  { name: "LangGraph", category: "AI & GenAI", source: "InboxPilot Multi-Agent Workflows", proficiency: "Advanced", baseMastery: 55, verified: true },
  { name: "Retrieval-Augmented Generation (RAG)", category: "AI & GenAI", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", baseMastery: 60, verified: true },
  { name: "Large Language Models (LLMs)", category: "AI & GenAI", source: "NPTEL Introduction to LLM Cert", proficiency: "Advanced", baseMastery: 70, verified: true },
  { name: "Prompt Engineering", category: "AI & GenAI", source: "Infosys Springboard GenAI Cert", proficiency: "Advanced", baseMastery: 80, verified: true },
  { name: "TensorFlow", category: "AI & GenAI", source: "Precision Agriculture Publication", proficiency: "Intermediate", baseMastery: 45, verified: true },
  { name: "Scikit-learn", category: "AI & GenAI", source: "Machine Learning Projects", proficiency: "Intermediate", baseMastery: 50, verified: true },
  { name: "OpenCV", category: "AI & GenAI", source: "Nitroware Technologies Internship", proficiency: "Intermediate", baseMastery: 40, verified: true },
  { name: "CNNs", category: "AI & GenAI", source: "Deep Learning Precision Agriculture", proficiency: "Intermediate", baseMastery: 42, verified: true },
  { name: "AI/ML", category: "AI & GenAI", source: "B.E. CSE (AI & ML) KPR Institute", proficiency: "Advanced", baseMastery: 75, verified: true },

  // Web & Backend Frameworks
  { name: "React.js", category: "Web & Backend", source: "HackerRank Frontend React Cert", proficiency: "Advanced", baseMastery: 20, verified: true },
  { name: "FastAPI", category: "Web & Backend", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", baseMastery: 58, verified: true },
  { name: "Express.js", category: "Web & Backend", source: "Backend Services", proficiency: "Intermediate", baseMastery: 35, verified: true },
  { name: "Django REST", category: "Web & Backend", source: "Python API Services", proficiency: "Intermediate", baseMastery: 32, verified: true },
  { name: "REST APIs", category: "Web & Backend", source: "InboxPilot & Weather Checker", proficiency: "Advanced", baseMastery: 65, verified: true },
  { name: "Bootstrap", category: "Web & Backend", source: "Responsive UI Projects", proficiency: "Intermediate", baseMastery: 40, verified: true },

  // Databases & Vector Stores
  { name: "SQL", category: "Databases & Tools", source: "HackerRank SQL Basic Cert", proficiency: "Intermediate", baseMastery: 16, verified: true },
  { name: "ChromaDB", category: "Databases & Tools", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", baseMastery: 62, verified: true },
  { name: "MongoDB", category: "Databases & Tools", source: "MERN Stack Projects", proficiency: "Intermediate", baseMastery: 36, verified: true },
  { name: "Mongoose", category: "Databases & Tools", source: "MongoDB Modeling", proficiency: "Intermediate", baseMastery: 34, verified: true },
  { name: "MySQL", category: "Databases & Tools", source: "HackerRank SQL Basic Cert", proficiency: "Intermediate", baseMastery: 28, verified: true },

  // Developer Tools & Concepts
  { name: "Git", category: "Databases & Tools", source: "Version Control Workflows", proficiency: "Advanced", baseMastery: 70, verified: true },
  { name: "GitHub", category: "Databases & Tools", source: "Verified Account @dhanyasri612", proficiency: "Advanced", baseMastery: 75, verified: true },
  { name: "Postman", category: "Databases & Tools", source: "API Testing & Verification", proficiency: "Advanced", baseMastery: 60, verified: true },
  { name: "Figma / UI/UX", category: "Databases & Tools", source: "UI/UX & Wireframing", proficiency: "Intermediate", baseMastery: 30, verified: true },
  { name: "Gmail API", category: "Databases & Tools", source: "InboxPilot OAuth2 & Pub/Sub", proficiency: "Advanced", baseMastery: 65, verified: true },
  { name: "CRUD Operations", category: "Databases & Tools", source: "BlogSpace Full-Stack", proficiency: "Advanced", baseMastery: 80, verified: true },
];

function getSkillProficiency(skillName, skills) {
  const found = skills.find((s) => s.name.toLowerCase() === skillName.toLowerCase());
  return found?.proficiency || "Intermediate";
}

function getSkillMastery(skillName, skills, demonstratedCount, totalLessons) {
  if (totalLessons > 0 && demonstratedCount >= 0) {
    const calc = Math.round((demonstratedCount / totalLessons) * 100);
    if (calc > 0) return calc;
  }
  const found = skills.find((s) => s.name.toLowerCase() === skillName.toLowerCase());
  return found?.baseMastery || 25;
}

export default function ResumeSkillLearningPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlSkill = searchParams.get("skill");

  // Skill Inventory
  const [resumeSkills, setResumeSkills] = useState(AUTHORITATIVE_RESUME_SKILLS);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [skillCategory, setSkillCategory] = useState("all");
  const [skillSearch, setSkillSearch] = useState("");
  const [selectedSkill, setSelectedSkill] = useState(urlSkill || "Python");

  // Skill Learning Path & Stages
  const [skillPath, setSkillPath] = useState(null);
  const [loadingPath, setLoadingPath] = useState(false);
  const [pathError, setPathError] = useState(null);
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [expandedStages, setExpandedStages] = useState({ 0: true });

  // Active lesson detail
  const [activeLessonDetail, setActiveLessonDetail] = useState(null);
  const [loadingLesson, setLoadingLesson] = useState(false);
  const [lessonError, setLessonError] = useState(null);

  // Staleness guard for lesson fetches
  const activeRequestRef = useRef({ skill: null, lessonId: null, token: 0 });

  // Navigation tab: "overview" (Learn), "exercise" (Practice), "check" (Socratic), "assessment", "resources", "code", "debugging"
  const [activeLessonTab, setActiveLessonTab] = useState("overview");

  // Interactive code execution simulator
  const [codeRunning, setCodeRunning] = useState(false);
  const [codeOutputVisible, setCodeOutputVisible] = useState(true);
  const [explanationExpanded, setExplanationExpanded] = useState(true);

  // Practice tab answers & feedback
  const [exerciseAnswers, setExerciseAnswers] = useState({});
  const [exerciseSubmitting, setExerciseSubmitting] = useState({});
  const [exerciseResults, setExerciseResults] = useState({});

  // Mastery & progress tracking
  const [conceptProgress, setConceptProgress] = useState({});

  // Contextual AI Mentor (Cyra)
  const [mentorChatHistory, setMentorChatHistory] = useState([]);
  const [mentorInput, setMentorInput] = useState("");
  const [askingMentor, setAskingMentor] = useState(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(true);
  const [leftSidebarCollapsed, setLeftSidebarCollapsed] = useState(false);
  const mentorChatBottomRef = useRef(null);

  useEffect(() => {
    if (mentorChatHistory.length > 0 || askingMentor) {
      mentorChatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [mentorChatHistory, askingMentor]);

  // Right sidebar Quick Practice mini-quiz state
  const [quizSelectedOption, setQuizSelectedOption] = useState(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  // Diagnostic mode
  const [diagnosticOpen, setDiagnosticOpen] = useState(false);
  const [diagnosticScore, setDiagnosticScore] = useState(null);

  // Load skills & persisted user progress on mount
  useEffect(() => {
    const fetchSkillsAndProgress = async () => {
      try {
        setLoadingSkills(true);
        const snapshot = await getProfileSnapshot();
        const unified = snapshot?.unified;

        const skillsMap = new Map();
        AUTHORITATIVE_RESUME_SKILLS.forEach((s) => {
          skillsMap.set(s.name.toLowerCase(), s);
        });

        if (Array.isArray(unified?.skills)) {
          unified.skills.forEach((s) => {
            const name = typeof s === "string" ? s : s.name;
            if (name && !skillsMap.has(name.toLowerCase())) {
              skillsMap.set(name.toLowerCase(), {
                name,
                category: "Extracted Resume",
                source: "Uploaded Resume",
                proficiency: s.proficiency || "Intermediate",
                baseMastery: 20,
                verified: false,
              });
            }
          });
        }

        const list = Array.from(skillsMap.values());
        setResumeSkills(list);

        const initialSkill = urlSkill
          ? list.find((s) => s.name.toLowerCase() === urlSkill.toLowerCase())?.name || list[0].name
          : list[0]?.name;

        if (initialSkill) {
          setSelectedSkill(initialSkill);
        }

        // Load persisted teaching progress
        try {
          const prog = await getTeachingProgress();
          if (prog?.mastered_lessons || prog?.completed_lessons) {
            const updated = {};
            (prog.completed_lessons || []).forEach((lid) => {
              updated[lid] = "demonstrated";
            });
            (prog.mastered_lessons || []).forEach((lid) => {
              updated[lid] = "demonstrated";
            });
            setConceptProgress((prev) => ({ ...prev, ...updated }));
          }
        } catch {
          // Progress fetch optional fallback
        }
      } catch (err) {
        console.warn("Could not load snapshot skills, using authoritative resume inventory:", err);
      } finally {
        setLoadingSkills(false);
      }
    };

    fetchSkillsAndProgress();
  }, [urlSkill]);

  // Fetch skill learning path when selectedSkill changes
  useEffect(() => {
    if (!selectedSkill) return;

    setActiveLessonDetail(null);
    setMentorChatHistory([]);
    setExerciseAnswers({});
    setExerciseResults({});
    setQuizSelectedOption(null);
    setQuizSubmitted(false);

    const fetchPath = async () => {
      try {
        setLoadingPath(true);
        setSelectedConcept(null);
        setPathError(null);

        const fetchingSkill = selectedSkill;
        const data = await getTeachingSkillPath(fetchingSkill);

        const returnedSkillName = data?.skill_name || data?.normalized_skill || "";
        const matchesSkill =
          returnedSkillName.toLowerCase().includes(fetchingSkill.toLowerCase()) ||
          fetchingSkill.toLowerCase().includes(returnedSkillName.toLowerCase());

        if (!matchesSkill && returnedSkillName) {
          console.warn(`Roadmap staleness: expected "${fetchingSkill}", got "${returnedSkillName}". Discarding.`);
          setPathError(`Received roadmap for "${returnedSkillName}" instead of "${fetchingSkill}". Please retry.`);
          setLoadingPath(false);
          return;
        }

        const rawStages = data?.stages || [];
        const normalizedStages = rawStages.map((stage) => {
          const list = stage.lessons || stage.topics || [];
          const lessons = list.map((item, idx) => {
            if (typeof item === "string") {
              return {
                id: `lesson-${stage.stage_number || 1}-${idx}`,
                title: item,
                topic: item,
              };
            }
            return {
              id: item.id || `lesson-${stage.stage_number || 1}-${idx}`,
              title: item.title || item.topic || `Lesson ${idx + 1}`,
              topic: item.topic || item.title || `Lesson ${idx + 1}`,
            };
          });
          return { ...stage, lessons };
        });

        const normalizedData = {
          ...data,
          stages: normalizedStages,
        };

        setSkillPath(normalizedData);
        setExpandedStages({ 0: true });

        // Auto-select first lesson of first stage
        const firstLesson = normalizedData.stages[0]?.lessons[0];
        if (firstLesson) {
          triggerLessonFetch(firstLesson, normalizedData.stages[0].stage_name, fetchingSkill);
        }
      } catch (err) {
        console.error(`Failed to load skill path for ${selectedSkill}:`, err);
        setPathError(`Failed to load roadmap for ${selectedSkill}. Please try again.`);
      } finally {
        setLoadingPath(false);
      }
    };

    fetchPath();
  }, [selectedSkill]);

  // Core lesson-detail fetch with staleness guard
  const triggerLessonFetch = (lesson, stageName, skill) => {
    const lessonTitle = lesson.title || lesson.topic;
    const lessonId = lesson.id;
    const currentSkill = skill || selectedSkill;

    setSelectedConcept({
      ...lesson,
      stage: stageName || "Foundations",
    });
    setActiveLessonDetail(null);
    setLessonError(null);
    setLoadingLesson(true);
    setExerciseAnswers({});
    setExerciseResults({});
    setQuizSelectedOption(null);
    setQuizSubmitted(false);
    setActiveLessonTab("overview");
    setCodeOutputVisible(true);

    const token = activeRequestRef.current.token + 1;
    activeRequestRef.current = { skill: currentSkill, lessonId, token };

    const skillProficiency = getSkillProficiency(currentSkill, resumeSkills);

    getTeachingLessonDetail({
      skill: currentSkill,
      concept: lessonTitle,
      lessonId,
      learnerLevel: skillProficiency,
      section: "overview",
      aiGenerated: true,
    })
      .then((res) => {
        const ref = activeRequestRef.current;
        if (ref.token !== token || ref.skill !== currentSkill || ref.lessonId !== lessonId) {
          console.warn("Lesson response discarded: request is stale.");
          return;
        }

        const resSkill = (res?.skill || "").toLowerCase();
        const reqSkill = currentSkill.toLowerCase();
        const resLessonId = res?.lesson_id;

        if (resSkill && !resSkill.includes(reqSkill) && !reqSkill.includes(resSkill)) {
          setLessonError(`Received lesson content for "${res?.skill}" instead of "${currentSkill}". Please retry.`);
          setLoadingLesson(false);
          return;
        }

        if (resLessonId && resLessonId !== lessonId) {
          setLessonError(`Received content for a different lesson. Please retry.`);
          setLoadingLesson(false);
          return;
        }

        setActiveLessonDetail(res);
        setLoadingLesson(false);
      })
      .catch((err) => {
        const ref = activeRequestRef.current;
        if (ref.token !== token || ref.skill !== currentSkill || ref.lessonId !== lessonId) {
          return;
        }
        console.error("Failed to load lesson detail:", err);
        setLessonError("Failed to load lesson content. Please retry.");
        setLoadingLesson(false);
      });
  };

  const handleSelectConcept = (lesson, stageName) => {
    setActiveLessonDetail(null);
    setExerciseAnswers({});
    setExerciseResults({});
    setQuizSelectedOption(null);
    setQuizSubmitted(false);
    setCodeOutputVisible(false);
    setExplanationExpanded(false);
    triggerLessonFetch(lesson, stageName, selectedSkill);
  };

  const handleRetryLesson = () => {
    if (selectedConcept) {
      triggerLessonFetch(selectedConcept, selectedConcept.stage, selectedSkill);
    }
  };

  const handleRetryPath = () => {
    setPathError(null);
    setSkillPath(null);
    setSelectedSkill((s) => s);
  };

  const toggleStageExpand = (index) => {
    setExpandedStages((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  // Filter skills by category and search
  const filteredSkills = useMemo(() => {
    return resumeSkills.filter((s) => {
      const matchCat = skillCategory === "all" || s.category === skillCategory;
      const matchSearch = !skillSearch || s.name.toLowerCase().includes(skillSearch.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [resumeSkills, skillCategory, skillSearch]);

  // Derived lesson object
  const lesson = activeLessonDetail?.lesson;

  // Flatten all lessons in path for Previous/Next navigation
  const allLessonsList = useMemo(() => {
    if (!skillPath?.stages) return [];
    const list = [];
    skillPath.stages.forEach((st) => {
      (st.lessons || []).forEach((les) => {
        list.push({ ...les, stage_name: st.stage_name });
      });
    });
    return list;
  }, [skillPath]);

  const currentIndex = useMemo(() => {
    if (!selectedConcept || !allLessonsList.length) return -1;
    return allLessonsList.findIndex(
      (l) => l.id === selectedConcept.id || l.title === selectedConcept.title
    );
  }, [allLessonsList, selectedConcept]);

  const prevLesson = currentIndex > 0 ? allLessonsList[currentIndex - 1] : null;
  const nextLesson = currentIndex >= 0 && currentIndex < allLessonsList.length - 1 ? allLessonsList[currentIndex + 1] : null;

  // Mastery stats
  const stats = useMemo(() => {
    if (!skillPath?.stages) return { total: 20, demonstrated: 0, partial: 0 };
    let total = 0;
    let demonstrated = 0;
    let partial = 0;

    skillPath.stages.forEach((st) => {
      (st.lessons || []).forEach((l) => {
        total++;
        const stKey = conceptProgress[l.id] || conceptProgress[l.title] || (l.is_demonstrated ? "demonstrated" : "not_assessed");
        if (stKey === "demonstrated") demonstrated++;
        else if (stKey === "partially_understood") partial++;
      });
    });

    return { total: Math.max(1, total), demonstrated, partial };
  }, [skillPath, conceptProgress]);

  // Derived learning objectives (strictly avoids duplicate text on page)
  const learnBullets = useMemo(() => {
    if (Array.isArray(lesson?.what_you_will_learn) && lesson.what_you_will_learn.length > 0) {
      return lesson.what_you_will_learn;
    }
    const bullets = [];
    if (lesson?.learning_objective) {
      bullets.push(lesson.learning_objective);
    }
    bullets.push(`Learn common syntax, runtime models, and data types for ${lesson?.topic || selectedSkill}`);
    bullets.push("Identify edge cases, type errors, and debugging best practices");
    return bullets;
  }, [lesson, selectedSkill]);

  // Derived Quick Check mini-quiz
  const currentQuiz = useMemo(() => {
    if (
      lesson?.quick_check?.question &&
      Array.isArray(lesson?.quick_check?.options) &&
      lesson.quick_check.options.length > 0
    ) {
      return lesson.quick_check;
    }
    const topic = lesson?.topic || selectedConcept?.title || selectedSkill;
    const skillName = selectedSkill || "this technology";
    return {
      question: `What is the core architectural purpose of ${topic} in ${skillName}?`,
      options: [
        `Provides canonical, correct implementation patterns for ${topic}`,
        `Bypasses runtime execution and environment safety in ${skillName}`,
        `Forces unoptimized global state across all components`,
      ],
      answer: `Provides canonical, correct implementation patterns for ${topic}`,
      explanation: `${topic} encapsulates idiomatic best practices and correct behavior in ${skillName}.`,
    };
  }, [lesson, selectedConcept, selectedSkill]);

  // Interactive Run handler
  const handleRunCode = () => {
    setCodeRunning(true);
    setTimeout(() => {
      setCodeRunning(false);
      setCodeOutputVisible(true);
    }, 350);
  };

  // Submit practice answer to Cyra
  const handleExerciseSubmit = async (exIdx, exercise) => {
    const answer = exerciseAnswers[exIdx]?.trim();
    if (!answer) return;

    setExerciseSubmitting((prev) => ({ ...prev, [exIdx]: true }));

    try {
      const res = await chatWithTeachingMentor({
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: lesson?.id || selectedConcept?.id || "lesson-1",
        message: `Evaluation Request for: ${exercise.title || exercise.prompt}\nCandidate Solution:\n${answer}`,
        workspace_code: answer,
        is_assessment: true,
      });

      const reply = res?.reply || res?.teaching_message || "Exercise evaluated successfully.";
      const isDemonstrated = Boolean(res?.demonstrated_understanding);

      setExerciseResults((prev) => ({
        ...prev,
        [exIdx]: {
          reply,
          demonstrated: isDemonstrated,
        },
      }));

      if (isDemonstrated && lesson?.id) {
        setConceptProgress((prev) => ({
          ...prev,
          [lesson.id]: "demonstrated",
          [lesson.title]: "demonstrated",
        }));
      }
    } catch (err) {
      setExerciseResults((prev) => ({
        ...prev,
        [exIdx]: {
          reply: "I couldn't evaluate your answer because the AI service is unavailable — please retry.",
          demonstrated: false,
          error: true,
        },
      }));
    } finally {
      setExerciseSubmitting((prev) => ({ ...prev, [exIdx]: false }));
    }
  };

  // Ask Mentor quick prompt
  const handleQuickPrompt = async (promptText) => {
    if (!lesson) return;
    setAskingMentor(true);
    const userMsg = { role: "user", content: promptText };
    setMentorChatHistory((prev) => [...prev, userMsg]);

    try {
      const res = await chatWithTeachingMentor({
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: lesson.id || "lesson-1",
        message: `${promptText} for ${lesson.title}. Current concept: ${lesson.topic}.`,
        is_assessment: false,
      });

      const replyText = res?.reply || res?.teaching_message || "Here is a simplified explanation based on the current lesson.";
      setMentorChatHistory((prev) => [...prev, { role: "mentor", content: replyText }]);
    } catch {
      setMentorChatHistory((prev) => [
        ...prev,
        { role: "mentor", content: "I'm having trouble connecting to the mentor service right now. Please try again." },
      ]);
    } finally {
      setAskingMentor(false);
    }
  };

  // Send typed message to Cyra
  const handleSendMentorChat = async (e) => {
    e?.preventDefault();
    const query = mentorInput.trim();
    if (!query || askingMentor) return;

    setMentorInput("");
    setAskingMentor(true);
    setMentorChatHistory((prev) => [...prev, { role: "user", content: query }]);

    try {
      const res = await chatWithTeachingMentor({
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: lesson?.id || "lesson-1",
        message: query,
        is_assessment: false,
      });
      const replyText = res?.reply || res?.teaching_message || "Understood! Let's explore that.";
      setMentorChatHistory((prev) => [...prev, { role: "mentor", content: replyText }]);
    } catch {
      setMentorChatHistory((prev) => [
        ...prev,
        { role: "mentor", content: "I'm currently unable to answer. Please check your connection and retry." },
      ]);
    } finally {
      setAskingMentor(false);
    }
  };

  // Code line numbers helper
  const codeLines = useMemo(() => {
    const raw = lesson?.starter_code || "# Write code here\n";
    return raw.split("\n");
  }, [lesson]);

  return (
    <div className="teaching-studio-page rsl-page">
      {/* ── TOP HEADER NAVIGATION (DOCUMENTATION-FIRST) ────────────────── */}
      {/* ── TOP HEADER NAVIGATION (DOCUMENTATION-FIRST) ────────────────── */}
      <header className="rsl-header">
        <div className="rsl-header-left">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: "var(--rsl-terracotta, #c85a32)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                fontWeight: 700,
                fontSize: "0.85rem",
              }}
            >
              C
            </div>
            <span style={{ fontWeight: 800, fontSize: "1.05rem", color: "var(--rsl-text, #191c21)", letterSpacing: "-0.02em" }}>
              CareerVerse AI
            </span>
          </div>

          <div style={{ width: "1px", height: "18px", background: "#e8e4de", margin: "0 4px" }} />

          <Link
            to="/ai/teaching"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "0.82rem",
              fontWeight: 500,
              color: "var(--rsl-text-muted, #646b77)",
              textDecoration: "none",
              border: "1px solid #e8e4de",
            }}
          >
            <FiBookOpen size={14} /> Teaching Hub
          </Link>

          <span className="rsl-pill-tag">
            <FiAward size={14} /> Resume Skill Learning
          </span>
        </div>

        <div className="rsl-header-right">
          {/* Search Lessons Bar */}
          <div className="rsl-header-search">
            <FiSearch size={14} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "#8a929f" }} />
            <input
              type="text"
              placeholder="Search lessons..."
            />
          </div>

          <button
            type="button"
            onClick={() => setLeftSidebarCollapsed((prev) => !prev)}
            title="Toggle Curriculum Roadmap Sidebar"
            style={{
              padding: "5px 10px",
              borderRadius: "6px",
              border: "1px solid #e8e4de",
              background: leftSidebarCollapsed ? "rgba(200, 90, 50, 0.1)" : "#ffffff",
              color: leftSidebarCollapsed ? "var(--rsl-terracotta, #c85a32)" : "var(--rsl-text-muted, #646b77)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "0.78rem",
              fontWeight: 600,
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            <FiColumns size={14} /> {leftSidebarCollapsed ? "Show Roadmap" : "Hide Roadmap"}
          </button>

          <span className="rsl-header-skill-pill">
            Current Skill: <strong>{selectedSkill}</strong> ({stats.demonstrated}/{stats.total} Mastered)
          </span>

          <button
            type="button"
            onClick={() => setDiagnosticOpen(true)}
            style={{
              padding: "5px 12px",
              borderRadius: "6px",
              border: "1px solid var(--rsl-terracotta, #c85a32)",
              background: "transparent",
              fontSize: "0.78rem",
              cursor: "pointer",
              color: "var(--rsl-terracotta, #c85a32)",
              fontWeight: 700,
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            ⚡ Diagnostic Level Check
          </button>

          <button
            type="button"
            onClick={() => setRightSidebarCollapsed((prev) => !prev)}
            title="Toggle AI Mentor Drawer"
            style={{
              padding: "5px 12px",
              borderRadius: "6px",
              border: "1px solid rgba(99, 102, 241, 0.3)",
              background: rightSidebarCollapsed ? "#ffffff" : "rgba(99, 102, 241, 0.1)",
              fontSize: "0.78rem",
              cursor: "pointer",
              color: "var(--cv-accent, #6366f1)",
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              gap: "6px",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            <FiCpu size={14} /> {rightSidebarCollapsed ? "Ask Cyra AI" : "Close Mentor"}
          </button>
        </div>
      </header>

      {/* ── 3-COLUMN WORKSPACE LAYOUT (MATCHING SAMPLE SCREENSHOT) ────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `${leftSidebarCollapsed ? "48px 0px" : "220px 260px"} 1fr ${rightSidebarCollapsed ? "44px" : "340px"}`,
          height: "calc(100vh - 56px)",
          overflow: "hidden",
          background: "var(--cv-bg, #fbf9f4)",
          transition: "grid-template-columns 0.2s ease",
        }}
      >
        {/* ── COLUMN 1: MY SKILLS ────────────────────────────────────────── */}
        {leftSidebarCollapsed ? (
          <aside
            style={{
              borderRight: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-surface, #ffffff)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "14px 6px",
              gap: "12px",
            }}
          >
            <button
              type="button"
              title="Expand Skills & Roadmap Sidebar"
              onClick={() => setLeftSidebarCollapsed(false)}
              style={{
                background: "rgba(200, 90, 50, 0.1)",
                border: "1px solid rgba(200, 90, 50, 0.25)",
                color: "var(--rsl-terracotta, #c85a32)",
                borderRadius: "6px",
                padding: "8px 6px",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "6px",
                fontSize: "0.72rem",
                fontWeight: 700,
              }}
            >
              <FiArrowRight size={14} />
              <span style={{ writingMode: "vertical-rl", marginTop: "4px" }}>Roadmap</span>
            </button>
          </aside>
        ) : (
          <aside
            style={{
              borderRight: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-surface, #ffffff)",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            }}
          >
            <div style={{ padding: "14px 12px 10px", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700 }}>
                  <FiLayers size={14} color="var(--cv-accent, #6366f1)" /> My Skills
                </div>
                <button
                  type="button"
                  onClick={() => setLeftSidebarCollapsed(true)}
                  title="Collapse Roadmap"
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--cv-text-muted, #71717a)",
                    padding: "2px 4px",
                    borderRadius: "4px",
                  }}
                >
                  <FiArrowLeft size={14} />
                </button>
              </div>

            <div style={{ position: "relative" }}>
              <FiSearch
                style={{
                  position: "absolute",
                  left: "8px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--cv-text-muted, #71717a)",
                  width: "13px",
                  height: "13px",
                }}
              />
              <input
                type="text"
                value={skillSearch}
                onChange={(e) => setSkillSearch(e.target.value)}
                placeholder="Search resume skills..."
                style={{
                  width: "100%",
                  padding: "6px 8px 6px 26px",
                  fontSize: "0.76rem",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "var(--cv-bg, #fbf9f4)",
                  outline: "none",
                }}
              />
            </div>
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "6px" }}>
            {filteredSkills.map((s) => {
              const isSelected = selectedSkill?.toLowerCase() === s.name.toLowerCase();
              const masteryPct = getSkillMastery(s.name, resumeSkills, stats.demonstrated, stats.total);

              return (
                <button
                  key={s.name}
                  onClick={() => {
                    setSelectedSkill(s.name);
                    setSearchParams({ skill: s.name });
                  }}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "8px 10px",
                    borderRadius: "8px",
                    border: "1px solid",
                    borderColor: isSelected ? "var(--rsl-terracotta, #c85a32)" : "transparent",
                    background: isSelected ? "rgba(200, 90, 50, 0.08)" : "transparent",
                    cursor: "pointer",
                    marginBottom: "3px",
                    transition: "all 0.15s ease",
                    textAlign: "left",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", minWidth: 0 }}>
                    <div
                      style={{
                        width: "22px",
                        height: "22px",
                        borderRadius: "5px",
                        background: isSelected ? "rgba(200, 90, 50, 0.18)" : "#f1f5f9",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "0.75rem",
                        flexShrink: 0,
                        color: isSelected ? "var(--rsl-terracotta, #c85a32)" : "inherit",
                        fontWeight: 700,
                      }}
                    >
                      {s.name.charAt(0)}
                    </div>
                    <span
                      style={{
                        fontWeight: isSelected ? 700 : 500,
                        fontSize: "0.82rem",
                        color: isSelected ? "var(--rsl-terracotta, #c85a32)" : "var(--rsl-text, #191c21)",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {s.name}
                    </span>
                  </div>

                  <span
                    style={{
                      fontSize: "0.72rem",
                      fontWeight: 700,
                      color: isSelected ? "var(--rsl-terracotta, #c85a32)" : "var(--rsl-text-muted, #646b77)",
                    }}
                  >
                    {masteryPct}%
                  </span>
                </button>
              );
            })}
          </div>
        </aside>
      )}

      {/* ── COLUMN 2: ROADMAP FOR SELECTED SKILL ────────────────────────── */}
      {!leftSidebarCollapsed && (
        <aside
          style={{
            borderRight: "1px solid var(--rsl-border, #e8e4de)",
            background: "var(--rsl-surface, #ffffff)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "14px 14px 10px", borderBottom: "1px solid var(--rsl-border, #e8e4de)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
              <span style={{ fontWeight: 800, fontSize: "0.92rem", color: "var(--rsl-text, #191c21)" }}>
                {selectedSkill} Roadmap
              </span>
              <button
                onClick={handleRetryPath}
                title="Refresh Roadmap"
                style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--rsl-text-muted, #646b77)" }}
              >
                <FiRefreshCw size={13} />
              </button>
            </div>
            {/* Progress bar line */}
            <div style={{ height: "4px", background: "#f0ede8", borderRadius: "2px", overflow: "hidden", margin: "6px 0 4px" }}>
              <div
                style={{
                  height: "100%",
                  width: `${Math.round((stats.demonstrated / Math.max(1, stats.total)) * 100)}%`,
                  background: "var(--rsl-terracotta, #c85a32)",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
            <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)" }}>
              {stats.demonstrated}/{stats.total} Mastered ({Math.round((stats.demonstrated / Math.max(1, stats.total)) * 100)}%)
            </div>
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "10px 8px" }}>
            {loadingPath ? (
              <div style={{ padding: "30px 10px", textAlign: "center", color: "var(--rsl-text-muted, #646b77)" }}>
                <FiRefreshCw className="spin-icon" style={{ marginBottom: "8px" }} />
                <div style={{ fontSize: "0.8rem" }}>Generating personalized curriculum...</div>
              </div>
            ) : pathError ? (
              <div role="alert" style={{ padding: "12px", borderRadius: "6px", border: "1px solid #ef4444", background: "rgba(239, 68, 68, 0.05)" }}>
                <div style={{ fontSize: "0.78rem", color: "#ef4444", marginBottom: "8px" }}>{pathError}</div>
                <button
                  onClick={handleRetryPath}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "4px",
                    border: "1px solid #ef4444",
                    background: "transparent",
                    color: "#ef4444",
                    fontSize: "0.74rem",
                    cursor: "pointer",
                  }}
                >
                  Retry
                </button>
              </div>
            ) : (
              skillPath?.stages?.map((stage, sIdx) => {
                const isExpanded = expandedStages[sIdx] !== false;
                const lessons = stage.lessons || [];
                const stageMastered = lessons.filter(
                  (l) => conceptProgress[l.id] === "demonstrated" || l.is_demonstrated
                ).length;

                return (
                  <div key={sIdx} style={{ marginBottom: "8px" }}>
                    {/* Stage Header Accordion Toggle */}
                    <button
                      type="button"
                      onClick={() => toggleStageExpand(sIdx)}
                      style={{
                        width: "100%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "8px 10px",
                        background: "var(--rsl-surface-subtle, #f8f6f2)",
                        border: "1px solid var(--rsl-border, #e8e4de)",
                        borderRadius: "6px",
                        fontSize: "0.78rem",
                        fontWeight: 700,
                        color: "var(--rsl-text, #191c21)",
                        cursor: "pointer",
                        textAlign: "left",
                      }}
                    >
                      <span>
                        {stage.stage_number || sIdx + 1}. {stage.stage_name} ({stageMastered}/{lessons.length})
                      </span>
                      {isExpanded ? <FiChevronUp size={14} /> : <FiChevronDown size={14} />}
                    </button>

                    {/* Stage Lessons */}
                    {isExpanded && (
                      <div style={{ paddingLeft: "4px", marginTop: "4px", display: "flex", flexDirection: "column", gap: "2px" }}>
                        {lessons.map((les, lIdx) => {
                          const title = les.title || les.topic || `Lesson ${lIdx + 1}`;
                          const isSelected = selectedConcept?.id === les.id || selectedConcept?.title === title;
                          const isMastered = conceptProgress[les.id] === "demonstrated" || les.is_demonstrated;

                          return (
                            <button
                              key={lIdx}
                              onClick={() => handleSelectConcept(les, stage.stage_name)}
                              style={{
                                width: "100%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                padding: "7px 10px",
                                borderRadius: "6px",
                                border: "1px solid",
                                borderColor: isSelected ? "var(--rsl-terracotta, #c85a32)" : "transparent",
                                background: isSelected ? "var(--rsl-terracotta-light, #fdf2ed)" : "transparent",
                                color: isSelected ? "var(--rsl-terracotta, #c85a32)" : "var(--rsl-text, #191c21)",
                                fontSize: "0.78rem",
                                fontWeight: isSelected ? 700 : 400,
                                cursor: "pointer",
                                textAlign: "left",
                                transition: "all 0.15s ease",
                              }}
                            >
                              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                {lIdx + 1}. {title.replace(/^[^•]*•\s*/, "")}
                              </span>

                              {isMastered ? (
                                <FiCheck size={14} color="#10b981" />
                              ) : isSelected ? (
                                <div style={{ width: "12px", height: "12px", borderRadius: "50%", border: "2px solid #c85a32", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                  <div style={{ width: "4px", height: "4px", borderRadius: "50%", background: "#c85a32" }} />
                                </div>
                              ) : (
                                <span style={{ width: "10px", height: "10px", borderRadius: "50%", border: "1px solid #b8bfc9" }} />
                              )}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </aside>
      )}

      {/* ── COLUMN 3: CENTER LESSON WORKSPACE ───────────────────────────── */}
        <main
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: "var(--cv-surface, #ffffff)",
          }}
        >
          {loadingLesson ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px" }}>
              <FiRefreshCw className="spin-icon" size={24} style={{ color: "var(--cv-accent, #6366f1)", marginBottom: "12px" }} />
              <div style={{ fontSize: "0.92rem", fontWeight: 600, color: "var(--cv-text, #1c1c1e)" }}>
                Loading lesson for {selectedSkill}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--cv-text-muted, #71717a)", marginTop: "4px" }}>
                {selectedConcept?.title || selectedConcept?.topic}
              </div>
            </div>
          ) : lessonError ? (
            <div style={{ padding: "40px", textAlign: "center" }}>
              <div style={{ color: "#ef4444", fontSize: "0.88rem", marginBottom: "12px" }}>{lessonError}</div>
              <button
                onClick={handleRetryLesson}
                style={{
                  padding: "6px 14px",
                  borderRadius: "6px",
                  border: "1px solid #ef4444",
                  background: "transparent",
                  color: "#ef4444",
                  cursor: "pointer",
                }}
              >
                Retry Lesson
              </button>
            </div>
          ) : selectedConcept ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
              {/* Workspace Header */}
              <div style={{ padding: "16px 28px 14px", borderBottom: "1px solid var(--cv-border, #e5e2d9)", background: "#ffffff" }}>
                {/* Breadcrumbs & Pagination Top Bar */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ fontSize: "0.78rem", color: "var(--cv-text-muted, #71717a)", display: "flex", alignItems: "center", gap: "6px" }}>
                    <span>🏠</span> <span>&gt;</span>
                    <span>{selectedSkill}</span> <span>&gt;</span>
                    <span>{selectedConcept.stage || "Foundations"}</span> <span>&gt;</span>
                    <strong style={{ color: "var(--rsl-terracotta, #c85a32)" }}>
                      {selectedConcept.title?.replace(/^[^•]*•\s*/, "")}
                    </strong>
                  </div>

                  {/* Top Pagination & Save */}
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    {currentIndex >= 0 && allLessonsList.length > 0 && (
                      <span style={{ fontSize: "0.78rem", color: "var(--cv-text-muted, #71717a)", fontWeight: 600 }}>
                        Lesson {currentIndex + 1} of {allLessonsList.length}
                      </span>
                    )}
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <button
                        type="button"
                        aria-label="Previous Lesson Arrow"
                        disabled={!prevLesson}
                        onClick={() => prevLesson && handleSelectConcept(prevLesson, prevLesson.stage_name)}
                        style={{
                          padding: "3px 8px",
                          borderRadius: "4px",
                          border: "1px solid var(--cv-border, #e5e2d9)",
                          background: "#ffffff",
                          cursor: prevLesson ? "pointer" : "not-allowed",
                          opacity: prevLesson ? 1 : 0.4,
                          fontSize: "0.75rem",
                          fontWeight: 700,
                        }}
                      >
                        &lt;
                      </button>
                      <button
                        type="button"
                        aria-label="Next Lesson Arrow"
                        disabled={!nextLesson}
                        onClick={() => nextLesson && handleSelectConcept(nextLesson, nextLesson.stage_name)}
                        style={{
                          padding: "3px 8px",
                          borderRadius: "4px",
                          border: "1px solid var(--cv-border, #e5e2d9)",
                          background: "#ffffff",
                          cursor: nextLesson ? "pointer" : "not-allowed",
                          opacity: nextLesson ? 1 : 0.4,
                          fontSize: "0.75rem",
                          fontWeight: 700,
                        }}
                      >
                        &gt;
                      </button>
                    </div>

                    <button
                      type="button"
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "4px",
                        padding: "4px 10px",
                        borderRadius: "6px",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        background: "#ffffff",
                        fontSize: "0.75rem",
                        fontWeight: 600,
                        color: "var(--cv-text, #1c1c1e)",
                        cursor: "pointer",
                      }}
                    >
                      <FiBookmark size={12} /> Save
                    </button>
                  </div>
                </div>

                {/* Lesson Title in Editorial Serif */}
                <h1 style={{
                  fontSize: "1.75rem",
                  fontFamily: "var(--rsl-font-serif, Georgia, serif)",
                  fontWeight: 800,
                  margin: "4px 0 6px 0",
                  color: "var(--cv-text, #1c1c1e)",
                  lineHeight: 1.25,
                }}>
                  {lesson?.title || selectedConcept.title}
                </h1>

                {/* Subtitle / Short description */}
                <p style={{ fontSize: "0.92rem", color: "var(--cv-text-muted, #52525b)", margin: "0 0 12px 0", lineHeight: 1.5 }}>
                  {lesson?.concept_summary || lesson?.what_it_is || "Understand core syntax, runtime models, and memory architectures."}
                </p>

                {/* Meta Chips */}
                <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
                  <span
                    style={{
                      padding: "3px 10px",
                      borderRadius: "14px",
                      fontSize: "0.74rem",
                      fontWeight: 700,
                      background: "rgba(200, 90, 50, 0.1)",
                      color: "var(--rsl-terracotta, #c85a32)",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <FiHelpCircle size={12} /> {lesson?.difficulty || "Intermediate"}
                  </span>
                  <span
                    style={{
                      padding: "3px 10px",
                      borderRadius: "14px",
                      fontSize: "0.74rem",
                      fontWeight: 600,
                      background: "#f1f5f9",
                      color: "#64748b",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <FiClock size={12} /> {lesson?.duration || "18 min read"}
                  </span>
                  <span
                    style={{
                      padding: "3px 10px",
                      borderRadius: "14px",
                      fontSize: "0.74rem",
                      fontWeight: 600,
                      background: "rgba(16, 185, 129, 0.08)",
                      color: "#059669",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <FiCompass size={12} /> {lesson?.why_matters_for_role || "Personalized for your frontend projects and React experience"}
                  </span>
                </div>

                {/* Documentation Section Navigation Quick Jumps */}
                <div style={{ display: "flex", alignItems: "center", gap: "6px", overflowX: "auto", paddingBottom: "2px" }}>
                  <span style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--cv-text-muted, #71717a)", display: "flex", alignItems: "center", marginRight: "4px" }}>
                    Jump to:
                  </span>
                  {[
                    { id: "section-overview", tab: "overview", label: "Overview", ariaLabel: "Learn Overview", icon: <FiBookOpen size={13} /> },
                    { id: "section-diagram", tab: "diagram", label: "Architecture Diagram", ariaLabel: "Architecture Diagram", icon: <FiLayers size={13} /> },
                    { id: "section-code", tab: "code", label: "Code & Runtime", ariaLabel: "Code & Runtime Flow", icon: <FiTerminal size={13} /> },
                    { id: "section-debugging", tab: "debugging", label: "Pitfalls & Debugging", ariaLabel: "Pitfalls & Debugging", icon: <FiAlertTriangle size={13} /> },
                    { id: "section-exercise", tab: "exercise", label: "Practice Challenge", ariaLabel: "Practice Exercise", icon: <FiCode size={13} /> },
                    { id: "section-check", tab: "check", label: "Knowledge Check", ariaLabel: "Socratic Check", icon: <FiSparkles size={13} /> },
                    { id: "section-resources", tab: "resources", label: "Verified Sources", ariaLabel: "Verified Resources", icon: <FiExternalLink size={13} /> },
                  ].map((tab) => {
                    const isActive = activeLessonTab === tab.tab;
                    return (
                      <button
                        key={tab.id}
                        type="button"
                        aria-label={tab.ariaLabel}
                        onClick={() => {
                          setActiveLessonTab(tab.tab);
                          const el = document.getElementById(tab.id);
                          if (el && typeof el.scrollIntoView === "function") {
                            el.scrollIntoView({ behavior: "smooth", block: "start" });
                          }
                        }}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "5px",
                          padding: "4px 10px",
                          borderRadius: "16px",
                          fontSize: "0.74rem",
                          fontWeight: isActive ? 700 : 500,
                          border: "1px solid",
                          borderColor: isActive ? "var(--rsl-terracotta, #c85a32)" : "var(--cv-border, #e5e2d9)",
                          background: isActive ? "rgba(200, 90, 50, 0.1)" : "transparent",
                          color: isActive ? "var(--rsl-terracotta, #c85a32)" : "var(--cv-text, #1c1c1e)",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {tab.icon} {tab.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Lesson Workspace Content — Unified Documentation Article */}
              <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px" }}>
                <article style={{ maxWidth: "860px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "28px" }}>
                  
                  {/* Callout: Learning Objectives & Prerequisites */}
                  <div
                    style={{
                      background: "rgba(99, 102, 241, 0.04)",
                      border: "1px solid rgba(99, 102, 241, 0.2)",
                      borderRadius: "10px",
                      padding: "16px 20px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--cv-accent, #6366f1)", fontWeight: 700, fontSize: "0.9rem", marginBottom: "10px" }}>
                      <FiShield size={16} /> Learning Objectives & Key Invariants
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "8px" }}>
                      {learnBullets.map((bullet, bIdx) => (
                        <li key={bIdx} style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.86rem", lineHeight: 1.5, color: "var(--cv-text, #1c1c1e)" }}>
                          <FiCheck size={15} color="#10b981" style={{ flexShrink: 0, marginTop: "3px" }} />
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>

                    {lesson?.prerequisites && lesson.prerequisites.length > 0 && (
                      <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px solid rgba(99, 102, 241, 0.15)", display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                        <span style={{ fontSize: "0.76rem", fontWeight: 700, color: "var(--cv-text-muted, #71717a)" }}>Prerequisites:</span>
                        {lesson.prerequisites.map((p, pIdx) => (
                          <span key={pIdx} style={{ fontSize: "0.72rem", padding: "2px 8px", background: "rgba(99, 102, 241, 0.08)", borderRadius: "12px", color: "var(--cv-accent, #6366f1)", fontWeight: 600 }}>
                            {p}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* ── SECTION 1: CONCEPT EXPLANATION & MENTAL MODELS ────────── */}
                  <section id="section-overview" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="rsl-step-num">1</span> 1. The Mental Model ({lesson?.topic?.replace(/^[^•]*•\s*/, "") || selectedSkill})
                    </h2>

                    {lesson?.intuition && (
                      <div
                        style={{
                          background: "#fff7ed",
                          border: "1px solid #ffedd5",
                          borderRadius: "10px",
                          padding: "14px 18px",
                          marginBottom: "14px",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--rsl-terracotta, #c85a32)", fontWeight: 700, fontSize: "0.85rem", marginBottom: "6px" }}>
                          <FiCompass size={16} /> Building Intuition & Mental Model
                        </div>
                        <p style={{ margin: 0, fontSize: "0.88rem", lineHeight: 1.65, color: "#7c2d12" }}>
                          {lesson.intuition}
                        </p>
                      </div>
                    )}
                    
                    <p style={{ fontSize: "0.95rem", lineHeight: 1.65, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)" }}>
                      {lesson?.what_it_is || lesson?.concept_summary || "Explore the core syntax, memory representation, and idiomatic use cases."}
                    </p>

                    {/* Inline Visual Architecture Diagram for Closures */}
                    {selectedSkill?.toLowerCase()?.includes("javascript") && (lesson?.topic?.toLowerCase()?.includes("closure") || selectedConcept?.title?.toLowerCase()?.includes("closure")) && (
                      <div style={{
                        background: "#fcfaf7",
                        border: "1px solid #ede7df",
                        borderRadius: "12px",
                        padding: "18px 20px",
                        margin: "16px 0",
                      }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
                          <div style={{
                            flex: "0 0 210px",
                            background: "#fff7ed",
                            border: "1px solid #ffedd5",
                            borderRadius: "10px",
                            padding: "12px 14px",
                          }}>
                            <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px" }}>
                              <FiLightbulb size={14} /> Key idea
                            </div>
                            <div style={{ fontSize: "0.8rem", lineHeight: 1.5, color: "#7c2d12" }}>
                              The inner function "remembers" the variables from its outer scope, forming a closure.
                            </div>
                          </div>

                          <div style={{ flex: 1, minWidth: "280px", display: "flex", alignItems: "center", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
                            <div style={{
                              background: "#ffffff",
                              border: "1px solid #fed7aa",
                              borderRadius: "8px",
                              padding: "10px 14px",
                              boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
                            }}>
                              <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", marginBottom: "4px" }}>
                                Outer scope (createCounter)
                              </div>
                              <div style={{ fontFamily: "var(--cv-font-mono, monospace)", fontSize: "0.78rem", color: "#334155", lineHeight: 1.5 }}>
                                <div>let count = 0;</div>
                                <div>return increment;</div>
                              </div>
                            </div>

                            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", color: "#94a3b8", fontSize: "0.7rem", fontWeight: 600 }}>
                              <span>returns</span>
                              <span style={{ fontSize: "1.1rem" }}>→</span>
                            </div>

                            <div style={{
                              background: "#ffffff",
                              border: "1px solid #c7d2fe",
                              borderRadius: "8px",
                              padding: "10px 14px",
                              boxShadow: "0 2px 6px rgba(0,0,0,0.02)",
                            }}>
                              <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "#4f46e5", marginBottom: "4px" }}>
                                Closure (increment)
                              </div>
                              <div style={{ fontFamily: "var(--cv-font-mono, monospace)", fontSize: "0.78rem", color: "#334155", lineHeight: 1.5 }}>
                                <div>increment() &#123; count++; &#125;</div>
                                <div style={{ color: "#64748b", fontSize: "0.72rem" }}>has access to count</div>
                              </div>
                            </div>

                            <div style={{ fontSize: "1.1rem", color: "#94a3b8" }}>→</div>

                            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                              <div style={{ padding: "3px 8px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.25)", borderRadius: "4px", fontSize: "0.72rem", fontWeight: 600, color: "#065f46", fontFamily: "var(--cv-font-mono, monospace)" }}>
                                increment() → 1
                              </div>
                              <div style={{ padding: "3px 8px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.25)", borderRadius: "4px", fontSize: "0.72rem", fontWeight: 600, color: "#065f46", fontFamily: "var(--cv-font-mono, monospace)" }}>
                                increment() → 2
                              </div>
                              <div style={{ padding: "3px 8px", background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.25)", borderRadius: "4px", fontSize: "0.72rem", fontWeight: 600, color: "#065f46", fontFamily: "var(--cv-font-mono, monospace)" }}>
                                increment() → 3
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {lesson?.why_it_exists && (
                      <div style={{ background: "var(--cv-surface, #ffffff)", borderLeft: "3px solid var(--rsl-terracotta, #c85a32)", padding: "10px 14px", margin: "14px 0", borderRadius: "0 6px 6px 0", fontSize: "0.88rem", lineHeight: 1.55 }}>
                        <strong style={{ color: "var(--rsl-terracotta, #c85a32)" }}>Why it exists: </strong>
                        {lesson.why_it_exists}
                      </div>
                    )}

                    {lesson?.detailed_explanation && (
                      <div
                        className="teaching-markdown-content"
                        dangerouslySetInnerHTML={{ __html: marked.parse(lesson.detailed_explanation) }}
                        style={{ fontSize: "0.9rem", lineHeight: 1.7, marginTop: "12px" }}
                      />
                    )}

                    {lesson?.terminology_and_mental_models && (
                      <div style={{ marginTop: "16px", padding: "14px 16px", background: "#f8fafc", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "8px" }}>
                        <div style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", color: "var(--rsl-terracotta, #c85a32)", marginBottom: "6px" }}>
                          Core Terminology & Mental Models
                        </div>
                        <div
                          className="teaching-markdown-content"
                          dangerouslySetInnerHTML={{ __html: marked.parse(lesson.terminology_and_mental_models) }}
                          style={{ fontSize: "0.85rem", lineHeight: 1.6 }}
                        />
                      </div>
                    )}
                  </section>

                  {/* ── SECTION: VISUAL ARCHITECTURE & FLOWCHART ────────────── */}
                  <section id="section-diagram" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 12px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <FiLayers size={18} color="var(--rsl-terracotta, #c85a32)" /> Visual Architecture & Flowchart Walkthrough
                    </h2>
                    <p style={{ fontSize: "0.86rem", lineHeight: 1.6, color: "var(--cv-text-muted, #71717a)", margin: "0 0 12px 0" }}>
                      Trace the execution lifecycle, state transitions, and boundary contracts for {lesson?.topic || selectedConcept.title}.
                    </p>

                    {/* Diagram Terminal Box */}
                    <div
                      style={{
                        background: "#0b0f19",
                        border: "1px solid #1e293b",
                        borderRadius: "10px",
                        padding: "16px 18px",
                        overflowX: "auto",
                        boxShadow: "0 4px 14px rgba(0,0,0,0.08)",
                        marginBottom: "12px",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px", borderBottom: "1px solid #1e293b", paddingBottom: "8px" }}>
                        <span style={{ fontSize: "0.74rem", fontWeight: 700, color: "#38bdf8", display: "flex", alignItems: "center", gap: "6px" }}>
                          <FiLayers size={13} /> Architecture Blueprint & State Transition Flow
                        </span>
                        <span style={{ fontSize: "0.7rem", color: "#64748b" }}>ASCII / Structural Flow</span>
                      </div>

                      <pre
                        style={{
                          margin: 0,
                          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                          fontSize: "0.82rem",
                          lineHeight: 1.45,
                          color: "#38bdf8",
                          whiteSpace: "pre",
                        }}
                      >
                        {lesson?.mental_model_diagram || (
                          `┌──────────────────────────────────────────────┐\n` +
                          `│ Input Scope: ${lesson?.topic || selectedSkill} │\n` +
                          `└──────────────────────┬───────────────────────┘\n` +
                          `                       │ 1. Parameter validation & contract check\n` +
                          `                       ▼\n` +
                          `┌──────────────────────────────────────────────┐\n` +
                          `│ Runtime Execution Engine & State Transitions │\n` +
                          `└──────────────────────┬───────────────────────┘\n` +
                          `                       │ 2. Deterministic result generation\n` +
                          `                       ▼\n` +
                          `┌──────────────────────────────────────────────┐\n` +
                          `│ Output Commit & Verified Resource Release    │\n` +
                          `└──────────────────────────────────────────────┘`
                        )}
                      </pre>
                    </div>

                    {/* Diagram Node Explanations */}
                    {lesson?.diagram_explanation && (
                      <div style={{ padding: "14px 16px", background: "var(--cv-surface, #ffffff)", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "8px" }}>
                        <div style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", color: "var(--rsl-terracotta, #c85a32)", marginBottom: "8px" }}>
                          Step-by-Step Flow & Node Explanations
                        </div>
                        <div
                          className="teaching-markdown-content"
                          dangerouslySetInnerHTML={{ __html: marked.parse(lesson.diagram_explanation) }}
                          style={{ fontSize: "0.84rem", lineHeight: 1.65 }}
                        />
                      </div>
                    )}
                  </section>

                  {/* ── SECTION 2: WORKED EXAMPLE & IMPLEMENTATION ──────────── */}
                  <section id="section-code" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="rsl-step-num">2</span> 2. See it in Code (Worked Example)
                    </h2>

                    {(lesson?.time_complexity || lesson?.space_complexity) && (
                      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "12px" }}>
                        {lesson?.time_complexity && (
                          <div style={{ padding: "4px 10px", borderRadius: "6px", background: "rgba(200, 90, 50, 0.08)", border: "1px solid rgba(200, 90, 50, 0.2)", fontSize: "0.78rem", color: "var(--cv-text, #1c1c1e)" }}>
                            <strong style={{ color: "var(--rsl-terracotta, #c85a32)" }}>Time: </strong> {lesson.time_complexity}
                          </div>
                        )}
                        {lesson?.space_complexity && (
                          <div style={{ padding: "4px 10px", borderRadius: "6px", background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.2)", fontSize: "0.78rem", color: "var(--cv-text, #1c1c1e)" }}>
                            <strong style={{ color: "#10b981" }}>Space: </strong> {lesson.space_complexity}
                          </div>
                        )}
                      </div>
                    )}

                    <div style={{ display: "flex", gap: "14px", flexWrap: "wrap", alignItems: "flex-start", marginBottom: "12px" }}>
                      <div
                        style={{
                          flex: "1 1 500px",
                          background: "#0f172a",
                          borderRadius: "10px",
                          border: "1px solid #1e293b",
                          overflow: "hidden",
                          boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "10px 16px",
                            background: "#1e293b",
                            borderBottom: "1px solid #334155",
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#e2e8f0", fontSize: "0.8rem", fontWeight: 600 }}>
                            <FiCode size={14} color="#60a5fa" />
                            <span>Implementation: {lesson?.topic || selectedConcept.title}</span>
                          </div>

                          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                            <button
                              type="button"
                              onClick={() => {
                                navigator?.clipboard?.writeText(lesson?.starter_code || "");
                              }}
                              style={{
                                padding: "4px 8px",
                                borderRadius: "4px",
                                fontSize: "0.72rem",
                                background: "rgba(255,255,255,0.08)",
                                color: "#cbd5e1",
                                border: "1px solid rgba(255,255,255,0.15)",
                                cursor: "pointer",
                              }}
                            >
                              Copy Code
                            </button>

                            <button
                              type="button"
                              onClick={handleRunCode}
                              disabled={codeRunning}
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "5px",
                                padding: "4px 12px",
                                borderRadius: "4px",
                                fontSize: "0.75rem",
                                fontWeight: 700,
                                background: "var(--rsl-terracotta, #c85a32)",
                                color: "#ffffff",
                                border: "none",
                                cursor: codeRunning ? "not-allowed" : "pointer",
                              }}
                            >
                              <FiPlay size={12} /> {codeRunning ? "Running..." : "Run ▶"}
                            </button>
                          </div>
                        </div>

                        {/* Code with line numbers */}
                        <div style={{ padding: "14px 16px", overflowX: "auto" }}>
                          <pre style={{ margin: 0, padding: 0 }}>
                            {codeLines.map((line, idx) => (
                              <div key={idx} style={{ display: "flex", gap: "14px", lineHeight: "1.6" }}>
                                <span style={{ width: "24px", textAlign: "right", color: "#64748b", userSelect: "none", fontSize: "0.78rem" }}>
                                  {idx + 1}
                                </span>
                                <span style={{ flex: 1, fontFamily: "var(--cv-font-mono, monospace)", fontSize: "0.82rem", color: "#f8fafc" }}>
                                  {line}
                                </span>
                              </div>
                            ))}
                          </pre>
                        </div>

                        {/* Expected output box */}
                        {codeOutputVisible && lesson?.expected_output && (
                          <div
                            style={{
                              padding: "10px 16px",
                              background: "#090d16",
                              borderTop: "1px solid #1e293b",
                            }}
                          >
                            <div style={{ fontSize: "0.7rem", textTransform: "uppercase", color: "#94a3b8", fontWeight: 700, marginBottom: "4px" }}>
                              Output
                            </div>
                            <pre style={{ margin: 0, fontFamily: "var(--cv-font-mono, monospace)", fontSize: "0.8rem", color: "#38bdf8", whiteSpace: "pre-wrap" }}>
                              {lesson.expected_output}
                            </pre>
                          </div>
                        )}
                      </div>

                      {/* Try it callout on side */}
                      <div style={{
                        flex: "0 0 220px",
                        background: "#fff7ed",
                        border: "1px solid #ffedd5",
                        borderRadius: "10px",
                        padding: "14px",
                        alignSelf: "stretch",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "center",
                      }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", marginBottom: "6px" }}>
                          &gt;_ Try it:
                        </div>
                        <div style={{ fontSize: "0.82rem", lineHeight: 1.5, color: "#7c2d12" }}>
                          Predict what the function returns on sequential calls or state mutations.
                        </div>
                      </div>
                    </div>

                    {/* Line-by-Line Explanation Accordion */}
                    <div
                      style={{
                        background: "var(--cv-card-bg, #ffffff)",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        borderRadius: "8px",
                        marginTop: "12px",
                        overflow: "hidden",
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => setExplanationExpanded(!explanationExpanded)}
                        style={{
                          width: "100%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "10px 14px",
                          background: "transparent",
                          border: "none",
                          fontSize: "0.84rem",
                          fontWeight: 700,
                          color: "var(--cv-text, #1c1c1e)",
                          cursor: "pointer",
                          textAlign: "left",
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                          <FiTerminal size={14} color="var(--rsl-terracotta, #c85a32)" /> Line-by-Line Technical Explanation
                        </span>
                        {explanationExpanded ? <FiChevronUp size={15} /> : <FiChevronDown size={15} />}
                      </button>

                      {explanationExpanded && (
                        <div style={{ padding: "0 14px 12px", borderTop: "1px solid var(--cv-border, #e5e2d9)", paddingTop: "8px" }}>
                          {lesson?.code_walkthrough ? (
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.code_walkthrough) }}
                              style={{ fontSize: "0.83rem", lineHeight: 1.6 }}
                            />
                          ) : (
                            <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "0.83rem", lineHeight: 1.6, color: "var(--cv-text, #1c1c1e)" }}>
                              {codeLines.filter((l) => l.trim().length > 0).slice(0, 6).map((line, idx) => (
                                <li key={idx} style={{ marginBottom: "4px" }}>
                                  <code>{line.trim()}</code>: Demonstrates execution semantics for {lesson?.topic || selectedSkill}.
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      )}
                    </div>
                  </section>

                  {/* ── SECTION 3: HOW IT WORKS & EXECUTION TRACE ───────────── */}
                  <section style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="rsl-step-num">3</span> 3. Trace the Execution (Step-by-Step Flow)
                    </h2>

                    {lesson?.step_by_step && (
                      <div style={{ marginBottom: "16px", padding: "12px 16px", background: "#fcfaf7", border: "1px solid #ede7df", borderRadius: "8px" }}>
                        <div
                          className="teaching-markdown-content"
                          dangerouslySetInnerHTML={{ __html: marked.parse(lesson.step_by_step) }}
                          style={{ fontSize: "0.86rem", lineHeight: 1.65 }}
                        />
                      </div>
                    )}

                    {/* Execution Trace Table */}
                    {lesson?.execution_trace_table && lesson.execution_trace_table.length > 0 && (
                      <div style={{ overflowX: "auto", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "8px", background: "#ffffff", marginBottom: "16px" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem", textAlign: "left" }}>
                          <thead>
                            <tr style={{ background: "#f8fafc", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
                              <th style={{ padding: "10px 14px", fontWeight: 700, width: "60px", color: "var(--cv-text, #1c1c1e)" }}>Step</th>
                              <th style={{ padding: "10px 14px", fontWeight: 700, color: "var(--cv-text, #1c1c1e)" }}>Call / Action</th>
                              <th style={{ padding: "10px 14px", fontWeight: 700, color: "var(--cv-text, #1c1c1e)" }}>Variable Environment</th>
                              <th style={{ padding: "10px 14px", fontWeight: 700, color: "var(--cv-text, #1c1c1e)" }}>Returned Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {lesson.execution_trace_table.map((row, rIdx) => (
                              <tr key={rIdx} style={{ borderBottom: rIdx < lesson.execution_trace_table.length - 1 ? "1px solid #f1f5f9" : "none" }}>
                                <td style={{ padding: "10px 14px", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)" }}>{row.step || rIdx + 1}</td>
                                <td style={{ padding: "10px 14px", fontFamily: "var(--cv-font-mono, monospace)" }}>{row.call_action || row.action}</td>
                                <td style={{ padding: "10px 14px", fontFamily: "var(--cv-font-mono, monospace)", color: "#0284c7" }}>{row.variable_env || row.environment}</td>
                                <td style={{ padding: "10px 14px", fontFamily: "var(--cv-font-mono, monospace)", fontWeight: 600 }}>{row.returned_value || row.result}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>

                  {/* ── SECTION 4: WHY DEVELOPERS USE THIS / PRACTICAL USE CASES */}
                  <section style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="rsl-step-num">4</span> 4. Why Developers Use This (Practical Applications)
                    </h2>

                    {/* 3-card use-cases grid */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px", marginBottom: "14px" }}>
                      <div style={{ padding: "14px", borderRadius: "8px", border: "1px solid var(--cv-border, #e5e2d9)", background: "#ffffff" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, fontSize: "0.85rem", color: "var(--rsl-terracotta, #c85a32)", marginBottom: "6px" }}>
                          <FiLock size={14} /> Private state
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "var(--cv-text-muted, #71717a)", lineHeight: 1.5 }}>
                          Keep data hidden and controlled (e.g., counters, configuration, encapsulation).
                        </div>
                      </div>

                      <div style={{ padding: "14px", borderRadius: "8px", border: "1px solid var(--cv-border, #e5e2d9)", background: "#ffffff" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, fontSize: "0.85rem", color: "var(--rsl-terracotta, #c85a32)", marginBottom: "6px" }}>
                          <FiZap size={14} /> Event handlers
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "var(--cv-text-muted, #71717a)", lineHeight: 1.5 }}>
                          Preserve context and state across asynchronous events and UI callbacks.
                        </div>
                      </div>

                      <div style={{ padding: "14px", borderRadius: "8px", border: "1px solid var(--cv-border, #e5e2d9)", background: "#ffffff" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontWeight: 700, fontSize: "0.85rem", color: "var(--rsl-terracotta, #c85a32)", marginBottom: "6px" }}>
                          <FiLayers size={14} /> Memoization & Hooks
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "var(--cv-text-muted, #71717a)", lineHeight: 1.5 }}>
                          Remember previous results to avoid recomputation and power stateful React hooks.
                        </div>
                      </div>
                    </div>

                    <div
                      style={{
                        background: "rgba(16, 185, 129, 0.04)",
                        border: "1px solid rgba(16, 185, 129, 0.2)",
                        borderRadius: "10px",
                        padding: "16px 18px",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#10b981", fontWeight: 700, fontSize: "0.88rem", marginBottom: "8px" }}>
                        <FiLightbulb size={16} /> Engineering Use Cases
                      </div>
                      {lesson?.real_world_applications ? (
                        <div
                          className="teaching-markdown-content"
                          dangerouslySetInnerHTML={{ __html: marked.parse(lesson.real_world_applications) }}
                          style={{ fontSize: "0.86rem", lineHeight: 1.6, color: "var(--cv-text, #1c1c1e)" }}
                        />
                      ) : (
                        <p style={{ margin: 0, fontSize: "0.86rem", lineHeight: 1.6, color: "var(--cv-text, #1c1c1e)" }}>
                          In production systems, {lesson?.topic || selectedConcept?.title || selectedSkill} is essential for building scalable, reliable, and maintainable services.
                        </p>
                      )}

                      {lesson?.why_matters_for_role && (
                        <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px solid rgba(16, 185, 129, 0.15)", fontSize: "0.82rem", color: "var(--cv-text-muted, #71717a)" }}>
                          <strong>Why it matters for your role: </strong> {lesson.why_matters_for_role}
                        </div>
                      )}
                    </div>
                  </section>

                  {/* ── SECTION 5: COMMON PITFALLS & DEBUGGING ─────────────── */}
                  <section id="section-debugging" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: "0 0 14px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", display: "flex", alignItems: "center", gap: "8px" }}>
                      <span className="rsl-step-num">5</span> 5. Common Mistakes & Pitfalls
                    </h2>

                    <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                      <div
                        style={{
                          background: "#fff7ed",
                          border: "1px solid #fed7aa",
                          borderRadius: "10px",
                          padding: "16px 18px",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--rsl-terracotta, #c85a32)", fontWeight: 700, fontSize: "0.88rem", marginBottom: "8px" }}>
                          <FiAlertTriangle size={16} /> Common Pitfalls
                        </div>
                        {lesson?.common_mistakes ? (
                          <div
                            className="teaching-markdown-content"
                            dangerouslySetInnerHTML={{ __html: marked.parse(lesson.common_mistakes) }}
                            style={{ fontSize: "0.84rem", lineHeight: 1.6, color: "var(--cv-text, #1c1c1e)" }}
                          />
                        ) : (
                          <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "0.84rem", lineHeight: 1.6, color: "var(--cv-text, #1c1c1e)" }}>
                            <li>Violating type contracts or input schemas for {lesson?.topic || selectedSkill}.</li>
                            <li>Unintended side-effects or improper lifecycle mutations.</li>
                            <li>Failing to handle upstream error responses or boundary conditions.</li>
                          </ul>
                        )}
                      </div>

                      {lesson?.debugging_tips && (
                        <div style={{ background: "#f8fafc", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "8px", padding: "14px 16px" }}>
                          <h4 style={{ margin: "0 0 6px 0", color: "var(--cv-accent, #6366f1)", fontSize: "0.86rem" }}>
                            Debugging Invariants & Tips
                          </h4>
                          <div
                            className="teaching-markdown-content"
                            dangerouslySetInnerHTML={{ __html: marked.parse(lesson.debugging_tips) }}
                            style={{ fontSize: "0.84rem", lineHeight: 1.6 }}
                          />
                        </div>
                      )}

                      {lesson?.edge_cases_and_limitations && (
                        <div style={{ background: "#fffbeb", border: "1px solid #fef3c7", borderRadius: "8px", padding: "12px 16px", fontSize: "0.82rem", color: "#92400e" }}>
                          <strong>Edge Cases & Limitations: </strong>
                          {lesson.edge_cases_and_limitations}
                        </div>
                      )}
                    </div>
                  </section>

                  {/* ── SECTION 5: GUIDED PRACTICE CHALLENGE ───────────────── */}
                  <section id="section-exercise" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 800, margin: "0 0 12px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", borderBottom: "1px solid var(--cv-border, #e5e2d9)", paddingBottom: "8px" }}>
                      Practice Exercises & Guided Challenge
                    </h2>

                    {(lesson?.practice_exercises?.length ? lesson.practice_exercises : [
                      {
                        title: `${lesson?.topic || selectedConcept?.title || selectedSkill} Practice Challenge`,
                        difficulty: "Intermediate",
                        problem_statement: `Implement an idiomatic pattern demonstrating ${lesson?.topic || selectedConcept?.title || selectedSkill}. Ensure your solution adheres to proper conventions and error handling.`,
                        given_inputs: `Valid ${lesson?.topic || selectedConcept?.title || selectedSkill} inputs`,
                        expected_output: "Deterministic and verified output",
                        constraints: `Must use idiomatic ${selectedSkill} syntax.`,
                        starter_code: lesson?.starter_code || `// Implement ${lesson?.topic || selectedConcept?.title || selectedSkill} here\n`,
                      }
                    ]).map((ex, exIdx) => (
                      <div
                        key={exIdx}
                        style={{
                          background: "var(--cv-card-bg, #ffffff)",
                          border: "1px solid var(--cv-border, #e5e2d9)",
                          borderRadius: "10px",
                          padding: "20px",
                          marginBottom: "16px",
                          boxShadow: "0 1px 4px rgba(0,0,0,0.02)",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                          <h4 style={{ margin: 0, fontSize: "1rem", fontWeight: 700, color: "var(--cv-text, #1c1c1e)" }}>
                            {ex.title || `Exercise ${exIdx + 1}`}
                          </h4>
                          {ex.difficulty && (
                            <span
                              style={{
                                padding: "2px 8px",
                                borderRadius: "10px",
                                fontSize: "0.72rem",
                                fontWeight: 700,
                                background: "rgba(16, 185, 129, 0.12)",
                                color: "#10b981",
                              }}
                            >
                              {ex.difficulty}
                            </span>
                          )}
                        </div>

                        {/* Problem Statement */}
                        <div style={{ marginBottom: "12px" }}>
                          <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "4px" }}>
                            Problem
                          </div>
                          <p style={{ margin: 0, fontSize: "0.88rem", lineHeight: 1.55, color: "var(--cv-text, #1c1c1e)" }}>
                            {ex.problem_statement || ex.prompt}
                          </p>
                        </div>

                        {/* Given Inputs */}
                        {ex.given_inputs !== undefined && (
                          <div style={{ marginBottom: "10px" }}>
                            <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "4px" }}>
                              Given Inputs
                            </div>
                            <pre style={{ margin: 0, padding: "8px 12px", background: "#f8fafc", borderRadius: "6px", fontSize: "0.82rem", border: "1px solid var(--cv-border, #e5e2d9)" }}>
                              {typeof ex.given_inputs === "string" ? ex.given_inputs : JSON.stringify(ex.given_inputs)}
                            </pre>
                          </div>
                        )}

                        {/* Expected Output */}
                        {ex.expected_output !== undefined && (
                          <div style={{ marginBottom: "10px" }}>
                            <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "4px" }}>
                              Expected Output
                            </div>
                            <pre style={{ margin: 0, padding: "8px 12px", background: "#f8fafc", borderRadius: "6px", fontSize: "0.82rem", border: "1px solid var(--cv-border, #e5e2d9)" }}>
                              {typeof ex.expected_output === "string" ? ex.expected_output : JSON.stringify(ex.expected_output)}
                            </pre>
                          </div>
                        )}

                        {/* Constraints */}
                        {ex.constraints && (
                          <div style={{ marginBottom: "12px" }}>
                            <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "4px" }}>
                              Constraints
                            </div>
                            <div style={{ fontSize: "0.84rem", color: "var(--cv-text, #1c1c1e)" }}>
                              {typeof ex.constraints === "string" ? ex.constraints : JSON.stringify(ex.constraints)}
                            </div>
                          </div>
                        )}

                        {/* Starter Code */}
                        {ex.starter_code && (
                          <div style={{ marginBottom: "12px" }}>
                            <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "4px" }}>
                              Starter Code
                            </div>
                            <pre style={{ margin: 0, padding: "10px 14px", background: "#1e1e1e", color: "#d4d4d4", borderRadius: "6px", fontSize: "0.82rem", overflowX: "auto" }}>
                              {ex.starter_code}
                            </pre>
                          </div>
                        )}

                        {/* Solution Input Area */}
                        <div style={{ marginTop: "14px" }}>
                          <textarea
                            placeholder="Write your solution..."
                            value={exerciseAnswers[exIdx] || ""}
                            onChange={(e) =>
                              setExerciseAnswers((prev) => ({ ...prev, [exIdx]: e.target.value }))
                            }
                            rows={4}
                            style={{
                              width: "100%",
                              padding: "10px 12px",
                              fontFamily: "var(--cv-font-mono, monospace)",
                              fontSize: "0.82rem",
                              borderRadius: "6px",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              background: "#fbf9f4",
                              outline: "none",
                              marginBottom: "10px",
                            }}
                          />

                          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                            <button
                              type="button"
                              onClick={() => handleExerciseSubmit(exIdx, ex)}
                              disabled={!exerciseAnswers[exIdx]?.trim() || exerciseSubmitting[exIdx]}
                              style={{
                                padding: "7px 16px",
                                borderRadius: "6px",
                                border: "none",
                                background: "var(--cv-accent, #6366f1)",
                                color: "#ffffff",
                                fontSize: "0.8rem",
                                fontWeight: 700,
                                cursor: exerciseAnswers[exIdx]?.trim() && !exerciseSubmitting[exIdx] ? "pointer" : "not-allowed",
                                opacity: exerciseAnswers[exIdx]?.trim() ? 1 : 0.6,
                              }}
                            >
                              {exerciseSubmitting[exIdx] ? "Evaluating..." : "Submit Solution"}
                            </button>

                            {ex.solution && (
                              <button
                                type="button"
                                onClick={() => {
                                  setExerciseAnswers((prev) => ({ ...prev, [exIdx]: ex.solution }));
                                }}
                                style={{
                                  padding: "6px 12px",
                                  borderRadius: "6px",
                                  border: "1px solid var(--cv-border, #e5e2d9)",
                                  background: "transparent",
                                  fontSize: "0.76rem",
                                  fontWeight: 600,
                                  color: "var(--cv-text-muted, #71717a)",
                                  cursor: "pointer",
                                }}
                              >
                                Reveal Reference Solution
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Evaluation feedback result */}
                        {exerciseResults[exIdx] && (
                          <div
                            style={{
                              marginTop: "12px",
                              padding: "12px",
                              borderRadius: "6px",
                              border: "1px solid",
                              borderColor: exerciseResults[exIdx].demonstrated ? "#10b981" : "#ef4444",
                              background: exerciseResults[exIdx].demonstrated ? "rgba(16, 185, 129, 0.05)" : "rgba(239, 68, 68, 0.05)",
                            }}
                          >
                            <div style={{ fontWeight: 700, fontSize: "0.82rem", color: exerciseResults[exIdx].demonstrated ? "#10b981" : "#ef4444", marginBottom: "4px" }}>
                              {exerciseResults[exIdx].demonstrated ? "✓ Demonstrated Understanding!" : "⚠️ Feedback from Dr. Cyra Vance"}
                            </div>
                            <div style={{ fontSize: "0.84rem", lineHeight: 1.5 }}>
                              {exerciseResults[exIdx].reply}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </section>

                  {/* ── SECTION 6: KNOWLEDGE CHECK & SOCRATIC QUESTION ──────── */}
                  <section id="section-check" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 800, margin: "0 0 12px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", borderBottom: "1px solid var(--cv-border, #e5e2d9)", paddingBottom: "8px" }}>
                      Knowledge Check & Socratic Reasoning
                    </h2>

                    <div
                      style={{
                        background: "var(--cv-card-bg, #ffffff)",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        borderRadius: "10px",
                        padding: "18px 20px",
                        marginBottom: "14px",
                      }}
                    >
                      <div style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                        Diagnostic Question
                      </div>
                      <p style={{ margin: "0 0 14px 0", fontSize: "0.9rem", fontWeight: 600, lineHeight: 1.5, color: "var(--cv-text, #1c1c1e)" }}>
                        {currentQuiz.question}
                      </p>

                      <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "14px" }}>
                        {currentQuiz.options.map((opt, oIdx) => {
                          const isSelected = quizSelectedOption === opt;
                          const isCorrect = opt === currentQuiz.answer;
                          let bg = "transparent";
                          let border = "var(--cv-border, #e5e2d9)";
                          let color = "var(--cv-text, #1c1c1e)";

                          if (quizSubmitted) {
                            if (isCorrect) {
                              bg = "rgba(16, 185, 129, 0.1)";
                              border = "#10b981";
                              color = "#047857";
                            } else if (isSelected) {
                              bg = "rgba(239, 68, 68, 0.08)";
                              border = "#ef4444";
                              color = "#b91c1c";
                            }
                          } else if (isSelected) {
                            bg = "rgba(99, 102, 241, 0.08)";
                            border = "var(--cv-accent, #6366f1)";
                            color = "var(--cv-accent, #6366f1)";
                          }

                          return (
                            <button
                              key={oIdx}
                              type="button"
                              onClick={() => {
                                if (!quizSubmitted) setQuizSelectedOption(opt);
                              }}
                              style={{
                                width: "100%",
                                textAlign: "left",
                                padding: "10px 14px",
                                borderRadius: "6px",
                                border: `1px solid ${border}`,
                                background: bg,
                                color,
                                fontSize: "0.84rem",
                                fontWeight: isSelected ? 600 : 400,
                                cursor: quizSubmitted ? "default" : "pointer",
                                transition: "all 0.15s ease",
                              }}
                            >
                              {opt}
                            </button>
                          );
                        })}
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        {!quizSubmitted ? (
                          <button
                            type="button"
                            onClick={() => {
                              if (quizSelectedOption) setQuizSubmitted(true);
                            }}
                            disabled={!quizSelectedOption}
                            style={{
                              padding: "6px 16px",
                              borderRadius: "6px",
                              border: "none",
                              background: "var(--cv-accent, #6366f1)",
                              color: "#ffffff",
                              fontSize: "0.8rem",
                              fontWeight: 700,
                              cursor: quizSelectedOption ? "pointer" : "not-allowed",
                              opacity: quizSelectedOption ? 1 : 0.6,
                            }}
                          >
                            Check Answer
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => {
                              setQuizSubmitted(false);
                              setQuizSelectedOption(null);
                            }}
                            style={{
                              padding: "6px 14px",
                              borderRadius: "6px",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              background: "transparent",
                              color: "var(--cv-text, #1c1c1e)",
                              fontSize: "0.78rem",
                              fontWeight: 600,
                              cursor: "pointer",
                            }}
                          >
                            Retry Question
                          </button>
                        )}
                      </div>

                      {quizSubmitted && (
                        <div style={{ marginTop: "12px", padding: "10px 14px", borderRadius: "6px", background: quizSelectedOption === currentQuiz.answer ? "rgba(16, 185, 129, 0.08)" : "rgba(239, 68, 68, 0.08)", fontSize: "0.84rem", lineHeight: 1.5 }}>
                          <strong>{quizSelectedOption === currentQuiz.answer ? "✓ Correct! " : "Incorrect. "}</strong>
                          {currentQuiz.explanation}
                        </div>
                      )}
                    </div>
                  </section>

                  {/* ── SECTION 7: VERIFIED SOURCES & FURTHER READING ───────── */}
                  <section id="section-resources" style={{ scrollMarginTop: "20px" }}>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 800, margin: "0 0 12px 0", color: "var(--cv-text, #1c1c1e)", letterSpacing: "-0.01em", borderBottom: "1px solid var(--cv-border, #e5e2d9)", paddingBottom: "8px" }}>
                      Verified Sources & Further Reading
                    </h2>

                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                      {(lesson?.resources?.length ? lesson.resources : [
                        {
                          title: `${selectedSkill} Documentation`,
                          canonical_url: `https://www.google.com/search?q=${encodeURIComponent(selectedSkill + " official documentation")}`,
                          is_verified: true,
                          relevance_explanation: `Official reference and guides for ${selectedSkill}.`,
                        }
                      ]).map((res, rIdx) => {
                        const host = res.canonical_url ? (() => { try { return new URL(res.canonical_url).hostname; } catch { return "docs"; } })() : "docs";
                        return (
                          <div
                            key={rIdx}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              padding: "12px 16px",
                              background: "var(--cv-card-bg, #ffffff)",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              borderRadius: "8px",
                            }}
                          >
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <span style={{ fontWeight: 600, fontSize: "0.86rem", color: "var(--cv-text, #1c1c1e)" }}>
                                  {res.title}
                                </span>
                                <span style={{ fontSize: "0.68rem", fontWeight: 700, padding: "1px 6px", borderRadius: "10px", background: "rgba(16, 185, 129, 0.12)", color: "#10b981" }}>
                                  {host}
                                </span>
                              </div>
                              <div style={{ fontSize: "0.76rem", color: "var(--cv-text-muted, #71717a)", marginTop: "2px" }}>
                                {res.relevance_rationale || res.relevance_explanation || res.source || "Official reference documentation"}
                              </div>
                            </div>

                            {res.canonical_url && (
                              <a
                                href={res.canonical_url}
                                target="_blank"
                                rel="noreferrer"
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  padding: "5px 12px",
                                  borderRadius: "6px",
                                  border: "1px solid var(--cv-border, #e5e2d9)",
                                  fontSize: "0.76rem",
                                  color: "var(--cv-accent, #6366f1)",
                                  textDecoration: "none",
                                  fontWeight: 600,
                                  background: "#ffffff",
                                }}
                              >
                                View Doc <FiExternalLink size={12} />
                              </a>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </section>

                  {/* ── SECTION 8: BOTTOM NAVIGATION & COMPLETION ───────────── */}
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginTop: "16px",
                      paddingTop: "20px",
                      borderTop: "1px solid var(--cv-border, #e5e2d9)",
                    }}
                  >
                    {prevLesson ? (
                      <button
                        type="button"
                        aria-label="Previous Lesson"
                        onClick={() => handleSelectConcept(prevLesson, prevLesson.stage_name)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          padding: "8px 16px",
                          borderRadius: "6px",
                          border: "1px solid var(--cv-border, #e5e2d9)",
                          background: "#ffffff",
                          fontSize: "0.82rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          color: "var(--cv-text, #1c1c1e)",
                        }}
                      >
                        <FiArrowLeft size={14} /> Previous: {prevLesson.title.replace(/^[^•]*•\s*/, "")}
                      </button>
                    ) : (
                      <div />
                    )}

                    <button
                      type="button"
                      onClick={() => {
                        if (lesson?.id) {
                          setConceptProgress((prev) => ({
                            ...prev,
                            [lesson.id]: "demonstrated",
                            [lesson.title]: "demonstrated",
                          }));
                        }
                      }}
                      style={{
                        padding: "8px 18px",
                        borderRadius: "6px",
                        border: "1px solid #10b981",
                        background: conceptProgress[lesson?.id] === "demonstrated" ? "#10b981" : "rgba(16, 185, 129, 0.1)",
                        color: conceptProgress[lesson?.id] === "demonstrated" ? "#ffffff" : "#10b981",
                        fontSize: "0.82rem",
                        fontWeight: 700,
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <FiCheckCircle size={15} />
                      {conceptProgress[lesson?.id] === "demonstrated" ? "Completed ✓" : "Mark as Completed"}
                    </button>

                    {nextLesson ? (
                      <button
                        type="button"
                        aria-label="Next Lesson"
                        onClick={() => handleSelectConcept(nextLesson, nextLesson.stage_name)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          padding: "8px 18px",
                          borderRadius: "6px",
                          border: "none",
                          background: "var(--cv-accent, #6366f1)",
                          fontSize: "0.82rem",
                          fontWeight: 700,
                          cursor: "pointer",
                          color: "#ffffff",
                        }}
                      >
                        Next: {nextLesson.title.replace(/^[^•]*•\s*/, "")} <FiArrowRight size={14} />
                      </button>
                    ) : (
                      <div />
                    )}
                  </div>

                </article>
              </div>
            </div>
          ) : (
            <div style={{ padding: "40px", textAlign: "center", color: "var(--cv-text-muted, #71717a)" }}>
              Select a lesson from the roadmap to begin learning.
            </div>
          )}
        </main>

        {/* ── COLUMN 4: RIGHT SIDEBAR — AI MENTOR & PRACTICE ─────────────── */}
        {rightSidebarCollapsed ? (
          <aside
            style={{
              borderLeft: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-surface, #ffffff)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "14px 6px",
              gap: "12px",
            }}
          >
            <button
              type="button"
              title="Expand AI Mentor & Progress"
              onClick={() => setRightSidebarCollapsed(false)}
              style={{
                background: "rgba(99, 102, 241, 0.1)",
                border: "1px solid rgba(99, 102, 241, 0.25)",
                color: "var(--cv-accent, #6366f1)",
                borderRadius: "6px",
                padding: "10px 6px",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "6px",
                fontSize: "0.72rem",
                fontWeight: 700,
              }}
            >
              <FiArrowLeft size={14} />
              <span style={{ writingMode: "vertical-rl", transform: "rotate(180deg)", marginTop: "4px" }}>
                AI Mentor
              </span>
            </button>
          </aside>
        ) : (
          <aside
            style={{
              borderLeft: "1px solid var(--cv-border, #e5e2d9)",
              background: "var(--cv-surface, #ffffff)",
              display: "flex",
              flexDirection: "column",
              overflowY: "auto",
              padding: "14px",
              gap: "14px",
            }}
          >
          {/* Card 1: Cyra — Your AI Mentor */}
          <div
            style={{
              background: "var(--cv-card-bg, #ffffff)",
              border: "1px solid var(--cv-border, #e5e2d9)",
              borderRadius: "12px",
              padding: "14px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
            }}
          >
            {/* Mentor Header with Collapse Button */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, #6366f1, #c084fc)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "1rem",
                    flexShrink: 0,
                  }}
                >
                  👩‍🏫
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: "0.88rem", color: "var(--cv-text, #1c1c1e)" }}>
                    Cyra – Your AI Mentor
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#10b981", fontWeight: 600 }}>
                    ● Online • Socratic Guide
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setRightSidebarCollapsed(true)}
                title="Collapse sidebar"
                style={{
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  color: "var(--cv-text-muted, #71717a)",
                  padding: "4px",
                  borderRadius: "4px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <FiChevronRight size={16} />
              </button>
            </div>

            {/* Conversational Prompt Bubble */}
            <div
              style={{
                background: "rgba(99, 102, 241, 0.06)",
                border: "1px solid rgba(99, 102, 241, 0.15)",
                borderRadius: "8px",
                padding: "10px 12px",
                fontSize: "0.8rem",
                lineHeight: 1.45,
                color: "var(--cv-text, #1c1c1e)",
                marginBottom: "10px",
              }}
            >
              Ask a question or tap a mentor action to deepen your understanding:
            </div>

            {/* Quick Action Buttons (6 Topic-Grounded Actions) */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px", marginBottom: "10px" }}>
              <button
                type="button"
                onClick={() => handleQuickPrompt("Explain this concept more simply")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiHelpCircle size={11} color="var(--cv-accent, #6366f1)" /> Explain simply
              </button>

              <button
                type="button"
                onClick={() => handleQuickPrompt("Show a different example")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiCode size={11} color="var(--cv-accent, #6366f1)" /> Another example
              </button>

              <button
                type="button"
                onClick={() => handleQuickPrompt("Give me a hint")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiSparkles size={11} color="var(--cv-accent, #6366f1)" /> Give a hint
              </button>

              <button
                type="button"
                onClick={() => handleQuickPrompt("Explain why my answer is incorrect")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiAlertTriangle size={11} color="#f59e0b" /> Why incorrect?
              </button>

              <button
                type="button"
                onClick={() => handleQuickPrompt("Give me a practical challenge")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiZap size={11} color="var(--cv-accent, #6366f1)" /> Challenge
              </button>

              <button
                type="button"
                onClick={() => handleQuickPrompt("Connect this concept to my project")}
                disabled={askingMentor}
                style={{
                  padding: "6px 8px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "#fbf9f4",
                  fontSize: "0.71rem",
                  fontWeight: 600,
                  cursor: askingMentor ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "4px",
                }}
              >
                <FiCompass size={11} color="var(--cv-accent, #6366f1)" /> My project
              </button>
            </div>

            {/* Chat History & Input */}
            {mentorChatHistory.length > 0 && (
              <div className="rsl-mentor-chat-stream">
                {mentorChatHistory.map((msg, mIdx) => (
                  <div
                    key={mIdx}
                    className={`rsl-chat-msg ${msg.role}`}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        marginBottom: "4px",
                        fontWeight: 700,
                        fontSize: "0.74rem",
                        color: msg.role === "user" ? "var(--cv-accent, #6366f1)" : "var(--rsl-terracotta, #c85a32)",
                      }}
                    >
                      {msg.role === "user" ? "You" : "👩‍🏫 Cyra"}
                    </div>

                    {msg.role === "mentor" ? (
                      <div
                        className="teaching-markdown-content rsl-mentor-markdown"
                        dangerouslySetInnerHTML={{ __html: marked.parse(msg.content || "") }}
                      />
                    ) : (
                      <div style={{ color: "var(--cv-text, #1c1c1e)", fontSize: "0.8rem", whiteSpace: "pre-wrap" }}>
                        {msg.content}
                      </div>
                    )}
                  </div>
                ))}

                {askingMentor && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "8px 12px",
                      background: "#ffffff",
                      borderRadius: "8px",
                      border: "1px solid var(--rsl-border, #e8e4de)",
                      fontSize: "0.76rem",
                      color: "var(--cv-text-muted, #71717a)",
                    }}
                  >
                    <FiRefreshCw size={12} style={{ animation: "spin 1s linear infinite" }} />
                    <span>Cyra is formulating guidance...</span>
                  </div>
                )}
                <div ref={mentorChatBottomRef} />
              </div>
            )}

            <form onSubmit={handleSendMentorChat} style={{ display: "flex", gap: "6px" }}>
              <input
                type="text"
                value={mentorInput}
                onChange={(e) => setMentorInput(e.target.value)}
                placeholder="Ask Cyra anything..."
                disabled={askingMentor}
                style={{
                  flex: 1,
                  padding: "7px 10px",
                  fontSize: "0.78rem",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  outline: "none",
                  background: "#fbf9f4",
                  color: "var(--cv-text, #1c1c1e)",
                }}
              />
              <button
                type="submit"
                disabled={askingMentor || !mentorInput.trim()}
                title="Send message to Cyra"
                style={{
                  padding: "7px 12px",
                  borderRadius: "6px",
                  border: "none",
                  background: "var(--rsl-terracotta, #c85a32)",
                  color: "#ffffff",
                  cursor: mentorInput.trim() && !askingMentor ? "pointer" : "not-allowed",
                  opacity: mentorInput.trim() && !askingMentor ? 1 : 0.6,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <FiSend size={13} />
              </button>
            </form>
          </div>

          {/* Card 2: Your Learning Path Context */}
          <div
            style={{
              background: "#ffffff",
              border: "1px solid var(--cv-border, #e5e2d9)",
              borderRadius: "12px",
              padding: "14px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", marginBottom: "8px" }}>
              <FiCompass size={15} /> Your learning path
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
              <div style={{
                width: "24px",
                height: "24px",
                borderRadius: "50%",
                background: "rgba(200, 90, 50, 0.1)",
                color: "var(--rsl-terracotta, #c85a32)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                marginTop: "2px",
              }}>
                <FiCompass size={13} />
              </div>
              <p style={{ margin: 0, fontSize: "0.8rem", lineHeight: 1.5, color: "var(--cv-text, #1c1c1e)" }}>
                {lesson?.why_matters_for_role || "This concept builds a strong foundation for your frontend projects and React components, preserving state across renders."}
              </p>
            </div>
          </div>

          {/* Card 3: Key Takeaways */}
          <div
            style={{
              background: "#ffffff",
              border: "1px solid var(--cv-border, #e5e2d9)",
              borderRadius: "12px",
              padding: "14px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", marginBottom: "10px" }}>
              <FiLightbulb size={15} /> Key Takeaways
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {[
                "A closure captures and remembers variables from its outer lexical scope.",
                "It preserves these variables in heap memory even after the outer function finishes executing.",
                "Crucial for data privacy, function factories, and stateful hooks in production.",
              ].map((takeaway, tIdx) => (
                <div key={tIdx} style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.78rem", lineHeight: 1.45, color: "var(--cv-text, #1c1c1e)" }}>
                  <FiCheck size={14} color="#10b981" style={{ flexShrink: 0, marginTop: "2px" }} />
                  <span>{takeaway}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Card 4: Quick Practice */}
          {currentQuiz && (
            <div
              style={{
                background: "var(--cv-card-bg, #ffffff)",
                border: "1px solid var(--cv-border, #e5e2d9)",
                borderRadius: "12px",
                padding: "14px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700, color: "var(--rsl-terracotta, #c85a32)", marginBottom: "10px" }}>
                <FiZap size={15} /> Practice
              </div>

              <p style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--cv-text, #1c1c1e)", margin: "0 0 10px 0" }}>
                {currentQuiz.question}
              </p>

              {/* Radio options */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
                {currentQuiz.options.map((opt, oIdx) => {
                  const isSelected = quizSelectedOption === opt;
                  return (
                    <button
                      key={oIdx}
                      type="button"
                      onClick={() => {
                        if (!quizSubmitted) setQuizSelectedOption(opt);
                      }}
                      style={{
                        textAlign: "left",
                        padding: "8px 10px",
                        borderRadius: "6px",
                        fontSize: "0.78rem",
                        lineHeight: 1.4,
                        border: "1px solid",
                        borderColor: isSelected ? "var(--rsl-terracotta, #c85a32)" : "var(--cv-border, #e5e2d9)",
                        background: isSelected ? "rgba(200, 90, 50, 0.08)" : "#fbf9f4",
                        color: "var(--cv-text, #1c1c1e)",
                        cursor: quizSubmitted ? "default" : "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      <span
                        style={{
                          width: "12px",
                          height: "12px",
                          borderRadius: "50%",
                          border: `2px solid ${isSelected ? "var(--rsl-terracotta, #c85a32)" : "#94a3b8"}`,
                          background: isSelected ? "var(--rsl-terracotta, #c85a32)" : "transparent",
                          flexShrink: 0,
                        }}
                      />
                      <span>{opt}</span>
                    </button>
                  );
                })}
              </div>

              {!quizSubmitted ? (
                <button
                  type="button"
                  onClick={() => {
                    if (quizSelectedOption) setQuizSubmitted(true);
                  }}
                  disabled={!quizSelectedOption}
                  style={{
                    width: "100%",
                    padding: "7px 14px",
                    borderRadius: "6px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    border: "none",
                    background: quizSelectedOption ? "var(--rsl-terracotta, #c85a32)" : "#cbd5e1",
                    color: "#ffffff",
                    cursor: quizSelectedOption ? "pointer" : "not-allowed",
                  }}
                >
                  Check Answer
                </button>
              ) : (
                <div
                  style={{
                    padding: "10px",
                    borderRadius: "8px",
                    background: quizSelectedOption === currentQuiz.answer ? "rgba(16, 185, 129, 0.08)" : "rgba(239, 68, 68, 0.08)",
                    border: `1px solid ${quizSelectedOption === currentQuiz.answer ? "#10b981" : "#ef4444"}`,
                  }}
                >
                  <div
                    style={{
                      fontSize: "0.82rem",
                      fontWeight: 700,
                      color: quizSelectedOption === currentQuiz.answer ? "#10b981" : "#ef4444",
                      marginBottom: "4px",
                    }}
                  >
                    {quizSelectedOption === currentQuiz.answer ? "✓ Correct!" : "✗ Not quite right."}
                  </div>
                  <div style={{ fontSize: "0.76rem", color: "var(--cv-text, #1c1c1e)", marginBottom: "8px" }}>
                    {quizSelectedOption === currentQuiz.answer
                      ? currentQuiz.explanation || `${quizSelectedOption} is the verified answer for ${lesson?.topic || selectedConcept?.title || selectedSkill}.`
                      : `Review the technical concept for ${lesson?.topic || selectedConcept?.title || selectedSkill} and try again.`}
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setQuizSubmitted(false);
                      setQuizSelectedOption(null);
                    }}
                    style={{
                      padding: "4px 8px",
                      borderRadius: "4px",
                      border: "1px solid var(--cv-border, #e5e2d9)",
                      background: "#ffffff",
                      fontSize: "0.72rem",
                      cursor: "pointer",
                    }}
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Card 3: Skill Mastery & Learning Progress */}
          <div
            style={{
              background: "var(--cv-card-bg, #ffffff)",
              border: "1px solid var(--cv-border, #e5e2d9)",
              borderRadius: "12px",
              padding: "14px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700, color: "var(--cv-accent, #6366f1)" }}>
                <FiAward size={15} /> Skill Mastery
              </div>
              <span style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--cv-accent, #6366f1)" }}>
                {getSkillMastery(selectedSkill, resumeSkills, stats.demonstrated, stats.total)}%
              </span>
            </div>
            <div style={{ height: "6px", background: "#f1f5f9", borderRadius: "3px", overflow: "hidden", marginBottom: "8px" }}>
              <div
                style={{
                  height: "100%",
                  width: `${getSkillMastery(selectedSkill, resumeSkills, stats.demonstrated, stats.total)}%`,
                  background: "linear-gradient(90deg, #6366f1, #10b981)",
                  borderRadius: "3px",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "var(--cv-text-muted, #71717a)" }}>
              <span>Completed: {stats.demonstrated}/{stats.total || 0} Lessons</span>
              <span>Level: {getSkillProficiency(selectedSkill, resumeSkills)}</span>
            </div>
          </div>

          {/* Card 4: Verified Resources */}
          {lesson?.resources && lesson.resources.length > 0 && (
            <div
              style={{
                background: "var(--cv-card-bg, #ffffff)",
                border: "1px solid var(--cv-border, #e5e2d9)",
                borderRadius: "12px",
                padding: "14px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: 700, color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                <FiExternalLink size={14} /> Verified Citations
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                {lesson.resources.slice(0, 3).map((res, rIdx) => (
                  <a
                    key={rIdx}
                    href={res.canonical_url || res.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "6px 8px",
                      background: "#f8fafc",
                      borderRadius: "6px",
                      fontSize: "0.74rem",
                      color: "var(--cv-accent, #6366f1)",
                      textDecoration: "none",
                      border: "1px solid var(--cv-border, #e5e2d9)",
                    }}
                  >
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginRight: "6px" }}>
                      {res.canonical_url ? (() => { try { return new URL(res.canonical_url).hostname; } catch { return res.source || "Official Doc"; } })() : (res.source || "Official Documentation")}
                    </span>
                    <FiExternalLink size={11} style={{ flexShrink: 0 }} />
                  </a>
                ))}
              </div>
            </div>
          )}
        </aside>
        )}
      </div>

      {/* ── DIAGNOSTIC LEVEL CHECK MODAL ─────────────────────────────────── */}
      {diagnosticOpen && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "12px",
              padding: "24px",
              maxWidth: "520px",
              width: "90%",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700 }}>
                Diagnostic Knowledge Placement: {selectedSkill}
              </h3>
              <button
                type="button"
                onClick={() => setDiagnosticOpen(false)}
                style={{ background: "transparent", border: "none", cursor: "pointer" }}
              >
                <FiX size={18} />
              </button>
            </div>

            <p style={{ fontSize: "0.84rem", color: "var(--cv-text-muted, #71717a)", marginBottom: "14px", lineHeight: 1.5 }}>
              Answer this quick diagnostic to evaluate your starting level. Passing allows experienced developers to jump straight to core and advanced architecture without repeating beginner lessons.
            </p>

            <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "8px", marginBottom: "14px", fontSize: "0.85rem", border: "1px solid var(--cv-border, #e5e2d9)" }}>
              <strong>Diagnostic Challenge:</strong>
              <div style={{ marginTop: "4px" }}>
                {skillPath?.diagnostic_question || `How does ${selectedSkill} handle memory references, state transitions, and asynchronous execution?`}
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
              <button
                type="button"
                onClick={() => setDiagnosticOpen(false)}
                style={{
                  padding: "6px 14px",
                  borderRadius: "6px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "transparent",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setDiagnosticScore(90);
                  setDiagnosticOpen(false);
                  if (skillPath?.stages?.[1]?.lessons?.[0]) {
                    triggerLessonFetch(skillPath.stages[1].lessons[0], skillPath.stages[1].stage_name, selectedSkill);
                  }
                }}
                style={{
                  padding: "6px 16px",
                  borderRadius: "6px",
                  border: "none",
                  background: "var(--cv-accent, #6366f1)",
                  color: "#ffffff",
                  fontSize: "0.8rem",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Demonstrate & Jump to Stage 2
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useMemo, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  ArrowLeft as FiArrowLeft,
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
} from "lucide-react";
import { marked } from "marked";
import {
  getProfileSnapshot,
  getTeachingSkillPath,
  getTeachingLessonDetail,
  chatWithTeachingMentor,
} from "../services/careerService";
import "./TeachingStudioPage.css";

// ── AUTHORITATIVE RESUME SKILL INVENTORY FROM DHANYASRIK_AIML_KPR.PDF ─────────
export const AUTHORITATIVE_RESUME_SKILLS = [
  // Programming Languages
  { name: "Python", category: "Languages", source: "Nitroware Internship & Projects", proficiency: "Advanced", verified: true },
  { name: "Java", category: "Languages", source: "IIT Bombay Spoken Tutorial", proficiency: "Intermediate", verified: true },
  { name: "JavaScript", category: "Languages", source: "InboxPilot & Web Projects", proficiency: "Advanced", verified: true },
  { name: "C", category: "Languages", source: "IIT Bombay Spoken Tutorial", proficiency: "Intermediate", verified: true },

  // AI, ML & GenAI
  { name: "LangChain", category: "AI & GenAI", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", verified: true },
  { name: "LangGraph", category: "AI & GenAI", source: "InboxPilot Multi-Agent Workflows", proficiency: "Advanced", verified: true },
  { name: "Retrieval-Augmented Generation (RAG)", category: "AI & GenAI", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", verified: true },
  { name: "Large Language Models (LLMs)", category: "AI & GenAI", source: "NPTEL Introduction to LLM Cert", proficiency: "Advanced", verified: true },
  { name: "Prompt Engineering", category: "AI & GenAI", source: "Infosys Springboard GenAI Cert", proficiency: "Advanced", verified: true },
  { name: "TensorFlow", category: "AI & GenAI", source: "Precision Agriculture Publication", proficiency: "Intermediate", verified: true },
  { name: "Scikit-learn", category: "AI & GenAI", source: "Machine Learning Projects", proficiency: "Intermediate", verified: true },
  { name: "OpenCV", category: "AI & GenAI", source: "Nitroware Technologies Internship", proficiency: "Intermediate", verified: true },
  { name: "CNNs", category: "AI & GenAI", source: "Deep Learning Precision Agriculture", proficiency: "Intermediate", verified: true },
  { name: "AI/ML", category: "AI & GenAI", source: "B.E. CSE (AI & ML) KPR Institute", proficiency: "Advanced", verified: true },

  // Web & Backend Frameworks
  { name: "React.js", category: "Web & Backend", source: "HackerRank Frontend React Cert", proficiency: "Advanced", verified: true },
  { name: "FastAPI", category: "Web & Backend", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", verified: true },
  { name: "Express.js", category: "Web & Backend", source: "Backend Services", proficiency: "Intermediate", verified: true },
  { name: "Django REST", category: "Web & Backend", source: "Python API Services", proficiency: "Intermediate", verified: true },
  { name: "REST APIs", category: "Web & Backend", source: "InboxPilot & Weather Checker", proficiency: "Advanced", verified: true },
  { name: "Bootstrap", category: "Web & Backend", source: "Responsive UI Projects", proficiency: "Intermediate", verified: true },

  // Databases & Vector Stores
  { name: "ChromaDB", category: "Databases & Tools", source: "InboxPilot & AI Code Reviewer", proficiency: "Advanced", verified: true },
  { name: "MongoDB", category: "Databases & Tools", source: "MERN Stack Projects", proficiency: "Intermediate", verified: true },
  { name: "Mongoose", category: "Databases & Tools", source: "MongoDB Modeling", proficiency: "Intermediate", verified: true },
  { name: "MySQL", category: "Databases & Tools", source: "HackerRank SQL Basic Cert", proficiency: "Intermediate", verified: true },

  // Developer Tools & Concepts
  { name: "Git", category: "Databases & Tools", source: "Version Control Workflows", proficiency: "Advanced", verified: true },
  { name: "GitHub", category: "Databases & Tools", source: "Verified Account @dhanyasri612", proficiency: "Advanced", verified: true },
  { name: "Postman", category: "Databases & Tools", source: "API Testing & Verification", proficiency: "Advanced", verified: true },
  { name: "Figma / UI/UX", category: "Databases & Tools", source: "UI/UX & Wireframing", proficiency: "Intermediate", verified: true },
  { name: "Gmail API", category: "Databases & Tools", source: "InboxPilot OAuth2 & Pub/Sub", proficiency: "Advanced", verified: true },
  { name: "CRUD Operations", category: "Databases & Tools", source: "BlogSpace Full-Stack", proficiency: "Advanced", verified: true },
];

// Skill proficiency level derived from skill data
function getSkillProficiency(skillName, skills) {
  const found = skills.find((s) => s.name.toLowerCase() === skillName.toLowerCase());
  return found?.proficiency || "Intermediate";
}

export default function ResumeSkillLearningPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlSkill = searchParams.get("skill");

  // Skill Inventory
  const [resumeSkills, setResumeSkills] = useState(AUTHORITATIVE_RESUME_SKILLS);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [skillCategory, setSkillCategory] = useState("all");
  const [skillSearch, setSkillSearch] = useState("");
  const [selectedSkill, setSelectedSkill] = useState(urlSkill || "React.js");

  // Skill Learning Path
  const [skillPath, setSkillPath] = useState(null);
  const [loadingPath, setLoadingPath] = useState(false);
  const [pathError, setPathError] = useState(null);
  const [selectedConcept, setSelectedConcept] = useState(null);

  // Active lesson detail fetched from the lesson-detail endpoint
  const [activeLessonDetail, setActiveLessonDetail] = useState(null);
  const [loadingLesson, setLoadingLesson] = useState(false);
  const [lessonError, setLessonError] = useState(null);

  // Staleness guard for lesson fetches
  const activeRequestRef = useRef({ skill: null, lessonId: null, token: 0 });

  // 6-tab section navigation
  const [activeLessonTab, setActiveLessonTab] = useState("overview");

  // Per-exercise answers (keyed by exercise index)
  const [exerciseAnswers, setExerciseAnswers] = useState({});
  const [exerciseSubmitting, setExerciseSubmitting] = useState({});
  const [exerciseResults, setExerciseResults] = useState({});

  const [learnerAnswer, setLearnerAnswer] = useState("");
  const [evaluating, setEvaluating] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);

  // Progress tracking: { [conceptTitle]: 'not_assessed' | 'partially_understood' | 'demonstrated' }
  const [conceptProgress, setConceptProgress] = useState({});

  // Adaptive mentor explanations
  const [askingMentor, setAskingMentor] = useState(false);
  const [mentorExplanations, setMentorExplanations] = useState([]);

  // Fetch unified skills from backend snapshot and merge with authoritative list
  useEffect(() => {
    const fetchSkills = async () => {
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
      } catch (err) {
        console.warn("Could not load snapshot skills, using authoritative resume inventory:", err);
      } finally {
        setLoadingSkills(false);
      }
    };

    fetchSkills();
  }, [urlSkill]);

  // Fetch skill learning path when selectedSkill changes
  useEffect(() => {
    if (!selectedSkill) return;

    // Clear lesson state on skill change
    setActiveLessonDetail(null);
    setEvaluationResult(null);
    setMentorExplanations([]);
    setLearnerAnswer("");
    setExerciseAnswers({});
    setExerciseResults({});

    const fetchPath = async () => {
      try {
        setLoadingPath(true);
        setSelectedConcept(null);
        setPathError(null);

        // Capture the skill we're fetching for
        const fetchingSkill = selectedSkill;

        const data = await getTeachingSkillPath(fetchingSkill);

        // Roadmap staleness guard: verify the returned data matches selectedSkill
        const returnedSkillName = data?.skill_name || data?.normalized_skill || "";
        const currentSkill = fetchingSkill; // captured at fetch time
        const matchesSkill =
          returnedSkillName.toLowerCase().includes(currentSkill.toLowerCase()) ||
          currentSkill.toLowerCase().includes(returnedSkillName.toLowerCase());

        // If the selected skill has changed since we started fetching, discard
        // We use a ref-less approach here: we'll check via the closure variable
        if (!matchesSkill && returnedSkillName) {
          console.warn(
            `Roadmap staleness: expected "${currentSkill}", got "${returnedSkillName}". Discarding.`
          );
          setPathError(`Received roadmap for "${returnedSkillName}" instead of "${currentSkill}". Please retry.`);
          setLoadingPath(false);
          return;
        }

        // Normalize stages: map stage.lessons or stage.topics into {id, title, topic} only
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
            // Keep only id, title, topic from roadmap items — no fabricated content
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

  /**
   * Core lesson-detail fetch with staleness guard.
   * skill param is the skill at the time of dispatch (may differ from selectedSkill by the time the promise resolves).
   */
  const triggerLessonFetch = (lesson, stageName, skill) => {
    const lessonTitle = lesson.title || lesson.topic;
    const lessonId = lesson.id;
    const currentSkill = skill || selectedSkill;

    // Update selected concept immediately
    setSelectedConcept({
      ...lesson,
      stage: stageName || "Foundations",
    });
    setActiveLessonDetail(null);
    setLessonError(null);
    setLoadingLesson(true);
    setLearnerAnswer("");
    setEvaluationResult(null);
    setMentorExplanations([]);
    setExerciseAnswers({});
    setExerciseResults({});
    setActiveLessonTab("overview");

    // Increment staleness token
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
        // Staleness guard: check token, skill, and lessonId all match
        const ref = activeRequestRef.current;
        if (
          ref.token !== token ||
          ref.skill !== currentSkill ||
          ref.lessonId !== lessonId
        ) {
          console.warn("Lesson response discarded: request is stale (token/skill/lessonId mismatch)");
          return;
        }

        // Additional content validation: verify response matches requested skill/lesson
        const resSkill = (res?.skill || "").toLowerCase();
        const reqSkill = currentSkill.toLowerCase();
        const resLessonId = res?.lesson_id;

        if (resSkill && !resSkill.includes(reqSkill) && !reqSkill.includes(resSkill)) {
          console.warn(`Lesson content mismatch: expected skill "${currentSkill}", got "${res?.skill}"`);
          setLessonError(
            `Received lesson content for "${res?.skill}" instead of "${currentSkill}". Please retry.`
          );
          setLoadingLesson(false);
          return;
        }

        if (resLessonId && resLessonId !== lessonId) {
          console.warn(`Lesson ID mismatch: expected "${lessonId}", got "${resLessonId}"`);
          setLessonError(
            `Received content for a different lesson. Please retry.`
          );
          setLoadingLesson(false);
          return;
        }

        setActiveLessonDetail(res);
        setLoadingLesson(false);
      })
      .catch((err) => {
        // Only apply error if this request is still current
        const ref = activeRequestRef.current;
        if (ref.token !== token || ref.skill !== currentSkill || ref.lessonId !== lessonId) {
          return;
        }
        console.error("Failed to load lesson detail:", err);
        setLessonError(`Failed to load lesson content. Please retry.`);
        setLoadingLesson(false);
      });
  };

  const handleSelectConcept = (lesson, stageName) => {
    // Clear lesson state on lesson change
    setActiveLessonDetail(null);
    setEvaluationResult(null);
    setMentorExplanations([]);
    setLearnerAnswer("");
    setExerciseAnswers({});
    setExerciseResults({});

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
    // Re-trigger the path fetch by toggling a dummy state or we can re-trigger via the same useEffect
    // Force re-trigger by setting selectedSkill to itself via a functional update trick:
    setSelectedSkill((prev) => {
      // This is a no-op value change but won't re-trigger useEffect since value is the same.
      // Instead we'll use a separate retryCount state.
      return prev;
    });
    // We need a separate trigger; use pathRetryCount
    setPathRetryCount((c) => c + 1);
  };

  const [pathRetryCount, setPathRetryCount] = useState(0);

  // Re-trigger path fetch on retry
  useEffect(() => {
    if (pathRetryCount === 0) return;
    if (!selectedSkill) return;

    setActiveLessonDetail(null);
    setEvaluationResult(null);
    setMentorExplanations([]);
    setLearnerAnswer("");
    setExerciseAnswers({});
    setExerciseResults({});

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

        const normalizedData = { ...data, stages: normalizedStages };
        setSkillPath(normalizedData);

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
  }, [pathRetryCount]);

  // Evaluate Socratic understanding check
  const handleEvaluateUnderstanding = async (e) => {
    if (e) e.preventDefault();
    if (!learnerAnswer.trim() || evaluating) return;

    try {
      setEvaluating(true);
      const res = await chatWithTeachingMentor({
        message: learnerAnswer,
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: selectedConcept?.id,
        is_assessment: true,
      });

      setEvaluationResult(res);

      const isDemonstrated = Boolean(res?.demonstrated_understanding);
      setConceptProgress((prev) => ({
        ...prev,
        [selectedConcept.title]: isDemonstrated ? "demonstrated" : "partially_understood",
      }));
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setEvaluating(false);
    }
  };

  // Submit a practice exercise answer
  const handleSubmitExercise = async (exerciseIdx, exerciseTitle) => {
    const answer = exerciseAnswers[exerciseIdx];
    if (!answer?.trim() || exerciseSubmitting[exerciseIdx]) return;

    try {
      setExerciseSubmitting((prev) => ({ ...prev, [exerciseIdx]: true }));
      const res = await chatWithTeachingMentor({
        message: answer,
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: selectedConcept?.id,
        is_assessment: false,
      });
      setExerciseResults((prev) => ({ ...prev, [exerciseIdx]: res }));
    } catch (err) {
      console.error("Exercise submission error:", err);
      setExerciseResults((prev) => ({
        ...prev,
        [exerciseIdx]: { reply: "Failed to get feedback. Please retry." },
      }));
    } finally {
      setExerciseSubmitting((prev) => ({ ...prev, [exerciseIdx]: false }));
    }
  };

  // Quick mentor adaptation prompt
  const handleRequestAdaptation = async (promptType) => {
    const lessonTitle = selectedConcept?.title || selectedConcept?.topic;
    const promptText =
      promptType === "simpler"
        ? `Explain ${lessonTitle} in simpler, everyday analogies for a beginner.`
        : promptType === "example"
          ? `Give me another production-grade practical code example of ${lessonTitle}.`
          : `Explain the deep runtime internals, performance bottlenecks, and concurrency trade-offs of ${lessonTitle}.`;

    if (askingMentor) return;

    try {
      setAskingMentor(true);
      const res = await chatWithTeachingMentor({
        message: promptText,
        mode: "skill",
        target_id: selectedSkill,
        lesson_id: selectedConcept?.id,
        is_assessment: false,
      });

      setMentorExplanations((prev) => [
        ...prev,
        { prompt: promptText, reply: res.reply || res.feedback || "Explanation generated." },
      ]);
    } catch (err) {
      console.error("Mentor request error:", err);
    } finally {
      setAskingMentor(false);
    }
  };

  // Filter skills by category & search term
  const filteredSkills = useMemo(() => {
    return resumeSkills.filter((s) => {
      if (skillCategory !== "all" && s.category !== skillCategory) return false;
      if (skillSearch.trim()) {
        const q = skillSearch.toLowerCase();
        return s.name.toLowerCase().includes(q) || s.source?.toLowerCase().includes(q);
      }
      return true;
    });
  }, [resumeSkills, skillCategory, skillSearch]);

  // Overall lesson progress stats
  const stats = useMemo(() => {
    if (!skillPath?.stages) return { total: 7, demonstrated: 0, partial: 0 };
    let total = 0;
    let demonstrated = 0;
    let partial = 0;

    skillPath.stages.forEach((st) => {
      (st.lessons || []).forEach((l) => {
        total++;
        const stKey = conceptProgress[l.title] || (l.is_demonstrated ? "demonstrated" : "not_assessed");
        if (stKey === "demonstrated") demonstrated++;
        else if (stKey === "partially_understood") partial++;
      });
    });

    return { total: Math.max(1, total), demonstrated, partial };
  }, [skillPath, conceptProgress]);

  // The lesson object from the detail response
  const lesson = activeLessonDetail?.lesson;

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
            <h1 className="teaching-title-text">Resume Skill Learning</h1>
            <span className="teaching-mentor-badge">
              <FiBookOpen /> Dr. Cyra Vance • Socratic Skill Mastery
            </span>
          </div>
        </div>

        <div className="teaching-header-controls">
          <span style={{ fontSize: "0.82rem", color: "var(--cv-text-muted, #71717a)" }}>
            Current Skill: <strong>{selectedSkill}</strong> ({stats.demonstrated}/{stats.total} Mastered)
          </span>
        </div>
      </header>

      {/* ── 3-Column Skill Learning Layout ───────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "300px 320px 1fr",
          height: "calc(100vh - 65px)",
          overflow: "hidden",
          background: "var(--cv-bg, var(--surface))",
        }}
      >
        {/* ── COLUMN 1: Resume Skill Inventory ────────────────── */}
        <aside
          style={{
            borderRight: "1px solid var(--cv-border, #e5e2d9)",
            background: "var(--cv-surface, #ffffff)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Header & Filter Controls */}
          <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
            <div style={{ fontSize: "0.74rem", textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", fontWeight: 700, letterSpacing: "0.05em", marginBottom: "8px" }}>
              Authoritative Resume Skills ({resumeSkills.length})
            </div>

            {/* Skill Search */}
            <div style={{ position: "relative", marginBottom: "8px" }}>
              <FiSearch style={{ position: "absolute", left: "8px", top: "50%", transform: "translateY(-50%)", color: "var(--cv-text-muted, #71717a)", width: "13px", height: "13px" }} />
              <input
                type="text"
                value={skillSearch}
                onChange={(e) => setSkillSearch(e.target.value)}
                placeholder="Search resume skills..."
                style={{
                  width: "100%",
                  padding: "5px 8px 5px 28px",
                  fontSize: "0.78rem",
                  borderRadius: "5px",
                  border: "1px solid var(--cv-border, #e5e2d9)",
                  background: "var(--cv-bg, #fbf9f4)",
                  outline: "none",
                }}
              />
            </div>

            {/* Category Filter Pills */}
            <div style={{ display: "flex", gap: "4px", overflowX: "auto", paddingBottom: "2px" }}>
              {[
                { id: "all", label: "All" },
                { id: "AI & GenAI", label: "AI & GenAI" },
                { id: "Web & Backend", label: "Web/Backend" },
                { id: "Languages", label: "Languages" },
                { id: "Databases & Tools", label: "Data & Tools" },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSkillCategory(cat.id)}
                  style={{
                    padding: "2px 7px",
                    borderRadius: "10px",
                    fontSize: "0.68rem",
                    whiteSpace: "nowrap",
                    border: "1px solid",
                    borderColor: skillCategory === cat.id ? "var(--cv-accent, #6366f1)" : "var(--cv-border, #e5e2d9)",
                    background: skillCategory === cat.id ? "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))" : "transparent",
                    color: skillCategory === cat.id ? "var(--cv-accent, #6366f1)" : "var(--cv-text-muted, #71717a)",
                    fontWeight: skillCategory === cat.id ? 700 : 500,
                    cursor: "pointer",
                  }}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Skill List */}
          <div style={{ flex: 1, overflowY: "auto", padding: "8px" }}>
            {filteredSkills.map((s) => {
              const isSelected = selectedSkill?.toLowerCase() === s.name.toLowerCase();
              return (
                <button
                  key={s.name}
                  onClick={() => {
                    setSelectedSkill(s.name);
                    setSearchParams({ skill: s.name });
                  }}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    padding: "9px 12px",
                    borderRadius: "6px",
                    border: "1px solid",
                    borderColor: isSelected ? "var(--cv-accent, #6366f1)" : "transparent",
                    background: isSelected ? "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))" : "transparent",
                    cursor: "pointer",
                    marginBottom: "3px",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2px" }}>
                    <span style={{ fontWeight: 600, fontSize: "0.84rem", color: isSelected ? "var(--cv-accent, #6366f1)" : "var(--cv-text, #1c1c1e)" }}>
                      {s.name}
                    </span>
                    <span style={{ fontSize: "0.68rem", color: "var(--cv-accent, #6366f1)", fontWeight: 600 }}>
                      {s.proficiency}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--cv-text-muted, #71717a)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    Source: {s.source}
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        {/* ── COLUMN 2: Topic Roadmap for Selected Skill ─────── */}
        <aside
          style={{
            borderRight: "1px solid var(--cv-border, #e5e2d9)",
            background: "var(--cv-surface-2, rgba(0, 0, 0, 0.02))",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "14px 16px", background: "var(--cv-surface, #fff)", borderBottom: "1px solid var(--cv-border, #e5e2d9)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: 700, fontSize: "0.88rem" }}>{selectedSkill} Roadmap</span>
              <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--cv-accent, #6366f1)" }}>
                {stats.demonstrated}/{stats.total} Mastered
              </span>
            </div>
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "12px" }}>
            {loadingPath ? (
              <div style={{ padding: "30px 16px", textAlign: "center", color: "var(--cv-text-muted, #71717a)" }}>
                <FiRefreshCw className="spin-icon" style={{ marginBottom: "8px" }} />
                <div style={{ fontSize: "0.82rem" }}>Generating personalized curriculum...</div>
              </div>
            ) : pathError ? (
              <div role="alert" style={{ padding: "16px", margin: "8px", borderRadius: "8px", border: "1px solid #ef4444", background: "rgba(239, 68, 68, 0.05)" }}>
                <div style={{ fontSize: "0.82rem", color: "#ef4444", marginBottom: "10px" }}>{pathError}</div>
                <button
                  onClick={handleRetryPath}
                  style={{
                    padding: "5px 12px",
                    borderRadius: "5px",
                    border: "1px solid #ef4444",
                    background: "transparent",
                    color: "#ef4444",
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "5px",
                  }}
                >
                  <FiRefreshCw size={12} /> Retry
                </button>
              </div>
            ) : !skillPath?.stages?.length ? (
              <div style={{ padding: "20px", textAlign: "center", color: "var(--cv-text-muted, #71717a)", fontSize: "0.85rem" }}>
                Select a skill to view its roadmap.
              </div>
            ) : (
              skillPath.stages.map((stage, sIdx) => {
                const lessons = stage.lessons || [];
                return (
                  <div key={sIdx} style={{ marginBottom: "16px" }}>
                    <div style={{ fontSize: "0.74rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-text-muted, #71717a)", marginBottom: "6px" }}>
                      Stage {stage.stage_number || sIdx + 1}: {stage.stage_name}
                    </div>

                    {lessons.map((lesson, lIdx) => {
                      const title = lesson.title || lesson.topic || `Lesson ${lIdx + 1}`;
                      const isSelected = selectedConcept?.title === title || selectedConcept?.id === lesson.id;
                      const status = conceptProgress[title] || (lesson.is_demonstrated ? "demonstrated" : "not_assessed");

                      return (
                        <button
                          key={lIdx}
                          onClick={() => handleSelectConcept(lesson, stage.stage_name)}
                          style={{
                            width: "100%",
                            textAlign: "left",
                            padding: "8px 10px",
                            borderRadius: "6px",
                            border: "1px solid",
                            borderColor: isSelected ? "var(--cv-accent, #6366f1)" : "var(--cv-border, #e5e2d9)",
                            background: isSelected ? "var(--cv-accent-soft, rgba(99, 102, 241, 0.08))" : "var(--cv-surface, #ffffff)",
                            color: isSelected ? "var(--cv-accent, #6366f1)" : "var(--cv-text, #1c1c1e)",
                            fontWeight: isSelected ? 600 : 400,
                            fontSize: "0.8rem",
                            cursor: "pointer",
                            marginBottom: "4px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span style={{ flex: 1, paddingRight: "6px" }}>{title}</span>
                          {status === "demonstrated" ? (
                            <span style={{ color: "#10b981", fontSize: "0.72rem", fontWeight: 700, display: "inline-flex", alignItems: "center", gap: "2px" }}>
                              <FiCheck size={12} /> Mastered
                            </span>
                          ) : status === "partially_understood" ? (
                            <span style={{ color: "#d97706", fontSize: "0.72rem", fontWeight: 700 }}>⚠️ In Review</span>
                          ) : (
                            <span style={{ color: "var(--cv-text-muted, #71717a)", fontSize: "0.7rem" }}>Ready</span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                );
              })
            )}
          </div>
        </aside>

        {/* ── COLUMN 3: Deep-Dive Pedagogical Workspace ─── */}
        <main
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: "var(--cv-surface, #ffffff)",
          }}
        >
          {selectedConcept ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
              {/* Concept Header */}
              <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--cv-border, #e5e2d9)", background: "var(--cv-surface, #ffffff)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                      <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "4px", background: "var(--cv-accent-soft, rgba(99, 102, 241, 0.12))", color: "var(--cv-accent, #6366f1)", fontWeight: 700 }}>
                        {selectedSkill} • {selectedConcept.stage}
                      </span>
                      {conceptProgress[selectedConcept.title] === "demonstrated" && (
                        <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "12px", background: "rgba(16, 185, 129, 0.12)", color: "#10b981", fontWeight: 700 }}>
                          ✓ Demonstrated
                        </span>
                      )}
                      {activeLessonDetail?.validation_status === "fallback_curated" && (
                        <span style={{ fontSize: "0.72rem", padding: "2px 8px", borderRadius: "4px", background: "rgba(245, 158, 11, 0.1)", color: "#d97706", fontWeight: 600 }}>
                          ⚠ Showing curated content — AI generation unavailable
                        </span>
                      )}
                    </div>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 700, margin: 0, color: "var(--cv-text, #1c1c1e)" }}>
                      {selectedConcept.title || selectedConcept.topic}
                    </h2>
                  </div>

                  {/* Adaptive Guidance Actions */}
                  <div style={{ display: "flex", gap: "6px" }}>
                    <button
                      onClick={() => handleRequestAdaptation("simpler")}
                      disabled={askingMentor}
                      style={{
                        padding: "5px 10px",
                        borderRadius: "4px",
                        fontSize: "0.74rem",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        background: "transparent",
                        cursor: askingMentor ? "not-allowed" : "pointer",
                      }}
                    >
                      💡 Simpler
                    </button>
                    <button
                      onClick={() => handleRequestAdaptation("example")}
                      disabled={askingMentor}
                      style={{
                        padding: "5px 10px",
                        borderRadius: "4px",
                        fontSize: "0.74rem",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        background: "transparent",
                        cursor: askingMentor ? "not-allowed" : "pointer",
                      }}
                    >
                      🔍 Example
                    </button>
                    <button
                      onClick={() => handleRequestAdaptation("deeper")}
                      disabled={askingMentor}
                      style={{
                        padding: "5px 10px",
                        borderRadius: "4px",
                        fontSize: "0.74rem",
                        border: "1px solid var(--cv-border, #e5e2d9)",
                        background: "transparent",
                        cursor: askingMentor ? "not-allowed" : "pointer",
                      }}
                    >
                      ⚙️ Internals
                    </button>
                  </div>
                </div>

                {/* Section Tabs */}
                <div style={{ display: "flex", gap: "6px", borderBottom: "none", marginTop: "12px" }}>
                  {[
                    { id: "overview", label: "1-3. Purpose & Walkthrough" },
                    { id: "code", label: "4-5. Code & Runtime Flow" },
                    { id: "debugging", label: "6. Pitfalls & Debugging" },
                    { id: "exercise", label: "7. Practice Exercise" },
                    { id: "check", label: "8. Socratic Check" },
                    { id: "resources", label: "9. Verified Resources" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveLessonTab(tab.id)}
                      style={{
                        padding: "6px 12px",
                        borderRadius: "4px",
                        fontSize: "0.78rem",
                        fontWeight: activeLessonTab === tab.id ? 700 : 500,
                        border: "1px solid",
                        borderColor: activeLessonTab === tab.id ? "var(--cv-accent, #6366f1)" : "var(--cv-border, #e5e2d9)",
                        background: activeLessonTab === tab.id ? "var(--cv-accent, #6366f1)" : "transparent",
                        color: activeLessonTab === tab.id ? "#ffffff" : "var(--cv-text, #1c1c1e)",
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Lesson Body */}
              <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>

                {/* Loading state */}
                {loadingLesson && (
                  <div style={{ padding: "40px", textAlign: "center", color: "var(--cv-text-muted, #71717a)" }}>
                    <FiRefreshCw className="spin-icon" style={{ marginBottom: "10px", width: "20px", height: "20px" }} />
                    <div style={{ fontSize: "0.88rem", fontWeight: 600, marginBottom: "4px" }}>
                      Loading lesson for {selectedSkill}
                    </div>
                    <div style={{ fontSize: "0.8rem" }}>
                      {selectedConcept?.title || selectedConcept?.topic}
                    </div>
                  </div>
                )}

                {/* Error state */}
                {!loadingLesson && lessonError && (
                  <div
                    role="alert"
                    style={{
                      padding: "16px",
                      borderRadius: "8px",
                      border: "1px solid #ef4444",
                      background: "rgba(239, 68, 68, 0.05)",
                      marginBottom: "16px",
                    }}
                  >
                    <div style={{ fontSize: "0.85rem", color: "#ef4444", marginBottom: "10px" }}>
                      {lessonError}
                    </div>
                    <button
                      onClick={handleRetryLesson}
                      style={{
                        padding: "6px 14px",
                        borderRadius: "5px",
                        border: "1px solid #ef4444",
                        background: "transparent",
                        color: "#ef4444",
                        fontSize: "0.82rem",
                        fontWeight: 600,
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "5px",
                      }}
                    >
                      <FiRefreshCw size={13} /> Retry
                    </button>
                  </div>
                )}

                {/* Lesson content — only when not loading and no error */}
                {!loadingLesson && !lessonError && (
                  <>
                    {/* 1-3. Overview / Learn Tab */}
                    {activeLessonTab === "overview" && (
                      <div>
                        {lesson?.what_it_is && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              1. What It Is
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.what_it_is) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.why_it_exists && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              2. Why It Exists
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.why_it_exists) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.detailed_explanation && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              3. Detailed Explanation
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.detailed_explanation) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.step_by_step && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              Step-by-Step Walkthrough
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.step_by_step) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.terminology_and_mental_models && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              Terminology & Mental Models
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.terminology_and_mental_models) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.learning_objective && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              Learning Objective
                            </h3>
                            <p style={{ fontSize: "0.88rem", lineHeight: 1.6, marginBottom: "18px" }}>
                              {lesson.learning_objective}
                            </p>
                          </>
                        )}

                        {lesson?.real_world_applications && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                              Real-World Applications
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.real_world_applications) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {/* Fallback: show concept_summary if no rich fields available */}
                        {!lesson && activeLessonDetail && (
                          <p style={{ fontSize: "0.88rem", lineHeight: 1.6, color: "var(--cv-text-muted, #71717a)" }}>
                            No overview content available for this lesson yet.
                          </p>
                        )}
                      </div>
                    )}

                    {/* 4-5. Code & Run Tab */}
                    {activeLessonTab === "code" && (
                      <div>
                        <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                          4. Code Example
                        </h3>
                        {lesson?.starter_code ? (
                          <pre
                            style={{
                              background: "var(--cv-bg, #fbf9f4)",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              borderRadius: "8px",
                              padding: "16px",
                              fontFamily: "var(--cv-font-mono, monospace)",
                              fontSize: "0.82rem",
                              lineHeight: 1.5,
                              overflowX: "auto",
                              marginBottom: "18px",
                            }}
                          >
                            {lesson.starter_code}
                          </pre>
                        ) : (
                          <p style={{ fontSize: "0.85rem", color: "var(--cv-text-muted, #71717a)", marginBottom: "18px" }}>
                            No code example available for this lesson.
                          </p>
                        )}

                        {(lesson?.code_walkthrough || lesson?.execution_walkthrough) && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                              5. Code Walkthrough & Execution Flow
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{
                                __html: marked.parse(lesson.code_walkthrough || lesson.execution_walkthrough),
                              }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}

                        {lesson?.expected_output && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                              Expected Output
                            </h3>
                            <pre
                              style={{
                                background: "var(--cv-bg, #fbf9f4)",
                                border: "1px solid var(--cv-border, #e5e2d9)",
                                borderRadius: "6px",
                                padding: "12px 16px",
                                fontFamily: "var(--cv-font-mono, monospace)",
                                fontSize: "0.82rem",
                                lineHeight: 1.5,
                                overflowX: "auto",
                                marginBottom: "18px",
                              }}
                            >
                              {lesson.expected_output}
                            </pre>
                          </>
                        )}

                        {lesson?.debugging_tips && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                              Debugging Tips
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.debugging_tips) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}
                      </div>
                    )}

                    {/* 6. Pitfalls & Debugging Tab */}
                    {activeLessonTab === "debugging" && (
                      <div>
                        <h3 style={{ fontSize: "0.95rem", color: "#ef4444", marginBottom: "8px" }}>
                          6. Common Pitfalls & How to Debug Them
                        </h3>
                        {lesson?.common_mistakes ? (
                          <div style={{ background: "rgba(239, 68, 68, 0.05)", border: "1px solid #ef4444", borderRadius: "8px", padding: "16px", marginBottom: "18px" }}>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.common_mistakes) }}
                            />
                          </div>
                        ) : (
                          <p style={{ fontSize: "0.85rem", color: "var(--cv-text-muted, #71717a)", marginBottom: "18px" }}>
                            No common mistakes documented for this lesson.
                          </p>
                        )}

                        {lesson?.edge_cases_and_limitations && (
                          <>
                            <h3 style={{ fontSize: "0.95rem", color: "#ef4444", marginBottom: "8px" }}>
                              Edge Cases & Limitations
                            </h3>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(lesson.edge_cases_and_limitations) }}
                              style={{ marginBottom: "18px" }}
                            />
                          </>
                        )}
                      </div>
                    )}

                    {/* 7. Practice Exercise Tab */}
                    {activeLessonTab === "exercise" && (
                      <div>
                        <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "12px" }}>
                          7. Practice Exercises
                        </h3>
                        {lesson?.practice_exercises?.length > 0 ? (
                          lesson.practice_exercises.map((exercise, exIdx) => (
                            <div
                              key={exIdx}
                              style={{
                                border: "1px solid var(--cv-border, #e5e2d9)",
                                borderRadius: "8px",
                                padding: "16px",
                                marginBottom: "20px",
                                background: "var(--cv-bg, #fbf9f4)",
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                                <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>
                                  {exercise.title || `Exercise ${exIdx + 1}`}
                                </span>
                                {exercise.difficulty && (
                                  <span
                                    style={{
                                      fontSize: "0.72rem",
                                      padding: "2px 8px",
                                      borderRadius: "10px",
                                      background:
                                        exercise.difficulty.toLowerCase() === "easy"
                                          ? "rgba(16, 185, 129, 0.12)"
                                          : exercise.difficulty.toLowerCase() === "medium"
                                            ? "rgba(245, 158, 11, 0.12)"
                                            : "rgba(239, 68, 68, 0.12)",
                                      color:
                                        exercise.difficulty.toLowerCase() === "easy"
                                          ? "#10b981"
                                          : exercise.difficulty.toLowerCase() === "medium"
                                            ? "#d97706"
                                            : "#ef4444",
                                      fontWeight: 700,
                                    }}
                                  >
                                    {exercise.difficulty}
                                  </span>
                                )}
                              </div>

                              {/* Problem statement */}
                              {(exercise.problem_statement || exercise.prompt) && (
                                <div style={{ marginBottom: "12px" }}>
                                  <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                    Problem
                                  </div>
                                  <p style={{ fontSize: "0.86rem", lineHeight: 1.6, margin: 0 }}>
                                    {exercise.problem_statement || exercise.prompt}
                                  </p>
                                </div>
                              )}

                              {/* Inputs & Outputs */}
                              {exercise.given_inputs !== undefined && (
                                <div style={{ marginBottom: "8px" }}>
                                  <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                    Given Inputs
                                  </div>
                                  <pre style={{ fontSize: "0.8rem", background: "#fff", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "5px", padding: "8px 12px", margin: 0, fontFamily: "var(--cv-font-mono, monospace)" }}>
                                    {typeof exercise.given_inputs === "string"
                                      ? exercise.given_inputs
                                      : JSON.stringify(exercise.given_inputs, null, 2)}
                                  </pre>
                                </div>
                              )}

                              {exercise.expected_output !== undefined && (
                                <div style={{ marginBottom: "8px" }}>
                                  <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                    Expected Output
                                  </div>
                                  <pre style={{ fontSize: "0.8rem", background: "#fff", border: "1px solid var(--cv-border, #e5e2d9)", borderRadius: "5px", padding: "8px 12px", margin: 0, fontFamily: "var(--cv-font-mono, monospace)" }}>
                                    {typeof exercise.expected_output === "string"
                                      ? exercise.expected_output
                                      : JSON.stringify(exercise.expected_output, null, 2)}
                                  </pre>
                                </div>
                              )}

                              {/* Constraints */}
                              {exercise.constraints && (
                                <div style={{ marginBottom: "8px" }}>
                                  <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                    Constraints
                                  </div>
                                  <p style={{ fontSize: "0.82rem", lineHeight: 1.5, margin: 0, color: "var(--cv-text, #1c1c1e)" }}>
                                    {typeof exercise.constraints === "string"
                                      ? exercise.constraints
                                      : Array.isArray(exercise.constraints)
                                        ? exercise.constraints.join(", ")
                                        : JSON.stringify(exercise.constraints)}
                                  </p>
                                </div>
                              )}

                              {/* Starter code */}
                              {exercise.starter_code && (
                                <div style={{ marginBottom: "12px" }}>
                                  <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                    Starter Code
                                  </div>
                                  <pre
                                    style={{
                                      background: "#1e1e1e",
                                      color: "#d4d4d4",
                                      borderRadius: "6px",
                                      padding: "12px 14px",
                                      fontFamily: "var(--cv-font-mono, monospace)",
                                      fontSize: "0.8rem",
                                      lineHeight: 1.5,
                                      overflowX: "auto",
                                      margin: 0,
                                    }}
                                  >
                                    {exercise.starter_code}
                                  </pre>
                                </div>
                              )}

                              {/* Answer textarea */}
                              <div style={{ marginTop: "12px" }}>
                                <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--cv-text-muted, #71717a)", marginBottom: "4px", textTransform: "uppercase" }}>
                                  Your Answer
                                </div>
                                <textarea
                                  rows={5}
                                  value={exerciseAnswers[exIdx] || ""}
                                  onChange={(e) =>
                                    setExerciseAnswers((prev) => ({
                                      ...prev,
                                      [exIdx]: e.target.value,
                                    }))
                                  }
                                  placeholder="Write your solution or explanation here..."
                                  style={{
                                    width: "100%",
                                    padding: "10px",
                                    borderRadius: "6px",
                                    border: "1px solid var(--cv-border, #e5e2d9)",
                                    background: "#fff",
                                    fontSize: "0.84rem",
                                    lineHeight: 1.5,
                                    outline: "none",
                                    fontFamily: "var(--cv-font-mono, monospace)",
                                    marginBottom: "8px",
                                    boxSizing: "border-box",
                                  }}
                                />
                                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                                  <button
                                    onClick={() => handleSubmitExercise(exIdx, exercise.title)}
                                    disabled={!exerciseAnswers[exIdx]?.trim() || exerciseSubmitting[exIdx]}
                                    style={{
                                      padding: "6px 14px",
                                      borderRadius: "6px",
                                      background: "var(--cv-accent, #6366f1)",
                                      color: "#fff",
                                      border: "none",
                                      fontWeight: 600,
                                      fontSize: "0.82rem",
                                      cursor: (!exerciseAnswers[exIdx]?.trim() || exerciseSubmitting[exIdx]) ? "not-allowed" : "pointer",
                                      opacity: (!exerciseAnswers[exIdx]?.trim() || exerciseSubmitting[exIdx]) ? 0.6 : 1,
                                      display: "inline-flex",
                                      alignItems: "center",
                                      gap: "6px",
                                    }}
                                  >
                                    {exerciseSubmitting[exIdx] ? <FiRefreshCw className="spin-icon" size={13} /> : <FiSend size={13} />}
                                    Submit
                                  </button>
                                </div>
                              </div>

                              {/* Exercise feedback */}
                              {exerciseResults[exIdx] && (
                                <div
                                  style={{
                                    marginTop: "12px",
                                    padding: "14px",
                                    borderRadius: "6px",
                                    border: "1px solid var(--cv-border, #e5e2d9)",
                                    background: "var(--cv-surface, #ffffff)",
                                  }}
                                >
                                  <div style={{ fontWeight: 700, fontSize: "0.82rem", color: "var(--cv-accent, #6366f1)", marginBottom: "6px" }}>
                                    Dr. Cyra's Feedback
                                  </div>
                                  <div
                                    className="teaching-markdown-content"
                                    dangerouslySetInnerHTML={{
                                      __html: marked.parse(
                                        exerciseResults[exIdx].reply || exerciseResults[exIdx].feedback || "Feedback received."
                                      ),
                                    }}
                                  />
                                </div>
                              )}
                            </div>
                          ))
                        ) : (
                          <p style={{ fontSize: "0.85rem", color: "var(--cv-text-muted, #71717a)" }}>
                            No practice exercises available for this lesson yet.
                          </p>
                        )}
                      </div>
                    )}

                    {/* 8. Socratic Check Tab */}
                    {activeLessonTab === "check" && (
                      <div>
                        <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "8px" }}>
                          8. Socratic Understanding Check
                        </h3>
                        <div
                          style={{
                            background: "var(--cv-bg, #fbf9f4)",
                            border: "1px solid var(--cv-border, #e5e2d9)",
                            borderRadius: "8px",
                            padding: "16px",
                            marginBottom: "16px",
                          }}
                        >
                          <div style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "12px" }}>
                            {lesson?.diagnostic_question ||
                              selectedConcept?.diagnostic_question ||
                              `Explain how ${selectedConcept?.title || selectedConcept?.topic} works in ${selectedSkill} and when you would use it.`}
                          </div>

                          <textarea
                            rows={4}
                            value={learnerAnswer}
                            onChange={(e) => setLearnerAnswer(e.target.value)}
                            placeholder="Type your explanation here. Dr. Cyra Vance will assess your understanding..."
                            style={{
                              width: "100%",
                              padding: "10px",
                              borderRadius: "6px",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              background: "#fff",
                              fontSize: "0.85rem",
                              lineHeight: 1.5,
                              outline: "none",
                              marginBottom: "10px",
                              boxSizing: "border-box",
                            }}
                          />

                          <div style={{ display: "flex", justifyContent: "flex-end" }}>
                            <button
                              onClick={handleEvaluateUnderstanding}
                              disabled={!learnerAnswer.trim() || evaluating}
                              style={{
                                padding: "6px 14px",
                                borderRadius: "6px",
                                background: "var(--cv-accent, #6366f1)",
                                color: "#fff",
                                border: "none",
                                fontWeight: 600,
                                fontSize: "0.82rem",
                                cursor: (!learnerAnswer.trim() || evaluating) ? "not-allowed" : "pointer",
                                opacity: (!learnerAnswer.trim() || evaluating) ? 0.6 : 1,
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "6px",
                              }}
                            >
                              {evaluating ? <FiRefreshCw className="spin-icon" size={13} /> : <FiSend size={13} />}
                              Submit to Dr. Cyra
                            </button>
                          </div>
                        </div>

                        {evaluationResult && (
                          <div
                            style={{
                              padding: "16px",
                              borderRadius: "8px",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              background: "var(--cv-surface, #ffffff)",
                            }}
                          >
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                              <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--cv-accent, #6366f1)" }}>
                                Dr. Cyra's Evaluation
                              </span>
                              {evaluationResult.demonstrated_understanding ? (
                                <span style={{ color: "#10b981", fontSize: "0.75rem", fontWeight: 700 }}>
                                  ✓ Concept Mastered
                                </span>
                              ) : (
                                <span style={{ color: "#d97706", fontSize: "0.75rem", fontWeight: 700 }}>
                                  ⚠️ Needs Reinforcement
                                </span>
                              )}
                            </div>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{
                                __html: marked.parse(evaluationResult.reply || evaluationResult.feedback || "Evaluation complete."),
                              }}
                            />
                          </div>
                        )}
                      </div>
                    )}

                    {/* 9. Verified Resources Tab */}
                    {activeLessonTab === "resources" && (
                      <div>
                        <h3 style={{ fontSize: "0.95rem", color: "var(--cv-accent, #6366f1)", marginBottom: "12px" }}>
                          9. Verified Resources
                        </h3>
                        {lesson?.resources?.length > 0 ? (
                          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "10px" }}>
                            {lesson.resources.map((res, rIdx) => (
                              <div
                                key={rIdx}
                                style={{
                                  padding: "12px 16px",
                                  borderRadius: "6px",
                                  border: "1px solid",
                                  borderColor: res.is_verified ? "#10b981" : "var(--cv-border, #e5e2d9)",
                                  background: res.is_verified ? "rgba(16, 185, 129, 0.04)" : "var(--cv-bg, #fbf9f4)",
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                }}
                              >
                                <div>
                                  <div style={{ fontWeight: 600, fontSize: "0.85rem", marginBottom: "2px", display: "flex", alignItems: "center", gap: "6px" }}>
                                    {res.title || res.name || "Resource"}
                                    {res.is_verified ? (
                                      <span style={{ fontSize: "0.68rem", padding: "1px 6px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.12)", color: "#10b981", fontWeight: 700 }}>
                                        ✓ Verified
                                      </span>
                                    ) : (
                                      <span style={{ fontSize: "0.68rem", padding: "1px 6px", borderRadius: "8px", background: "rgba(99, 102, 241, 0.08)", color: "var(--cv-accent, #6366f1)", fontWeight: 600 }}>
                                        Suggested
                                      </span>
                                    )}
                                  </div>
                                  {res.description && (
                                    <div style={{ fontSize: "0.74rem", color: "var(--cv-text-muted, #71717a)" }}>
                                      {res.description}
                                    </div>
                                  )}
                                </div>
                                {res.canonical_url && (
                                  <a
                                    href={res.canonical_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{
                                      fontSize: "0.78rem",
                                      color: "var(--cv-accent, #6366f1)",
                                      textDecoration: "none",
                                      display: "inline-flex",
                                      alignItems: "center",
                                      gap: "4px",
                                      fontWeight: 600,
                                      whiteSpace: "nowrap",
                                      marginLeft: "12px",
                                    }}
                                  >
                                    Open <FiExternalLink size={12} />
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p style={{ fontSize: "0.85rem", color: "var(--cv-text-muted, #71717a)" }}>
                            No verified resources available for this lesson yet.
                          </p>
                        )}
                      </div>
                    )}

                    {/* Adapted Explanations History */}
                    {mentorExplanations.length > 0 && (
                      <div style={{ marginTop: "24px", borderTop: "1px solid var(--cv-border, #e5e2d9)", paddingTop: "16px" }}>
                        <h4 style={{ fontSize: "0.82rem", color: "var(--cv-text-muted, #71717a)", textTransform: "uppercase", marginBottom: "10px" }}>
                          Dr. Cyra's Adaptive Explanations
                        </h4>
                        {mentorExplanations.map((exp, i) => (
                          <div
                            key={i}
                            style={{
                              padding: "12px 14px",
                              borderRadius: "6px",
                              background: "var(--cv-bg, #fbf9f4)",
                              border: "1px solid var(--cv-border, #e5e2d9)",
                              marginBottom: "10px",
                              fontSize: "0.82rem",
                            }}
                          >
                            <div style={{ fontWeight: 600, color: "var(--cv-accent, #6366f1)", marginBottom: "4px" }}>
                              Question: {exp.prompt}
                            </div>
                            <div
                              className="teaching-markdown-content"
                              dangerouslySetInnerHTML={{ __html: marked.parse(exp.reply) }}
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ) : (
            <div style={{ padding: "40px", textAlign: "center", color: "var(--cv-text-muted, #71717a)" }}>
              Select a lesson from the roadmap to begin learning.
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

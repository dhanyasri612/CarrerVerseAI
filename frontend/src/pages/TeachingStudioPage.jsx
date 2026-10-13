import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  BookOpen,
  Code2,
  Layers,
  GitBranch,
  FileText,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  ArrowLeft,
  Bot,
  Volume2,
  Check,
  Zap,
  Award,
  Search,
  Globe,
  Lightbulb,
  Compass,
  Star,
  PanelLeftClose,
  PanelLeftOpen,
  Info,
  X,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Send,
  Terminal,
  Cpu,
  ShieldCheck,
  MessageSquare,
  FolderGit2,
} from "lucide-react";
import {
  getTeachingCurriculum,
  evaluateAndTeach,
  interactTeachingLesson,
  getTeachingProgress,
  getTeachingConceptMap,
  getSkillLearningPath,
  getProjectLearningPath,
  getRepositoryUnderstanding,
  chatWithTeachingMentor,
} from "../services/careerService";
import { useAuth } from "../context/AuthContext";

export const SUPPORTED_TEACHING_LANGUAGES = [
  { code: "en", bcp47: "en-US", label: "English", flag: "🇺🇸", native: "English" },
  { code: "ta", bcp47: "ta-IN", label: "Tamil", flag: "🇮🇳", native: "தமிழ் / Tanglish" },
  { code: "hi", bcp47: "hi-IN", label: "Hindi", flag: "🇮🇳", native: "हिन्दी / Hinglish" },
  { code: "te", bcp47: "te-IN", label: "Telugu", flag: "🇮🇳", native: "తెలుగు" },
  { code: "kn", bcp47: "kn-IN", label: "Kannada", flag: "🇮🇳", native: "ಕನ್ನಡ" },
  { code: "ml", bcp47: "ml-IN", label: "Malayalam", flag: "🇮🇳", native: "മലയാളം" },
  { code: "es", bcp47: "es-ES", label: "Spanish", flag: "🇪🇸", native: "Español" },
  { code: "fr", bcp47: "fr-FR", label: "French", flag: "🇫🇷", native: "Français" },
  { code: "de", bcp47: "de-DE", label: "German", flag: "🇩🇪", native: "Deutsch" },
];

const POPULAR_SKILLS = [
  "React",
  "Python",
  "Java",
  "SQL",
  "FastAPI",
  "Docker",
  "TypeScript",
  "PostgreSQL",
  "System Design",
  "Machine Learning",
];

export default function TeachingStudioPage() {
  const { user } = useAuth();
  const [curriculum, setCurriculum] = useState(null);
  const [teachingProgress, setTeachingProgress] = useState(null);
  const [loadingCurriculum, setLoadingCurriculum] = useState(true);

  // Teaching Room Primary Modes: 'skill' | 'project' | 'curriculum'
  const [learningMode, setLearningMode] = useState("curriculum");

  // Mode A: Skill Learning Path state
  const [selectedSkill, setSelectedSkill] = useState("React");
  const [skillPath, setSkillPath] = useState(null);
  const [loadingSkillPath, setLoadingSkillPath] = useState(false);
  const [skillSearchInput, setSkillSearchInput] = useState("");

  // Mode B: Understand My Project state
  const [selectedRepoId, setSelectedRepoId] = useState(null);
  const [repoUnderstanding, setRepoUnderstanding] = useState(null);
  const [projectJourney, setProjectJourney] = useState(null);
  const [loadingProjectData, setLoadingProjectData] = useState(false);
  const [showArchAccordion, setShowArchAccordion] = useState(false);
  const [projectSubTab, setProjectSubTab] = useState("stages"); // 'stages' | 'interview'

  // General navigation state
  const [activeSectionId, setActiveSectionId] = useState("dsa");
  const [activeLessonIndex, setActiveLessonIndex] = useState(0);
  const [lessonSearchQuery, setLessonSearchQuery] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("en");

  // Layout panels toggles
  const [showNavigator, setShowNavigator] = useState(true);
  const [showContextPanel, setShowContextPanel] = useState(false);

  // Knowledge Concept Graph state
  const [conceptMap, setConceptMap] = useState(null);
  const [showConceptMap, setShowConceptMap] = useState(false);
  const [loadingConceptMap, setLoadingConceptMap] = useState(false);
  const [selectedConceptNode, setSelectedConceptNode] = useState(null);

  // Candidate submission state
  const [candidateThoughts, setCandidateThoughts] = useState("");
  const [candidateCode, setCandidateCode] = useState("");
  const [showCodeInput, setShowCodeInput] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [teachingResult, setTeachingResult] = useState(null);
  const [activeHint, setActiveHint] = useState(null);
  const [activeSimplerExample, setActiveSimplerExample] = useState(null);
  const [activeCodeDemo, setActiveCodeDemo] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Conversational Tutor (Dr. Cyra Vance) Chat state
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [isAssessmentChat, setIsAssessmentChat] = useState(false);
  const [isSendingChat, setIsSendingChat] = useState(false);

  // 1. Load initial curriculum & progress
  useEffect(() => {
    async function loadData() {
      try {
        setLoadingCurriculum(true);
        const [currRes, progRes] = await Promise.allSettled([
          getTeachingCurriculum(),
          getTeachingProgress(),
        ]);
        if (currRes.status === "fulfilled") {
          setCurriculum(currRes.value);
          // If candidate has projects, pre-select first project
          const projSection = currRes.value?.sections?.find((s) => s.id === "projects");
          if (projSection && projSection.lessons?.length > 0) {
            const firstProj = projSection.lessons[0];
            const matchId = firstProj.id?.replace("proj-", "");
            if (matchId) setSelectedRepoId(matchId);
          }
        }
        if (progRes.status === "fulfilled") setTeachingProgress(progRes.value);
      } catch (err) {
        console.warn("Failed to load curriculum from server, using fallback:", err);
      } finally {
        setLoadingCurriculum(false);
      }
    }
    loadData();
  }, []);

  // 2. Load Mode A: Skill Learning Path
  useEffect(() => {
    async function fetchSkillPath() {
      if (!selectedSkill) return;
      try {
        setLoadingSkillPath(true);
        const data = await getSkillLearningPath(selectedSkill);
        setSkillPath(data);
      } catch (err) {
        console.warn("Failed to load skill learning path:", err);
      } finally {
        setLoadingSkillPath(false);
      }
    }
    if (learningMode === "skill") {
      fetchSkillPath();
    }
  }, [selectedSkill, learningMode]);

  // 3. Load Mode B: Project Understanding & Learning Path
  useEffect(() => {
    async function fetchProjectData() {
      if (!selectedRepoId) return;
      try {
        setLoadingProjectData(true);
        const [underRes, journeyRes] = await Promise.allSettled([
          getRepositoryUnderstanding(selectedRepoId),
          getProjectLearningPath(selectedRepoId),
        ]);
        if (underRes.status === "fulfilled") setRepoUnderstanding(underRes.value);
        if (journeyRes.status === "fulfilled") setProjectJourney(journeyRes.value);
      } catch (err) {
        console.warn("Failed to load repository understanding:", err);
      } finally {
        setLoadingProjectData(false);
      }
    }
    if (learningMode === "project" && selectedRepoId) {
      fetchProjectData();
    }
  }, [selectedRepoId, learningMode]);

  // Derive active lesson based on mode
  let activeSection = curriculum?.sections?.find((s) => s.id === activeSectionId) || curriculum?.sections?.[0];
  let activeLesson = activeSection?.lessons?.[activeLessonIndex] || activeSection?.lessons?.[0];

  // If in skill mode and skill path loaded, sync active lesson
  if (learningMode === "skill" && skillPath?.stages?.length > 0) {
    const allSkillLessons = skillPath.stages.flatMap((s) => s.lessons);
    if (allSkillLessons[activeLessonIndex]) {
      activeLesson = allSkillLessons[activeLessonIndex];
    }
  } else if (learningMode === "project" && projectJourney?.stages?.length > 0) {
    const allProjLessons = projectJourney.stages.flatMap((s) => s.lessons);
    if (allProjLessons[activeLessonIndex]) {
      activeLesson = allProjLessons[activeLessonIndex];
    }
  }

  // Derive statistics
  const totalLessonsInCurriculum =
    curriculum?.sections?.reduce((acc, s) => acc + (s.lessons?.length || 0), 0) || 0;
  const completedCount = teachingProgress?.completed_lessons?.length || 0;
  const masteredCount = teachingProgress?.mastered_lessons?.length || 0;

  // Reset thought & result when switching lessons
  const handleSelectLesson = (sectionId, lessonIdx) => {
    setActiveSectionId(sectionId);
    setActiveLessonIndex(lessonIdx);
    setCandidateThoughts("");
    setCandidateCode("");
    setTeachingResult(null);
    setActiveHint(null);
    setActiveSimplerExample(null);
    setActiveCodeDemo(null);
    setErrorMsg("");
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // Toggle Interactive Concept Knowledge Graph
  const handleToggleConceptMap = async () => {
    const nextShow = !showConceptMap;
    setShowConceptMap(nextShow);
    if (nextShow) {
      setLoadingConceptMap(true);
      try {
        const data = await getTeachingConceptMap(activeLesson?.id);
        const parsed = data?.data || data;
        setConceptMap(parsed);
        if (parsed?.nodes?.length > 0) {
          const current = parsed.nodes.find((n) => n.is_current) || parsed.nodes[0];
          setSelectedConceptNode(current);
        }
      } catch (err) {
        console.warn("Failed to load concept map:", err);
      } finally {
        setLoadingConceptMap(false);
      }
    }
  };

  // Refresh repository analysis with forced re-indexing
  const handleRefreshRepoAnalysis = async () => {
    if (!selectedRepoId) return;
    try {
      setLoadingProjectData(true);
      const [underRes, journeyRes] = await Promise.allSettled([
        getRepositoryUnderstanding(selectedRepoId, true),
        getProjectLearningPath(selectedRepoId, true),
      ]);
      if (underRes.status === "fulfilled") setRepoUnderstanding(underRes.value);
      if (journeyRes.status === "fulfilled") setProjectJourney(journeyRes.value);
    } catch (err) {
      console.warn("Error refreshing repo analysis:", err);
    } finally {
      setLoadingProjectData(false);
    }
  };

  // Socratic Action Handler (hint, simpler, explain, code, why, practice, assess)
  const handleSocraticAction = async (action) => {
    setIsEvaluating(true);
    setErrorMsg("");
    try {
      const payload = {
        section_id: activeSectionId,
        lesson_id: activeLesson?.id || "lesson",
        action,
        candidate_response: candidateThoughts || null,
        candidate_code: candidateCode || null,
        language: selectedLanguage,
      };
      const res = await interactTeachingLesson(payload);
      if (res.hint_revealed) {
        setActiveHint(res.hint_revealed);
      }
      if (res.example_grounding) {
        setActiveSimplerExample(res.example_grounding);
      }
      if (res.code_demonstration) {
        setActiveCodeDemo(res.code_demonstration);
      }
      if (res.what_is_right || res.step_by_step_explanation) {
        setTeachingResult({
          what_is_right: res.what_is_right,
          what_is_wrong: res.what_is_wrong,
          masterclass_lesson: res.step_by_step_explanation || res.teaching_message,
          optimal_solution: res.code_demonstration || "",
          key_takeaway: "Master foundational engineering invariants and complexity bounds.",
          suggested_follow_up: res.follow_up_question,
        });
      } else if (res.teaching_message && !res.hint_revealed && !res.example_grounding && !res.code_demonstration) {
        setTeachingResult({
          what_is_right: res.assessment_evaluation?.notes?.join(" ") || "Socratic Deep Dive",
          what_is_wrong: res.assessment_evaluation?.score < 80 ? "Refine constraints and edge cases to reach 80+ mastery." : "",
          masterclass_lesson: res.teaching_message,
          optimal_solution: res.code_demonstration || "",
          key_takeaway: "Master foundational engineering invariants and complexity bounds.",
          suggested_follow_up: res.follow_up_question,
        });
      }
      if (res.is_lesson_complete || res.action === "assess") {
        getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => {});
      }
    } catch (err) {
      console.warn("Socratic interaction error:", err);
      setErrorMsg("Failed to execute Socratic action. Please try again.");
    } finally {
      setIsEvaluating(false);
    }
  };

  // Submit thought process for evaluation and teaching
  const handleSubmitThoughts = async (e) => {
    e?.preventDefault();
    if (!candidateThoughts.trim()) {
      setErrorMsg("Please write down your thoughts, intuition, or approach first so Cyra can teach you!");
      return;
    }
    setErrorMsg("");
    setIsEvaluating(true);

    try {
      const payload = {
        section_id: activeSectionId,
        lesson_id: activeLesson?.id || "lesson",
        concept_title: activeLesson?.title || activeLesson?.topic,
        question_prompt: activeLesson?.challenge_question,
        candidate_thoughts: candidateThoughts,
        candidate_code: candidateCode || null,
        role: curriculum?.target_role || "Software Engineer (SDE)",
        language: selectedLanguage,
      };

      const result = await evaluateAndTeach(payload);
      setTeachingResult(result);

      // Refresh persisted progress
      getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => {});

      // Speak Cyra's affirmation & right/wrong feedback in selected language
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const speechText = result.what_is_right ? result.what_is_right.slice(0, 160) : "Great approach.";
        const utterance = new SpeechSynthesisUtterance(speechText);
        const langObj = SUPPORTED_TEACHING_LANGUAGES.find((l) => l.code === selectedLanguage) || SUPPORTED_TEACHING_LANGUAGES[0];
        utterance.lang = langObj.bcp47;
        const voices = window.speechSynthesis.getVoices();
        const matchVoice = voices.find((v) => v.lang === langObj.bcp47 || v.lang.startsWith(langObj.code));
        if (matchVoice) utterance.voice = matchVoice;
        utterance.rate = 1.0;
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      console.error("Evaluation error:", err);
      setErrorMsg("Failed to connect to Cyra's pedagogical engine. Please try again.");
    } finally {
      setIsEvaluating(false);
    }
  };

  // Send Conversational Chat Turn to Dr. Cyra Vance
  const handleSendChatMessage = async (e, customMessage = null) => {
    e?.preventDefault();
    const msgToSend = (customMessage || chatInput).trim();
    if (!msgToSend) return;

    const userTurn = {
      role: "user",
      content: msgToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const newMessages = [...chatMessages, userTurn];
    setChatMessages(newMessages);
    if (!customMessage) setChatInput("");
    setIsSendingChat(true);

    try {
      const payload = {
        mode: learningMode,
        target_id: learningMode === "skill" ? selectedSkill : (learningMode === "project" ? String(selectedRepoId || "repo") : activeSectionId),
        lesson_id: activeLesson?.id || null,
        message: msgToSend,
        chat_history: newMessages,
        is_assessment: isAssessmentChat,
        code_workspace: candidateCode || null,
        language: selectedLanguage,
      };

      const res = await chatWithTeachingMentor(payload);
      const cyraTurn = {
        role: "cyra",
        content: res.reply,
        citations: res.citations || [],
        suggested_follow_ups: res.suggested_follow_ups || [],
        is_assessment: res.is_assessment,
        demonstrated_understanding: res.demonstrated_understanding,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setChatMessages([...newMessages, cyraTurn]);

      if (res.demonstrated_understanding) {
        getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => {});
      }
    } catch (err) {
      console.warn("Chat with Cyra error:", err);
      setChatMessages([
        ...newMessages,
        {
          role: "cyra",
          content: "I ran into a temporary connection issue. Let's try again in a moment!",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsSendingChat(false);
    }
  };

  // Speak the lesson in selected language
  const handleSpeakLesson = () => {
    if (!("speechSynthesis" in window)) return;
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    const textToSpeak = teachingResult
      ? `${teachingResult.masterclass_lesson} Key takeaway: ${teachingResult.key_takeaway}`
      : `${activeLesson?.concept_summary} Challenge: ${activeLesson?.challenge_question}`;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(textToSpeak.slice(0, 450));
    const langObj = SUPPORTED_TEACHING_LANGUAGES.find((l) => l.code === selectedLanguage) || SUPPORTED_TEACHING_LANGUAGES[0];
    utterance.lang = langObj.bcp47;
    const voices = window.speechSynthesis.getVoices();
    const matchVoice = voices.find((v) => v.lang === langObj.bcp47 || v.lang.startsWith(langObj.code));
    if (matchVoice) utterance.voice = matchVoice;
    utterance.rate = 1.0;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const getSectionIcon = (iconName) => {
    switch (iconName) {
      case "code":
        return <Code2 size={16} />;
      case "layers":
        return <Layers size={16} />;
      case "git-branch":
        return <GitBranch size={16} />;
      case "file-text":
      default:
        return <FileText size={16} />;
    }
  };

  // Collect connected repositories for Mode B
  const connectedRepos = curriculum?.sections?.find((s) => s.id === "projects")?.lessons || [];

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--cv-bg, #f3f0e6)",
        color: "var(--cv-text, #20242d)",
        fontFamily: "var(--cv-font-sans, 'Plus Jakarta Sans', sans-serif)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* ── 1. EDITORIAL STUDIO TOP NAVIGATION ────────────────────────── */}
      <header
        style={{
          background: "var(--cv-paper, #fbf9f4)",
          borderBottom: "1px solid var(--cv-rule, #ded9cb)",
          padding: "14px 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "14px",
          position: "sticky",
          top: 0,
          zIndex: 40,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "18px" }}>
          <Link
            to="/dashboard"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              color: "var(--cv-muted, #686b70)",
              textDecoration: "none",
              fontSize: "0.84rem",
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={15} />
            <span>Studio Home</span>
          </Link>

          <div style={{ width: "1px", height: "18px", background: "var(--cv-rule, #ded9cb)" }} />

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              style={{
                fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)",
                fontSize: "1.2rem",
                color: "var(--cv-text, #20242d)",
                letterSpacing: "-0.01em",
              }}
            >
              AI Teaching & Socratic Studio
            </span>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                fontSize: "0.74rem",
                color: "var(--cv-accent, #203d9b)",
                background: "var(--cv-accent-soft, #e0e5f5)",
                padding: "2px 8px",
                borderRadius: "4px",
                fontWeight: 600,
              }}
            >
              <Bot size={13} />
              Dr. Cyra Vance
            </span>
          </div>
        </div>

        {/* Studio Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          {/* Navigator Toggle Button */}
          <button
            type="button"
            onClick={() => setShowNavigator(!showNavigator)}
            aria-label="Toggle curriculum navigator"
            title={showNavigator ? "Hide Curriculum Navigator" : "Show Curriculum Navigator"}
            style={{
              background: "transparent",
              border: "1px solid var(--cv-rule, #ded9cb)",
              color: "var(--cv-text, #20242d)",
              padding: "6px 12px",
              borderRadius: "4px",
              fontSize: "0.8rem",
              fontWeight: 500,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            {showNavigator ? <PanelLeftClose size={14} /> : <PanelLeftOpen size={14} />}
            <span>{showNavigator ? "Hide Curriculum" : "Curriculum"}</span>
          </button>

          {/* Language Selector */}
          <div style={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              aria-label="Language selection"
              style={{
                background: "var(--cv-paper, #fbf9f4)",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderRadius: "4px",
                padding: "6px 28px 6px 10px",
                fontSize: "0.8rem",
                color: "var(--cv-text, #20242d)",
                cursor: "pointer",
                appearance: "none",
                fontWeight: 500,
                outline: "none",
              }}
            >
              {SUPPORTED_TEACHING_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.native}
                </option>
              ))}
            </select>
            <Globe
              size={13}
              style={{ position: "absolute", right: 8, pointerEvents: "none", color: "var(--cv-muted, #686b70)" }}
            />
          </div>

          {/* Cyra Voice Button */}
          <button
            type="button"
            onClick={handleSpeakLesson}
            aria-label="Listen to Dr. Cyra lesson"
            style={{
              background: isSpeaking ? "var(--cv-accent, #203d9b)" : "transparent",
              border: "1px solid " + (isSpeaking ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
              color: isSpeaking ? "#ffffff" : "var(--cv-text, #20242d)",
              padding: "6px 12px",
              borderRadius: "4px",
              fontSize: "0.8rem",
              fontWeight: 500,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Volume2 size={14} />
            <span>{isSpeaking ? "Stop Voice" : "Listen to Cyra"}</span>
          </button>

          {/* Concept Knowledge Graph Toggle */}
          <button
            type="button"
            onClick={handleToggleConceptMap}
            aria-label="Knowledge Map"
            style={{
              background: showConceptMap ? "var(--cv-accent, #203d9b)" : "transparent",
              border: "1px solid " + (showConceptMap ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
              color: showConceptMap ? "#ffffff" : "var(--cv-text, #20242d)",
              padding: "6px 12px",
              borderRadius: "4px",
              fontSize: "0.8rem",
              fontWeight: 500,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Compass size={14} />
            <span>Knowledge Map</span>
          </button>

          {/* Context References Toggle */}
          <button
            type="button"
            onClick={() => setShowContextPanel(!showContextPanel)}
            aria-label="Toggle reference panel"
            style={{
              background: showContextPanel ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
              border: "1px solid var(--cv-rule, #ded9cb)",
              color: "var(--cv-text, #20242d)",
              padding: "6px 10px",
              borderRadius: "4px",
              fontSize: "0.8rem",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
          >
            <Info size={14} />
            <span>References</span>
          </button>
        </div>
      </header>

      {/* ── 2. TWO PRIMARY ENTRY MODES (Learn a Skill vs Understand My Project) ───────── */}
      <div
        style={{
          background: "var(--cv-paper, #fbf9f4)",
          borderBottom: "1px solid var(--cv-rule, #ded9cb)",
          padding: "12px 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "14px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.74rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--cv-muted, #686b70)", fontWeight: 700, marginRight: "4px" }}>
            Mentorship Mode:
          </span>

          <button
            type="button"
            onClick={() => setLearningMode("skill")}
            style={{
              padding: "7px 16px",
              borderRadius: "4px",
              border: "1px solid " + (learningMode === "skill" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
              background: learningMode === "skill" ? "var(--cv-accent, #203d9b)" : "transparent",
              color: learningMode === "skill" ? "#ffffff" : "var(--cv-text, #20242d)",
              fontSize: "0.82rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Layers size={14} />
            <span>Mode A: Learn a Skill</span>
          </button>

          <button
            type="button"
            onClick={() => setLearningMode("project")}
            style={{
              padding: "7px 16px",
              borderRadius: "4px",
              border: "1px solid " + (learningMode === "project" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
              background: learningMode === "project" ? "var(--cv-accent, #203d9b)" : "transparent",
              color: learningMode === "project" ? "#ffffff" : "var(--cv-text, #20242d)",
              fontSize: "0.82rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <FolderGit2 size={14} />
            <span>Mode B: Understand My Project</span>
          </button>

          <button
            type="button"
            onClick={() => setLearningMode("curriculum")}
            style={{
              padding: "7px 14px",
              borderRadius: "4px",
              border: "1px solid " + (learningMode === "curriculum" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
              background: learningMode === "curriculum" ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
              color: learningMode === "curriculum" ? "var(--cv-accent, #203d9b)" : "var(--cv-muted, #686b70)",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
          >
            <Code2 size={13} />
            <span>DSA & Behavioral Track</span>
          </button>
        </div>

        {/* Verified Studio Progress Counter */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "0.82rem", color: "var(--cv-muted, #686b70)" }}>
          <span>
            Progress: <strong>{completedCount}</strong> lessons completed
          </span>
          {masteredCount > 0 && (
            <span style={{ color: "var(--cv-warning, #a56f36)", fontWeight: 700 }}>
              • {masteredCount} Mastered ★
            </span>
          )}
        </div>
      </div>

      {/* Mode A Selector Chips (Skill Selector) */}
      {learningMode === "skill" && (
        <div
          style={{
            background: "var(--cv-paper, #fbf9f4)",
            borderBottom: "1px solid var(--cv-rule, #ded9cb)",
            padding: "10px 28px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            overflowX: "auto",
          }}
        >
          <span style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-muted, #686b70)", marginRight: "4px", flexShrink: 0 }}>
            Select Technology:
          </span>
          {POPULAR_SKILLS.map((sk) => {
            const isSel = selectedSkill.toLowerCase() === sk.toLowerCase();
            return (
              <button
                key={sk}
                type="button"
                onClick={() => setSelectedSkill(sk)}
                style={{
                  padding: "4px 10px",
                  borderRadius: "3px",
                  fontSize: "0.76rem",
                  fontWeight: isSel ? 700 : 500,
                  border: "1px solid " + (isSel ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                  background: isSel ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                  color: isSel ? "var(--cv-accent, #203d9b)" : "var(--cv-text, #20242d)",
                  cursor: "pointer",
                  flexShrink: 0,
                }}
              >
                {sk}
              </button>
            );
          })}
        </div>
      )}

      {/* Mode B Selector Bar (Connected GitHub Repositories) */}
      {learningMode === "project" && (
        <div
          style={{
            background: "var(--cv-paper, #fbf9f4)",
            borderBottom: "1px solid var(--cv-rule, #ded9cb)",
            padding: "10px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-muted, #686b70)" }}>
              Connected Repository:
            </span>
            {connectedRepos.length > 0 ? (
              connectedRepos.map((r, idx) => {
                const rId = r.id?.replace("proj-", "") || idx;
                const isSel = selectedRepoId === rId || (!selectedRepoId && idx === 0);
                return (
                  <button
                    key={r.id || idx}
                    type="button"
                    onClick={() => setSelectedRepoId(rId)}
                    style={{
                      padding: "4px 12px",
                      borderRadius: "3px",
                      fontSize: "0.78rem",
                      fontWeight: isSel ? 700 : 500,
                      border: "1px solid " + (isSel ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                      background: isSel ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                      color: isSel ? "var(--cv-accent, #203d9b)" : "var(--cv-text, #20242d)",
                      cursor: "pointer",
                    }}
                  >
                    📦 {r.title?.split("•")[0]?.trim() || "Repository"}
                  </button>
                );
              })
            ) : (
              <span style={{ fontSize: "0.78rem", color: "var(--cv-muted, #686b70)" }}>
                No connected repositories. (Showing Architecture Masterclass).
              </span>
            )}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              type="button"
              onClick={handleRefreshRepoAnalysis}
              disabled={loadingProjectData}
              style={{
                background: "transparent",
                border: "1px solid var(--cv-rule, #ded9cb)",
                padding: "4px 10px",
                borderRadius: "3px",
                fontSize: "0.74rem",
                color: "var(--cv-text, #20242d)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              <RefreshCw size={12} className={loadingProjectData ? "spin" : ""} />
              <span>{loadingProjectData ? "Analyzing..." : "Refresh Analysis"}</span>
            </button>
            <button
              type="button"
              onClick={() => setShowArchAccordion(!showArchAccordion)}
              style={{
                background: showArchAccordion ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                border: "1px solid var(--cv-rule, #ded9cb)",
                padding: "4px 10px",
                borderRadius: "3px",
                fontSize: "0.74rem",
                color: "var(--cv-accent, #203d9b)",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {showArchAccordion ? "Hide 13-Point Architecture ✕" : "Explore 13-Point Architecture ▼"}
            </button>
          </div>
        </div>
      )}

      {/* Mode B: 13-Point Repository Understanding Accordion */}
      {learningMode === "project" && showArchAccordion && repoUnderstanding && (
        <section
          style={{
            background: "#ffffff",
            borderBottom: "1px solid var(--cv-rule, #ded9cb)",
            padding: "20px 28px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <div>
              <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                Verified Repository Understanding Model: {repoUnderstanding.repository_name}
              </h3>
              <p style={{ margin: "2px 0 0 0", fontSize: "0.8rem", color: "var(--cv-muted, #686b70)" }}>
                Grounded analysis from {repoUnderstanding.source_file_count} verified source files and documentation.
              </p>
            </div>
            <span style={{ fontSize: "0.72rem", background: "#f0fdf4", color: "#166534", padding: "3px 8px", borderRadius: "3px", fontWeight: 700 }}>
              ✓ Verified Source Grounding
            </span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", fontSize: "0.85rem", lineHeight: 1.55 }}>
            <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
              <strong>1. Problem & Purpose:</strong>
              <div style={{ marginTop: "4px", color: "#374151" }}>{repoUnderstanding.project_purpose}</div>

              <div style={{ marginTop: "10px" }}>
                <strong>2. Tech Stack:</strong>
                <div style={{ marginTop: "3px", display: "flex", gap: "4px", flexWrap: "wrap" }}>
                  {repoUnderstanding.main_technologies?.map((t) => (
                    <span key={t} style={{ background: "#e2e8f0", padding: "2px 6px", borderRadius: "3px", fontSize: "0.72rem" }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: "10px" }}>
                <strong>3. Request Flow:</strong>
                <div style={{ marginTop: "3px", color: "#374151" }}>{repoUnderstanding.request_flow}</div>
              </div>

              <div style={{ marginTop: "10px" }}>
                <strong>4. Database Flow:</strong>
                <div style={{ marginTop: "3px", color: "#374151" }}>{repoUnderstanding.database_flow}</div>
              </div>
            </div>

            <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
              <strong>5. Security & Auth Flow:</strong>
              <div style={{ marginTop: "4px", color: "#374151" }}>{repoUnderstanding.auth_security_flow}</div>

              <div style={{ marginTop: "10px" }}>
                <strong>6. Application Entry Points:</strong>
                <div style={{ marginTop: "3px", fontFamily: "var(--cv-font-mono, monospace)", fontSize: "0.78rem" }}>
                  {repoUnderstanding.application_entry_points?.join(", ") || "README.md"}
                </div>
              </div>

              <div style={{ marginTop: "10px" }}>
                <strong>7. Architectural Strengths:</strong>
                <ul style={{ margin: "4px 0 0 16px", padding: 0 }}>
                  {repoUnderstanding.architectural_strengths?.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>

              <div style={{ marginTop: "10px" }}>
                <strong>8. Verified Citations:</strong>
                <div style={{ marginTop: "3px", fontSize: "0.75rem", color: "var(--cv-muted, #686b70)" }}>
                  {repoUnderstanding.source_evidence_citations?.slice(0, 3).map((c, idx) => (
                    <span key={idx} style={{ display: "inline-block", marginRight: "8px" }}>
                      📁 {c.file_path}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ── 3. MAIN WORKBENCH GRID ────────────────────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: showNavigator ? "320px 1fr" : "1fr",
          flex: 1,
          transition: "grid-template-columns 0.2s ease",
        }}
      >
        {/* ── LEFT: COLLAPSIBLE CURRICULUM NAVIGATOR ───────────────────────── */}
        {showNavigator && (
          <aside
            style={{
              background: "var(--cv-paper, #fbf9f4)",
              borderRight: "1px solid var(--cv-rule, #ded9cb)",
              padding: "20px 18px",
              display: "flex",
              flexDirection: "column",
              gap: "14px",
              overflowY: "auto",
              maxHeight: "calc(100vh - 120px)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.76rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--cv-muted, #686b70)" }}>
                {learningMode === "skill" ? `${selectedSkill} Stages` : (learningMode === "project" ? "Project Stages" : "Curriculum")}
              </span>
              <span style={{ fontSize: "0.72rem", color: "var(--cv-muted, #686b70)" }}>
                {learningMode === "skill" ? `${skillPath?.total_lessons || 0} lessons` : `${curriculum?.total_lessons || 0} lessons`}
              </span>
            </div>

            {/* Mode A: Skill Stages & Lessons */}
            {learningMode === "skill" && skillPath?.stages && (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {skillPath.stages.map((stage) => (
                  <div key={stage.stage_number} style={{ borderBottom: "1px solid var(--cv-rule, #ded9cb)", paddingBottom: "8px" }}>
                    <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--cv-accent, #203d9b)", marginBottom: "4px" }}>
                      Stage {stage.stage_number} • {stage.stage_name}
                    </div>
                    {stage.lessons.map((les) => {
                      const isLesActive = activeLesson?.id === les.id;
                      return (
                        <button
                          key={les.id}
                          type="button"
                          onClick={() => {
                            setActiveSectionId("skills");
                            const allLessons = skillPath.stages.flatMap((s) => s.lessons);
                            const idx = allLessons.findIndex((l) => l.id === les.id);
                            setActiveLessonIndex(idx >= 0 ? idx : 0);
                          }}
                          style={{
                            width: "100%",
                            textAlign: "left",
                            padding: "6px 8px",
                            borderRadius: "3px",
                            border: "none",
                            background: isLesActive ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                            color: isLesActive ? "var(--cv-accent, #203d9b)" : "var(--cv-text, #20242d)",
                            fontSize: "0.78rem",
                            fontWeight: isLesActive ? 700 : 500,
                            cursor: "pointer",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {les.title}
                          </span>
                          {les.is_demonstrated && <span style={{ color: "#16a34a", fontSize: "0.7rem" }}>★</span>}
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            )}

            {/* Mode B: Project Stages & Lessons */}
            {learningMode === "project" && projectJourney?.stages && (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {projectJourney.stages.map((stage) => (
                  <div key={stage.stage_number} style={{ borderBottom: "1px solid var(--cv-rule, #ded9cb)", paddingBottom: "8px" }}>
                    <div style={{ fontSize: "0.74rem", fontWeight: 700, color: "var(--cv-accent, #203d9b)", marginBottom: "4px" }}>
                      Stage {stage.stage_number} • {stage.stage_name}
                    </div>
                    {stage.lessons.map((les) => {
                      const isLesActive = activeLesson?.id === les.id;
                      return (
                        <button
                          key={les.id}
                          type="button"
                          onClick={() => {
                            setActiveSectionId("projects");
                            const allLessons = projectJourney.stages.flatMap((s) => s.lessons);
                            const idx = allLessons.findIndex((l) => l.id === les.id);
                            setActiveLessonIndex(idx >= 0 ? idx : 0);
                          }}
                          style={{
                            width: "100%",
                            textAlign: "left",
                            padding: "6px 8px",
                            borderRadius: "3px",
                            border: "none",
                            background: isLesActive ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                            color: isLesActive ? "var(--cv-accent, #203d9b)" : "var(--cv-text, #20242d)",
                            fontSize: "0.78rem",
                            fontWeight: isLesActive ? 700 : 500,
                            cursor: "pointer",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {les.title}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            )}

            {/* Mode C: Standard Curriculum (DSA & STAR) */}
            {learningMode === "curriculum" && (
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                {(activeSection?.lessons || []).map((les, idx) => {
                  const isLesActive = idx === activeLessonIndex;
                  return (
                    <button
                      key={les.id}
                      type="button"
                      onClick={() => handleSelectLesson(activeSectionId, idx)}
                      style={{
                        width: "100%",
                        textAlign: "left",
                        padding: "8px 10px",
                        borderRadius: "3px",
                        border: "1px solid " + (isLesActive ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                        background: isLesActive ? "var(--cv-accent-soft, #e0e5f5)" : "transparent",
                        color: isLesActive ? "var(--cv-accent, #203d9b)" : "var(--cv-text, #20242d)",
                        fontSize: "0.8rem",
                        fontWeight: isLesActive ? 700 : 500,
                        cursor: "pointer",
                      }}
                    >
                      {les.title}
                    </button>
                  );
                })}
              </div>
            )}
          </aside>
        )}

        {/* ── CENTER: ACTIVE LESSON & CONVERSATIONAL WORKBENCH ─────────────── */}
        <main
          style={{
            padding: "24px 32px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            maxWidth: "960px",
            margin: "0 auto",
            width: "100%",
            boxSizing: "border-box",
          }}
        >
          {/* Active Lesson Header Banner */}
          <header style={{ borderBottom: "1px solid var(--cv-rule, #ded9cb)", paddingBottom: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span
                style={{
                  fontSize: "0.72rem",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  background: "var(--cv-accent-soft, #e0e5f5)",
                  color: "var(--cv-accent, #203d9b)",
                  padding: "3px 8px",
                  borderRadius: "3px",
                  fontWeight: 700,
                }}
              >
                {activeLesson?.stage_name || "Foundations"} • {activeLesson?.difficulty || "Medium"}
              </span>
              <span style={{ fontSize: "0.76rem", color: "var(--cv-muted, #686b70)" }}>
                {activeLesson?.grounding_source}
              </span>
            </div>

            <h1
              style={{
                margin: "0 0 6px 0",
                fontSize: "1.45rem",
                fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)",
                color: "var(--cv-text, #20242d)",
              }}
            >
              {activeLesson?.title || "Interactive Technical Lesson"}
            </h1>

            <p style={{ margin: 0, fontSize: "0.92rem", lineHeight: 1.55, color: "#374151" }}>
              {activeLesson?.concept_summary}
            </p>

            {/* Learning Objective Callout */}
            {activeLesson?.learning_objective && (
              <div style={{ marginTop: "10px", fontSize: "0.82rem", color: "var(--cv-accent, #203d9b)", fontWeight: 600 }}>
                🎯 Objective: {activeLesson.learning_objective}
              </div>
            )}
          </header>

          {/* ── DR. CYRA SOCRATIC INQUIRY BUBBLE ─────────────────────────── */}
          <section
            aria-label="Socratic challenge"
            style={{
              background: "var(--cv-paper, #fbf9f4)",
              border: "1px solid var(--cv-rule, #ded9cb)",
              borderRadius: "4px",
              padding: "20px 24px",
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Bot size={18} color="var(--cv-accent, #203d9b)" />
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                Dr. Cyra Vance asks:
              </span>
            </div>

            <div
              style={{
                fontSize: "1rem",
                lineHeight: 1.6,
                color: "var(--cv-text, #20242d)",
                whiteSpace: "pre-line",
              }}
            >
              {activeLesson?.challenge_question}
            </div>

            {/* Diagnostic Self-Check Question Callout */}
            {activeLesson?.diagnostic_question && (
              <div
                style={{
                  borderTop: "1px solid var(--cv-rule, #ded9cb)",
                  paddingTop: "12px",
                  marginTop: "6px",
                  display: "flex",
                  gap: "10px",
                  alignItems: "baseline",
                }}
              >
                <HelpCircle size={15} color="var(--cv-accent, #203d9b)" style={{ flexShrink: 0 }} />
                <div>
                  <div
                    style={{
                      fontSize: "0.72rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      fontWeight: 700,
                      color: "var(--cv-accent, #203d9b)",
                    }}
                  >
                    Diagnostic Check • Diagnostic Self-Check Question
                  </div>
                  <div style={{ fontSize: "0.86rem", color: "var(--cv-text, #20242d)", marginTop: "2px", lineHeight: 1.5 }}>
                    {activeLesson.diagnostic_question}
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* ── SOCRATIC ASSISTANCE BAR (Clean & Uncluttered) ──────────── */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "10px",
              borderTop: "1px solid var(--cv-rule, #ded9cb)",
              paddingTop: "14px",
            }}
          >
            <span style={{ fontSize: "0.78rem", color: "var(--cv-muted, #686b70)", fontWeight: 600 }}>
              Need assistance before responding?
            </span>

            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              <button
                type="button"
                onClick={() => handleSocraticAction("hint")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Lightbulb size={13} color="var(--cv-warning, #a56f36)" />
                <span>💡 Reveal Hint</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocraticAction("simpler")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Compass size={13} color="var(--cv-accent, #203d9b)" />
                <span>🔍 Simpler Toy Example • Simpler Example</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocraticAction("explain")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <BookOpen size={13} />
                <span>🎓 Masterclass</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocraticAction("why")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Zap size={13} />
                <span>🧠 Why This Pattern</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocraticAction("code")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Code2 size={13} />
                <span>💻 Show Reference Code • Starter Code</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocraticAction("assess")}
                disabled={isEvaluating}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  color: "var(--cv-text, #20242d)",
                  padding: "6px 12px",
                  borderRadius: "4px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Award size={13} />
                <span>📝 Assess Mastery</span>
              </button>
            </div>
          </div>

          {/* ── ACTIVE REVEALED SOCRATIC BANNERS ───────────────────────── */}
          {activeHint && (
            <div
              style={{
                background: "#faf7ed",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderLeft: "4px solid var(--cv-warning, #a56f36)",
                padding: "16px 20px",
                borderRadius: "4px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-warning, #a56f36)" }}>
                  Socratic Hint
                </span>
                <button
                  type="button"
                  onClick={() => setActiveHint(null)}
                  style={{ background: "transparent", border: "none", color: "var(--cv-muted, #686b70)", cursor: "pointer", fontSize: "0.75rem" }}
                >
                  Dismiss ✕
                </button>
              </div>
              <div style={{ fontSize: "0.9rem", color: "var(--cv-text, #20242d)", marginTop: "6px", lineHeight: 1.55 }}>
                {activeHint}
              </div>
            </div>
          )}

          {activeSimplerExample && (
            <div
              style={{
                background: "#f4f7f6",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderLeft: "4px solid var(--cv-success, #587867)",
                padding: "16px 20px",
                borderRadius: "4px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-success, #587867)" }}>
                  Simplified Toy Walkthrough
                </span>
                <button
                  type="button"
                  onClick={() => setActiveSimplerExample(null)}
                  style={{ background: "transparent", border: "none", color: "var(--cv-muted, #686b70)", cursor: "pointer", fontSize: "0.75rem" }}
                >
                  Dismiss ✕
                </button>
              </div>
              <div style={{ fontSize: "0.9rem", color: "var(--cv-text, #20242d)", marginTop: "6px", lineHeight: 1.55 }}>
                {activeSimplerExample}
              </div>
            </div>
          )}

          {activeCodeDemo && (
            <div
              style={{
                background: "var(--cv-text, #20242d)",
                color: "#fbf9f4",
                padding: "16px 20px",
                borderRadius: "4px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "#a5b4fc" }}>
                  💻 Reference Implementation Blueprint
                </span>
                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCodeInput(true);
                      setCandidateCode(activeCodeDemo);
                    }}
                    style={{
                      background: "transparent",
                      border: "1px solid #64748b",
                      color: "#f8fafc",
                      fontSize: "0.72rem",
                      padding: "3px 8px",
                      borderRadius: "3px",
                      cursor: "pointer",
                    }}
                  >
                    Copy to Workspace
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveCodeDemo(null)}
                    style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer", fontSize: "0.72rem" }}
                  >
                    Hide
                  </button>
                </div>
              </div>
              <pre
                style={{
                  margin: 0,
                  fontFamily: "var(--cv-font-mono, monospace)",
                  fontSize: "0.82rem",
                  lineHeight: 1.5,
                  overflowX: "auto",
                }}
              >
                {activeCodeDemo}
              </pre>
            </div>
          )}

          {/* ── DR. CYRA CONVERSATIONAL DIALOGUE STREAM (Multi-Turn Chat) ───── */}
          {chatMessages.length > 0 && (
            <section
              style={{
                background: "#ffffff",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderRadius: "4px",
                padding: "18px 22px",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.76rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-accent, #203d9b)" }}>
                  💬 Mentorship Dialogue with Dr. Cyra Vance
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--cv-muted, #686b70)" }}>
                  Persisted & Context-Aware
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px", maxHeight: "360px", overflowY: "auto" }}>
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                      maxWidth: "85%",
                      background: msg.role === "user" ? "var(--cv-accent-soft, #e0e5f5)" : "var(--cv-paper, #fbf9f4)",
                      padding: "10px 14px",
                      borderRadius: "6px",
                      border: "1px solid var(--cv-rule, #ded9cb)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                      <span style={{ fontSize: "0.72rem", fontWeight: 700, color: msg.role === "user" ? "var(--cv-accent, #203d9b)" : "#1e293b" }}>
                        {msg.role === "user" ? "You" : "Dr. Cyra Vance"}
                      </span>
                      <span style={{ fontSize: "0.68rem", color: "var(--cv-muted, #686b70)", marginLeft: "8px" }}>
                        {msg.timestamp}
                      </span>
                    </div>

                    <div style={{ fontSize: "0.88rem", lineHeight: 1.55, color: "#1e293b", whiteSpace: "pre-wrap" }}>
                      {msg.content}
                    </div>

                    {msg.citations?.length > 0 && (
                      <div style={{ marginTop: "6px", paddingTop: "4px", borderTop: "1px dashed var(--cv-rule, #ded9cb)", fontSize: "0.72rem", color: "var(--cv-muted, #686b70)" }}>
                        Citations: {msg.citations.map((c) => c.file_path || c.title).join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* ── LEARNER'S NATURAL RESPONSE WORKBENCH ───────────────────── */}
          <section
            aria-label="Learner response workspace"
            style={{
              background: "var(--cv-paper, #fbf9f4)",
              border: "1px solid var(--cv-rule, #ded9cb)",
              borderRadius: "4px",
              padding: "24px 28px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <div>
                <span
                  style={{
                    fontSize: "0.7rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--cv-muted, #686b70)",
                    fontWeight: 600,
                  }}
                >
                  Candidate Inquiry
                </span>
                <h2 style={{ margin: "3px 0 0 0", fontSize: "1.05rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                  Explain Your Approach & Reasoning
                </h2>
              </div>

              <button
                type="button"
                onClick={() => setShowCodeInput(!showCodeInput)}
                style={{
                  background: "transparent",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  padding: "5px 12px",
                  borderRadius: "4px",
                  fontSize: "0.76rem",
                  color: "var(--cv-muted, #686b70)",
                  cursor: "pointer",
                }}
              >
                {showCodeInput ? "Hide Code Workspace" : "+ Add Code Workspace"}
              </button>
            </div>

            {/* Quick Socratic Prompt Chips */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "12px" }}>
              <button
                type="button"
                onClick={(e) => handleSendChatMessage(e, "Explain this concept more simply using an intuitive analogy.")}
                style={{ background: "#ffffff", border: "1px solid var(--cv-rule, #ded9cb)", borderRadius: "3px", padding: "4px 8px", fontSize: "0.74rem", cursor: "pointer", color: "var(--cv-text, #20242d)" }}
              >
                💡 Explain more simply
              </button>
              <button
                type="button"
                onClick={(e) => handleSendChatMessage(e, "Show me another practical code example with comments.")}
                style={{ background: "#ffffff", border: "1px solid var(--cv-rule, #ded9cb)", borderRadius: "3px", padding: "4px 8px", fontSize: "0.74rem", cursor: "pointer", color: "var(--cv-text, #20242d)" }}
              >
                🔍 Show another example
              </button>
              <button
                type="button"
                onClick={(e) => handleSendChatMessage(e, "Explain each line of the optimal implementation code.")}
                style={{ background: "#ffffff", border: "1px solid var(--cv-rule, #ded9cb)", borderRadius: "3px", padding: "4px 8px", fontSize: "0.74rem", cursor: "pointer", color: "var(--cv-text, #20242d)" }}
              >
                💻 Walk through code line-by-line
              </button>
              <button
                type="button"
                onClick={(e) => handleSendChatMessage(e, "How does this pattern connect to my GitHub repository project?")}
                style={{ background: "#ffffff", border: "1px solid var(--cv-rule, #ded9cb)", borderRadius: "3px", padding: "4px 8px", fontSize: "0.74rem", cursor: "pointer", color: "var(--cv-text, #20242d)" }}
              >
                🔗 How is this used in my project?
              </button>
            </div>

            <form onSubmit={handleSubmitThoughts}>
              <textarea
                value={candidateThoughts}
                onChange={(e) => setCandidateThoughts(e.target.value)}
                placeholder="Explain your thought process here... (e.g., 'First, I consider the constraints. Then I identify that checking previous elements costs O(N²)...')"
                rows={5}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  borderRadius: "4px",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  padding: "14px 16px",
                  fontSize: "0.92rem",
                  lineHeight: 1.6,
                  color: "var(--cv-text, #20242d)",
                  background: "#ffffff",
                  outline: "none",
                  fontFamily: "inherit",
                  resize: "vertical",
                  marginBottom: showCodeInput ? "12px" : "16px",
                }}
              />

              {showCodeInput && (
                <div style={{ marginBottom: "16px" }}>
                  <div style={{ fontSize: "0.74rem", fontWeight: 600, color: "var(--cv-muted, #686b70)", marginBottom: "6px" }}>
                    Workspace Code (Optional):
                  </div>
                  <textarea
                    value={candidateCode || activeLesson?.starter_code || ""}
                    onChange={(e) => setCandidateCode(e.target.value)}
                    rows={7}
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      borderRadius: "4px",
                      background: "var(--cv-text, #20242d)",
                      color: "#fbf9f4",
                      border: "1px solid #111827",
                      padding: "12px 14px",
                      fontFamily: "var(--cv-font-mono, monospace)",
                      fontSize: "0.82rem",
                      lineHeight: 1.5,
                      outline: "none",
                      resize: "vertical",
                    }}
                  />
                </div>
              )}

              {errorMsg && (
                <div style={{ color: "var(--cv-danger, #a34d43)", fontSize: "0.82rem", fontWeight: 600, marginBottom: "12px" }}>
                  {errorMsg}
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.78rem", color: "var(--cv-muted, #686b70)" }}>
                  Submit for full pedagogical evaluation & masterclass
                </span>
                <button
                  type="submit"
                  disabled={isEvaluating}
                  style={{
                    background: "var(--cv-text, #20242d)",
                    color: "#fbf9f4",
                    border: "none",
                    borderRadius: "4px",
                    padding: "12px 24px",
                    fontSize: "0.88rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <Sparkles size={15} />
                  <span>{isEvaluating ? "Cyra is Analyzing & Teaching..." : "Submit My Thought & Learn from Cyra 🎓"}</span>
                </button>
              </div>
            </form>
          </section>

          {/* ── CONTEXTUAL EVALUATION & MASTERCLASS FEEDBACK ─────────────── */}
          {teachingResult && (
            <section
              aria-label="Pedagogical feedback"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "18px",
                borderTop: "1px solid var(--cv-rule, #ded9cb)",
                paddingTop: "24px",
              }}
            >
              {/* Dual Assessment Grid */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                {/* What You Got Right */}
                <div
                  style={{
                    background: "#f4f7f5",
                    border: "1px solid var(--cv-rule, #ded9cb)",
                    borderLeft: "4px solid var(--cv-success, #587867)",
                    borderRadius: "4px",
                    padding: "18px 20px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <CheckCircle2 size={16} color="var(--cv-success, #587867)" />
                    <span style={{ fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, color: "var(--cv-success, #587867)" }}>
                      What You Got Right
                    </span>
                  </div>
                  <div style={{ fontSize: "0.9rem", lineHeight: 1.6, color: "var(--cv-text, #20242d)", whiteSpace: "pre-line" }}>
                    {teachingResult.what_is_right}
                  </div>
                </div>

                {/* What Was Sub-Optimal */}
                <div
                  style={{
                    background: "#faf6f5",
                    border: "1px solid var(--cv-rule, #ded9cb)",
                    borderLeft: "4px solid var(--cv-danger, #a34d43)",
                    borderRadius: "4px",
                    padding: "18px 20px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                    <AlertCircle size={16} color="var(--cv-danger, #a34d43)" />
                    <span style={{ fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, color: "var(--cv-danger, #a34d43)" }}>
                      What Was Wrong or Sub-Optimal
                    </span>
                  </div>
                  <div style={{ fontSize: "0.9rem", lineHeight: 1.6, color: "var(--cv-text, #20242d)", whiteSpace: "pre-line" }}>
                    {teachingResult.what_is_wrong || "No major omissions noted."}
                  </div>
                </div>
              </div>

              {/* Masterclass Lesson */}
              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid var(--cv-rule, #ded9cb)",
                  borderRadius: "4px",
                  padding: "24px 28px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                  <Award size={18} color="var(--cv-accent, #203d9b)" />
                  <h3 style={{ margin: 0, fontSize: "1.1rem", fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)", color: "var(--cv-text, #20242d)" }}>
                    Dr. Cyra Vance's Masterclass Breakdown
                  </h3>
                </div>

                <div style={{ fontSize: "0.95rem", lineHeight: 1.7, color: "var(--cv-text, #20242d)", whiteSpace: "pre-line" }}>
                  {teachingResult.masterclass_lesson}
                </div>

                {/* Optimal Solution Code */}
                {teachingResult.optimal_solution && (
                  <div style={{ marginTop: "18px" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--cv-muted, #686b70)", marginBottom: "6px" }}>
                      Optimal Architectural Solution:
                    </div>
                    <pre
                      style={{
                        margin: 0,
                        background: "var(--cv-text, #20242d)",
                        color: "#fbf9f4",
                        padding: "16px 18px",
                        borderRadius: "4px",
                        fontFamily: "var(--cv-font-mono, monospace)",
                        fontSize: "0.82rem",
                        lineHeight: 1.5,
                        overflowX: "auto",
                      }}
                    >
                      {teachingResult.optimal_solution}
                    </pre>
                  </div>
                )}
              </div>

              {/* Key Takeaway Banner */}
              <div
                style={{
                  background: "var(--cv-accent-soft, #e0e5f5)",
                  border: "1px solid var(--cv-accent, #203d9b)",
                  borderRadius: "4px",
                  padding: "16px 20px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <Star size={18} color="var(--cv-accent, #203d9b)" style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, color: "var(--cv-accent, #203d9b)" }}>
                    Permanent Engineering Principle
                  </div>
                  <div style={{ fontSize: "0.92rem", fontWeight: 600, color: "var(--cv-text, #20242d)", marginTop: "2px" }}>
                    {teachingResult.key_takeaway}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Mode B: Interview Preparation & Walkthrough Module */}
          {learningMode === "project" && projectJourney?.interview_prep && (
            <section
              style={{
                background: "#ffffff",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderRadius: "4px",
                padding: "24px 28px",
                marginTop: "16px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
                <Terminal size={18} color="var(--cv-accent, #203d9b)" />
                <h3 style={{ margin: 0, fontSize: "1.15rem", fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)", color: "var(--cv-text, #20242d)" }}>
                  Project Interview Walkthrough & Defense: {projectJourney.repository_name}
                </h3>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "14px", fontSize: "0.88rem", lineHeight: 1.6 }}>
                <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
                  <strong style={{ color: "var(--cv-accent, #203d9b)" }}>A. 60-Second Executive Pitch:</strong>
                  <p style={{ margin: "4px 0 0 0" }}>{projectJourney.interview_prep.short_introduction}</p>
                </div>

                <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
                  <strong style={{ color: "var(--cv-accent, #203d9b)" }}>B. Architecture Walkthrough:</strong>
                  <p style={{ margin: "4px 0 0 0" }}>{projectJourney.interview_prep.architecture_walkthrough}</p>
                </div>

                <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
                  <strong style={{ color: "var(--cv-accent, #203d9b)" }}>C. Sample Interview Answers (Grounding):</strong>
                  {projectJourney.interview_prep.sample_interview_answers?.map((sa, idx) => (
                    <div key={idx} style={{ marginTop: "8px", borderTop: idx > 0 ? "1px dashed var(--cv-rule, #ded9cb)" : "none", paddingTop: idx > 0 ? "8px" : 0 }}>
                      <div style={{ fontWeight: 700, color: "#1e293b" }}>Q: {sa.question}</div>
                      <div style={{ marginTop: "2px", color: "#475569", fontStyle: "italic" }}>Model Answer: "{sa.recommended_answer}"</div>
                    </div>
                  ))}
                </div>

                <div style={{ background: "#fbf9f4", padding: "14px", borderRadius: "4px", border: "1px solid var(--cv-rule, #ded9cb)" }}>
                  <strong style={{ color: "var(--cv-accent, #203d9b)" }}>D. Practice Interview Questions:</strong>
                  <ul style={{ margin: "6px 0 0 16px", padding: 0 }}>
                    {projectJourney.interview_prep.practice_interview_questions?.map((pq, idx) => (
                      <li key={idx} style={{ marginBottom: "4px" }}>
                        {pq}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          )}

          {/* ── INTERACTIVE KNOWLEDGE & CONCEPT GRAPH PANEL ────────────── */}
          {showConceptMap && (
            <section
              style={{
                margin: "24px 0",
                background: "var(--cv-paper, #fbf9f4)",
                border: "1px solid var(--cv-rule, #ded9cb)",
                borderRadius: "6px",
                padding: "24px 28px",
              }}
            >
              <h2 style={{ margin: "0 0 16px 0", fontSize: "1.2rem", fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)", color: "var(--cv-text, #20242d)" }}>
                Interactive Knowledge &amp; Concept Graph
              </h2>
              {loadingConceptMap ? (
                <p style={{ color: "var(--cv-muted, #686b70)", fontSize: "0.9rem" }}>Loading concept graph…</p>
              ) : conceptMap?.nodes?.length > 0 ? (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                  {conceptMap.nodes.map((node) => (
                    <button
                      key={node.id}
                      type="button"
                      onClick={() => setSelectedConceptNode(node)}
                      style={{
                        padding: "8px 14px",
                        borderRadius: "20px",
                        border: node.is_current ? "2px solid var(--cv-accent, #203d9b)" : "1px solid var(--cv-rule, #ded9cb)",
                        background: node.is_current ? "var(--cv-accent, #203d9b)" : "var(--cv-paper, #fbf9f4)",
                        color: node.is_current ? "#ffffff" : "var(--cv-text, #20242d)",
                        fontSize: "0.85rem",
                        fontWeight: node.is_current ? 700 : 400,
                        cursor: "pointer",
                      }}
                    >
                      {node.label}
                    </button>
                  ))}
                </div>
              ) : (
                <p style={{ color: "var(--cv-muted, #686b70)", fontSize: "0.9rem" }}>
                  No concept map data available for this lesson.
                </p>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

import React, { useState, useEffect, useMemo } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
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
  GraduationCap,
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
  getProfileSnapshot,
  getLeetCodeProfile,
  getGithubRepositories,
  getResumes,
} from "../services/careerService";
import { useAuth } from "../context/AuthContext";
import { speakTextInLanguage } from "../services/speechService";
import "./TeachingStudioPage.css";
import "./InterviewPage.css";

export const SUPPORTED_TEACHING_LANGUAGES = [
  { code: "en", bcp47: "en-US", label: "English", flag: "🇺🇸", native: "English" },
  { code: "ta", bcp47: "ta-IN", label: "Tamil", flag: "🇮🇳", native: "தமிழ் / Tanglish" },
  { code: "hi", bcp47: "hi-IN", label: "Hindi", flag: "🇮🇳", native: "हिन्दी / Hinglish" },
  { code: "te", bcp47: "te-IN", label: "Telugu", flag: "🇮🇳", native: "తెలుగు", limitedSupport: true, limitedSupportNote: "Voice: rare outside Android/ChromeOS" },
  { code: "kn", bcp47: "kn-IN", label: "Kannada", flag: "🇮🇳", native: "ಕನ್ನಡ", limitedSupport: true, limitedSupportNote: "Beta — limited voice support on most platforms" },
  { code: "ml", bcp47: "ml-IN", label: "Malayalam", flag: "🇮🇳", native: "മലയാളം", limitedSupport: true, limitedSupportNote: "Beta — limited voice support on most platforms" },
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

  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const hubParam = searchParams?.get("hub");
  const trackParam = searchParams?.get("track");
  const modeParam = searchParams?.get("mode");

  const isStudioWorkbench =
    modeParam === "studio" ||
    Boolean(trackParam) ||
    (location.pathname === "/" && hubParam !== "true");

  const [selectedTrackId, setSelectedTrackId] = useState(trackParam || "coding");
  const [trackSelected, setTrackSelected] = useState(hubParam === "true" ? false : true);
  const [profileSnapshot, setProfileSnapshot] = useState(null);

  // Teaching Hub Telemetry Data State
  const [loadingHubData, setLoadingHubData] = useState(true);
  const [hubLeetcode, setHubLeetcode] = useState(null);
  const [hubRepos, setHubRepos] = useState([]);
  const [hubResumes, setHubResumes] = useState([]);
  const [hubSnapshotData, setHubSnapshotData] = useState(null);
  const [hubProgressData, setHubProgressData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadHubTelemetry() {
      try {
        setLoadingHubData(true);
        const [lcRes, repoRes, snapRes, resumeRes, progRes] = await Promise.allSettled([
          typeof getLeetCodeProfile === "function" ? getLeetCodeProfile() : Promise.resolve(null),
          typeof getGithubRepositories === "function"
            ? getGithubRepositories({ limit: 1000, offset: 0 })
            : Promise.resolve([]),
          typeof getProfileSnapshot === "function" ? getProfileSnapshot() : Promise.resolve(null),
          typeof getResumes === "function" ? getResumes() : Promise.resolve([]),
          typeof getTeachingProgress === "function" ? getTeachingProgress() : Promise.resolve(null),
        ]);

        if (!isMounted) return;

        if (lcRes.status === "fulfilled" && lcRes.value) {
          setHubLeetcode(lcRes.value);
        }
        if (repoRes.status === "fulfilled" && repoRes.value) {
          const repoList = Array.isArray(repoRes.value)
            ? repoRes.value
            : repoRes.value?.repositories || [];
          setHubRepos(repoList);
        }
        if (snapRes.status === "fulfilled" && snapRes.value) {
          setHubSnapshotData(snapRes.value);
          setProfileSnapshot(snapRes.value);
        }
        if (resumeRes.status === "fulfilled" && resumeRes.value) {
          const rList = Array.isArray(resumeRes.value)
            ? resumeRes.value
            : resumeRes.value?.resumes || [];
          setHubResumes(rList);
        }
        if (progRes.status === "fulfilled" && progRes.value) {
          setHubProgressData(progRes.value);
        }
      } catch (err) {
        console.warn("Could not load hub telemetry:", err);
      } finally {
        if (isMounted) setLoadingHubData(false);
      }
    }

    loadHubTelemetry();
    return () => {
      isMounted = false;
    };
  }, []);

  // 1. Load initial curriculum & progress (only needed for studio workbench)
  useEffect(() => {
    if (!isStudioWorkbench) return;
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

  // Derive connected resources telemetry
  const conn = profileSnapshot?.connected_resources || {};
  const lcProfile = conn.leetcode;
  const ghProfile = conn.github;
  const hrProfile = conn.hackerrank;
  const skillsList = conn.skills || [];
  const lcSolved = lcProfile?.total_solved || 531;
  const hrSolved = hrProfile?.total_solved || 103;
  const ghRepos = ghProfile?.repositories || [
    { name: "agentic-ecomm" },
    { name: "CareerVerseAI" },
  ];
  const skillsCount = skillsList.length || 39;

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
        getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => { });
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
      getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => { });

      // Speak Cyra's affirmation & right/wrong feedback in selected language
      if ("speechSynthesis" in window) {
        const speechText = result.what_is_right ? result.what_is_right.slice(0, 160) : "Great approach.";
        setIsSpeaking(speakTextInLanguage(speechText, selectedLanguage, {
          onUnsupported: (match) => setErrorMsg(match.message),
          onStarted: (v) => setIsSpeaking(v),
        }));
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
        repository_id: selectedRepoId || null,
        file_path: activeLesson?.file_path || (activeLesson?.source_references && activeLesson.source_references[1]) || null,
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
        companion_files: res.companion_files || [],
        file_path: res.file_path || null,
        suggested_follow_ups: res.suggested_follow_ups || [],
        is_assessment: res.is_assessment,
        demonstrated_understanding: res.demonstrated_understanding,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setChatMessages([...newMessages, cyraTurn]);

      if (res.demonstrated_understanding) {
        getTeachingProgress().then((p) => setTeachingProgress(p)).catch(() => { });
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

    setIsSpeaking(speakTextInLanguage(textToSpeak.slice(0, 450), selectedLanguage, {
      onUnsupported: (match) => {
        setErrorMsg(match.message);
        setIsSpeaking(false);
      },
      onStarted: (v) => setIsSpeaking(v),
    }));
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

  // Derived user details for compact header
  const hubDisplayName =
    user?.full_name ||
    user?.username ||
    hubSnapshotData?.basic?.full_name ||
    hubSnapshotData?.unified?.full_name ||
    "Learner";

  const hubTargetRole =
    hubSnapshotData?.basic?.target_role ||
    hubSnapshotData?.unified?.target_role ||
    "Software Engineer";

  const hubInitials = (hubDisplayName || "L")
    .split(" ")
    .filter(Boolean)
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  // Card 1: LeetCode Learning telemetry
  const isLeetCodeConnected = Boolean(
    hubLeetcode &&
      (hubLeetcode.total_solved != null ||
        hubLeetcode.username ||
        hubLeetcode.ranking != null)
  );
  const lcSolvedCount = hubLeetcode?.total_solved ?? 0;
  const lcEasyCount = hubLeetcode?.easy_solved ?? 0;
  const lcMediumCount = hubLeetcode?.medium_solved ?? 0;
  const lcHardCount = hubLeetcode?.hard_solved ?? 0;
  const lcWeakTopics = Array.isArray(hubLeetcode?.weak_topics)
    ? hubLeetcode.weak_topics
    : [];
  const lcRecommendedTopic =
    hubLeetcode?.recommended_topic ||
    (lcWeakTopics.length > 0 ? lcWeakTopics[0] : "Dynamic Programming & Trees");

  // Card 2: GitHub Learning telemetry
  const isGithubConnected = Boolean(hubRepos && hubRepos.length > 0);
  const ghRepoCount = hubRepos.length;
  const ghLanguages = useMemo(() => {
    const langSet = new Set();
    hubRepos.forEach((r) => {
      if (r?.language) langSet.add(r.language);
      if (Array.isArray(r?.languages)) {
        r.languages.forEach((l) => langSet.add(l));
      }
    });
    return Array.from(langSet).slice(0, 4);
  }, [hubRepos]);
  const ghRecommendedRepo = hubRepos[0]?.name || hubRepos[0]?.full_name || null;
  const ghImprovementArea =
    hubRepos[0]?.improvement_area ||
    "Architecture modularity, error boundaries & test coverage";

  // Card 3: Resume Skill Learning telemetry
  const rawSkills =
    hubSnapshotData?.unified?.skills ||
    hubSnapshotData?.basic?.skills ||
    [];
  const resumeSkillsList = useMemo(() => {
    if (!Array.isArray(rawSkills)) return [];
    return rawSkills
      .map((s) => (typeof s === "string" ? s : s?.name))
      .filter(Boolean);
  }, [rawSkills]);
  const hasResume = Boolean(
    (hubResumes && hubResumes.length > 0) || resumeSkillsList.length > 0
  );
  const resumeSkillsCount = resumeSkillsList.length;
  const topResumeSkills = resumeSkillsList.slice(0, 4);
  const resumeWeakSkill =
    hubSnapshotData?.unified?.skill_gaps?.[0] ||
    hubSnapshotData?.unified?.weak_skills?.[0] ||
    "System Design & Distributed Patterns";
  const resumeRecommendedLesson = resumeSkillsList[0]
    ? `${resumeSkillsList[0]} Core Patterns & Production Invariants`
    : "Object-Oriented Design & Invariants";
  const resumeLessonsCompleted = hubProgressData?.completed_lessons?.length || 0;
  const resumeLessonsMastered = hubProgressData?.mastered_lessons?.length || 0;

  if (!isStudioWorkbench) {
    return (
      <div className="teaching-hub-landing-page">
        {/* Compact Header */}
        <header className="teaching-hub-header">
          <div className="teaching-hub-header-left">
            <Link to="/dashboard" className="teaching-hub-brand-logo-link" title="CareerVerse AI Home">
              <div className="teaching-hub-logo-mark">
                <Sparkles size={16} />
              </div>
              <div className="teaching-hub-brand-text">
                <span className="teaching-hub-brand-title">CareerVerse AI</span>
                <span className="teaching-hub-brand-badge">
                  <Bot size={11} /> AI Teaching &amp; Socratic Studio
                </span>
              </div>
            </Link>

            <div className="teaching-hub-header-divider" />

            <div className="teaching-hub-header-titles">
              <h1 className="teaching-hub-page-title">Teaching Hub</h1>
              <p className="teaching-hub-page-subtitle">Choose your personalized learning path.</p>
            </div>
          </div>

          <div className="teaching-hub-header-right">
            <div className="teaching-hub-user-pill" title={hubDisplayName}>
              <div className="teaching-hub-avatar-circle">{hubInitials}</div>
              <div className="teaching-hub-user-info">
                <span className="teaching-hub-user-name">{hubDisplayName}</span>
                <span className="teaching-hub-user-role">{hubTargetRole}</span>
              </div>
            </div>
          </div>
        </header>

        {/* Hub Main Body */}
        <main className="teaching-hub-content-container">
          <div className="teaching-hub-hero-section">
            <div className="teaching-hub-eyebrow">TEACHING HUB</div>
            <h2 className="teaching-hub-hero-title">Your skills. Your projects. Your learning path.</h2>
            <p className="teaching-hub-hero-sub">
              Personalized, Socratic learning grounded in your real-world problem solving history, GitHub repositories, and verified resume profile.
            </p>
          </div>

          {loadingHubData ? (
            <div className="teaching-hub-cards-grid" aria-busy="true">
              {[1, 2, 3].map((idx) => (
                <div key={idx} className="teaching-hub-card teaching-hub-card-skeleton">
                  <div className="skeleton-icon-shimmer" />
                  <div className="skeleton-line-shimmer title" />
                  <div className="skeleton-line-shimmer desc" />
                  <div className="skeleton-line-shimmer desc short" />
                  <div className="skeleton-box-shimmer stats" />
                  <div className="skeleton-btn-shimmer" />
                </div>
              ))}
            </div>
          ) : (
            <div className="teaching-hub-cards-grid" role="region" aria-label="Learning Paths">
              {/* CARD 1: LeetCode Learning */}
              <div
                className="teaching-hub-card"
                data-testid="hub-card-leetcode"
                onClick={() => navigate("/ai/teaching/coding-profile")}
              >
                <div className="teaching-hub-card-top">
                  <div className="teaching-hub-icon-wrapper leetcode">
                    <Code2 size={24} />
                  </div>
                  <span className={`teaching-hub-connection-badge ${isLeetCodeConnected ? "connected" : "not-connected"}`}>
                    <span className="badge-dot" />
                    {isLeetCodeConnected ? "Connected" : "Not Connected"}
                  </span>
                </div>

                <div className="teaching-hub-card-body">
                  <h3 className="teaching-hub-card-title">LeetCode Learning</h3>
                  <p className="teaching-hub-card-desc">
                    Master data structures, algorithms, problem-solving patterns, and coding interview techniques using your actual problem-solving history.
                  </p>

                  <div className="teaching-hub-card-metrics">
                    {isLeetCodeConnected ? (
                      <>
                        <div className="hub-metric-row primary">
                          <span className="hub-metric-value">{lcSolvedCount}</span>
                          <span className="hub-metric-label">Problems Solved</span>
                        </div>

                        <div className="hub-diff-pills-row">
                          <span className="hub-diff-pill easy">
                            <span className="diff-dot easy" /> Easy {lcEasyCount}
                          </span>
                          <span className="hub-diff-pill medium">
                            <span className="diff-dot medium" /> Med {lcMediumCount}
                          </span>
                          <span className="hub-diff-pill hard">
                            <span className="diff-dot hard" /> Hard {lcHardCount}
                          </span>
                        </div>

                        {lcWeakTopics.length > 0 && (
                          <div className="hub-metric-field">
                            <span className="hub-field-label">Identified Weak Topics:</span>
                            <div className="hub-pill-tags">
                              {lcWeakTopics.slice(0, 3).map((topic) => (
                                <span key={topic} className="hub-pill-tag">
                                  {topic}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="hub-metric-field">
                          <span className="hub-field-label">Recommended Next:</span>
                          <span className="hub-field-value accent">{lcRecommendedTopic}</span>
                        </div>
                      </>
                    ) : (
                      <div className="hub-empty-state">
                        <AlertCircle size={18} className="hub-empty-icon" />
                        <p className="hub-empty-text">
                          Connect your LeetCode account to analyze problem-solving history, identify weak algorithmic patterns, and generate targeted practice.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="teaching-hub-card-footer">
                  <button
                    type="button"
                    className={`teaching-hub-action-btn ${isLeetCodeConnected ? "primary" : "secondary"}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate("/ai/teaching/coding-profile");
                    }}
                  >
                    <span>{isLeetCodeConnected ? "Continue Learning" : "Connect LeetCode"}</span>
                    <ArrowRight size={15} />
                  </button>
                </div>
              </div>

              {/* CARD 2: GitHub Learning */}
              <div
                className="teaching-hub-card"
                data-testid="hub-card-github"
                onClick={() => navigate("/ai/teaching/repositories")}
              >
                <div className="teaching-hub-card-top">
                  <div className="teaching-hub-icon-wrapper github">
                    <FolderGit2 size={24} />
                  </div>
                  <span className={`teaching-hub-connection-badge ${isGithubConnected ? "connected" : "not-connected"}`}>
                    <span className="badge-dot" />
                    {isGithubConnected ? "Connected" : "Not Connected"}
                  </span>
                </div>

                <div className="teaching-hub-card-body">
                  <h3 className="teaching-hub-card-title">GitHub Learning</h3>
                  <p className="teaching-hub-card-desc">
                    Learn from your own repositories. Understand your code, explore architecture, improve code quality, and strengthen real-world engineering skills.
                  </p>

                  <div className="teaching-hub-card-metrics">
                    {isGithubConnected ? (
                      <>
                        <div className="hub-metric-row primary">
                          <span className="hub-metric-value">{ghRepoCount}</span>
                          <span className="hub-metric-label">Connected {ghRepoCount === 1 ? "Repository" : "Repositories"}</span>
                        </div>

                        {ghLanguages.length > 0 && (
                          <div className="hub-metric-field">
                            <span className="hub-field-label">Languages &amp; Tech Detected:</span>
                            <div className="hub-pill-tags">
                              {ghLanguages.map((lang) => (
                                <span key={lang} className="hub-pill-tag">
                                  {lang}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {ghRecommendedRepo && (
                          <div className="hub-metric-field">
                            <span className="hub-field-label">Recommended Repository:</span>
                            <span className="hub-field-value accent">{ghRecommendedRepo}</span>
                          </div>
                        )}

                        <div className="hub-metric-field">
                          <span className="hub-field-label">Areas for Improvement:</span>
                          <span className="hub-field-value muted">{ghImprovementArea}</span>
                        </div>
                      </>
                    ) : (
                      <div className="hub-empty-state">
                        <AlertCircle size={18} className="hub-empty-icon" />
                        <p className="hub-empty-text">
                          Connect your GitHub profile to index real codebases, explore architectural patterns, and receive Socratic codebase critique.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="teaching-hub-card-footer">
                  <button
                    type="button"
                    className={`teaching-hub-action-btn ${isGithubConnected ? "primary" : "secondary"}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate("/ai/teaching/repositories");
                    }}
                  >
                    <span>{isGithubConnected ? "Explore My Repositories" : "Connect GitHub"}</span>
                    <ArrowRight size={15} />
                  </button>
                </div>
              </div>

              {/* CARD 3: Resume Skill Learning */}
              <div
                className="teaching-hub-card"
                data-testid="hub-card-resume"
                onClick={() => navigate("/ai/teaching/resume-skills")}
              >
                <div className="teaching-hub-card-top">
                  <div className="teaching-hub-icon-wrapper resume">
                    <GraduationCap size={24} />
                  </div>
                  <span className={`teaching-hub-connection-badge ${hasResume ? "connected" : "not-connected"}`}>
                    <span className="badge-dot" />
                    {hasResume ? "Connected" : "Upload Required"}
                  </span>
                </div>

                <div className="teaching-hub-card-body">
                  <h3 className="teaching-hub-card-title">Resume Skill Learning</h3>
                  <p className="teaching-hub-card-desc">
                    Turn your resume into a personalized learning roadmap. Study the skills you already have, strengthen weak areas, and learn technologies relevant to your projects and career goals.
                  </p>

                  <div className="teaching-hub-card-metrics">
                    {hasResume ? (
                      <>
                        <div className="hub-metric-row primary">
                          <span className="hub-metric-value">{resumeSkillsCount}</span>
                          <span className="hub-metric-label">Verified Skills Extracted</span>
                        </div>

                        {topResumeSkills.length > 0 && (
                          <div className="hub-metric-field">
                            <span className="hub-field-label">Verified Resume Skills:</span>
                            <div className="hub-pill-tags">
                              {topResumeSkills.map((skill) => (
                                <span key={skill} className="hub-pill-tag">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="hub-metric-field">
                          <span className="hub-field-label">Skills Requiring Improvement:</span>
                          <span className="hub-field-value muted">{resumeWeakSkill}</span>
                        </div>

                        <div className="hub-metric-field">
                          <span className="hub-field-label">Recommended First Lesson:</span>
                          <span className="hub-field-value accent">{resumeRecommendedLesson}</span>
                        </div>

                        {(resumeLessonsCompleted > 0 || resumeLessonsMastered > 0) && (
                          <div className="hub-metric-field">
                            <span className="hub-field-label">Learning Progress:</span>
                            <span className="hub-field-value">
                              {resumeLessonsMastered > 0
                                ? `${resumeLessonsMastered} mastered, ${resumeLessonsCompleted} completed`
                                : `${resumeLessonsCompleted} lessons completed`}
                            </span>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="hub-empty-state">
                        <AlertCircle size={18} className="hub-empty-icon" />
                        <p className="hub-empty-text">
                          Upload your resume to extract verified skills, detect target role gaps, and generate customized multi-stage learning roadmaps.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="teaching-hub-card-footer">
                  <button
                    type="button"
                    className={`teaching-hub-action-btn ${hasResume ? "primary" : "secondary"}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(hasResume ? "/ai/teaching/resume-skills" : "/resumes");
                    }}
                  >
                    <span>{hasResume ? "Start Learning" : "Upload Resume"}</span>
                    <ArrowRight size={15} />
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="teaching-hub-footer-hint">
            <span>Select a path to continue learning.</span>
          </div>
        </main>
      </div>
    );
  }

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

        {/* Studio Controls — only shown inside workbench */}
        {trackSelected && (
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
          </div>
        )}
      </header>

      {/* ── ENTRY SCREEN: 3 TRACK CARDS (shown before any track is selected) ── */}
      {!trackSelected && (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "48px 28px",
            gap: "36px",
          }}
        >
          {/* Hero heading */}
          <div style={{ textAlign: "center", maxWidth: "560px" }}>
            <div style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--cv-accent, #203d9b)", marginBottom: "10px" }}>
              AI Teaching &amp; Socratic Studio · Dr. Cyra Vance
            </div>
            <h1
              style={{
                margin: "0 0 10px 0",
                fontSize: "2rem",
                fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)",
                color: "var(--cv-text, #20242d)",
                letterSpacing: "-0.02em",
                lineHeight: 1.2,
              }}
            >
              Choose Your Teaching Track
            </h1>
            <p style={{ margin: 0, fontSize: "0.92rem", color: "var(--cv-muted, #686b70)", lineHeight: 1.6 }}>
              Grounded in your LeetCode activity, GitHub repositories, and verified resume skills.
            </p>
          </div>

          {/* 3 Track Cards */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "20px",
              width: "100%",
              maxWidth: "980px",
            }}
          >
            {/* Card 1: LeetCode Algorithmic Problem Solving */}
            <div
              className={`interview-track-card ${selectedTrackId === "coding" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("coding")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon"><Code2 size={20} /></div>
                  <span className="interview-track-badge">LeetCode Connected</span>
                </div>
                <h3 className="interview-track-title">LeetCode Algorithmic Problem Solving</h3>
                <div className="interview-track-evidence">
                  <span>✓ From LeetCode:</span>
                  <span style={{ fontWeight: 600 }}>{lcSolved} Problems Solved</span>
                </div>
                <p className="interview-track-desc">
                  Practice algorithmic problems, binary trees, dynamic programming, sliding window, and Big-O invariants grounded in your LeetCode problem bank.
                </p>
              </div>
              <div className="interview-track-footer">
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setSelectedTrackId("coding"); setTrackSelected(true); }}
                  style={{
                    padding: "9px 20px",
                    borderRadius: "6px",
                    background: selectedTrackId === "coding" ? "var(--cv-accent, #203d9b)" : "var(--cv-paper, #fbf9f4)",
                    color: selectedTrackId === "coding" ? "#fff" : "var(--cv-text, #20242d)",
                    border: "1px solid " + (selectedTrackId === "coding" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    transition: "all 0.15s ease",
                  }}
                >
                  Start Track <ArrowRight size={14} />
                </button>
                <div className="interview-radio-dot">
                  {selectedTrackId === "coding" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>

            {/* Card 2: GitHub Architecture & Codebase Review */}
            <div
              className={`interview-track-card ${selectedTrackId === "github" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("github")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon"><GitBranch size={20} /></div>
                  <span className="interview-track-badge">GitHub Connected</span>
                </div>
                <h3 className="interview-track-title">GitHub Architecture &amp; Codebase Review</h3>
                <div className="interview-track-evidence">
                  <span>✓ From GitHub:</span>
                  <span style={{ fontWeight: 600 }}>{ghRepos.length} Repositories</span>
                </div>
                <p className="interview-track-desc">
                  Deep dive into your real codebases. Cyra evaluates code design, repository modularity, API contracts, and production trade-offs.
                </p>
              </div>
              <div className="interview-track-footer">
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setSelectedTrackId("github"); setTrackSelected(true); }}
                  style={{
                    padding: "9px 20px",
                    borderRadius: "6px",
                    background: selectedTrackId === "github" ? "var(--cv-accent, #203d9b)" : "var(--cv-paper, #fbf9f4)",
                    color: selectedTrackId === "github" ? "#fff" : "var(--cv-text, #20242d)",
                    border: "1px solid " + (selectedTrackId === "github" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    transition: "all 0.15s ease",
                  }}
                >
                  Start Track <ArrowRight size={14} />
                </button>
                <div className="interview-radio-dot">
                  {selectedTrackId === "github" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>

            {/* Card 3: Resume Experience & STAR Leadership */}
            <div
              className={`interview-track-card ${selectedTrackId === "resume" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("resume")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon"><MessageSquare size={20} /></div>
                  <span className="interview-track-badge">Resume Connected</span>
                </div>
                <h3 className="interview-track-title">Resume Experience &amp; STAR Leadership</h3>
                <div className="interview-track-evidence">
                  <span>✓ From Resume &amp; Skills:</span>
                  <span style={{ fontWeight: 600 }}>{skillsCount} Verified Skills</span>
                </div>
                <p className="interview-track-desc">
                  Master verified skills from your resume with multi-stage roadmaps and Dr. Cyra's 9-point deep-dive curriculum.
                </p>
              </div>
              <div className="interview-track-footer">
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setSelectedTrackId("resume"); setTrackSelected(true); }}
                  style={{
                    padding: "9px 20px",
                    borderRadius: "6px",
                    background: selectedTrackId === "resume" ? "var(--cv-accent, #203d9b)" : "var(--cv-paper, #fbf9f4)",
                    color: selectedTrackId === "resume" ? "#fff" : "var(--cv-text, #20242d)",
                    border: "1px solid " + (selectedTrackId === "resume" ? "var(--cv-accent, #203d9b)" : "var(--cv-rule, #ded9cb)"),
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    transition: "all 0.15s ease",
                  }}
                >
                  Start Track <ArrowRight size={14} />
                </button>
                <div className="interview-radio-dot">
                  {selectedTrackId === "resume" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── WORKBENCH (shown only after track is selected) ── */}
      {trackSelected && (
        <>
          {/* Back to track selection */}
          <div style={{ padding: "10px 28px", borderBottom: "1px solid var(--cv-rule, #ded9cb)", display: "flex", alignItems: "center", gap: "10px", background: "var(--cv-paper, #fbf9f4)" }}>
            <button
              type="button"
              onClick={() => setTrackSelected(false)}
              style={{
                display: "flex", alignItems: "center", gap: "6px",
                background: "transparent", border: "none",
                color: "var(--cv-muted, #686b70)", fontSize: "0.82rem",
                fontWeight: 500, cursor: "pointer", padding: "4px 0",
              }}
            >
              <ArrowLeft size={14} /> Change Track
            </button>
            <span style={{ color: "var(--cv-rule, #ded9cb)", fontSize: "0.9rem" }}>|</span>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--cv-text, #20242d)" }}>
              {selectedTrackId === "coding" && "🧠 LeetCode Algorithmic Problem Solving"}
              {selectedTrackId === "github" && "🐙 GitHub Architecture & Codebase Review"}
              {selectedTrackId === "resume" && "📄 Resume Experience & STAR Leadership"}
            </span>
          </div>

          {/* Direct studio launch prompts when GitHub or Resume track is selected */}
          {selectedTrackId === "github" && (
            <div
              style={{
                margin: "0 28px 24px",
                padding: "20px 24px",
                background: "var(--surface, #ffffff)",
                border: "1px solid var(--border, #e5e2d9)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <h4 style={{ margin: "0 0 4px 0", fontSize: "1rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                  Ready to analyze your GitHub codebases?
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--cv-muted, #686b70)" }}>
                  Explore your {ghRepos.length} authorized repositories, trace file call-stacks, and receive line-level Socratic mentoring from Dr. Cyra.
                </p>
              </div>
              <Link
                to="/ai/teaching/repositories"
                style={{
                  padding: "10px 20px",
                  borderRadius: "6px",
                  background: "var(--accent, #6366f1)",
                  color: "#ffffff",
                  textDecoration: "none",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                Launch Repository Studio →
              </Link>
            </div>
          )}

          {selectedTrackId === "resume" && (
            <div
              style={{
                margin: "0 28px 24px",
                padding: "20px 24px",
                background: "var(--surface, #ffffff)",
                border: "1px solid var(--border, #e5e2d9)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <h4 style={{ margin: "0 0 4px 0", fontSize: "1rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                  Ready to master your verified resume skills?
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--cv-muted, #686b70)" }}>
                  Explore {skillsCount} authoritative resume skills across 9 pedagogical masterclasses with Socratic triggers and verified citations.
                </p>
              </div>
              <Link
                to="/ai/teaching/resume-skills"
                style={{
                  padding: "10px 20px",
                  borderRadius: "6px",
                  background: "var(--accent, #6366f1)",
                  color: "#ffffff",
                  textDecoration: "none",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                Launch Resume Skill Studio →
              </Link>
            </div>
          )}

          {/* placeholder to replace original grounding bar start */}
          <div style={{ display: "none" }}>
            <div
              className="interview-grounding-header"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "12px",
              }}
            >
              <div
                className="interview-grounding-label"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  color: "var(--cv-text, #20242d)",
                }}
              >
                <Zap size={15} color="var(--accent, #6366f1)" />
                <span>Connected Resources Powering Your Learning Options:</span>
              </div>
              <Link
                to="/resume"
                style={{
                  fontSize: "0.78rem",
                  fontWeight: 700,
                  color: "var(--accent, #6366f1)",
                  textDecoration: "none",
                }}
              >
                Manage Sources →
              </Link>
            </div>

            <div
              className="interview-grounding-pills"
              style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}
            >
              {/* LeetCode Badge */}
              <div className="interview-evidence-pill connected">
                <span style={{ fontSize: "0.95rem" }}>⚡</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "var(--cv-muted, #686b70)", fontWeight: 700 }}>
                    LeetCode
                  </div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                    {lcSolved} Solved
                  </div>
                </div>
              </div>

              {/* GitHub Badge */}
              <div className="interview-evidence-pill connected">
                <span style={{ fontSize: "0.95rem" }}>🐙</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "var(--cv-muted, #686b70)", fontWeight: 700 }}>
                    GitHub
                  </div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                    {ghRepos.length} Repositories
                  </div>
                </div>
              </div>

              {/* HackerRank Badge */}
              <div className="interview-evidence-pill connected">
                <span style={{ fontSize: "0.95rem" }}>🏆</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "var(--cv-muted, #686b70)", fontWeight: 700 }}>
                    HackerRank
                  </div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                    {hrSolved} Solved
                  </div>
                </div>
              </div>

              {/* Resume & Experience Badge */}
              <div className="interview-evidence-pill connected">
                <span style={{ fontSize: "0.95rem" }}>📄</span>
                <div>
                  <div style={{ fontSize: "0.72rem", color: "var(--cv-muted, #686b70)", fontWeight: 700 }}>
                    Resume &amp; Experience
                  </div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                    {skillsCount} Verified Skills
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ── 3 TRACK SELECTION CARDS (Strictly Coding, GitHub, Resume Skills) ── */}
          <div className="interview-tracks-grid" style={{ margin: "0 28px 16px" }}>
            {/* Card 1: Coding (LeetCode Algorithmic Problem Solving) */}
            <div
              className={`interview-track-card ${selectedTrackId === "coding" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("coding")}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon">
                    <Code2 size={20} />
                  </div>
                  <span className="interview-track-badge">LeetCode Connected</span>
                </div>

                <h3 className="interview-track-title">LeetCode Algorithmic Problem Solving</h3>

                <div className="interview-track-evidence">
                  <span>✓ From LeetCode:</span>
                  <span style={{ fontWeight: 600 }}>531 Problems Solved (298 Easy • 215 Med • 18 Hard)</span>
                </div>

                <p className="interview-track-desc">
                  Practice algorithmic problems, binary trees, dynamic programming, sliding window, and Big-O invariants grounded in your LeetCode problem bank.
                </p>
              </div>

              <div className="interview-track-footer">
                <Link
                  to="/ai/teaching/coding-profile"
                  style={{
                    textDecoration: "none",
                    fontWeight: 600,
                    color: "var(--accent, #6366f1)",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                  title="Launch Fullscreen Coding Profile Studio"
                >
                  LeetCode Canonical Problem Bank ↗
                </Link>
                <div className="interview-radio-dot">
                  {selectedTrackId === "coding" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>

            {/* Card 2: GitHub Architecture & Codebase Review */}
            <div
              className={`interview-track-card ${selectedTrackId === "github" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("github")}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon">
                    <GitBranch size={20} />
                  </div>
                  <span className="interview-track-badge">GitHub Connected</span>
                </div>

                <h3 className="interview-track-title">GitHub Architecture & Codebase Review</h3>

                <div className="interview-track-evidence">
                  <span>✓ From GitHub:</span>
                  <span style={{ fontWeight: 600 }}>38 Repositories: agentic-ecomm</span>
                </div>

                <p className="interview-track-desc">
                  Deep dive into your real codebases like agentic-ecomm. Cyra evaluates code design, repository modularity, API contracts, and production trade-offs.
                </p>
              </div>

              <div className="interview-track-footer">
                <Link
                  to="/ai/teaching/repositories"
                  style={{
                    textDecoration: "none",
                    fontWeight: 600,
                    color: "var(--accent, #6366f1)",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                  title="Launch Fullscreen GitHub Repository Studio"
                >
                  GitHub: agentic-ecomm ↗
                </Link>
                <div className="interview-radio-dot">
                  {selectedTrackId === "github" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>

            {/* Card 3: Resume Experience & STAR Leadership */}
            <div
              className={`interview-track-card ${selectedTrackId === "resume" ? "selected" : ""}`}
              onClick={() => setSelectedTrackId("resume")}
            >
              <div>
                <div className="interview-track-card-head">
                  <div className="interview-track-icon">
                    <MessageSquare size={20} />
                  </div>
                  <span className="interview-track-badge">Resume Connected</span>
                </div>

                <h3 className="interview-track-title">Resume Experience & STAR Leadership</h3>

                <div className="interview-track-evidence">
                  <span>✓ From Resume &amp; Skills:</span>
                  <span style={{ fontWeight: 600 }}>39 Verified Skills</span>
                </div>

                <p className="interview-track-desc">
                  Master verified skills from your resume with multi-stage roadmaps and Dr. Cyra's 9-point deep-dive curriculum covering runtime mechanics, code examples, pitfalls, and verified citations.
                </p>
              </div>

              <div className="interview-track-footer">
                <Link
                  to="/ai/teaching/resume-skills"
                  style={{
                    textDecoration: "none",
                    fontWeight: 600,
                    color: "var(--accent, #6366f1)",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                  title="Launch Fullscreen Resume Skill Studio"
                >
                  Resume Experience &amp; STAR Method ↗
                </Link>
                <div className="interview-radio-dot">
                  {selectedTrackId === "resume" && <div className="interview-radio-dot-inner" />}
                </div>
              </div>
            </div>
          </div>

          {/* Direct studio launch prompts when GitHub or Resume track is selected */}
          {selectedTrackId === "github" && (
            <div
              style={{
                margin: "0 28px 24px",
                padding: "20px 24px",
                background: "var(--surface, #ffffff)",
                border: "1px solid var(--border, #e5e2d9)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <h4 style={{ margin: "0 0 4px 0", fontSize: "1rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                  Ready to analyze your GitHub codebases?
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--cv-muted, #686b70)" }}>
                  Explore your 38 authorized repositories, trace file call-stacks, and receive line-level Socratic mentoring from Dr. Cyra.
                </p>
              </div>
              <Link
                to="/ai/teaching/repositories"
                style={{
                  padding: "10px 20px",
                  borderRadius: "6px",
                  background: "var(--accent, #6366f1)",
                  color: "#ffffff",
                  textDecoration: "none",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                Launch Repository Studio →
              </Link>
            </div>
          )}

          {selectedTrackId === "resume" && (
            <div
              style={{
                margin: "0 28px 24px",
                padding: "20px 24px",
                background: "var(--surface, #ffffff)",
                border: "1px solid var(--border, #e5e2d9)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <div>
                <h4 style={{ margin: "0 0 4px 0", fontSize: "1rem", fontWeight: 700, color: "var(--cv-text, #20242d)" }}>
                  Ready to master your verified resume skills?
                </h4>
                <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--cv-muted, #686b70)" }}>
                  Explore 30 authoritative resume skills across 9 pedagogical masterclasses with Socratic triggers and verified citations.
                </p>
              </div>
              <Link
                to="/ai/teaching/resume-skills"
                style={{
                  padding: "10px 20px",
                  borderRadius: "6px",
                  background: "var(--accent, #6366f1)",
                  color: "#ffffff",
                  textDecoration: "none",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                Launch Resume Skill Studio →
              </Link>
            </div>
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
                padding: "28px 40px",
                display: "flex",
                flexDirection: "column",
                gap: "24px",
                width: "100%",
                boxSizing: "border-box",
                minWidth: 0,
                overflowY: "auto",
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
                    margin: "0 0 8px 0",
                    fontSize: "1.7rem",
                    fontFamily: "var(--cv-font-display, 'DM Serif Display', Georgia, serif)",
                    color: "var(--cv-text, #20242d)",
                    letterSpacing: "-0.015em",
                    lineHeight: 1.2,
                  }}
                >
                  {activeLesson?.title || "Interactive Technical Lesson"}
                </h1>

                <p style={{ margin: 0, fontSize: "0.97rem", lineHeight: 1.65, color: "#374151" }}>
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
                    aria-label="Reveal Hint"
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
                    aria-label="Simpler Example"
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
                    aria-label="Masterclass"
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
                    aria-label="Why This Pattern"
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
                    aria-label="Starter Code"
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
                    aria-label="Assess Mastery"
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

                        {(msg.citations?.length > 0 || msg.companion_files?.length > 0) && (
                          <div style={{ marginTop: "8px", paddingTop: "6px", borderTop: "1px dashed var(--cv-rule, #ded9cb)", display: "flex", flexWrap: "wrap", gap: "6px", alignItems: "center" }}>
                            <span style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--cv-muted, #686b70)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Verified Sources:</span>
                            {msg.citations?.map((c, cIdx) => (
                              <span key={cIdx} style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.72rem", background: "rgba(16, 185, 129, 0.08)", color: "#065f46", border: "1px solid rgba(16, 185, 129, 0.25)", borderRadius: "4px", padding: "2px 6px" }}>
                                <ShieldCheck size={11} /> {c.file_path || c.title}
                              </span>
                            ))}
                            {msg.companion_files?.map((cf, cfIdx) => (
                              <span key={cfIdx} style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "0.72rem", background: "rgba(99, 102, 241, 0.08)", color: "#3730a3", border: "1px solid rgba(99, 102, 241, 0.25)", borderRadius: "4px", padding: "2px 6px" }}>
                                <Code2 size={11} /> Companion: {cf.file_name || cf.file_path}
                              </span>
                            ))}
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
        </>
      )}
    </div>
  );
}

import api from "./api";

// Keep browser-side AI requests bounded if the API process stops responding
// before it can return its own provider timeout response.
export const AI_REQUEST_TIMEOUT_MS = 210000;
const aiRequestConfig = { timeout: AI_REQUEST_TIMEOUT_MS };

let profileSnapshotPromise = null;
let profileSnapshot = null;
let resumeMetadataPromise = null;
let resumeMetadata = null;

export const clearProfileSnapshot = () => {
  profileSnapshot = null;
  profileSnapshotPromise = null;
  resumeMetadata = null;
  resumeMetadataPromise = null;
};

export const getProfileSnapshot = async ({ force = false } = {}) => {
  if (force) clearProfileSnapshot();
  if (profileSnapshot) return profileSnapshot;
  if (!profileSnapshotPromise) {
    profileSnapshotPromise = Promise.all([getUnifiedProfile(), getProfile()])
      .then(([unified, basic]) => {
        profileSnapshot = { unified, basic };
        return profileSnapshot;
      })
      .finally(() => {
        profileSnapshotPromise = null;
      });
  }
  return profileSnapshotPromise;
};

export const getProfile = async () => (await api.get("/profile")).data;
export const updateProfile = async (payload) => {
  const result = (await api.put("/profile", payload)).data;
  clearProfileSnapshot();
  return result;
};
export const getResumes = async () => {
  if (resumeMetadata) return resumeMetadata;
  if (!resumeMetadataPromise) {
    resumeMetadataPromise = api.get("/resume").then((response) => {
      resumeMetadata = response.data;
      return resumeMetadata;
    }).finally(() => { resumeMetadataPromise = null; });
  }
  return resumeMetadataPromise;
};
export const getParsedResume = async (resumeId) =>
  (await api.get(`/parser/resume/${resumeId}`)).data;
export const parseResume = async (resumeId) => {
  const result = (await api.post(`/parser/resume/${resumeId}`)).data;
  clearProfileSnapshot();
  return result;
};
export const uploadResume = async (file) => {
  const body = new FormData();
  body.append("file", file);
  const result = (
    await api.post("/resume/upload", body, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  ).data;
  clearProfileSnapshot();
  return result;
};
export const deleteResume = async (resumeId) => {
  const result = (await api.delete(`/resume/${resumeId}`)).data;
  clearProfileSnapshot();
  return result;
};
export const getJobs = async () => (await api.get("/jobs/")).data;
export const getRecommendations = async (resumeId) =>
  (await api.get(`/recommendations/${resumeId}`)).data;
export const getSkillGap = async (resumeId, jobId) =>
  (await api.get(`/skill-gap/${resumeId}/${jobId}`)).data;
export const getRoadmap = async (resumeId, jobId) =>
  (await api.get(`/career-roadmap/${resumeId}/${jobId}`)).data;
export const getResumeImprovement = async (resumeId, jobId) =>
  (await api.get(`/resume-improvement/${resumeId}/${jobId}`)).data;
export const syncGithub = async (username, force = true) =>
  (await api.post(`/github/sync/${encodeURIComponent(username)}?force=${force}`)).data;
export const syncLeetCode = async (username, force = true) =>
  (await api.post(`/leetcode/sync/${encodeURIComponent(username)}?force=${force}`)).data;
export const syncHackerRank = async (username, force = true) =>
  (await api.post(`/hackerrank/sync/${encodeURIComponent(username)}?force=${force}`)).data;
export const getGithubRepositories = async (params = {}) =>
  (await api.get("/github/repositories", { params })).data;
export const getUnifiedProfile = async () =>
  (await api.get("/candidate-intelligence/unified-profile")).data;
export const getLeetCodeProfile = async () =>
  (await api.get("/leetcode/profile")).data;
export const getHackerRankProfile = async () =>
  (await api.get("/hackerrank/profile")).data;
export const getCertifications = async () =>
  (await api.get("/certifications")).data;
export const importGoogleDriveCert = async (drive_file_url, drive_file_name = "Certificate.pdf") =>
  (await api.post("/certifications/google-drive/import", { drive_file_url, drive_file_name, auto_save: true })).data;
export const uploadCertificate = async (file) => {
  const body = new FormData();
  body.append("file", file);
  return (await api.post("/certifications/upload", body, { headers: { "Content-Type": "multipart/form-data" } })).data;
};
export const getDsaRecommendations = async (targetRole = "Software Developer") =>
  (await api.get(`/leetcode/dsa-recommendations?target_role=${encodeURIComponent(targetRole)}`)).data;
export const getDsaCodeHint = async (payload) =>
  (await api.post("/leetcode/dsa-hint", payload)).data;
export const evaluateDsaCode = async (payload) =>
  (await api.post("/leetcode/dsa-evaluate", payload)).data;
export const generateRagDsaProblem = async (payload) =>
  (await api.post("/leetcode/dsa/generate-rag", payload)).data;
export const chatWithCyra = async (payload) =>
  (await api.post("/ai/career/interview/cyra-chat", payload)).data;

// Compatibility adapters for the editorial chapter pages. The pages can
// consume the current AI contracts without duplicating profile/role lookup.
export const discoverCareers = async () =>
  aiRecommend("Which career directions fit my current evidence?");

export const getSkillGapAnalysis = async (targetRole = null) => {
  let role = targetRole;
  if (!role && typeof window !== "undefined") {
    role = sessionStorage.getItem("careerverse_target_role");
  }
  return aiSkillGap(role || "Software Developer");
};

export const getLearningRoadmap = async (targetRole = null) => {
  let role = targetRole;
  if (!role && typeof window !== "undefined") {
    role = sessionStorage.getItem("careerverse_target_role");
  }
  const effectiveRole = role || "Software Developer";

  try {
    const resumes = await getResumes();
    const resume = Array.isArray(resumes) ? resumes[0] : null;
    if (resume?.id) {
      const res = await analyzeSkillGapWithRoadmap(resume.id, effectiveRole);
      const stages = Array.isArray(res?.roadmap) ? res.roadmap : (Array.isArray(res?.missions) ? res.missions : []);
      if (stages.length > 0) {
        return res;
      }
    }
  } catch (err) {
    console.warn("Resume-based roadmap lookup fell back to AI evaluation agent:", err);
  }

  // 3. Grounded Multi-Source Fallback: Generate structured roadmap from LangGraph skill gap agent
  try {
    const skillGap = await aiSkillGap(effectiveRole);
    const gaps = skillGap?.skill_gaps || [];
    const missing = gaps.filter(g => g.status === "missing" || g.gap_level === "high" || g.gap_level === "medium");
    const areas = skillGap?.improvement_areas || [];

    const stages = [];
    stages.push({
      stage: 1,
      title: `Core Foundations for ${effectiveRole}`,
      goal: areas[0] || `Master required foundational proficiencies for ${effectiveRole}`,
      skills: missing.slice(0, 3).map(m => m.skill),
      learning_objectives: [
        `Study core architectural principles and idioms of ${missing[0]?.skill || effectiveRole}`,
        `Review industry design patterns and operational fundamentals`,
      ],
      practical_task: `Build a small prototype demonstrating ${missing[0]?.skill || "core concepts"}`,
      estimated_effort: "2–3 weeks",
    });

    if (missing.length > 2 || areas.length > 1) {
      stages.push({
        stage: 2,
        title: `Advanced Integration & System Design`,
        goal: areas[1] || `Apply intermediate skills in realistic application workflows`,
        skills: missing.slice(3, 6).map(m => m.skill),
        learning_objectives: [
          `Implement asynchronous data flows, API integration, and persistence`,
          `Configure automated testing and contract validation`,
        ],
        practical_task: `Design and deploy an end-to-end module meeting ${effectiveRole} requirements`,
        estimated_effort: "3–4 weeks",
      });
    }

    stages.push({
      stage: stages.length + 1,
      title: `Production Readiness & Portfolio Delivery`,
      goal: areas[2] || `Consolidate deliverables into production-grade demonstrations`,
      skills: missing.slice(6, 9).map(m => m.skill),
      learning_objectives: [
        `Optimize latency, security headers, and observability`,
        `Package codebase with CI/CD automation and documentation`,
      ],
      practical_task: `Publish an open-source demonstration project highlighting verified competencies`,
      estimated_effort: "2–3 weeks",
    });

    return {
      target_role: effectiveRole,
      roadmap: stages,
      readiness_score: skillGap?.readiness_score,
      summary: skillGap?.summary,
      status: "completed",
    };
  } catch (fallbackErr) {
    console.error("Failed to generate fallback roadmap from AI skill gap:", fallbackErr);
    throw fallbackErr;
  }
};


// ─── Phase 8 — LangGraph AI endpoints ────────────────────────────────────────
// Candidate identity is resolved server-side from the JWT.
// No candidate_id is sent from the frontend.

/** POST /ai/career/recommend — grounded career role recommendations */
export const aiRecommend = async (query, language = null) => {
  const queryStr = typeof query === "object" ? query?.query : query;
  const langStr = typeof query === "object" ? query?.language : language;
  const body = { query: queryStr || "Which career directions fit my current profile evidence?" };
  if (langStr) body.language = langStr;
  return (await api.post("/ai/career/recommend", body, aiRequestConfig)).data;
};

/** POST /ai/career/skill-gap — role-specific skill-gap analysis */
export const aiSkillGap = async (targetRole, query = null, language = null) => {
  const roleStr = typeof targetRole === "object" ? (targetRole?.target_role || targetRole?.role) : targetRole;
  const queryStr = typeof targetRole === "object" ? targetRole?.query : query;
  const langStr = typeof targetRole === "object" ? targetRole?.language : language;
  const body = { target_role: roleStr || "Software Engineer" };
  if (queryStr) body.query = queryStr;
  if (langStr) body.language = langStr;
  return (await api.post("/ai/career/skill-gap", body, aiRequestConfig)).data;
};

/** POST /ai/skill-gap/analyze — grounded skill gaps plus personalized roadmap */
export const analyzeSkillGapWithRoadmap = async (
  resumeId,
  targetRole,
  jobId = null,
) => {
  let rId = resumeId;
  let role = targetRole;
  let jId = jobId;
  if (typeof resumeId === "object" && resumeId !== null) {
    rId = resumeId.resume_id || resumeId.id;
    role = resumeId.target_role || resumeId.role;
    jId = resumeId.job_id;
  }
  const body = { resume_id: Number(rId), target_role: role || "Software Engineer" };
  if (jId) body.job_id = Number(jId);
  return (await api.post("/ai/skill-gap/analyze", body, aiRequestConfig)).data;
};

/** POST /ai/career/interview — personalised interview preparation */
export const aiInterview = async (
  query = null,
  targetRole = null,
  language = null,
) => {
  const body = {};
  if (typeof query === "object" && query !== null) {
    if (query.query) body.query = query.query;
    if (query.target_role || query.role) body.target_role = query.target_role || query.role;
    if (query.language) body.language = query.language;
  } else {
    if (query) body.query = query;
    if (targetRole) body.target_role = targetRole;
    if (language) body.language = language;
  }
  return (await api.post("/ai/career/interview", body, aiRequestConfig)).data;
};

export const createInterviewSession = async (
  targetRole,
  interviewMode = "technical",
  language = "en",
  focusTopic = null,
  repositoryId = null,
  sessionMode = "fresh",
  totalCoreQuestions = 5,
) => {
  let role = targetRole;
  let mode = interviewMode;
  let lang = language;
  let focus = focusTopic;
  let repoId = repositoryId;
  let sessMode = sessionMode;
  let totalQuestions = totalCoreQuestions;
  if (typeof targetRole === "object" && targetRole !== null) {
    role = targetRole.target_role || targetRole.role;
    mode = targetRole.interview_mode || mode || "technical";
    lang = targetRole.language || lang || "en";
    focus = targetRole.focus_topic || targetRole.topic || focus;
    repoId = targetRole.repository_id || repoId;
    sessMode = targetRole.session_mode || sessMode || "fresh";
    totalQuestions = targetRole.total_core_questions || targetRole.totalQuestions || totalQuestions;
  }
  const payload = {
    target_role: role || null,
    interview_mode: mode || "technical",
    language: lang || "en",
    total_core_questions: Number(totalQuestions) || 5,
  };
  if (focus && typeof focus === "string" && focus.trim()) {
    payload.focus_topic = focus.trim();
  }
  if (repoId) {
    payload.repository_id = repoId;
  }
  if (sessMode) {
    payload.session_mode = sessMode;
  }
  return (
    await api.post("/ai/career/interview/session", payload, aiRequestConfig)
  ).data;
};

export const getInterviewSession = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.get(`/ai/career/interview/session/${sId}`)).data;
};

export const submitInterviewAnswer = async (sessionId, answer, code = null, language = null, focusTopic = null) => {
  let sId = sessionId;
  let ans = answer;
  let cd = code;
  let lang = language;
  let focus = focusTopic;
  if (typeof sessionId === "object" && sessionId !== null) {
    sId = sessionId.session_id || sessionId.id;
    ans = sessionId.answer;
    cd = sessionId.code;
    lang = sessionId.language;
    focus = sessionId.focus_topic || sessionId.topic || focus;
  }
  const payload = { answer: ans };
  if (cd && typeof cd === "string" && cd.trim()) payload.code = cd.trim();
  if (lang && typeof lang === "string" && lang.trim()) payload.language = lang.trim();
  if (focus && typeof focus === "string" && focus.trim()) payload.focus_topic = focus.trim();

  return (
    await api.post(`/ai/career/interview/session/${sId}/answer`, payload, aiRequestConfig)
  ).data;
};

export const completeInterviewSession = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.post(`/ai/career/interview/session/${sId}/complete`, undefined, aiRequestConfig)).data;
};

export const endInterviewSession = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.post(`/ai/career/interview/session/${sId}/end`, undefined, aiRequestConfig)).data;
};

export const recordProctoringEvent = async (sessionId, eventType, durationMs = null, metadata = {}) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  const payload = {
    event_type: eventType,
    duration_ms: durationMs,
    metadata: metadata || {},
  };
  return (await api.post(`/ai/career/interview/session/${sId}/proctoring/events`, payload, aiRequestConfig)).data;
};

export const getInterviewProctoringSummary = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.get(`/ai/career/interview/session/${sId}/proctoring/summary`, aiRequestConfig)).data;
};


export const updateInterviewSessionLanguage = async (sessionId, language) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.patch(`/ai/career/interview/session/${sId}/language`, { language }, aiRequestConfig)).data;
};

export const getInterviewQuestionHistory = async () => {
  return (await api.get("/ai/career/interview/questions/history", aiRequestConfig)).data;
};

export const getInterviewResourcesAndModes = async () => {
  return (await api.get("/ai/career/interview/resources-and-modes", aiRequestConfig)).data;
};

export const createCareerQuizSession = async (language = "en") => {
  const lang = typeof language === "object" ? (language?.language || "en") : language;
  return (await api.post("/ai/career/quiz/session", { language: lang || "en" }, aiRequestConfig)).data;
};

export const getCareerQuizSession = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.get(`/ai/career/quiz/session/${sId}`)).data;
};

export const submitCareerQuizAnswer = async (sessionId, answer) => {
  let sId = sessionId;
  let ans = answer;
  if (typeof sessionId === "object" && sessionId !== null) {
    sId = sessionId.session_id || sessionId.id;
    ans = sessionId.answer;
  }
  return (await api.post(`/ai/career/quiz/session/${sId}/answer`, { answer: ans }, aiRequestConfig)).data;
};

export const completeCareerQuiz = async (sessionId) => {
  const sId = typeof sessionId === "object" ? (sessionId?.session_id || sessionId?.id) : sessionId;
  return (await api.post(`/ai/career/quiz/session/${sId}/complete`, undefined, aiRequestConfig)).data;
};

/** POST /ai/career/intelligence — full multi-agent orchestration */
export const aiIntelligence = async (
  query,
  targetRole = null,
  language = null,
) => {
  let q = query;
  let role = targetRole;
  let lang = language;
  if (typeof query === "object" && query !== null) {
    q = query.query;
    role = query.target_role || query.role || role;
    lang = query.language || lang;
  }
  const body = { query: q || "Based on everything CareerVerse knows about me, what should I focus on next in my career?" };
  if (role) body.target_role = role;
  if (lang) body.language = lang;
  return (await api.post("/ai/career/intelligence", body, aiRequestConfig)).data;
};

/** GET /ai/career/teaching/curriculum */
export const getTeachingCurriculum = async () => {
  return (await api.get("/ai/career/teaching/curriculum", aiRequestConfig)).data;
};

/** POST /ai/career/teaching/evaluate-and-teach */
export const evaluateAndTeach = async (payload) => {
  return (await api.post("/ai/career/teaching/evaluate-and-teach", payload, aiRequestConfig)).data;
};

/** GET /ai/career/interview/sessions */
export const getInterviewSessionsList = async (limit = 50, offset = 0) => {
  return (await api.get(`/ai/career/interview/sessions?limit=${limit}&offset=${offset}`, aiRequestConfig)).data;
};

/** POST /ai/career/teaching/interact */
export const interactTeachingLesson = async (payload) => {
  return (await api.post("/ai/career/teaching/interact", payload, aiRequestConfig)).data;
};

/** GET /ai/career/teaching/progress */
export const getTeachingProgress = async () => {
  return (await api.get("/ai/career/teaching/progress", aiRequestConfig)).data;
};

/** GET /ai/career/teaching/concept-map */
export const getTeachingConceptMap = async (lessonId = null) => {
  const url = lessonId ? `/ai/career/teaching/concept-map?lesson_id=${encodeURIComponent(lessonId)}` : "/ai/career/teaching/concept-map";
  return (await api.get(url, aiRequestConfig)).data;
};

/** GET /ai/career/teaching/skill-path */
export const getSkillLearningPath = async (skill) => {
  return (await api.get(`/ai/career/teaching/skill-path?skill=${encodeURIComponent(skill)}`, aiRequestConfig)).data;
};
export const getTeachingSkillPath = getSkillLearningPath;

/** GET /ai/career/teaching/lesson-detail */
export const getTeachingLessonDetail = async ({ skill, concept, lessonId, learnerLevel = "Intermediate", section, aiGenerated }) => {
  const params = new URLSearchParams();
  if (skill) params.append("skill", skill);
  if (concept) params.append("concept", concept);
  if (lessonId) params.append("lesson_id", lessonId);
  if (learnerLevel) params.append("learner_level", learnerLevel);
  if (section) params.append("section", section);
  if (aiGenerated !== undefined && aiGenerated !== null) params.append("ai_generated", String(aiGenerated));
  return (await api.get(`/ai/career/teaching/lesson-detail?${params.toString()}`, aiRequestConfig)).data;
};

/** GET /ai/career/teaching/project-path */
export const getProjectLearningPath = async (repositoryId, forceRefresh = false) => {
  return (await api.get(`/ai/career/teaching/project-path?repository_id=${encodeURIComponent(repositoryId)}&force_refresh=${Boolean(forceRefresh)}`, aiRequestConfig)).data;
};

/** GET /ai/career/teaching/repository-understanding */
export const getRepositoryUnderstanding = async (repositoryId, forceRefresh = false) => {
  return (await api.get(`/ai/career/teaching/repository-understanding?repository_id=${encodeURIComponent(repositoryId)}&force_refresh=${Boolean(forceRefresh)}`, aiRequestConfig)).data;
};

/** POST /ai/career/teaching/chat */
export const chatWithTeachingMentor = async (payload) => {
  return (await api.post("/ai/career/teaching/chat", payload, aiRequestConfig)).data;
};

/** GET /github/repositories/{id}/files */
export const getRepositoryFiles = async (repositoryId) => {
  return (await api.get(`/github/repositories/${repositoryId}/files`)).data;
};

/** GET /github/files/{id}/content */
export const getRepositoryFileContent = async (fileId) => {
  return (await api.get(`/github/files/${fileId}/content`)).data;
};

/** POST /ai/career/teaching/code-question */
export const getCodeQuestionForFile = async (payload) => {
  return (await api.post("/ai/career/teaching/code-question", payload, aiRequestConfig)).data;
};

/** POST /ai/career/teaching/file-explanation */
export const getFileExplanation = async (payload) => {
  return (await api.post("/ai/career/teaching/file-explanation", payload, aiRequestConfig)).data;
};

/** POST /course-documents/upload (PDF, MD, TXT - max 15MB) */
export const uploadCourseDocument = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return (
    await api.post("/course-documents/upload", formData, {
      ...aiRequestConfig,
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    })
  ).data;
};

/** GET /course-documents */
export const getCourseDocuments = async () => {
  return (await api.get("/course-documents", aiRequestConfig)).data;
};

/** GET /course-documents/:id */
export const getCourseDocumentDetail = async (documentId) => {
  return (await api.get(`/course-documents/${documentId}`, aiRequestConfig)).data;
};

/** DELETE /course-documents/:id */
export const deleteCourseDocument = async (documentId) => {
  return (await api.delete(`/course-documents/${documentId}`, aiRequestConfig)).data;
};

/** GET /course-documents/search */
export const searchCourseMaterials = async (query, topK = 4) => {
  return (
    await api.get(
      `/course-documents/search?q=${encodeURIComponent(query)}&top_k=${topK}`,
      aiRequestConfig
    )
  ).data;
};

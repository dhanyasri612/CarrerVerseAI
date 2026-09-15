import api from "./api";

export const getProfile = async () => (await api.get("/profile")).data;
export const updateProfile = async (payload) =>
  (await api.put("/profile", payload)).data;
export const getResumes = async () => (await api.get("/resume")).data;
export const getParsedResume = async (resumeId) =>
  (await api.get(`/parser/resume/${resumeId}`)).data;
export const parseResume = async (resumeId) =>
  (await api.post(`/parser/resume/${resumeId}`)).data;
export const uploadResume = async (file) => {
  const body = new FormData();
  body.append("file", file);
  return (
    await api.post("/resume/upload", body, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  ).data;
};
export const deleteResume = async (resumeId) =>
  (await api.delete(`/resume/${resumeId}`)).data;
export const getJobs = async () => (await api.get("/jobs/")).data;
export const getRecommendations = async (resumeId) =>
  (await api.get(`/recommendations/${resumeId}`)).data;
export const getSkillGap = async (resumeId, jobId) =>
  (await api.get(`/skill-gap/${resumeId}/${jobId}`)).data;
export const getRoadmap = async (resumeId, jobId) =>
  (await api.get(`/career-roadmap/${resumeId}/${jobId}`)).data;
export const getResumeImprovement = async (resumeId, jobId) =>
  (await api.get(`/resume-improvement/${resumeId}/${jobId}`)).data;
export const syncGithub = async (username) =>
  (await api.post(`/github/sync/${encodeURIComponent(username)}`)).data;

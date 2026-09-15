import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cv_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("cv_token");
      localStorage.removeItem("cv_user");
      window.dispatchEvent(new Event("cv:logout"));
    }

    return Promise.reject(error);
  },
);

export const getApiError = (error, fallback = "Something went wrong.") => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return (
      detail
        .map((item) => item?.msg || item?.message)
        .filter(Boolean)
        .join(" ") || fallback
    );
  }
  if (typeof detail === "string") return detail;
  if (error?.message === "Network Error") {
    return "Unable to reach CareerVerse AI. Check that the API is running.";
  }
  return fallback;
};

export default api;

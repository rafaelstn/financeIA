import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Ensure trailing slash to avoid FastAPI 307 redirects on POST
api.interceptors.request.use((config) => {
  if (config.url && !config.url.includes("?") && !config.url.endsWith("/")) {
    config.url += "/";
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.warn("Request timeout:", error.config?.url);
    } else if (!error.response) {
      console.warn("Network error:", error.config?.url);
    }
    return Promise.reject(error);
  }
);

export default api;

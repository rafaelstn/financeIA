import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
  timeout: 120000,
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

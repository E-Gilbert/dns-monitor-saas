import axios from "axios"

// Keep backend URL explicit for local frontend <-> backend communication.
// Can be overridden with Vite env var when needed.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export default api
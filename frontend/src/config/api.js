/**
 * API base URL: uses VITE_API_BASE_URL from env, or falls back by mode.
 * - Production (Vercel): https://mak-a3dk.onrender.com
 * - Local dev: http://localhost:8001 (override with .env.local for phone testing)
 */
export function getApiBaseUrl() {
  const env = import.meta.env?.VITE_API_BASE_URL
  if (env && typeof env === 'string' && env.trim()) return env.trim()
  return import.meta.env?.MODE === 'production'
    ? 'https://mak-a3dk.onrender.com'
    : 'http://localhost:8001'
}

export const API_BASE_URL = getApiBaseUrl()

import http from '@/http'

export const getAiHealth = () => http.get('/ai/health')

// The shared Axios instance keeps form encoding for legacy controller methods.
// DeepSeek chat accepts a nested message array, so this endpoint must explicitly
// use JSON instead of inheriting application/x-www-form-urlencoded.
export const sendAiChat = (messages) => http.post(
  '/ai/chat',
  { messages },
  { headers: { 'Content-Type': 'application/json' } }
)

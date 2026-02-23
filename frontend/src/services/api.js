import axios from 'axios'

// API base URL: always uses production backend
export const API_BASE_URL = 'https://mak-a3dk.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Refresh token on 401 and retry once (avoids circular import by using api instance)
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry && localStorage.getItem('refresh_token')) {
      original._retry = true
      try {
        const ref = localStorage.getItem('refresh_token')
        const { data } = await api.post('/auth/refresh', { refresh_token: ref })
        if (data?.access_token) {
          localStorage.setItem('access_token', data.access_token)
          if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        }
      } catch (_) {}
    }
    return Promise.reject(err)
  }
)

// ——— Chat WebSocket ———
function getWsUrl() {
  const base = API_BASE_URL.replace(/^https?:\/\//, '')
  const protocol = API_BASE_URL.startsWith('https') ? 'wss' : 'ws'
  return `${protocol}://${base}/chat/ws`
}
let ws = null
let reconnectTimer = null
let pingInterval = null
const RECONNECT_DELAY_MS = 3000
const PING_INTERVAL_MS = 25000
const listeners = new Set()
const readListeners = new Set()
const typingListeners = new Set()
const presenceListeners = new Set()

function connectWs() {
  const token = localStorage.getItem('access_token')
  if (!token) return
  const url = `${getWsUrl()}?token=${encodeURIComponent(token)}`
  try {
    ws = new WebSocket(url)
  } catch (e) {
    scheduleReconnect()
    return
  }
  ws.onopen = () => {
    startPing()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }
  ws.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data)
      if (data.type === 'pong') return
      if (data.type === 'new_message' && data.message) {
        listeners.forEach((cb) => { try { cb(data.message) } catch (_) {} })
      }
      if (data.type === 'messages_read' && data.message_ids) {
        readListeners.forEach((cb) => { try { cb({ message_ids: data.message_ids, read_at: data.read_at }) } catch (_) {} })
      }
      if (data.type === 'typing' && data.conversation_id) {
        typingListeners.forEach((cb) => { try { cb({ conversation_id: data.conversation_id, userid: data.userid, username: data.username || data.userid }) } catch (_) {} })
      }
      if (data.type === 'user_online' && data.userid) {
        presenceListeners.forEach((cb) => { try { cb({ type: 'online', userid: data.userid }) } catch (_) {} })
      }
      if (data.type === 'user_offline' && data.userid) {
        presenceListeners.forEach((cb) => { try { cb({ type: 'offline', userid: data.userid }) } catch (_) {} })
      }
      if (data.type === 'online_status' && Array.isArray(data.online_userids)) {
        data.online_userids.forEach((uid) => {
          presenceListeners.forEach((cb) => { try { cb({ type: 'online', userid: uid }) } catch (_) {} })
        })
      }
    } catch (_) {}
  }
  ws.onclose = () => {
    stopPing()
    ws = null
    scheduleReconnect()
  }
  ws.onerror = () => {}
}

function scheduleReconnect() {
  if (reconnectTimer) return
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    if (localStorage.getItem('access_token')) connectWs()
  }, RECONNECT_DELAY_MS)
}

function startPing() {
  stopPing()
  pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }))
  }, PING_INTERVAL_MS)
}

function stopPing() {
  if (pingInterval) {
    clearInterval(pingInterval)
    pingInterval = null
  }
}

export function onNewMessage(callback) {
  listeners.add(callback)
  return () => listeners.delete(callback)
}
export function onMessagesRead(callback) {
  readListeners.add(callback)
  return () => readListeners.delete(callback)
}
export function onTyping(callback) {
  typingListeners.add(callback)
  return () => typingListeners.delete(callback)
}
export function onPresence(callback) {
  presenceListeners.add(callback)
  return () => presenceListeners.delete(callback)
}
export function sendTyping(conversationId, username) {
  if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'typing', conversation_id: conversationId, username }))
}
export function connectChatWebSocket() {
  if (!localStorage.getItem('access_token')) return
  if (ws?.readyState === WebSocket.OPEN) return
  connectWs()
}
export function disconnectChatWebSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  stopPing()
  if (ws) {
    ws.close()
    ws = null
  }
  listeners.clear()
  readListeners.clear()
  typingListeners.clear()
  presenceListeners.clear()
}

// ——— Web Push ———
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; i++) outputArray[i] = rawData.charCodeAt(i)
  return outputArray
}

export async function setupPush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return
  try {
    const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' })
    let sub = await reg.pushManager.getSubscription()
    if (sub) return
    const { data } = await api.get('/push/vapid-public')
    const vapidKey = data?.vapid_public_key
    if (!vapidKey) return
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey),
    })
    const subscription = sub.toJSON()
    await api.post('/push/subscribe', {
      endpoint: subscription.endpoint,
      keys: subscription.keys,
    })
  } catch (_) {}
}

export function requestPushPermission() {
  if (!('Notification' in window)) return Promise.resolve(false)
  if (Notification.permission === 'granted') return Promise.resolve(true)
  if (Notification.permission === 'denied') return Promise.resolve(false)
  return Notification.requestPermission().then((p) => p === 'granted')
}

// ——— API endpoints ———
export const usersApi = {
  list(params) {
    return api.get('/admin/users/', { params }).then(res => res.data)
  },
  listByRole(role, params = {}) {
    return api.get(`/admin/users/role/${role}`, { params }).then(res => res.data)
  },
  getById(userid) {
    return api.get(`/admin/users/${userid}`).then(res => res.data)
  },
  createSingle(data) {
    return api.post('/admin/users/single', data).then(res => res.data)
  },
  createBulk(data) {
    return api.post('/admin/users/bulk', data).then(res => res.data)
  },
  update(userid, data) {
    return api.put(`/admin/users/${userid}`, data).then(res => res.data)
  },
  delete(userid, soft = true) {
    return api.delete(`/admin/users/${userid}`, { params: { soft } }).then(res => res.data)
  },
  bulkDelete(userids, soft = true) {
    return api.post('/admin/users/bulk-delete', { userids }, { params: { soft } }).then(res => res.data)
  },
}

export const studentsApi = {
  list(params) {
    return api.get('/admin/students/', { params }).then(res => res.data)
  },
  getById(userid) {
    return api.get(`/admin/students/${userid}`).then(res => res.data)
  },
  createSingle(data) {
    return api.post('/admin/students/single', data).then(res => res.data)
  },
  createBulk(data) {
    return api.post('/admin/students/bulk', data).then(res => res.data)
  },
  update(userid, data) {
    return api.put(`/admin/students/${userid}`, data).then(res => res.data)
  },
  delete(userid) {
    return api.delete(`/admin/students/${userid}`).then(res => res.data)
  },
  bulkDelete(userids) {
    return api.post('/admin/students/bulk-delete', { userids }).then(res => res.data)
  },
}

export const projectsApi = {
  list(params) {
    return api.get('/admin/projects/', { params }).then(res => res.data)
  },
  getById(projectid) {
    return api.get(`/admin/projects/${projectid}`).then(res => res.data)
  },
  create(data) {
    return api.post('/admin/projects/create', data).then(res => res.data)
  },
  update(projectid, data) {
    return api.put(`/admin/projects/${projectid}`, data).then(res => res.data)
  },
  delete(projectid) {
    return api.delete(`/admin/projects/${projectid}`).then(res => res.data)
  },
  assignManager(projectid, manager_userid) {
    return api.post(`/admin/projects/${projectid}/assign-manager`, { manager_userid }).then(res => res.data)
  },
  getManagers(projectid) {
    return api.get(`/admin/projects/${projectid}/managers`).then(res => res.data)
  },
}

export const managerApi = {
  myProjects() {
    return api.get('/manager/my-projects').then(res => res.data)
  },
  getProjectModules(projectid, params) {
    return api.get(`/manager/projects/${projectid}/modules`, { params }).then(res => res.data)
  },
  getModule(moduleid) {
    return api.get(`/manager/modules/${moduleid}`).then(res => res.data)
  },
  createModule(projectid, data) {
    return api.post(`/manager/projects/${projectid}/modules/create`, data).then(res => res.data)
  },
  updateModule(moduleid, data) {
    return api.put(`/manager/modules/${moduleid}`, data).then(res => res.data)
  },
  deleteModule(moduleid) {
    return api.delete(`/manager/modules/${moduleid}`).then(res => res.data)
  },
  assignMentor(moduleid, mentor_userid) {
    return api.post(`/manager/modules/${moduleid}/assign-mentor`, { mentor_userid }).then(res => res.data)
  },
  getModuleMentors(moduleid) {
    return api.get(`/manager/modules/${moduleid}/mentors`).then(res => res.data)
  },
}

export const mentorApi = {
  myModules() {
    return api.get('/mentor/my-modules').then(res => res.data)
  },
  getTeams() {
    return api.get('/mentor/teams').then(res => res.data)
  },
  createTeam(team_name) {
    return api.post('/mentor/teams/create', { team_name }).then(res => res.data)
  },
  addStudentToTeam(teamid, student_userid) {
    return api.post(`/mentor/teams/${teamid}/add-student`, { student_userid }).then(res => res.data)
  },
  getTeamMembers(teamid) {
    return api.get(`/mentor/teams/${teamid}/members`).then(res => res.data)
  },
  removeStudentFromTeam(teamid, student_userid) {
    return api.delete(`/mentor/teams/${teamid}/remove-student/${student_userid}`).then(res => res.data)
  },
  deleteTeam(teamid) {
    return api.delete(`/mentor/teams/${teamid}`).then(res => res.data)
  },
  getModuleTasks(moduleid, params) {
    return api.get(`/mentor/modules/${moduleid}/tasks`, { params }).then(res => res.data)
  },
  getTask(taskid) {
    return api.get(`/mentor/tasks/${taskid}`).then(res => res.data)
  },
  createTask(moduleid, data) {
    return api.post(`/mentor/modules/${moduleid}/tasks/create`, data).then(res => res.data)
  },
  updateTask(taskid, data) {
    return api.put(`/mentor/tasks/${taskid}`, data).then(res => res.data)
  },
  deleteTask(taskid) {
    return api.delete(`/mentor/tasks/${taskid}`).then(res => res.data)
  },
  assignStudent(taskid, student_userid) {
    return api.post(`/mentor/tasks/${taskid}/assign-student`, { student_userid }).then(res => res.data)
  },
  bulkAssign(taskid, student_userids) {
    return api.post(`/mentor/tasks/${taskid}/bulk-assign`, { student_userids }).then(res => res.data)
  },
  getTaskAssignments(taskid) {
    return api.get(`/mentor/tasks/${taskid}/assignments`).then(res => res.data)
  },
  reviewAssignment(assignmentId, data) {
    return api.post(`/mentor/tasks/assignments/${assignmentId}/review`, data).then(res => res.data)
  },
  getSubmissionUrl(assignmentId) {
    return api.get(`/mentor/tasks/assignments/${assignmentId}/submission`).then(res => res.data)
  },
  uploadReviewFile(assignmentId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/mentor/tasks/assignments/${assignmentId}/review-file`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then(res => res.data)
  },
}

export const studentApi = {
  myTasks(params) {
    return api.get('/student/my-tasks', { params }).then(res => res.data)
  },
  getTask(taskid) {
    return api.get(`/student/tasks/${taskid}`).then(res => res.data)
  },
  updateStatus(assignment_id, status) {
    return api.put(`/student/tasks/${assignment_id}/update-status`, { status }).then(res => res.data)
  },
  submit(assignment_id, notes, file = null) {
    const formData = new FormData()
    if (notes != null) formData.append('notes', notes)
    if (file) formData.append('file', file)
    return api.post(`/student/tasks/${assignment_id}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data)
  },
}

export const notificationsApi = {
  list(params = {}) {
    return api.get('/notifications', { params }).then(res => res.data)
  },
  unreadCount() {
    return api.get('/notifications/unread-count').then(res => res.data)
  },
  markRead(notificationId) {
    return api.put(`/notifications/${notificationId}/read`).then(res => res.data)
  },
  markAllRead() {
    return api.put('/notifications/read-all').then(res => res.data)
  },
  delete(notificationId) {
    return api.delete(`/notifications/${notificationId}`).then(res => res.data)
  },
}

export const dashboardApi = {
  getAdminStats() {
    return api.get('/dashboard/admin-stats').then(res => res.data)
  },
  getManagerStats() {
    return api.get('/dashboard/manager-stats').then(res => res.data)
  },
  getMentorStats() {
    return api.get('/dashboard/mentor-stats').then(res => res.data)
  },
  getStudentStats() {
    return api.get('/dashboard/student-stats').then(res => res.data)
  },
}

export const activityLogsApi = {
  list(params) {
    return api.get('/admin/activity-logs', { params }).then(res => res.data)
  },
}

export const exportApi = {
  students() {
    return api.get('/admin/export/students', { responseType: 'blob' })
  },
  projects() {
    return api.get('/admin/export/projects', { responseType: 'blob' })
  },
  mentorTasks() {
    return api.get('/mentor/export/tasks', { responseType: 'blob' })
  },
}

export const commentsApi = {
  list(assignmentId) {
    return api.get(`/mentor/tasks/assignments/${assignmentId}/comments`).then(res => res.data)
  },
  add(assignmentId, comment) {
    return api.post(`/mentor/tasks/assignments/${assignmentId}/comments`, { comment }).then(res => res.data)
  },
  delete(commentId) {
    return api.delete(`/mentor/tasks/comments/${commentId}`).then(res => res.data)
  },
}

export const studentCommentsApi = {
  list(assignmentId) {
    return api.get(`/student/tasks/assignments/${assignmentId}/comments`).then(res => res.data)
  },
  add(assignmentId, comment) {
    return api.post(`/student/tasks/assignments/${assignmentId}/comments`, { comment }).then(res => res.data)
  },
  delete(commentId) {
    return api.delete(`/student/tasks/comments/${commentId}`).then(res => res.data)
  },
}

// In-memory cache for chat to reduce API calls when switching back to chat tab
const CHAT_CACHE_TTL_MS = 60000 // 1 minute
const _chatCache = {
  conversations: null,
  onlineStatus: null,
  messages: {},
}

function _isCacheFresh(ts) {
  return ts && Date.now() - ts < CHAT_CACHE_TTL_MS
}

export const chatApi = {
  getConversations() {
    if (_chatCache.conversations && _isCacheFresh(_chatCache.conversations.ts)) {
      return Promise.resolve(_chatCache.conversations.data)
    }
    return api.get('/chat/conversations').then(res => {
      const data = res.data
      _chatCache.conversations = { data, ts: Date.now() }
      return data
    })
  },
  getOnlineStatus() {
    if (_chatCache.onlineStatus && _isCacheFresh(_chatCache.onlineStatus.ts)) {
      return Promise.resolve(_chatCache.onlineStatus.data)
    }
    return api.get('/chat/online-status').then(res => {
      const data = res.data
      _chatCache.onlineStatus = { data, ts: Date.now() }
      return data
    })
  },
  searchAvailableUsers(q = '') {
    return api.get('/chat/available-users', { params: { q, limit: 20 } }).then(res => res.data)
  },
  getOrCreateWith(otherUserid) {
    return api.get(`/chat/conversations/with/${otherUserid}`).then(res => res.data)
  },
  getMessages(conversationId) {
    const key = String(conversationId)
    const cached = _chatCache.messages[key]
    if (cached && _isCacheFresh(cached.ts)) {
      return Promise.resolve(cached.data)
    }
    return api.get(`/chat/conversations/${conversationId}/messages`).then(res => {
      const data = res.data
      _chatCache.messages[key] = { data, ts: Date.now() }
      return data
    })
  },
  sendMessage(conversationId, body) {
    return api.post(`/chat/conversations/${conversationId}/messages`, { body }).then(res => {
      delete _chatCache.messages[String(conversationId)]
      return res.data
    })
  },
  invalidateChatCache() {
    _chatCache.conversations = null
    _chatCache.onlineStatus = null
    _chatCache.messages = {}
  },
}

export const collegesApi = {
  list() {
    return api.get('/admin/colleges').then(res => res.data)
  },
  create(data) {
    return api.post('/admin/colleges', data).then(res => res.data)
  },
}

export const permissionsApi = {
  list() {
    return api.get('/admin/permissions').then(res => res.data)
  },
  listForRole(role) {
    return api.get(`/admin/permissions/role/${role}`).then(res => res.data)
  },
  set(data) {
    return api.post('/admin/permissions', data).then(res => res.data)
  },
}

export const reportsApi = {
  projectSummaryExcel() {
    return api.get('/admin/reports/project-summary.xlsx', { responseType: 'blob' })
  },
  projectSummaryPdf() {
    return api.get('/admin/reports/project-summary.pdf', { responseType: 'blob' })
  },
  studentProgressExcel() {
    return api.get('/admin/reports/student-progress.xlsx', { responseType: 'blob' })
  },
}

export const authService = {
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    const data = response.data
    if (data.access_token) localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  async register(data) {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  async resendOtp(email) {
    const response = await api.post('/auth/resend-otp', { email })
    return response.data
  },

  async verifyEmail(email, otp) {
    const response = await api.post('/auth/verify-email', { email, otp })
    return response.data
  },

  async getMe() {
    const response = await api.get('/auth/me')
    return response.data
  },

  async changePassword(currentPassword, newPassword) {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },

  async forgotPassword(email) {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  },

  async resetPassword(email, otp, newPassword) {
    const response = await api.post('/auth/reset-password', {
      email,
      otp,
      new_password: newPassword,
    })
    return response.data
  },

  async refreshToken() {
    const refresh = localStorage.getItem('refresh_token')
    if (!refresh) return null
    const response = await api.post('/auth/refresh', { refresh_token: refresh })
    const data = response.data
    if (data.access_token) localStorage.setItem('access_token', data.access_token)
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  logout() {
    disconnectChatWebSocket()
    chatApi.invalidateChatCache()
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

export default api

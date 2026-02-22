import axios from 'axios'
import { disconnectChatWebSocket } from './chatWebSocket'

const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8001'
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

export const chatApi = {
  getConversations() {
    return api.get('/chat/conversations').then(res => res.data)
  },
  getOnlineStatus() {
    return api.get('/chat/online-status').then(res => res.data)
  },
  searchAvailableUsers(q = '') {
    return api.get('/chat/available-users', { params: { q, limit: 20 } }).then(res => res.data)
  },
  getOrCreateWith(otherUserid) {
    return api.get(`/chat/conversations/with/${otherUserid}`).then(res => res.data)
  },
  getMessages(conversationId) {
    return api.get(`/chat/conversations/${conversationId}/messages`).then(res => res.data)
  },
  sendMessage(conversationId, body) {
    return api.post(`/chat/conversations/${conversationId}/messages`, { body }).then(res => res.data)
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
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

export default api

import axios from 'axios'

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

export const usersApi = {
  list(params) {
    return api.get('/admin/users/', { params }).then(res => res.data)
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
  submit(assignment_id, notes) {
    return api.post(`/student/tasks/${assignment_id}/submit`, { notes }).then(res => res.data)
  },
}

export const authService = {
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  async register(data) {
    const response = await api.post('/auth/register', data)
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
}

export default api

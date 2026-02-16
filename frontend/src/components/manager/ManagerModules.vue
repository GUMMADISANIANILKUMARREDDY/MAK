<script setup>
import { ref, onMounted } from 'vue'
import { managerApi, projectsApi } from '../../services/api'

const projects = ref([])
const selectedProject = ref(null)
const modules = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const subTab = ref('list')
const addForm = ref({ title: '', description: '', priority: 'medium', due_date: '' })
const editModal = ref(false)
const assignModal = ref(false)
const editModule = ref(null)
const assignModule = ref(null)
const editForm = ref({ title: '', description: '', priority: '', status: '', due_date: '' })
const assignForm = ref({ mentor_userid: '' })
const moduleFilters = ref({ search: '', status: '', sort: 'created_at', order: 'desc' })

const fetchProjects = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await managerApi.myProjects()
    projects.value = res.projects || []
    if (projects.value.length && !selectedProject.value) {
      selectedProject.value = projects.value[0]
      await loadModules(projects.value[0])
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load projects'
  } finally {
    loading.value = false
  }
}

const loadModules = async (project) => {
  selectedProject.value = project
  error.value = ''
  try {
    const params = {}
    if (moduleFilters.value.search) params.search = moduleFilters.value.search
    if (moduleFilters.value.status) params.status = moduleFilters.value.status
    params.sort = moduleFilters.value.sort
    params.order = moduleFilters.value.order
    const res = await managerApi.getProjectModules(project.projectid, params)
    modules.value = res.modules || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load modules'
  }
}

onMounted(() => fetchProjects())

const handleCreate = async () => {
  if (!selectedProject.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...addForm.value }
    if (!data.due_date) delete data.due_date
    await managerApi.createModule(selectedProject.value.projectid, data)
    successMsg.value = 'Module created'
    addForm.value = { title: '', description: '', priority: 'medium', due_date: '' }
    loadModules(selectedProject.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create module'
  } finally {
    loading.value = false
  }
}

const openEdit = (m) => {
  editModule.value = m
  editForm.value = {
    title: m.title,
    description: m.description || '',
    priority: m.priority || 'medium',
    status: m.status || '',
    due_date: m.due_date ? m.due_date.slice(0, 10) : '',
  }
  editModal.value = true
}

const handleUpdate = async () => {
  if (!editModule.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...editForm.value }
    if (!data.due_date) delete data.due_date
    if (!data.status) delete data.status
    await managerApi.updateModule(editModule.value.moduleid, data)
    successMsg.value = 'Module updated'
    editModal.value = false
    loadModules(selectedProject.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update module'
  } finally {
    loading.value = false
  }
}

const openAssign = (m) => {
  assignModule.value = m
  assignForm.value = { mentor_userid: '' }
  assignModal.value = true
}

const handleAssignMentor = async () => {
  if (!assignModule.value || !assignForm.value.mentor_userid) {
    error.value = 'Enter mentor user ID'
    return
  }
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await managerApi.assignMentor(assignModule.value.moduleid, assignForm.value.mentor_userid)
    successMsg.value = 'Mentor assigned'
    assignModal.value = false
    loadModules(selectedProject.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to assign mentor'
  } finally {
    loading.value = false
  }
}

const handleDelete = async (moduleid) => {
  if (!confirm('Delete this module?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await managerApi.deleteModule(moduleid)
    successMsg.value = 'Module deleted'
    loadModules(selectedProject.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete module'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="manager-modules">
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="loading && projects.length === 0" class="loading">Loading...</div>
    <div v-else-if="projects.length === 0" class="empty">No projects assigned. Create modules from a project.</div>
    <template v-else>
      <div class="project-select">
        <label>Project:</label>
        <select
          :value="selectedProject?.projectid"
          @change="
            (e) => {
              const p = projects.find((x) => x.projectid === e.target.value)
              if (p) loadModules(p)
            }
          "
        >
          <option v-for="p in projects" :key="p.projectid" :value="p.projectid">{{ p.title }}</option>
        </select>
      </div>
      <div class="tabs">
        <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">Modules</button>
        <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Create Module</button>
      </div>
      <div v-show="subTab === 'list'" class="content-block">
        <div class="filters">
          <input v-model="moduleFilters.search" placeholder="Search title or description" @keyup.enter="loadModules(selectedProject)" />
          <select v-model="moduleFilters.status" @change="loadModules(selectedProject)">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          <select v-model="moduleFilters.sort" @change="loadModules(selectedProject)">
            <option value="created_at">Created</option>
            <option value="due_date">Due Date</option>
            <option value="title">Title</option>
          </select>
          <select v-model="moduleFilters.order" @change="loadModules(selectedProject)">
            <option value="desc">Desc</option>
            <option value="asc">Asc</option>
          </select>
          <button class="btn btn-primary" @click="loadModules(selectedProject)">Search</button>
        </div>
        <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Priority</th>
              <th>Due Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in modules" :key="m.moduleid">
              <td>{{ m.title }}</td>
              <td>{{ m.priority || '-' }}</td>
              <td>{{ m.due_date ? m.due_date.slice(0, 10) : '-' }}</td>
              <td>{{ m.status || '-' }}</td>
              <td>
                <button class="btn-sm btn-edit" @click="openEdit(m)">Edit</button>
                <button class="btn-sm btn-assign" @click="openAssign(m)">Assign Mentor</button>
                <button class="btn-sm btn-delete" @click="handleDelete(m.moduleid)">Delete</button>
              </td>
            </tr>
            <tr v-if="modules.length === 0">
              <td colspan="5" class="empty">No modules. Create one.</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
      <div v-show="subTab === 'add'" class="content-block">
        <form @submit.prevent="handleCreate" class="form-add">
          <div class="form-group">
            <label>Title *</label>
            <input v-model="addForm.title" required placeholder="Module title" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="addForm.description" rows="3"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Priority</label>
              <select v-model="addForm.priority">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div class="form-group">
              <label>Due Date</label>
              <input v-model="addForm.due_date" type="date" />
            </div>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">Create Module</button>
        </form>
      </div>
      <div v-if="editModal" class="modal-overlay" @click="editModal = false">
        <div class="modal-content" @click.stop>
          <h3>Edit Module</h3>
          <form @submit.prevent="handleUpdate">
            <div class="form-group">
              <label>Title</label>
              <input v-model="editForm.title" required />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="2"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Priority</label>
                <select v-model="editForm.priority">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div class="form-group">
                <label>Due Date</label>
                <input v-model="editForm.due_date" type="date" />
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="editModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">Save</button>
            </div>
          </form>
        </div>
      </div>
      <div v-if="assignModal" class="modal-overlay" @click="assignModal = false">
        <div class="modal-content" @click.stop>
          <h3>Assign Mentor</h3>
          <p class="muted">{{ assignModule?.title }}</p>
          <form @submit.prevent="handleAssignMentor">
            <div class="form-group">
              <label>Mentor User ID *</label>
              <input v-model="assignForm.mentor_userid" required placeholder="e.g. MNT001" />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="assignModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">Assign</button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.manager-modules { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.alert-success { background: #f0fdf4; color: #16a34a; }
.project-select { margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.project-select select { padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; min-width: 200px; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tabs button { padding: 0.5rem 1rem; border: 2px solid #e2e8f0; background: white; border-radius: 8px; font-weight: 600; cursor: pointer; }
.tabs button.active { background: #0ea5e9; border-color: #0ea5e9; color: white; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; align-items: center; }
.filters input, .filters select { padding: 0.4rem 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.content-block { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
.data-table th { font-weight: 600; background: #f8fafc; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; margin-right: 0.5rem; }
.btn-edit { background: #e0f2fe; color: #0ea5e9; }
.btn-assign { background: #ecfdf5; color: #059669; }
.btn-delete { background: #fef2f2; color: #dc2626; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-secondary { background: #f1f5f9; color: #475569; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 12px; padding: 2rem; max-width: 480px; width: 100%; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.muted { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.loading, .empty { padding: 2rem; text-align: center; color: #64748b; }

.manager-modules .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.manager-modules .data-table { min-width: 520px; }
@media (max-width: 768px) {
  .manager-modules .project-select select { min-width: 100%; }
  .manager-modules .form-row { grid-template-columns: 1fr; }
  .manager-modules .data-table th, .manager-modules .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

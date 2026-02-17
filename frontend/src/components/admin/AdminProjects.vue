<script setup>
import { ref, onMounted } from 'vue'
import { projectsApi, exportApi } from '../../services/api'

const projects = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list')

const filters = ref({ status: '', search: '', date_from: '', date_to: '', sort: 'created_at', order: 'desc', page: 1, limit: 20 })

const addForm = ref({ title: '', description: '', start_date: '', end_date: '' })

const editModal = ref(false)
const assignModal = ref(false)
const editProject = ref(null)
const assignProject = ref(null)
const editForm = ref({ title: '', description: '', status: '', start_date: '', end_date: '' })
const assignForm = ref({ manager_userid: '' })

const fetchProjects = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = { page: filters.value.page, limit: filters.value.limit }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    params.sort = filters.value.sort
    params.order = filters.value.order
    const res = await projectsApi.list(params)
    projects.value = res.projects || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load projects'
  } finally {
    loading.value = false
  }
}

async function exportCsv() {
  try {
    const res = await exportApi.projects()
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'projects.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (_) {}
}

onMounted(() => fetchProjects())

const handleCreate = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...addForm.value }
    if (!data.start_date) delete data.start_date
    if (!data.end_date) delete data.end_date
    await projectsApi.create(data)
    successMsg.value = 'Project created'
    addForm.value = { title: '', description: '', start_date: '', end_date: '' }
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create project'
  } finally {
    loading.value = false
  }
}

const openEdit = (p) => {
  editProject.value = p
  editForm.value = {
    title: p.title,
    description: p.description || '',
    status: p.status || '',
    start_date: p.start_date ? p.start_date.slice(0, 10) : '',
    end_date: p.end_date ? p.end_date.slice(0, 10) : '',
  }
  editModal.value = true
}

const handleUpdate = async () => {
  if (!editProject.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...editForm.value }
    if (!data.start_date) delete data.start_date
    if (!data.end_date) delete data.end_date
    if (!data.status) delete data.status
    await projectsApi.update(editProject.value.projectid, data)
    successMsg.value = 'Project updated'
    editModal.value = false
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update project'
  } finally {
    loading.value = false
  }
}

const openAssign = (p) => {
  assignProject.value = p
  assignForm.value = { manager_userid: '' }
  assignModal.value = true
}

const handleAssignManager = async () => {
  if (!assignProject.value || !assignForm.value.manager_userid) {
    error.value = 'Enter manager user ID'
    return
  }
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await projectsApi.assignManager(assignProject.value.projectid, assignForm.value.manager_userid)
    successMsg.value = 'Manager assigned'
    assignModal.value = false
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to assign manager'
  } finally {
    loading.value = false
  }
}

const handleDelete = async (projectid) => {
  if (!confirm('Delete this project?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await projectsApi.delete(projectid)
    successMsg.value = 'Project deleted'
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete project'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-projects">
    <div class="tabs">
      <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">List Projects</button>
      <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Create Project</button>
    </div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <div v-show="subTab === 'list'" class="content-block">
      <div class="filters">
        <button type="button" class="btn btn-secondary" @click="exportCsv">Export CSV</button>
        <input v-model="filters.search" placeholder="Search title or description" @keyup.enter="fetchProjects" class="search-inp" />
        <select v-model="filters.status" @change="fetchProjects">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
        <input v-model="filters.date_from" type="date" placeholder="From" @change="fetchProjects" />
        <input v-model="filters.date_to" type="date" placeholder="To" @change="fetchProjects" />
        <select v-model="filters.sort" @change="fetchProjects">
          <option value="created_at">Created</option>
          <option value="start_date">Start Date</option>
          <option value="title">Title</option>
        </select>
        <select v-model="filters.order" @change="fetchProjects">
          <option value="desc">Desc</option>
          <option value="asc">Asc</option>
        </select>
        <button class="btn btn-primary" @click="fetchProjects">Search</button>
      </div>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Description</th>
            <th>Status</th>
            <th>Dates</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in projects" :key="p.projectid">
            <td>{{ p.title }}</td>
            <td>{{ (p.description || '').slice(0, 50) }}...</td>
            <td>{{ p.status || '-' }}</td>
            <td>{{ p.start_date || '-' }} / {{ p.end_date || '-' }}</td>
            <td>
              <button class="btn-sm btn-edit" @click="openEdit(p)">Edit</button>
              <button class="btn-sm btn-assign" @click="openAssign(p)">Assign</button>
              <button class="btn-sm btn-delete" @click="handleDelete(p.projectid)">Delete</button>
            </td>
          </tr>
          <tr v-if="projects.length === 0">
            <td colspan="5" class="empty">No projects found</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <div v-show="subTab === 'add'" class="content-block">
      <form @submit.prevent="handleCreate" class="form-add">
        <div class="form-group">
          <label>Title *</label>
          <input v-model="addForm.title" required placeholder="Project title" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="addForm.description" rows="3" placeholder="Project description"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Start Date</label>
            <input v-model="addForm.start_date" type="date" />
          </div>
          <div class="form-group">
            <label>End Date</label>
            <input v-model="addForm.end_date" type="date" />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Create Project</button>
      </form>
    </div>

    <div v-if="editModal" class="modal-overlay" @click="editModal = false">
      <div class="modal-content" @click.stop>
        <h3>Edit Project</h3>
        <form @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>Title</label>
            <input v-model="editForm.title" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editForm.description" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="editForm.status">
              <option value="">--</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Start Date</label>
              <input v-model="editForm.start_date" type="date" />
            </div>
            <div class="form-group">
              <label>End Date</label>
              <input v-model="editForm.end_date" type="date" />
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
        <h3>Assign Manager</h3>
        <p class="muted">{{ assignProject?.title }}</p>
        <form @submit.prevent="handleAssignManager">
          <div class="form-group">
            <label>Manager User ID *</label>
            <input v-model="assignForm.manager_userid" required placeholder="e.g. MGR001" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="assignModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">Assign</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-projects { width: 100%; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tabs button { padding: 0.5rem 1rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); background: var(--color-surface); border-radius: 8px; font-weight: 600; cursor: pointer; color: var(--color-muted); }
.tabs button.active { background: var(--color-primary); border-color: var(--color-primary); color: white; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: var(--color-danger-bg); color: var(--color-danger); }
.alert-success { background: var(--color-success-bg); color: var(--color-success); }
.content-block { background: var(--color-surface); padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent); }
.filters { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
.filters select { padding: 0.5rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); border-radius: 8px; background: var(--color-surface); color: var(--color-text); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid color-mix(in srgb, var(--color-border) 70%, transparent); }
.data-table th { font-weight: 600; background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface)); color: color-mix(in srgb, var(--color-heading) 85%, transparent); }
.data-table td.empty { text-align: center; color: var(--color-muted); padding: 2rem; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; margin-right: 0.5rem; }
.btn-edit { background: color-mix(in srgb, var(--color-primary) 12%, var(--color-surface)); color: var(--color-primary-strong); }
.btn-assign { background: color-mix(in srgb, var(--color-accent) 14%, var(--color-surface)); color: var(--color-accent-strong); }
.btn-delete { background: var(--color-danger-bg); color: var(--color-danger); }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.5rem 0.75rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); border-radius: 8px; background: var(--color-surface); color: var(--color-text); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-secondary { background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface)); color: var(--color-muted); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--color-surface); border-radius: 12px; padding: 2rem; max-width: 480px; width: 100%; border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent); }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.muted { color: var(--color-muted); font-size: 0.9rem; margin-bottom: 1rem; }

.admin-projects .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.admin-projects .data-table { min-width: 520px; }
@media (max-width: 768px) {
  .admin-projects .filters { flex-direction: column; }
  .admin-projects .form-row { grid-template-columns: 1fr; }
  .admin-projects .data-table th, .admin-projects .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

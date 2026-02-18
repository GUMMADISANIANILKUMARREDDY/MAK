<script setup>
import { ref, onMounted, watch } from 'vue'
import { projectsApi, exportApi, usersApi } from '@/services/api'

const projects = ref([])
const managers = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list')

const filters = ref({ status: '', search: '', sort: 'created_at', order: 'desc', page: 1, limit: 20 })
const addForm = ref({ title: '', description: '', start_date: '', end_date: '' })

const editModal = ref(false)
const assignModal = ref(false)
const showModal = ref(false)
const showProject = ref(null)
const editProject = ref(null)
const assignProject = ref(null)
const editForm = ref({ title: '', description: '', status: '', start_date: '', end_date: '', manager_userid: '' })
const assignForm = ref({ manager_userid: '' })

const fetchProjects = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = { page: filters.value.page, limit: filters.value.limit }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
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

const managersLoading = ref(false)
const managersError = ref('')
const fetchManagers = async () => {
  managersLoading.value = true
  managersError.value = ''
  try {
    const res = await usersApi.list({ role: 'manager', limit: 100 })
    managers.value = res.users || []
  } catch (err) {
    managers.value = []
    managersError.value = err.response?.data?.detail || 'Failed to load managers'
  } finally {
    managersLoading.value = false
  }
}

onMounted(() => {
  fetchProjects()
  fetchManagers()
})

watch(assignModal, (v) => { if (v) fetchManagers() })
watch(editModal, (v) => { if (v) fetchManagers() })

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
    subTab.value = 'list'
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create project'
  } finally {
    loading.value = false
  }
}

const openShow = async (p) => {
  showProject.value = p
  showModal.value = true
  try {
    const [projRes, mgrRes] = await Promise.all([
      projectsApi.getById(p.projectid),
      projectsApi.getManagers(p.projectid)
    ])
    showProject.value = { ...p, ...(projRes.project || projRes), managers: mgrRes.managers || [] }
  } catch {
    showProject.value = { ...p, managers: [] }
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
    manager_userid: '',
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
    const manager_userid = data.manager_userid
    delete data.manager_userid
    if (!data.start_date) delete data.start_date
    if (!data.end_date) delete data.end_date
    if (!data.status) delete data.status
    await projectsApi.update(editProject.value.projectid, data)
    if (manager_userid) {
      await projectsApi.assignManager(editProject.value.projectid, manager_userid)
    }
    successMsg.value = 'Project updated' + (manager_userid ? ' and manager assigned' : '')
    editModal.value = false
    fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update project'
  } finally {
    loading.value = false
  }
}

const openAssign = async (p) => {
  assignProject.value = p
  assignForm.value = { manager_userid: '' }
  await fetchManagers()
  assignModal.value = true
}

const handleAssignManager = async () => {
  if (!assignProject.value || !assignForm.value.manager_userid) {
    error.value = 'Select a manager'
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

const statusBadgeClass = (status) => {
  if (status === 'active') return 'badge-active'
  if (status === 'completed') return 'badge-completed'
  return 'badge-default'
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
  <div class="section-content">
    <div class="section-tabs d-flex gap-2 mb-4">
      <button type="button" :class="['section-tab', { active: subTab === 'list' }]" @click="subTab = 'list'">
        <i class="bi bi-folder2-open me-2"></i>List Projects
      </button>
      <button type="button" :class="['section-tab', { active: subTab === 'add' }]" @click="subTab = 'add'">
        <i class="bi bi-plus-circle me-2"></i>Create Project
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <div v-show="subTab === 'list'" class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="section-filters row g-2 align-items-center mb-3">
          <div class="col-auto">
            <button type="button" class="btn btn-outline-secondary" @click="exportCsv">
              <i class="bi bi-download me-1"></i>Export CSV
            </button>
          </div>
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
              <input v-model="filters.search" type="text" class="form-control" placeholder="Search title or description" @keyup.enter="fetchProjects" />
            </div>
          </div>
          <div class="col-auto">
            <select v-model="filters.status" class="form-select" @change="fetchProjects">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="fetchProjects">
              <i class="bi bi-search me-1"></i>Search
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
                <th>Date</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in projects" :key="p.projectid">
                <td>{{ p.title }}</td>
                <td class="text-truncate" style="max-width: 200px">{{ (p.description || '').slice(0, 50) }}{{ (p.description || '').length > 50 ? '...' : '' }}</td>
                <td><span class="badge" :class="statusBadgeClass(p.status)">{{ p.status || '-' }}</span></td>
                <td>{{ p.start_date ? p.start_date.slice(0, 10) : '-' }}</td>
                <td class="text-end">
                  <button type="button" class="btn btn-sm btn-action btn-view" @click="openShow(p)" title="View"><i class="bi bi-eye me-1"></i>View</button>
                  <button type="button" class="btn btn-sm btn-action btn-edit" @click="openEdit(p)" title="Edit"><i class="bi bi-pencil me-1"></i>Edit</button>
                  <button type="button" class="btn btn-sm btn-action btn-assign" @click="openAssign(p)" title="Assign Manager"><i class="bi bi-person-plus me-1"></i>Assign</button>
                  <button type="button" class="btn btn-sm btn-action btn-delete" @click="handleDelete(p.projectid)" title="Delete"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
              <tr v-if="projects.length === 0">
                <td colspan="5" class="text-center text-muted py-4">No projects found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-show="subTab === 'add'" class="card border-0 shadow-sm">
      <div class="card-body">
        <form @submit.prevent="handleCreate" class="row g-3">
          <div class="col-12">
            <label class="form-label">Title *</label>
            <input v-model="addForm.title" type="text" class="form-control" required placeholder="Project title" />
          </div>
          <div class="col-12">
            <label class="form-label">Description</label>
            <textarea v-model="addForm.description" class="form-control" rows="3" placeholder="Project description"></textarea>
          </div>
          <div class="col-md-6">
            <label class="form-label">Start Date</label>
            <input v-model="addForm.start_date" type="date" class="form-control" />
          </div>
          <div class="col-md-6">
            <label class="form-label">End Date</label>
            <input v-model="addForm.end_date" type="date" class="form-control" />
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-teal" :disabled="loading">Create Project</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)" @click.self="showModal = false">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Project Details</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body" v-if="showProject">
            <div class="project-detail-grid">
              <div class="detail-row">
                <span class="detail-label">Title</span>
                <span class="detail-value">{{ showProject.title }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Description</span>
                <span class="detail-value">{{ showProject.description || '-' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status</span>
                <span><span class="badge" :class="statusBadgeClass(showProject.status)">{{ showProject.status || '-' }}</span></span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Start Date</span>
                <span class="detail-value">{{ showProject.start_date ? showProject.start_date.slice(0, 10) : '-' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">End Date</span>
                <span class="detail-value">{{ showProject.end_date ? showProject.end_date.slice(0, 10) : '-' }}</span>
              </div>
              <div class="detail-row" v-if="showProject.managers && showProject.managers.length">
                <span class="detail-label">Assigned Managers</span>
                <span class="detail-value">
                  <span v-for="a in showProject.managers" :key="a.manager_userid" class="badge bg-secondary me-1">{{ a.username || a.manager_userid }} ({{ a.manager_userid }})</span>
                </span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showModal = false">Close</button>
            <button type="button" class="btn btn-teal" @click="showModal = false; openEdit(showProject)"><i class="bi bi-pencil me-1"></i>Edit</button>
          </div>
          
        </div>
      </div>
    </div>

    <div v-if="editModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Project</h5>
            <button type="button" class="btn-close" @click="editModal = false"></button>
          </div>
          <form @submit.prevent="handleUpdate">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Title</label>
                <input v-model="editForm.title" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="editForm.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Status</label>
                <select v-model="editForm.status" class="form-select">
                  <option value="">--</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label">Start Date</label>
                  <input v-model="editForm.start_date" type="date" class="form-control" />
                </div>
                <div class="col-6">
                  <label class="form-label">End Date</label>
                  <input v-model="editForm.end_date" type="date" class="form-control" />
                </div>
              </div>
              <div class="mb-3 mt-3">
                <label class="form-label">Assign Manager</label>
                <select v-model="editForm.manager_userid" class="form-select">
                  <option value="">-- None / Skip --</option>
                  <option v-for="m in managers" :key="m.userid" :value="m.userid">{{ m.username || m.userid }} ({{ m.userid }})</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="editModal = false">Cancel</button>
              <button type="submit" class="btn btn-teal" :disabled="loading">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="assignModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Assign Manager</h5>
            <button type="button" class="btn-close" @click="assignModal = false"></button>
          </div>
          <form @submit.prevent="handleAssignManager">
            <div class="modal-body">
              <p class="text-muted small mb-3">{{ assignProject?.title }}</p>
              <label class="form-label">Select Manager *</label>
              <select v-model="assignForm.manager_userid" class="form-select" required>
                <option value="">{{ managersLoading ? 'Loading managers...' : '-- Select Manager --' }}</option>
                <option v-for="m in managers" :key="m.userid" :value="m.userid">{{ m.username || m.userid }} ({{ m.userid }})</option>
              </select>
              <p v-if="managersError" class="text-danger small mt-2 mb-0">{{ managersError }}</p>
              <p v-else-if="!managersLoading && managers.length === 0" class="text-muted small mt-2 mb-0">No managers found. Add manager users first.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="assignModal = false">Cancel</button>
              <button type="submit" class="btn btn-assign-submit" :disabled="loading">Assign</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-tab {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  background: #fff;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}
.section-tab:hover { border-color: #20BFB6; color: #20BFB6; }
.section-tab.active {
  background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%);
  border-color: transparent;
  color: white;
}
.btn-teal { background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%); border: none; color: white; font-weight: 600; }
.btn-teal:hover { opacity: 0.95; color: white; }
.btn-action { padding: 0.35rem 0.65rem; font-size: 0.85rem; border-radius: 8px; margin-left: 0.25rem; }
.btn-edit { border: 1px solid #0d6efd; color: #0d6efd; background: rgba(13, 110, 253, 0.08); }
.btn-edit:hover { background: rgba(13, 110, 253, 0.15); color: #0d6efd; }
.btn-assign { border: 1px solid #f59e0b; color: #d97706; background: rgba(245, 158, 11, 0.15); }
.btn-assign:hover { background: rgba(245, 158, 11, 0.25); color: #b45309; border-color: #f59e0b; }
.btn-view { border: 1px solid #64748b; color: #475569; background: rgba(100, 116, 139, 0.08); }
.btn-view:hover { background: rgba(100, 116, 139, 0.15); color: #334155; }
.btn-delete { border: 1px solid #dc3545; color: #dc3545; background: rgba(220, 53, 69, 0.08); }
.btn-delete:hover { background: rgba(220, 53, 69, 0.15); color: #dc3545; }
.badge-active { background: #86efac; color: #166534; }
.badge-completed { background: #93c5fd; color: #1e40af; }
.badge-default { background: #cbd5e1; color: #475569; }
.btn-assign-submit { background: #fed7aa; color: #c2410c; border: 1px solid #fdba74; font-weight: 600; }
.btn-assign-submit:hover { background: #fdba74; color: #9a3412; border-color: #f59e0b; }
.project-detail-grid { display: flex; flex-direction: column; gap: 1rem; }
.detail-row { display: flex; flex-direction: column; gap: 0.25rem; }
.detail-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748b; }
.detail-value { font-size: 0.95rem; color: #0f172a; white-space: pre-wrap; word-break: break-word; }
</style>

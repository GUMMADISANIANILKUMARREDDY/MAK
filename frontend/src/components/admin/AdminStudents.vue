<script setup>
import { ref, onMounted } from 'vue'
import { studentsApi, exportApi } from '@/services/api'

const students = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list')

const filters = ref({ search: '', sort: 'userid', order: 'asc', page: 1, limit: 20 })
const addForm = ref({ userid: '', first_name: '', last_name: '', phone: '', email: '' })
const bulkForm = ref({ students: [{ userid: '', first_name: '', last_name: '', phone: '', email: '' }] })
const bulkDeleteIds = ref('')

const editModal = ref(false)
const editStudent = ref(null)
const editForm = ref({ first_name: '', last_name: '', phone: '', email: '' })

const fetchStudents = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    params.sort = filters.value.sort
    params.order = filters.value.order
    params.page = filters.value.page
    params.limit = filters.value.limit
    const res = await studentsApi.list(params)
    students.value = res.students || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load students'
  } finally {
    loading.value = false
  }
}

async function exportCsv() {
  try {
    const res = await exportApi.students()
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'students.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (_) {}
}

onMounted(() => fetchStudents())

const handleAddStudent = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.createSingle(addForm.value)
    successMsg.value = 'Student added successfully'
    addForm.value = { userid: '', first_name: '', last_name: '', phone: '', email: '' }
    subTab.value = 'list'
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add student'
  } finally {
    loading.value = false
  }
}

const addBulkRow = () => bulkForm.value.students.push({ userid: '', first_name: '', last_name: '', phone: '', email: '' })
const removeBulkRow = (i) => bulkForm.value.students.splice(i, 1)

const handleBulkAdd = async () => {
  const valid = bulkForm.value.students.filter(s => s.userid && s.first_name && s.last_name && s.email)
  if (!valid.length) {
    error.value = 'Add at least one student with userid, first_name, last_name, email'
    return
  }
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const res = await studentsApi.createBulk({ students: valid })
    successMsg.value = `Added ${res.created || valid.length} student(s)`
    bulkForm.value.students = [{ userid: '', first_name: '', last_name: '', phone: '', email: '' }]
    subTab.value = 'list'
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add students'
  } finally {
    loading.value = false
  }
}

const openEdit = (s) => {
  editStudent.value = s
  editForm.value = { first_name: s.first_name, last_name: s.last_name, phone: s.phone || '', email: s.email }
  editModal.value = true
}

const handleUpdateStudent = async () => {
  if (!editStudent.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.update(editStudent.value.userid, editForm.value)
    successMsg.value = 'Student updated'
    editModal.value = false
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update student'
  } finally {
    loading.value = false
  }
}

const handleDeleteStudent = async (userid) => {
  if (!confirm('Delete this student?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.delete(userid)
    successMsg.value = 'Student deleted'
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete student'
  } finally {
    loading.value = false
  }
}

const handleBulkDelete = async () => {
  const ids = bulkDeleteIds.value.split(/[\s,]+/).filter(Boolean)
  if (!ids.length) { error.value = 'Enter user IDs'; return }
  if (!confirm(`Delete ${ids.length} student(s)?`)) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.bulkDelete(ids)
    successMsg.value = 'Deleted student(s)'
    bulkDeleteIds.value = ''
    subTab.value = 'list'
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete students'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="section-content">
    <div class="section-tabs d-flex gap-2 mb-4 flex-wrap">
      <button type="button" :class="['section-tab', { active: subTab === 'list' }]" @click="subTab = 'list'">
        <i class="bi bi-mortarboard me-2"></i>List Students
      </button>
      <button type="button" :class="['section-tab', { active: subTab === 'add' }]" @click="subTab = 'add'">
        <i class="bi bi-person-plus me-2"></i>Add Student
      </button>
      <button type="button" :class="['section-tab', { active: subTab === 'bulk-add' }]" @click="subTab = 'bulk-add'">
        <i class="bi bi-cloud-upload me-2"></i>Bulk Add
      </button>
      <button type="button" :class="['section-tab', { active: subTab === 'bulk-delete' }]" @click="subTab = 'bulk-delete'">
        <i class="bi bi-trash me-2 text-danger"></i>Bulk Delete
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
              <input v-model="filters.search" type="text" class="form-control" placeholder="Search name, email, ID" @keyup.enter="fetchStudents" />
            </div>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="fetchStudents">
              <i class="bi bi-search me-1"></i>Search
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>User ID</th>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in students" :key="s.userid">
                <td>{{ s.userid }}</td>
                <td>{{ s.first_name }}</td>
                <td>{{ s.last_name }}</td>
                <td>{{ s.phone || '-' }}</td>
                <td>{{ s.email }}</td>
                <td class="text-end">
                  <button type="button" class="btn btn-sm btn-action btn-edit" @click="openEdit(s)" title="Edit"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-sm btn-action btn-delete" @click="handleDeleteStudent(s.userid)" title="Delete"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
              <tr v-if="students.length === 0">
                <td colspan="6" class="text-center text-muted py-4">No students found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-show="subTab === 'add'" class="card border-0 shadow-sm">
      <div class="card-body">
        <form @submit.prevent="handleAddStudent" class="row g-3">
          <div class="col-md-6">
            <label class="form-label">User ID *</label>
            <input v-model="addForm.userid" type="text" class="form-control" required placeholder="e.g. S001" />
          </div>
          <div class="col-md-6">
            <label class="form-label">First Name *</label>
            <input v-model="addForm.first_name" type="text" class="form-control" required />
          </div>
          <div class="col-md-6">
            <label class="form-label">Last Name *</label>
            <input v-model="addForm.last_name" type="text" class="form-control" required />
          </div>
          <div class="col-md-6">
            <label class="form-label">Phone</label>
            <input v-model="addForm.phone" type="text" class="form-control" placeholder="Phone" />
          </div>
          <div class="col-12">
            <label class="form-label">Email *</label>
            <input v-model="addForm.email" type="email" class="form-control" required />
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-teal" :disabled="loading">Add Student</button>
          </div>
        </form>
      </div>
    </div>

    <div v-show="subTab === 'bulk-add'" class="card border-0 shadow-sm">
      <div class="card-body">
        <button type="button" class="btn btn-outline-secondary mb-3" @click="addBulkRow"><i class="bi bi-plus me-1"></i>Add Row</button>
        <form @submit.prevent="handleBulkAdd">
          <div v-for="(s, i) in bulkForm.students" :key="i" class="row g-2 align-items-center mb-2">
            <div class="col"><input v-model="s.userid" class="form-control form-control-sm" placeholder="User ID" /></div>
            <div class="col"><input v-model="s.first_name" class="form-control form-control-sm" placeholder="First Name" /></div>
            <div class="col"><input v-model="s.last_name" class="form-control form-control-sm" placeholder="Last Name" /></div>
            <div class="col"><input v-model="s.phone" class="form-control form-control-sm" placeholder="Phone" /></div>
            <div class="col"><input v-model="s.email" type="email" class="form-control form-control-sm" placeholder="Email" /></div>
            <div class="col-auto"><button type="button" class="btn btn-sm btn-outline-danger" @click="removeBulkRow(i)"><i class="bi bi-x"></i></button></div>
          </div>
          <button type="submit" class="btn btn-teal mt-2" :disabled="loading">Add All</button>
        </form>
      </div>
    </div>

    <div v-show="subTab === 'bulk-delete'" class="card border-0 shadow-sm">
      <div class="card-body">
        <label class="form-label">User IDs (comma or space separated)</label>
        <textarea v-model="bulkDeleteIds" class="form-control mb-3" rows="4" placeholder="S001, S002"></textarea>
        <button type="button" class="btn btn-danger" @click="handleBulkDelete" :disabled="loading">Delete Selected</button>
      </div>
    </div>

    <div v-if="editModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Student</h5>
            <button type="button" class="btn-close" @click="editModal = false"></button>
          </div>
          <form @submit.prevent="handleUpdateStudent">
            <div class="modal-body">
              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label">First Name</label>
                  <input v-model="editForm.first_name" type="text" class="form-control" required />
                </div>
                <div class="col-6">
                  <label class="form-label">Last Name</label>
                  <input v-model="editForm.last_name" type="text" class="form-control" required />
                </div>
              </div>
              <div class="mb-3 mt-2">
                <label class="form-label">Phone</label>
                <input v-model="editForm.phone" type="text" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="editForm.email" type="email" class="form-control" required />
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
.btn-action { width: 36px; height: 36px; padding: 0; border-radius: 8px; margin-left: 0.25rem; }
.btn-edit { border: 1px solid #0d6efd; color: #0d6efd; background: rgba(13, 110, 253, 0.08); }
.btn-edit:hover { background: rgba(13, 110, 253, 0.15); color: #0d6efd; }
.btn-delete { border: 1px solid #dc3545; color: #dc3545; background: rgba(220, 53, 69, 0.08); }
.btn-delete:hover { background: rgba(220, 53, 69, 0.15); color: #dc3545; }
</style>

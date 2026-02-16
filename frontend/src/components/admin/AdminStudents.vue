<script setup>
import { ref, onMounted } from 'vue'
import { studentsApi } from '../../services/api'

const students = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list')

const filters = ref({ name: '', email: '', userid: '', page: 1, limit: 20 })

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
    if (filters.value.name) params.name = filters.value.name
    if (filters.value.email) params.email = filters.value.email
    if (filters.value.userid) params.userid = filters.value.userid
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

onMounted(() => fetchStudents())

const handleAddStudent = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.createSingle(addForm.value)
    successMsg.value = 'Student added successfully'
    addForm.value = { userid: '', first_name: '', last_name: '', phone: '', email: '' }
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add student'
  } finally {
    loading.value = false
  }
}

const addBulkRow = () => {
  bulkForm.value.students.push({ userid: '', first_name: '', last_name: '', phone: '', email: '' })
}
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
  if (!ids.length) {
    error.value = 'Enter user IDs'
    return
  }
  if (!confirm(`Delete ${ids.length} student(s)?`)) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentsApi.bulkDelete(ids)
    successMsg.value = `Deleted student(s)`
    bulkDeleteIds.value = ''
    fetchStudents()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete students'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-students">
    <div class="tabs">
      <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">List Students</button>
      <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Add Student</button>
      <button :class="{ active: subTab === 'bulk-add' }" @click="subTab = 'bulk-add'">Bulk Add</button>
      <button :class="{ active: subTab === 'bulk-delete' }" @click="subTab = 'bulk-delete'">Bulk Delete</button>
    </div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <div v-show="subTab === 'list'" class="content-block">
      <div class="filters">
        <input v-model="filters.userid" placeholder="User ID" @keyup.enter="fetchStudents" />
        <input v-model="filters.name" placeholder="Search by name" @keyup.enter="fetchStudents" />
        <input v-model="filters.email" placeholder="Search by email" @keyup.enter="fetchStudents" />
        <button class="btn btn-primary" @click="fetchStudents">Search</button>
      </div>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.userid">
            <td>{{ s.userid }}</td>
            <td>{{ s.first_name }}</td>
            <td>{{ s.last_name }}</td>
            <td>{{ s.phone }}</td>
            <td>{{ s.email }}</td>
            <td>
              <button class="btn-sm btn-edit" @click="openEdit(s)">Edit</button>
              <button class="btn-sm btn-delete" @click="handleDeleteStudent(s.userid)">Delete</button>
            </td>
          </tr>
          <tr v-if="students.length === 0">
            <td colspan="6" class="empty">No students found</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <div v-show="subTab === 'add'" class="content-block">
      <form @submit.prevent="handleAddStudent" class="form-add">
        <div class="form-row">
          <div class="form-group">
            <label>User ID *</label>
            <input v-model="addForm.userid" required placeholder="e.g. S001" />
          </div>
          <div class="form-group">
            <label>First Name *</label>
            <input v-model="addForm.first_name" required />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Last Name *</label>
            <input v-model="addForm.last_name" required />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="addForm.phone" placeholder="Phone" />
          </div>
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input v-model="addForm.email" type="email" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Add Student</button>
      </form>
    </div>

    <div v-show="subTab === 'bulk-add'" class="content-block">
      <button class="btn btn-secondary" @click="addBulkRow">+ Add Row</button>
      <form @submit.prevent="handleBulkAdd" class="form-bulk">
        <div v-for="(s, i) in bulkForm.students" :key="i" class="bulk-row">
          <input v-model="s.userid" placeholder="User ID" />
          <input v-model="s.first_name" placeholder="First Name" />
          <input v-model="s.last_name" placeholder="Last Name" />
          <input v-model="s.phone" placeholder="Phone" />
          <input v-model="s.email" type="email" placeholder="Email" />
          <button type="button" class="btn-remove" @click="removeBulkRow(i)">×</button>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Add All</button>
      </form>
    </div>

    <div v-show="subTab === 'bulk-delete'" class="content-block">
      <div class="form-group">
        <label>User IDs (comma or space separated)</label>
        <textarea v-model="bulkDeleteIds" rows="4" placeholder="S001, S002"></textarea>
      </div>
      <button class="btn btn-danger" @click="handleBulkDelete" :disabled="loading">Delete Selected</button>
    </div>

    <div v-if="editModal" class="modal-overlay" @click="editModal = false">
      <div class="modal-content" @click.stop>
        <h3>Edit Student</h3>
        <form @submit.prevent="handleUpdateStudent">
          <div class="form-row">
            <div class="form-group">
              <label>First Name</label>
              <input v-model="editForm.first_name" required />
            </div>
            <div class="form-group">
              <label>Last Name</label>
              <input v-model="editForm.last_name" required />
            </div>
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="editForm.phone" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="editForm.email" type="email" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="editModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-students { width: 100%; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.tabs button { padding: 0.5rem 1rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); background: var(--color-surface); border-radius: 8px; font-weight: 600; cursor: pointer; color: var(--color-muted); }
.tabs button:hover { border-color: var(--color-primary); color: var(--color-primary); }
.tabs button.active { background: var(--color-primary); border-color: var(--color-primary); color: white; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: var(--color-danger-bg); color: var(--color-danger); }
.alert-success { background: var(--color-success-bg); color: var(--color-success); }
.content-block { background: var(--color-surface); padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent); }
.filters { display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filters input { padding: 0.5rem 0.75rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); border-radius: 8px; min-width: 140px; background: var(--color-surface); color: var(--color-text); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid color-mix(in srgb, var(--color-border) 70%, transparent); }
.data-table th { font-weight: 600; background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface)); color: color-mix(in srgb, var(--color-heading) 85%, transparent); }
.data-table td.empty { text-align: center; color: var(--color-muted); padding: 2rem; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; margin-right: 0.5rem; }
.btn-edit { background: color-mix(in srgb, var(--color-primary) 12%, var(--color-surface)); color: var(--color-primary-strong); }
.btn-delete { background: var(--color-danger-bg); color: var(--color-danger); }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group input, .form-group textarea { width: 100%; padding: 0.5rem 0.75rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); border-radius: 8px; background: var(--color-surface); color: var(--color-text); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-secondary { background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface)); color: var(--color-muted); margin-bottom: 1rem; }
.btn-danger { background: var(--color-danger); color: white; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.bulk-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1.5fr auto; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; }
.bulk-row input { padding: 0.4rem; border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent); border-radius: 6px; background: var(--color-surface); color: var(--color-text); }
.btn-remove { background: var(--color-danger-bg); color: var(--color-danger); border: none; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--color-surface); border-radius: 12px; padding: 2rem; max-width: 450px; width: 100%; border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent); }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }

.admin-students .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.admin-students .data-table { min-width: 560px; }
@media (max-width: 768px) {
  .admin-students .filters { flex-direction: column; }
  .admin-students .filters input { min-width: 100%; }
  .admin-students .form-row { grid-template-columns: 1fr; }
  .admin-students .bulk-row { grid-template-columns: 1fr 1fr 1fr auto; }
  .admin-students .data-table th, .admin-students .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

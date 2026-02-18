<script setup>
import { ref, onMounted } from 'vue'
import { usersApi } from '@/services/api'

const users = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list')

const filters = ref({ role: '', search: '', active: '', sort: 'userid', order: 'asc', page: 1, limit: 20 })
const totalPages = ref(1)

const addForm = ref({ userid: '', username: '', email: '', password: '', role: 'student', active: true })
const bulkForm = ref({ users: [{ userid: '', username: '', email: '', password: '', role: 'student', active: true }] })
const bulkDeleteIds = ref('')

const editModal = ref(false)
const editUser = ref(null)
const editForm = ref({ username: '', email: '', password: '', role: '', active: null })

const ROLES = ['student', 'mentor', 'manager', 'clgadmin', 'admin']

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.role) params.role = filters.value.role
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.active !== '') params.active = filters.value.active === 'true'
    params.sort = filters.value.sort
    params.order = filters.value.order
    params.page = filters.value.page
    params.limit = filters.value.limit
    const res = await usersApi.list(params)
    users.value = res.users || []
    totalPages.value = Math.ceil((res.total || users.value.length) / filters.value.limit) || 1
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load users'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchUsers())

const handleAddUser = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await usersApi.createSingle(addForm.value)
    successMsg.value = 'User added successfully'
    addForm.value = { userid: '', username: '', email: '', password: '', role: 'student', active: true }
    subTab.value = 'list'
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add user'
  } finally {
    loading.value = false
  }
}

const addBulkRow = () => {
  bulkForm.value.users.push({ userid: '', username: '', email: '', password: '', role: 'student', active: true })
}

const removeBulkRow = (i) => bulkForm.value.users.splice(i, 1)

const handleBulkAdd = async () => {
  const valid = bulkForm.value.users.filter((u) => u.userid && u.username && u.email && u.password)
  if (valid.length === 0) {
    error.value = 'Add at least one user with userid, username, email, password'
    return
  }
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const res = await usersApi.createBulk({ users: valid })
    successMsg.value = `Added ${res.created} user(s). ${res.errors?.length ? 'Errors: ' + res.errors.length : ''}`
    bulkForm.value.users = [{ userid: '', username: '', email: '', password: '', role: 'student', active: true }]
    subTab.value = 'list'
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add users'
  } finally {
    loading.value = false
  }
}

const openEdit = (u) => {
  editUser.value = u
  editForm.value = { username: u.username, email: u.email, password: '', role: u.role, active: u.active }
  editModal.value = true
}

const handleUpdateUser = async () => {
  if (!editUser.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const updates = { ...editForm.value }
    if (!updates.password) delete updates.password
    await usersApi.update(editUser.value.userid, updates)
    successMsg.value = 'User updated'
    editModal.value = false
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update user'
  } finally {
    loading.value = false
  }
}

const handleDeleteUser = async (userid, soft = true) => {
  if (!confirm('Delete this user?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await usersApi.delete(userid, soft)
    successMsg.value = 'User deleted'
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete user'
  } finally {
    loading.value = false
  }
}

const handleBulkDelete = async () => {
  const ids = bulkDeleteIds.value.split(/[\s,]+/).filter(Boolean)
  if (ids.length === 0) {
    error.value = 'Enter user IDs'
    return
  }
  if (!confirm(`Delete ${ids.length} user(s)?`)) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const res = await usersApi.bulkDelete(ids, true)
    successMsg.value = `Deleted ${res.deleted} user(s)`
    bulkDeleteIds.value = ''
    subTab.value = 'list'
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete users'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="section-content">
    <div class="section-tabs d-flex gap-2 mb-4">
      <button type="button" :class="['section-tab', { active: subTab === 'list' }]" @click="subTab = 'list'">
        <i class="bi bi-people-fill me-2"></i>List Users
      </button>
      <button type="button" :class="['section-tab', { active: subTab === 'add' }]" @click="subTab = 'add'">
        <i class="bi bi-person-plus me-2"></i>Add User
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
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
              <input v-model="filters.search" type="text" class="form-control" placeholder="Search username, email, ID" @keyup.enter="fetchUsers" />
            </div>
          </div>
          <div class="col-auto">
            <select v-model="filters.role" class="form-select" @change="fetchUsers">
              <option value="">All Roles</option>
              <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="col-auto">
            <select v-model="filters.active" class="form-select" @change="fetchUsers">
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="fetchUsers">
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
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Active</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.userid">
                <td>{{ u.userid }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.email }}</td>
                <td><span class="badge bg-success">{{ u.role }}</span></td>
                <td><span class="badge" :class="u.active ? 'bg-success' : 'bg-secondary'">{{ u.active ? 'Yes' : 'No' }}</span></td>
                <td class="text-end">
                  <button type="button" class="btn btn-sm btn-action btn-edit" @click="openEdit(u)" title="Edit"><i class="bi bi-pencil"></i></button>
                  <button type="button" class="btn btn-sm btn-action btn-delete" @click="handleDeleteUser(u.userid)" title="Delete"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="6" class="text-center text-muted py-4">No users found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-show="subTab === 'add'" class="card border-0 shadow-sm">
      <div class="card-body">
        <form @submit.prevent="handleAddUser" class="row g-3">
          <div class="col-md-6">
            <label class="form-label">User ID *</label>
            <input v-model="addForm.userid" type="text" class="form-control" required placeholder="e.g. EMP001" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Username *</label>
            <input v-model="addForm.username" type="text" class="form-control" required placeholder="Full name" />
          </div>
          <div class="col-12">
            <label class="form-label">Email *</label>
            <input v-model="addForm.email" type="email" class="form-control" required placeholder="email@example.com" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Password *</label>
            <input v-model="addForm.password" type="password" class="form-control" required placeholder="Password" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Role</label>
            <select v-model="addForm.role" class="form-select">
              <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="col-12">
            <div class="form-check">
              <input v-model="addForm.active" type="checkbox" class="form-check-input" id="addActive" />
              <label class="form-check-label" for="addActive">Active</label>
            </div>
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-teal" :disabled="loading">Add User</button>
          </div>
        </form>
      </div>
    </div>

    <div v-show="subTab === 'bulk-add'" class="card border-0 shadow-sm">
      <div class="card-body">
        <button type="button" class="btn btn-outline-secondary mb-3" @click="addBulkRow"><i class="bi bi-plus me-1"></i>Add Row</button>
        <form @submit.prevent="handleBulkAdd">
          <div v-for="(u, i) in bulkForm.users" :key="i" class="row g-2 align-items-center mb-2">
            <div class="col"><input v-model="u.userid" class="form-control form-control-sm" placeholder="User ID" /></div>
            <div class="col"><input v-model="u.username" class="form-control form-control-sm" placeholder="Username" /></div>
            <div class="col"><input v-model="u.email" type="email" class="form-control form-control-sm" placeholder="Email" /></div>
            <div class="col"><input v-model="u.password" type="password" class="form-control form-control-sm" placeholder="Password" /></div>
            <div class="col-auto"><select v-model="u.role" class="form-select form-select-sm"><option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option></select></div>
            <div class="col-auto"><button type="button" class="btn btn-sm btn-outline-danger" @click="removeBulkRow(i)"><i class="bi bi-x"></i></button></div>
          </div>
          <button type="submit" class="btn btn-teal mt-2" :disabled="loading">Add All</button>
        </form>
      </div>
    </div>

    <div v-show="subTab === 'bulk-delete'" class="card border-0 shadow-sm">
      <div class="card-body">
        <label class="form-label">User IDs (comma or space separated)</label>
        <textarea v-model="bulkDeleteIds" class="form-control mb-3" rows="4" placeholder="EMP001, EMP002, EMP003"></textarea>
        <button type="button" class="btn btn-danger" @click="handleBulkDelete" :disabled="loading">Delete Selected</button>
      </div>
    </div>

    <div v-if="editModal" class="modal show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit User</h5>
            <button type="button" class="btn-close" @click="editModal = false"></button>
          </div>
          <form @submit.prevent="handleUpdateUser">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="editForm.username" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="editForm.email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password (leave blank to keep)</label>
                <input v-model="editForm.password" type="password" class="form-control" placeholder="New password" />
              </div>
              <div class="mb-3">
                <label class="form-label">Role</label>
                <select v-model="editForm.role" class="form-select">
                  <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>
              <div class="form-check">
                <input v-model="editForm.active" type="checkbox" class="form-check-input" id="editActive" />
                <label class="form-check-label" for="editActive">Active</label>
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
.btn-teal {
  background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%);
  border: none;
  color: white;
  font-weight: 600;
}
.btn-teal:hover { opacity: 0.95; color: white; }
.btn-action {
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 8px;
  margin-left: 0.25rem;
}
.btn-edit { border: 1px solid #0d6efd; color: #0d6efd; background: rgba(13, 110, 253, 0.08); }
.btn-edit:hover { background: rgba(13, 110, 253, 0.15); color: #0d6efd; }
.btn-delete { border: 1px solid #dc3545; color: #dc3545; background: rgba(220, 53, 69, 0.08); }
.btn-delete:hover { background: rgba(220, 53, 69, 0.15); color: #dc3545; }
</style>

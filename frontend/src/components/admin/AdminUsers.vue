<script setup>
import { ref, onMounted } from 'vue'
import { usersApi } from '../../services/api'

const users = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const subTab = ref('list') // list | add | bulk-add | bulk-delete

const filters = ref({ role: '', name: '', email: '', active: '', search: '', sort: 'userid', order: 'asc', page: 1, limit: 20 })
const totalPages = ref(1)

const addForm = ref({
  userid: '',
  username: '',
  email: '',
  password: '',
  role: 'student',
  active: true,
})

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
    if (filters.value.name) params.name = filters.value.name
    if (filters.value.email) params.email = filters.value.email
    if (filters.value.active !== '') params.active = filters.value.active === 'true'
    if (filters.value.search) params.search = filters.value.search
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

const removeBulkRow = (i) => {
  bulkForm.value.users.splice(i, 1)
}

const handleBulkAdd = async () => {
  const valid = bulkForm.value.users.filter(
    (u) => u.userid && u.username && u.email && u.password
  )
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
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete users'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-users">
    <div class="tabs">
      <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">List Users</button>
      <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Add User</button>
      <button :class="{ active: subTab === 'bulk-add' }" @click="subTab = 'bulk-add'">Bulk Add</button>
      <button :class="{ active: subTab === 'bulk-delete' }" @click="subTab = 'bulk-delete'">Bulk Delete</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

    <!-- List Users -->
    <div v-show="subTab === 'list'" class="content-block">
      <div class="filters">
        <input v-model="filters.search" placeholder="Search username, email, ID" @keyup.enter="fetchUsers" class="search-inp" />
        <select v-model="filters.role" @change="fetchUsers">
          <option value="">All Roles</option>
          <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
        </select>
        <input v-model="filters.name" placeholder="Name" @keyup.enter="fetchUsers" />
        <input v-model="filters.email" placeholder="Email" @keyup.enter="fetchUsers" />
        <select v-model="filters.active" @change="fetchUsers">
          <option value="">All</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
        <select v-model="filters.sort" @change="fetchUsers">
          <option value="userid">User ID</option>
          <option value="username">Username</option>
          <option value="email">Email</option>
          <option value="role">Role</option>
        </select>
        <select v-model="filters.order" @change="fetchUsers">
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
        <button class="btn btn-primary" @click="fetchUsers">Search</button>
      </div>

      <div v-if="loading" class="loading">Loading...</div>
      <div v-else class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.userid">
            <td>{{ u.userid }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.role }}</td>
            <td>{{ u.active ? 'Yes' : 'No' }}</td>
            <td>
              <button class="btn-sm btn-edit" @click="openEdit(u)">Edit</button>
              <button class="btn-sm btn-delete" @click="handleDeleteUser(u.userid)">Delete</button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="empty">No users found</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Add User -->
    <div v-show="subTab === 'add'" class="content-block">
      <form @submit.prevent="handleAddUser" class="form-add">
        <div class="form-row">
          <div class="form-group">
            <label>User ID *</label>
            <input v-model="addForm.userid" required placeholder="e.g. EMP001" />
          </div>
          <div class="form-group">
            <label>Username *</label>
            <input v-model="addForm.username" required placeholder="Full name" />
          </div>
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input v-model="addForm.email" type="email" required placeholder="email@example.com" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Password *</label>
            <input v-model="addForm.password" type="password" required placeholder="Password" />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="addForm.role">
              <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
        </div>
        <div class="form-group checkbox">
          <label><input v-model="addForm.active" type="checkbox" /> Active</label>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Add User</button>
      </form>
    </div>

    <!-- Bulk Add -->
    <div v-show="subTab === 'bulk-add'" class="content-block">
      <button class="btn btn-secondary" @click="addBulkRow">+ Add Row</button>
      <form @submit.prevent="handleBulkAdd" class="form-bulk">
        <div v-for="(u, i) in bulkForm.users" :key="i" class="bulk-row">
          <input v-model="u.userid" placeholder="User ID" />
          <input v-model="u.username" placeholder="Username" />
          <input v-model="u.email" type="email" placeholder="Email" />
          <input v-model="u.password" type="password" placeholder="Password" />
          <select v-model="u.role">
            <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
          </select>
          <button type="button" class="btn-remove" @click="removeBulkRow(i)">×</button>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Add All</button>
      </form>
    </div>

    <!-- Bulk Delete -->
    <div v-show="subTab === 'bulk-delete'" class="content-block">
      <div class="form-group">
        <label>User IDs (comma or space separated)</label>
        <textarea v-model="bulkDeleteIds" rows="4" placeholder="EMP001, EMP002, EMP003"></textarea>
      </div>
      <button class="btn btn-danger" @click="handleBulkDelete" :disabled="loading">Delete Selected</button>
    </div>

    <!-- Edit Modal -->
    <div v-if="editModal" class="modal-overlay" @click="editModal = false">
      <div class="modal-content" @click.stop>
        <h3>Edit User</h3>
        <form @submit.prevent="handleUpdateUser">
          <div class="form-group">
            <label>Username</label>
            <input v-model="editForm.username" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="editForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Password (leave blank to keep)</label>
            <input v-model="editForm.password" type="password" placeholder="New password" />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="editForm.role">
              <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="form-group checkbox">
            <label><input v-model="editForm.active" type="checkbox" /> Active</label>
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
.admin-users {
  width: 100%;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tabs button {
  padding: 0.5rem 1rem;
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
  background: var(--color-surface);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  color: var(--color-muted);
  transition: all 0.2s;
}

.tabs button:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tabs button.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.alert-error {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.alert-success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.content-block {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent);
}

.filters {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filters input,
.filters select {
  padding: 0.5rem 0.75rem;
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
  border-radius: 8px;
  font-size: 0.9rem;
  background: var(--color-surface);
  color: var(--color-text);
}

.filters input {
  min-width: 120px;
  flex: 1;
}

@media (max-width: 768px) {
  .admin-users .filters {
    flex-direction: column;
  }
  .admin-users .filters input,
  .admin-users .filters select {
    min-width: 100%;
  }
  .admin-users .users-table th,
  .admin-users .users-table td {
    padding: 0.5rem;
    font-size: 0.85rem;
  }
  .admin-users .form-row {
    grid-template-columns: 1fr;
  }
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 70%, transparent);
}

.users-table th {
  font-weight: 600;
  color: color-mix(in srgb, var(--color-heading) 85%, transparent);
  background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface));
}

.users-table td.empty {
  text-align: center;
  color: var(--color-muted);
  padding: 2rem;
}

.btn-sm {
  padding: 0.35rem 0.65rem;
  font-size: 0.8rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  margin-right: 0.5rem;
}

.btn-edit {
  background: color-mix(in srgb, var(--color-primary) 12%, var(--color-surface));
  color: var(--color-primary-strong);
}

.btn-edit:hover {
  background: color-mix(in srgb, var(--color-primary) 20%, var(--color-surface));
}

.btn-delete {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.btn-delete:hover {
  background: color-mix(in srgb, var(--color-danger) 18%, var(--color-surface));
}

.form-add,
.form-bulk {
  max-width: 600px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
  border-radius: 8px;
  font-size: 0.95rem;
  background: var(--color-surface);
  color: var(--color-text);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-group.checkbox input {
  width: auto;
}

.btn {
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 0.95rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-strong);
}

.btn-secondary {
  background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface));
  color: var(--color-muted);
  margin-bottom: 1rem;
}

.btn-secondary:hover {
  background: color-mix(in srgb, var(--color-surface-2) 88%, var(--color-surface));
}

.btn-danger {
  background: var(--color-danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-danger) 85%, #000);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.bulk-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1.5fr 1fr 1fr auto;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.5rem;
}

.bulk-row input,
.bulk-row select {
  padding: 0.4rem 0.6rem;
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--color-surface);
  color: var(--color-text);
}

.btn-remove {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 2rem;
  max-width: 450px;
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent);
}

.modal-content h3 {
  margin: 0 0 1rem 0;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .admin-users .bulk-row {
    grid-template-columns: 1fr 1fr auto;
  }
  .admin-users .bulk-row input:nth-child(3),
  .admin-users .bulk-row input:nth-child(4) {
    grid-column: span 2;
  }
}

.admin-users .table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.admin-users .users-table {
  min-width: 580px;
}
</style>

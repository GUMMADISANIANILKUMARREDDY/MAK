<script setup>
import { ref, onMounted } from 'vue'
import { permissionsApi } from '@/services/api'

const permissions = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const form = ref({ role: 'student', resource: 'tasks', action: 'read', grant: true })
const roles = ['admin', 'manager', 'mentor', 'student', 'clgadmin']
const resources = ['users', 'students', 'projects', 'modules', 'tasks', 'notifications']
const actions = ['create', 'read', 'update', 'delete']

async function fetchPermissions() {
  loading.value = true
  error.value = ''
  try {
    const res = await permissionsApi.list()
    permissions.value = res.permissions || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function handleSet() {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await permissionsApi.set(form.value)
    successMsg.value = 'Permission set'
    fetchPermissions()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchPermissions())
</script>

<template>
  <div class="section-content">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-4">Role Permissions</h5>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

        <div class="row g-2 align-items-end mb-4">
          <div class="col-md-2">
            <label class="form-label">Role</label>
            <select v-model="form.role" class="form-select">
              <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Resource</label>
            <select v-model="form.resource" class="form-select">
              <option v-for="r in resources" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Action</label>
            <select v-model="form.action" class="form-select">
              <option v-for="a in actions" :key="a" :value="a">{{ a }}</option>
            </select>
          </div>
          <div class="col-auto">
            <div class="form-check mb-0">
              <input v-model="form.grant" type="checkbox" class="form-check-input" id="grant" />
              <label class="form-check-label" for="grant">Grant</label>
            </div>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="handleSet" :disabled="loading">Set</button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Role</th>
                <th>Resource</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in permissions" :key="p.id">
                <td><span class="badge bg-success">{{ p.role }}</span></td>
                <td>{{ p.resource }}</td>
                <td>{{ p.action }}</td>
              </tr>
              <tr v-if="permissions.length === 0">
                <td colspan="3" class="text-center text-muted py-4">No custom permissions. Admins have full access by default.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-teal { background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%); border: none; color: white; font-weight: 600; }
.btn-teal:hover { opacity: 0.95; color: white; }
</style>

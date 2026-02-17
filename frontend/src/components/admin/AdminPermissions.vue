<script setup>
import { ref, onMounted } from 'vue'
import { permissionsApi } from '@/services/api'

const permissions = ref([])
const loading = ref(false)
const error = ref('')
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
  try {
    await permissionsApi.set(form.value)
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
  <div class="admin-permissions">
    <h3>Role Permissions</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div class="form-inline">
      <select v-model="form.role">
        <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
      </select>
      <select v-model="form.resource">
        <option v-for="r in resources" :key="r" :value="r">{{ r }}</option>
      </select>
      <select v-model="form.action">
        <option v-for="a in actions" :key="a" :value="a">{{ a }}</option>
      </select>
      <label><input v-model="form.grant" type="checkbox" /> Grant</label>
      <button class="btn btn-primary" @click="handleSet">Set</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <table v-else class="table">
      <thead>
        <tr><th>Role</th><th>Resource</th><th>Action</th></tr>
      </thead>
      <tbody>
        <tr v-for="p in permissions" :key="p.id">
          <td>{{ p.role }}</td><td>{{ p.resource }}</td><td>{{ p.action }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="!loading && permissions.length === 0" class="empty">No custom permissions. Admins have full access by default.</p>
  </div>
</template>

<style scoped>
.form-inline { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 0.4rem; border-bottom: 1px solid var(--color-border); text-align: left; }
.empty { color: var(--color-muted); }
</style>

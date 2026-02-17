<script setup>
import { ref, onMounted } from 'vue'
import { activityLogsApi } from '@/services/api'

const logs = ref([])
const loading = ref(false)
const error = ref('')
const filters = ref({ userid: '', entity_type: '', entity_id: '', date_from: '', date_to: '', page: 1, limit: 50 })

async function fetchLogs() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: filters.value.page, limit: filters.value.limit }
    if (filters.value.userid) params.userid = filters.value.userid
    if (filters.value.entity_type) params.entity_type = filters.value.entity_type
    if (filters.value.entity_id) params.entity_id = filters.value.entity_id
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    const res = await activityLogsApi.list(params)
    logs.value = res.logs || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load logs'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchLogs())
</script>

<template>
  <div class="admin-activity-logs">
    <h3>Activity Logs</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div class="filters">
      <input v-model="filters.userid" placeholder="User ID" @keyup.enter="fetchLogs" />
      <input v-model="filters.entity_type" placeholder="Entity type" @keyup.enter="fetchLogs" />
      <input v-model="filters.entity_id" placeholder="Entity ID" @keyup.enter="fetchLogs" />
      <input v-model="filters.date_from" type="date" />
      <input v-model="filters.date_to" type="date" />
      <button class="btn btn-primary" @click="fetchLogs">Search</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="content-block">
      <table class="logs-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>User</th>
            <th>Action</th>
            <th>Entity</th>
            <th>ID</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ log.created_at ? new Date(log.created_at).toLocaleString() : '' }}</td>
            <td>{{ log.userid }}</td>
            <td>{{ log.action }}</td>
            <td>{{ log.entity_type }}</td>
            <td>{{ log.entity_id }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="logs.length === 0" class="empty">No activity logs.</p>
    </div>
  </div>
</template>

<style scoped>
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.filters input { padding: 0.4rem 0.6rem; border-radius: 6px; border: 1px solid var(--color-border, #e5e7eb); }
.logs-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.logs-table th, .logs-table td { padding: 0.5rem; border-bottom: 1px solid var(--color-border); text-align: left; }
.logs-table th { background: var(--color-surface-2, #f3f4f6); }
.empty { color: var(--color-muted); padding: 1rem; }
</style>

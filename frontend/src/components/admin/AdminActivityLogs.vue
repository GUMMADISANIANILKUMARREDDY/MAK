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
  <div class="section-content">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-4">Activity Logs</h5>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div class="section-filters row g-2 align-items-center mb-3">
          <div class="col-md-2">
            <input v-model="filters.userid" type="text" class="form-control" placeholder="User ID" @keyup.enter="fetchLogs" />
          </div>
          <div class="col-md-2">
            <input v-model="filters.entity_type" type="text" class="form-control" placeholder="Entity type" @keyup.enter="fetchLogs" />
          </div>
          <div class="col-md-2">
            <input v-model="filters.entity_id" type="text" class="form-control" placeholder="Entity ID" @keyup.enter="fetchLogs" />
          </div>
          <div class="col-auto">
            <input v-model="filters.date_from" type="date" class="form-control" @change="fetchLogs" />
          </div>
          <div class="col-auto">
            <input v-model="filters.date_to" type="date" class="form-control" @change="fetchLogs" />
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="fetchLogs">
              <i class="bi bi-search me-1"></i>Search
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
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
                <td><span class="badge bg-secondary">{{ log.action }}</span></td>
                <td>{{ log.entity_type }}</td>
                <td>{{ log.entity_id }}</td>
              </tr>
              <tr v-if="logs.length === 0">
                <td colspan="5" class="text-center text-muted py-4">No activity logs</td>
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

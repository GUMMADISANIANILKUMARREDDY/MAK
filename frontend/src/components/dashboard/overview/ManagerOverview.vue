<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/services/api'
import OverviewHeader from './OverviewHeader.vue'

const props = defineProps({ username: { type: String, default: '' } })
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await dashboardApi.getManagerStats()
  } catch {
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="manager-overview">
    <OverviewHeader :username="username" subtitle="Here's your manager dashboard overview." />

    <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Total Modules</p>
            <h3 class="mb-0 fw-bold">{{ stats?.total_modules ?? 0 }}</h3>
            <i class="bi bi-grid-3x3-gap-fill text-primary fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm border-primary border-opacity-25">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Tasks Pending Review</p>
            <h3 class="mb-0 fw-bold text-primary">{{ stats?.tasks_pending_review ?? 0 }}</h3>
            <i class="bi bi-clipboard-check text-primary fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="fw-bold">Modules by Status</h5>
            <div class="row g-2 mt-2" v-if="stats?.modules_by_status && Object.keys(stats.modules_by_status).length">
              <div class="col-auto" v-for="(count, status) in stats.modules_by_status" :key="status">
                <span class="badge bg-secondary">{{ status }}: {{ count }}</span>
              </div>
            </div>
            <p v-else class="text-muted mb-0">No modules yet.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

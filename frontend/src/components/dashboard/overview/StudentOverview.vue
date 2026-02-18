<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/services/api'
import OverviewHeader from './OverviewHeader.vue'

const props = defineProps({ username: { type: String, default: '' } })
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await dashboardApi.getStudentStats()
  } catch {
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="student-overview">
    <OverviewHeader :username="username" subtitle="Here's your task overview." />

    <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
    <div v-else class="row g-3">
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Total Tasks</p>
            <h3 class="mb-0 fw-bold">{{ stats?.total ?? 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Assigned</p>
            <h3 class="mb-0 fw-bold">{{ stats?.assigned ?? 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">In Progress</p>
            <h3 class="mb-0 fw-bold">{{ stats?.in_progress ?? 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">In Review</p>
            <h3 class="mb-0 fw-bold">{{ stats?.review ?? 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm bg-success bg-opacity-10">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Approved</p>
            <h3 class="mb-0 fw-bold text-success">{{ stats?.approved ?? 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4">
        <div class="card border-0 shadow-sm bg-danger bg-opacity-10">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Rejected</p>
            <h3 class="mb-0 fw-bold text-danger">{{ stats?.rejected ?? 0 }}</h3>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

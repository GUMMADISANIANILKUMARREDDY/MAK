<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/services/api'
import OverviewHeader from './OverviewHeader.vue'

const props = defineProps({ username: { type: String, default: '' } })
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await dashboardApi.getMentorStats()
  } catch {
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mentor-overview">
    <OverviewHeader :username="username" subtitle="Here's your mentor dashboard overview." />

    <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm border-primary border-opacity-25">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Tasks Pending Review</p>
            <h3 class="mb-0 fw-bold text-primary">{{ stats?.tasks_pending_review ?? 0 }}</h3>
            <i class="bi bi-clipboard-check text-primary fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Teams</p>
            <h3 class="mb-0 fw-bold">{{ stats?.teams_count ?? 0 }}</h3>
            <i class="bi bi-people-fill text-info fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">My Modules</p>
            <h3 class="mb-0 fw-bold">{{ stats?.modules_count ?? 0 }}</h3>
            <i class="bi bi-mortarboard-fill text-success fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

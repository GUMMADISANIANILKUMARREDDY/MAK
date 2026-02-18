<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/services/api'
import OverviewHeader from './OverviewHeader.vue'

const props = defineProps({ username: { type: String, default: '' } })
const stats = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await dashboardApi.getAdminStats()
  } catch {
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="college-admin-overview">
    <OverviewHeader :username="username" subtitle="Here's your college admin dashboard." />

    <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Users</p>
            <h3 class="mb-0 fw-bold">{{ stats?.total_users ?? 0 }}</h3>
            <i class="bi bi-people-fill text-primary fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
      <div class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small text-uppercase mb-1">Students</p>
            <h3 class="mb-0 fw-bold">{{ stats?.total_students ?? 0 }}</h3>
            <i class="bi bi-mortarboard-fill text-info fs-4 float-end opacity-75"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

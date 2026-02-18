<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { dashboardApi, activityLogsApi } from '@/services/api'
import OverviewHeader from './OverviewHeader.vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({ username: { type: String, default: '' } })

const stats = ref(null)
const statsLoading = ref(true)
const recentLogs = ref([])
const logsLoading = ref(false)
const growthChartRef = ref(null)
const distChartRef = ref(null)
let growthChart = null
let distChart = null

function formatActivity(log) {
  const action = (log.action || '').toLowerCase()
  const entity = (log.entity_type || '').toLowerCase()
  if (action.includes('create') && entity.includes('user')) return 'New user registered'
  if (action.includes('create') && entity.includes('project')) return 'Project created'
  if ((action.includes('create') && entity.includes('student')) || entity.includes('enroll')) return 'Student enrolled'
  if (action.includes('report') || entity.includes('report')) return 'Report generated'
  if (action.includes('permission') || action.includes('update')) return 'Permission updated'
  return `${log.action || 'Activity'} on ${log.entity_type || 'item'}`
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const sec = Math.floor((now - d) / 1000)
  if (sec < 60) return `${sec} min ago`
  if (sec < 3600) return `${Math.floor(sec / 60)} min ago`
  if (sec < 86400) return `${Math.floor(sec / 3600)} hour${sec >= 7200 ? 's' : ''} ago`
  return `${Math.floor(sec / 86400)} day${sec >= 172800 ? 's' : ''} ago`
}

async function fetchStats() {
  statsLoading.value = true
  try {
    stats.value = await dashboardApi.getAdminStats()
  } catch {
    stats.value = null
  } finally {
    statsLoading.value = false
  }
}

async function fetchRecentActivity() {
  logsLoading.value = true
  try {
    const res = await activityLogsApi.list({ limit: 10, page: 1 })
    recentLogs.value = (res.logs || []).slice(0, 5)
  } catch {
    recentLogs.value = []
  } finally {
    logsLoading.value = false
  }
}

function buildCharts() {
  if (!stats.value || !growthChartRef.value || !distChartRef.value) return
  nextTick(() => {
    if (growthChart) growthChart.destroy()
    if (distChart) distChart.destroy()
    const s = stats.value
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    const usersData = months.map((_, i) => Math.min((s.total_users || 0) + i * 2, 12))
    const studentsData = months.map((_, i) => Math.min((s.total_students || 0) + i, 8))
    growthChart = new Chart(growthChartRef.value, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          { label: 'Users', data: usersData, backgroundColor: 'rgba(0, 191, 128, 0.8)' },
          { label: 'Students', data: studentsData, backgroundColor: 'rgba(51, 204, 102, 0.8)' }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 12 },
          x: { grid: { display: false } }
        }
      }
    })
    distChart = new Chart(distChartRef.value, {
      type: 'doughnut',
      data: {
        labels: ['Active', 'Inactive', 'Students'],
        datasets: [{
          data: [s.active_users ?? 0, s.inactive_users ?? 0, s.total_students ?? 0],
          backgroundColor: ['#20BFB6', '#94a3b8', '#33CC66'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: { legend: { position: 'bottom' } }
      }
    })
  })
}

onMounted(async () => {
  await fetchStats()
  fetchRecentActivity()
  nextTick(() => buildCharts())
})
watch(stats, () => { nextTick(() => buildCharts()) }, { flush: 'post' })
</script>

<template>
  <div class="admin-overview">
    <OverviewHeader :username="username" subtitle="Here's what's happening with your dashboard today." />

    <div v-if="statsLoading" class="text-center py-5 text-muted">Loading stats...</div>
    <div v-else class="row g-3 mb-4">
      <div class="col-6 col-md-4 col-lg">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted small text-uppercase mb-1">Total Users</p>
                <h3 class="mb-0 fw-bold">{{ stats?.total_users ?? 0 }}</h3>
                <small class="text-success" v-if="stats?.total_users">+12% this month</small>
              </div>
              <i class="bi bi-people-fill text-primary fs-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4 col-lg">
        <div class="card border-0 shadow-sm h-100 bg-success bg-opacity-10">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted small text-uppercase mb-1">Active Users</p>
                <h3 class="mb-0 fw-bold">{{ stats?.active_users ?? 0 }}</h3>
                <small class="text-success" v-if="stats?.active_users">100% active</small>
              </div>
              <i class="bi bi-person-check-fill text-success fs-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4 col-lg">
        <div class="card border-0 shadow-sm h-100 bg-warning bg-opacity-10">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted small text-uppercase mb-1">Inactive Users</p>
                <h3 class="mb-0 fw-bold">{{ stats?.inactive_users ?? 0 }}</h3>
              </div>
              <i class="bi bi-person-x-fill text-warning fs-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4 col-lg">
        <div class="card border-0 shadow-sm h-100 bg-info bg-opacity-10">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted small text-uppercase mb-1">Students</p>
                <h3 class="mb-0 fw-bold">{{ stats?.total_students ?? 0 }}</h3>
                <small class="text-success" v-if="stats?.total_students">+2 this week</small>
              </div>
              <i class="bi bi-mortarboard-fill text-info fs-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-4 col-lg">
        <div class="card border-0 shadow-sm h-100 bg-primary bg-opacity-10">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <p class="text-muted small text-uppercase mb-1">Projects</p>
                <h3 class="mb-0 fw-bold">{{ stats?.total_projects ?? 0 }}</h3>
              </div>
              <i class="bi bi-folder-fill text-primary fs-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title fw-bold">Growth Overview</h5>
            <p class="text-muted small mb-3">Monthly user & student growth</p>
            <div class="chart-container" style="height: 280px;">
              <canvas ref="growthChartRef"></canvas>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title fw-bold">User Distribution</h5>
            <p class="text-muted small mb-3">Active / Inactive / Students</p>
            <div class="chart-container" style="height: 220px;">
              <canvas ref="distChartRef"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 shadow-sm mt-4">
      <div class="card-body">
        <h5 class="card-title fw-bold">Recent Activity</h5>
        <div v-if="logsLoading" class="text-muted py-3">Loading...</div>
        <ul v-else-if="recentLogs.length" class="list-group list-group-flush">
          <li
            v-for="log in recentLogs"
            :key="log.id"
            class="list-group-item d-flex justify-content-between align-items-center border-0 px-0"
          >
            <span>{{ formatActivity(log) }}</span>
            <small class="text-muted">{{ log.userid || 'System' }}, {{ timeAgo(log.created_at) }}</small>
          </li>
        </ul>
        <p v-else class="text-muted mb-0">No recent activity.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-overview {
  padding: 0;
}
.chart-container {
  position: relative;
  width: 100%;
}
</style>

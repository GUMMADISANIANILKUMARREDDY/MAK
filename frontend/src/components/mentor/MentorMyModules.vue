<script setup>
import { ref, onMounted } from 'vue'
import { mentorApi } from '../../services/api'

const modules = ref([])
const loading = ref(false)
const error = ref('')

const fetchModules = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await mentorApi.myModules()
    modules.value = res.modules || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load modules'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchModules())
</script>

<template>
  <div class="mentor-modules">
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="content-block">
      <h3>My Assigned Modules</h3>
      <div v-if="modules.length === 0" class="empty">No modules assigned to you.</div>
      <div v-else class="module-list">
        <div v-for="m in modules" :key="m.moduleid" class="module-card">
          <h4>{{ m.title }}</h4>
          <p class="desc">{{ (m.description || '').slice(0, 100) }}{{ (m.description || '').length > 100 ? '...' : '' }}</p>
          <div class="meta">
            <span class="badge">{{ m.priority || 'medium' }}</span>
            <span class="date">{{ m.due_date ? m.due_date.slice(0, 10) : '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mentor-modules { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.content-block { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.module-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.module-card { padding: 1rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.module-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; }
.module-card .desc { margin: 0; font-size: 0.85rem; color: #64748b; }
.module-card .meta { display: flex; gap: 0.5rem; margin-top: 0.75rem; }
.module-card .badge { font-size: 0.75rem; background: #e0f2fe; color: #0ea5e9; padding: 0.2rem 0.5rem; border-radius: 4px; }
.module-card .date { font-size: 0.8rem; color: #64748b; }
.loading, .empty { padding: 2rem; text-align: center; color: #64748b; }

@media (max-width: 768px) {
  .mentor-modules .module-list { grid-template-columns: 1fr; }
}
</style>

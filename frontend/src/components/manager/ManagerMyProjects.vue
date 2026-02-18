<script setup>
import { ref, onMounted } from 'vue'
import { managerApi } from '../../services/api'

const projects = ref([])
const loading = ref(false)
const error = ref('')

const selectedProject = ref(null)
const modules = ref([])
const modulesLoading = ref(false)

const fetchProjects = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await managerApi.myProjects()
    projects.value = res.projects || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load projects'
  } finally {
    loading.value = false
  }
}

const loadModules = async (project) => {
  selectedProject.value = project
  modulesLoading.value = true
  modules.value = []
  try {
    const res = await managerApi.getProjectModules(project.projectid)
    modules.value = res.modules || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load modules'
  } finally {
    modulesLoading.value = false
  }
}

onMounted(() => fetchProjects())
</script>

<template>
  <div class="section-content manager-projects">
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
    <div v-else class="card border-0 shadow-sm">
      <div class="card-body">
      <h5 class="card-title mb-4">My Assigned Projects</h5>
      <div v-if="projects.length === 0" class="text-center text-muted py-4">No projects assigned to you.</div>
      <div v-else class="project-list">
        <div
          v-for="p in projects"
          :key="p.projectid"
          class="project-card"
          :class="{ selected: selectedProject?.projectid === p.projectid }"
          @click="loadModules(p)"
        >
          <h4>{{ p.title }}</h4>
          <p class="desc">{{ (p.description || '').slice(0, 80) }}{{ (p.description || '').length > 80 ? '...' : '' }}</p>
          <span class="badge bg-success">{{ p.status || 'active' }}</span>
        </div>
      </div>
      <div v-if="selectedProject" class="modules-section">
        <h4>Modules in {{ selectedProject.title }}</h4>
        <div v-if="modulesLoading" class="text-center py-4 text-muted">Loading modules...</div>
        <div v-else class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>Title</th>
              <th>Priority</th>
              <th>Due Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in modules" :key="m.moduleid">
              <td>{{ m.title }}</td>
              <td>{{ m.priority || '-' }}</td>
              <td>{{ m.due_date ? m.due_date.slice(0, 10) : '-' }}</td>
              <td><span class="badge bg-success">{{ m.status || '-' }}</span></td>
            </tr>
            <tr v-if="modules.length === 0">
              <td colspan="4" class="text-center text-muted py-4">No modules yet</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.manager-projects { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.card-body { padding: 1.5rem; }
.project-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.project-card { padding: 1rem; border: 2px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.project-card:hover { border-color: #0ea5e9; background: #f0f9ff; }
.project-card.selected { border-color: #0ea5e9; background: #e0f2fe; }
.project-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; }
.project-card .desc { margin: 0; font-size: 0.85rem; color: #64748b; }
.project-card .badge { font-size: 0.75rem; background: #e0f2fe; color: #0ea5e9; padding: 0.2rem 0.5rem; border-radius: 4px; }
.modules-section { margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; }
.modules-section h4 { margin: 0 0 1rem 0; }
@media (max-width: 768px) {
  .manager-projects .project-list { grid-template-columns: 1fr; }
  .manager-projects .data-table th, .manager-projects .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

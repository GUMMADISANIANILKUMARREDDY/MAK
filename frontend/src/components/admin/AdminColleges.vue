<script setup>
import { ref, onMounted } from 'vue'
import { collegesApi } from '@/services/api'

const colleges = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')
const form = ref({ name: '', code: '' })

async function fetchColleges() {
  loading.value = true
  error.value = ''
  try {
    const res = await collegesApi.list()
    colleges.value = res.colleges || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.name.trim()) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await collegesApi.create({ name: form.value.name.trim(), code: form.value.code.trim() || null })
    form.value = { name: '', code: '' }
    successMsg.value = 'College added'
    fetchColleges()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchColleges())
</script>

<template>
  <div class="section-content">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-4">Colleges</h5>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
        <div class="row g-2 align-items-end mb-4">
          <div class="col-md-4">
            <label class="form-label">College name</label>
            <input v-model="form.name" type="text" class="form-control" placeholder="College name" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Code (optional)</label>
            <input v-model="form.code" type="text" class="form-control" placeholder="Code" />
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-teal" @click="handleCreate" :disabled="loading || !form.name.trim()">Add College</button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">Loading...</div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Name</th>
                <th>Code</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in colleges" :key="c.collegeid">
                <td>{{ c.name }}</td>
                <td><span class="badge bg-secondary" v-if="c.code">{{ c.code }}</span><span v-else class="text-muted">-</span></td>
              </tr>
              <tr v-if="colleges.length === 0">
                <td colspan="2" class="text-center text-muted py-4">No colleges yet</td>
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

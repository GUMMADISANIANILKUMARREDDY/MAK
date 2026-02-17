<script setup>
import { ref, onMounted } from 'vue'
import { collegesApi } from '@/services/api'

const colleges = ref([])
const loading = ref(false)
const error = ref('')
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
  try {
    await collegesApi.create({ name: form.value.name.trim(), code: form.value.code.trim() || null })
    form.value = { name: '', code: '' }
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
  <div class="admin-colleges">
    <h3>Colleges</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div class="form-inline">
      <input v-model="form.name" placeholder="College name" />
      <input v-model="form.code" placeholder="Code (optional)" />
      <button class="btn btn-primary" @click="handleCreate">Add College</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <ul v-else class="list">
      <li v-for="c in colleges" :key="c.collegeid">{{ c.name }} <span v-if="c.code">({{ c.code }})</span></li>
    </ul>
    <p v-if="!loading && colleges.length === 0" class="empty">No colleges yet.</p>
  </div>
</template>

<style scoped>
.form-inline { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.form-inline input { padding: 0.4rem 0.6rem; border-radius: 6px; border: 1px solid var(--color-border); }
.list { list-style: none; padding: 0; }
.list li { padding: 0.4rem 0; border-bottom: 1px solid var(--color-border); }
.empty { color: var(--color-muted); }
</style>

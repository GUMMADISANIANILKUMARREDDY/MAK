<script setup>
import { ref } from 'vue'
import { reportsApi } from '@/services/api'

const error = ref('')
const loading = ref(false)

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function downloadProjectSummaryExcel() {
  loading.value = true
  error.value = ''
  try {
    const res = await reportsApi.projectSummaryExcel()
    downloadBlob(res.data, 'project-summary.xlsx')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Download failed'
  } finally {
    loading.value = false
  }
}

async function downloadProjectSummaryPdf() {
  loading.value = true
  error.value = ''
  try {
    const res = await reportsApi.projectSummaryPdf()
    downloadBlob(res.data, 'project-summary.pdf')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Download failed'
  } finally {
    loading.value = false
  }
}

async function downloadStudentProgressExcel() {
  loading.value = true
  error.value = ''
  try {
    const res = await reportsApi.studentProgressExcel()
    downloadBlob(res.data, 'student-progress.xlsx')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Download failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-reports">
    <h3>Reports</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div class="report-buttons">
      <button class="btn btn-primary" :disabled="loading" @click="downloadProjectSummaryExcel">Project Summary (Excel)</button>
      <button class="btn btn-primary" :disabled="loading" @click="downloadProjectSummaryPdf">Project Summary (PDF)</button>
      <button class="btn btn-primary" :disabled="loading" @click="downloadStudentProgressExcel">Student Progress (Excel)</button>
    </div>
  </div>
</template>

<style scoped>
.report-buttons { display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>

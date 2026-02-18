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
  <div class="section-content">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h5 class="card-title mb-4">Reports</h5>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-teal" :disabled="loading" @click="downloadProjectSummaryExcel">
            <i class="bi bi-file-earmark-excel me-2"></i>Project Summary (Excel)
          </button>
          <button type="button" class="btn btn-teal" :disabled="loading" @click="downloadProjectSummaryPdf">
            <i class="bi bi-file-earmark-pdf me-2"></i>Project Summary (PDF)
          </button>
          <button type="button" class="btn btn-teal" :disabled="loading" @click="downloadStudentProgressExcel">
            <i class="bi bi-file-earmark-excel me-2"></i>Student Progress (Excel)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-teal { background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%); border: none; color: white; font-weight: 600; }
.btn-teal:hover { opacity: 0.95; color: white; }
</style>

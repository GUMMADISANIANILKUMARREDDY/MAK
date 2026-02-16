<script setup>
import { ref, onMounted } from 'vue'
import { studentApi } from '@/services/api'

const tasks = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const filterStatus = ref('')
const filterSearch = ref('')
const filterSort = ref('assigned_at')
const filterOrder = ref('desc')
const selectedTask = ref(null)
const taskDetail = ref(null)
const statusModal = ref(false)
const submitModal = ref(false)
const selectedAssignment = ref(null)
const statusForm = ref({ status: '' })
const submitForm = ref({ notes: '', file: null })

const fetchTasks = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = { sort: filterSort.value, order: filterOrder.value }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterSearch.value) params.search = filterSearch.value
    const res = await studentApi.myTasks(params)
    tasks.value = res.tasks || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load tasks'
  } finally {
    loading.value = false
  }
}

const loadTaskDetail = async (assignment) => {
  selectedAssignment.value = assignment
  taskDetail.value = null
  try {
    const taskid = assignment.taskid || assignment.tasks?.taskid
    if (taskid) {
      const res = await studentApi.getTask(taskid)
      taskDetail.value = res.task
    } else {
      taskDetail.value = assignment.tasks || assignment
    }
  } catch {
    taskDetail.value = assignment.tasks || assignment
  }
}

const openStatusModal = (a) => {
  selectedAssignment.value = a
  statusForm.value = { status: a.status || 'assigned' }
  statusModal.value = true
}

const handleUpdateStatus = async () => {
  if (!selectedAssignment.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentApi.updateStatus(selectedAssignment.value.assignment_id, statusForm.value.status)
    successMsg.value = 'Status updated'
    statusModal.value = false
    fetchTasks()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update status'
  } finally {
    loading.value = false
  }
}

const openSubmitModal = (a) => {
  selectedAssignment.value = a
  submitForm.value = { notes: '', file: null }
  submitModal.value = true
}

const handleSubmit = async () => {
  if (!selectedAssignment.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await studentApi.submit(selectedAssignment.value.assignment_id, submitForm.value.notes, submitForm.value.file || undefined)
    successMsg.value = 'Task submitted for review'
    submitModal.value = false
    fetchTasks()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit'
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchTasks())
</script>

<template>
  <div class="student-tasks">
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div class="filters">
      <input v-model="filterSearch" placeholder="Search task title" @keyup.enter="fetchTasks" />
      <select v-model="filterStatus" @change="fetchTasks">
        <option value="">All Status</option>
        <option value="assigned">Assigned</option>
        <option value="in_progress">In Progress</option>
        <option value="review">Review</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <select v-model="filterSort" @change="fetchTasks">
        <option value="assigned_at">Assigned Date</option>
        <option value="completed_at">Completed</option>
        <option value="status">Status</option>
      </select>
      <select v-model="filterOrder" @change="fetchTasks">
        <option value="desc">Desc</option>
        <option value="asc">Asc</option>
      </select>
      <button class="btn btn-primary" @click="fetchTasks">Search</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="content-block">
      <h3>My Assigned Tasks</h3>
      <div v-if="tasks.length === 0" class="empty">No tasks assigned to you.</div>
      <div v-else class="task-list">
        <div v-for="t in tasks" :key="t.assignment_id || t.taskid || t.id" class="task-card">
          <div class="task-info">
            <h4>{{ t.tasks?.title || t.title || 'Task' }}</h4>
            <p class="desc">{{ (t.tasks?.description || t.description || '').slice(0, 80) }}...</p>
            <div class="meta">
              <span class="badge" :class="t.status">{{ t.status || 'assigned' }}</span>
              <span v-if="t.tasks?.priority || t.priority" class="priority">{{ t.tasks?.priority || t.priority }}</span>
            </div>
            <div v-if="t.review_result || t.status === 'approved' || t.status === 'rejected'" class="review-block">
              <strong>Review:</strong>
              <span :class="{ approved: (t.review_result || t.status) === 'approved', rejected: (t.review_result || t.status) === 'rejected' }">
                {{ t.review_result || t.status }}
              </span>
              <span v-if="t.review_score != null" class="score">Score: {{ t.review_score }}</span>
              <p v-if="t.review_feedback" class="feedback">{{ t.review_feedback }}</p>
            </div>
          </div>
          <div class="task-actions">
            <button class="btn-sm btn-status" @click="openStatusModal(t)">Update Status</button>
            <button class="btn-sm btn-submit" @click="openSubmitModal(t)">Submit</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="statusModal" class="modal-overlay" @click="statusModal = false">
      <div class="modal-content" @click.stop>
        <h3>Update Status</h3>
        <form @submit.prevent="handleUpdateStatus">
          <div class="form-group">
            <label>Status</label>
            <select v-model="statusForm.status" required>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="review">Review</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="statusModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">Update</button>
          </div>
        </form>
      </div>
    </div>
    <div v-if="submitModal" class="modal-overlay" @click="submitModal = false">
      <div class="modal-content" @click.stop>
        <h3>Submit Task</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Notes (optional)</label>
            <textarea v-model="submitForm.notes" rows="3" placeholder="Add any notes for review"></textarea>
          </div>
          <div class="form-group">
            <label>Attachment (optional)</label>
            <input type="file" @change="submitForm.file = $event.target.files?.[0] || null" accept=".pdf,.doc,.docx,.zip,.txt,image/*" />
            <span v-if="submitForm.file" class="file-name">{{ submitForm.file.name }}</span>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="submitModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">Submit for Review</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.student-tasks { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.alert-success { background: #f0fdf4; color: #16a34a; }
.filters { display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; }
.filters select { padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; min-width: 140px; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-secondary { background: #f1f5f9; color: #475569; }
.content-block { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.task-list { display: flex; flex-direction: column; gap: 1rem; }
.task-card { display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem; border: 2px solid #e2e8f0; border-radius: 8px; gap: 1rem; }
.task-card .task-info { flex: 1; }
.task-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; }
.task-card .desc { margin: 0; font-size: 0.85rem; color: #64748b; }
.task-card .meta { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.task-card .badge { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; }
.task-card .badge.assigned { background: #e0f2fe; color: #0ea5e9; }
.task-card .badge.in_progress { background: #fef3c7; color: #d97706; }
.task-card .badge.review { background: #fce7f3; color: #db2777; }
.task-card .badge.approved { background: #ecfdf5; color: #059669; }
.task-card .badge.rejected { background: #fef2f2; color: #dc2626; }
.task-card .priority { font-size: 0.8rem; color: #64748b; }
.task-card .review-block { margin-top: 0.75rem; padding: 0.75rem; background: #f8fafc; border-radius: 6px; font-size: 0.85rem; }
.task-card .review-block .approved { color: #059669; font-weight: 600; }
.task-card .review-block .rejected { color: #dc2626; font-weight: 600; }
.task-card .review-block .score { margin-left: 0.5rem; color: #64748b; }
.task-card .review-block .feedback { margin: 0.5rem 0 0 0; color: #475569; white-space: pre-wrap; }
.task-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }
.btn-status { background: #e0f2fe; color: #0ea5e9; }
.btn-submit { background: #ecfdf5; color: #059669; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group select, .form-group textarea { width: 100%; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.form-group input[type="file"] { width: 100%; font-size: 0.9rem; }
.file-name { font-size: 0.85rem; color: #64748b; margin-top: 0.25rem; display: block; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 12px; padding: 2rem; max-width: 420px; width: 100%; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.loading, .empty { padding: 2rem; text-align: center; color: #64748b; }

@media (max-width: 768px) {
  .student-tasks .task-card { flex-direction: column; align-items: stretch; }
  .student-tasks .task-actions { flex-wrap: wrap; }
  .student-tasks .filters { flex-direction: column; }
  .student-tasks .filters select { min-width: 100%; }
}
</style>

<script setup>
import { ref, onMounted } from 'vue'
import { mentorApi } from '../../services/api'

const modules = ref([])
const selectedModule = ref(null)
const tasks = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const subTab = ref('list')
const addForm = ref({ title: '', description: '', task_type: 'task', priority: 'medium', story_points: 0, due_date: '' })
const editModal = ref(false)
const assignModal = ref(false)
const editTask = ref(null)
const assignTask = ref(null)
const editForm = ref({ title: '', description: '', task_type: '', priority: '', status: '', due_date: '' })
const assignForm = ref({ student_userid: '' })
const bulkAssignForm = ref({ student_userids: '' })
const assignments = ref([])

const fetchModules = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await mentorApi.myModules()
    modules.value = res.modules || []
    if (modules.value.length && !selectedModule.value) {
      selectedModule.value = modules.value[0]
      await loadTasks(modules.value[0])
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load modules'
  } finally {
    loading.value = false
  }
}

const loadTasks = async (mod) => {
  selectedModule.value = mod
  error.value = ''
  try {
    const res = await mentorApi.getModuleTasks(mod.moduleid)
    tasks.value = res.tasks || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load tasks'
  }
}

onMounted(() => fetchModules())

const handleCreate = async () => {
  if (!selectedModule.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...addForm.value }
    if (!data.due_date) delete data.due_date
    await mentorApi.createTask(selectedModule.value.moduleid, data)
    successMsg.value = 'Task created'
    addForm.value = { title: '', description: '', task_type: 'task', priority: 'medium', story_points: 0, due_date: '' }
    loadTasks(selectedModule.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create task'
  } finally {
    loading.value = false
  }
}

const openEdit = (t) => {
  editTask.value = t
  editForm.value = {
    title: t.title,
    description: t.description || '',
    task_type: t.task_type || 'task',
    priority: t.priority || 'medium',
    status: t.status || '',
    due_date: t.due_date ? t.due_date.slice(0, 10) : '',
  }
  editModal.value = true
}

const handleUpdate = async () => {
  if (!editTask.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    const data = { ...editForm.value }
    if (!data.due_date) delete data.due_date
    if (!data.status) delete data.status
    await mentorApi.updateTask(editTask.value.taskid, data)
    successMsg.value = 'Task updated'
    editModal.value = false
    loadTasks(selectedModule.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update task'
  } finally {
    loading.value = false
  }
}

const openAssign = (t) => {
  assignTask.value = t
  assignForm.value = { student_userid: '' }
  bulkAssignForm.value = { student_userids: '' }
  assignModal.value = true
  loadAssignments(t)
}

const loadAssignments = async (t) => {
  try {
    const res = await mentorApi.getTaskAssignments(t.taskid)
    assignments.value = res.assignments || []
  } catch {
    assignments.value = []
  }
}

const handleAssignStudent = async () => {
  if (!assignTask.value || !assignForm.value.student_userid.trim()) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.assignStudent(assignTask.value.taskid, assignForm.value.student_userid.trim())
    successMsg.value = 'Student assigned'
    assignForm.value = { student_userid: '' }
    loadAssignments(assignTask.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to assign student'
  } finally {
    loading.value = false
  }
}

const handleBulkAssign = async () => {
  if (!assignTask.value) return
  const ids = bulkAssignForm.value.student_userids.split(/[\s,]+/).filter(Boolean)
  if (!ids.length) {
    error.value = 'Enter student user IDs'
    return
  }
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.bulkAssign(assignTask.value.taskid, ids)
    successMsg.value = `Assigned to ${ids.length} student(s)`
    bulkAssignForm.value = { student_userids: '' }
    loadAssignments(assignTask.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to assign'
  } finally {
    loading.value = false
  }
}

const handleDelete = async (taskid) => {
  if (!confirm('Delete this task?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.deleteTask(taskid)
    successMsg.value = 'Task deleted'
    loadTasks(selectedModule.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete task'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mentor-tasks">
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="loading && modules.length === 0" class="loading">Loading...</div>
    <template v-else-if="modules.length">
      <div class="module-select">
        <label>Module:</label>
        <select :value="selectedModule?.moduleid" @change="e => loadTasks(modules.find(m => m.moduleid === e.target.value) || selectedModule)">
          <option v-for="m in modules" :key="m.moduleid" :value="m.moduleid">{{ m.title }}</option>
        </select>
      </div>
      <div class="tabs">
        <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">Tasks</button>
        <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Create Task</button>
      </div>
      <div v-show="subTab === 'list'" class="content-block">
        <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Due Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in tasks" :key="t.taskid">
              <td>{{ t.title }}</td>
              <td>{{ t.task_type || 'task' }}</td>
              <td>{{ t.priority || '-' }}</td>
              <td>{{ t.status || '-' }}</td>
              <td>{{ t.due_date ? t.due_date.slice(0, 10) : '-' }}</td>
              <td>
                <button class="btn-sm btn-edit" @click="openEdit(t)">Edit</button>
                <button class="btn-sm btn-assign" @click="openAssign(t)">Assign</button>
                <button class="btn-sm btn-delete" @click="handleDelete(t.taskid)">Delete</button>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="6" class="empty">No tasks. Create one.</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
      <div v-show="subTab === 'add'" class="content-block">
        <form @submit.prevent="handleCreate" class="form-add">
          <div class="form-group">
            <label>Title *</label>
            <input v-model="addForm.title" required placeholder="Task title" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="addForm.description" rows="2"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Type</label>
              <select v-model="addForm.task_type">
                <option value="task">Task</option>
                <option value="bug">Bug</option>
                <option value="story">Story</option>
              </select>
            </div>
            <div class="form-group">
              <label>Priority</label>
              <select v-model="addForm.priority">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Due Date</label>
            <input v-model="addForm.due_date" type="date" />
          </div>
          <button type="submit" class="btn btn-primary" :disabled="loading">Create Task</button>
        </form>
      </div>
      <div v-if="editModal" class="modal-overlay" @click="editModal = false">
        <div class="modal-content" @click.stop>
          <h3>Edit Task</h3>
          <form @submit.prevent="handleUpdate">
            <div class="form-group">
              <label>Title</label>
              <input v-model="editForm.title" required />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="2"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Priority</label>
                <select v-model="editForm.priority">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div class="form-group">
                <label>Status</label>
                <select v-model="editForm.status">
                  <option value="">--</option>
                  <option value="backlog">Backlog</option>
                  <option value="assigned">Assigned</option>
                  <option value="in_progress">In Progress</option>
                  <option value="review">Review</option>
                  <option value="done">Done</option>
                </select>
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="editModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">Save</button>
            </div>
          </form>
        </div>
      </div>
      <div v-if="assignModal" class="modal-overlay" @click="assignModal = false">
        <div class="modal-content modal-wide" @click.stop>
          <h3>Assign Students</h3>
          <p class="muted">{{ assignTask?.title }}</p>
          <div class="assign-section">
            <h4>Assign Single</h4>
            <form @submit.prevent="handleAssignStudent" class="inline-form">
              <input v-model="assignForm.student_userid" placeholder="Student User ID" />
              <button type="submit" class="btn btn-primary" :disabled="loading">Add</button>
            </form>
          </div>
          <div class="assign-section">
            <h4>Bulk Assign</h4>
            <form @submit.prevent="handleBulkAssign" class="inline-form">
              <input v-model="bulkAssignForm.student_userids" placeholder="S001, S002, S003" style="flex:1" />
              <button type="submit" class="btn btn-secondary" :disabled="loading">Assign All</button>
            </form>
          </div>
          <div v-if="assignments.length" class="assign-section">
            <h4>Assigned</h4>
            <ul class="assigned-list">
              <li v-for="a in assignments" :key="a.assignment_id">{{ a.student_userid }} ({{ a.status }})</li>
            </ul>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="assignModal = false">Close</button>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty">No modules assigned. Tasks are created within modules.</div>
  </div>
</template>

<style scoped>
.mentor-tasks { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.alert-success { background: #f0fdf4; color: #16a34a; }
.module-select { margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.module-select select { padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; min-width: 200px; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tabs button { padding: 0.5rem 1rem; border: 2px solid #e2e8f0; background: white; border-radius: 8px; font-weight: 600; cursor: pointer; }
.tabs button.active { background: #0ea5e9; border-color: #0ea5e9; color: white; }
.content-block { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
.data-table th { font-weight: 600; background: #f8fafc; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; margin-right: 0.5rem; }
.btn-edit { background: #e0f2fe; color: #0ea5e9; }
.btn-assign { background: #ecfdf5; color: #059669; }
.btn-delete { background: #fef2f2; color: #dc2626; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-secondary { background: #f1f5f9; color: #475569; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 12px; padding: 2rem; max-width: 480px; width: 100%; }
.modal-wide { max-width: 560px; }
.assign-section { margin-bottom: 1rem; }
.assign-section h4 { margin: 0 0 0.5rem 0; font-size: 0.9rem; }
.inline-form { display: flex; gap: 0.5rem; align-items: center; }
.inline-form input { flex: 1; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.assigned-list { margin: 0; padding-left: 1.5rem; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.muted { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.loading, .empty { padding: 2rem; text-align: center; color: #64748b; }

.mentor-tasks .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.mentor-tasks .data-table { min-width: 520px; }
@media (max-width: 768px) {
  .mentor-tasks .module-select select { min-width: 100%; }
  .mentor-tasks .form-row { grid-template-columns: 1fr; }
  .mentor-tasks .inline-form { flex-direction: column; }
  .mentor-tasks .data-table th, .mentor-tasks .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

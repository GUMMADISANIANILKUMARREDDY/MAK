<script setup>
import { ref, onMounted } from 'vue'
import { mentorApi } from '../../services/api'

const teams = ref([])
const loading = ref(false)
const error = ref('')
const successMsg = ref('')

const subTab = ref('list')
const addForm = ref({ team_name: '' })
const selectedTeam = ref(null)
const members = ref([])
const addMemberForm = ref({ student_userid: '' })
const addMemberModal = ref(false)

const fetchTeams = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await mentorApi.getTeams()
    teams.value = res.teams || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load teams'
  } finally {
    loading.value = false
  }
}

const loadMembers = async (team) => {
  selectedTeam.value = team
  members.value = []
  try {
    const res = await mentorApi.getTeamMembers(team.teamid)
    members.value = res.members || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load members'
  }
}

onMounted(() => fetchTeams())

const handleCreate = async () => {
  if (!addForm.value.team_name.trim()) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.createTeam(addForm.value.team_name.trim())
    successMsg.value = 'Team created'
    addForm.value = { team_name: '' }
    fetchTeams()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create team'
  } finally {
    loading.value = false
  }
}

const openAddMember = (team) => {
  selectedTeam.value = team
  addMemberForm.value = { student_userid: '' }
  addMemberModal.value = true
}

const handleAddMember = async () => {
  if (!selectedTeam.value || !addMemberForm.value.student_userid.trim()) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.addStudentToTeam(selectedTeam.value.teamid, addMemberForm.value.student_userid.trim())
    successMsg.value = 'Student added'
    addMemberModal.value = false
    loadMembers(selectedTeam.value)
    fetchTeams()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add student'
  } finally {
    loading.value = false
  }
}

const handleRemoveMember = async (teamid, student_userid) => {
  if (!confirm('Remove this student from team?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.removeStudentFromTeam(teamid, student_userid)
    successMsg.value = 'Student removed'
    if (selectedTeam.value?.teamid === teamid) loadMembers(selectedTeam.value)
    fetchTeams()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to remove student'
  } finally {
    loading.value = false
  }
}

const handleDeleteTeam = async (teamid) => {
  if (!confirm('Delete this team?')) return
  loading.value = true
  error.value = ''
  successMsg.value = ''
  try {
    await mentorApi.deleteTeam(teamid)
    successMsg.value = 'Team deleted'
    selectedTeam.value = null
    members.value = []
    fetchTeams()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete team'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mentor-teams">
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div class="tabs">
      <button :class="{ active: subTab === 'list' }" @click="subTab = 'list'">Teams</button>
      <button :class="{ active: subTab === 'add' }" @click="subTab = 'add'">Create Team</button>
    </div>
    <div v-show="subTab === 'list'" class="content-block">
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else>
        <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Team Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in teams" :key="t.teamid">
              <td>{{ t.team_name }}</td>
              <td>
                <button class="btn-sm btn-view" @click="loadMembers(t)">View Members</button>
                <button class="btn-sm btn-add" @click="openAddMember(t)">Add Student</button>
                <button class="btn-sm btn-delete" @click="handleDeleteTeam(t.teamid)">Delete</button>
              </td>
            </tr>
            <tr v-if="teams.length === 0">
              <td colspan="2" class="empty">No teams. Create one.</td>
            </tr>
          </tbody>
        </table>
        </div>
        <div v-if="selectedTeam" class="members-section">
          <h4>Members: {{ selectedTeam.team_name }}</h4>
          <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Name</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.student_userid">
                <td>{{ m.student_userid }}</td>
                <td>{{ m.username || '-' }}</td>
                <td>
                  <button class="btn-sm btn-delete" @click="handleRemoveMember(selectedTeam.teamid, m.student_userid)">Remove</button>
                </td>
              </tr>
              <tr v-if="members.length === 0">
                <td colspan="3" class="empty">No members</td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </div>
    <div v-show="subTab === 'add'" class="content-block">
      <form @submit.prevent="handleCreate" class="form-add">
        <div class="form-group">
          <label>Team Name *</label>
          <input v-model="addForm.team_name" required placeholder="e.g. Team Alpha" />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Create Team</button>
      </form>
    </div>
    <div v-if="addMemberModal" class="modal-overlay" @click="addMemberModal = false">
      <div class="modal-content" @click.stop>
        <h3>Add Student to Team</h3>
        <p class="muted">{{ selectedTeam?.team_name }}</p>
        <form @submit.prevent="handleAddMember">
          <div class="form-group">
            <label>Student User ID *</label>
            <input v-model="addMemberForm.student_userid" required placeholder="e.g. S001" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="addMemberModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">Add</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mentor-teams { width: 100%; }
.alert { padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; }
.alert-error { background: #fef2f2; color: #dc2626; }
.alert-success { background: #f0fdf4; color: #16a34a; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.tabs button { padding: 0.5rem 1rem; border: 2px solid #e2e8f0; background: white; border-radius: 8px; font-weight: 600; cursor: pointer; }
.tabs button.active { background: #0ea5e9; border-color: #0ea5e9; color: white; }
.content-block { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
.data-table th { font-weight: 600; background: #f8fafc; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; margin-right: 0.5rem; }
.btn-view { background: #e0f2fe; color: #0ea5e9; }
.btn-add { background: #ecfdf5; color: #059669; }
.btn-delete { background: #fef2f2; color: #dc2626; }
.members-section { margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; }
.members-section h4 { margin: 0 0 1rem 0; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
.form-group input { width: 100%; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 8px; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; }
.btn-primary { background: #0ea5e9; color: white; }
.btn-secondary { background: #f1f5f9; color: #475569; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 12px; padding: 2rem; max-width: 400px; width: 100%; }
.modal-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
.muted { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.loading, .empty { padding: 2rem; text-align: center; color: #64748b; }

.mentor-teams .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.mentor-teams .data-table { min-width: 400px; }
@media (max-width: 768px) {
  .mentor-teams .data-table th, .mentor-teams .data-table td { padding: 0.5rem; font-size: 0.85rem; }
}
</style>

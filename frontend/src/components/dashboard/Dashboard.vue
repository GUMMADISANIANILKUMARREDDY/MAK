<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminUsers from '../admin/AdminUsers.vue'
import AdminStudents from '../admin/AdminStudents.vue'
import AdminProjects from '../admin/AdminProjects.vue'
import ManagerMyProjects from '../manager/ManagerMyProjects.vue'
import ManagerModules from '../manager/ManagerModules.vue'
import MentorMyModules from '../mentor/MentorMyModules.vue'
import MentorTeams from '../mentor/MentorTeams.vue'
import MentorTasks from '../mentor/MentorTasks.vue'
import StudentMyTasks from '../student/StudentMyTasks.vue'
import makLogo from '@/assets/mak-only.svg'

const router = useRouter()
const user = ref(null)
const loading = ref(true)
const activeSection = ref('overview')

onMounted(() => {
  const stored = localStorage.getItem('user')
  const token = localStorage.getItem('access_token')

  if (!token || !stored) {
    router.push('/home')
    return
  }

  try {
    user.value = JSON.parse(stored)
  } catch {
    router.push('/home')
  } finally {
    loading.value = false
  }
})

const username = computed(() => user.value?.username || user.value?.email || 'User')
const role = computed(() => user.value?.role || 'student')
const roleLabel = computed(() => {
  const r = role.value
  const labels = { admin: 'Admin', manager: 'Manager', mentor: 'Mentor', student: 'Student', clgadmin: 'College Admin' }
  return labels[r] || r
})

// Role-based sidebar menu items
const menuItems = computed(() => {
  const allItems = [
    { id: 'overview', label: 'Overview', icon: '◆', roles: ['admin', 'manager', 'mentor', 'student', 'clgadmin'] },
    { id: 'projects', label: 'Projects', icon: '◇', roles: ['admin'] },
    { id: 'users', label: 'Users', icon: '◆', roles: ['admin', 'clgadmin'] },
    { id: 'students', label: 'Students', icon: '●', roles: ['admin', 'clgadmin'] },
    { id: 'my-projects', label: 'My Projects', icon: '◇', roles: ['manager'] },
    { id: 'modules', label: 'Modules', icon: '■', roles: ['manager'] },
    { id: 'my-modules', label: 'My Modules', icon: '■', roles: ['mentor'] },
    { id: 'teams', label: 'Teams', icon: '◆', roles: ['mentor'] },
    { id: 'tasks', label: 'Tasks', icon: '●', roles: ['mentor'] },
    { id: 'my-tasks', label: 'My Tasks', icon: '●', roles: ['student'] },
  ]
  return allItems.filter(item => item.roles.includes(role.value))
})

const sidebarOpen = ref(false)

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  router.push('/home')
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}
</script>

<template>
  <div class="dashboard">
    <button class="sidebar-toggle" aria-label="Toggle menu" @click="toggleSidebar">
      <span></span><span></span><span></span>
    </button>
    <div class="sidebar-overlay" :class="{ open: sidebarOpen }" @click="closeSidebar"></div>
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <a href="/home" class="logo">
          <img class="logo-img" :src="makLogo" alt="MAK" />
        </a>
        <span class="role-badge">{{ roleLabel }}</span>
      </div>

      <nav class="sidebar-nav">
        <a
          v-for="item in menuItems"
          :key="item.id"
          href="#"
          class="nav-item"
          :class="{ active: activeSection === item.id }"
          @click.prevent="activeSection = item.id; closeSidebar()"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-name">{{ username }}</span>
        </div>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </aside>

    <div class="dashboard-body">
      <header class="top-bar">
        <h2>{{ menuItems.find(m => m.id === activeSection)?.label || 'Overview' }}</h2>
      </header>

      <main class="dashboard-main">
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else class="dashboard-content scroll-area">
          <div v-if="activeSection === 'overview'" class="content-block">
            <h1>Welcome, {{ username }}!</h1>
            <p class="subtitle">You are logged in as <strong>{{ roleLabel }}</strong></p>
            <div class="welcome-card">
              <p>This is your dashboard. Use the sidebar to access role-specific features.</p>
            </div>
          </div>

          <AdminProjects v-else-if="activeSection === 'projects'" />

          <AdminUsers v-else-if="activeSection === 'users'" />

          <AdminStudents v-else-if="activeSection === 'students'" />

          <ManagerMyProjects v-else-if="activeSection === 'my-projects'" />

          <ManagerModules v-else-if="activeSection === 'modules'" />

          <MentorMyModules v-else-if="activeSection === 'my-modules'" />

          <MentorTeams v-else-if="activeSection === 'teams'" />

          <MentorTasks v-else-if="activeSection === 'tasks'" />

          <StudentMyTasks v-else-if="activeSection === 'my-tasks'" />

          <div v-else class="content-block">
            <h2>{{ activeSection }}</h2>
            <p>Content coming soon.</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  min-height: 100vh;
  background: var(--color-background);
  position: relative;
}

.sidebar-toggle {
  display: none;
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 200;
  width: 44px;
  height: 44px;
  padding: 8px;
  background: var(--color-surface);
  border: 2px solid color-mix(in srgb, var(--color-border) 90%, transparent);
  border-radius: 8px;
  cursor: pointer;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.sidebar-toggle span {
  display: block;
  width: 20px;
  height: 2px;
  background: color-mix(in srgb, var(--color-muted) 90%, transparent);
  border-radius: 1px;
}
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 150;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
}
.sidebar-overlay.open {
  opacity: 1;
  visibility: visible;
}

.sidebar {
  width: 260px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 160;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent);
}

.logo {
  font-size: 1.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-decoration: none;
  display: block;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-img {
  width: 108px;
  height: 48px;
  display: block;
}
.role-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: color-mix(in srgb, var(--color-sun) 85%, var(--color-surface));
  color: var(--color-primary-strong);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid color-mix(in srgb, var(--color-sun-strong) 35%, transparent);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--color-muted);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface));
  color: var(--color-primary);
}

.nav-item.active {
  background: color-mix(in srgb, var(--color-primary) 10%, var(--color-surface));
  color: var(--color-primary-strong);
  border-left-color: var(--color-primary);
}

.nav-icon {
  font-size: 1rem;
  opacity: 0.9;
}

.nav-label {
  font-size: 0.95rem;
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent);
}

.user-name {
  font-size: 0.85rem;
  color: var(--color-muted);
  display: block;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  width: 100%;
  padding: 0.5rem 1rem;
  background: color-mix(in srgb, var(--color-surface-2) 70%, var(--color-surface));
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  color: var(--color-muted);
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fef2f2;
  color: #dc2626;
}

.dashboard-body {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 0;
  width: 100%;
}

.top-bar {
  background: var(--color-surface);
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.top-bar h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-heading);
  margin: 0;
}

.dashboard-main {
  flex: 1;
  padding: 1rem;
  overflow-x: auto;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.dashboard-content.scroll-area {
  width: 100%;
  min-width: 0;
  max-width: 100%;
}

.dashboard-content.scroll-area > * {
  max-width: 100%;
  min-width: 0;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: var(--color-muted);
}

.dashboard-content h1,
.dashboard-content h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--color-muted);
  margin-bottom: 1.5rem;
}

.content-block {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  border: 1px solid color-mix(in srgb, var(--color-border) 55%, transparent);
}

.welcome-card {
  margin-top: 1rem;
}

.welcome-card p,
.content-block p {
  color: var(--color-muted);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .sidebar-toggle {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
  }

  .sidebar {
    width: 280px;
    transform: translateX(-100%);
    box-shadow: none;
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
  }

  .sidebar .nav-label,
  .sidebar .logo,
  .sidebar .role-badge,
  .sidebar .user-name {
    display: block;
  }

  .sidebar .logo {
    font-size: 1.1rem;
    text-align: left;
  }

  .dashboard-body {
    margin-left: 0;
    padding-top: 60px;
  }

  .top-bar {
    padding: 0.75rem 1rem 0.75rem 4rem;
  }

  .top-bar h2 {
    font-size: 1rem;
  }

  .dashboard-main {
    padding: 1rem;
  }

  .content-block {
    padding: 1rem;
  }

  .dashboard-content h1,
  .dashboard-content h2 {
    font-size: 1.25rem;
  }
}

@media (min-width: 480px) and (max-width: 768px) {
  .dashboard-main {
    padding: 1.25rem;
  }
}

@media (min-width: 769px) {
  .sidebar-overlay.open {
    display: none;
  }
}
</style>

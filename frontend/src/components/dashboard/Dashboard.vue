<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import AdminUsers from '../admin/AdminUsers.vue'
import AdminStudents from '../admin/AdminStudents.vue'
import AdminProjects from '../admin/AdminProjects.vue'
import AdminActivityLogs from '../admin/AdminActivityLogs.vue'
import AdminColleges from '../admin/AdminColleges.vue'
import AdminPermissions from '../admin/AdminPermissions.vue'
import AdminReports from '../admin/AdminReports.vue'
import ChatView from '../chat/ChatView.vue'
import ManagerMyProjects from '../manager/ManagerMyProjects.vue'
import ManagerModules from '../manager/ManagerModules.vue'
import MentorMyModules from '../mentor/MentorMyModules.vue'
import MentorTeams from '../mentor/MentorTeams.vue'
import MentorTasks from '../mentor/MentorTasks.vue'
import StudentMyTasks from '../student/StudentMyTasks.vue'
import AdminOverview from './overview/AdminOverview.vue'
import ManagerOverview from './overview/ManagerOverview.vue'
import MentorOverview from './overview/MentorOverview.vue'
import StudentOverview from './overview/StudentOverview.vue'
import CollegeAdminOverview from './overview/CollegeAdminOverview.vue'
import NotificationBell from './NotificationBell.vue'

const router = useRouter()
const user = ref(null)
const loading = ref(true)
const activeSection = ref('overview')
const sidebarCollapsed = ref(false)
const sidebarOpen = ref(false)
const userDropdownOpen = ref(false)
const searchQuery = ref('')

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/home')
    return
  }
  const stored = localStorage.getItem('user')
  if (stored) {
    try {
      user.value = JSON.parse(stored)
      if (user.value && (user.value.userid || user.value.role)) {
        loading.value = false
        return
      }
    } catch (_) {}
  }
  try {
    const me = await authService.getMe()
    if (me && (me.userid || me.role)) {
      user.value = me
      localStorage.setItem('user', JSON.stringify(me))
    } else {
      router.push('/home')
      return
    }
  } catch (_) {
    router.push('/home')
    return
  } finally {
    loading.value = false
  }
})

const username = computed(() => user.value?.username || user.value?.email || user.value?.userid || 'User')
const role = computed(() => user.value?.role || 'student')
const roleLabel = computed(() => {
  const r = role.value
  const labels = { admin: 'Admin', manager: 'Manager', mentor: 'Mentor', student: 'Student', clgadmin: 'College Admin' }
  return labels[r] || r
})

const menuItems = computed(() => {
  const allItems = [
    { id: 'overview', label: 'Overview', icon: 'bi-layout-dashboard', roles: ['admin', 'manager', 'mentor', 'student', 'clgadmin'] },
    { id: 'projects', label: 'Projects', icon: 'bi-folder2-open', roles: ['admin'] },
    { id: 'users', label: 'Users', icon: 'bi-people', roles: ['admin', 'clgadmin'] },
    { id: 'students', label: 'Students', icon: 'bi-mortarboard', roles: ['admin', 'clgadmin'] },
    { id: 'activity-logs', label: 'Activity Logs', icon: 'bi-graph-up', roles: ['admin'] },
    { id: 'colleges', label: 'Colleges', icon: 'bi-building', roles: ['admin'] },
    { id: 'permissions', label: 'Permissions', icon: 'bi-shield-lock', roles: ['admin'] },
    { id: 'reports', label: 'Reports', icon: 'bi-bar-chart', roles: ['admin'] },
    { id: 'my-projects', label: 'My Projects', icon: 'bi-folder2', roles: ['manager'] },
    { id: 'modules', label: 'Modules', icon: 'bi-grid-3x3-gap', roles: ['manager'] },
    { id: 'my-modules', label: 'My Modules', icon: 'bi-grid-3x3-gap', roles: ['mentor'] },
    { id: 'teams', label: 'Teams', icon: 'bi-people', roles: ['mentor'] },
    { id: 'tasks', label: 'Tasks', icon: 'bi-list-check', roles: ['mentor'] },
    { id: 'chat', label: 'Chat', icon: 'bi-chat-dots', roles: ['mentor', 'student'] },
    { id: 'my-tasks', label: 'My Tasks', icon: 'bi-list-check', roles: ['student'] },
  ]
  return allItems.filter(item => item.roles.includes(role.value))
})

const OverviewComponent = computed(() => {
  const r = role.value
  if (r === 'admin') return AdminOverview
  if (r === 'manager') return ManagerOverview
  if (r === 'mentor') return MentorOverview
  if (r === 'student') return StudentOverview
  if (r === 'clgadmin') return CollegeAdminOverview
  return StudentOverview
})

const handleLogout = () => {
  userDropdownOpen.value = false
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.push('/home')
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const toggleSidebarCollapse = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

function toggleUserDropdown() {
  userDropdownOpen.value = !userDropdownOpen.value
}

function closeUserDropdown() {
  userDropdownOpen.value = false
}

const userDropdownRef = ref(null)
function onDocClick(e) {
  if (userDropdownRef.value && !userDropdownRef.value.contains(e.target)) {
    closeUserDropdown()
  }
}
onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))
</script>

<template>
  <div class="dashboard">
    <!-- Sidebar overlay for mobile -->
    <div class="sidebar-overlay" :class="{ show: sidebarOpen }" @click="closeSidebar"></div>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-open': sidebarOpen }">
      <div class="sidebar-header">
        <a href="/home" class="sidebar-logo" aria-label="MAK Home">
          <img src="/mak-only.svg" alt="MAK" class="sidebar-logo-img" />
          <span class="sidebar-logo-text">Technologies</span>
        </a>
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
          <i :class="['bi', item.icon, 'nav-icon']"></i>
          <span class="nav-label">{{ item.label }}</span>
        </a>
      </nav>
      <button class="sidebar-collapse-btn" @click="toggleSidebarCollapse" :title="sidebarCollapsed ? 'Expand' : 'Collapse'">
        <i :class="['bi', sidebarCollapsed ? 'bi-chevron-right' : 'bi-chevron-left']"></i>
      </button>
    </aside>

    <!-- Main content wrapper -->
    <div class="main-wrapper" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Top bar -->
      <header class="top-bar">
        <button class="sidebar-toggle d-lg-none" aria-label="Toggle menu" @click="toggleSidebar">
          <i class="bi bi-list"></i>
        </button>
        <div class="top-bar-actions">
          <div class="search-wrap">
            <i class="bi bi-search"></i>
            <input v-model="searchQuery" type="text" class="form-control" placeholder="Search..." />
          </div>
          <NotificationBell />
          <div class="user-dropdown" :class="{ open: userDropdownOpen }" ref="userDropdownRef">
            <button
              type="button"
              class="user-dropdown-trigger"
              @click="toggleUserDropdown"
            >
              <span class="user-avatar">{{ (username || 'U').charAt(0).toUpperCase() }}</span>
              <span class="user-name">{{ username }}</span>
              <i class="bi bi-chevron-down"></i>
            </button>
            <Transition name="dropdown">
              <div v-show="userDropdownOpen" class="user-dropdown-menu">
                <div class="user-dropdown-head">
                  <span class="fw-semibold">{{ username }}</span>
                  <small class="text-muted">{{ roleLabel }}</small>
                </div>
                <button type="button" class="user-dropdown-item text-danger" @click="handleLogout">
                  Log out
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="dashboard-main">
        <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>
        <div v-else class="dashboard-content">
          <component
            v-if="activeSection === 'overview'"
            :is="OverviewComponent"
            :username="username"
          />
          <AdminProjects v-else-if="activeSection === 'projects'" />
          <AdminUsers v-else-if="activeSection === 'users'" />
          <AdminStudents v-else-if="activeSection === 'students'" />
          <AdminActivityLogs v-else-if="activeSection === 'activity-logs'" />
          <AdminColleges v-else-if="activeSection === 'colleges'" />
          <AdminPermissions v-else-if="activeSection === 'permissions'" />
          <AdminReports v-else-if="activeSection === 'reports'" />
          <ManagerMyProjects v-else-if="activeSection === 'my-projects'" />
          <ManagerModules v-else-if="activeSection === 'modules'" />
          <MentorMyModules v-else-if="activeSection === 'my-modules'" />
          <MentorTeams v-else-if="activeSection === 'teams'" />
          <MentorTasks v-else-if="activeSection === 'tasks'" />
          <StudentMyTasks v-else-if="activeSection === 'my-tasks'" />
          <ChatView v-else-if="activeSection === 'chat'" />
          <div v-else class="card">
            <div class="card-body">
              <h5>{{ activeSection }}</h5>
              <p class="text-muted mb-0">Content coming soon.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 72px;
  --top-bar-height: 64px;
  --sidebar-dark: #1F2B3E;
  --sidebar-hover: rgba(255, 255, 255, 0.08);
  --active-teal: #20BFB6;
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1040;
  opacity: 0;
  transition: opacity 0.25s;
}
.sidebar-overlay.show {
  opacity: 1;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--sidebar-dark);
  z-index: 1050;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease, transform 0.3s ease;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}
.sidebar.collapsed .sidebar-header {
  padding: 0.75rem;
  justify-content: center;
  align-items: center;
}
.sidebar.collapsed .sidebar-logo {
  flex-direction: column;
  align-items: center;
}
.sidebar.collapsed .sidebar-logo-img {
  width: 40px;
  height: auto;
}
.sidebar.collapsed .sidebar-logo-text {
  display: none;
}
.sidebar.collapsed .nav-label {
  opacity: 0;
  width: 0;
  overflow: hidden;
  white-space: nowrap;
  padding: 0;
  margin: 0;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar.collapsed .nav-icon {
  margin: 0;
}

.sidebar-header {
  padding: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}
.sidebar-logo {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  text-decoration: none;
  color: inherit;
}
.sidebar-logo-img {
  height: 36px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
  transition: width 0.2s;
}
.sidebar-logo-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  transition: opacity 0.2s;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0.5rem;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin: 0.25rem 0;
  color: rgba(226, 232, 240, 0.9);
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: white;
}

.nav-item.active {
  background: var(--active-teal);
  color: white;
}

.nav-icon {
  font-size: 1.2rem;
  min-width: 1.5rem;
  text-align: center;
}

.nav-label {
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  transition: opacity 0.2s, width 0.2s;
}

.sidebar-collapse-btn {
  padding: 0.75rem;
  margin: 0.5rem;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 8px;
  color: rgba(226, 232, 240, 0.8);
  cursor: pointer;
  transition: background 0.2s;
}
.sidebar-collapse-btn:hover {
  background: var(--sidebar-hover);
  color: white;
}

.main-wrapper {
  flex: 1;
  margin-left: var(--sidebar-width);
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}
.main-wrapper.sidebar-collapsed {
  margin-left: var(--sidebar-collapsed-width);
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: var(--top-bar-height);
  padding: 0 1.5rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1030;
}

.sidebar-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--sidebar-dark);
  color: white;
  border-radius: 10px;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.top-bar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-wrap {
  display: flex;
  align-items: center;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 0.5rem 1rem;
  min-width: 220px;
}
.search-wrap i {
  color: #64748b;
  margin-right: 0.5rem;
}
.search-wrap input {
  border: none !important;
  background: transparent !important;
  padding: 0.25rem 0 !important;
  font-size: 0.95rem;
}

.user-dropdown {
  position: relative;
}

.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 9999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  color: #0f172a;
  transition: all 0.2s;
}

.user-dropdown-trigger:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00AACC 0%, #00BF80 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  padding: 0.5rem 0;
  z-index: 1100;
}

.user-dropdown-head {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.user-dropdown-item {
  display: block;
  width: 100%;
  padding: 0.65rem 1rem;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}
.user-dropdown-item:hover {
  background: #fef2f2;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.dashboard-main {
  flex: 1;
  padding: 1.5rem;
  overflow-x: auto;
}

.dashboard-content {
  max-width: 100%;
}

@media (max-width: 991.98px) {
  .sidebar-overlay {
    display: block;
    pointer-events: none;
  }
  .sidebar-overlay.show {
    pointer-events: auto;
  }

  .sidebar {
    transform: translateX(-100%);
    box-shadow: none;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: 6px 0 24px rgba(0, 0, 0, 0.25);
  }
  .sidebar.collapsed {
    width: var(--sidebar-width);
  }
  .sidebar.mobile-open.collapsed .nav-label {
    opacity: 1;
    width: auto;
  }
  .sidebar.mobile-open.collapsed .sidebar-logo-text {
    display: block;
  }
  .sidebar.mobile-open.collapsed .sidebar-logo {
    flex-direction: column;
    align-items: flex-start;
  }
  .sidebar.mobile-open.collapsed .sidebar-header {
    justify-content: flex-start;
    align-items: flex-start;
  }

  .main-wrapper {
    margin-left: 0 !important;
  }
  .main-wrapper.sidebar-collapsed {
    margin-left: 0 !important;
  }

  .search-wrap {
    min-width: 160px;
  }
}

@media (max-width: 575.98px) {
  .top-bar {
    padding: 0 1rem;
  }
  .search-wrap {
    display: none;
  }
  .user-name {
    display: none;
  }
}
</style>

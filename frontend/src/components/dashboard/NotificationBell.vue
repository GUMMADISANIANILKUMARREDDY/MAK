<script setup>
import { ref, onMounted } from 'vue'
import { notificationsApi } from '@/services/api'

const open = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(false)

async function fetchCount() {
  try {
    const res = await notificationsApi.unreadCount()
    unreadCount.value = res?.count ?? 0
  } catch {
    unreadCount.value = 0
  }
}

async function fetchList() {
  loading.value = true
  try {
    const res = await notificationsApi.list({ limit: 20 })
    notifications.value = res?.notifications ?? []
  } catch {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

async function toggle() {
  open.value = !open.value
  if (open.value) {
    await fetchList()
    await fetchCount()
  }
}

async function markOneRead(id) {
  try {
    await notificationsApi.markRead(id)
    await fetchCount()
    const n = notifications.value.find(x => x.id === id)
    if (n) n.read = true
  } catch (_) {}
}

async function markAllRead() {
  try {
    await notificationsApi.markAllRead()
    unreadCount.value = 0
    notifications.value.forEach(n => { n.read = true })
  } catch (_) {}
}

async function deleteNotification(id, e) {
  e?.stopPropagation()
  try {
    const n = notifications.value.find(x => x.id === id)
    const wasUnread = n && !n.read
    await notificationsApi.delete(id)
    notifications.value = notifications.value.filter(x => x.id !== id)
    if (wasUnread) unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (_) {}
}

onMounted(() => {
  fetchCount()
})
</script>

<template>
  <div class="notification-bell-wrap">
    <button
      type="button"
      class="bell-btn"
      aria-label="Notifications"
      @click="toggle"
    >
      <i class="bi bi-bell bell-icon"></i>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>
    <div v-if="open" class="dropdown" @click.stop>
      <div class="dropdown-header">
        <span>Notifications</span>
        <button
          v-if="notifications.length && unreadCount > 0"
          type="button"
          class="mark-all"
          @click="markAllRead"
        >
          Mark all read
        </button>
      </div>
      <div v-if="loading" class="dropdown-loading">Loading...</div>
      <div v-else-if="!notifications.length" class="dropdown-empty">No notifications</div>
      <ul v-else class="dropdown-list">
        <li
          v-for="n in notifications"
          :key="n.id"
          class="dropdown-item"
          :class="{ unread: !n.read }"
          @click="!n.read && markOneRead(n.id)"
        >
          <div class="item-content">
            <strong>{{ n.title }}</strong>
            <p v-if="n.message" class="msg">{{ n.message }}</p>
            <span class="time">{{ n.created_at ? new Date(n.created_at).toLocaleString() : '' }}</span>
          </div>
          <button
            type="button"
            class="dismiss-btn"
            aria-label="Dismiss"
            @click="deleteNotification(n.id, $event)"
          >
            ×
          </button>
        </li>
      </ul>
    </div>
    <div v-if="open" class="backdrop" @click="open = false" />
  </div>
</template>

<style scoped>
.notification-bell-wrap {
  position: relative;
}
.bell-btn {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  font-size: 1.25rem;
  border-radius: 8px;
  color: var(--color-text, #374151);
}
.bell-btn:hover {
  background: color-mix(in srgb, var(--color-border, #e5e7eb) 50%, transparent);
}
.notification-badge {
  position: absolute;
  top: 2px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
  background: #dc2626;
  color: #fff;
  border-radius: 9px;
}
.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 320px;
  max-height: 400px;
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
}
.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  font-weight: 600;
}
.mark-all {
  font-size: 12px;
  color: var(--color-primary, #2563eb);
  background: none;
  border: none;
  cursor: pointer;
}
.dropdown-loading,
.dropdown-empty {
  padding: 24px;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}
.dropdown-list {
  list-style: none;
  margin: 0;
  padding: 8px 0;
  overflow-y: auto;
  max-height: 320px;
}
.dropdown-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid color-mix(in srgb, var(--color-border, #e5e7eb) 50%, transparent);
  cursor: default;
}
.dropdown-item .item-content {
  flex: 1;
  min-width: 0;
}
.dismiss-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  border-radius: 4px;
}
.dismiss-btn:hover {
  color: #ef4444;
  background: color-mix(in srgb, #ef4444 15%, transparent);
}
.dropdown-item.unread {
  background: color-mix(in srgb, var(--color-primary, #2563eb) 8%, transparent);
  cursor: pointer;
}
.dropdown-item .msg {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dropdown-item .time {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #9ca3af;
}
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 99;
}
</style>

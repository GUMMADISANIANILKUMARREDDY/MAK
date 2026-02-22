<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({ initialConversationId: { type: String, default: null } })
const emit = defineEmits(['ready'])
import { chatApi } from '@/services/api'
import { connectChatWebSocket, onNewMessage, onMessagesRead, onTyping, onPresence, sendTyping } from '@/services/chatWebSocket'

const currentUserid = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u?.userid || ''
  } catch { return '' }
})

const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const searchDebounceTimer = ref(null)
const typingUser = ref(null)
const typingTimer = ref(null)
const onlineUserids = ref(new Set())

let unsubscribeNewMessage = null
let unsubscribeMessagesRead = null
let unsubscribeTyping = null
let unsubscribePresence = null
const typingDebounceRef = ref(null)

function handleNewMessage(msg) {
  if (!msg?.conversation_id) return
  const conv = conversations.value.find((c) => String(c.id) === String(msg.conversation_id))
  if (conv) updateConvLastMessage(conv, msg)
  if (!selectedConversation.value) return
  const convId = String(selectedConversation.value.id || '')
  const msgConvId = String(msg.conversation_id || '')
  if (msgConvId !== convId) return
  if (messages.value.some((m) => m.id === msg.id)) return
  messages.value = [...messages.value, msg]
}

function handleTyping({ conversation_id, userid, username }) {
  if (!selectedConversation.value || String(selectedConversation.value.id) !== String(conversation_id)) return
  if (userid === currentUserid.value) return
  typingUser.value = { userid, username }
  if (typingTimer.value) clearTimeout(typingTimer.value)
  typingTimer.value = setTimeout(() => { typingUser.value = null }, 3000)
}

function handlePresence({ type, userid }) {
  if (type === 'online') onlineUserids.value = new Set([...onlineUserids.value, userid])
  else onlineUserids.value = new Set([...onlineUserids.value].filter((id) => id !== userid))
}

function updateConvLastMessage(conv, msg) {
  if (!conv) return
  const list = conversations.value
  const idx = list.findIndex((c) => c.id === conv.id)
  if (idx >= 0) {
    const updated = [...list]
    updated[idx] = { ...updated[idx], last_message: { body: msg.body, created_at: msg.created_at, sender_userid: msg.sender_userid } }
    conversations.value = updated
  }
}

function isOnline(userid) {
  return onlineUserids.value.has(userid)
}

function onInputKeydown() {
  if (!selectedConversation.value) return
  const username = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}').username || currentUserid.value } catch { return currentUserid.value } })()
  if (typingDebounceRef.value) clearTimeout(typingDebounceRef.value)
  typingDebounceRef.value = setTimeout(() => {
    sendTyping(selectedConversation.value.id, username)
  }, 300)
}

function handleMessagesRead({ message_ids, read_at }) {
  if (!message_ids?.length || !read_at) return
  const ids = new Set(message_ids.map((id) => String(id)))
  let changed = false
  const updated = messages.value.map((m) => {
    if (ids.has(String(m.id))) {
      changed = true
      return { ...m, read_at }
    }
    return m
  })
  if (changed) messages.value = updated
}

async function fetchConversations() {
  loading.value = true
  error.value = ''
  try {
    const [convRes, onlineRes] = await Promise.all([
      chatApi.getConversations(),
      chatApi.getOnlineStatus().catch(() => ({ online_userids: [] })),
    ])
    conversations.value = convRes.conversations || []
    onlineUserids.value = new Set(onlineRes?.online_userids || [])
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function openConversation(conv) {
  selectedConversation.value = conv
  searchQuery.value = ''
  searchResults.value = []
  try {
    const res = await chatApi.getMessages(conv.id)
    messages.value = res.messages || []
  } catch {
    messages.value = []
  }
}

async function searchUsers() {
  const q = (searchQuery.value || '').trim()
  if (!q) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    const res = await chatApi.searchAvailableUsers(q)
    const list = res.users || []
    const existingIds = new Set(conversations.value.map(c => c.mentor_userid).concat(conversations.value.map(c => c.student_userid)))
    searchResults.value = list.filter(u => !existingIds.has(u.userid))
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

function scheduleSearch() {
  if (searchDebounceTimer.value) clearTimeout(searchDebounceTimer.value)
  searchDebounceTimer.value = setTimeout(searchUsers, 300)
}

function roleLabel(role) {
  const labels = { admin: 'Admin', manager: 'Manager', mentor: 'Mentor', student: 'Student', clgadmin: 'College Admin' }
  return labels[role] || role
}

function tickStatus(m) {
  if (m.sender_userid !== currentUserid.value) return null
  if (m.read_at) return 'read'
  return 'sent'
}

async function startConversationWith(user) {
  error.value = ''
  try {
    const res = await chatApi.getOrCreateWith(user.userid)
    const conv = res?.conversation
    if (!conv) throw new Error('Failed to start conversation')
    const exists = conversations.value.some(c => c.id === conv.id)
    if (!exists) {
      conversations.value = [conv, ...conversations.value]
    }
    openConversation(conv)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not start conversation'
  }
}

watch(searchQuery, () => scheduleSearch())
watch(() => [conversations.value.length, props.initialConversationId], () => {
  const id = props.initialConversationId
  if (!id || conversations.value.length === 0) return
  const conv = conversations.value.find((c) => String(c.id) === String(id))
  if (conv) {
    openConversation(conv)
    emit('ready')
  }
}, { immediate: true })

async function sendMsg() {
  if (!selectedConversation.value || !newMessage.value.trim()) return
  try {
    const res = await chatApi.sendMessage(selectedConversation.value.id, newMessage.value.trim())
    newMessage.value = ''
    // WebSocket will deliver the message in real-time; for sender we add immediately for instant feedback
    const sent = res?.message
    if (sent && !messages.value.some((m) => m.id === sent.id)) {
      messages.value = [...messages.value, sent]
      updateConvLastMessage(selectedConversation.value, sent)
    } else if (!sent) {
      const refreshed = await chatApi.getMessages(selectedConversation.value.id)
      messages.value = refreshed.messages || []
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Send failed'
  }
}

function onVisibilityChange() {
  if (document.visibilityState === 'visible' && selectedConversation.value) {
    chatApi.getMessages(selectedConversation.value.id).then((res) => {
      messages.value = res.messages || []
    }).catch(() => {})
  }
}

onMounted(() => {
  fetchConversations()
  connectChatWebSocket()
  unsubscribeNewMessage = onNewMessage(handleNewMessage)
  unsubscribeMessagesRead = onMessagesRead(handleMessagesRead)
  unsubscribeTyping = onTyping(handleTyping)
  unsubscribePresence = onPresence(handlePresence)
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onUnmounted(() => {
  if (unsubscribeNewMessage) unsubscribeNewMessage()
  if (unsubscribeMessagesRead) unsubscribeMessagesRead()
  if (unsubscribeTyping) unsubscribeTyping()
  if (unsubscribePresence) unsubscribePresence()
  if (searchDebounceTimer.value) clearTimeout(searchDebounceTimer.value)
  if (typingTimer.value) clearTimeout(typingTimer.value)
  if (typingDebounceRef.value) clearTimeout(typingDebounceRef.value)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<template>
  <div class="chat-view">
    <h3>Chat</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading && !selectedConversation" class="loading">Loading...</div>
    <div v-else class="chat-layout">
      <div class="conv-list">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search users to chat with..."
            class="search-input"
          />
          <span v-if="searchLoading" class="search-spinner">...</span>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <button
            v-for="u in searchResults"
            :key="u.userid"
            type="button"
            class="search-result-item"
            @click="startConversationWith(u)"
          >
            <span class="sr-name">{{ u.username || u.userid }}</span>
            <span class="sr-meta">{{ u.email }}{{ u.role ? ` · ${roleLabel(u.role)}` : '' }}</span>
          </button>
        </div>
        <p v-else-if="conversations.length === 0 && !searchQuery.trim()" class="empty">No conversations. Search above to start a chat.</p>
        <button
          v-for="c in conversations"
          v-show="!searchQuery.trim()"
          :key="c.id"
          class="conv-item"
          :class="{ active: selectedConversation?.id === c.id }"
          @click="openConversation(c)"
        >
          <span class="conv-item-header">
            <span class="conv-status-dot" :class="{ online: isOnline(c.other_userid), offline: !isOnline(c.other_userid) }"></span>
            <span class="conv-name">{{ c.other_username || c.mentor_userid + ' / ' + c.student_userid }}</span>
          </span>
          <span v-if="c.last_message" class="conv-preview">{{ c.last_message.body?.slice(0, 40) }}{{ (c.last_message.body || '').length > 40 ? '...' : '' }}</span>
        </button>
      </div>
      <div v-if="selectedConversation" class="messages-panel">
        <div class="messages">
          <div v-for="m in messages" :key="m.id" class="msg-row" :class="{ self: m.sender_userid === currentUserid }">
            <div class="msg-bubble">
              <span class="msg-body">{{ m.body }}</span>
              <span class="msg-meta">
                <span class="msg-time">{{ m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '' }}</span>
                <span v-if="m.sender_userid === currentUserid" class="msg-ticks" :class="tickStatus(m)">
                  <span class="double-tick">
                    <svg class="tick-icon" viewBox="0 0 16 16" width="12" height="12"><path fill="currentColor" d="M13.5 3L6 10.5 2.5 7"/></svg>
                    <svg class="tick-icon" viewBox="0 0 16 16" width="12" height="12"><path fill="currentColor" d="M13.5 3L6 10.5 2.5 7"/></svg>
                  </span>
                </span>
              </span>
            </div>
          </div>
        </div>
        <div v-if="typingUser" class="typing-indicator">{{ typingUser.username }} is typing...</div>
        <form class="send-form" @submit.prevent="sendMsg">
          <input v-model="newMessage" placeholder="Type a message..." @input="onInputKeydown" />
          <button type="submit" class="btn btn-primary">Send</button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout { display: flex; gap: 1rem; min-height: 300px; }
.conv-list { width: 220px; border: 1px solid var(--color-border); border-radius: 8px; padding: 0.5rem; }
.conv-item { display: flex; flex-direction: column; align-items: flex-start; width: 100%; text-align: left; padding: 0.5rem; border: none; background: none; cursor: pointer; border-radius: 4px; gap: 0.2rem; }
.conv-item:hover, .conv-item.active { background: var(--color-surface-2, #f3f4f6); }
.conv-item-header { display: flex; align-items: center; gap: 0.4rem; }
.conv-status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.conv-status-dot.online { background: #22c55e; }
.conv-status-dot.offline { background: #ef4444; }
.conv-name { font-weight: 600; font-size: 0.9rem; }
.conv-preview { font-size: 0.75rem; color: var(--color-muted, #64748b); max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.typing-indicator { font-size: 0.8rem; color: var(--color-muted); font-style: italic; padding: 0.25rem 0.75rem; }
.messages-panel { flex: 1; border: 1px solid var(--color-border); border-radius: 8px; display: flex; flex-direction: column; background: #e5ddd5; }
.messages { flex: 1; overflow-y: auto; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.25rem; }
.msg-row { display: flex; }
.msg-row.self { justify-content: flex-end; }
.msg-row:not(.self) { justify-content: flex-start; }
.msg-bubble { max-width: 65%; padding: 0.4rem 0.6rem 0.25rem; border-radius: 8px; font-size: 0.9rem; box-shadow: 0 1px 1px rgba(0,0,0,0.1); }
.msg-row.self .msg-bubble { background: #dcf8c6; margin-left: auto; border-bottom-right-radius: 2px; }
.msg-row:not(.self) .msg-bubble { background: #fff; border-bottom-left-radius: 2px; }
.msg-body { display: block; word-break: break-word; }
.msg-meta { display: flex; align-items: center; justify-content: flex-end; gap: 0.25rem; margin-top: 0.15rem; }
.msg-time { font-size: 0.7rem; color: rgba(0,0,0,0.45); }
.msg-ticks { display: inline-flex; align-items: center; }
.msg-ticks.sent .tick-icon { color: rgba(0,0,0,0.45); }
.msg-ticks.read .tick-icon { color: #34b7f1; }
.double-tick { display: flex; margin-left: -6px; }
.double-tick .tick-icon:first-child { margin-right: -4px; }
.send-form { display: flex; gap: 0.5rem; padding: 0.5rem; border-top: 1px solid #ccc; background: #f0f0f0; }
.send-form input { flex: 1; padding: 0.5rem 0.75rem; border-radius: 20px; border: 1px solid #ddd; font-size: 0.95rem; }
.search-box { position: relative; margin-bottom: 0.5rem; }
.search-input { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--color-border); font-size: 0.9rem; }
.search-spinner { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--color-muted); font-size: 0.8rem; }
.search-results { max-height: 200px; overflow-y: auto; border: 1px solid var(--color-border); border-radius: 6px; margin-bottom: 0.5rem; }
.search-result-item { display: flex; flex-direction: column; align-items: flex-start; width: 100%; padding: 0.5rem 0.75rem; border: none; background: none; cursor: pointer; text-align: left; border-bottom: 1px solid var(--color-border); font-size: 0.9rem; }
.search-result-item:last-child { border-bottom: none; }
.search-result-item:hover { background: var(--color-surface-2, #f3f4f6); }
.sr-name { font-weight: 600; }
.sr-meta { font-size: 0.75rem; color: var(--color-muted); }
.empty { color: var(--color-muted); padding: 1rem; }
</style>

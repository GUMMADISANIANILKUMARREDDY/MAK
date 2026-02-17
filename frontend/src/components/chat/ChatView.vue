<script setup>
import { ref, onMounted } from 'vue'
import { chatApi } from '@/services/api'

const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const error = ref('')

async function fetchConversations() {
  loading.value = true
  error.value = ''
  try {
    const res = await chatApi.getConversations()
    conversations.value = res.conversations || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load'
  } finally {
    loading.value = false
  }
}

async function openConversation(conv) {
  selectedConversation.value = conv
  try {
    const res = await chatApi.getMessages(conv.id)
    messages.value = res.messages || []
  } catch {
    messages.value = []
  }
}

async function sendMsg() {
  if (!selectedConversation.value || !newMessage.value.trim()) return
  try {
    await chatApi.sendMessage(selectedConversation.value.id, newMessage.value.trim())
    newMessage.value = ''
    const res = await chatApi.getMessages(selectedConversation.value.id)
    messages.value = res.messages || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Send failed'
  }
}

onMounted(() => fetchConversations())
</script>

<template>
  <div class="chat-view">
    <h3>Chat</h3>
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading && !selectedConversation" class="loading">Loading...</div>
    <div v-else class="chat-layout">
      <div class="conv-list">
        <p v-if="conversations.length === 0" class="empty">No conversations. Start a conversation from a task or team.</p>
        <button
          v-for="c in conversations"
          :key="c.id"
          class="conv-item"
          :class="{ active: selectedConversation?.id === c.id }"
          @click="openConversation(c)"
        >
          {{ c.mentor_userid }} ↔ {{ c.student_userid }}
        </button>
      </div>
      <div v-if="selectedConversation" class="messages-panel">
        <div class="messages">
          <div v-for="m in messages" :key="m.id" class="msg" :class="{ self: m.sender_userid === $store?.state?.user?.userid }">
            <strong>{{ m.sender_userid }}:</strong> {{ m.body }}
            <span class="time">{{ m.created_at ? new Date(m.created_at).toLocaleTimeString() : '' }}</span>
          </div>
        </div>
        <form class="send-form" @submit.prevent="sendMsg">
          <input v-model="newMessage" placeholder="Type a message..." />
          <button type="submit" class="btn btn-primary">Send</button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout { display: flex; gap: 1rem; min-height: 300px; }
.conv-list { width: 220px; border: 1px solid var(--color-border); border-radius: 8px; padding: 0.5rem; }
.conv-item { display: block; width: 100%; text-align: left; padding: 0.5rem; border: none; background: none; cursor: pointer; border-radius: 4px; }
.conv-item:hover, .conv-item.active { background: var(--color-surface-2, #f3f4f6); }
.messages-panel { flex: 1; border: 1px solid var(--color-border); border-radius: 8px; display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; padding: 0.75rem; }
.msg { padding: 0.4rem 0; border-bottom: 1px solid var(--color-border); font-size: 0.9rem; }
.msg .time { font-size: 0.75rem; color: var(--color-muted); margin-left: 0.5rem; }
.send-form { display: flex; gap: 0.5rem; padding: 0.5rem; border-top: 1px solid var(--color-border); }
.send-form input { flex: 1; padding: 0.5rem; border-radius: 6px; border: 1px solid var(--color-border); }
.empty { color: var(--color-muted); padding: 1rem; }
</style>

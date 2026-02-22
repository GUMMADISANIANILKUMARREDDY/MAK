/**
 * WebSocket service for real-time chat.
 * Connects to backend /chat/ws, receives new_message events and notifies subscribers.
 */
import { API_BASE_URL } from '@/config/api'

function getWsUrl() {
  const base = API_BASE_URL.replace(/^https?:\/\//, '')
  const protocol = API_BASE_URL.startsWith('https') ? 'wss' : 'ws'
  return `${protocol}://${base}/chat/ws`
}

let ws = null
let reconnectTimer = null
let pingInterval = null
const RECONNECT_DELAY_MS = 3000
const PING_INTERVAL_MS = 25000

/** @type {Set<(message: object) => void>} */
const listeners = new Set()
/** @type {Set<(data: { message_ids: string[], read_at: string }) => void>} */
const readListeners = new Set()
/** @type {Set<(data: { conversation_id: string, userid: string, username: string }) => void>} */
const typingListeners = new Set()
/** @type {Set<(data: { type: 'online' | 'offline', userid: string }) => void>} */
const presenceListeners = new Set()

function connect() {
  const token = localStorage.getItem('access_token')
  if (!token) return
  const url = `${getWsUrl()}?token=${encodeURIComponent(token)}`
  try {
    ws = new WebSocket(url)
  } catch (e) {
    scheduleReconnect()
    return
  }

  ws.onopen = () => {
    startPing()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  ws.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data)
      if (data.type === 'pong') return
      if (data.type === 'new_message' && data.message) {
        listeners.forEach((cb) => {
          try { cb(data.message) } catch (_) {}
        })
      }
      if (data.type === 'messages_read' && data.message_ids) {
        readListeners.forEach((cb) => {
          try { cb({ message_ids: data.message_ids, read_at: data.read_at }) } catch (_) {}
        })
      }
      if (data.type === 'typing' && data.conversation_id) {
        typingListeners.forEach((cb) => {
          try { cb({ conversation_id: data.conversation_id, userid: data.userid, username: data.username || data.userid }) } catch (_) {}
        })
      }
      if (data.type === 'user_online' && data.userid) {
        presenceListeners.forEach((cb) => {
          try { cb({ type: 'online', userid: data.userid }) } catch (_) {}
        })
      }
      if (data.type === 'user_offline' && data.userid) {
        presenceListeners.forEach((cb) => {
          try { cb({ type: 'offline', userid: data.userid }) } catch (_) {}
        })
      }
      if (data.type === 'online_status' && Array.isArray(data.online_userids)) {
        data.online_userids.forEach((uid) => {
          presenceListeners.forEach((cb) => {
            try { cb({ type: 'online', userid: uid }) } catch (_) {}
          })
        })
      }
    } catch (_) {}
  }

  ws.onclose = () => {
    stopPing()
    ws = null
    scheduleReconnect()
  }

  ws.onerror = () => {}
}

function scheduleReconnect() {
  if (reconnectTimer) return
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    if (localStorage.getItem('access_token')) connect()
  }, RECONNECT_DELAY_MS)
}

function startPing() {
  stopPing()
  pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, PING_INTERVAL_MS)
}

function stopPing() {
  if (pingInterval) {
    clearInterval(pingInterval)
    pingInterval = null
  }
}

/**
 * Subscribe to incoming new messages. Returns an unsubscribe function.
 * @param {(message: object) => void} callback
 * @returns {() => void}
 */
export function onNewMessage(callback) {
  listeners.add(callback)
  return () => listeners.delete(callback)
}

/**
 * Subscribe to messages-read events (for blue tick). Returns an unsubscribe function.
 * @param {(data: { message_ids: string[], read_at: string }) => void} callback
 * @returns {() => void}
 */
export function onMessagesRead(callback) {
  readListeners.add(callback)
  return () => readListeners.delete(callback)
}

export function onTyping(callback) {
  typingListeners.add(callback)
  return () => typingListeners.delete(callback)
}

export function onPresence(callback) {
  presenceListeners.add(callback)
  return () => presenceListeners.delete(callback)
}

export function sendTyping(conversationId, username) {
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'typing', conversation_id: conversationId, username }))
  }
}

/**
 * Connect WebSocket. Call when user logs in or app loads with valid token.
 */
export function connectChatWebSocket() {
  if (!localStorage.getItem('access_token')) return
  if (ws?.readyState === WebSocket.OPEN) return
  connect()
}

/**
 * Disconnect WebSocket. Call on logout.
 */
export function disconnectChatWebSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  stopPing()
  if (ws) {
    ws.close()
    ws = null
  }
  listeners.clear()
  readListeners.clear()
  typingListeners.clear()
  presenceListeners.clear()
}

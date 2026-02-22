/**
 * Web Push: register Service Worker, request permission, subscribe, send to backend.
 * Call setupPush() after user is logged in (e.g. in Dashboard on mount).
 */
import api from './api'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export async function setupPush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) return
  try {
    const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' })
    let sub = await reg.pushManager.getSubscription()
    if (sub) return
    const { data } = await api.get('/push/vapid-public')
    const vapidKey = data?.vapid_public_key
    if (!vapidKey) return
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidKey),
    })
    const subscription = sub.toJSON()
    await api.post('/push/subscribe', {
      endpoint: subscription.endpoint,
      keys: subscription.keys,
    })
  } catch (_) {
    // Permission denied, push not configured, or network error
  }
}

export function requestPushPermission() {
  if (!('Notification' in window)) return Promise.resolve(false)
  if (Notification.permission === 'granted') return Promise.resolve(true)
  if (Notification.permission === 'denied') return Promise.resolve(false)
  return Notification.requestPermission().then((p) => p === 'granted')
}

/* Service Worker for Web Push notifications */
self.addEventListener('push', (event) => {
  let data = { title: 'MAK', body: '' }
  try {
    if (event.data) {
      data = event.data.json()
    }
  } catch (_) {}
  const options = {
    body: data.body || '',
    icon: '/mak-only.svg',
    badge: '/mak-only.svg',
    data: data.data || {},
    tag: data.data?.conversation_id ? `chat-${data.data.conversation_id}` : undefined,
    requireInteraction: false,
  }
  event.waitUntil(self.registration.showNotification(data.title || 'MAK', options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/dashboard'
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url)
          return client.focus()
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(url)
      }
    })
  )
})

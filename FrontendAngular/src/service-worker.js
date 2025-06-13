self.addEventListener('push', event => {
  const data = event.data?.json() || { title: 'Phishing Alert', body: 'New suspicious activity detected.' };

  const options = {
    body: data.body,
    icon: '/assets/icons/icon-512x512.png',
    badge: '/assets/icons/badge-128x128.png',
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  const urlToOpen = event.notification.data?.url || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      return clients.openWindow(urlToOpen);
    })
  );
});

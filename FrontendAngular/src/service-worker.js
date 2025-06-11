self.addEventListener('push', function(event) {
  const data = event.data?.json() || {};
  const options = {
    body: data.body || 'Phishing alert detected!',
    icon: '/assets/icons/phishing.png',
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Alert', options)
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});

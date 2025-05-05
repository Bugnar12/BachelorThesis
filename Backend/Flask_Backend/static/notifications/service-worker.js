self.addEventListener('push', event => {
  const data = event.data.json();
  console.log('Push Received:', data);

  self.registration.showNotification(data.title, {
    body: data.body,
    // icon: '/static/notifications/icon.png' // optional
  });
});

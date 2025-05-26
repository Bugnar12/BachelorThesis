// console.log('Service Worker loaded!');
//
// self.addEventListener('push', event => {
//   console.log('Push event received:', event);
//
//   let data = { title: 'No title', body: 'No body', url: '/manual-analyze' };
//
//   try {
//     if (event.data) {
//       const parsed = event.data.json();
//       data = { ...data, ...parsed };
//     }
//   } catch (err) {
//     console.error('Failed to parse push data:', err);
//   }
//
//   const options = {
//     body: data.body,
//     icon: '/assets/danger.png',
//     data: {
//       url: data.url || '/manual-analyze'
//     }
//   };
//
//   event.waitUntil(
//     self.registration.showNotification(data.title, options)
//   );
// });
//
// self.addEventListener('notificationclick', event => {
//   const targetUrl = new URL(event.notification.data?.url || '/', self.location.origin).href;
//
//   event.notification.close();
//
//   event.waitUntil(
//     clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
//       for (let client of windowClients) {
//         if (client.url === targetUrl && 'focus' in client) {
//           return client.focus();
//         }
//       }
//       return clients.openWindow(targetUrl);
//     })
//   );
// });
//

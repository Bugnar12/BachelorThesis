const publicVapidKey = 'BC-eFWeA6XIeWohMDDZg4m_gIE7pOL-xYQXBYb0b9fhHeLZ9U3qQxojGlB3TCK1DG9-XuPmL9LNmwCPdCKZwrB4';

// Use access_token from sessionStorage/localStorage
async function subscribeToPush() {
  const token = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
  console.log("auth token fe", token)

  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.register('/static/notifications/service-worker.js');

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
    });

    await fetch('/push/subscribe', {
      method: 'POST',
      body: JSON.stringify(subscription),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    });
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = atob(base64);
  return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Immediately subscribe after page load
window.addEventListener('load', () => {
  subscribeToPush().catch(console.error);
});

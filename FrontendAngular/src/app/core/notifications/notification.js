const publicVapidKey = 'BC-eFWeA6XIeWohMDDZg4m_gIE7pOL-xYQXBYb0b9fhHeLZ9U3qQxojGlB3TCK1DG9-XuPmL9LNmwCPdCKZwrB4';

async function subscribeToPush() {
  console.log("enters subscribe push")
  const token = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
  if (!token) {
    console.warn('[Push] No token found — skipping push subscription.');
    return;
  }

  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('[Push] Push not supported by this browser.');
    return;
  }

  try {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      console.warn('[Push] Notification permission was denied.');
      return;
    }

    const registration = await navigator.serviceWorker.register('/service-worker.js');
    console.log('[Push] Service Worker registered:', registration.scope);

    // Check if already subscribed
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
      });
      console.log('[Push] New subscription created.');
    } else {
      console.log('[Push] Existing subscription found.');
    }

    // Send to backend
    console.log('[Push] Sending subscription to backend...');
    const res = await fetch('/push/subscribe', {
      method: 'POST',
      body: JSON.stringify(subscription),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    });

    if (!res.ok) {
      throw new Error(`[Push] Backend error: ${res.statusText}`);
    }

    console.log('[Push] Push subscription successfully sent.');
  } catch (err) {
    console.error('[Push] Subscription failed:', err);
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  return new Uint8Array([...rawData].map(c => c.charCodeAt(0)));
}

window.addEventListener('load', () => {
  subscribeToPush().catch(console.error);
});

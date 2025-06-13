import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {AuthService} from './auth.service';

@Injectable({ providedIn: 'root' })
export class PushNotificationService {
  readonly VAPID_PUBLIC_KEY = 'BKrfVX0c5FTp7ylDrFARxAWy25OKDQmqzq51zpiRH7LoFG001ayraGDr_oMs2rF3m2TwSgBeHwxM3Zpgqt7-roQ';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  async initPush() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        console.log('Service Worker registered');

        await navigator.serviceWorker.ready; // 🔑 Wait for it to be active
        console.log('Service Worker ready');
        await this.subscribe(registration);
      } catch (err) {
        console.error('Service worker registration failed:', err);
      }
    }
  }


  async subscribe(registration: ServiceWorkerRegistration) {
    const existingSubscription = await registration.pushManager.getSubscription();

    if (existingSubscription) {
      await existingSubscription.unsubscribe();
      console.log('Old push subscription removed');
    }

    const convertedVapidKey = this.urlBase64ToUint8Array(this.VAPID_PUBLIC_KEY);

    const newSubscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: convertedVapidKey,
    });

    console.log('New push subscription:', newSubscription);

    await this.http.post(
      `https://bachelorthesis-production-8acf.up.railway.app/users/push/subscribe`,
      newSubscription,
      {
        headers: {
          Authorization: `Bearer ${this.authService.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      }
    ).toPromise();
  }



  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
  }
}

import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';
import { importProvidersFrom } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { AuthInterceptor } from './app/core/services/auth.interceptor';
import { provideAnimations } from '@angular/platform-browser/animations';

// ✅ Chart.js component registration (MUST come before app bootstrap)
import {
  Chart,
  ArcElement,
  PieController,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js';

Chart.register(
  ArcElement,
  PieController,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    importProvidersFrom(HttpClientModule),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
    provideAnimations()
  ]
}).then(() => {
  // Register the custom service worker AFTER app is bootstrapped
  // if ('serviceWorker' in navigator) {
  //   navigator.serviceWorker
  //     .register('/service-worker.js')
  //     .then(reg => console.log('Service Worker registered:', reg.scope))
  //     .catch(err => console.error('Service Worker failed:', err));
  // }
});

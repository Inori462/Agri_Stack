import { registerSW } from 'virtual:pwa-register';

export default function ServiceWorkerWrapper() {
  // Register the service worker and handle updates.
  const updateSW = registerSW({
    onNeedRefresh() {
      // Prompt user to refresh - placeholder console log.
      console.log('New content is available, please refresh.');
    },
    onOfflineReady() {
      console.log('App is ready for offline use.');
    },
  });

  // No UI component; just side‑effect registration.
  return null;
}

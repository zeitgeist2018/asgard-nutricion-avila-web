// Service worker mínimo: solo lo necesario para que el navegador
// considere esta página "instalable" como app. No cachea nada
// especial, así que la app siempre usa la versión más reciente.

self.addEventListener("install", function (event) {
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  event.respondWith(fetch(event.request));
});

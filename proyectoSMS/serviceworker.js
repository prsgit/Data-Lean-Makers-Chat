// Base Service Worker implementation.  To use your own Service Worker, set the PWA_SERVICE_WORKER_PATH variable in settings.py

var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = [
  "/offline/",
  "/static/css/home.css",
  "/static/img/home.jpg",
];

// Cache on install
self.addEventListener("install", (event) => {
  this.skipWaiting();
  event.waitUntil(
    caches.open(staticCacheName).then((cache) => {
      return cache.addAll(filesToCache);
    })
  );
});

// Clear cache on activate
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName.startsWith("django-pwa-"))
          .filter((cacheName) => cacheName !== staticCacheName)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});

// Serve from Cache
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches
      .match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
      .catch(() => {
        return caches.match("/offline/");
      })
  );
});

// Manejo de notificaciones push
self.addEventListener("push", function (event) {
  let data = {};
  if (event.data) {
    data = event.data.json(); // intenta convertir los datos que se envían en formato JSON
  }

  const title = data.title || "Notificación";
  const options = {
    body: data.body || "Tienes una nueva notificación.",
    icon: data.icon || "/static/img/icon192.png", // Ruta del icono de la notificación
    badge: data.badge || "/static/img/icon192.png", // Ruta del badge de la notificación
    data: {
      url: data.url || "/chat/" + data.room_name, // URL a abrir al hacer clic
    },
  };

  event.waitUntil(
    self.registration.showNotification(title, options).catch((error) => {
      console.error("Error al mostrar la notificación:", error);
    })
  );
});

// Manejo de clic en la notificación
self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url) // URL a abrir al hacer clic
  );
});

const CACHE_NAME = 'puxbay-store-v1';
const ASSETS = [
    '/',
    '/static/css/tailwind.css',
    '/static/css/material-icons-round.css',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

const CACHE_NAME = 'puxbay-store-v2';
const STATIC_CACHE = 'puxbay-static-v2';
const IMAGE_CACHE = 'puxbay-images-v2';

const STATIC_ASSETS = [
    '/',
    '/static/css/tailwind.css',
    '/static/css/material-icons-round.css',
    '/static/pwa/offline.html'
];

// Install Event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            console.log('Precaching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate Event - Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== STATIC_CACHE && key !== IMAGE_CACHE)
                    .map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// Fetch Event
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests and browser extensions
    if (request.method !== 'GET' || !url.protocol.startsWith('http')) return;

    // Image Caching (Cache-First)
    if (request.destination === 'image') {
        event.respondWith(
            caches.open(IMAGE_CACHE).then(async (cache) => {
                const cachedResponse = await cache.match(request);
                if (cachedResponse) return cachedResponse;

                try {
                    const networkResponse = await fetch(request);
                    cache.put(request, networkResponse.clone());
                    return networkResponse;
                } catch (err) {
                    return cachedResponse;
                }
            })
        );
        return;
    }

    // Static Assets & Pages (Stale-While-Revalidate)
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            const fetchPromise = fetch(request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    caches.open(STATIC_CACHE).then((cache) => {
                        cache.put(request, networkResponse.clone());
                    });
                }
                return networkResponse;
            }).catch(() => {
                // If network fails and no cache, show offline page for navigation requests
                if (request.mode === 'navigate') {
                    return caches.match('/static/pwa/offline.html');
                }
            });

            return cachedResponse || fetchPromise;
        })
    );
});

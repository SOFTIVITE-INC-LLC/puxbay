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

    // 1. Bypass List: Never cache sensitive paths (Admin, Auth, API, Signup)
    const bypassPaths = ['/admin/', '/login/', '/logout/', '/api/', '/signup/', '/accounts/'];
    if (bypassPaths.some(path => url.pathname.includes(path))) {
        // We do NOT return here, instead we respond with network directly
        // to avoid any potential caching logic later in the event.
        return;
    }

    // Skip non-GET requests and browser extensions
    if (request.method !== 'GET' || !url.protocol.startsWith('http')) return;

    // 2. Navigation Requests (Network-First)
    // Ensures fresh HTML and CSRF tokens while online, with offline fallback
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).then((networkResponse) => {
                // Update cache if successful, but ONLY if not in bypass list
                const shouldCache = !bypassPaths.some(path => url.pathname.includes(path));
                if (networkResponse && networkResponse.status === 200 && shouldCache) {
                    caches.open(STATIC_CACHE).then((cache) => {
                        cache.put(request, networkResponse.clone());
                    });
                }
                return networkResponse;
            }).catch(async () => {
                // Return cached version if available, else show offline page
                const cachedResponse = await caches.match(request);
                return cachedResponse || caches.match('/static/pwa/offline.html');
            })
        );
        return;
    }

    // 3. Image Caching (Cache-First)
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

    // 4. Static Assets (Stale-While-Revalidate)
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
                // Handled above for navigation
                return undefined;
            });

            return cachedResponse || fetchPromise;
        })
    );
});

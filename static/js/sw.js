// Service Worker for Offline-First POS System
const CACHE_VERSION = 'v6'; // Incremented to force update
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `dynamic-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline/';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/offline/',
    '/static/css/tailwind.css',
    '/static/css/fonts.css',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(STATIC_CACHE).then(async (cache) => {
            console.log('[SW] Caching static assets');
            // Cache assets individually to handle failures gracefully
            for (const asset of STATIC_ASSETS) {
                try {
                    await cache.add(asset);
                    console.log('[SW] Cached:', asset);
                } catch (error) {
                    console.warn('[SW] Failed to cache:', asset, error);
                }
            }
        }).then(() => {
            return self.skipWaiting();
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip cross-origin requests
    if (!url.origin.includes(self.location.origin)) return;

    // Handle API requests separately? No, cache them too if needed.
    // For this app, we mainly cache static assets.

    event.respondWith(handleFetch(request));
});

async function handleFetch(request) {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request, { ignoreSearch: true, ignoreVary: true });

    if (cachedResponse) return cachedResponse;

    try {
        const response = await fetch(request);
        // Only cache successful GET requests
        if (response.ok && request.method === 'GET') {
            const dynamicCache = await caches.open(DYNAMIC_CACHE);
            dynamicCache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);
        const dynamicCache = await caches.open(DYNAMIC_CACHE);
        const cached = await dynamicCache.match(request, { ignoreSearch: true, ignoreVary: true });

        if (cached) {
            return cached;
        }

        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            const staticCache = await caches.open(STATIC_CACHE);
            const offlinePage = await staticCache.match(OFFLINE_URL, { ignoreSearch: true, ignoreVary: true });
            if (offlinePage) {
                return offlinePage;
            }
        }

        return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Background Sync - sync queued transactions
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync triggered:', event.tag);

    if (event.tag === 'sync-transactions') {
        event.waitUntil(syncTransactions());
    }
});

// Sync queued transactions
async function syncTransactions() {
    console.log('[SW] Syncing queued transactions...');

    try {
        const db = await openDB();

        // 1. Get CSRF Token
        const csrfToken = await getFromStore(db, 'settings', 'csrf_token');
        const token = csrfToken?.value || '';
        console.log('[SW] CSRF Token:', token ? 'Found' : 'Missing');

        // 1b. Get API Key
        const apiKeyData = await getFromStore(db, 'settings', 'api_key');
        const apiKey = apiKeyData?.value || '';
        console.log('[SW] API Key:', apiKey ? `Found (${apiKey.substring(0, 10)}...)` : 'Missing');

        if (!apiKey) {
            console.error('[SW] No API key found in IndexedDB - cannot sync');
            return;
        }

        // 2. Get Security Key
        const secureKeyData = await getFromStore(db, 'settings', 'pos_secure_key');
        let cryptoKey = null;
        if (secureKeyData?.value) {
            try {
                cryptoKey = await self.crypto.subtle.importKey(
                    'jwk',
                    secureKeyData.value,
                    { name: 'AES-GCM', length: 256 },
                    true,
                    ['decrypt']
                );
            } catch (e) {
                console.error('[SW] Failed to import security key:', e);
            }
        }

        // 3. Get Queue
        const queue = await getAllFromStore(db, 'sync_queue');

        if (queue.length === 0) {
            console.log('[SW] No transactions to sync');
            return;
        }

        console.log(`[SW] Syncing ${queue.length} transactions`);

        // Send each transaction to server
        for (const item of queue) {
            try {
                // Decrypt the queue item if it's encrypted
                let queueItem = item;
                if (item._encrypted && cryptoKey) {
                    try {
                        queueItem = await decryptData(item, cryptoKey);
                    } catch (e) {
                        console.error('[SW] Failed to decrypt queue item, skipping:', item.uuid, e);
                        continue;
                    }
                }

                const payload = queueItem.data;

                if (!payload) {
                    console.error('[SW] No payload data found for transaction:', item.uuid);
                    continue;
                }

                const response = await fetch('/api/v1/offline/transaction/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': token,
                        'X-API-Key': apiKey
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        uuid: item.uuid,
                        type: item.type,
                        data: payload
                    })
                });

                if (response.ok) {
                    await deleteFromStore(db, 'sync_queue', item.uuid);
                    console.log('[SW] Synced transaction:', item.uuid);
                } else {
                    const errorText = await response.text();
                    console.warn('[SW] Server rejected transaction:', item.uuid, response.status, errorText);
                    console.warn('[SW] Request headers:', {
                        'X-CSRFToken': token ? 'Present' : 'Missing',
                        'X-API-Key': apiKey ? 'Present' : 'Missing'
                    });
                }
            } catch (error) {
                console.error('[SW] Failed to sync transaction:', item.uuid, error);
            }
        }

        // Notify all clients about sync completion
        const allClients = await self.clients.matchAll();
        allClients.forEach(client => {
            client.postMessage({
                type: 'SYNC_COMPLETE',
                count: queue.length
            });
        });

    } catch (error) {
        console.error('[SW] Sync failed:', error);
        throw error;
    }
}

/**
 * Decrypts data using AES-GCM
 */
async function decryptData(encryptedObj, key) {
    try {
        const iv = new Uint8Array(encryptedObj.iv);
        const content = new Uint8Array(encryptedObj.content);

        const decryptedContent = await self.crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv },
            key,
            content
        );

        return JSON.parse(new TextDecoder().decode(decryptedContent));
    } catch (e) {
        console.error('[SW] Decryption failed:', e);
        return encryptedObj; // Fallback to raw if decryption fails (might be unencrypted)
    }
}

/**
 * Promisified IDB Helpers
 */
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('POSDatabase', 6);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function getFromStore(db, storeName, key) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const request = store.get(key);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

function getAllFromStore(db, storeName) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

function deleteFromStore(db, storeName, key) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.delete(key);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

// Message handler
self.addEventListener('message', (event) => {
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

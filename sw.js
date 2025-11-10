// Service Worker for SmartCart - Offline-First Support
// This enables the app to work offline after first load

const CACHE_NAME = 'smartcart-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/smartcart/',
    '/smartcart/index.html'
];

// Install event - cache app shell
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Service Worker: Caching app shell');
            return cache.addAll(urlsToCache).catch(() => {
                // If caching fails, that's OK - we'll cache on first request
                console.log('Service Worker: Could not cache all URLs, will cache on demand');
            });
        })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - Network first, fallback to cache
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests and external APIs for now
    if (request.method !== 'GET') {
        return;
    }

    // For GitHub Pages, use network-first strategy with cache fallback
    if (url.origin === 'https://ericssandbox.github.io' || 
        url.hostname.includes('smartcart') ||
        url.pathname.includes('smartcart')) {
        
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Only cache successful responses
                    if (response.status === 200) {
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, responseToCache);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Network failed, try cache
                    return caches.match(request).then((cached) => {
                        if (cached) {
                            console.log('Service Worker: Serving from cache', request.url);
                            return cached;
                        }
                        // If not in cache, return offline page
                        return caches.match('/index.html').catch(() => {
                            return new Response('Offline - Please check connection', {
                                status: 503,
                                statusText: 'Service Unavailable'
                            });
                        });
                    });
                })
        );
        return;
    }

    // For external APIs (TheMealDB, etc), use cache-first strategy
    if (url.hostname.includes('themealdb') || url.hostname.includes('api')) {
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) {
                    return cached;
                }
                return fetch(request)
                    .then((response) => {
                        if (response.status === 200) {
                            const responseToCache = response.clone();
                            caches.open(CACHE_NAME).then((cache) => {
                                cache.put(request, responseToCache);
                            });
                        }
                        return response;
                    })
                    .catch(() => {
                        // API call failed - that's OK, user can retry when online
                        console.log('Service Worker: API call failed (offline)', request.url);
                    });
            })
        );
    }
});

// Message handler for cache updates
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

console.log('Service Worker: Loaded');

/**
 * Smart Offline Navigation (Optimized)
 * - Only prefetches on intentional hover (100ms delay).
 * - Avoids mass-scanning links on page load to prevent server congestion.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Only run if service worker is active
    if (!navigator.serviceWorker || !navigator.serviceWorker.controller) return;

    let prefetchTimeout = null;

    // --- 1. Throttled Hover Prefetch ---
    const setupSafePrefetch = () => {
        // Use 'mouseenter' with a small delay to ensure it's an intentional hover
        document.body.addEventListener('mouseenter', (e) => {
            const anchor = e.target.closest('a[href]');
            if (!anchor) return;

            const href = anchor.getAttribute('href');
            if (!href ||
                href.startsWith('#') ||
                href.startsWith('javascript:') ||
                (!href.startsWith('/') && !href.startsWith(window.location.origin))) {
                return;
            }

            // Clear previous timeout if mouse moved off too fast
            if (prefetchTimeout) clearTimeout(prefetchTimeout);

            // Trigger fetch only after 100ms of hovering
            prefetchTimeout = setTimeout(() => {
                // Double check we are still on an anchor
                if (navigator.serviceWorker.controller) {
                    console.log(`[Offline-Nav] Pre-caching intentional hover: ${href}`);
                    navigator.serviceWorker.controller.postMessage({
                        type: 'CACHE_URLS',
                        urls: [href]
                    });
                }
            }, 100);

        }, { passive: true, capture: true });

        document.body.addEventListener('mouseleave', (e) => {
            const anchor = e.target.closest('a[href]');
            if (anchor && prefetchTimeout) {
                clearTimeout(prefetchTimeout);
                prefetchTimeout = null;
            }
        }, { passive: true, capture: true });
    };

    // Execute safe strategies
    setupSafePrefetch();

    console.log('[Offline-Nav] Optimized navigation prefetcher initialized.');
});

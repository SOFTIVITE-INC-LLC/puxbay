// Sync Manager for Offline Transactions
class SyncManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.syncInProgress = false;
        this.listeners = [];

        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Listen for service worker messages
        navigator.serviceWorker?.addEventListener('message', (event) => {
            this.handleSWMessage(event.data);
        });
    }

    // Handle online event
    async handleOnline() {
        console.log('[Sync] Network online');
        this.isOnline = true;
        this.notifyListeners('online');

        // Debounce sync to prevent rapid attempts when network toggles
        if (this.onlineTimeout) {
            clearTimeout(this.onlineTimeout);
        }

        this.onlineTimeout = setTimeout(async () => {
            try {
                await this.syncAll();
            } catch (error) {
                console.error('[Sync] Auto-sync on online failed:', error);
            }
        }, 1000); // Wait 1 second before syncing
    }

    // Handle offline event
    handleOffline() {
        console.log('[Sync] Network offline');
        this.isOnline = false;
        this.notifyListeners('offline');
    }

    // Handle service worker messages
    handleSWMessage(data) {
        console.log('[Sync] SW message:', data);
        console.log('[Sync] Current location:', window.location.href);
        console.log('[Sync] Current pathname:', window.location.pathname);

        if (data.type === 'SYNC_COMPLETE') {
            console.log('[Sync] SYNC_COMPLETE received, count:', data.count);

            // CRITICAL: Prevent any navigation away from POS page
            if (window.location.pathname.includes('/pos/')) {
                console.log('[Sync] ✓ Staying on POS page after sync completion');
                console.log('[Sync] ✓ No navigation will occur');
            }

            this.notifyListeners('sync_complete', { count: data.count });
        }
    }

    // Sync all queued data
    async syncAll() {
        if (this.syncInProgress) {
            console.log('[Sync] Sync already in progress');
            return;
        }

        if (!this.isOnline) {
            console.log('[Sync] Cannot sync while offline');
            return;
        }

        this.syncInProgress = true;
        this.notifyListeners('sync_start');

        try {
            // Get sync queue with retry logic for database connection issues
            let queue;
            try {
                queue = await window.posDB.getSyncQueue();
            } catch (dbError) {
                if (dbError.name === 'InvalidStateError') {
                    console.warn('[Sync] Database connection issue, retrying...');
                    // Wait a bit and retry once
                    await new Promise(resolve => setTimeout(resolve, 500));
                    queue = await window.posDB.getSyncQueue();
                } else {
                    throw dbError;
                }
            }

            console.log(`[Sync] Found ${queue.length} items to sync`);

            if (queue.length === 0) {
                this.syncInProgress = false;
                return;
            }

            let successCount = 0;
            let failCount = 0;

            // Process each item
            for (const item of queue) {
                try {
                    await this.syncItem(item);
                    await window.posDB.removeFromQueue(item.uuid);
                    successCount++;
                } catch (error) {
                    console.error('[Sync] Failed to sync item:', error);
                    failCount++;

                    // Update retry count
                    item.retries = (item.retries || 0) + 1;
                    if (item.retries < 3) {
                        await window.posDB.put('sync_queue', item);
                    } else {
                        // Max retries reached, remove from queue
                        await window.posDB.removeFromQueue(item.uuid);
                        console.error('[Sync] Max retries reached for:', item.uuid);
                    }
                }
            }

            console.log(`[Sync] Complete: ${successCount} success, ${failCount} failed`);
            this.notifyListeners('sync_complete', {
                success: successCount,
                failed: failCount
            });

        } catch (error) {
            console.error('[Sync] Sync failed:', error);
            this.notifyListeners('sync_error', { error });
        } finally {
            this.syncInProgress = false;
        }
    }

    // Helper to get CSRF token
    async getCsrfToken() {
        // 1. Try to get from document (if in main thread)
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (token) return token;

        // 2. Try to get from cookie
        token = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        if (token) return token;

        // 3. Try to get from IndexedDB (fallback)
        if (window.posDB) {
            try {
                return await window.posDB.getCsrfToken();
            } catch (e) {
                console.warn('[Sync] Failed to get CSRF from IDB:', e);
            }
        }

        return '';
    }

    // Sync individual item
    async syncItem(item) {
        console.log('[Sync] Syncing item:', item.type, item.uuid);

        const csrfToken = await this.getCsrfToken();

        // Get API key from IndexedDB
        const apiKeyData = await window.posDB.get('settings', 'api_key');
        const apiKey = apiKeyData?.value || '';

        console.log('[Sync] Sending to /api/v1/offline/transaction/');
        console.log('[Sync] Type:', item.type);
        console.log('[Sync] UUID:', item.uuid);
        console.log('[Sync] Has API Key:', !!apiKey);
        console.log('[Sync] Has CSRF Token:', !!csrfToken);

        const response = await fetch('/api/v1/offline/transaction/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-API-Key': apiKey
            },
            credentials: 'include',
            body: JSON.stringify({
                uuid: item.uuid,
                type: item.type,
                data: item.data
            })
        });

        console.log('[Sync] Response status:', response.status);
        console.log('[Sync] Response ok:', response.ok);

        if (!response.ok) {
            const error = await response.text();
            console.error('[Sync] Server error response:', error);
            console.error('[Sync] HTTP Status:', response.status);
            throw new Error(`Sync failed (${response.status}): ${error}`);
        }

        const result = await response.json();
        console.log('[Sync] Item synced successfully:', result);
        return result;
    }

    // Fetch and cache data from server
    async fetchAndCache(branchId) {
        if (!this.isOnline) {
            console.log('[Sync] Cannot fetch while offline');
            return;
        }

        console.log('[Sync] Fetching data for branch:', branchId);
        this.notifyListeners('cache_start');

        try {
            const csrfToken = await this.getCsrfToken();

            // Get API key from IndexedDB
            const apiKeyData = await window.posDB.get('settings', 'api_key');
            const apiKey = apiKeyData?.value || '';

            const response = await fetch(`/api/v1/offline/data/${branchId}/`, {
                headers: {
                    'X-API-Key': apiKey,
                    'X-CSRFToken': csrfToken
                },
                credentials: 'include'
            });
            if (!response.ok) {
                throw new Error('Failed to fetch sync data');
            }

            const data = await response.json();
            console.log('[Sync] Received data:', data);

            // Cache transactions (last 500)
            if (data.transactions) {
                await window.posDB.clear('transactions');
                await window.posDB.bulkPut('transactions', data.transactions);
                console.log(`[Sync] Cached ${data.transactions.length} transactions`);
            }

            // Cache products
            if (data.products) {
                await window.posDB.clear('products');
                await window.posDB.bulkPut('products', data.products);
                console.log(`[Sync] Cached ${data.products.length} products`);
            }

            // Cache customers
            if (data.customers) {
                await window.posDB.clear('customers');
                await window.posDB.bulkPut('customers', data.customers);
                console.log(`[Sync] Cached ${data.customers.length} customers`);
            }

            // Cache categories
            if (data.categories) {
                await window.posDB.clear('categories');
                await window.posDB.bulkPut('categories', data.categories);
                console.log(`[Sync] Cached ${data.categories.length} categories`);
            }

            // Cache settings
            if (data.settings) {
                // Settings store uses 'key' as primary key, so we need to transform the object
                const settingsEntries = Object.entries(data.settings).map(([key, value]) => ({
                    key: key,
                    value: value
                }));

                await window.posDB.clear('settings');
                // We don't have bulkPut for settings yet, doing loops for now or just put individual
                // Actually, let's use a loop since 'settings' store might not support bulkPut in our wrapper if not defined, 
                // but posDB wrapper likely uses Dexie or raw IDB. Assuming raw IDB wrapper based on context.
                // Let's safe-guard by using put for each.
                for (const entry of settingsEntries) {
                    await window.posDB.put('settings', entry);
                }
                console.log(`[Sync] Cached ${settingsEntries.length} settings`);
            }

            // Cache Attendance
            if (data.attendance) {
                await window.posDB.clear('attendance');
                if (data.attendance.length > 0) {
                    await window.posDB.bulkPut('attendance', data.attendance);
                }
                console.log(`[Sync] Cached ${data.attendance.length} attendance records`);
            }

            // Cache Staff
            if (data.staff) {
                await window.posDB.clear('staff');
                await window.posDB.bulkPut('staff', data.staff);
                console.log(`[Sync] Cached ${data.staff.length} staff profiles`);
            }

            // Cache Audit Logs
            if (data.audit_logs) {
                await window.posDB.clear('audit_logs');
                if (data.audit_logs.length > 0) {
                    await window.posDB.bulkPut('audit_logs', data.audit_logs);
                }
                console.log(`[Sync] Cached ${data.audit_logs.length} audit logs`);
            }

            // --- Cache Financials & Others ---

            // Cache Expenses
            if (data.expenses) {
                await window.posDB.clear('expenses');
                if (data.expenses.length > 0) {
                    await window.posDB.bulkPut('expenses', data.expenses);
                }
                console.log(`[Sync] Cached ${data.expenses.length} expenses`);
            }

            // Cache Taxes
            if (data.taxes) {
                await window.posDB.clear('taxes');
                if (data.taxes.length > 0) {
                    await window.posDB.bulkPut('taxes', data.taxes);
                }
                console.log(`[Sync] Cached ${data.taxes.length} tax configs`);
            }

            // Cache Suppliers
            if (data.suppliers) {
                await window.posDB.clear('suppliers');
                if (data.suppliers.length > 0) {
                    await window.posDB.bulkPut('suppliers', data.suppliers);
                }
                console.log(`[Sync] Cached ${data.suppliers.length} suppliers`);
            }

            // Cache Purchase Orders
            if (data.purchase_orders) {
                await window.posDB.clear('purchase_orders');
                if (data.purchase_orders.length > 0) {
                    await window.posDB.bulkPut('purchase_orders', data.purchase_orders);
                }
                console.log(`[Sync] Cached ${data.purchase_orders.length} purchase orders`);
            }

            // Cache Invoices (Future use)
            if (data.invoices && data.invoices.length > 0) {
                await window.posDB.clear('invoices');
                await window.posDB.bulkPut('invoices', data.invoices);
                console.log(`[Sync] Cached ${data.invoices.length} invoices`);
            }

            // Cache Stock Transfers
            if (data.stock_transfers) {
                await window.posDB.clear('stock_transfers');
                if (data.stock_transfers.length > 0) {
                    await window.posDB.bulkPut('stock_transfers', data.stock_transfers);
                }
                console.log(`[Sync] Cached ${data.stock_transfers.length} transfers`);
            }

            // Cache Stock Batches
            if (data.stock_batches) {
                await window.posDB.clear('stock_batches');
                if (data.stock_batches.length > 0) {
                    await window.posDB.bulkPut('stock_batches', data.stock_batches);
                }
                console.log(`[Sync] Cached ${data.stock_batches.length} stock batches`);
            }

            // Cache Cash Sessions
            if (data.cash_sessions) {
                await window.posDB.clear('cash_sessions');
                if (data.cash_sessions.length > 0) {
                    await window.posDB.bulkPut('cash_sessions', data.cash_sessions);
                }
                console.log(`[Sync] Cached ${data.cash_sessions.length} cash sessions`);
            }


            this.notifyListeners('cache_complete', data);
            return data;

        } catch (error) {
            console.error('[Sync] Cache failed:', error);
            this.notifyListeners('cache_error', { error });
            throw error;
        }
    }

    // Add listener
    addListener(callback) {
        this.listeners.push(callback);
    }

    // Remove listener
    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }

    // Notify all listeners
    notifyListeners(event, data = {}) {
        this.listeners.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('[Sync] Listener error:', error);
            }
        });
    }

    // Get sync status
    getStatus() {
        return {
            isOnline: this.isOnline,
            syncInProgress: this.syncInProgress
        };
    }

    // Queue transaction for sync
    async queueTransaction(arg1, arg2) {
        let type = 'transaction';
        let data = arg1;

        if (arg2 !== undefined) {
            type = arg1;
            data = arg2;
        }

        const uuid = await window.posDB.queueForSync(type, data);
        console.log('[Sync] Transaction queued:', type, uuid);

        // Try to sync immediately if online
        if (this.isOnline && 'serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
            try {
                const registration = await navigator.serviceWorker.ready;
                await registration.sync.register('sync-transactions');
                console.log('[Sync] Background sync registered');
            } catch (error) {
                console.error('[Sync] Background sync failed:', error);
                // Fallback to immediate sync
                await this.syncAll();
            }
        }

        return uuid;
    }

    // Sync inventory from server to prevent drift
    async syncInventory(branchId) {
        if (!this.isOnline) {
            console.log('[Sync] Cannot sync inventory while offline');
            return;
        }

        console.log('[Sync] Syncing inventory for branch:', branchId);

        try {
            const csrfToken = await this.getCsrfToken();

            // Get API key from IndexedDB
            const apiKeyData = await window.posDB.get('settings', 'api_key');
            const apiKey = apiKeyData?.value || '';

            const response = await fetch(`/api/v1/offline/inventory/${branchId}/`, {
                headers: {
                    'X-API-Key': apiKey,
                    'X-CSRFToken': csrfToken
                },
                credentials: 'include'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const products = await response.json();

            // Update local inventory
            for (const product of products) {
                const localProduct = await window.posDB.get('products', product.id);
                if (localProduct) {
                    localProduct.stock_quantity = product.stock_quantity;
                    await window.posDB.put('products', localProduct);
                }
            }

            console.log(`[Sync] Updated ${products.length} product inventories`);
            this.notifyListeners('inventory_synced', { count: products.length });

        } catch (error) {
            console.error('[Sync] Inventory sync failed:', error);
        }
    }
}

// Create global instance
window.syncManager = new SyncManager();

// Auto-sync on page load if online
window.addEventListener('load', () => {
    if (navigator.onLine) {
        console.log('[Sync] Page loaded, checking for pending syncs...');
        setTimeout(() => window.syncManager.syncAll(), 1000);
    }
});

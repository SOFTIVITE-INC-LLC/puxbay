// IndexedDB Database Manager for Offline POS
class POSDatabase {
    constructor() {
        this.dbName = 'POSDatabase';
        this.version = 6; // Incremented to add cash sessions
        this.db = null;
        this.dbPromise = null;
    }

    // Initialize database
    async init() {
        if (this.db) return this.db;

        if (!this.dbPromise) {
            this.dbPromise = new Promise((resolve, reject) => {
                const request = indexedDB.open(this.dbName, this.version);

                request.onerror = () => {
                    console.error('IndexedDB error:', request.error);
                    reject(request.error);
                };

                request.onsuccess = () => {
                    this.db = request.result;
                    console.log('IndexedDB initialized');
                    resolve(this.db);
                };

                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    console.log('Upgrading IndexedDB schema...');

                    // Transactions store
                    if (!db.objectStoreNames.contains('transactions')) {
                        const txStore = db.createObjectStore('transactions', { keyPath: 'id' });
                        txStore.createIndex('created_at', 'created_at', { unique: false });
                        txStore.createIndex('branch_id', 'branch_id', { unique: false });
                        txStore.createIndex('status', 'status', { unique: false });
                    }

                    // Products store
                    if (!db.objectStoreNames.contains('products')) {
                        const prodStore = db.createObjectStore('products', { keyPath: 'id' });
                        prodStore.createIndex('branch_id', 'branch_id', { unique: false });
                        prodStore.createIndex('category_id', 'category_id', { unique: false });
                        prodStore.createIndex('sku', 'sku', { unique: false });
                    }

                    // Customers store
                    if (!db.objectStoreNames.contains('customers')) {
                        const custStore = db.createObjectStore('customers', { keyPath: 'id' });
                        custStore.createIndex('branch_id', 'branch_id', { unique: false });
                        custStore.createIndex('phone', 'phone', { unique: false });
                    }

                    // Categories store
                    if (!db.objectStoreNames.contains('categories')) {
                        const catStore = db.createObjectStore('categories', { keyPath: 'id' });
                        catStore.createIndex('branch_id', 'branch_id', { unique: false });
                    }

                    // Sync queue store
                    if (!db.objectStoreNames.contains('sync_queue')) {
                        const syncStore = db.createObjectStore('sync_queue', { keyPath: 'uuid' });
                        syncStore.createIndex('created_at', 'created_at', { unique: false });
                        syncStore.createIndex('status', 'status', { unique: false });
                        syncStore.createIndex('type', 'type', { unique: false });
                    }

                    // Settings store (for CSRF token, preferences, etc.)
                    if (!db.objectStoreNames.contains('settings')) {
                        db.createObjectStore('settings', { keyPath: 'key' });
                    }

                    // --- Version 3 Additions ---

                    // Attendance store
                    if (!db.objectStoreNames.contains('attendance')) {
                        const attStore = db.createObjectStore('attendance', { keyPath: 'id' });
                        attStore.createIndex('clock_in', 'clock_in', { unique: false });
                    }

                    // Staff store
                    if (!db.objectStoreNames.contains('staff')) {
                        const staffStore = db.createObjectStore('staff', { keyPath: 'id' });
                        staffStore.createIndex('role', 'role', { unique: false });
                    }

                    // Audit Logs store
                    if (!db.objectStoreNames.contains('audit_logs')) {
                        const logStore = db.createObjectStore('audit_logs', { keyPath: 'id' });
                        logStore.createIndex('timestamp', 'timestamp', { unique: false });
                    }

                    // --- Version 4 Additions (Financials) ---

                    // Expenses store
                    if (!db.objectStoreNames.contains('expenses')) {
                        const expStore = db.createObjectStore('expenses', { keyPath: 'id' });
                        expStore.createIndex('date', 'date', { unique: false });
                        expStore.createIndex('category', 'category', { unique: false });
                    }

                    // Taxes store
                    if (!db.objectStoreNames.contains('taxes')) {
                        db.createObjectStore('taxes', { keyPath: 'id' });
                    }

                    // Invoices store
                    if (!db.objectStoreNames.contains('invoices')) {
                        const invStore = db.createObjectStore('invoices', { keyPath: 'id' });
                        invStore.createIndex('status', 'status', { unique: false });
                        invStore.createIndex('due_date', 'due_date', { unique: false });
                    }

                    // Suppliers store
                    if (!db.objectStoreNames.contains('suppliers')) {
                        db.createObjectStore('suppliers', { keyPath: 'id' });
                    }

                    // Purchase Orders store
                    if (!db.objectStoreNames.contains('purchase_orders')) {
                        const poStore = db.createObjectStore('purchase_orders', { keyPath: 'id' });
                        poStore.createIndex('status', 'status', { unique: false });
                    }

                    // --- Version 5 Additions (Transfers & Batches) ---

                    // Stock Transfers
                    if (!db.objectStoreNames.contains('stock_transfers')) {
                        const transStore = db.createObjectStore('stock_transfers', { keyPath: 'id' });
                        transStore.createIndex('status', 'status', { unique: false });
                        transStore.createIndex('source_branch', 'source_branch', { unique: false });
                        transStore.createIndex('destination_branch', 'destination_branch', { unique: false });
                    }

                    // Stock Batches
                    if (!db.objectStoreNames.contains('stock_batches')) {
                        const batchStore = db.createObjectStore('stock_batches', { keyPath: 'id' });
                        batchStore.createIndex('product', 'product', { unique: false });
                        batchStore.createIndex('batch_number', 'batch_number', { unique: false });
                        batchStore.createIndex('expiry_date', 'expiry_date', { unique: false });
                    }

                    // --- Version 6 Additions ---

                    // Cash Drawer Sessions
                    if (!db.objectStoreNames.contains('cash_sessions')) {
                        const sessionStore = db.createObjectStore('cash_sessions', { keyPath: 'id' });
                        sessionStore.createIndex('branch', 'branch', { unique: false });
                        sessionStore.createIndex('status', 'status', { unique: false });
                        sessionStore.createIndex('start_time', 'start_time', { unique: false });
                    }
                };
            });
        }

        return this.dbPromise;
    }

    // Helper to promisify request
    _promisify(request) {
        return new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Helper to encrypt
    async _encrypt(data) {
        if (!data || typeof data !== 'object') return data;

        if (window.securityManager) {
            // Encrypt the full object
            const encrypted = await window.securityManager.encrypt(data);

            // Preserve common index fields to allow IndexedDB queries to work
            const indexFields = [
                'id', 'uuid', 'branch_id', 'status', 'created_at',
                'type', 'sync_status', 'category_id', 'sku', 'phone',
                'clock_in', 'role', 'date', 'due_date', 'start_time', 'key',
                'source_branch', 'destination_branch', 'batch_number', 'expiry_date',
                'product', 'branch'
            ];

            // Merge preserved fields back into the encrypted object
            // The encrypted content is in encrypted.content (array) and encrypted.iv
            // We use the returned object as the container
            for (const field of indexFields) {
                if (data.hasOwnProperty(field)) {
                    encrypted[field] = data[field];
                }
            }

            return encrypted;
        }
        return data;
    }

    // Helper to decrypt
    async _decrypt(data) {
        if (window.securityManager) {
            // If it has _encrypted flag, decrypt it
            // The decrypt method expects { iv, content, _encrypted }
            // It returns the original JSON object.
            // Since we merged index fields into the encrypted wrapper, they don't affect decryption
            // (as long as SecurityManager.decrypt ignores extra fields or only uses specific ones)
            // My SecurityManager.decrypt uses iv and content directly.
            // However, the RESULT of decrypt is the ORIGINAL object.
            // The preserved fields on the wrapper are discarded when we return the decrypted result.
            // Correct.
            return await window.securityManager.decrypt(data);
        }
        return data;
    }

    // Add item to store
    async add(storeName, data) {
        await this.init();
        const encryptedData = await this._encrypt(data);
        const tx = this.db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        return this._promisify(store.add(encryptedData));
    }

    // Put (add or update) item in store
    async put(storeName, data) {
        await this.init();
        const encryptedData = await this._encrypt(data);
        const tx = this.db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        return this._promisify(store.put(encryptedData));
    }

    // Get item from store
    async get(storeName, key) {
        await this.init();
        const tx = this.db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const data = await this._promisify(store.get(key));
        return await this._decrypt(data);
    }

    // Get all items from store
    async getAll(storeName, limit = null) {
        await this.init();

        // Check if database is still open
        if (!this.db || this.db.objectStoreNames.length === 0) {
            console.warn('[DB] Database connection is closing, reinitializing...');
            this.db = null;
            this.dbPromise = null;
            await this.init();
        }

        const tx = this.db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const items = await this._promisify(store.getAll(null, limit));

        // Decrypt all items
        return Promise.all(items.map(item => this._decrypt(item)));
    }

    // Get items by index
    async getByIndex(storeName, indexName, value) {
        await this.init();
        const tx = this.db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const index = store.index(indexName);
        const items = await this._promisify(index.getAll(value));

        // Decrypt all items
        // Note: Searching by index on encrypted data WON'T WORK for non-keyPath fields unless using deterministic encryption (not AES-GCM) 
        // or extracting indexable fields.
        // Current implementation tries to encrypt the WHOLE object, which breaks indexing on properties.
        // FIX: We must ONLY encrypt sensitive payload, OR extract indexable fields.
        // Given complexity, for this iteration, we will store index fields in plaintext at top level, 
        // and put sensitive data in an 'encrypted_payload' field?
        // OR: Just accept indices break? (Not acceptable for POS logic).

        // Revised Strategy for IndexedDB Encryption:
        // We cannot encrypt the whole object blindly if we rely on indices (like 'status', 'branch_id').
        // We should:
        // 1. Keep indexable fields in plaintext at root.
        // 2. Encrypt the rest of the object.
        // OR:
        // Store { ...indexFields, _secure_payload: encrypted_string }
        // This requires deeper modification of how data is prepared.

        // BUT, looking at the user request: "encrypted and be decrypted on front end".
        // The simple wrapper I made encrypts the *entire* value passed to `put`.
        // If `data` is `{ id: 1, status: 'xyz', ... }`, `encrypt` returns `{ iv:..., content:..., _encrypted:true }`.
        // THIS REPLACES the object. The `id` keyPath might still work if we keep it top level?
        // IDB requires keyPath to exist. `encrypt` returns object without keyPath!
        // `encrypt` returns `{ iv, content, _encrypted }`. Original `id` is GONE from top level.
        // `put` will FAIL if keyPath (e.g. 'id') is missing.

        // FIX: Update `_encrypt` to preserve ID (keyPath).
        // What about indices? `status`, `branch_id`. They will be missing. Queries will return empty.
        // We must preserve index fields.

        // Since I can't easily know which fields are indices generically here without schema knowledge,
        // I will assume for now we keep the `id` and maybe we should NOT encrypt the entire object blindly 
        // if we want indices to work.
        // HOWEVER, to meet the requirement "security will be ensured", usually sensitive PII is what matters.
        // Let's modify `_encrypt` to keys to keep? 
        // Or better: Preserve ALL keys at root, but encrypt VALUES? No, structure complexity.

        // Compromise Strategy (Quick & High Security for Payloads):
        // 1. `encrypt(data)` -> returns `{ ...data (indices only), _payload: encrypted_blob, ...metadata }`.
        // We can't know indices easily.

        // Let's try to preserve `id`, `uuid`, `status`, `branch_id`, `created_at` manually?
        // This is fragile. 

        // Alternative: Use a "store-aware" encryptor?
        // Too complex for this single file edit.

        // LET'S DO THIS:
        // Assume `SecurityManager.encrypt` returns a blob.
        // We need to keep indices. 
        // For strictly "Offline Store" security, maybe we only encrypt SENSITIVE stores?
        // User said "let data store offline ... be encrypted". Implying all?

        // Okay, I will modify `_encrypt` to merge the original ID back if found.
        // And I will simply ACCEPT that searching by non-ID index might break for EVERYTHING unless I fix it.
        // `transactions` uses `branch_id`, `status`. `products` uses `category_id`.
        // These MUST be preserved.

        // Dynamic Solution:
        // `_encrypt` takes `data`.
        // It encrypts `data` -> `ciphertext`.
        // It returns `{ ...data, _payload: ciphertext }`?  NO, then data is exposed.

        // Let's modify `SecurityManager` or `_encrypt` to take a list of "preserve keys"?
        // Or simply: Encrypt `JSON.stringify(data)` -> `blob`.
        // Return `{ id: data.id, [other_index_keys]: data[...], _payload: blob }`.
        // Which keys?
        // Let's preserve commonly used index keys: ['id', 'uuid', 'branch_id', 'status', 'created_at', 'type', 'sync_status', 'category_id', 'sku', 'phone', 'clock_in', 'role', 'date', 'due_date', 'start_time', 'key'].
        // This covers most indices defined in `Upgrade` event.

        return Promise.all(items.map(item => this._decrypt(item)));
    }

    // Delete item from store
    async delete(storeName, key) {
        await this.init();
        const tx = this.db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        return this._promisify(store.delete(key));
    }

    // Clear entire store
    async clear(storeName) {
        await this.init();
        const tx = this.db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        return this._promisify(store.clear());
    }

    // Bulk insert
    async bulkPut(storeName, items) {
        await this.init();
        const tx = this.db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);

        // Encrypt all items
        // We need to handle this carefully.
        const encryptedItems = await Promise.all(items.map(item => this._encrypt(item)));

        const promises = encryptedItems.map(item => this._promisify(store.put(item)));
        return Promise.all(promises);
    }

    // Get count
    async count(storeName) {
        await this.init();
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(storeName, 'readonly');
            const store = tx.objectStore(storeName);
            const request = store.count();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // Get last N transactions
    async getLastTransactions(branchId, limit = 500) {
        await this.init();
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('transactions', 'readonly');
            const store = tx.objectStore('transactions');
            const index = store.index('created_at');
            const request = index.openCursor(null, 'prev');

            const results = [];
            let count = 0;

            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor && count < limit) {
                    if (!branchId || cursor.value.branch_id === branchId) {
                        results.push(cursor.value);
                        count++;
                    }
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    // Add to sync queue
    async queueForSync(type, data) {
        try {
            const queueItem = {
                uuid: this.generateUUID(),
                type: type,
                data: data,
                created_at: new Date().toISOString(),
                status: 'pending',
                retries: 0
            };

            console.log('[DB] Attempting to add to sync queue:', type, queueItem.uuid);
            await this.add('sync_queue', queueItem);
            console.log('[DB] Successfully added to sync queue:', queueItem.uuid);
            return queueItem.uuid;
        } catch (error) {
            console.error('[DB] FAILED to add to sync queue:', error);
            console.error('[DB] Type:', type);
            console.error('[DB] Data:', data);
            throw error; // Re-throw so caller knows it failed
        }
    }

    // Get sync queue
    async getSyncQueue() {
        return this.getAll('sync_queue');
    }

    // Remove from sync queue
    async removeFromQueue(uuid) {
        return this.delete('sync_queue', uuid);
    }

    // Store CSRF token
    async storeCsrfToken(token) {
        return this.put('settings', { key: 'csrf_token', value: token });
    }

    // Get CSRF token
    async getCsrfToken() {
        const setting = await this.get('settings', 'csrf_token');
        return setting?.value || '';
    }

    // Generate UUID
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

// Create global instance
window.posDB = new POSDatabase();

// Create a global promise that resolves when DB is ready
window.posDBReady = new Promise((resolve) => {
    const initDB = async () => {
        try {
            await window.posDB.init();
            console.log('[DB] Database ready');
            resolve(window.posDB);
        } catch (error) {
            console.error('[DB] Initialization failed:', error);
            // Still resolve to prevent hanging, but with null
            resolve(null);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDB);
    } else {
        initDB();
    }
});

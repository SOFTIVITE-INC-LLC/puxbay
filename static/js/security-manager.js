/**
 * SecurityManager
 *
 * Handles client-side encryption for offline data storage using Web Crypto API (AES-GCM).
 * This ensures that sensitive data stored in IndexedDB is encrypted at rest.
 */
class SecurityManager {
    constructor() {
        this.key = null;
        this.algo = { name: 'AES-GCM', length: 256 };
        this.keyStorageName = 'pos_secure_key';
    }

    /**
     * Initializes the security manager.
     * Tries to load an existing key or generates a new one.
     */
    async init() {
        try {
            await this.loadKey();
            if (!this.key) {
                console.log('[SecurityManager] No key found, generating new one...');
                await this.generateKey();
            }
            console.log('[SecurityManager] Initialized');
            return true;
        } catch (e) {
            console.error('[SecurityManager] Init failed', e);
            return false;
        }
    }

    /**
     * Generates a new AES-GCM key and saves it to localStorage (exported).
     * In a real production environment with stricter requirements, 
     * this might involve wrapping with a user-derived password key.
     */
    async generateKey() {
        this.key = await window.crypto.subtle.generateKey(
            this.algo,
            true, // extractable
            ['encrypt', 'decrypt']
        );
        await this.saveKey();
    }

    /**
     * Exports key to JWK and saves to IndexedDB
     */
    async saveKey() {
        if (!this.key) return;
        try {
            const exported = await window.crypto.subtle.exportKey('jwk', this.key);

            // Use raw IndexedDB to avoid circular dependency with posDB
            const db = await this._openDB();
            const tx = db.transaction('settings', 'readwrite');
            const store = tx.objectStore('settings');
            store.put({ key: this.keyStorageName, value: exported });

            // Backup to localStorage for now to ensure smooth transition (optional)
            localStorage.setItem(this.keyStorageName, JSON.stringify(exported));
        } catch (e) {
            console.error('[SecurityManager] Failed to save key', e);
        }
    }

    /**
     * Loads key from IndexedDB, falls back to localStorage
     */
    async loadKey() {
        try {
            // Try IndexedDB first (accessible by SW)
            const db = await this._openDB();
            const tx = db.transaction('settings', 'readonly');
            const store = tx.objectStore('settings');

            const request = store.get(this.keyStorageName);
            const result = await new Promise((resolve) => {
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => resolve(null);
            });

            let jwk = result ? result.value : null;

            // Fallback to localStorage (legacy)
            if (!jwk) {
                const jsonKey = localStorage.getItem(this.keyStorageName);
                if (jsonKey) {
                    jwk = JSON.parse(jsonKey);
                    // Migrating to IDB will happen next time saveKey is called
                }
            }

            if (jwk) {
                this.key = await window.crypto.subtle.importKey(
                    'jwk',
                    jwk,
                    this.algo,
                    true,
                    ['encrypt', 'decrypt']
                );
            }
        } catch (e) {
            console.error('[SecurityManager] Failed to load key', e);
        }
    }

    /**
     * Helper to get initialized DB from posDB
     */
    async _openDB() {
        // Wait for posDB to be ready before accessing
        if (window.posDBReady) {
            await window.posDBReady;
            if (window.posDB && window.posDB.db) {
                return window.posDB.db;
            }
        }

        // Fallback: open directly with proper upgrade handling
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('POSDatabase', 6);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                // Create settings store if it doesn't exist
                if (!db.objectStoreNames.contains('settings')) {
                    db.createObjectStore('settings', { keyPath: 'key' });
                }
            };

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Encrypts data object.
     * Returns { iv: ..., data: ... }
     */
    async encrypt(data) {
        if (!this.key) await this.init();

        const encoded = new TextEncoder().encode(JSON.stringify(data));
        const iv = window.crypto.getRandomValues(new Uint8Array(12));

        const encryptedContent = await window.crypto.subtle.encrypt(
            {
                name: 'AES-GCM',
                iv: iv
            },
            this.key,
            encoded
        );

        return {
            iv: Array.from(iv), // Store as array for JSON serialization
            content: Array.from(new Uint8Array(encryptedContent)),
            _encrypted: true
        };
    }

    /**
     * Decrypts encrypted data object.
     * dataObj must have { iv: [], content: [], _encrypted: true }
     */
    async decrypt(encryptedObj) {
        if (!this.key) await this.init();

        // Return as-is if not encrypted
        if (!encryptedObj || !encryptedObj._encrypted) return encryptedObj;

        try {
            const iv = new Uint8Array(encryptedObj.iv);
            const content = new Uint8Array(encryptedObj.content);

            const decryptedContent = await window.crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: iv
                },
                this.key,
                content
            );

            const decoded = new TextDecoder().decode(decryptedContent);
            return JSON.parse(decoded);
        } catch (e) {
            console.error('[SecurityManager] Decryption failed', e);
            throw e;
        }
    }
}

// Singleton export
window.securityManager = new SecurityManager();
// Don't auto-init - let it initialize lazily when first used
// This prevents race conditions with db.js initialization

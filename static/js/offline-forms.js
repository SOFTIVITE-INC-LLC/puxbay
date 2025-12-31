/**
 * OfflineFormManager
 * 
 * Handles intercepting form submissions, saving data to local IndexedDB,
 * and queuing transactions for background synchronization.
 */
class OfflineFormManager {
    constructor(config) {
        this.config = {
            formId: null,
            storeName: null,      // IndexedDB store name (e.g., 'stock_transfers')
            transactionType: null, // Sync transaction type (e.g., 'create_transfer')
            redirectUrl: null,    // URL to redirect to after success
            successMessage: 'Saved locally and queued for sync.',
            onBeforeSave: null,   // Async callback to transform data before saving
            validate: null, // Async function(data) -> { valid: boolean, message: string }
            ...config
        };

        this.form = document.getElementById(this.config.formId);
        this.isProcessing = false;

        this.init();
    }

    init() {
        if (!this.form) {
            console.error(`OfflineFormManager: Form #${this.config.formId} not found`);
            return;
        }

        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmit();
        });
    }

    async handleSubmit() {
        if (this.isProcessing) return;
        this.isProcessing = true;

        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn ? submitBtn.innerText : '';

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = 'Saving...';
            }

            // 1. Gather Form Data
            const formData = new FormData(this.form);
            let data = Object.fromEntries(formData.entries());

            // 2. Custom Data transformation
            if (this.config.onBeforeSave) {
                data = await this.config.onBeforeSave(data);
                if (!data) throw new Error('Form validation failed in onBeforeSave');
            }

            // 3. Add Metadata
            data.id = `temp_${Date.now()}`; // Temporary ID until synced
            data.created_at = new Date().toISOString();
            data.status = 'pending_sync'; // Local status
            data.synced = false;

            // 4. Save to Local DB (IndexedDB)
            if (window.posDB) {
                await window.posDB.init();

                // Save actual record to its store (for list display)
                if (this.config.storeName) {
                    await window.posDB.add(this.config.storeName, data);
                    console.log(`[OfflineFormManager] Saved to ${this.config.storeName}`);
                }

                // 5. Queue for Sync
                if (window.syncManager) {
                    try {
                        await window.syncManager.queueTransaction(this.config.transactionType, data);
                        console.log(`[OfflineFormManager] Queued ${this.config.transactionType}`);

                        // Trigger sync if online
                        if (navigator.onLine) {
                            window.syncManager.syncAll();
                        }
                    } catch (queueError) {
                        console.error('[OfflineFormManager] Failed to queue for sync:', queueError);
                        throw new Error('Failed to queue for sync: ' + queueError.message);
                    }
                }
            } else {
                throw new Error('Database not initialized');
            }

            // 6. UI Feedback & Redirect
            if (window.showToast) {
                window.showToast(this.config.successMessage, 'success');
            }

            await new Promise(r => setTimeout(r, 1000)); // Small delay for user to see 'Saving...'

            if (this.config.redirectUrl) {
                window.location.href = this.config.redirectUrl;
            }

        } catch (error) {
            console.error('[OfflineFormManager] Error:', error);
            if (window.showToast) {
                window.showToast('Failed to save offline: ' + error.message, 'error');
            }
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = originalBtnText;
            }
        } finally {
            this.isProcessing = false;
        }
    }
}

/**
 * OfflineListInjector
 * 
 * Fetches locally saved pending items and injects them into the list view.
 */
class OfflineListInjector {
    constructor(config) {
        this.config = {
            containerId: null,    // ID of the UL or Container
            storeName: null,      // IndexedDB store name
            emptyStateId: null,   // ID of empty state element to hide if items added
            templateFunc: null,   // Function(item) => HTML string
            filterFunc: (item) => true, // Optional filter
            ...config
        };

        this.container = document.getElementById(this.config.containerId);
        this.init();
    }

    async init() {
        if (!this.container || !window.posDB) return;

        try {
            await window.posDB.init();

            const items = await window.posDB.getAll(this.config.storeName);
            // Filter for pending items created locally (usually have id starting with 'temp_')
            const pendingItems = items.filter(item =>
                (item.status === 'pending_sync' || (typeof item.id === 'string' && item.id.startsWith('temp_'))) &&
                this.config.filterFunc(item)
            );

            if (pendingItems.length > 0) {
                console.log(`[OfflineListInjector] Found ${pendingItems.length} pending items for ${this.config.storeName}`);

                // Hide empty state if exists
                if (this.config.emptyStateId) {
                    const empty = document.getElementById(this.config.emptyStateId);
                    if (empty) empty.style.display = 'none';
                    // Also try finding by existing 'empty' class or similar if ID not provided? 
                    // Usually we just inject into the UL.
                }

                // Sort by newest first
                pendingItems.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

                // Keep track of injected IDs to avoid duplicates if re-run
                const existingIds = Array.from(this.container.querySelectorAll('[data-offline-id]'))
                    .map(el => el.dataset.offlineId);

                let html = '';
                for (const item of pendingItems) {
                    if (existingIds.includes(item.id.toString())) continue;
                    html += this.config.templateFunc(item);
                }

                // Prepend to list
                if (html) {
                    this.container.insertAdjacentHTML('afterbegin', html);
                }
            }

        } catch (error) {
            console.error('[OfflineListInjector] Error:', error);
        }
    }
}

/**
 * OfflineDeleteHandler
 * Handles offline deletions by intercepting form submissions or button clicks.
 */
class OfflineDeleteHandler {
    constructor(config) {
        this.config = Object.assign({
            triggerSelector: 'form[action*="delete"]', // Default: forms with delete in action
            storeName: null, // Optional: Update a store (usually remove item)
            transactionType: null, // Required if generic script cannot determine it. Or derived from context.
            redirectUrl: null,
            confirmMessage: 'Are you sure you want to delete this item?',
            idField: 'id' // Field in dataset or input to identify item
        }, config);

        this.init();
    }

    init() {
        const triggers = document.querySelectorAll(this.config.triggerSelector);
        triggers.forEach(trigger => {
            trigger.addEventListener('submit', (e) => this.handleSubmit(e, trigger));
            // Also handle buttons if selector targets buttons directly
            if (trigger.tagName === 'BUTTON' || trigger.tagName === 'A') {
                trigger.addEventListener('click', (e) => this.handleClick(e, trigger));
            }
        });
    }

    async handleSubmit(e, element) {
        e.preventDefault();
        await this.processDelete(element);
    }

    async handleClick(e, element) {
        e.preventDefault();
        await this.processDelete(element);
    }

    async processDelete(element) {
        if (this.config.confirmMessage && !confirm(this.config.confirmMessage)) return;

        try {
            // Determine ID
            let id = null;
            // 1. Try generic URL parsing if action/href exists
            const url = element.action || element.href;
            if (url) {
                const parts = url.split('/');
                // typical django url: /.../pk/delete/
                // e.g. /branches/staff/5/delete/ -> 5 is index -2 (with trailing slash)
                // Filter out empty strings
                const cleanParts = parts.filter(p => p !== '');
                // Try the last non-empty part or look for UUID-like string
                for (let i = cleanParts.length - 1; i >= 0; i--) {
                    // Check if part looks like an ID (number or UUID)
                    const part = cleanParts[i];
                    if (part.trim() !== '' && (!isNaN(part) || /^[0-9a-fA-F-]{36}$/.test(part))) {
                        id = part;
                        break;
                    }
                }
            }

            // 2. Try input hidden named 'pk' or 'id'
            if (!id && element.tagName === 'FORM') {
                const input = element.querySelector('input[name="pk"]') || element.querySelector('input[name="id"]');
                if (input) id = input.value;
            }

            // 3. Try dataset
            if (!id && element.dataset.id) id = element.dataset.id;
            if (!id && element.dataset.pk) id = element.dataset.pk;

            if (!id) {
                console.error("Could not determine ID for deletion");
                return; // Fallback to default submission?
            }

            // Queue Transaction
            const transactionData = { id: id }; // ID is now string (UUID)
            if (window.syncManager) {
                // If specific transaction type isn't provided, try to guess or fail?
                // We really need a specific type e.g. 'delete_staff'
                if (this.config.transactionType) {
                    await window.syncManager.queueTransaction(this.config.transactionType, transactionData);
                } else {
                    console.warn('No transactionType configured for offline delete');
                    return;
                }
            }

            // Remove from Store if configured
            if (this.config.storeName && window.posDB) {
                try {
                    await window.posDB.delete(this.config.storeName, id);
                } catch (dbErr) {
                    console.warn(`Could not delete from local store ${this.config.storeName}`, dbErr);
                }
            }

            // UI Feedback
            if (typeof showToast === 'function') {
                showToast('Item deleted successfully (Offline)', 'success');
            }

            // Redirect
            if (this.config.redirectUrl) {
                window.location.href = this.config.redirectUrl;
            } else {
                // If in a list, remove the row
                const row = element.closest('tr') || element.closest('.group') || element.closest('li');
                if (row) {
                    row.style.opacity = '0.5';
                    setTimeout(() => row.remove(), 500);
                }
            }

        } catch (error) {
            console.error('Offline delete failed:', error);
            alert('Offline deletion failed.');
        }
    }
}

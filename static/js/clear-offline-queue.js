/**
 * Clear Offline Sync Queue
 * Run this in the browser console to clear stuck items from the sync queue
 */

async function clearOfflineQueue() {
    console.log('[Clear Queue] Starting cleanup...');

    try {
        // Initialize database
        await window.posDB.init();

        // Get all items in sync queue
        const queue = await window.posDB.getSyncQueue();
        console.log(`[Clear Queue] Found ${queue.length} items in sync queue`);

        if (queue.length === 0) {
            console.log('[Clear Queue] Queue is already empty!');
            return;
        }

        // Show items
        console.table(queue.map(item => ({
            UUID: item.uuid,
            Type: item.type,
            Status: item.status,
            Retries: item.retries,
            Created: new Date(item.created_at).toLocaleString()
        })));

        // Ask for confirmation
        const confirmed = confirm(`Found ${queue.length} items in sync queue. Clear all?`);

        if (!confirmed) {
            console.log('[Clear Queue] Cancelled by user');
            return;
        }

        // Clear sync queue
        let cleared = 0;
        for (const item of queue) {
            await window.posDB.removeFromQueue(item.uuid);
            cleared++;
            console.log(`[Clear Queue] Removed: ${item.type} (${item.uuid})`);
        }

        console.log(`[Clear Queue] ✅ Successfully cleared ${cleared} items from sync queue`);

        // Also clear pending items from local stores
        console.log('[Clear Queue] Checking for pending items in local stores...');

        // Clear pending stock transfers
        const transfers = await window.posDB.getAll('stock_transfers');
        const pendingTransfers = transfers.filter(t =>
            t.status === 'pending_sync' ||
            (typeof t.id === 'string' && t.id.startsWith('temp_'))
        );

        if (pendingTransfers.length > 0) {
            console.log(`[Clear Queue] Found ${pendingTransfers.length} pending transfers`);
            for (const transfer of pendingTransfers) {
                await window.posDB.delete('stock_transfers', transfer.id);
                console.log(`[Clear Queue] Removed pending transfer: ${transfer.id}`);
            }
        }

        // Clear pending purchase orders
        const pos = await window.posDB.getAll('purchase_orders');
        const pendingPOs = pos.filter(po =>
            po.status === 'pending_sync' ||
            (typeof po.id === 'string' && po.id.startsWith('temp_'))
        );

        if (pendingPOs.length > 0) {
            console.log(`[Clear Queue] Found ${pendingPOs.length} pending purchase orders`);
            for (const po of pendingPOs) {
                await window.posDB.delete('purchase_orders', po.id);
                console.log(`[Clear Queue] Removed pending PO: ${po.id}`);
            }
        }

        console.log('[Clear Queue] ✅ Cleanup complete!');
        console.log('[Clear Queue] Refresh the page to see the changes.');

    } catch (error) {
        console.error('[Clear Queue] Error:', error);
    }
}

// Auto-run if called directly
if (typeof window !== 'undefined') {
    console.log('='.repeat(60));
    console.log('OFFLINE QUEUE CLEANER');
    console.log('='.repeat(60));
    console.log('Run: clearOfflineQueue()');
    console.log('This will remove all pending items from the sync queue');
    console.log('='.repeat(60));
}

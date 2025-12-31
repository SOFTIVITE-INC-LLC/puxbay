export class CartManager {
    constructor(app) {
        this.app = app;
        this.items = [];
    }

    addItem(product, batch = null) {
        const cartItemId = batch ? `${product.id}-${batch.id}` : product.id;
        const existing = this.items.find(item => item.cartItemId === cartItemId);

        if (existing) {
            if (existing.quantity < (batch ? batch.quantity : product.stock)) {
                existing.quantity++;
            } else {
                window.showToast?.('Maximum stock reached', 'warning');
            }
        } else {
            this.items.push({
                cartItemId,
                id: product.id,
                name: product.name,
                price: parseFloat(product.price),
                quantity: 1,
                batchId: batch ? batch.id : null,
                batchNumber: batch ? batch.batch_number : null,
                maxStock: batch ? batch.quantity : product.stock
            });
        }
        this.app.render();
    }

    addSpecialItem(itemData) {
        const cartItemId = `special-${Date.now()}`;
        this.items.push({
            cartItemId,
            quantity: 1,
            maxStock: 999, // Special items have virtually unlimited stock check
            ...itemData
        });
        this.app.render();
    }

    remove(cartItemId) {
        this.items = this.items.filter(item => item.cartItemId !== cartItemId);
        this.app.render();
    }

    updateQuantity(cartItemId, delta) {
        const item = this.items.find(i => i.cartItemId === cartItemId);
        if (item) {
            const newQty = item.quantity + delta;
            if (newQty > 0 && (item.type || newQty <= item.maxStock)) {
                item.quantity = newQty;
            } else if (newQty > item.maxStock) {
                window.showToast?.('Maximum stock reached', 'warning');
            }
            this.app.render();
        }
    }

    clear() {
        this.items = [];
        this.app.giftCardCode = null;
        this.app.splitPayments = [];
        this.app.paymentMethod = 'cash';
        this.app.render();
    }

    get subtotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    get total() {
        // Add tax logic here if needed
        return this.subtotal;
    }
}

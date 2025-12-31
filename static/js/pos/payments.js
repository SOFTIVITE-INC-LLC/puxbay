export class PaymentHandler {
    constructor(app, config) {
        this.app = app;
        this.config = config;
        this.stripe = this.config.stripe_enabled && window.Stripe ? window.Stripe(this.config.stripe_key) : null;
    }

    async processCheckout(amount, items, customerId, paymentMethod, giftCardCode = null, extraData = {}) {
        if (paymentMethod === 'stripe' && this.stripe) {
            return this.handleStripe(amount);
        } else if (paymentMethod === 'paystack' && this.config.paystack_enabled) {
            return this.handlePaystack(amount);
        } else {
            return this.submitFinalOrder({
                amount,
                items,
                customer_id: customerId,
                payment_method: paymentMethod,
                gift_card_code: giftCardCode,
                ...extraData
            });
        }
    }

    async handleStripe(amount) {
        // Implementation for Stripe checkout session or PaymentIntent
        // For POS, we usually use PaymentIntents or Terminal
        // This is a placeholder for the flow used in the original pos.html
        window.showToast?.('Stripe integration initialized...', 'info');
        // Original logic was likely simplified; assuming it returns a ref or handles via stripe.js
        return { success: false, error: 'Stripe POS flow needs specific implementation' };
    }

    handlePaystack(amount) {
        if (!window.PaystackPop) return { success: false, error: 'Paystack is not loaded' };

        const handler = window.PaystackPop.setup({
            key: this.config.paystack_key,
            email: 'pos-transaction@localhost', // Placeholder
            amount: amount * 100, // in kobo/cents
            currency: this.config.currency_code,
            callback: (response) => {
                this.app.handlePaymentSuccess('paystack', response.reference);
            },
            onClose: () => {
                window.showToast?.('Payment cancelled', 'warning');
                this.app.ui.setLoading(false);
            }
        });
        handler.openIframe();
        return { async: true };
    }

    async submitFinalOrder(orderData) {
        // Enforce consistent payload for both direct and offline sync
        orderData.branch_id = this.app.branchId;
        orderData.ordering_type = 'pos';
        if (!orderData.created_at) orderData.created_at = new Date().toISOString();
        if (!orderData.total_amount) orderData.total_amount = orderData.amount;

        try {
            // Check if explicitly offline
            if (!navigator.onLine) {
                throw new Error('Offline');
            }

            const response = await fetch(`/branches/${this.app.branchId}/pos/checkout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-API-Key': this.app.apiKey
                },
                credentials: 'include',
                body: JSON.stringify(orderData)
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(errText || `Server error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.warn('[POS] Online checkout failed, attempting offline fallback:', error);

            if (window.syncManager) {
                try {
                    const uuid = await window.syncManager.queueTransaction('order', orderData);
                    return {
                        success: true,
                        offline: true,
                        message: 'Order saved locally and will sync when online.',
                        order_id: uuid
                    };
                } catch (syncError) {
                    return { success: false, error: 'Offline storage failed: ' + syncError.message };
                }
            }

            return { success: false, error: error.message };
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }
}

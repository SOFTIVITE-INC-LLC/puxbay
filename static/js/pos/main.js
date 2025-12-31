import { CartManager } from './cart.js';
import { UIManager } from './ui.js';
import { PaymentHandler } from './payments.js';

class POSApp {
    constructor(config) {
        this.branchId = config.branchId;
        this.products = config.products;
        this.customers = config.customers;
        this.categories = config.categories;
        this.paymentConfig = config.paymentConfig;
        this.apiKey = config.apiKey;
        this.currency = config.currency;

        this.selectedCategory = 'all';
        this.searchQuery = '';
        this.selectedCustomerId = null;
        this.paymentMethod = 'cash';
        this.giftCardCode = null;
        this.splitPayments = [];

        // Managers
        this.cart = new CartManager(this);
        this.ui = new UIManager(this);
        this.payments = new PaymentHandler(this, this.paymentConfig);
        this.lastOrderId = null;
        this.currPin = "";
        this.currentUser = null;

        this.init();
    }

    async init() {
        this.ui.setLoading(true, 'Syncing latest data...');

        // Cache data for offline
        if (window.syncManager && navigator.onLine) {
            try {
                await window.posDB.init();
                await window.syncManager.fetchAndCache(this.branchId);
            } catch (error) {
                console.error('[POS] Sync failed:', error);
            }
        }

        // Load offline data if needed
        if (!navigator.onLine && window.posDB) {
            await this.loadOfflineData();
        }

        this.ui.setLoading(false);
        this.render();
        this.attachEventListeners();

        // Start with PIN login
        this.showPinModal();

        // Session persistence check - detect if session is lost
        this.startSessionMonitoring();
    }

    startSessionMonitoring() {
        console.log('[POS] Starting session monitoring...');

        // Check session every 30 seconds
        setInterval(async () => {
            try {
                // Use a lightweight endpoint to check session
                const response = await fetch(`/branches/${this.branchId}/pos/checkout/`, {
                    method: 'HEAD',
                    headers: { 'X-API-Key': this.apiKey },
                    credentials: 'include'
                });

                if (response.status === 401) {
                    console.error('[POS] ⚠️ Session lost detected (401 Unauthorized)');
                    window.showToast?.('Session expired. Please refresh the page.', 'error');
                } else if (response.ok || response.status === 405) {
                    // 405 is expected for HEAD request, means endpoint is reachable
                    console.log('[POS] ✓ Session check passed');
                }
            } catch (error) {
                console.warn('[POS] Session check failed:', error);
            }
        }, 30000);
    }

    async loadOfflineData() {
        try {
            await window.posDB.init();
            const cached = await window.posDB.getByIndex('products', 'branch_id', this.branchId);
            if (cached?.length) this.products = cached.map(p => ({ ...p, stock: p.stock_quantity }));
        } catch (e) {
            console.error('Offline load failed', e);
        }
    }

    attachEventListeners() {
        document.getElementById('search-input')?.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            this.render();
        });

        document.querySelectorAll('.payment-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const method = e.currentTarget.dataset.paymentMethod;
                this.setPaymentMethod(method);
            });
        });

        document.getElementById('checkout-btn')?.addEventListener('click', () => this.processCheckout());
        document.getElementById('clear-cart-btn')?.addEventListener('click', () => this.cart.clear());

        // Hardware Bridge Listeners
        document.getElementById('printer-config-btn')?.addEventListener('click', () => {
            document.getElementById('hardware-modal')?.classList.remove('hidden');
        });

        document.getElementById('pair-printer-btn')?.addEventListener('click', async () => {
            if (window.hardwareBridge) {
                const success = await window.hardwareBridge.connectPrinter();
                if (success) {
                    document.getElementById('printer-name').textContent = window.hardwareBridge.device.productName;
                    window.showToast?.('Printer connected successfully', 'success');
                } else {
                    window.showToast?.('Failed to connect printer', 'error');
                }
            }
        });

        document.getElementById('switch-user-btn')?.addEventListener('click', () => this.showPinModal());
    }

    showPinModal() {
        this.currPin = "";
        this.updatePinDots();
        document.getElementById('pin-login-modal')?.classList.remove('hidden');
        document.getElementById('pin-login-error').textContent = "";
    }

    handlePinInput(num) {
        if (this.currPin.length < 6) {
            this.currPin += num;
            this.updatePinDots();
            if (this.currPin.length >= 4) {
                // Auto-submit after 4 digits if it's a common PIN length, 
                // but let's allow up to 6. Maybe a submit button or just delay?
                // For "fast access", we'll try to submit at 4 and wait for more if it fails?
                // No, let's use a timeout or just wait for 4 or 6.
                if (this.currPin.length === 4 || this.currPin.length === 6) {
                    this.submitPin();
                }
            }
        }
    }

    updatePinDots() {
        for (let i = 1; i <= 6; i++) {
            const dot = document.getElementById(`pin-dot-${i}`);
            if (!dot) continue;
            if (i <= this.currPin.length) {
                dot.classList.add('bg-blue-600', 'border-blue-600', 'scale-110');
                dot.classList.remove('border-slate-300', 'dark:border-slate-600');
            } else {
                dot.classList.remove('bg-blue-600', 'border-blue-600', 'scale-110');
                dot.classList.add('border-slate-300', 'dark:border-slate-600');
            }
        }
    }

    clearPin() {
        this.currPin = "";
        this.updatePinDots();
    }

    deletePin() {
        this.currPin = this.currPin.slice(0, -1);
        this.updatePinDots();
    }

    async submitPin() {
        const pin = this.currPin;
        const errorEl = document.getElementById('pin-login-error');

        try {
            const response = await fetch('/api/v1/offline/pin-login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({ pin: pin })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                // Store tokens if needed for further API calls
                localStorage.setItem('pos_access_token', data.access);

                document.getElementById('pin-login-modal')?.classList.add('hidden');
                window.showToast?.(`Welcome, ${data.user.name || data.user.username}`, 'success');

                // Update UI with staff name
                const staffNameEl = document.getElementById('selected-staff-name');
                if (staffNameEl) staffNameEl.textContent = data.user.name || data.user.username;
            } else {
                if (this.currPin.length >= 6) {
                    errorEl.textContent = data.error || 'Invalid PIN';
                    this.clearPin();
                }
            }
        } catch (error) {
            console.error('[Auth] PIN login failed:', error);
            errorEl.textContent = "Connection error";
        }
    }

    setPaymentMethod(method) {
        this.paymentMethod = method;
        document.querySelectorAll('.payment-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.paymentMethod === method);
        });

        if (method === 'gift_card' && this.paymentMethod !== 'split') {
            document.getElementById('gift-card-modal')?.classList.remove('hidden');
        } else if (method === 'split') {
            this.openSplitModal();
        }
    }

    openSplitModal() {
        if (!this.cart.items.length) {
            window.showToast?.('Add items to cart first', 'warning');
            this.setPaymentMethod('cash');
            return;
        }

        // Default to two lines if empty, or keep existing
        if (!this.splitPayments.length) {
            this.splitPayments = [
                { method: 'cash', amount: this.cart.total / 2 },
                { method: 'card', amount: this.cart.total / 2 }
            ];
        }

        document.getElementById('split-total-due').textContent = `${this.currency}${this.cart.total.toFixed(2)}`;
        document.getElementById('split-payment-modal')?.classList.remove('hidden');
        this.renderSplitPayments();
    }

    renderSplitPayments() {
        const list = document.getElementById('split-payment-list');
        if (!list) return;

        list.innerHTML = this.splitPayments.map((p, index) => `
            <div class="flex flex-col gap-2 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
                <div class="flex items-center gap-3">
                    <select onchange="posApp.updateSplitLine(${index}, 'method', this.value)" class="flex-1 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg p-2 text-sm dark:text-white">
                        <option value="cash" ${p.method === 'cash' ? 'selected' : ''}>Cash</option>
                        <option value="card" ${p.method === 'card' ? 'selected' : ''}>Card</option>
                        <option value="gift_card" ${p.method === 'gift_card' ? 'selected' : ''}>Gift Card</option>
                        <option value="store_credit" ${p.method === 'store_credit' ? 'selected' : ''}>Store Credit</option>
                        <option value="loyalty_points" ${p.method === 'loyalty_points' ? 'selected' : ''}>Loyalty Points</option>
                    </select>
                    <div class="relative w-32">
                        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">${this.currency}</span>
                        <input type="number" step="0.01" value="${p.amount.toFixed(2)}" 
                               oninput="posApp.updateSplitLine(${index}, 'amount', this.value)" 
                               class="w-full bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg p-2 pl-6 text-sm text-right font-bold dark:text-white">
                    </div>
                    <button onclick="posApp.removeSplitLine(${index})" class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                </div>
                ${p.method === 'gift_card' ? `
                    <input type="text" placeholder="Enter Gift Card Code" value="${p.gift_card_code || ''}" 
                           oninput="posApp.updateSplitLine(${index}, 'gift_card_code', this.value)"
                           class="w-full bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg p-2 text-sm uppercase dark:text-white">
                ` : ''}
            </div>
        `).join('');

        this.updateSplitRemaining();
    }

    addSplitLine() {
        const remaining = this.calculateSplitRemainingValue();
        this.splitPayments.push({ method: 'cash', amount: Math.max(0, remaining) });
        this.renderSplitPayments();
    }

    removeSplitLine(index) {
        this.splitPayments.splice(index, 1);
        this.renderSplitPayments();
    }

    updateSplitLine(index, field, value) {
        if (field === 'amount') value = parseFloat(value) || 0;
        this.splitPayments[index][field] = value;
        if (field === 'method') this.renderSplitPayments(); // Re-render to show/hide GC code input
        else this.updateSplitRemaining();
    }

    calculateSplitRemainingValue() {
        const totalPaid = this.splitPayments.reduce((sum, p) => sum + p.amount, 0);
        return this.cart.total - totalPaid;
    }

    updateSplitRemaining() {
        const remaining = this.calculateSplitRemainingValue();
        const el = document.getElementById('split-remaining-amount');
        if (el) {
            el.textContent = `${this.currency}${remaining.toFixed(2)}`;
            el.classList.toggle('text-red-500', remaining > 0.01);
            el.classList.toggle('text-emerald-500', remaining <= 0.01);
        }

        const confirmBtn = document.getElementById('confirm-split-btn');
        if (confirmBtn) confirmBtn.disabled = (remaining > 0.01);
    }

    confirmSplit() {
        document.getElementById('split-payment-modal')?.classList.add('hidden');
        window.showToast?.('Split payments configured', 'success');
    }

    confirmGiftCard() {
        const input = document.getElementById('gift-card-code-input');
        this.giftCardCode = input?.value;
        document.getElementById('gift-card-modal')?.classList.add('hidden');
        window.showToast?.('Gift Card applied', 'success');
    }

    handleProductClick(productId) {
        const product = this.products.find(p => p.id == productId);
        if (product?.is_batch_tracked) {
            this.ui.showBatchModal(product);
        } else {
            this.cart.addItem(product);
        }
    }

    selectBatch(productId, batchId) {
        const product = this.products.find(p => p.id == productId);
        const batch = product?.batches?.find(b => b.id == batchId);
        if (product && batch) {
            this.cart.addItem(product, batch);
            document.getElementById('batch-modal')?.classList.add('hidden');
        }
    }

    get filteredProducts() {
        return this.products.filter(p => {
            const matches = p.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                p.sku.toLowerCase().includes(this.searchQuery.toLowerCase());
            if (this.selectedCategory === 'all') return matches;
            return matches && p.category_id == this.selectedCategory;
        });
    }

    async processCheckout() {
        if (!this.cart.items.length) return window.showToast?.('Cart is empty', 'warning');

        this.ui.setLoading(true, 'Processing payment...');

        const extraData = {};
        if (this.paymentMethod === 'split') {
            extraData.payments = this.splitPayments;
        }

        const result = await this.payments.processCheckout(
            this.cart.total,
            this.cart.items,
            this.selectedCustomerId,
            this.paymentMethod,
            this.giftCardCode,
            extraData
        );

        if (result.async) return; // Flow handled by payment provider callback

        this.handleCheckoutResult(result);
    }

    openIssueGiftCardModal() {
        document.getElementById('issue-gc-amount').value = "";
        document.getElementById('issue-gc-code').value = "";
        document.getElementById('issue-gift-card-modal')?.classList.remove('hidden');
    }

    generateGCCode() {
        const code = 'GC-' + Math.random().toString(36).substring(2, 10).toUpperCase();
        document.getElementById('issue-gc-code').value = code;
    }

    addToCartGiftCard() {
        const amountInput = document.getElementById('issue-gc-amount');
        const codeInput = document.getElementById('issue-gc-code');
        const amount = parseFloat(amountInput.value);
        const code = codeInput.value;

        if (!amount || amount <= 0) {
            return window.showToast?.('Enter a valid amount', 'warning');
        }

        this.cart.addSpecialItem({
            type: 'gift_card',
            name: `Gift Card (${code || 'Auto-Gen'})`,
            price: amount,
            gc_code: code
        });

        document.getElementById('issue-gift-card-modal')?.classList.add('hidden');
        window.showToast?.('Gift Card added to cart', 'success');
    }

    handlePaymentSuccess(method, reference) {
        this.payments.submitFinalOrder({
            amount: this.cart.total,
            items: this.cart.items,
            customer_id: this.selectedCustomerId,
            payment_method: method,
            payment_ref: reference
        }).then(result => this.handleCheckoutResult(result));
    }

    handleCheckoutResult(result) {
        this.ui.setLoading(false);
        if (result.success) {
            this.lastOrderId = result.order_id;
            this.ui.showSuccessModal();
            this.cart.clear();
        } else {
            window.showToast?.(result.error || 'Checkout failed', 'error');
        }
    }

    async printReceipt(orderId) {
        // If hardware bridge is connected, use it for direct printing
        if (window.hardwareBridge && window.hardwareBridge.device) {
            try {
                // Fetch receipt data if not already fully available
                // In this simplified version, we'll try to reconstruct from cart or just notify
                console.log('[POS] Direct printing via Hardware Bridge for order:', orderId);

                const receiptData = {
                    tenant_name: document.querySelector('h1').textContent,
                    branch_name: 'Main Branch',
                    items: this.cart.items.map(item => ({ name: item.name, price: item.price.toFixed(2) })),
                    total: this.cart.total.toFixed(2)
                };

                await window.hardwareBridge.printReceipt(receiptData);
                window.showToast?.('Receipt printed successfully', 'success');
                return;
            } catch (error) {
                console.error('[POS] Direct printing failed:', error);
                window.showToast?.('Direct print failed, opening browser print', 'warning');
            }
        }

        // Fallback to standard browser print
        const id = orderId || this.lastOrderId;
        if (!id) {
            window.showToast?.('No transaction ID found to print', 'error');
            return;
        }
        const url = `/branches/${this.branchId}/transactions/${id}/receipt/`;
        window.open(url, 'Receipt', 'width=400,height=600');
    }

    startNewSale() {
        this.ui.hideSuccessModal();
        this.render();
    }

    render() {
        this.ui.renderProducts(this.filteredProducts, this.currency);
        this.renderCart();
    }

    async fetchRecommendations() {
        if (!this.cart.items.length) {
            document.getElementById('smart-suggestions-panel')?.classList.add('hidden');
            return;
        }

        const productIds = [...new Set(this.cart.items.map(item => item.id))].join(',');

        try {
            const response = await fetch(`/api/v1/intelligence/pos-recommendations/?product_ids=${productIds}`, {
                headers: {
                    'X-API-Key': this.apiKey
                },
                credentials: 'include'
            });

            if (response.status === 401) {
                console.warn('[POS] Session expired or unauthorized');
                // Could trigger a re-login modal here
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.recommendations && data.recommendations.length > 0) {
                this.renderRecommendations(data.recommendations);
                document.getElementById('smart-suggestions-panel')?.classList.remove('hidden');
            } else {
                document.getElementById('smart-suggestions-panel')?.classList.add('hidden');
            }
        } catch (error) {
            console.error('[POS] Failed to fetch recommendations:', error);
            document.getElementById('smart-suggestions-panel')?.classList.add('hidden');
        }
    }

    renderRecommendations(recoms) {
        const list = document.getElementById('suggestions-list');
        if (!list) return;

        list.innerHTML = recoms.map(r => `
            <div onclick="posApp.handleProductClick('${r.id}')" class="flex-none w-32 bg-white dark:bg-slate-800 p-2 rounded-xl border border-blue-100 dark:border-blue-900 shadow-sm cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-all transform hover:-translate-y-1 active:scale-95 group">
                <div class="aspect-square bg-slate-50 dark:bg-slate-900 rounded-lg mb-2 overflow-hidden flex items-center justify-center p-2">
                    <img src="${r.image_url || '/static/images/placeholder.png'}" class="w-full h-full object-contain group-hover:scale-110 transition-transform">
                </div>
                <h5 class="text-[10px] font-bold text-slate-800 dark:text-white truncate mb-0.5">${r.name}</h5>
                <div class="text-[10px] font-black text-blue-600 dark:text-blue-400">${this.currency}${r.price.toFixed(2)}</div>
            </div>
        `).join('');
    }

    renderCart() {
        const container = document.getElementById('cart-container');
        const list = document.getElementById('cart-items-list') || document.createElement('div');
        list.id = 'cart-items-list';
        list.className = 'space-y-3';

        if (!this.cart.items.length) {
            container.innerHTML = `
                <div id="cart-empty" class="h-full flex flex-col items-center justify-center text-slate-400 space-y-3">
                    <div class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center">
                        <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                    </div>
                    <p class="text-sm">Your cart is empty</p>
                </div>
            `;
            document.getElementById('cart-subtotal').textContent = `${this.currency}0.00`;
            document.getElementById('cart-total').textContent = `0.00`;
            document.getElementById('clear-cart-btn').classList.add('hidden');

            // Still fetch recommendations (it will hide the panel)
            this.fetchRecommendations();
            return;
        }

        container.innerHTML = '';
        container.appendChild(list);
        list.innerHTML = this.cart.items.map(item => `
            <div class="flex items-center justify-between gap-3 p-3 bg-white dark:bg-slate-700/50 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm">
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-semibold text-slate-800 dark:text-white truncate">${item.name}</h4>
                    <div class="text-xs text-slate-500">${this.currency}${item.price.toFixed(2)} ${item.batchNumber ? '• ' + item.batchNumber : ''}</div>
                </div>
                <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 rounded-lg p-1">
                    <button onclick="posApp.cart.updateQuantity('${item.cartItemId}', -1)" class="w-7 h-7 flex items-center justify-center rounded-md hover:bg-white hover:shadow-sm text-slate-600 transition-all">-</button>
                    <span class="text-sm font-bold w-6 text-center">${item.quantity}</span>
                    <button onclick="posApp.cart.updateQuantity('${item.cartItemId}', 1)" class="w-7 h-7 flex items-center justify-center rounded-md hover:bg-white hover:shadow-sm text-slate-600 transition-all">+</button>
                </div>
                <button onclick="posApp.cart.remove('${item.cartItemId}')" class="text-slate-300 hover:text-red-500 transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
            </div>
        `).join('');

        document.getElementById('cart-subtotal').textContent = `${this.currency}${this.cart.subtotal.toFixed(2)}`;
        document.getElementById('cart-total').textContent = this.cart.total.toFixed(2);
        document.getElementById('clear-cart-btn').classList.remove('hidden');

        // At the end of renderCart, fetch recommendations
        this.fetchRecommendations();
    }
}

export const initPOS = (config) => {
    window.posApp = new POSApp(config);
};

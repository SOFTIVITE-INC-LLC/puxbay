import { createApp, reactive, computed, onMounted } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';
import { PaymentHandler } from './payments.js';

export function initVuePOS(config) {
    const app = createApp({
        setup() {
            const state = reactive({
                branchId: config.branchId,
                apiKey: config.apiKey,
                posDataUrl: config.posDataUrl,
                currency: config.currency,
                products: config.products || [],
                customers: config.customers || [],
                categories: config.categories || [],
                currentUser: config.currentUser,

                selectedCategory: 'all',
                searchQuery: '',
                customerSearch: '',
                showCustomerDropdown: false,
                selectedCustomerId: null,
                paymentMethod: 'cash',
                giftCardCode: null,
                momoNetwork: '',
                momoPhone: '',

                cart: [],
                splitPayments: [],

                loading: true,
                loadingMessage: 'Initializing POS...',
                lastOrderId: null,

                recommendations: [],

                // Modal States
                activeModal: null, // 'gift_card', 'batch', 'split', 'issue_gift_card', 'hardware', 'success'
                batchProduct: null,

                // PIN Login
                pin: '',
                pinError: '',
                isStaffLoggedIn: false,

                // Hardware status
                printerName: 'Not connected',
                connectionStatus: 'Online',

                // Mobile POS
                showMobileCart: false,
                isLargeScreen: window.innerWidth >= 1024
            });

            // --- Computed Properties ---
            const filteredProducts = computed(() => {
                return state.products.filter(p => {
                    const q = state.searchQuery.toLowerCase();
                    const nameMatch = p.name && p.name.toLowerCase().includes(q);
                    const skuMatch = p.sku && p.sku.toLowerCase().includes(q);
                    const matches = nameMatch || skuMatch;

                    if (state.selectedCategory === 'all') return matches;
                    return matches && p.category_id == state.selectedCategory;
                });
            });

            const cartSubtotal = computed(() => {
                return state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            });

            const cartTotal = computed(() => {
                // Currently same as subtotal, but can incorporate tax/discounts later
                return cartSubtotal.value;
            });

            const selectedCustomer = computed(() => {
                if (!state.selectedCustomerId) return { name: 'Walk-in Customer' };
                return state.customers.find(c => c.id == state.selectedCustomerId) || { name: 'Walk-in Customer' };
            });

            const filteredCustomers = computed(() => {
                if (!state.customerSearch) return state.customers;
                const q = state.customerSearch.toLowerCase();
                return state.customers.filter(c =>
                    c.name.toLowerCase().includes(q) ||
                    (c.phone && c.phone.includes(q))
                );
            });

            const splitRemaining = computed(() => {
                const paid = state.splitPayments.reduce((sum, p) => sum + p.amount, 0);
                return cartTotal.value - paid;
            });

            // --- Methods ---
            const selectCustomer = (customer) => {
                state.selectedCustomerId = customer.id;
                state.showCustomerDropdown = false;
                window.showToast?.(`Customer ${customer.name} selected`, 'success');
            };

            const handleProductClick = (product) => {
                if (product.is_batch_tracked) {
                    // Logic for showing batch modal (can be refactored into Vue later or bridged)
                    window.posApp?.ui?.showBatchModal(product);
                } else {
                    addToCart(product);
                }
            };

            const addToCart = (product, batch = null) => {
                const cartItemId = batch ? `${product.id}-${batch.id}` : product.id;
                const existing = state.cart.find(item => item.cartItemId === cartItemId);

                if (existing) {
                    existing.quantity++;
                } else {
                    state.cart.push({
                        cartItemId,
                        id: product.id,
                        name: product.name,
                        price: product.price,
                        quantity: 1,
                        batchId: batch?.id,
                        batchNumber: batch?.batch_number
                    });
                }
                fetchRecommendations();
            };

            const updateQuantity = (cartItemId, delta) => {
                const item = state.cart.find(i => i.cartItemId === cartItemId);
                if (item) {
                    item.quantity += delta;
                    if (item.quantity <= 0) {
                        removeFromCart(cartItemId);
                    }
                }
                fetchRecommendations();
            };

            const removeFromCart = (cartItemId) => {
                state.cart = state.cart.filter(i => i.cartItemId !== cartItemId);
                fetchRecommendations();
            };

            const clearCart = () => {
                state.cart = [];
                state.recommendations = [];
            };

            const toggleMobileCart = () => {
                state.showMobileCart = !state.showMobileCart;
            };

            let recommendationTimeout = null;
            const fetchRecommendations = async () => {
                // Debounce to prevent rapid repeated calls
                if (recommendationTimeout) {
                    clearTimeout(recommendationTimeout);
                }

                recommendationTimeout = setTimeout(async () => {
                    // Prevent concurrent requests during checkout/loading
                    if (state.loading) return;

                    if (!state.cart.length) {
                        state.recommendations = [];
                        return;
                    }
                    const productIds = [...new Set(state.cart.map(item => item.id))].join(',');
                    try {
                        const response = await fetch(`/api/v1/intelligence/pos-recommendations/?product_ids=${productIds}`, {
                            headers: { 'X-API-Key': state.apiKey },
                            credentials: 'include'
                        });
                        const data = await response.json();
                        state.recommendations = data.recommendations || [];
                    } catch (error) {
                        console.error('[Vue POS] Recommendations failed:', error);
                    }
                }, 300); // Wait 300ms before making the request
            };

            const setPaymentMethod = (method) => {
                state.paymentMethod = method;
                if (method === 'gift_card') {
                    state.activeModal = 'gift_card';
                } else if (method === 'split') {
                    openSplitModal();
                } else if (method === 'mobile') {
                    state.activeModal = 'mobile_money';
                }
            };

            const openSplitModal = () => {
                if (!state.cart.length) {
                    window.showToast?.('Add items to cart first', 'warning');
                    state.paymentMethod = 'cash';
                    return;
                }
                if (!state.splitPayments.length) {
                    state.splitPayments = [
                        { method: 'cash', amount: cartTotal.value / 2 },
                        { method: 'card', amount: cartTotal.value / 2 }
                    ];
                }
                document.getElementById('split-payment-modal')?.classList.remove('hidden');
                state.activeModal = 'split';
            };

            const processCheckout = async () => {
                if (!state.cart.length) return window.showToast?.('Cart is empty', 'warning');

                state.loading = true;
                state.loadingMessage = 'Processing payment...';
                state.showMobileCart = false; // Hide mobile cart during checkout

                const payments = new PaymentHandler(state, config.paymentConfig);
                const extraData = {};
                if (state.paymentMethod === 'split') {
                    extraData.payments = state.splitPayments;
                } else if (state.paymentMethod === 'mobile') {
                    extraData.mobile_money = {
                        network: state.momoNetwork,
                        phone: state.momoPhone
                    };
                }

                try {
                    const result = await payments.processCheckout(
                        cartTotal.value,
                        state.cart,
                        state.selectedCustomerId,
                        state.paymentMethod,
                        state.giftCardCode,
                        extraData
                    );

                    if (result.async) return;
                    handleCheckoutResult(result);
                } catch (error) {
                    window.showToast?.(error.message || 'Payment failed', 'error');
                    state.loading = false;
                }
            };

            const handleCheckoutResult = (result) => {
                state.loading = false;
                if (result.success) {
                    state.lastOrderId = result.order_id;
                    state.activeModal = 'success';
                    clearCart();
                    // Auto-print receipt
                    setTimeout(printReceipt, 500);
                } else {
                    window.showToast?.(result.error || 'Checkout failed', 'error');
                }
            };

            const closeModal = () => {
                state.activeModal = null;
            };

            const openModal = (name) => {
                console.log('[Vue POS] Opening modal:', name);
                state.activeModal = name;
            };

            const handlePinInput = (digit) => {
                if (state.pin.length < 6) {
                    state.pin += digit;
                    state.pinError = '';
                }
            };

            const validatePin = async () => {
                if (state.pin.length < 4) {
                    state.pinError = 'PIN must be 4-6 digits';
                    return;
                }

                state.loading = true;
                state.loadingMessage = 'Validating PIN...';

                try {
                    const response = await fetch(`/branches/${state.branchId}/pos/validate-pin/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-Key': state.apiKey
                        },
                        body: JSON.stringify({ pin: state.pin })
                    });

                    const result = await response.json();

                    if (result.success) {
                        state.currentUser = result.user;
                        if (result.api_key) {
                            state.apiKey = result.api_key;
                        }
                        state.isStaffLoggedIn = true;
                        state.pin = '';
                        state.pinError = '';
                        closeModal();
                        window.showToast?.(`Logged in as ${result.user.name}`, 'success');
                    } else {
                        state.pin = '';
                        state.pinError = result.error || 'Invalid PIN';
                    }
                } catch (error) {
                    console.error('[Vue POS] PIN validation failed:', error);
                    state.pinError = 'Validation failed. Check connection.';
                } finally {
                    state.loading = false;
                }
            };

            const deletePin = () => {
                state.pin = state.pin.slice(0, -1);
            };

            const clearPin = () => {
                state.pin = '';
            };

            const printReceipt = () => {
                if (!state.lastOrderId) {
                    window.showToast?.('No transaction found to print.', 'warning');
                    return;
                }

                const receiptUrl = `/branches/${state.branchId}/transactions/${state.lastOrderId}/receipt/`;
                console.log('[Vue POS] 🖨️ printReceipt called');
                console.log('[Vue POS] Receipt URL:', receiptUrl);

                // Use the hidden iframe for printing
                const printFrame = document.getElementById('receipt-print-frame');
                console.log('[Vue POS] Print frame found:', !!printFrame);

                if (printFrame) {
                    // Set onload handler to trigger print once loaded
                    printFrame.onload = function () {
                        console.log('[Vue POS] Iframe loaded. content:', printFrame.contentWindow.location.href);
                        // Wait a tiny bit for rendering then print
                        setTimeout(() => {
                            try {
                                console.log('[Vue POS] Triggering print()...');
                                printFrame.contentWindow.focus();
                                printFrame.contentWindow.print();
                            } catch (e) {
                                console.error('[Vue POS] Print error:', e);
                                window.open(receiptUrl, '_blank');
                            }
                        }, 500);
                    };
                    printFrame.src = receiptUrl;
                } else {
                    console.warn('[Vue POS] Iframe missing, falling back to window.open');
                    // Fallback if iframe missing
                    window.open(receiptUrl, '_blank');
                }
            };

            const toggleTheme = () => {
                const isDark = document.documentElement.classList.toggle('dark');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
                state.theme = isDark ? 'dark' : 'light';
            };

            const toggleKiosk = () => {
                const container = document.getElementById('pos-container');
                const isKiosk = container.classList.toggle('kiosk-mode');
                const text = document.getElementById('kiosk-status-text');
                if (text) text.innerText = isKiosk ? 'Kiosk' : 'Mobile';
            };

            const syncInventory = async () => {
                if (window.posDB && window.syncManager) {
                    state.loading = true;
                    state.loadingMessage = 'Syncing inventory...';
                    try {
                        await window.posDB.init();
                        await window.syncManager.syncInventory(state.branchId);
                        window.showToast?.('Inventory synced', 'success');
                    } catch (e) {
                        window.showToast?.('Sync failed: ' + e.message, 'error');
                    } finally {
                        state.loading = false;
                    }
                }
            };

            const toggleFullscreen = () => {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
            };

            const loadData = async () => {
                if (!state.posDataUrl) return;

                // Only fetch if data is missing or we explicitly want to refresh
                if (state.products.length > 0 && state.customers.length > 0) {
                    state.loading = false;
                    return;
                }

                state.loading = true;
                state.loadingMessage = 'Hydrating POS data...';

                try {
                    const response = await fetch(state.posDataUrl, {
                        headers: {
                            'X-API-Key': state.apiKey,
                            'Accept': 'application/json'
                        },
                        credentials: 'include'
                    });

                    if (!response.ok) throw new Error('Failed to fetch POS data');

                    const result = await response.json();

                    // The standardized API returns { status, data: { products, ... }, ... }
                    const data = result.data || result;

                    state.products = data.products || [];
                    state.customers = data.customers || [];
                    state.categories = data.categories || [];

                    console.log(`[Vue POS] Hydrated ${state.products.length} products, ${state.customers.length} customers`);
                } catch (error) {
                    console.error('[Vue POS] Data hydration failed:', error);
                    window.showToast?.('Failed to load POS data. Working offline if available.', 'warning');
                } finally {
                    state.loading = false;
                }
            };

            // --- Lifecycle Hooks ---
            onMounted(() => {
                console.log('[Vue POS] Mounted');

                // Load data asynchronously
                loadData();

                // Detect initial theme
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                    document.documentElement.classList.add('dark');
                }

                window.addEventListener('resize', () => {
                    state.isLargeScreen = window.innerWidth >= 1024;
                });

                setTimeout(() => {
                    state.loading = false;
                }, 500);
            });

            return {
                state,
                filteredProducts,
                filteredCustomers,
                cartSubtotal,
                cartTotal,
                selectedCustomer,
                splitRemaining,
                selectCustomer,
                handleProductClick,
                addToCart,
                updateQuantity,
                removeFromCart,
                clearCart,
                toggleMobileCart,
                setPaymentMethod,
                processCheckout,
                toggleTheme,
                toggleKiosk,
                syncInventory,
                toggleFullscreen,
                closeModal,
                openModal,
                handlePinInput,
                deletePin,
                clearPin,
                printReceipt,
                validatePin
            };
        }
    });

    app.mount('#pos-container');
    return app;
}

export class UIManager {
    constructor(app) {
        this.app = app;
        this.initTheme();
        this.initKioskMode();
    }

    initTheme() {
        const savedTheme = localStorage.getItem('pos-theme') || 'light';
        this.applyTheme(savedTheme);
        document.getElementById('theme-toggle-btn')?.addEventListener('click', () => this.toggleTheme());
    }

    toggleTheme() {
        const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        localStorage.setItem('pos-theme', newTheme);
    }

    applyTheme(theme) {
        const sunIcon = document.getElementById('theme-sun-icon');
        const moonIcon = document.getElementById('theme-moon-icon');
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            sunIcon?.classList.remove('hidden');
            moonIcon?.classList.add('hidden');
        } else {
            document.documentElement.classList.remove('dark');
            sunIcon?.classList.add('hidden');
            moonIcon?.classList.remove('hidden');
        }
    }

    initKioskMode() {
        this.kioskMode = localStorage.getItem('kioskMode') === 'true';
        this.updateKioskUI();
        document.getElementById('kiosk-toggle-btn')?.addEventListener('click', () => {
            this.kioskMode = !this.kioskMode;
            localStorage.setItem('kioskMode', this.kioskMode);
            this.updateKioskUI();
        });
    }

    updateKioskUI() {
        const container = document.getElementById('pos-container');
        const statusText = document.getElementById('kiosk-status-text');
        if (this.kioskMode) {
            container?.classList.add('kiosk-mode');
            if (statusText) statusText.textContent = 'Kiosk On';
        } else {
            container?.classList.remove('kiosk-mode');
            if (statusText) statusText.textContent = 'Mobile';
        }
        document.querySelectorAll('[data-kiosk-class]').forEach(el => {
            const classes = el.dataset.kioskClass.split(' ');
            if (this.kioskMode) el.classList.add(...classes);
            else el.classList.remove(...classes);
        });
    }

    renderProducts(products, currency) {
        const grid = document.getElementById('product-grid');
        const emptyState = document.getElementById('empty-products');
        if (!grid) return;

        if (products.length === 0) {
            grid.innerHTML = '';
            emptyState?.classList.remove('hidden');
            return;
        }

        emptyState?.classList.add('hidden');
        grid.innerHTML = products.map(product => {
            const price = parseFloat(product.price).toFixed(2);
            const colors = ['bg-blue-100 text-blue-600', 'bg-emerald-100 text-emerald-600', 'bg-violet-100 text-violet-600', 'bg-amber-100 text-amber-600', 'bg-rose-100 text-rose-600'];
            const colorClass = colors[this.getStringHash(product.id) % colors.length];
            const initial = product.name.charAt(0).toUpperCase();

            return `
            <div onclick="posApp.handleProductClick('${product.id}')" class="group bg-white rounded-2xl border border-slate-200 p-4 cursor-pointer hover:border-blue-400 hover:shadow-lg transition-all duration-200 flex flex-col items-center text-center h-full active:scale-[0.98]">
                <div class="w-16 h-16 rounded-2xl mb-3 ${colorClass} flex items-center justify-center text-2xl font-bold mb-3 shadow-inner">
                    ${initial}
                </div>
                <h3 class="font-semibold text-slate-800 line-clamp-2 text-sm mb-1 min-h-[2.5em] flex items-center justify-center w-full">${product.name}</h3>
                <div class="mt-auto pt-2 w-full">
                    <div class="text-lg font-bold text-slate-900">${currency}${price}</div>
                    <div class="text-xs text-slate-500 font-medium">Stock: ${product.stock}</div>
                </div>
            </div>
            `;
        }).join('');
    }

    getStringHash(str) {
        let hash = 0;
        const string = String(str || '');
        for (let i = 0; i < string.length; i++) {
            hash = ((hash << 5) - hash) + string.charCodeAt(i);
            hash = hash & hash;
        }
        return Math.abs(hash);
    }

    showBatchModal(product) {
        const modal = document.getElementById('batch-modal');
        const title = document.getElementById('batch-modal-product-name');
        const list = document.getElementById('batch-list');
        if (title) title.textContent = product.name;
        modal?.classList.remove('hidden');

        if (list) {
            if (!product.batches || product.batches.length === 0) {
                list.innerHTML = `<div class="p-4 text-center text-sm text-red-500">No active batches available.</div>`;
                return;
            }
            list.innerHTML = product.batches.map(batch => `
                <div onclick="posApp.selectBatch('${product.id}', '${batch.id}')" class="p-3 hover:bg-slate-50 cursor-pointer transition-colors flex justify-between items-center group">
                    <div>
                        <div class="font-medium text-slate-900 group-hover:text-blue-600">${batch.batch_number}</div>
                        <div class="text-xs text-slate-500">Exp: ${batch.expiry || 'N/A'}</div>
                    </div>
                    <div class="text-sm font-bold text-slate-700">Qty: ${batch.quantity}</div>
                </div>
            `).join('');
        }
    }

    setLoading(isLoading, message = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const msgEl = document.getElementById('loading-message');
        if (msgEl) msgEl.textContent = message;
        if (isLoading) overlay?.classList.replace('hidden', 'flex');
        else overlay?.classList.replace('flex', 'hidden');
    }

    showSuccessModal() {
        document.getElementById('success-modal')?.classList.remove('hidden');
    }

    hideSuccessModal() {
        document.getElementById('success-modal')?.classList.add('hidden');
    }
}

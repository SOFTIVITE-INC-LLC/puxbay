/**
 * UI Notifications - Lightweight Toast Library
 * Replaces native alert() with beautiful, responsive toasts.
 */
class UINotifications {
    constructor() {
        this.container = null;
        this.createContainer();
    }

    createContainer() {
        if (document.getElementById('toast-container')) return;

        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'fixed top-5 right-5 z-[9999] flex flex-col gap-3 pointer-events-none';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = 4000) {
        if (!this.container) this.createContainer();

        const toast = document.createElement('div');
        toast.className = `
            pointer-events-auto min-w-[300px] max-w-md p-4 rounded-xl shadow-2xl backdrop-blur-md border border-white/20
            flex items-center gap-3 transform transition-all duration-300 translate-x-full opacity-0
            ${this.getTypeStyles(type)}
        `;

        const icon = this.getIcon(type);

        toast.innerHTML = `
            <div class="flex-shrink-0">
                <span class="material-icons-round text-xl">${icon}</span>
            </div>
            <div class="flex-1 text-sm font-medium leading-tight text-white/90">
                ${message}
            </div>
            <button class="ml-2 text-white/60 hover:text-white transition-colors" onclick="this.parentElement.remove()">
                <span class="material-icons-round text-lg">close</span>
            </button>
        `;

        this.container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        });

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(toast);
            }, duration);
        }

        return toast;
    }

    // Alias for backward compatibility
    showToast(message, type = 'info', duration = 4000) {
        return this.show(message, type, duration);
    }

    dismiss(toast) {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 300);
    }

    getTypeStyles(type) {
        switch (type) {
            case 'success':
                return 'bg-green-600/90 shadow-green-500/20';
            case 'error':
                return 'bg-red-600/90 shadow-red-500/20';
            case 'warning':
                return 'bg-amber-500/90 shadow-amber-500/20';
            default:
                return 'bg-gray-800/90 shadow-gray-500/20';
        }
    }

    getIcon(type) {
        switch (type) {
            case 'success': return 'check_circle';
            case 'error': return 'error';
            case 'warning': return 'warning';
            default: return 'info';
        }
    }
}

// Global instance
window.uiNotifications = new UINotifications();
window.showToast = (msg, type, duration) => window.uiNotifications.show(msg, type, duration);

// Override native alert (optional, but safer to do explicitly in code)
// window.alert = (msg) => window.showToast(msg, 'info'); 

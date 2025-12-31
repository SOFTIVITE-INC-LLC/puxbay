/**
 * Dashboard Core JavaScript
 * Extracted from dashboard_base.html for maintainability
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Sidebar Logic ---
    const sidebar = document.getElementById('sidebar-menu');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');

    function toggleSidebar() {
        const isClosed = sidebar.classList.contains('-translate-x-full');
        if (isClosed) {
            sidebar.classList.remove('-translate-x-full');
            sidebar.classList.add('translate-x-0');
            if (sidebarOverlay) sidebarOverlay.style.display = 'block';
        } else {
            sidebar.classList.add('-translate-x-full');
            sidebar.classList.remove('translate-x-0');
            if (sidebarOverlay) sidebarOverlay.style.display = 'none';
        }
    }

    if (sidebarToggleBtn) sidebarToggleBtn.addEventListener('click', toggleSidebar);
    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);

    // --- Dark Mode Logic ---
    const themeToggleBtn = document.getElementById('dark-mode-toggle');

    function updateThemeUI(isDark) {
        const moonIcon = document.getElementById('icon-moon');
        const sunIcon = document.getElementById('icon-sun');

        if (isDark) {
            document.documentElement.classList.add('dark');
            if (moonIcon) moonIcon.style.display = 'none';
            if (sunIcon) sunIcon.style.display = 'block';
        } else {
            document.documentElement.classList.remove('dark');
            if (moonIcon) moonIcon.style.display = 'block';
            if (sunIcon) sunIcon.style.display = 'none';
        }
    }

    let isDarkMode = localStorage.getItem('darkMode') === 'true';
    updateThemeUI(isDarkMode);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            isDarkMode = !isDarkMode;
            localStorage.setItem('darkMode', isDarkMode);
            updateThemeUI(isDarkMode);
        });
    }

    // --- Notifications Dropdown ---
    const notifBtn = document.getElementById('notification-btn');
    const notifDropdown = document.getElementById('notification-dropdown');

    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = notifDropdown.style.display === 'none';
            notifDropdown.style.display = isHidden ? 'block' : 'none';
        });

        document.addEventListener('click', (e) => {
            if (!notifBtn.contains(e.target) && !notifDropdown.contains(e.target)) {
                notifDropdown.style.display = 'none';
            }
        });
    }

    // --- Network Status ---
    const networkStatusDiv = document.getElementById('network-status');

    function updateNetworkStatus() {
        if (!networkStatusDiv) return;
        const isOnline = navigator.onLine;

        if (isOnline) {
            networkStatusDiv.innerHTML = `
                <div class="flex items-center gap-2 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 px-3 py-1.5 rounded-full">
                    <span class="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full animate-pulse"></span>
                    <span>Online</span>
                </div>`;
        } else {
            networkStatusDiv.innerHTML = `
                <div class="flex items-center gap-2 bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 px-3 py-1.5 rounded-full">
                    <span class="w-2 h-2 bg-red-500 dark:bg-red-400 rounded-full"></span>
                    <span>Offline</span>
                </div>`;
        }
    }

    updateNetworkStatus();
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
});

// --- Toast Notification System ---
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
        error: '<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
        warning: '<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
        info: '<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };

    toast.innerHTML = `
        ${icons[type]}
        <span class="flex-1">${message}</span>
        <button onclick="this.parentElement.remove()" class="hover:opacity-75">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

window.showToast = showToast;

// --- Queue Count Monitor ---
async function updateQueueCount() {
    if (window.posDB) {
        try {
            const queue = await window.posDB.getSyncQueue();
            const queueStatus = document.getElementById('queue-status');
            const queueCount = document.getElementById('queue-count');

            if (queue.length > 0) {
                queueStatus.classList.remove('hidden');
                queueStatus.classList.add('flex');
                queueCount.textContent = `${queue.length} pending`;
            } else {
                queueStatus.classList.add('hidden');
                queueStatus.classList.remove('flex');
            }
        } catch (error) {
            console.error('[Queue] Failed to update count:', error);
        }
    }
}

setInterval(updateQueueCount, 5000);
setTimeout(updateQueueCount, 2000);

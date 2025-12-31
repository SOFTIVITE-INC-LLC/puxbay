/**
 * Real-time notification poller.
 * Polls the backend every 10 seconds for new notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
    const NOTIFICATION_API_URL = '/notifications/api/latest/';
    const POLL_INTERVAL = 10000; // 10 seconds

    // UI Elements (based on dashboard_base.html structure)
    // The button containing the SVG and possible red dot
    const notifBtn = document.getElementById('notification-btn');

    // The dropdown container
    const notifDropdown = document.getElementById('notification-dropdown');

    // The inner container for list items
    const notifListContainer = notifDropdown ? notifDropdown.querySelector('.max-h-64') : null;

    let lastCount = -1; // To track if count changed

    // Simple notification chime (base64 wav)
    // Actually, I will use a reliable short beep string.
    const notificationSound = new Audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbqWEzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2CJudPepWMzM2O3t8=");

    async function checkNotifications() {
        try {
            const response = await fetch(NOTIFICATION_API_URL, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) return;

            const data = await response.json();
            const count = data.count;
            const notifications = data.notifications;

            // 1. Update Red Dot
            if (notifBtn) {
                // Remove existing red dot if any
                const existingDot = notifBtn.querySelector('span.bg-red-500');
                if (existingDot) existingDot.remove();

                if (count > 0) {
                    const dot = document.createElement('span');
                    dot.className = 'absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white';
                    notifBtn.appendChild(dot);
                }
            }

            // 2. Add "Mark all read" button if needed
            if (notifDropdown) {
                const header = notifDropdown.querySelector('.px-4.py-2.border-b'); // Header container
                if (header) {
                    const markAllBtn = header.querySelector('#dropdown-mark-all-read');
                    if (count > 0 && !markAllBtn) {
                        const btn = document.createElement('button');
                        btn.id = 'dropdown-mark-all-read';
                        btn.className = 'text-xs text-indigo-600 hover:text-indigo-500';
                        btn.textContent = 'Mark all read';
                        // Basic click listener (would need actual logic, but mostly UI for now)
                        btn.onclick = () => {
                            fetch('/notifications/mark-all-read/', {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': getCookie('csrftoken'),
                                    'Content-Type': 'application/json'
                                }
                            }).then(() => checkNotifications());
                        };
                        header.appendChild(btn);
                    } else if (count === 0 && markAllBtn) {
                        markAllBtn.remove();
                    }
                }
            }

            // 3. Play Sound if new notification arrived
            if (lastCount !== -1 && count > lastCount) {
                try {
                    notificationSound.currentTime = 0;
                    const playPromise = notificationSound.play();
                    if (playPromise !== undefined) {
                        playPromise.catch(error => {
                            // Auto-play was prevented.
                            console.log('Audio autoplay prevented:', error);
                        });
                    }
                } catch (e) {
                    console.error("Error playing sound:", e);
                }
            }

            // 4. Update List only if changed (to avoid jitter while reading)
            // Or only if we are just polling.
            // A simple check: if count changed, or if count > 0 and we haven't rendered list yet.
            // For simplicity, we can rebuild the list if count differs or just periodically.
            // Let's rebuild if count changed to keep it fresh.
            if (count !== lastCount && notifListContainer) {
                lastCount = count;

                if (count === 0) {
                    notifListContainer.innerHTML = `
                        <div class="px-4 py-3 text-center text-sm text-gray-500 dark:text-slate-400">
                            No new notifications
                        </div>
                    `;
                } else {
                    notifListContainer.innerHTML = ''; // Clear
                    notifications.forEach(note => {
                        const div = document.createElement('div');
                        div.className = 'px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-700 transition duration-150 ease-in-out border-b border-gray-100 dark:border-slate-700 last:border-0 relative bg-blue-50 dark:bg-slate-700/50';

                        div.innerHTML = `
                            <p class="text-sm text-gray-900 dark:text-white font-semibold">
                                ${escapeHtml(note.message.length > 60 ? note.message.substring(0, 60) + '...' : note.message)}
                            </p>
                            <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">${note.created_at_display}</p>
                            ${note.link ? `<a href="${note.link}" class="absolute inset-0 z-10"></a>` : ''}
                        `;
                        notifListContainer.appendChild(div);
                    });
                }
            }

        } catch (error) {
            console.error('Failed to poll notifications', error);
        }
    }

    // Start polling
    // DISABLED: WebSockets now handle real-time notifications
    // checkNotifications(); // Initial check
    // setInterval(checkNotifications, POLL_INTERVAL);

    console.log('[Notifications] Polling disabled - using WebSockets for real-time updates');

    // Helper: Escape HTML
    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Helper: Get Cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

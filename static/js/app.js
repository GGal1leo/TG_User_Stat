// Main JavaScript file for IOC Monitor

// Global functions and utilities
window.IOCMonitor = {
    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function() {
                IOCMonitor.showToast('Copied to clipboard!', 'success');
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                IOCMonitor.showToast('Failed to copy', 'danger');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                IOCMonitor.showToast('Copied to clipboard!', 'success');
            } catch (err) {
                console.error('Fallback copy failed: ', err);
                IOCMonitor.showToast('Failed to copy', 'danger');
            }
            document.body.removeChild(textArea);
        }
    },

    // Show toast notification
    showToast: function(message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer') || IOCMonitor.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function () {
            toast.remove();
        });
    },

    // Create toast container if it doesn't exist
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
        return container;
    },

    // Format datetime
    formatDateTime: function(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            return dateString;
        }
    },

    // Get badge color for IOC type
    getTypeBadgeColor: function(type) {
        const colors = {
            'ip': 'success',
            'domain': 'warning',
            'url': 'info'
        };
        return colors[type] || 'secondary';
    },

    // Auto-refresh dashboard
    autoRefresh: function(interval = 30000) {
        if (window.location.pathname === '/') {
            setInterval(function() {
                IOCMonitor.updateDashboardStats();
            }, interval);
        }
    },

    // Update dashboard statistics
    updateDashboardStats: function() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(stats => {
                // Update stat cards if they exist
                const totalElement = document.querySelector('[data-stat="total_iocs"]');
                const ipElement = document.querySelector('[data-stat="ip_count"]');
                const domainElement = document.querySelector('[data-stat="domain_count"]');
                const urlElement = document.querySelector('[data-stat="url_count"]');
                
                if (totalElement) totalElement.textContent = stats.total_iocs || 0;
                if (ipElement) ipElement.textContent = stats.ip_count || 0;
                if (domainElement) domainElement.textContent = stats.domain_count || 0;
                if (urlElement) urlElement.textContent = stats.url_count || 0;
            })
            .catch(error => {
                console.error('Failed to update stats:', error);
            });
    },

    // Search functionality
    performSearch: function(searchTerm, type = '', limit = 100) {
        const params = new URLSearchParams({
            search: searchTerm,
            limit: limit
        });
        
        if (type) {
            params.append('type', type);
        }
        
        return fetch(`/api/iocs?${params}`)
            .then(response => response.json());
    },

    // Initialize the application
    init: function() {
        // Add active class to current nav item
        IOCMonitor.updateNavigation();
        
        // Initialize tooltips
        IOCMonitor.initializeTooltips();
        
        // Start auto-refresh if on dashboard
        IOCMonitor.autoRefresh();
        
        // Add keyboard shortcuts
        IOCMonitor.initializeKeyboardShortcuts();
    },

    // Update navigation active state
    updateNavigation: function() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || (currentPath === '/' && href === '/')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

    // Initialize Bootstrap tooltips
    initializeTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts: function() {
        document.addEventListener('keydown', function(e) {
            // Ctrl+/ for search focus
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                const searchInput = document.querySelector('#searchInput, input[type="search"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Escape to clear search
            if (e.key === 'Escape') {
                const searchInput = document.querySelector('#searchInput');
                if (searchInput && document.activeElement === searchInput) {
                    searchInput.value = '';
                }
            }
        });
    }
};

// Global helper functions for backward compatibility
function copyToClipboard(text) {
    IOCMonitor.copyToClipboard(text);
}

function quickSearch(term) {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = term;
        // Trigger search if on search page
        if (typeof performSearch === 'function') {
            performSearch();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    IOCMonitor.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IOCMonitor;
}

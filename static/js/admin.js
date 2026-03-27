/**
 * admin.js — Core Admin Utilities
 *
 * Provides shared functionality used across all admin dashboard pages:
 *   - Lucide icon initialization
 *   - Mobile sidebar toggle
 *   - Toast notification auto-dismiss
 *   - Dropdown menus (open/close/click-outside)
 *   - Modal open/close with scale animation
 *   - Generic table/card filtering (search + dropdown filters)
 */

// Initialize Lucide icons on page load
lucide.createIcons();


// =============================================================================
// Sidebar
// =============================================================================

/**
 * Toggles the mobile sidebar and overlay visibility.
 * Called by the hamburger menu button on small screens.
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
    }
}


// =============================================================================
// Toast Notifications
// =============================================================================

/**
 * Dismisses a toast notification with a fade-out animation.
 * @param {string} id - DOM ID of the toast element
 */
function dismissToast(id) {
    const toast = document.getElementById(id);
    if (toast) {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }
}

// Auto-dismiss all toasts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('[id^="toast-"]');
    toasts.forEach(toast => {
        setTimeout(() => {
            if (toast.parentElement) dismissToast(toast.id);
        }, 5000);
    });
});


// =============================================================================
// Dropdown Menus
// =============================================================================

/**
 * Toggles a dropdown menu, closing all others first.
 * @param {string} id - DOM ID of the dropdown menu
 */
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    // Close all other dropdowns before opening the clicked one
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu.id !== id) menu.classList.add('hidden');
    });
    dropdown.classList.toggle('hidden');
}

// Close dropdowns when clicking outside their container
document.addEventListener('click', function (event) {
    const dropdownContainer = event.target.closest('.dropdown-container');
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (!dropdownContainer || !dropdownContainer.contains(menu)) {
            menu.classList.add('hidden');
        }
    });
});


// =============================================================================
// Modals
// =============================================================================

/**
 * Toggles a modal's visibility with a scale/opacity animation.
 * Works with any modal that has a .bg-white child as the content panel.
 * @param {string} modalId - DOM ID of the modal overlay
 */
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const content = modal.querySelector('div.bg-white') || modal.children[0];

    if (modal.classList.contains('hidden')) {
        // Open: show overlay, then animate content in
        modal.classList.remove('hidden');
        setTimeout(() => {
            if (content) {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }
        }, 10);
    } else {
        // Close: animate content out, then hide overlay
        if (content) {
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        } else {
            modal.classList.add('hidden');
        }
    }
}


// =============================================================================
// Generic Table/Card Filtering
// =============================================================================

/**
 * Sets up client-side filtering for any admin data table or card grid.
 * Combines text search with multiple dropdown filters.
 *
 * Items must have data attributes matching filter IDs:
 *   - data-search-terms: for text search (falls back to textContent)
 *   - data-{filterType}: for each dropdown (e.g., data-role, data-status)
 *
 * @param {Object} config
 * @param {string} [config.searchInputId] - ID of the text search input
 * @param {string[]} [config.filterIds] - IDs of <select> dropdown filters
 * @param {string} config.itemSelector - CSS selector for items to filter
 */
function setupGenericFilter({ searchInputId, filterIds = [], itemSelector }) {
    const searchInput = searchInputId ? document.getElementById(searchInputId) : null;
    const filters = filterIds.map(id => document.getElementById(id));
    const items = document.querySelectorAll(itemSelector);

    if (!searchInput && filters.every(f => !f)) return;

    function applyFilters() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const filterValues = filters.map(f => f ? f.value : 'all');

        items.forEach(item => {
            // 1. Text search check
            let matchesSearch = false;
            if (item.dataset.searchTerms) {
                matchesSearch = item.dataset.searchTerms.includes(searchTerm);
            } else {
                matchesSearch = item.textContent.toLowerCase().includes(searchTerm);
            }

            // 2. Dropdown filter check
            let matchesFilters = true;
            filters.forEach((f, idx) => {
                if (!f) return;
                // Extract filter type from ID (e.g., 'role' from 'role-filter')
                const filterType = f.id.split('-')[0];
                const itemValue = item.dataset[filterType] || 'all';
                const filterValue = filterValues[idx];

                if (filterValue !== 'all' && itemValue !== filterValue) {
                    matchesFilters = false;
                }
            });

            // 3. Apply visibility
            item.style.display = (matchesSearch && matchesFilters) ? '' : 'none';
        });
    }

    // Bind event listeners
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    filters.forEach(f => {
        if (f) f.addEventListener('change', applyFilters);
    });
}

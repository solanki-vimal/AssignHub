lucide.createIcons();

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('-translate-x-full');
        overlay.classList.toggle('hidden');
    }
}

function dismissToast(id) {
    const toast = document.getElementById(id);
    if (toast) {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }
}

// Auto dismiss toasts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const toasts = document.querySelectorAll('[id^="toast-"]');
    toasts.forEach(toast => {
        setTimeout(() => {
            if (toast.parentElement) dismissToast(toast.id);
        }, 5000);
    });
});

function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu.id !== id) menu.classList.add('hidden');
    });
    dropdown.classList.toggle('hidden');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function (event) {
    const dropdownContainer = event.target.closest('.dropdown-container');
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (!dropdownContainer || !dropdownContainer.contains(menu)) {
            menu.classList.add('hidden');
        }
    });
});

// Modal toggle generic function
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // Attempt to find a container for animation
    const content = modal.querySelector('div.bg-white') || modal.children[0];

    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        setTimeout(() => {
            if (content) {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }
        }, 10);
    } else {
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

/**
 * Generic Filtering Logic for Admin Data Tables/Grids
 * @param {Object} config - Configuration for the filter
 * @param {string} config.searchInputId - ID of the text search input (optional)
 * @param {Array<string>} config.filterIds - Array of IDs for <select> dropdown filters (optional)
 * @param {string} config.itemSelector - CSS selector for the items (rows/cards) to filter
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
            // 1. Search Check
            let matchesSearch = false;
            if (item.dataset.searchTerms) {
                matchesSearch = item.dataset.searchTerms.includes(searchTerm);
            } else {
                // generic fallback if dataset.searchTerms is missing
                matchesSearch = item.textContent.toLowerCase().includes(searchTerm);
            }

            // 2. Dropdown Filter Check
            let matchesFilters = true;
            filters.forEach((f, idx) => {
                if (!f) return;
                const filterType = f.id.split('-')[0]; // e.g., 'role', 'status', 'semester' from 'role-filter'
                const itemValue = item.dataset[filterType] || 'all';
                const filterValue = filterValues[idx];

                if (filterValue !== 'all' && itemValue !== filterValue) {
                    matchesFilters = false;
                }
            });

            // 3. Apply Visibility
            if (matchesSearch && matchesFilters) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    if (searchInput) searchInput.addEventListener('input', applyFilters);
    filters.forEach(f => {
        if (f) f.addEventListener('change', applyFilters);
    });
}

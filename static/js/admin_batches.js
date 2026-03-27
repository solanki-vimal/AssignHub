/**
 * admin_batches.js — Batch Management Page
 *
 * Handles:
 *   - Edit modal: pre-fills form fields from batch data attributes
 *   - Client-side filtering by search, year, and semester
 *
 * Depends on: admin.js (toggleModal, setupGenericFilter)
 */


/**
 * Opens the edit batch modal and pre-fills form fields with current batch data.
 * Called via data attributes on edit buttons (delegated click handler below).
 *
 * @param {string} id       - Batch PK (used to set form action URL)
 * @param {string} name     - Current batch name
 * @param {string} year     - Academic year string (e.g., "2024-25")
 * @param {string} isActive - "true" or "false" string
 * @param {string} semester - Current semester value
 */
function openEditModal(id, name, year, isActive, semester) {
    const modal = document.getElementById('edit-batch-modal');
    if (!modal) {
        console.error("Edit modal not found!");
        return;
    }

    // Set form action to the batch-specific edit URL
    const form = modal.querySelector('form');
    if (form) {
        form.action = `/dashboard/admin/batches/${id}/edit/`;
    }

    // Fill form fields with current batch data
    const nameField = document.getElementById('id_edit-name');
    const startField = document.getElementById('id_edit-start_date');
    const endField = document.getElementById('id_edit-end_date');
    const statusField = document.getElementById('id_edit-status');
    const semesterField = document.getElementById('id_edit-semester');

    if (nameField) nameField.value = name;

    // Convert academic year (e.g., "2024-25") to date inputs
    if (year && year.includes('-')) {
        const parts = year.split('-');
        let sYear = parts[0];
        let eYear = parts[1];
        if (eYear.length === 2) eYear = "20" + eYear;
        if (startField) startField.value = sYear + "-01-01";
        if (endField) endField.value = eYear + "-12-31";
    }

    if (statusField) {
        statusField.value = (isActive.toLowerCase() === 'true') ? 'active' : 'inactive';
    }
    if (semesterField) {
        semesterField.value = semester || '';
    }

    // Open the modal using the shared toggleModal function
    if (typeof toggleModal === 'function') {
        toggleModal('edit-batch-modal');
    } else {
        console.error("toggleModal function not found!");
        modal.classList.remove('hidden');
    }
}

// Delegated click handler for edit buttons (avoids per-button event binding)
document.addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-batch-btn');
    if (editBtn) {
        e.preventDefault();
        const data = editBtn.dataset;
        openEditModal(data.id, data.name, data.year, data.active, data.semester);
    }
});

// Client-side filtering: search + year + semester dropdowns
document.addEventListener('DOMContentLoaded', () => {
    if (typeof setupGenericFilter === 'function') {
        setupGenericFilter({
            searchInputId: 'batch-search',
            filterIds: ['year-filter', 'semester-filter'],
            itemSelector: '.batch-card'
        });
    }
});

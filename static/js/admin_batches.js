function openEditModal(id, name, year, isActive, semester) {
    console.log("Opening edit modal for batch:", id);
    const modal = document.getElementById('edit-batch-modal');
    if (!modal) {
        console.error("Edit modal not found!");
        return;
    }
    
    const form = modal.querySelector('form');
    if (form) {
        form.action = `/dashboard/admin/batches/${id}/edit/`;
    }
    
    // Fill form fields
    const nameField = document.getElementById('id_edit-name');
    const startField = document.getElementById('id_edit-start_date');
    const endField = document.getElementById('id_edit-end_date');
    const statusField = document.getElementById('id_edit-status');
    const semesterField = document.getElementById('id_edit-semester');

    if (nameField) nameField.value = name;

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
    
    if (typeof toggleModal === 'function') {
        toggleModal('edit-batch-modal');
    } else {
        console.error("toggleModal function not found!");
        modal.classList.remove('hidden');
    }
}

// Centralized Event Listener for Edit Buttons
document.addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-batch-btn');
    if (editBtn) {
        e.preventDefault();
        const data = editBtn.dataset;
        openEditModal(
            data.id,
            data.name,
            data.year,
            data.active,
            data.semester
        );
    }
});

// Filtering logic
document.addEventListener('DOMContentLoaded', () => {
    if (typeof setupGenericFilter === 'function') {
        setupGenericFilter({
            searchInputId: 'batch-search',
            filterIds: ['year-filter', 'semester-filter'],
            itemSelector: '.batch-card'
        });
    }
});

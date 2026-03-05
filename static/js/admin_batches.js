function openEditModal(id, name, year, isActive, semester, coordinatorId) {
    document.getElementById('edit-batch-form').action = `/dashboard/admin/batches/${id}/edit/`;
    document.getElementById('edit-batch-name').value = name;

    // Format year back to dummy dates for the date pickers
    if (year && year.includes('-')) {
        const parts = year.split('-');
        let sYear = parts[0];
        let eYear = parts[1];
        if (eYear.length === 2) eYear = "20" + eYear;
        document.getElementById('edit-batch-start').value = sYear + "-06-01";
        document.getElementById('edit-batch-end').value = eYear + "-05-31";
    }

    document.getElementById('edit-batch-status').value = isActive === 'True' ? 'active' : 'inactive';
    const semesterSelect = document.getElementById('edit-batch-semester');
    if (semesterSelect) semesterSelect.value = semester || '';
    const coordinatorSelect = document.getElementById('edit-batch-coordinator');
    if (coordinatorSelect) coordinatorSelect.value = coordinatorId || '';
    toggleModal('edit-batch-modal');
}

// Filtering logic
document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'batch-search',
        filterIds: ['year-filter', 'semester-filter'],
        itemSelector: '.batch-card'
    });
});

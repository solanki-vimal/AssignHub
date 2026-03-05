function openEditModal(id, code, name, semester, department, isActive, facultyId) {
    document.getElementById('edit-course-form').action = `/dashboard/admin/courses/${id}/edit/`;
    document.getElementById('edit-course-code').value = code;
    document.getElementById('edit-course-name').value = name;
    document.getElementById('edit-course-semester').value = semester;
    document.getElementById('edit-course-department').value = department;
    document.getElementById('edit-course-status').value = isActive === 'True' ? 'active' : 'inactive';
    const facultySelect = document.getElementById('edit-course-faculty');
    if (facultySelect) facultySelect.value = facultyId || '';
    toggleModal('edit-course-modal');
}

// Filtering logic
document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'course-search',
        filterIds: ['semester-filter', 'dept-filter'],
        itemSelector: '.course-row'
    });
});

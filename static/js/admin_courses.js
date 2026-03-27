/**
 * admin_courses.js — Course Management Page
 *
 * Handles:
 *   - Edit modal: pre-fills form fields from course data
 *   - Client-side filtering by search, semester, and department
 *
 * Depends on: admin.js (toggleModal, setupGenericFilter)
 */


/**
 * Opens the edit course modal and pre-fills form fields.
 *
 * @param {string} id         - Course PK
 * @param {string} code       - Course code (e.g., "CS301")
 * @param {string} name       - Course name
 * @param {string} semester   - Semester number
 * @param {string} department - Department name
 * @param {string} isActive   - "True" or "False" (Python-style string)
 * @param {string} facultyId  - Faculty user PK (or empty)
 */
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

// Client-side filtering: search + semester + department dropdowns
document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'course-search',
        filterIds: ['semester-filter', 'dept-filter'],
        itemSelector: '.course-row'
    });
});

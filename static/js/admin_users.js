/**
 * admin_users.js — User Management Page
 *
 * Handles:
 *   - Client-side filtering by search, role, and status
 *   - Role-based field toggling in create/edit modals
 *     (show batch for students, department for faculty, hide both for admin)
 *   - Edit user modal pre-fill from data attributes
 *
 * Depends on: admin.js (setupGenericFilter, toggleModal)
 */


// Client-side filtering: search + role + status dropdowns
document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'user-search',
        filterIds: ['role-filter', 'status-filter'],
        itemSelector: '.user-row'
    });
});


/**
 * Shows/hides role-specific form fields (batch vs department) based on selected role.
 * Used in both the "Add User" and "Edit User" modals.
 *
 * @param {string} roleSelectId  - ID of the role <select>
 * @param {string} batchGroupId  - ID of the batch field container
 * @param {string} deptGroupId   - ID of the department field container
 * @param {string} batchInputId  - ID of the batch <input>/<select>
 * @param {string} deptInputId   - ID of the department <input>/<select>
 */
function toggleRoleFields(roleSelectId, batchGroupId, deptGroupId, batchInputId, deptInputId) {
    const roleEl = document.getElementById(roleSelectId);
    if (!roleEl) return;
    const role = roleEl.value;
    const batchGroup = document.getElementById(batchGroupId);
    const deptGroup = document.getElementById(deptGroupId);
    const batchInput = document.getElementById(batchInputId);
    const deptInput = document.getElementById(deptInputId);

    if (role === 'student') {
        batchGroup.style.display = 'block';
        deptGroup.style.display = 'none';
        batchInput.required = true;
        deptInput.required = false;
    } else if (role === 'faculty') {
        batchGroup.style.display = 'none';
        deptGroup.style.display = 'block';
        batchInput.required = false;
        deptInput.required = true;
    } else {
        // Admin — hide both role-specific field groups
        batchGroup.style.display = 'none';
        deptGroup.style.display = 'none';
        batchInput.required = false;
        deptInput.required = false;
    }
}

// Bind role change listeners for both Add and Edit modals
document.addEventListener('DOMContentLoaded', () => {
    const addUserRole = document.getElementById('add-user-role');
    const editUserRole = document.getElementById('edit-user-role');

    if (addUserRole) {
        addUserRole.addEventListener('change', function () {
            toggleRoleFields('add-user-role', 'add-batch-group', 'add-dept-group', 'add-user-batch', 'add-user-dept');
        });
        // Set initial field visibility on page load
        toggleRoleFields('add-user-role', 'add-batch-group', 'add-dept-group', 'add-user-batch', 'add-user-dept');
    }

    if (editUserRole) {
        editUserRole.addEventListener('change', function () {
            toggleRoleFields('edit-user-role', 'edit-batch-group', 'edit-dept-group', 'edit-user-batch', 'edit-user-dept');
        });
    }
});


/**
 * Opens the edit user modal and pre-fills all fields from data attributes.
 * Routes batch/department values to the correct input based on the user's role.
 *
 * @param {string} id           - User PK
 * @param {string} firstName    - User's first name
 * @param {string} lastName     - User's last name
 * @param {string} email        - User's email
 * @param {string} role         - 'student', 'faculty', or 'admin'
 * @param {string} deptOrBatch  - Batch name (students) or department (faculty)
 * @param {string} enrollmentNo - Student enrollment number (optional)
 * @param {string} facultyId    - Faculty ID (optional)
 */
function openEditUserModal(id, firstName, lastName, email, role, deptOrBatch, enrollmentNo, facultyId) {
    document.getElementById('edit-user-id').value = id;
    document.getElementById('edit-user-fullname').value = (firstName + ' ' + lastName).trim();
    document.getElementById('edit-user-email').value = email;
    document.getElementById('edit-user-role').value = role;

    // Reset both role-specific inputs
    document.getElementById('edit-user-batch').value = '';
    document.getElementById('edit-user-dept').value = '';

    const enrollInput = document.getElementById('edit-user-enrollment');
    const facInput = document.getElementById('edit-user-faculty-id');
    if (enrollInput) enrollInput.value = '';
    if (facInput) facInput.value = '';

    // Route batch/department value to the correct input based on role
    if (deptOrBatch && deptOrBatch !== 'None' && deptOrBatch !== 'System' && deptOrBatch !== 'N/A') {
        if (role === 'student') {
            document.getElementById('edit-user-batch').value = deptOrBatch;
        } else if (role === 'faculty') {
            document.getElementById('edit-user-dept').value = deptOrBatch;
        }
    }

    // Fill role-specific ID fields
    if (role === 'student' && enrollInput) {
        enrollInput.value = enrollmentNo || '';
    } else if (role === 'faculty' && facInput) {
        facInput.value = facultyId || '';
    }

    // Show/hide the correct field groups for the role
    toggleRoleFields('edit-user-role', 'edit-batch-group', 'edit-dept-group', 'edit-user-batch', 'edit-user-dept');

    toggleModal('edit-user-modal');
}

// Search and Filter functionality tailored for the users table
document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'user-search',
        filterIds: ['role-filter', 'status-filter'],
        itemSelector: '.user-row'
    });
});

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
        // Admin role
        batchGroup.style.display = 'none';
        deptGroup.style.display = 'none';
        batchInput.required = false;
        deptInput.required = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const addUserRole = document.getElementById('add-user-role');
    const editUserRole = document.getElementById('edit-user-role');

    if (addUserRole) {
        addUserRole.addEventListener('change', function () {
            toggleRoleFields('add-user-role', 'add-batch-group', 'add-dept-group', 'add-user-batch', 'add-user-dept');
        });
        // Initialize the add modal state
        toggleRoleFields('add-user-role', 'add-batch-group', 'add-dept-group', 'add-user-batch', 'add-user-dept');
    }

    if (editUserRole) {
        editUserRole.addEventListener('change', function () {
            toggleRoleFields('edit-user-role', 'edit-batch-group', 'edit-dept-group', 'edit-user-batch', 'edit-user-dept');
        });
    }
});

function openEditUserModal(id, firstName, lastName, email, role, deptOrBatch, enrollmentNo, facultyId) {
    document.getElementById('edit-user-id').value = id;
    document.getElementById('edit-user-fullname').value = (firstName + ' ' + lastName).trim();
    document.getElementById('edit-user-email').value = email;
    document.getElementById('edit-user-role').value = role;

    // Reset both inputs first
    document.getElementById('edit-user-batch').value = '';
    document.getElementById('edit-user-dept').value = '';

    // Safety check if elements exist
    const enrollInput = document.getElementById('edit-user-enrollment');
    const facInput = document.getElementById('edit-user-faculty-id');
    if (enrollInput) enrollInput.value = '';
    if (facInput) facInput.value = '';

    if (deptOrBatch && deptOrBatch !== 'None' && deptOrBatch !== 'System' && deptOrBatch !== 'N/A') {
        if (role === 'student') {
            document.getElementById('edit-user-batch').value = deptOrBatch;
        } else if (role === 'faculty') {
            document.getElementById('edit-user-dept').value = deptOrBatch;
        }
    }

    if (role === 'student' && enrollInput) {
        enrollInput.value = enrollmentNo || '';
    } else if (role === 'faculty' && facInput) {
        facInput.value = facultyId || '';
    }

    // Trigger the field toggle based on the new role
    toggleRoleFields('edit-user-role', 'edit-batch-group', 'edit-dept-group', 'edit-user-batch', 'edit-user-dept');

    toggleModal('edit-user-modal');
}

function openResetPasswordModal(id, email) {
    document.getElementById('reset-pwd-user-id').value = id;
    document.getElementById('reset-pwd-email').textContent = email;
    // reset input
    const input = document.querySelector('input[name="new_password"]');
    if (input) input.value = '';

    toggleModal('reset-password-modal');
}

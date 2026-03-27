/**
 * AssignHub Authentication & Common Utilities
 * Handles password toggling and role-based field switching.
 */

/**
 * Toggles input type between password and text
 * @param {string} inputId - ID of the password input field
 * @param {string} iconId - ID of the Lucide icon element
 */
function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.setAttribute('data-lucide', 'eye-off');
        } else {
            input.type = 'password';
            icon.setAttribute('data-lucide', 'eye');
        }
        
        // Re-render Lucide icons if the library is available
        if (window.lucide) {
            lucide.createIcons();
        }
    }
}

/**
 * Handles role-based conditional field toggling in registration
 * @param {string} role - 'student' or 'faculty'
 */
function handleRoleSwitch(role) {
    // Update hidden role field for the Django form
    const roleInput = document.querySelector('input[name="role"]');
    if (roleInput) roleInput.value = role;
    
    // Toggle container visibility for role-specific fields
    const studentContainer = document.getElementById('student-only-fields');
    const facultyContainer = document.getElementById('faculty-only-fields');
    
    if (studentContainer && facultyContainer) {
        if (role === 'student') {
            studentContainer.classList.remove('hidden');
            facultyContainer.classList.add('hidden');
        } else if (role === 'faculty') {
            studentContainer.classList.add('hidden');
            facultyContainer.classList.remove('hidden');
        }
    }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons if available
    if (window.lucide) {
        lucide.createIcons();
    }
    
    // Set initial registration state if we are on the registration page
    const checkedRole = document.querySelector('input[name="role_selector"]:checked');
    if (checkedRole) {
        handleRoleSwitch(checkedRole.value);
    }
});

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
        if (typeof lucide !== 'undefined') {
            lucide.createIcons(); // Re-render the icon
        }
    }
}

// Form logic for registration
document.addEventListener('DOMContentLoaded', () => {
    const roleRadios = document.querySelectorAll('.role-radio');
    const form = document.querySelector('form');
    const studentFieldsContainer = document.getElementById('student-fields');

    if (roleRadios.length > 0 && form && studentFieldsContainer) {
        roleRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const selectedRole = e.target.value;
                const inputs = form.querySelectorAll('input:not([name="csrfmiddlewaretoken"]):not([name="role"])');
                inputs.forEach(input => {
                    input.value = '';
                });

                // Show/hide student fields based on role
                if (selectedRole === 'student') {
                    studentFieldsContainer.classList.remove('hidden');
                } else {
                    studentFieldsContainer.classList.add('hidden');
                }
            });
        });
    }
});

if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

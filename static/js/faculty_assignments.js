// faculty_assignments.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('assignment-search');
    const courseFilter = document.getElementById('course-filter');
    const statusFilter = document.getElementById('status-filter');
    const cards = document.querySelectorAll('.assignment-card');

    function filterAssignments() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const courseValue = courseFilter ? courseFilter.value.toLowerCase() : 'all';
        const statusValue = statusFilter ? statusFilter.value.toLowerCase() : 'all';

        cards.forEach(card => {
            const titleData = card.getAttribute('data-title') || '';
            const courseData = card.getAttribute('data-course') || '';
            const statusData = card.getAttribute('data-status') || '';

            const matchesSearch = searchTerm === '' || titleData.includes(searchTerm) || courseData.includes(searchTerm);
            const matchesCourse = courseValue === 'all' || courseData.includes(courseValue);
            const matchesStatus = statusValue === 'all' || statusData === statusValue;

            if (matchesSearch && matchesCourse && matchesStatus) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (searchInput) searchInput.addEventListener('input', filterAssignments);
    if (courseFilter) courseFilter.addEventListener('change', filterAssignments);
    if (statusFilter) statusFilter.addEventListener('change', filterAssignments);

    // Modal handling for Deadline Extension
    window.openExtendModal = function(id, currentDue, title) {
        const modal = document.getElementById('extend-modal');
        const form = document.getElementById('extend-form');
        const titleEl = document.getElementById('extend-assignment-title');
        const dateInput = modal.querySelector('input[type="datetime-local"]');
        
        form.action = `/dashboard/faculty/assignments/${id}/extend/`;
        titleEl.textContent = title;
        
        if (currentDue) {
            try {
                // Parse date from string like "Mar 25, 2026, 12:00 PM" or similar
                // For simplicity, we can pass ISO string from template
                const date = new Date(currentDue);
                if (!isNaN(date)) {
                    const offset = date.getTimezoneOffset();
                    const localDate = new Date(date.getTime() - (offset * 60 * 1000));
                    dateInput.value = localDate.toISOString().slice(0, 16);
                }
            } catch(e) { console.error("Date parsing error:", e); }
        }
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    };

    window.closeExtendModal = function() {
        const modal = document.getElementById('extend-modal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };
});

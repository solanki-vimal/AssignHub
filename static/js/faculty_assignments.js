/**
 * faculty_assignments.js — Faculty Assignments Page
 *
 * Handles:
 *   - Client-side filtering by search, course, and publish status
 *   - Deadline extension modal (open/close with date pre-fill)
 *
 * Uses its own filter logic (not setupGenericFilter) because assignment
 * cards use data-title/data-course/data-status attributes.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('assignment-search');
    const courseFilter = document.getElementById('course-filter');
    const statusFilter = document.getElementById('status-filter');
    const cards = document.querySelectorAll('.assignment-card');

    /**
     * Filters assignment cards by search text, course, and status.
     * Matches against data-title, data-course, and data-status attributes.
     */
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

            card.style.display = (matchesSearch && matchesCourse && matchesStatus) ? '' : 'none';
        });
    }

    if (searchInput) searchInput.addEventListener('input', filterAssignments);
    if (courseFilter) courseFilter.addEventListener('change', filterAssignments);
    if (statusFilter) statusFilter.addEventListener('change', filterAssignments);


    // =========================================================================
    // Deadline Extension Modal
    // =========================================================================

    /**
     * Opens the deadline extension modal and pre-fills the date input.
     * @param {string} id         - Assignment PK
     * @param {string} currentDue - Current due date string
     * @param {string} title      - Assignment title (displayed in modal header)
     */
    window.openExtendModal = function(id, currentDue, title) {
        const modal = document.getElementById('extend-modal');
        const form = document.getElementById('extend-form');
        const titleEl = document.getElementById('extend-assignment-title');
        const dateInput = modal.querySelector('input[type="datetime-local"]');

        form.action = `/dashboard/faculty/assignments/${id}/extend/`;
        titleEl.textContent = title;

        // Convert current due date to local datetime-local format
        if (currentDue) {
            try {
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

    /** Closes the deadline extension modal. */
    window.closeExtendModal = function() {
        const modal = document.getElementById('extend-modal');
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };
});

/**
 * faculty_courses.js — Faculty Courses Page
 *
 * Client-side search filtering for faculty course cards.
 * Matches against data-name and data-code attributes.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('course-search');
    const cards = document.querySelectorAll('.course-card');

    /** Filters course cards by name or code. */
    function filterCourses() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';

        cards.forEach(card => {
            const nameData = card.getAttribute('data-name') || '';
            const codeData = card.getAttribute('data-code') || '';
            const matchesSearch = searchTerm === '' || nameData.includes(searchTerm) || codeData.includes(searchTerm);
            card.style.display = matchesSearch ? '' : 'none';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterCourses);
    }
});

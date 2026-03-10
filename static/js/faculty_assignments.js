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

});

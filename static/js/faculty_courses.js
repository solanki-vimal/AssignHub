// faculty_courses.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('course-search');
    const cards = document.querySelectorAll('.course-card');

    function filterCourses() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
        
        cards.forEach(card => {
            const nameData = card.getAttribute('data-name') || '';
            const codeData = card.getAttribute('data-code') || '';

            const matchesSearch = searchTerm === '' || nameData.includes(searchTerm) || codeData.includes(searchTerm);

            if (matchesSearch) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterCourses);
    }
});

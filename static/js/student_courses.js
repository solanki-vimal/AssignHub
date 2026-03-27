/**
 * student_courses.js — Student Courses Page
 *
 * Client-side search filtering for course cards.
 * Matches against data-search attribute (course name + code).
 * Shows an empty state message when no cards match.
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('course-search');
    const courseCards = document.querySelectorAll('.course-card');
    const gridContainer = document.getElementById('course-grid');

    if (searchInput && gridContainer) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            let visibleCount = 0;

            courseCards.forEach(card => {
                const searchData = card.getAttribute('data-search');
                if (searchTerm === '' || searchData.includes(searchTerm)) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Show/hide "no courses found" empty state
            const existingEmptyMessage = document.getElementById('search-empty-message');
            if (visibleCount === 0 && courseCards.length > 0) {
                if (!existingEmptyMessage) {
                    const emptyMessage = document.createElement('div');
                    emptyMessage.id = 'search-empty-message';
                    emptyMessage.className = 'col-span-1 md:col-span-2 lg:col-span-3 py-12 text-center';
                    emptyMessage.innerHTML = `
                        <p class="text-slate-500 font-medium">No courses found matching "${searchTerm}"</p>
                    `;
                    gridContainer.appendChild(emptyMessage);
                }
            } else if (existingEmptyMessage) {
                existingEmptyMessage.remove();
            }
        });
    }
});

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
    
    // Default action handlers to let the user know view/actions are pending phase 3
    const pendingActionButtons = document.querySelectorAll('.assignment-card button');
    pendingActionButtons.forEach(btn => {
        // Skip the dropdown toggle button and the assignment list action buttons
        if(btn.hasAttribute('onclick') && btn.getAttribute('onclick').includes('action-menu-')) return;
        
        if(!btn.classList.contains('handled')){
            btn.classList.add('handled');
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                alert('This feature (Detailed View / Evaluation / Editing) is scheduled for Phase 3 rollout.');
            });
        }
    });

    const pendingAnchorLinks = document.querySelectorAll('.assignment-card a');
    pendingAnchorLinks.forEach(link => {
        if(link.getAttribute('href') === '#') {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                alert('Detailed assignment view is scheduled for Phase 3 rollout.');
            });
        }
    });
});

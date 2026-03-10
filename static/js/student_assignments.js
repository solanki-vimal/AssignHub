document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('assignment-search');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const assignmentCards = document.querySelectorAll('.assignment-card');
    const listContainer = document.getElementById('assignments-list');
    
    if (searchInput && listContainer) {
        let currentSearch = '';
        let currentStatus = 'all';

        function applyFilters() {
            let visibleCount = 0;
            
            assignmentCards.forEach(card => {
                const searchData = card.getAttribute('data-search');
                const statusData = card.getAttribute('data-status');
                
                const matchesSearch = currentSearch === '' || searchData.includes(currentSearch);
                const matchesStatus = currentStatus === 'all' || statusData === currentStatus;
                
                if (matchesSearch && matchesStatus) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Handle Empty State
            const existingEmpty = document.getElementById('filter-empty-state');
            if (visibleCount === 0 && assignmentCards.length > 0) {
                if (!existingEmpty) {
                    const emptyState = document.createElement('div');
                    emptyState.id = 'filter-empty-state';
                    emptyState.className = 'bg-white rounded-2xl border border-slate-100 border-dashed p-12 text-center';
                    emptyState.innerHTML = `
                        <p class="text-slate-500 font-medium">No assignments match your current filters.</p>
                    `;
                    listContainer.appendChild(emptyState);
                }
            } else if (existingEmpty) {
                existingEmpty.remove();
            }
        }

        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.toLowerCase().trim();
            applyFilters();
        });

        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active styling from all
                filterBtns.forEach(b => {
                    b.classList.remove('bg-indigo-50', 'text-indigo-700');
                    b.classList.add('bg-slate-50', 'text-slate-600');
                });
                
                // Add active styling to clicked
                e.target.classList.remove('bg-slate-50', 'text-slate-600');
                e.target.classList.add('bg-indigo-50', 'text-indigo-700');
                
                currentStatus = e.target.getAttribute('data-filter');
                applyFilters();
            });
        });
    }
});

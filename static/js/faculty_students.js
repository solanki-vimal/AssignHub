// faculty_students.js

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('student-search');
    const courseFilter = document.getElementById('course-filter');
    const batchFilter = document.getElementById('batch-filter');
    const tableBody = document.getElementById('students-table-body');
    const rows = tableBody ? tableBody.querySelectorAll('tr.student-row') : [];
    const noStudentsRow = document.getElementById('no-students-row');

    function filterStudents() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const courseValue = courseFilter.value.toLowerCase();
        const batchValue = batchFilter.value.toLowerCase();
        
        let visibleCount = 0;

        rows.forEach(row => {
            const searchData = row.getAttribute('data-search') || '';
            const coursesData = row.getAttribute('data-courses') || '';
            const batchesData = row.getAttribute('data-batches') || '';

            const matchesSearch = searchTerm === '' || searchData.includes(searchTerm);
            const matchesCourse = courseValue === 'all' || coursesData.includes(courseValue);
            const matchesBatch = batchValue === 'all' || batchesData.includes(batchValue);

            if (matchesSearch && matchesCourse && matchesBatch) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        if (noStudentsRow) {
            noStudentsRow.style.display = visibleCount === 0 ? '' : 'none';
        }
    }

    if (searchInput) searchInput.addEventListener('input', filterStudents);
    if (courseFilter) courseFilter.addEventListener('change', filterStudents);
    if (batchFilter) batchFilter.addEventListener('change', filterStudents);
});

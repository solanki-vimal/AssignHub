document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'student-search',
        itemSelector: '.available-student'
    });

    setupGenericFilter({
        searchInputId: 'course-search',
        itemSelector: '.available-course'
    });
});

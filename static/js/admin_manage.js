/**
 * admin_manage.js — Batch Student & Course Management Pages
 *
 * Sets up search filtering for the "available students" and
 * "available courses" lists on the batch enrollment pages.
 *
 * Depends on: admin.js (setupGenericFilter)
 */

document.addEventListener('DOMContentLoaded', () => {
    // Filter available students list
    setupGenericFilter({
        searchInputId: 'student-search',
        itemSelector: '.available-student'
    });

    // Filter available courses list
    setupGenericFilter({
        searchInputId: 'course-search',
        itemSelector: '.available-course'
    });
});

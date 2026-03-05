document.addEventListener('DOMContentLoaded', () => {
    setupGenericFilter({
        searchInputId: 'log-search',
        filterIds: ['action-filter', 'role-filter'],
        itemSelector: '.log-row'
    });
});

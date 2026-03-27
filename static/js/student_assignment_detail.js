/**
 * student_assignment_detail.js — Student Assignment Detail Page
 *
 * Shows a visual list of selected files before form submission.
 * Displays file names and sizes in styled cards with Lucide icons.
 */


/**
 * Updates the selected file preview list when files are chosen.
 * Shows each file's name and size (in MB) in a styled card.
 *
 * @param {HTMLInputElement} input - The file input element
 */
function updateFileList(input) {
    const list = document.getElementById('selected-files');
    if (!list) return;

    list.innerHTML = '';

    if (input.files.length > 0) {
        list.classList.remove('hidden');
        Array.from(input.files).forEach(file => {
            const size = (file.size / (1024 * 1024)).toFixed(2);
            list.innerHTML += `
                <div class="flex items-center gap-3 p-2 bg-indigo-50 text-indigo-700 rounded-lg text-sm border border-indigo-100">
                    <i data-lucide="file" class="w-4 h-4 shrink-0"></i>
                    <span class="truncate flex-1">${file.name}</span>
                    <span class="text-xs opacity-70 shrink-0">${size} MB</span>
                </div>
            `;
        });
        // Re-render Lucide icons for the newly added file icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } else {
        list.classList.add('hidden');
    }
}

// Expose globally for inline onchange="updateFileList(this)" in template
window.updateFileList = updateFileList;

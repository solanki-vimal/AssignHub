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
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    } else {
        list.classList.add('hidden');
    }
}

// Make globally available for inline onchange attribute
window.updateFileList = updateFileList;

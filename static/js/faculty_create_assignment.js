// faculty_create_assignment.js

function togglePublished() {
    if (!window.ASSIGNMENT_CONFIG) return;
    const checkbox = document.getElementById(window.ASSIGNMENT_CONFIG.publishedCheckboxId);
    const bg = document.getElementById('toggle-bg');
    const circle = document.getElementById('toggle-circle');

    checkbox.checked = !checkbox.checked;
    if (checkbox.checked) {
        bg.classList.add('bg-indigo-600');
        bg.classList.remove('bg-slate-200');
        circle.classList.add('translate-x-6');
        circle.classList.remove('translate-x-1');
    } else {
        bg.classList.remove('bg-indigo-600');
        bg.classList.add('bg-slate-200');
        circle.classList.remove('translate-x-6');
        circle.classList.remove('translate-x-1');
    }
}

function filterBatches() {
    if (!window.ASSIGNMENT_CONFIG) return;
    const courseSelect = document.getElementById(window.ASSIGNMENT_CONFIG.courseSelectId);
    const batchSelect = document.getElementById(window.ASSIGNMENT_CONFIG.batchSelectId);
    const selectedCourseId = courseSelect.value;
    const previousBatchId = batchSelect.value;

    const courseToBatches = window.ASSIGNMENT_CONFIG.courseToBatches;

    // Save current selected batch if any, to restore after rebuild if still valid
    const preservedBatchId = previousBatchId;

    // Clear existing options
    batchSelect.innerHTML = '';

    if (selectedCourseId && courseToBatches[selectedCourseId]) {
        const batches = courseToBatches[selectedCourseId];
        if (batches.length > 0) {
            batches.forEach(batch => {
                const option = document.createElement('option');
                option.value = batch.id;
                option.textContent = batch.name;
                if (batch.id === preservedBatchId) {
                    option.selected = true;
                }
                batchSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "No batches assigned to this course";
            batchSelect.appendChild(option);
        }
    } else {
        const option = document.createElement('option');
        option.value = "";
        option.textContent = "Please select a course first";
        batchSelect.appendChild(option);
    }
}

// Initialize state
window.addEventListener('load', () => {
    if (!window.ASSIGNMENT_CONFIG) return;
    // Toggle state
    const checkbox = document.getElementById(window.ASSIGNMENT_CONFIG.publishedCheckboxId);
    if (checkbox && checkbox.checked) {
        const bg = document.getElementById('toggle-bg');
        const circle = document.getElementById('toggle-circle');
        bg.classList.add('bg-indigo-600');
        bg.classList.remove('bg-slate-200');
        circle.classList.add('translate-x-6');
        circle.classList.remove('translate-x-1');
    }

    // Setup initial filtering
    const courseSelect = document.getElementById(window.ASSIGNMENT_CONFIG.courseSelectId);
    if (courseSelect) {
        courseSelect.addEventListener('change', filterBatches);
        filterBatches(); // Run once for initial state
    }

    // File Input Feedback
    const fileInput = document.querySelector('input[type="file"][name="attachments"]');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            let feedback = document.getElementById('file-upload-feedback');
            const dropzoneText = document.querySelector('label[for="attachments"] p.font-medium, label p.font-medium');

            // Create feedback container if not exists
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.id = 'file-upload-feedback';
                feedback.className = 'text-xs text-indigo-600 mt-2 font-bold px-4 text-center break-words';
                fileInput.parentElement.appendChild(feedback);
            }

            if (files.length > 0) {
                const names = Array.from(files).map(f => f.name).join(', ');
                feedback.innerHTML = `<span class="text-indigo-800">Selected (${files.length}):</span> ${names}`;
                feedback.classList.remove('hidden');
                if (dropzoneText) dropzoneText.textContent = 'Files Ready for Upload';
                fileInput.parentElement.classList.add('border-indigo-400', 'bg-indigo-50');
            } else {
                feedback.classList.add('hidden');
                if (dropzoneText) dropzoneText.textContent = 'Click to upload files';
                fileInput.parentElement.classList.remove('border-indigo-400', 'bg-indigo-50');
            }
        });
    }
});

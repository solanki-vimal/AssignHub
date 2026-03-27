/**
 * faculty_create_assignment.js — Create/Edit Assignment Page
 *
 * Handles:
 *   - Publish toggle switch (custom UI checkbox)
 *   - Dynamic batch dropdown filtering based on selected course
 *   - File input feedback (shows selected file names in dropzone)
 *
 * Requires window.ASSIGNMENT_CONFIG to be set by the template:
 *   {
 *     publishedCheckboxId: string,
 *     courseSelectId: string,
 *     batchSelectId: string,
 *     courseToBatches: { [courseId]: [{ id, name }] }
 *   }
 */


/**
 * Toggles the custom publish toggle switch UI.
 * Syncs the hidden checkbox state with the visual toggle.
 */
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


/**
 * Rebuilds the batch dropdown based on the selected course.
 * Uses the courseToBatches mapping from ASSIGNMENT_CONFIG to
 * show only batches assigned to the selected course.
 */
function filterBatches() {
    if (!window.ASSIGNMENT_CONFIG) return;
    const courseSelect = document.getElementById(window.ASSIGNMENT_CONFIG.courseSelectId);
    const batchSelect = document.getElementById(window.ASSIGNMENT_CONFIG.batchSelectId);
    const selectedCourseId = courseSelect.value;
    const previousBatchId = batchSelect.value;
    const courseToBatches = window.ASSIGNMENT_CONFIG.courseToBatches;

    // Clear existing options
    batchSelect.innerHTML = '';

    if (selectedCourseId && courseToBatches[selectedCourseId]) {
        const batches = courseToBatches[selectedCourseId];
        if (batches.length > 0) {
            batches.forEach(batch => {
                const option = document.createElement('option');
                option.value = batch.id;
                option.textContent = batch.name;
                // Preserve previous selection if still valid
                if (batch.id === previousBatchId) {
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


// Initialize all interactive elements on page load
window.addEventListener('load', () => {
    if (!window.ASSIGNMENT_CONFIG) return;

    // Set initial toggle state for published checkbox
    const checkbox = document.getElementById(window.ASSIGNMENT_CONFIG.publishedCheckboxId);
    if (checkbox && checkbox.checked) {
        const bg = document.getElementById('toggle-bg');
        const circle = document.getElementById('toggle-circle');
        bg.classList.add('bg-indigo-600');
        bg.classList.remove('bg-slate-200');
        circle.classList.add('translate-x-6');
        circle.classList.remove('translate-x-1');
    }

    // Bind course change → batch filter
    const courseSelect = document.getElementById(window.ASSIGNMENT_CONFIG.courseSelectId);
    if (courseSelect) {
        courseSelect.addEventListener('change', filterBatches);
        filterBatches(); // Set initial batch options
    }

    // File input visual feedback in the dropzone
    const fileInput = document.querySelector('input[type="file"][name="attachments"]');
    if (fileInput) {
        const dropzoneText = document.getElementById('dropzone-text');
        const defaultText = dropzoneText ? dropzoneText.textContent : 'Click to upload files';

        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            let feedback = document.getElementById('file-upload-feedback');

            // Create feedback container if it doesn't exist yet
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
                if (dropzoneText) dropzoneText.textContent = defaultText;
                fileInput.parentElement.classList.remove('border-indigo-400', 'bg-indigo-50');
            }
        });
    }
});

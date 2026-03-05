// Initialize Icons
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

// Simple Animation Logic
document.addEventListener('DOMContentLoaded', () => {
    const hero = document.getElementById('hero-content');
    const preview = document.getElementById('dashboard-preview');

    // Trigger animations
    if (hero) {
        setTimeout(() => {
            hero.classList.remove('opacity-0', 'translate-y-4');
            hero.classList.add('transition-all', 'duration-700', 'ease-out');
        }, 100);
    }

    if (preview) {
        setTimeout(() => {
            preview.classList.remove('opacity-0', 'translate-y-8');
            preview.classList.add('transition-all', 'duration-1000', 'ease-out');
        }, 300);
    }
});

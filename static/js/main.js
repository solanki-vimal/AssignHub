/**
 * main.js — Landing Page (Home)
 *
 * Handles:
 *   - Lucide icon initialization
 *   - Hero section fade-in animation
 *   - Dashboard preview slide-up animation
 */

// Initialize Lucide icons
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

// Entrance animations for the landing page sections
document.addEventListener('DOMContentLoaded', () => {
    const hero = document.getElementById('hero-content');
    const preview = document.getElementById('dashboard-preview');

    // Hero: fade in + slide up (100ms delay)
    if (hero) {
        setTimeout(() => {
            hero.classList.remove('opacity-0', 'translate-y-4');
            hero.classList.add('transition-all', 'duration-700', 'ease-out');
        }, 100);
    }

    // Dashboard preview: fade in + slide up (300ms delay for stagger)
    if (preview) {
        setTimeout(() => {
            preview.classList.remove('opacity-0', 'translate-y-8');
            preview.classList.add('transition-all', 'duration-1000', 'ease-out');
        }, 300);
    }
});

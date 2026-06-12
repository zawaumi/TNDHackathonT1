const panelButtons = document.querySelectorAll('[data-panel-toggle]');
const closeButtons = document.querySelectorAll('[data-panel-close]');
const navToggle = document.querySelector('[data-mobile-nav-toggle]');
const navBackdrop = document.querySelector('[data-mobile-nav-backdrop]');
const navRail = document.querySelector('.side-rail');

function closePanels() {
    document.querySelectorAll('.slide-menu.is-open').forEach((panel) => {
        panel.classList.remove('is-open');
    });
}

function closeMobileNav() {
    navRail?.classList.remove('is-open');
    navBackdrop?.classList.remove('is-visible');
    document.body.classList.remove('is-mobile-nav-open');
    if (navToggle) {
        navToggle.setAttribute('aria-expanded', 'false');
    }
}

navToggle?.addEventListener('click', (event) => {
    event.stopPropagation();
    closePanels();
    const shouldOpen = !navRail?.classList.contains('is-open');
    if (!navRail) return;
    navRail.classList.toggle('is-open', shouldOpen);
    navBackdrop?.classList.toggle('is-visible', shouldOpen);
    document.body.classList.toggle('is-mobile-nav-open', shouldOpen);
    navToggle.setAttribute('aria-expanded', String(shouldOpen));
});

navBackdrop?.addEventListener('click', closeMobileNav);

panelButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
        event.stopPropagation();
        const panel = document.getElementById(`${button.dataset.panelToggle}-panel`);
        if (!panel) return;
        const shouldOpen = !panel.classList.contains('is-open');
        closePanels();
        panel.classList.toggle('is-open', shouldOpen);
    });
});

closeButtons.forEach((button) => {
    button.addEventListener('click', closePanels);
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('.slide-menu') && !event.target.closest('[data-panel-toggle]') && !event.target.closest('.side-rail') && !event.target.closest('[data-mobile-nav-toggle]')) {
        closePanels();
        closeMobileNav();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closePanels();
        closeMobileNav();
    }
});

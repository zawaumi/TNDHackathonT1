const panelButtons = document.querySelectorAll('[data-panel-toggle]');
const closeButtons = document.querySelectorAll('[data-panel-close]');

function closePanels() {
    document.querySelectorAll('.slide-menu.is-open').forEach((panel) => {
        panel.classList.remove('is-open');
    });
}

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
    if (!event.target.closest('.slide-menu') && !event.target.closest('[data-panel-toggle]')) {
        closePanels();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closePanels();
    }
});

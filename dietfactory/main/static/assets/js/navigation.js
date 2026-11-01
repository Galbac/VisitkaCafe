document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const menu = document.getElementById('main-navigation');
    if (!toggle || !menu) return;
    const mobile = window.matchMedia('(max-width: 960px)');
    function setOpen(open, restoreFocus = false) {
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
        toggle.querySelector('.menu-label').textContent = open ? 'Закрыть' : 'Меню';
        toggle.classList.toggle('open', open);
        menu.classList.toggle('show', open);
        document.body.classList.toggle('menu-open', open);
        menu.inert = mobile.matches && !open;
        if (restoreFocus) toggle.focus();
    }
    setOpen(false);
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    menu.addEventListener('click', event => { if (event.target.closest('a')) setOpen(false); });
    document.addEventListener('click', event => {
        if (!menu.contains(event.target) && !toggle.contains(event.target)) setOpen(false);
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') setOpen(false, true);
    });
    // Keep keyboard navigation inside the open mobile menu and its close button.
    document.addEventListener('keydown', event => {
        if (event.key !== 'Tab' || toggle.getAttribute('aria-expanded') !== 'true') return;
        const controls = [toggle, ...menu.querySelectorAll('a[href], input, button')];
        const first = controls[0], last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    mobile.addEventListener('change', () => setOpen(false));
});

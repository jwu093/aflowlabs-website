// Native details owns menu state. This enhancement closes it after navigation,
// outside clicks or Escape. No storage, network, account, analytics or timers.
document.querySelectorAll('details.shell-mobile-menu').forEach((menu) => {
  const summary = menu.querySelector('summary');
  menu.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => { menu.open = false; });
  });
  menu.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      summary.focus();
      event.preventDefault();
    }
  });
  document.addEventListener('click', (event) => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
});

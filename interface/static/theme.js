/* theme.js — Gerenciador de Tema Lynx Monitor */

(function () {
    const STORAGE_KEY = 'lynx-theme';
    const root = document.documentElement;

    const saved = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = saved ?? (prefersDark ? 'dark' : 'light');
    root.setAttribute('data-theme', initial);

    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('theme-toggle');
        if (!btn) return;

        btn.addEventListener('click', () => {
            const current = root.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';

            root.style.transition = 'background-color 220ms ease, color 220ms ease';
            root.setAttribute('data-theme', next);
            localStorage.setItem(STORAGE_KEY, next);

            btn.setAttribute('aria-label',
                next === 'dark' ? 'Alternar para modo claro' : 'Alternar para modo escuro'
            );
        });

        const theme = root.getAttribute('data-theme');
        btn.setAttribute('aria-label',
            theme === 'dark' ? 'Alternar para modo claro' : 'Alternar para modo escuro'
        );

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(STORAGE_KEY)) {
                root.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            }
        });
    });
})();
/* Eve Workspace Navigation & Sidebar Controller */
(function () {
    const STORAGE_KEY = 'eve_sidebar_collapsed';

    function setCollapsed(collapsed) {
        document.documentElement.classList.toggle('eve-sidebar-collapsed', collapsed);
        const btn = document.getElementById('eveSidebarCollapseBtn');
        if (btn) {
            btn.setAttribute('aria-expanded', String(!collapsed));
            btn.setAttribute('title', collapsed ? 'Expand sidebar' : 'Collapse sidebar');
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = collapsed ? 'bi bi-chevron-double-right' : 'bi bi-chevron-double-left';
            }
        }
        try {
            localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0');
        } catch (e) {}
    }

    function closeDrawer() {
        document.body.classList.remove('eve-drawer-open');
        const btn = document.getElementById('eveMobileMenuBtn');
        if (btn) btn.setAttribute('aria-expanded', 'false');
    }

    function openDrawer() {
        document.body.classList.add('eve-drawer-open');
        const btn = document.getElementById('eveMobileMenuBtn');
        if (btn) btn.setAttribute('aria-expanded', 'true');
    }

    document.addEventListener('DOMContentLoaded', function () {
        try {
            if (localStorage.getItem(STORAGE_KEY) === '1') {
                setCollapsed(true);
            }
        } catch (e) {}

        const collapseBtn = document.getElementById('eveSidebarCollapseBtn');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', function () {
                const isCollapsed = document.documentElement.classList.contains('eve-sidebar-collapsed');
                setCollapsed(!isCollapsed);
            });
        }

        const mobileBtn = document.getElementById('eveMobileMenuBtn');
        if (mobileBtn) {
            mobileBtn.addEventListener('click', function () {
                if (document.body.classList.contains('eve-drawer-open')) {
                    closeDrawer();
                } else {
                    openDrawer();
                }
            });
        }

        const backdrop = document.getElementById('eveSidebarBackdrop');
        if (backdrop) {
            backdrop.addEventListener('click', closeDrawer);
        }

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && document.body.classList.contains('eve-drawer-open')) {
                closeDrawer();
            }
        });
    });
})();

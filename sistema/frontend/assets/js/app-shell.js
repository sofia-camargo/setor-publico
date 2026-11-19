(function () {
    const token = localStorage.getItem('jwt_token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!token || !user) { window.location.replace('index.html'); return; }

    const frames = Array.from(document.querySelectorAll('.content-frame'));
    let activeFrame = frames[0];
    let pendingFrame = null;
    const workspace = document.querySelector('.shell-workspace');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const links = Array.from(document.querySelectorAll('#shell-menu a'));
    const title = document.getElementById('shell-title');
    document.getElementById('shell-user-name').textContent = user.nome || 'Usuário';
    document.getElementById('shell-user-role').textContent = user.nivel_acesso || '';
    document.getElementById('shell-user-avatar').textContent = (user.nome || 'U').charAt(0).toUpperCase();
    if (user.nivel_acesso === 'Administrador' || user.nivel_acesso === 'Gestor') document.getElementById('shell-menu-usuarios').style.display = 'block';
    if (['Administrador', 'Gestor', 'Secretário'].includes(user.nivel_acesso)) document.getElementById('shell-menu-assistente').style.display = 'block';
    if (user.visao_estrategica) document.getElementById('shell-menu-cruzados').style.display = 'block';

    function setSidebarCollapsed(collapsed) {
        document.body.classList.toggle('sidebar-collapsed', collapsed);
        sidebarToggle.setAttribute('aria-expanded', String(!collapsed));
        sidebarToggle.setAttribute('aria-label', collapsed ? 'Expandir menu lateral' : 'Recolher menu lateral');
        sidebarToggle.setAttribute('title', collapsed ? 'Expandir menu lateral' : 'Recolher menu lateral');
        localStorage.setItem('sigdei_sidebar_collapsed', String(collapsed));
    }
    setSidebarCollapsed(localStorage.getItem('sigdei_sidebar_collapsed') === 'true');
    sidebarToggle.addEventListener('click', () => setSidebarCollapsed(!document.body.classList.contains('sidebar-collapsed')));

    function viewUrl(href) { return `${href}${href.includes('?') ? '&' : '?'}embedded=1`; }
    function selectLink(href) {
        links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === href));
        const active = links.find(link => link.getAttribute('href') === href);
        title.textContent = active ? active.dataset.title : 'SIGDEI';
    }
    function navigate(href, updateHistory = true) {
        selectLink(href);
        if (pendingFrame) return;
        pendingFrame = frames.find(frame => frame !== activeFrame);
        workspace.classList.add('is-loading');
        pendingFrame.classList.add('is-loading');
        pendingFrame.src = viewUrl(href);
        if (updateHistory) history.pushState({ href }, '', `dashboard.html?view=${encodeURIComponent(href)}`);
    }
    links.forEach(link => link.addEventListener('click', event => { event.preventDefault(); navigate(link.getAttribute('href')); }));
    document.getElementById('shell-logout').addEventListener('click', () => { localStorage.clear(); window.location.replace('index.html'); });
    window.addEventListener('popstate', event => navigate((event.state && event.state.href) || 'dashboard-content.html', false));

    function prepareFrame(frame) {
        const doc = frame.contentDocument;
        if (!doc) return;
        doc.body.classList.add('embedded-view');
        doc.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', event => {
                const href = link.getAttribute('href');
                if (!href || href === '#') return;
                event.preventDefault();
                navigate(href);
            });
        });
    }

    frames.forEach(frame => frame.addEventListener('load', () => {
        prepareFrame(frame);
        if (frame !== pendingFrame) return;
        requestAnimationFrame(() => {
            frame.classList.remove('is-loading');
            frame.classList.add('is-active');
            activeFrame.classList.remove('is-active');
            const previousFrame = activeFrame;
            activeFrame = frame;
            pendingFrame = null;
            setTimeout(() => {
                previousFrame.src = 'about:blank';
                workspace.classList.remove('is-loading');
            }, 220);
        });
    }));

    const initial = new URLSearchParams(window.location.search).get('view') || 'dashboard-content.html';
    if (initial !== 'dashboard-content.html') navigate(initial, false);
})();

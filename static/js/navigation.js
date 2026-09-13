// navigation.js — Sidebar toggle + tab switching

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('active');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('active');
}

function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.getElementById(tab + 'Tab').classList.add('active');

    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const sn = document.getElementById('snav-' + tab);
    if (sn) sn.classList.add('active');

    document.querySelectorAll('.bnav-item').forEach(el => el.classList.remove('active'));
    const bn = document.getElementById('bnav-' + tab);
    if (bn) bn.classList.add('active');

    AppState.currentTab = tab;

    if (tab === 'dashboard') {
        loadDashboard();
        // Force a second load after 500ms to ensure data updates
        setTimeout(loadDashboard, 500);
    }
    if (tab === 'sales') loadSales();
    if (tab === 'expenses') loadExpenses();
    if (tab === 'credits') loadCredits();
    if (tab === 'calendar') initCalendar();
    closeSidebar();
}

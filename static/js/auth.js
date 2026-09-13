// auth.js — Login, logout, auto-login check

async function doLogout() {
    await api('/logout', 'POST');
    document.getElementById('appPage').style.display = 'none';
    document.getElementById('loginPage').style.display = 'flex';
}

// Expose as `logout` for the sidebar button onclick
window.logout = doLogout;

function bindLoginForm() {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const errDiv = document.getElementById('loginError');
        errDiv.style.display = 'none';
        try {
            const result = await api('/login', 'POST', {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            });
            if (result.success) {
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('appPage').style.display = 'block';
                const name = result.full_name || document.getElementById('username').value;
                document.getElementById('userName').textContent = name;
                document.getElementById('userNameMobile').textContent = name;
                await loadItems();
                await loadCategories();
                loadDashboard();
            } else {
                errDiv.textContent = result.error || 'Login failed';
                errDiv.style.display = 'block';
            }
        } catch {
            errDiv.textContent = 'Connection error';
            errDiv.style.display = 'block';
        }
    });
}

async function checkAuthAndResume() {
    try {
        const result = await api('/check-auth');
        if (result.authenticated) {
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('appPage').style.display = 'block';
            const name = result.full_name || result.user;
            document.getElementById('userName').textContent = name;
            document.getElementById('userNameMobile').textContent = name;
            await loadItems();
            await loadCategories();
            loadDashboard();
        }
    } catch {}
}

// auth.js — Login, register, logout, auto-login check

async function doLogout() {
    await api('/logout', 'POST');
    document.getElementById('appPage').style.display = 'none';
    document.getElementById('loginPage').style.display = 'flex';
}

window.logout = doLogout;

// ─── LOGIN ───
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
                await enterApp(result);
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

// ─── REGISTER ───
function bindRegisterForm() {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const errDiv = document.getElementById('loginError');
        errDiv.style.display = 'none';
        try {
            const result = await api('/register', 'POST', {
                username: document.getElementById('regUsername').value.trim(),
                password: document.getElementById('regPassword').value,
                full_name: document.getElementById('regFullName').value.trim(),
                email: document.getElementById('regEmail').value.trim(),
                company_name: document.getElementById('regCompany').value.trim()
            });
            if (result.success) {
                await enterApp(result);
            } else {
                errDiv.textContent = result.error || 'Registration failed';
                errDiv.style.display = 'block';
            }
        } catch {
            errDiv.textContent = 'Connection error';
            errDiv.style.display = 'block';
        }
    });

    // Toggle between login and register forms
    document.getElementById('showRegister').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'block';
        document.getElementById('showRegister').style.display = 'none';
        document.getElementById('showLogin').style.display = 'inline';
    });
    document.getElementById('showLogin').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('registerForm').style.display = 'none';
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('showLogin').style.display = 'none';
        document.getElementById('showRegister').style.display = 'inline';
    });
}

// ─── SHARED — enter app after successful login/register ───
async function enterApp(result) {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('appPage').style.display = 'block';
    const name = result.full_name || result.user;
    document.getElementById('userName').textContent = name;
    document.getElementById('userNameMobile').textContent = name;
    // Show company name somewhere — optional
    if (result.company) {
        console.log('Company:', result.company);
    }
    await loadItems();
    await loadCategories();
    loadDashboard();
}

// ─── AUTO-LOGIN CHECK ───
async function checkAuthAndResume() {
    try {
        const result = await api('/check-auth');
        if (result.authenticated) {
            await enterApp({
                full_name: result.full_name,
                user: result.user,
                company: result.company
            });
        }
    } catch {}
}
// api.js — Fetch wrapper + shared app state

// Compute base path so API calls work at subpath (e.g. /haven/)
// e.g. URL = https://www.jtech.et/haven/  →  BASE_PATH = /haven
// e.g. URL = https://www.jtech.et/haven   →  BASE_PATH = /haven
// e.g. URL = https://www.jtech.et/        →  BASE_PATH = ''
const BASE_PATH = window.location.pathname.replace(/\/$/, '');
const API = window.location.origin + BASE_PATH + '/api';

// Shared state (global to all modules)
const AppState = {
    deleteTarget: null,
    deleteType: null,
    allItems: [],
    allCategories: [],
    salesData: [],
    expensesData: [],
    calendarInst: null,
    currentTab: 'dashboard'
};

async function api(endpoint, method = 'GET', data = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    };
    if (data) opts.body = JSON.stringify(data);
    const res = await fetch(API + endpoint, opts);
    return res.json();
}

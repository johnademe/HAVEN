// api.js — Fetch wrapper + shared app state

const API = window.location.origin + '/api';

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

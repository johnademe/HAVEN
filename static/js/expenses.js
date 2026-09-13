// expenses.js — Expenses CRUD + modal

async function loadExpenses() {
    try {
        AppState.expensesData = (await api('/expenses')) || [];
        renderExpenses(AppState.expensesData);
    } catch {}
}

function renderExpenses(data) {
    const tbody = document.getElementById('expensesTableBody');
    if (!data.length) {
        tbody.innerHTML =
            '<tr class="empty-row"><td colspan="5"><div class="empty-state"><i class="fas fa-receipt"></i><p>No expenses yet</p></div></td></tr>';
        return;
    }
    tbody.innerHTML = data.map(e => `
        <tr>
            <td><span class="badge badge-red">${e.category}</span></td>
            <td style="color:var(--text-2);font-size:12px">${e.description || '—'}</td>
            <td><span style="font-weight:700;color:var(--red)">$${parseFloat(e.amount).toFixed(2)}</span></td>
            <td style="color:var(--text-2);font-size:12px">${e.expense_date || '—'}</td>
            <td>
                <button class="icon-btn edit" onclick="editExpense(${e.id})"><i class="fas fa-pen"></i></button>
                <button class="icon-btn delete" onclick="deleteExpense(${e.id})" style="margin-left:6px"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

function openExpenseModal(data = null) {
    document.getElementById('expenseModal').classList.add('open');
    document.getElementById('categoryAutocompleteList').classList.remove('open');
    if (data) {
        document.getElementById('expenseEditId').value = data.id;
        document.getElementById('expenseCategory').value = data.category;
        document.getElementById('expenseAmount').value = data.amount;
        document.getElementById('expenseDescription').value = data.description || '';
        document.getElementById('expenseDate').value = data.expense_date;
    } else {
        document.getElementById('expenseEditId').value = '';
        document.getElementById('expenseForm').reset();
        document.getElementById('expenseDate').value = new Date().toISOString().split('T')[0];
    }
}

function closeExpenseModal() {
    document.getElementById('expenseModal').classList.remove('open');
}

async function editExpense(id) {
    const e = AppState.expensesData.find(e => e.id === id);
    if (e) openExpenseModal(e);
}

function deleteExpense(id) {
    AppState.deleteTarget = id;
    AppState.deleteType = 'expense';
    document.getElementById('deleteModal').classList.add('open');
}

function bindExpenseForm() {
    document.getElementById('expenseForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('expenseEditId').value;
        const data = {
            category: document.getElementById('expenseCategory').value,
            amount: parseFloat(document.getElementById('expenseAmount').value),
            description: document.getElementById('expenseDescription').value || 'Expense',
            expense_date: document.getElementById('expenseDate').value || new Date().toISOString().split('T')[0]
        };
        const result = await api(id ? `/expense/${id}` : '/expenses', id ? 'PUT' : 'POST', data);
        if (result.success || result.status === 'updated') {
            closeExpenseModal();
            await loadCategories();
            loadExpenses();
            loadDashboard();
        } else {
            alert(result.error || 'Error saving expense');
        }
    });
}

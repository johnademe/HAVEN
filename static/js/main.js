// main.js — Init + global event bindings

// ─── DELETE ───
async function confirmDelete() {
    if (!AppState.deleteTarget || !AppState.deleteType) return;
    const result = await api(
        AppState.deleteType === 'sale'
            ? `/sale/${AppState.deleteTarget}`
            : `/expense/${AppState.deleteTarget}`,
        'DELETE'
    );
    if (result.status === 'deleted') {
        closeDeleteModal();
        if (AppState.deleteType === 'sale') loadSales();
        else loadExpenses();
        loadDashboard();
    } else {
        alert('Error deleting');
    }
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('open');
    AppState.deleteTarget = null;
    AppState.deleteType = null;
}

// ─── INIT ───


document.addEventListener('DOMContentLoaded', () => {
    bindLoginForm();
    bindRegisterForm();      
    bindSaleForm();
    bindExpenseForm();


    // Close modals on overlay click
    ['saleModal', 'expenseModal', 'deleteModal'].forEach(id => {
        document.getElementById(id).addEventListener('click', (e) => {
            if (e.target === document.getElementById(id)) {
                if (id === 'saleModal') closeSaleModal();
                else if (id === 'expenseModal') closeExpenseModal();
                else closeDeleteModal();
            }
        });
    });

    // Auto-login check
    checkAuthAndResume();
});

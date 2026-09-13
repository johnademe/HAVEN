// sales.js — Sales CRUD, summary, modal

async function loadSales() {
    try {
        AppState.salesData = (await api('/recent')) || [];
        renderSales(AppState.salesData);
    } catch {}
}

function renderSales(data) {
    const tbody = document.getElementById('salesTableBody');
    if (!data.length) {
        tbody.innerHTML =
            '<tr class="empty-row"><td colspan="5"><div class="empty-state"><i class="fas fa-shopping-cart"></i><p>No sales yet</p><small>Tap New Sale to get started</small></div></td></tr>';
        return;
    }
    tbody.innerHTML = data.map(s => `
        <tr>
            <td style="font-weight:600">${s.item}</td>
            <td>${s.customer_name ? `<span class="badge badge-gray">${s.customer_name}</span>` : '<span style="color:var(--text-3)">—</span>'}</td>
            <td><span style="font-weight:700;color:var(--blue)">$${parseFloat(s.total).toFixed(2)}</span></td>
            <td style="color:var(--text-2);font-size:12px">${s.sale_date || '—'}</td>
            <td>
                <button class="icon-btn edit" onclick="editSale(${s.id})" title="Edit"><i class="fas fa-pen"></i></button>
                <button class="icon-btn delete" onclick="deleteSale(${s.id})" title="Delete" style="margin-left:6px"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

function openSaleModal(data = null) {
    document.getElementById('saleModal').classList.add('open');
    document.getElementById('autocompleteList').classList.remove('open');
    if (data) {
        document.getElementById('saleEditId').value = data.id;
        document.getElementById('saleItem').value = data.item;
        document.getElementById('customerName').value = data.customer_name || '';
        document.getElementById('saleQuantity').value = data.quantity;
        document.getElementById('salePrice').value = data.price;
        document.getElementById('saleCredit').value = data.credit || 0;
        document.getElementById('saleDate').value = data.sale_date;
    } else {
        document.getElementById('saleEditId').value = '';
        document.getElementById('saleForm').reset();
        document.getElementById('saleQuantity').value = 1;
        document.getElementById('saleCredit').value = 0;
        document.getElementById('saleDate').value = new Date().toISOString().split('T')[0];
    }
}

function closeSaleModal() {
    document.getElementById('saleModal').classList.remove('open');
}

async function editSale(id) {
    const s = AppState.salesData.find(s => s.id === id);
    if (s) openSaleModal(s);
}

function deleteSale(id) {
    AppState.deleteTarget = id;
    AppState.deleteType = 'sale';
    document.getElementById('deleteModal').classList.add('open');
}

function bindSaleForm() {
    document.getElementById('saleForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('saleEditId').value;
        const data = {
            item: document.getElementById('saleItem').value,
            customer_name: document.getElementById('customerName').value || '',
            quantity: parseInt(document.getElementById('saleQuantity').value),
            price: parseFloat(document.getElementById('salePrice').value),
            credit: parseFloat(document.getElementById('saleCredit').value) || 0,
            sale_date: document.getElementById('saleDate').value || new Date().toISOString().split('T')[0]
        };
        const result = await api(id ? `/sale/${id}` : '/sale', id ? 'PUT' : 'POST', data);
        if (result.id || result.status === 'updated') {
            closeSaleModal();
            loadSales();
            loadDashboard();
        } else {
            alert(result.error || 'Error saving sale');
        }
    });
}

// ─── SALES SUMMARY ───
async function loadSalesSummary() {
    try {
        const item = document.getElementById('salesItemFilter').value;
        const startDate = document.getElementById('salesStartDate').value;
        const endDate = document.getElementById('salesEndDate').value;

        let url = '/sales/summary?';
        if (item) url += `item=${encodeURIComponent(item)}&`;
        if (startDate) url += `start_date=${startDate}&`;
        if (endDate) url += `end_date=${endDate}`;

        const data = await api(url);

        document.getElementById('salesSummaryCount').textContent = data.totals?.total_sales || 0;
        document.getElementById('salesSummaryRevenue').textContent = '$' + (data.totals?.total_revenue || 0);
        document.getElementById('salesSummaryNet').textContent = '$' + (data.totals?.total_net || 0);
        document.getElementById('salesSummaryCredit').textContent = '$' + (data.totals?.total_credit || 0);
        document.getElementById('salesSummaryItems').textContent = data.items?.length || 0;

        const tbody = document.getElementById('salesSummaryBody');
        if (!data.items?.length) {
            tbody.innerHTML = '<tr class="empty-row"><td colspan="5"><div class="empty-state"><i class="fas fa-chart-bar"></i><p>No items found</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.items.map(item => `
            <tr>
                <td style="font-weight:600">${item.item}</td>
                <td>${item.count}</td>
                <td><span style="font-weight:700;color:var(--blue)">$${parseFloat(item.total).toFixed(2)}</span></td>
                <td style="color:var(--amber)">$${parseFloat(item.total_credit).toFixed(2)}</td>
                <td><span style="font-weight:700;color:var(--green)">$${parseFloat(item.net).toFixed(2)}</span></td>
            </tr>
        `).join('');
    } catch (e) {
        console.log('Sales summary error:', e);
    }
}

function clearSalesFilters() {
    document.getElementById('salesItemFilter').value = '';
    document.getElementById('salesStartDate').value = '';
    document.getElementById('salesEndDate').value = '';
    loadSalesSummary();
}

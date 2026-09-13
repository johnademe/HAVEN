// reports.js — Profit & loss report

async function loadReport(type) {
    const container = document.getElementById('reportContent');
    const today = new Date();
    let startDate, endDate;
    if (type === 'daily') {
        startDate = endDate = today.toISOString().split('T')[0];
    } else if (type === 'weekly') {
        const s = new Date(today);
        s.setDate(today.getDate() - 7);
        startDate = s.toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
    } else {
        startDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
    }
    container.innerHTML = '<div class="spinner"><i class="fas fa-spinner fa-spin"></i></div>';
    try {
        const data = await api(`/reports/profit-loss?start_date=${startDate}&end_date=${endDate}`);
        container.innerHTML = `
            <div class="report-grid">
                <div class="report-box blue">
                    <div class="rb-label">Revenue</div>
                    <div class="rb-value">$${parseFloat(data.revenue?.total_revenue || 0).toFixed(2)}</div>
                </div>
                <div class="report-box red">
                    <div class="rb-label">Expenses</div>
                    <div class="rb-value">$${parseFloat(data.expenses?.total_expenses || 0).toFixed(2)}</div>
                </div>
                <div class="report-box green">
                    <div class="rb-label">Net Profit</div>
                    <div class="rb-value">$${parseFloat(data.profit?.net_profit || 0).toFixed(2)}</div>
                </div>
                <div class="report-box purple">
                    <div class="rb-label">Margin</div>
                    <div class="rb-value">${data.profit?.profit_margin || 0}%</div>
                </div>
            </div>
            <div style="text-align:center;font-size:11px;color:var(--text-3);margin-top:16px;padding-top:12px;border-top:1px solid var(--border)">
                ${data.period?.start_date} → ${data.period?.end_date}
            </div>`;
    } catch {
        container.innerHTML =
            '<div class="empty-state"><i class="fas fa-exclamation-circle" style="color:var(--red)"></i><p>Error loading report</p></div>';
    }
}

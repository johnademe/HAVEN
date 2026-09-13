// credits.js — Pending credits + payment

async function loadCredits() {
    try {
        const data = await api('/credits/pending');
        document.getElementById('totalPending').textContent = '$' + (data.total_pending || 0);
        const tbody = document.getElementById('creditsTableBody');
        if (!data.pending_credits?.length) {
            tbody.innerHTML =
                '<tr class="empty-row"><td colspan="5"><div class="empty-state"><i class="fas fa-check-circle" style="color:var(--green)"></i><p>No pending credits</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.pending_credits.map(c => `
            <tr>
                <td style="font-weight:600">${c.item}</td>
                <td>${c.customer_name ? `<span class="badge badge-gray">${c.customer_name}</span>` : '—'}</td>
                <td><span style="font-weight:700;color:var(--amber)">$${parseFloat(c.amount).toFixed(2)}</span></td>
                <td style="color:var(--text-2);font-size:12px">${c.sale_date || '—'}</td>
                <td>
                    <button class="btn" style="background:var(--green);color:white;font-size:12px;padding:6px 14px;border-radius:20px;" onclick="payCredit(${c.sale_id},${c.amount})">
                        <i class="fas fa-check"></i> Pay
                    </button>
                </td>
            </tr>
        `).join('');
    } catch {}
}

async function payCredit(saleId, maxAmount) {
    const amount = prompt(`Enter amount (max: $${maxAmount})`, maxAmount);
    if (!amount) return;
    const result = await api(`/credits/pay/${saleId}`, 'POST', { amount: parseFloat(amount) });
    if (result.success) {
        alert(`✅ Paid $${result.amount_paid}\nRemaining: $${result.remaining_credit}`);
        loadCredits();
        loadDashboard();
    } else {
        alert('❌ ' + (result.error || 'Error'));
    }
}

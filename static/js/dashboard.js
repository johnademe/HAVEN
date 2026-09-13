// dashboard.js — Dashboard stats loader

async function loadDashboard() {
    try {
        const data = await api('/reports/summary');
        document.getElementById('todayRevenue').textContent = '$' + (data.today?.revenue || 0);
        document.getElementById('todayNet').textContent = '$' + (data.today?.net_revenue || 0);
        document.getElementById('todayExpenses').textContent = '$' + (data.today?.expenses || 0);
        document.getElementById('todayProfit').textContent = '$' + (data.today?.profit || 0);
        document.getElementById('todaysCredit').textContent = '$' + (data.todays_credit || 0);
        document.getElementById('pendingCredits').textContent = '$' + (data.pending_credits || 0);
        document.getElementById('monthRevenue').textContent = '$' + (data.month_to_date?.revenue || 0);
        document.getElementById('monthNet').textContent = '$' + (data.month_to_date?.net_revenue || 0);

        // Get daily required sales
        try {
            const required = await api('/sales/daily-required');
            console.log('Daily required response:', required);
            // Use Number() to ensure numeric values
            document.getElementById('todaySalesCount').textContent = Number(required.today_count) || 0;
            document.getElementById('salesNeeded').textContent = Number(required.sales_needed) || 0;
        } catch (e) {
            console.log('Daily required not available:', e);
        }
    } catch (e) {
        console.log('Dashboard error:', e);
    }
}

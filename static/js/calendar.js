// calendar.js — FullCalendar setup

function initCalendar() {
    if (AppState.calendarInst) {
        AppState.calendarInst.destroy();
    }
    AppState.calendarInst = new FullCalendar.Calendar(document.getElementById('calendar'), {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
        },
        height: 'auto',
        dayMaxEvents: true,
        events: async (info, success, fail) => {
            try {
                const data = await api('/calendar-data?start=' + info.startStr + '&end=' + info.endStr);
                const events = [];
                Object.keys(data).forEach(date => {
                    const d = data[date];
                    if (d.revenue > 0) events.push({
                        title: '💰 $' + d.revenue.toFixed(2),
                        start: date,
                        color: '#3B82F6',
                        textColor: 'white',
                        extendedProps: d
                    });
                    if (d.expenses > 0) events.push({
                        title: '💳 $' + d.expenses.toFixed(2),
                        start: date,
                        color: '#EF4444',
                        textColor: 'white',
                        extendedProps: d
                    });
                });
                success(events);
            } catch (e) {
                fail(e);
            }
        },
        eventClick: (info) => {
            const p = info.event.extendedProps;
            alert(
                `📅 ${info.event.startStr}\n\n💰 Revenue: $${(p.revenue||0).toFixed(2)}\n💳 Expenses: $${(p.expenses||0).toFixed(2)}\n📈 Profit: $${(p.profit||0).toFixed(2)}`
            );
        }
    });
    AppState.calendarInst.render();
}

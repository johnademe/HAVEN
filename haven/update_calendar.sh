#!/bin/bash

# Backup
cp index.html index.html.backup.$(date +%Y%m%d_%H%M%S)

# Use sed to replace the entire initCalendar function
sed -i '/function initCalendar() {/,/calendar.render();/c\
        function initCalendar() {\
            if (calendar) { calendar.destroy(); }\
            const calendarEl = document.getElementById("calendar");\
            calendar = new FullCalendar.Calendar(calendarEl, {\
                initialView: "dayGridMonth",\
                headerToolbar: {\
                    left: "prev,next today",\
                    center: "title",\
                    right: "dayGridMonth,dayGridWeek"\
                },\
                height: "auto",\
                dayMaxEvents: true,\
                events: async function(info, successCallback, failureCallback) {\
                    try {\
                        const start = info.startStr;\
                        const end = info.endStr;\
                        const data = await api("/calendar-data?start=" + start + "&end=" + end);\
                        const events = [];\
                        Object.keys(data).forEach(date => {\
                            const day = data[date];\
                            const revenue = day.revenue || 0;\
                            const expenses = day.expenses || 0;\
                            const profit = day.profit || 0;\
                            if (revenue > 0) {\
                                events.push({\
                                    title: "💰 $" + revenue.toFixed(2),\
                                    start: date,\
                                    color: "#3b82f6",\
                                    textColor: "white",\
                                    extendedProps: { revenue: revenue, expenses: expenses, profit: profit }\
                                });\
                            }\
                            if (expenses > 0) {\
                                events.push({\
                                    title: "💳 $" + expenses.toFixed(2),\
                                    start: date,\
                                    color: "#ef4444",\
                                    textColor: "white",\
                                    extendedProps: { revenue: revenue, expenses: expenses, profit: profit }\
                                });\
                            }\
                        });\
                        successCallback(events);\
                    } catch (e) {\
                        console.error("Calendar error:", e);\
                        failureCallback(e);\
                    }\
                },\
                eventClick: function(info) {\
                    const date = info.event.startStr;\
                    const props = info.event.extendedProps;\
                    const revenue = props.revenue || 0;\
                    const expenses = props.expenses || 0;\
                    const profit = props.profit || 0;\
                    alert(\
                        " 📅 Date: " + date + "\\n\\n" +\
                        "💰 Revenue: $" + revenue.toFixed(2) + "\\n" +\
                        "💳 Expenses: $" + expenses.toFixed(2) + "\\n" +\
                        "📊 Profit: $" + profit.toFixed(2)\
                    );\
                }\
            });\
            calendar.render();\
        }' index.html

echo "✅ Calendar updated!"

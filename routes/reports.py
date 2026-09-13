# routes/reports.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/api/revenue/today')
@login_required
def revenue_today():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT
            COALESCE(SUM(total),0) as total,
            COALESCE(SUM(credit),0) as credit,
            COALESCE(SUM(total - credit),0) as net,
            COUNT(*) as transactions
        FROM sales
        WHERE sale_date = CURRENT_DATE AND company_id = %s
    """, (session['company_id'],))
    data = cur.fetchone()
    cur.execute("""
        SELECT id, item, quantity, price, total, credit, sale_date, customer_name
        FROM sales
        WHERE sale_date = CURRENT_DATE AND company_id = %s
        ORDER BY id DESC
    """, (session['company_id'],))
    data['sales'] = cur.fetchall()
    conn.close()
    return jsonify(data)


@reports_bp.route('/api/reports/summary')
@login_required
def summary_report():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            COALESCE(SUM(total), 0) as revenue,
            COALESCE(SUM(credit), 0) as credit,
            COUNT(*) as sales_count
        FROM sales
        WHERE sale_date = CURRENT_DATE AND company_id = %s
    """, (session['company_id'],))
    today_sales = cur.fetchone()

    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as expenses
        FROM expenses
        WHERE expense_date = CURRENT_DATE AND company_id = %s
    """, (session['company_id'],))
    today_expenses = cur.fetchone()

    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as todays_credit
        FROM credits
        WHERE status = 'pending'
        AND company_id = %s
        AND created_at >= CURRENT_DATE
    """, (session['company_id'],))
    todays_credit = cur.fetchone()

    cur.execute("""
        SELECT
            COALESCE(SUM(total), 0) as revenue,
            COALESCE(SUM(credit), 0) as credit,
            COUNT(*) as sales_count
        FROM sales
        WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE) AND company_id = %s
    """, (session['company_id'],))
    month_sales = cur.fetchone()

    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as expenses
        FROM expenses
        WHERE expense_date >= DATE_TRUNC('month', CURRENT_DATE) AND company_id = %s
    """, (session['company_id'],))
    month_expenses = cur.fetchone()

    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as pending_credit
        FROM credits
        WHERE status = 'pending' AND company_id = %s
    """, (session['company_id'],))
    credit_summary = cur.fetchone()

    conn.close()

    return jsonify({
        "today": {
            "revenue": today_sales['revenue'],
            "credit": today_sales['credit'],
            "net_revenue": today_sales['revenue'] - today_sales['credit'],
            "expenses": today_expenses['expenses'],
            "profit": today_sales['revenue'] - today_sales['credit'] - today_expenses['expenses'],
            "sales_count": today_sales['sales_count']
        },
        "month_to_date": {
            "revenue": month_sales['revenue'],
            "credit": month_sales['credit'],
            "net_revenue": month_sales['revenue'] - month_sales['credit'],
            "expenses": month_expenses['expenses'],
            "profit": month_sales['revenue'] - month_sales['credit'] - month_expenses['expenses'],
            "sales_count": month_sales['sales_count']
        },
        "pending_credits": credit_summary['pending_credit'],
        "todays_credit": todays_credit['todays_credit']
    })


@reports_bp.route('/api/reports/profit-loss', methods=['GET'])
@login_required
def profit_loss_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                COALESCE(SUM(total), 0) as total_revenue,
                COALESCE(SUM(credit), 0) as total_credit,
                COALESCE(SUM(total - credit), 0) as net_revenue,
                COUNT(*) as transaction_count
            FROM sales
            WHERE sale_date BETWEEN %s AND %s AND company_id = %s
        """, (start_date, end_date, session['company_id']))
        revenue = cur.fetchone()

        cur.execute("""
            SELECT
                COALESCE(SUM(amount), 0) as total_expenses,
                COUNT(*) as expense_count
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s AND company_id = %s
        """, (start_date, end_date, session['company_id']))
        expenses = cur.fetchone()

        net_profit = revenue['net_revenue'] - expenses['total_expenses']
        profit_margin = (net_profit / revenue['total_revenue'] * 100) if revenue['total_revenue'] > 0 else 0

        conn.close()

        return jsonify({
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "revenue": revenue,
            "expenses": expenses,
            "profit": {
                "net_profit": net_profit,
                "profit_margin": round(profit_margin, 2)
            }
        })
    except Exception as e:
        print(f"Profit/Loss error: {e}")
        return jsonify({"error": str(e)}), 500

# routes/calendar.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/api/calendar-data', methods=['GET'])
@login_required
def calendar_data():
    try:
        start = request.args.get('start')
        end = request.args.get('end')

        if not start or not end:
            return jsonify({"error": "Start and end dates required"}), 400

        try:
            if 'T' in start:
                start_date = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            else:
                start_date = start[:10]

            if 'T' in end:
                end_date = datetime.fromisoformat(end.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            else:
                end_date = end[:10]
        except:
            start_date = start[:10] if len(start) >= 10 else start
            end_date = end[:10] if len(end) >= 10 else end

        print(f"Calendar data: start={start_date}, end={end_date}, company_id={session.get('company_id')}")

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                sale_date as date,
                COALESCE(SUM(total), 0) as revenue,
                COALESCE(SUM(credit), 0) as credit,
                COALESCE(SUM(total - credit), 0) as net_revenue,
                COUNT(*) as sales_count
            FROM sales
            WHERE sale_date BETWEEN %s AND %s AND company_id = %s
            GROUP BY sale_date
            ORDER BY sale_date
        """, (start_date, end_date, session['company_id']))
        sales_by_date = cur.fetchall()

        cur.execute("""
            SELECT
                expense_date as date,
                COALESCE(SUM(amount), 0) as expenses,
                COUNT(*) as expense_count
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s AND company_id = %s
            GROUP BY expense_date
            ORDER BY expense_date
        """, (start_date, end_date, session['company_id']))
        expenses_by_date = cur.fetchall()

        conn.close()

        result = {}

        for row in sales_by_date:
            if row['date']:
                date_str = row['date'].strftime('%Y-%m-%d')
                result[date_str] = {
                    'revenue': float(row['revenue'] or 0),
                    'credit': float(row['credit'] or 0),
                    'net_revenue': float(row['net_revenue'] or 0),
                    'sales_count': row['sales_count'] or 0,
                    'expenses': 0,
                    'expense_count': 0,
                    'profit': float(row['net_revenue'] or 0)
                }

        for row in expenses_by_date:
            if row['date']:
                date_str = row['date'].strftime('%Y-%m-%d')
                expense_amount = float(row['expenses'] or 0)
                if date_str in result:
                    result[date_str]['expenses'] = expense_amount
                    result[date_str]['expense_count'] = row['expense_count'] or 0
                    result[date_str]['profit'] = result[date_str]['net_revenue'] - expense_amount
                else:
                    result[date_str] = {
                        'revenue': 0,
                        'credit': 0,
                        'net_revenue': 0,
                        'sales_count': 0,
                        'expenses': expense_amount,
                        'expense_count': row['expense_count'] or 0,
                        'profit': -expense_amount
                    }

        return jsonify(result)
    except Exception as e:
        print(f"Calendar data error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

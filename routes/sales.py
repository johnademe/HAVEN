# routes/sales.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/api/sale', methods=['POST'])
@login_required
def add_sale():
    try:
        data = request.json
        conn = get_db()
        cur = conn.cursor()

        total = data['quantity'] * data['price']
        credit = data.get('credit', 0)
        customer_name = data.get('customer_name', '')

        if credit > total:
            return jsonify({"error": "Credit cannot exceed total"}), 400

        cur.execute("""
            INSERT INTO sales (item, quantity, price, total, credit, sale_date, company_id, created_by, customer_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['item'],
            data['quantity'],
            data['price'],
            total,
            credit,
            data.get('sale_date', datetime.now().strftime("%Y-%m-%d")),
            session['company_id'],
            session['user_id'],
            customer_name
        ))
        sale_id = cur.fetchone()[0]

        if credit > 0:
            cur.execute("""
                INSERT INTO credits (sale_id, amount, status, due_date, company_id, customer_name)
                VALUES (%s, %s, 'pending', %s, %s, %s)
            """, (
                sale_id,
                credit,
                data.get('due_date', (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")),
                session['company_id'],
                customer_name
            ))

        conn.commit()
        conn.close()
        return jsonify({
            "id": sale_id,
            "total": total,
            "credit": credit,
            "net": total - credit
        })
    except Exception as e:
        print(f"Add sale error: {e}")
        return jsonify({"error": str(e)}), 500


@sales_bp.route('/api/sale/<int:sale_id>', methods=['PUT'])
@login_required
def update_sale(sale_id):
    try:
        data = request.json
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT company_id FROM sales WHERE id = %s", (sale_id,))
        sale = cur.fetchone()
        if not sale or sale[0] != session['company_id']:
            conn.close()
            return jsonify({"error": "Sale not found"}), 404

        total = data['quantity'] * data['price']
        credit = data.get('credit', 0)
        customer_name = data.get('customer_name', '')

        if credit > total:
            conn.close()
            return jsonify({"error": "Credit cannot exceed total"}), 400

        cur.execute("""
            UPDATE sales
            SET item = %s, quantity = %s, price = %s, total = %s,
                credit = %s, sale_date = %s, customer_name = %s
            WHERE id = %s RETURNING id
        """, (
            data['item'],
            data['quantity'],
            data['price'],
            total,
            credit,
            data.get('sale_date'),
            customer_name,
            sale_id
        ))
        updated = cur.fetchone()
        conn.commit()
        conn.close()

        if updated:
            return jsonify({"status": "updated", "id": sale_id, "total": total})
        return jsonify({"error": "Update failed"}), 500
    except Exception as e:
        print(f"Update sale error: {e}")
        return jsonify({"error": str(e)}), 500


@sales_bp.route('/api/sale/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT company_id FROM sales WHERE id = %s", (sale_id,))
        sale = cur.fetchone()
        if not sale or sale[0] != session['company_id']:
            conn.close()
            return jsonify({"error": "Sale not found"}), 404

        cur.execute("DELETE FROM credits WHERE sale_id = %s", (sale_id,))
        cur.execute("DELETE FROM sales WHERE id = %s RETURNING id", (sale_id,))
        deleted = cur.fetchone()
        conn.commit()
        conn.close()

        if deleted:
            return jsonify({"status": "deleted", "id": sale_id})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        print(f"Delete sale error: {e}")
        return jsonify({"error": str(e)}), 500


@sales_bp.route('/api/recent')
@login_required
def recent():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, item, quantity, price, total, credit, sale_date, customer_name
        FROM sales
        WHERE company_id = %s
        ORDER BY id DESC LIMIT 20
    """, (session['company_id'],))
    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@sales_bp.route('/api/sales/daily-required')
@login_required
def daily_sales_required():
    """Calculate how many more sales needed today to hit target"""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                COUNT(*) as count,
                COALESCE(SUM(total), 0) as revenue
            FROM sales
            WHERE sale_date = CURRENT_DATE
            AND company_id = %s
        """, (session['company_id'],))
        today_data = cur.fetchone()

        cur.execute("""
            SELECT
                COALESCE(AVG(daily_count), 0)::int as avg_daily_sales,
                COALESCE(AVG(daily_revenue), 0)::int as avg_daily_revenue
            FROM (
                SELECT
                    sale_date,
                    COUNT(*) as daily_count,
                    COALESCE(SUM(total), 0) as daily_revenue
                FROM sales
                WHERE sale_date >= (CURRENT_DATE - INTERVAL '30 days')
                AND sale_date < CURRENT_DATE
                AND company_id = %s
                GROUP BY sale_date
            ) daily_stats
        """, (session['company_id'],))
        avg_stats = cur.fetchone()

        conn.close()

        return jsonify({
            "today_count": today_data['count'] or 0,
            "today_revenue": today_data['revenue'] or 0,
            "avg_daily_sales": avg_stats['avg_daily_sales'] or 0,
            "avg_daily_revenue": avg_stats['avg_daily_revenue'] or 0,
            "sales_needed": max(0, (avg_stats['avg_daily_sales'] or 0) - (today_data['count'] or 0)),
            "revenue_needed": max(0, (avg_stats['avg_daily_revenue'] or 0) - (today_data['revenue'] or 0))
        })
    except Exception as e:
        print(f"Daily required error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@sales_bp.route('/api/sales/summary', methods=['GET'])
@login_required
def sales_summary():
    """Get sales summary with filters"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        item_filter = request.args.get('item')

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                item,
                COUNT(*) as count,
                COALESCE(SUM(total), 0) as total,
                COALESCE(SUM(credit), 0) as total_credit,
                COALESCE(SUM(total - credit), 0) as net
            FROM sales
            WHERE company_id = %s
        """
        params = [session['company_id']]

        if start_date:
            query += " AND sale_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND sale_date <= %s"
            params.append(end_date)
        if item_filter:
            query += " AND item ILIKE %s"
            params.append(f"%{item_filter}%")

        query += " GROUP BY item ORDER BY total DESC"

        cur.execute(query, params)
        data = cur.fetchall()

        total_query = """
            SELECT
                COUNT(*) as total_sales,
                COALESCE(SUM(total), 0) as total_revenue,
                COALESCE(SUM(credit), 0) as total_credit,
                COALESCE(SUM(total - credit), 0) as total_net
            FROM sales
            WHERE company_id = %s
        """
        total_params = [session['company_id']]

        if start_date:
            total_query += " AND sale_date >= %s"
            total_params.append(start_date)
        if end_date:
            total_query += " AND sale_date <= %s"
            total_params.append(end_date)
        if item_filter:
            total_query += " AND item ILIKE %s"
            total_params.append(f"%{item_filter}%")

        cur.execute(total_query, total_params)
        totals = cur.fetchone()

        conn.close()

        return jsonify({
            "items": data,
            "totals": {
                "total_sales": totals['total_sales'] or 0,
                "total_revenue": totals['total_revenue'] or 0,
                "total_credit": totals['total_credit'] or 0,
                "total_net": totals['total_net'] or 0
            }
        })
    except Exception as e:
        print(f"Sales summary error: {e}")
        return jsonify({"error": str(e)}), 500

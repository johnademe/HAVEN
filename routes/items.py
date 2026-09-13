# routes/items.py
from flask import Blueprint, jsonify, session
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

items_bp = Blueprint('items', __name__)


@items_bp.route('/api/items', methods=['GET'])
@login_required
def items():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT item_name, default_price, usage_count
        FROM items
        WHERE company_id = %s
        ORDER BY usage_count DESC, last_used DESC LIMIT 100
    """, (session['company_id'],))
    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@items_bp.route('/api/expense-categories', methods=['GET'])
@login_required
def expense_categories():
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT DISTINCT category, COUNT(*) as count
            FROM expenses
            WHERE company_id = %s
            GROUP BY category
            ORDER BY count DESC
        """, (session['company_id'],))
        data = cur.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        print(f"Expense categories error: {e}")
        return jsonify([])

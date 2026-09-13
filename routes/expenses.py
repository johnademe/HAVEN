# routes/expenses.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

expenses_bp = Blueprint('expenses', __name__)


@expenses_bp.route('/api/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        data = request.json
        required = ['category', 'amount']
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        cur.execute("""
            INSERT INTO expenses (category, amount, description, expense_date, company_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['category'],
            data['amount'],
            data.get('description', ''),
            data.get('expense_date', datetime.now().strftime("%Y-%m-%d")),
            session['company_id'],
            session['user_id']
        ))
        expense_id = cur.fetchone()['id']
        conn.commit()
        conn.close()
        return jsonify({"success": True, "id": expense_id})

    cur.execute("""
        SELECT id, category, amount, description, expense_date
        FROM expenses
        WHERE company_id = %s
        ORDER BY expense_date DESC LIMIT 100
    """, (session['company_id'],))
    expenses = cur.fetchall()
    conn.close()
    return jsonify(expenses)


@expenses_bp.route('/api/expense/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id):
    try:
        data = request.json
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT company_id FROM expenses WHERE id = %s", (expense_id,))
        expense = cur.fetchone()
        if not expense or expense[0] != session['company_id']:
            conn.close()
            return jsonify({"error": "Expense not found"}), 404

        cur.execute("""
            UPDATE expenses
            SET category = %s, amount = %s, description = %s, expense_date = %s
            WHERE id = %s RETURNING id
        """, (
            data['category'],
            data['amount'],
            data.get('description', ''),
            data.get('expense_date'),
            expense_id
        ))
        updated = cur.fetchone()
        conn.commit()
        conn.close()

        if updated:
            return jsonify({"status": "updated", "id": expense_id})
        return jsonify({"error": "Update failed"}), 500
    except Exception as e:
        print(f"Update expense error: {e}")
        return jsonify({"error": str(e)}), 500


@expenses_bp.route('/api/expense/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT company_id FROM expenses WHERE id = %s", (expense_id,))
        expense = cur.fetchone()
        if not expense or expense[0] != session['company_id']:
            conn.close()
            return jsonify({"error": "Expense not found"}), 404

        cur.execute("DELETE FROM expenses WHERE id = %s RETURNING id", (expense_id,))
        deleted = cur.fetchone()
        conn.commit()
        conn.close()

        if deleted:
            return jsonify({"status": "deleted", "id": expense_id})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        print(f"Delete expense error: {e}")
        return jsonify({"error": str(e)}), 500

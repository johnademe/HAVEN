# routes/credits.py
from flask import Blueprint, request, jsonify, session
from psycopg2.extras import RealDictCursor
from utils.db import get_db
from utils.decorators import login_required

credits_bp = Blueprint('credits', __name__)


@credits_bp.route('/api/credits/pending')
@login_required
def pending_credits():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT
            c.id, c.sale_id, c.amount, c.due_date, c.status,
            s.item, s.sale_date, s.customer_name
        FROM credits c
        JOIN sales s ON c.sale_id = s.id
        WHERE c.status = 'pending' AND c.company_id = %s
        ORDER BY c.id DESC
    """, (session['company_id'],))
    credits = cur.fetchall()
    total_pending = sum(credit['amount'] for credit in credits)
    conn.close()
    return jsonify({"pending_credits": credits, "total_pending": total_pending})


@credits_bp.route('/api/credits/pay/<int:sale_id>', methods=['POST'])
@login_required
def pay_credit(sale_id):
    try:
        data = request.json
        amount = data.get('amount', 0)

        if amount <= 0:
            return jsonify({"error": "Valid amount required"}), 400

        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT id, amount, status FROM credits
            WHERE sale_id = %s AND company_id = %s AND status = 'pending'
        """, (sale_id, session['company_id']))
        credit = cur.fetchone()

        if not credit:
            conn.close()
            return jsonify({"error": "No pending credit found"}), 404

        if amount > credit['amount']:
            conn.close()
            return jsonify({"error": f"Amount exceeds pending credit of {credit['amount']}"}), 400

        cur.execute("""
            UPDATE credits
            SET status = 'paid', paid_date = CURRENT_DATE, amount_paid = %s
            WHERE id = %s
        """, (amount, credit['id']))

        cur.execute("UPDATE sales SET credit = credit - %s WHERE id = %s", (amount, sale_id))

        remaining = credit['amount'] - amount
        if remaining <= 0:
            cur.execute("UPDATE sales SET credit = 0 WHERE id = %s", (sale_id,))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "amount_paid": amount,
            "remaining_credit": max(0, remaining)
        })
    except Exception as e:
        print(f"Pay credit error: {e}")
        return jsonify({"error": str(e)}), 500

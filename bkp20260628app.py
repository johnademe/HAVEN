from flask import Flask, request, jsonify, session
import psycopg2
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secret key for sessions

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'revenue_db',
    'user': 'haven',
    'password': 'haven'
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Please login first"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return jsonify({
            "message": "Revenue API",
            "user": session.get('username'),
            "endpoints": [
                "/api/revenue/today",
                "/api/revenue/week",
                "/api/revenue/month",
                "/api/revenue/date",
                "/api/revenue/date/summary",
                "/api/sale",
                "/api/items",
                "/api/recent"
            ]
        })
    return jsonify({"message": "Please login", "login_url": "/login"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Simple password check (for demo)
    # In production, use check_password_hash(user['password_hash'], password)
    if password == 'admin123':  # Replace with proper hash check
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"success": True, "user": username})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({"authenticated": True, "user": session.get('username')})
    return jsonify({"authenticated": False})

@app.route('/api/revenue/today')
@login_required
def today():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COALESCE(SUM(total),0) as total, COALESCE(SUM(credit),0) as credit FROM sales WHERE sale_date = CURRENT_DATE")
    data = cur.fetchone()
    cur.execute("SELECT id, item, quantity, price, total, credit, sale_date FROM sales WHERE sale_date = CURRENT_DATE ORDER BY id DESC")
    data['sales'] = cur.fetchall()
    conn.close()
    data['net'] = data['total'] - data['credit']
    return jsonify(data)

@app.route('/api/revenue/week')
@login_required
def week():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COALESCE(SUM(total),0) as total, COALESCE(SUM(credit),0) as credit, COUNT(*) as transactions FROM sales WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days'")
    data = cur.fetchone()
    cur.execute("SELECT id, item, quantity, price, total, credit, sale_date FROM sales WHERE sale_date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY sale_date DESC")
    data['sales'] = cur.fetchall()
    conn.close()
    data['net'] = data['total'] - data['credit']
    return jsonify(data)

@app.route('/api/revenue/month')
@login_required
def month():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COALESCE(SUM(total),0) as total, COALESCE(SUM(credit),0) as credit, COUNT(*) as transactions FROM sales WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE)")
    data = cur.fetchone()
    cur.execute("SELECT id, item, quantity, price, total, credit, sale_date FROM sales WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE) ORDER BY sale_date DESC")
    data['sales'] = cur.fetchall()
    conn.close()
    data['net'] = data['total'] - data['credit']
    return jsonify(data)

@app.route('/api/revenue/date')
@login_required
def date_revenue():
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COALESCE(SUM(total),0) as total, COALESCE(SUM(credit),0) as credit FROM sales WHERE sale_date = %s", (date,))
    data = cur.fetchone()
    cur.execute("SELECT id, item, quantity, price, total, credit, sale_date FROM sales WHERE sale_date = %s ORDER BY id DESC", (date,))
    data['sales'] = cur.fetchall()
    conn.close()
    data['net'] = data['total'] - data['credit']
    return jsonify(data)

@app.route('/api/revenue/date/summary')
@login_required
def date_summary():
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            item,
            COUNT(*) as transactions,
            SUM(quantity) as total_quantity,
            SUM(total) as total_revenue,
            SUM(credit) as total_credit,
            SUM(total - credit) as net_revenue
        FROM sales 
        WHERE sale_date = %s 
        GROUP BY item 
        ORDER BY total_revenue DESC
    """, (date,))
    summary = cur.fetchall()
    cur.execute("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(quantity) as total_items_sold,
            SUM(total) as total_revenue,
            SUM(credit) as total_credit,
            SUM(total - credit) as net_revenue
        FROM sales 
        WHERE sale_date = %s
    """, (date,))
    totals = cur.fetchone()
    conn.close()
    return jsonify({
        "date": date,
        "summary": summary,
        "totals": totals
    })

@app.route('/api/recent')
@login_required
def recent():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, item, quantity, price, total, credit, sale_date FROM sales ORDER BY id DESC LIMIT 20")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/api/sale', methods=['POST'])
@login_required
def add_sale():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    total = data['quantity'] * data['price']
    cur.execute("""
        INSERT INTO sales (item, quantity, price, total, credit, sale_date)
        VALUES (%s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE))
        RETURNING id
    """, (data['item'], data['quantity'], data['price'], total, data.get('credit', 0), data.get('sale_date')))
    sale_id = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO items (item_name, default_price, usage_count, last_used)
        VALUES (%s, %s, 1, CURRENT_DATE)
        ON CONFLICT (item_name) DO UPDATE SET
            usage_count = items.usage_count + 1,
            default_price = COALESCE(EXCLUDED.default_price, items.default_price),
            last_used = CURRENT_DATE
    """, (data['item'], data['price']))
    conn.commit()
    conn.close()
    return jsonify({"id": sale_id, "total": total})

@app.route('/api/sale/<int:sale_id>', methods=['PUT', 'DELETE'])
@login_required
def update_sale(sale_id):
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute("DELETE FROM sales WHERE id = %s RETURNING id", (sale_id,))
        deleted = cur.fetchone()
        conn.commit()
        conn.close()
        if deleted:
            return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404
    data = request.json
    total = data['quantity'] * data['price']
    cur.execute("""
        UPDATE sales
        SET item = %s, quantity = %s, price = %s, total = %s, credit = %s, sale_date = %s
        WHERE id = %s RETURNING id
    """, (data['item'], data['quantity'], data['price'], total, data.get('credit', 0), data.get('sale_date'), sale_id))
    updated = cur.fetchone()
    conn.commit()
    conn.close()
    if updated:
        return jsonify({"status": "updated", "id": sale_id, "total": total})
    return jsonify({"error": "Not found"}), 404

@app.route('/api/items', methods=['GET', 'POST'])
@login_required
def items():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        data = request.json
        cur.execute("""
            INSERT INTO items (item_name, default_price)
            VALUES (%s, %s)
            ON CONFLICT (item_name) DO UPDATE SET default_price = EXCLUDED.default_price
        """, (data['item_name'], data.get('default_price', 0)))
        conn.commit()
        conn.close()
        return jsonify({"status": "created"})
    cur.execute("SELECT item_name, default_price, usage_count FROM items ORDER BY usage_count DESC, last_used DESC LIMIT 100")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

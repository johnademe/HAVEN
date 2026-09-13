# Add these to your app.py - replace the existing endpoints

# ==================== UPDATE SALE ENDPOINT ====================
# Replace the /api/sale POST endpoint with this version that includes customer_name

@app.route('/api/sale', methods=['POST'])
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
            return jsonify({"error": "Credit cannot exceed total amount"}), 400

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
        print(f"Error adding sale: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== UPDATE RECENT ENDPOINT ====================
@app.route('/api/recent')
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

# ==================== UPDATE CREDITS PENDING ENDPOINT ====================
@app.route('/api/credits/pending')
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
        ORDER BY c.due_date ASC
    """, (session['company_id'],))
    credits = cur.fetchall()
    total_pending = sum(credit['amount'] for credit in credits)
    conn.close()
    return jsonify({"pending_credits": credits, "total_pending": total_pending})

# ==================== ADD MISSING PROFIT-LOSS ENDPOINT ====================
@app.route('/api/reports/profit-loss', methods=['GET'])
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
        
        # Get revenue
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
        
        # Get expenses
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

# ==================== UPDATE EXPENSES - ADD AUTOCOMPLETE ====================
# Add new endpoint for expense categories
@app.route('/api/expense-categories', methods=['GET'])
@login_required
def expense_categories():
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

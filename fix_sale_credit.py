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
            return jsonify({"error": "Credit cannot exceed total"}), 400

        # If there's credit, customer name is required
        if credit > 0 and not customer_name:
            return jsonify({"error": "Customer name is required when credit is given"}), 400

        # Insert sale with customer_name
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
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

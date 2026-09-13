# app.py
from flask import Flask, render_template
from config import SECRET_KEY

# Import blueprints
from routes.auth import auth_bp
from routes.items import items_bp
from routes.sales import sales_bp
from routes.expenses import expenses_bp
from routes.credits import credits_bp
from routes.reports import reports_bp
from routes.calendar import calendar_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(items_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(credits_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(calendar_bp)


# ==================== UI ROUTES ====================
@app.route('/')
@app.route('/ui')
@app.route('/dashboard')
def serve_ui():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

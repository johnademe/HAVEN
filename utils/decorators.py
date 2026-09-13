# utils/decorators.py
from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Please login first"}), 401
        if 'company_id' not in session:
            return jsonify({"error": "Please select a company"}), 400
        return f(*args, **kwargs)
    return decorated_function

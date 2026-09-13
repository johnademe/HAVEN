# config.py
import secrets

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'revenue_db',
    'user': 'haven',
    'password': 'haven'
}

SECRET_KEY = secrets.token_hex(32)

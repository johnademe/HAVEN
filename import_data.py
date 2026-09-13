import psycopg2
import csv
import re
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'revenue_db',
    'user': 'haven',
    'password': 'haven'
}

def clean_price(val):
    if not val or str(val).strip() == '':
        return 0
    val = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val)
    except:
        return 0

def import_from_csv(filename):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    added = 0
    
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 3:
                continue
                
            item = row[1].strip() if len(row) > 1 else ''
            qty = int(row[2]) if len(row) > 2 and row[2].strip() else 1
            price = clean_price(row[3]) if len(row) > 3 else 0
            credit = clean_price(row[5]) if len(row) > 5 else 0
            
            if not item or price == 0:
                continue
                
            total = qty * price
            sale_date = datetime.now().strftime("%Y-%m-%d")
            
            cur.execute("""
                INSERT INTO sales (item, quantity, price, total, credit, sale_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item, qty, price, total, credit, sale_date))
            
            # Update items
            cur.execute("""
                INSERT INTO items (item_name, default_price, usage_count, last_used) 
                VALUES (%s, %s, 1, %s) 
                ON CONFLICT (item_name) DO UPDATE SET 
                    usage_count = items.usage_count + 1,
                    default_price = COALESCE(EXCLUDED.default_price, items.default_price),
                    last_used = EXCLUDED.last_used
            """, (item, price, sale_date))
            
            added += 1
            print(f"Added: {item} x{qty} = ${total}")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Imported {added} sales!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 import_data.py data.csv")
        sys.exit(1)
    import_from_csv(sys.argv[1])

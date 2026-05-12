import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'store.db')
print(f"Connecting to {db_path}")
conn = sqlite3.connect(db_path)
# Update old categories to the new standard to hide them from expenses
conn.execute("UPDATE expenses SET category = 'INTERNAL_TRANSFER' WHERE category = 'تحويل_صندوق'")
# Also update the prefix one I used briefly
conn.execute("UPDATE expenses SET category = 'INTERNAL_TRANSFER' WHERE category LIKE 'TRANS:%'")
conn.commit()
print(f"Updated {conn.total_changes} rows.")
conn.close()

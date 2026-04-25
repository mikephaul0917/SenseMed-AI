import os
import sqlite3

db_path = os.path.join('agent_app', 'instance', 'drugs.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT drug_name, description, pro_tip, dosage_snapshot FROM drug")
rows = cursor.fetchall()

print("Current Database Status:")
for row in rows:
    print(f"Drug: {row[0]}")
    print(f"  Description: {row[1][:50]}..." if row[1] else "  Description: None")
    print(f"  Pro Tip: {row[2]}" if row[2] else "  Pro Tip: EMPTY")
    print(f"  Dosage: {row[3]}" if row[3] else "  Dosage: EMPTY")
    print("-" * 20)

conn.close()

import sqlite3
import os

db_path = os.path.join('agent_app', 'instance', 'drugs.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE side_effect_report ADD COLUMN side_effect_severity FLOAT DEFAULT 5.0')
    print("Added severity column.")
except sqlite3.OperationalError:
    print("Severity column already exists.")

try:
    cursor.execute('ALTER TABLE side_effect_report ADD COLUMN side_effect_demographics TEXT')
    print("Added demographics column.")
except sqlite3.OperationalError:
    print("Demographics column already exists.")

conn.commit()
conn.close()

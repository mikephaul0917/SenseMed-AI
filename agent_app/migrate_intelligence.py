import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'drugs.db')

def migrate():
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding pro_tip column to drug table...")
        cursor.execute("ALTER TABLE drug ADD COLUMN pro_tip TEXT")
    except sqlite3.OperationalError as e:
        print(f"Note: {e}")

    try:
        print("Adding dosage_snapshot column to drug table...")
        cursor.execute("ALTER TABLE drug ADD COLUMN dosage_snapshot TEXT")
    except sqlite3.OperationalError as e:
        print(f"Note: {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()

import sqlite3

conn = sqlite3.connect("data/pod_bot.db")
try:
    conn.execute("ALTER TABLE design_jobs ADD COLUMN ebay_item_id TEXT DEFAULT ''")
    conn.commit()
    print("Column added.")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("Column already exists.")
    else:
        raise
finally:
    conn.close()

import sqlite3

db_path = r"D:\intelligence_systems_site\instance\site_old.db"

con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r[0] for r in cur.fetchall()]

print("Tables found:")
for t in tables:
    print("-", t)

con.close()

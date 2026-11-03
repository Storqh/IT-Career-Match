import sqlite3

db = sqlite3.connect("database/it_career_match.db")

tables = db.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

print("DANH SÁCH BẢNG SQLITE:")
for table in tables:
    print("-", table[0])

db.close()
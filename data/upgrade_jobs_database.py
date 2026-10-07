import sqlite3

DB_PATH = "database/it_career_match.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Lấy danh sách cột hiện tại
cursor.execute("PRAGMA table_info(jobs)")
existing_columns = [row[1] for row in cursor.fetchall()]

print("Các cột hiện tại:")
print(existing_columns)

# Các cột mới cần bổ sung
new_columns = {
    "requirements": "TEXT",
    "benefits": "TEXT",
    "skills": "TEXT",
    "salary_min": "INTEGER DEFAULT 0",
    "salary_max": "INTEGER DEFAULT 0",
    "salary_text": "TEXT",
    "experience": "TEXT",
    "level": "TEXT",
    "deadline": "TEXT",
    "source": "TEXT DEFAULT 'IT Career Match'",
    "source_url": "TEXT",
    "status": "TEXT DEFAULT 'active'"
}

for column_name, column_type in new_columns.items():

    if column_name not in existing_columns:

        sql = f"""
        ALTER TABLE jobs
        ADD COLUMN {column_name} {column_type}
        """

        cursor.execute(sql)

        print(f"Đã thêm cột: {column_name}")

    else:
        print(f"Cột {column_name} đã tồn tại.")

connection.commit()

# Kiểm tra lại
cursor.execute("PRAGMA table_info(jobs)")

print("\n===== JOBS TABLE =====")

for column in cursor.fetchall():
    print(
        column[0],
        column[1],
        column[2]
    )

connection.close()

print("\nUpgrade database thành công!")
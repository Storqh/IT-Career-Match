import sys
sys.stdout.reconfigure(encoding="utf-8")
import sqlite3

DB_PATH = "database/it_career_match.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""").fetchall()

print("=" * 70)
print("CHI TIẾT CẤU TRÚC SQLITE")
print("=" * 70)

for (table_name,) in tables:
    print(f"\n\n{'=' * 70}")
    print(f"BẢNG: {table_name}")
    print("=" * 70)

    # Thông tin cột
    columns = cursor.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    print("\n[COLUMNS]")
    for column in columns:
        cid, name, data_type, not_null, default_value, primary_key = column

        print(
            f"- {name}: {data_type}"
            f" | NOT NULL: {bool(not_null)}"
            f" | DEFAULT: {default_value}"
            f" | PRIMARY KEY: {bool(primary_key)}"
        )

    # Khóa ngoại
    foreign_keys = cursor.execute(
        f'PRAGMA foreign_key_list("{table_name}")'
    ).fetchall()

    print("\n[FOREIGN KEYS]")
    if foreign_keys:
        for fk in foreign_keys:
            print(
                f"- {fk[3]} -> {fk[2]}.{fk[4]}"
            )
    else:
        print("- Không có khóa ngoại")

    # Số lượng bản ghi
    count = cursor.execute(
        f'SELECT COUNT(*) FROM "{table_name}"'
    ).fetchone()[0]

    print(f"\n[ROW COUNT]: {count}")

conn.close()

print("\n\nĐÃ KIỂM TRA XONG DATABASE.")
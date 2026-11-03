import sqlite3

db_path = "database/it_career_match.db"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name
""").fetchall()

for row in tables:
    table = row["name"]

    print(f"\n{'=' * 60}")
    print(f"TABLE: {table}")
    print("=" * 60)

    indexes = conn.execute(
        f'PRAGMA index_list("{table}")'
    ).fetchall()

    if not indexes:
        print("Không có index bổ sung.")

    for index in indexes:
        index_name = index["name"]

        columns = conn.execute(
            f'PRAGMA index_info("{index_name}")'
        ).fetchall()

        column_names = [
            column["name"]
            for column in columns
        ]

        print(
            f"INDEX: {index_name} | "
            f"UNIQUE: {index['unique']} | "
            f"COLUMNS: {column_names}"
        )

conn.close()
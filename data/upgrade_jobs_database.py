from database.database import get_connection


EXPECTED_COLUMNS = {
    "job_id",
    "title",
    "description",
    "company",
    "location",
    "job_type",
    "category",
    "created_at",
    "requirements",
    "benefits",
    "skills",
    "salary_min",
    "salary_max",
    "salary_text",
    "experience",
    "level",
    "deadline",
    "source",
    "source_url",
    "status"
}


def verify_jobs_table():

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position
            """,
            ("jobs",)
        ).fetchall()

        existing_columns = {
            row["column_name"]
            for row in rows
        }

        print("===== JOBS TABLE =====")

        for row in rows:
            print(
                row["column_name"],
                row["data_type"]
            )

        missing_columns = EXPECTED_COLUMNS - existing_columns

        if missing_columns:
            raise RuntimeError(
                "PostgreSQL đang thiếu các cột: "
                + ", ".join(sorted(missing_columns))
            )

        print("\nĐã tìm thấy đầy đủ các cột.")
        print("Kiểm tra bảng jobs thành công!")

    finally:
        connection.close()


if __name__ == "__main__":
    verify_jobs_table()
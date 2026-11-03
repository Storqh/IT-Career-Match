
import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


# Đọc cấu hình từ file .env ở thư mục dự án
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """
    Tạo kết nối đến PostgreSQL.
    dict_row giúp truy cập dữ liệu bằng tên cột:
    row["email"], row["user_id"], ...
    """

    if not DATABASE_URL:
        raise RuntimeError(
            "Không tìm thấy DATABASE_URL trong file .env"
        )

    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

    return connection


def create_tables():
    """
    PostgreSQL đã có sẵn 10 bảng và dữ liệu được migrate
    từ SQLite. Hàm này chỉ kiểm tra bảng, không tạo lại
    hoặc xóa dữ liệu.
    """

    expected_tables = {
        "users",
        "student_profiles",
        "cvs",
        "skills",
        "student_skills",
        "jobs",
        "job_skills",
        "recommendations",
        "favourites",
        "applications"
    }

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
        """).fetchall()

    existing_tables = {
        row["table_name"] for row in rows
    }

    missing_tables = expected_tables - existing_tables

    if missing_tables:
        raise RuntimeError(
            "PostgreSQL đang thiếu các bảng: "
            + ", ".join(sorted(missing_tables))
        )

    print("Kết nối PostgreSQL thành công.")
    print("Đã tìm thấy đủ 10 bảng.")
    

if __name__ == "__main__":
    create_tables()

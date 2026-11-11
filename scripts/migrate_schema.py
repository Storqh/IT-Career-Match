#!/usr/bin/env python3
"""
Database Schema Migration Script for IT Career Match
Adds: Foreign Keys, Check Constraints, Indexes, and fixes column naming

Run: python scripts/migrate_schema.py
"""
import os
import sys
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    sys.exit(1)

# =========================================================
# MIGRATION STATEMENTS
# =========================================================
MIGRATIONS = [
    # -----------------------------------------------------------------
    # 1. Fix skills table column name (name -> skill_name)
    # -----------------------------------------------------------------
    """
    -- Check if 'name' column exists and rename to 'skill_name'
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'skills' AND column_name = 'name'
        ) THEN
            ALTER TABLE skills RENAME COLUMN name TO skill_name;
            RAISE NOTICE 'Renamed skills.name -> skills.skill_name';
        ELSE
            RAISE NOTICE 'skills.name already renamed or does not exist';
        END IF;
    END $$;
    """,

    # -----------------------------------------------------------------
    # 2. Add UNIQUE constraint on skills.skill_name
    # -----------------------------------------------------------------
    """
    ALTER TABLE skills
    ADD CONSTRAINT uq_skills_skill_name UNIQUE (skill_name);
    """,

    # -----------------------------------------------------------------
    # 3. Foreign Keys with CASCADE DELETE
    # -----------------------------------------------------------------

    # student_profiles -> users
    """
    ALTER TABLE student_profiles
    ADD CONSTRAINT fk_student_profiles_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # cvs -> users
    """
    ALTER TABLE cvs
    ADD CONSTRAINT fk_cvs_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # student_skills -> users
    """
    ALTER TABLE student_skills
    ADD CONSTRAINT fk_student_skills_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # student_skills -> skills
    """
    ALTER TABLE student_skills
    ADD CONSTRAINT fk_student_skills_skill
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE;
    """,

    # job_skills -> jobs
    """
    ALTER TABLE job_skills
    ADD CONSTRAINT fk_job_skills_job
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE;
    """,

    # job_skills -> skills
    """
    ALTER TABLE job_skills
    ADD CONSTRAINT fk_job_skills_skill
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE;
    """,

    # recommendations -> users
    """
    ALTER TABLE recommendations
    ADD CONSTRAINT fk_recommendations_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # recommendations -> jobs
    """
    ALTER TABLE recommendations
    ADD CONSTRAINT fk_recommendations_job
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE;
    """,

    # favourites -> users
    """
    ALTER TABLE favourites
    ADD CONSTRAINT fk_favourites_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # favourites -> jobs
    """
    ALTER TABLE favourites
    ADD CONSTRAINT fk_favourites_job
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE;
    """,

    # applications -> users
    """
    ALTER TABLE applications
    ADD CONSTRAINT fk_applications_user
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
    """,

    # applications -> jobs
    """
    ALTER TABLE applications
    ADD CONSTRAINT fk_applications_job
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE;
    """,

    # -----------------------------------------------------------------
    # 4. Check Constraints
    # -----------------------------------------------------------------

    # users.role
    """
    ALTER TABLE users
    ADD CONSTRAINT chk_users_role
    CHECK (role IN ('student', 'admin'));
    """,

    # jobs.status
    """
    ALTER TABLE jobs
    ADD CONSTRAINT chk_jobs_status
    CHECK (status IN ('active', 'inactive'));
    """,

    # jobs.job_type
    """
    ALTER TABLE jobs
    ADD CONSTRAINT chk_jobs_job_type
    CHECK (job_type IN ('Full-time', 'Part-time', 'Internship', 'Contract', 'Remote'));
    """,

    # jobs.level
    """
    ALTER TABLE jobs
    ADD CONSTRAINT chk_jobs_level
    CHECK (level IN ('Intern', 'Fresher', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager'));
    """,

    # jobs.salary logic
    """
    ALTER TABLE jobs
    ADD CONSTRAINT chk_jobs_salary
    CHECK (salary_min >= 0 AND salary_max >= salary_min);
    """,

    # applications.status
    """
    ALTER TABLE applications
    ADD CONSTRAINT chk_applications_status
    CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn'));
    """,

    # -----------------------------------------------------------------
    # 5. Indexes for Query Performance
    # -----------------------------------------------------------------

    # users
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
    "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",

    # student_profiles
    "CREATE INDEX IF NOT EXISTS idx_profiles_major ON student_profiles(major);",

    # cvs
    "CREATE INDEX IF NOT EXISTS idx_cvs_user_id ON cvs(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_cvs_created_at ON cvs(created_at DESC);",

    # jobs
    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(job_type);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_experience ON jobs(experience);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_level ON jobs(level);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_status_category ON jobs(status, category);",

    # skills
    "CREATE INDEX IF NOT EXISTS idx_skills_skill_name ON skills(skill_name);",

    # student_skills
    "CREATE INDEX IF NOT EXISTS idx_student_skills_user ON student_skills(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_student_skills_skill ON student_skills(skill_id);",

    # job_skills
    "CREATE INDEX IF NOT EXISTS idx_job_skills_job ON job_skills(job_id);",
    "CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill_id);",

    # recommendations
    "CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_recommendations_job ON recommendations(job_id);",
    "CREATE INDEX IF NOT EXISTS idx_recommendations_user_score ON recommendations(user_id, match_score DESC);",
    """
    ALTER TABLE recommendations
        ADD COLUMN IF NOT EXISTS skill_match REAL,
        ADD COLUMN IF NOT EXISTS career_match BOOLEAN;
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_recommendations_user_job ON recommendations(user_id, job_id);",

    # favourites
    "CREATE INDEX IF NOT EXISTS idx_favourites_user ON favourites(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_favourites_job ON favourites(job_id);",

    # applications
    "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_user_status ON applications(user_id, status);",
]


def run_migrations():
    print("=" * 60)
    print("IT CAREER MATCH - DATABASE SCHEMA MIGRATION")
    print("=" * 60)
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    print()

    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            for i, migration in enumerate(MIGRATIONS, 1):
                print(f"[{i}/{len(MIGRATIONS)}] Running migration...")
                try:
                    cur.execute(migration)
                    conn.commit()
                    print(f"  [OK] Success")
                except psycopg.errors.DuplicateObject as e:
                    conn.rollback()
                    print(f"  [SKIP] Already exists: {e}")
                except psycopg.errors.UndefinedColumn as e:
                    conn.rollback()
                    print(f"  [WARN] Column issue: {e}")
                except psycopg.errors.UndefinedTable as e:
                    conn.rollback()
                    print(f"  [WARN] Table missing: {e}")
                except Exception as e:
                    conn.rollback()
                    print(f"  [FAIL] Failed: {e}")
                    # Continue with other migrations

        print()
        print("=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)

        # Verify
        print("\nVerifying constraints...")
        with conn.cursor() as cur:
            # Check FKs
            cur.execute("""
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid IN (
                    SELECT oid FROM pg_class WHERE relname IN (
                        'student_profiles', 'cvs', 'student_skills', 'job_skills',
                        'recommendations', 'favourites', 'applications'
                    )
                ) AND contype = 'f'
                ORDER BY conname;
            """)
            fks = cur.fetchall()
            print(f"Foreign Keys ({len(fks)}):")
            for fk in fks:
                print(f"  - {fk['conname']}")

            # Check indexes
            cur.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname;
            """)
            indexes = cur.fetchall()
            print(f"\nIndexes ({len(indexes)}):")
            for idx in indexes:
                print(f"  - {idx['tablename']}.{idx['indexname']}")

            # Check constraints
            cur.execute("""
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid IN (
                    SELECT oid FROM pg_class WHERE relname IN (
                        'users', 'jobs', 'applications', 'skills'
                    )
                ) AND contype = 'c'
                ORDER BY conname;
            """)
            checks = cur.fetchall()
            print(f"\nCheck Constraints ({len(checks)}):")
            for chk in checks:
                print(f"  - {chk['conname']}")

    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()
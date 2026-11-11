#!/usr/bin/env python3
"""
Script để xoá .env khỏi git history và rotate secrets.
CHẠY SCRIPT NÀY TRƯỚC KHI COMMIT BẤT KỲ THAY ĐỔI NÀO KHÁC.

⚠️ CẢNH BÁO: Script này sẽ rewrite git history!
- Chạy trên branch riêng (không phải main)
- Backup repo trước khi chạy
- Sau khi chạy: force push (--force-with-lease)
"""
import subprocess
import sys
import os

def run_cmd(cmd, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def main():
    repo_path = r"E:\IT-Career-Match"
    os.chdir(repo_path)

    print("=" * 60)
    print("IT CAREER MATCH - SECRET ROTATION & GIT HISTORY CLEANUP")
    print("=" * 60)

    # 1. Kiểm tra .env có trong history không
    print("\n[1/5] Kiểm tra .env trong git history...")
    result = run_cmd("git log --all --full-history -- .env", check=False)
    if result.stdout.strip():
        print("⚠️  .env TỒN TẠI TRONG GIT HISTORY!")
        print("Cần chạy git filter-repo để xoá vĩnh viễn.")
    else:
        print("✅ .env không có trong history (hoặc chưa từng commit)")

    # 2. Tạo backup branch
    print("\n[2/5] Tạo backup branch...")
    run_cmd("git branch backup-before-secret-rotation 2>/dev/null || true")

    # 3. Hướng dẫn rotate secrets
    print("\n" + "=" * 60)
    print("SECRETS CẦN ROTATE NGAY (tự làm trên dashboard nhà cung cấp):")
    print("=" * 60)
    print("""
1. BREVO_API_KEY (Sendinblue)
   → https://app.brevo.com/settings/keys/api
   → Revoke old key, tạo key mới
   → Cập nhật vào .env mới

2. POSTGRES_PASSWORD / DATABASE_URL
   → ALTER USER postgres WITH PASSWORD 'new_secure_password';
   → Cập nhật DATABASE_URL trong .env

3. SECRET_KEY (Flask)
   → Tạo mới: python -c "import secrets; print(secrets.token_hex(32))"
   → Cập nhật vào .env

4. Nếu dùng các service khác (Sentry, Redis, etc.) → rotate tương tự
""")

    # 4. Chạy git filter-repo nếu cần
    print("\n[3/5] Xoá .env khỏi history (git filter-repo)...")
    print("⚠️  CẦN CÀI ĐẶT: pip install git-filter-repo")
    print("Chạy lệnh sau (SAU KHI ĐÃ ROTATE SECRETS):")
    print("  git filter-repo --path .env --invert-paths --force")
    print()
    print("Hoặc dùng BFG Repo-Cleaner (nhanh hơn):")
    print("  java -jar bfg.jar --delete-files .env")
    print("  git reflog expire --expire=now --all && git gc --prune=now --aggressive")

    # 5. Force push hướng dẫn
    print("\n[4/5] Sau khi filter-repo xong:")
    print("  git push origin --force-with-lease --all")
    print("  git push origin --force-with-lease --tags")
    print()
    print("⚠️  TẤT CẢ CONTRIBUTORS PHẢI RE-CLONE REPO!")

    # 6. Verify
    print("\n[5/5] Verify secrets không còn trong repo:")
    run_cmd("git log --all --full-history -p -- .env 2>/dev/null | head -20", check=False)
    run_cmd("git grep -r 'BREVO_API_KEY\\|POSTGRES_PASSWORD\\|SECRET_KEY' -- '*.py' '*.txt' '*.md' '*.yml' '*.yaml' '*.json' 2>/dev/null | grep -v '.env.example' | head -20", check=False)

    print("\n" + "=" * 60)
    print("HOÀN TẤT KIỂM TRA. HÃY THỰC HIỆN ROTATE SECRETS TRÊN DASHBOARD!")
    print("=" * 60)

if __name__ == "__main__":
    main()
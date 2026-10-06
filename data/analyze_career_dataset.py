import pandas as pd

# Đọc dataset đã chuẩn bị
df = pd.read_csv("data/career_ml_dataset.csv")

print("===== PHÂN TÍCH CAREER ML DATASET =====")

# 1. Kích thước dataset
print("\n1. Kích thước:")
print(df.shape)

# 2. Các cột
print("\n2. Các cột:")
print(df.columns.tolist())

# 3. Kiểm tra NULL
print("\n3. Dữ liệu NULL:")
print(df.isnull().sum())

# 4. Kiểm tra dòng trùng lặp
print("\n4. Số dòng trùng lặp:")
print(df.duplicated().sum())

# 5. Số class
print("\n5. Số Career Category:")
print(df["Career Category"].nunique())

# 6. Phân bố class
print("\n6. Phân bố Career Category:")
print(df["Career Category"].value_counts())

# 7. Tỷ lệ phần trăm
print("\n7. Tỷ lệ phần trăm:")
print(
    (
        df["Career Category"].value_counts(normalize=True) * 100
    ).round(2)
)
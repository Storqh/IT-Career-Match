import pandas as pd

df = pd.read_csv("data/career_dataset.csv")

print("===== THÔNG TIN DATASET =====")

print("\nSố dòng và số cột:")
print(df.shape)

print("\nTên các cột:")
print(df.columns.tolist())

print("\n5 dòng đầu:")
print(df.head())

print("\nSố dữ liệu NULL:")
print(df.isnull().sum())
# =========================
# PHÂN TÍCH DATASET
# =========================

print("\n===== PHÂN TÍCH JOB TITLE =====")

print("Số Job Title khác nhau:")
print(df["Job Title"].nunique())

print("\nDanh sách Job Title:")
print(df["Job Title"].unique())

print("\nSố lượng mỗi Job Title:")
print(df["Job Title"].value_counts())
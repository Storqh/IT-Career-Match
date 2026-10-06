import pandas as pd
import sys
import os

# Cho phép import thư mục ai
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from ai.text_preprocessing import preprocess_text


# Đọc dataset
df = pd.read_csv("data/career_ml_dataset.csv")


# Gộp dữ liệu text
df["Combined Text"] = (
    df["Job Title"].astype(str)
    + " "
    + df["Skills"].astype(str)
    + " "
    + df["Job Description"].astype(str)
)


# Tiền xử lý
df["Cleaned Text"] = df["Combined Text"].apply(
    preprocess_text
)


print("===== KẾT QUẢ TIỀN XỬ LÝ =====")

print("\nSố mẫu:")
print(len(df))

print("\nVí dụ dữ liệu gốc:")
print(df["Combined Text"].iloc[0])

print("\nSau khi tiền xử lý:")
print(df["Cleaned Text"].iloc[0])

print("\nSố Cleaned Text rỗng:")
print((df["Cleaned Text"] == "").sum())


# Lưu dataset
df.to_csv(
    "data/career_preprocessed.csv",
    index=False
)

print("\nĐã lưu: data/career_preprocessed.csv")
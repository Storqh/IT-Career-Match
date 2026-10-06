import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ==============================
# ĐỌC DATASET
# ==============================

df = pd.read_csv("data/career_preprocessed.csv")

X_text = df["Cleaned Text"]
y = df["Career Category"]


# ==============================
# TRAIN / TEST SPLIT TRƯỚC
# ==============================

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==============================
# TF-IDF
# ==============================

tfidf = TfidfVectorizer(
    max_features=2000,
    ngram_range=(1, 2)
)

# Chỉ học vocabulary từ TRAIN
X_train = tfidf.fit_transform(X_train_text)

# TEST chỉ được transform
X_test = tfidf.transform(X_test_text)


print("===== TRAIN / TEST + TF-IDF =====")

print("\nTraining samples:")
print(X_train.shape)

print("\nTesting samples:")
print(X_test.shape)

print("\nSố features:")
print(len(tfidf.get_feature_names_out()))

print("\nPhân bố y_train:")
print(y_train.value_counts())

print("\nPhân bố y_test:")
print(y_test.value_counts())
# ==============================
# LOGISTIC REGRESSION MODEL
# ==============================

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

print("\n===== TRAINING MODEL =====")

model.fit(X_train, y_train)
# ==============================
# CAREER PREDICTION
# ==============================

y_pred = model.predict(X_test)
# ==============================
# ACCURACY EVALUATION
# ==============================

accuracy = accuracy_score(y_test, y_pred)

correct_predictions = (y_test.values == y_pred).sum()
total_predictions = len(y_test)

print("\n===== ACCURACY EVALUATION =====")

print("Số dự đoán đúng:", correct_predictions)
print("Tổng số mẫu test:", total_predictions)

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Accuracy (%): {accuracy * 100:.2f}%"
)
# ==============================
# PRECISION / RECALL / F1
# ==============================

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print("\n===== MODEL EVALUATION =====")

print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nDạng phần trăm:")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall:    {recall * 100:.2f}%")
print(f"F1-score:  {f1 * 100:.2f}%")
print("\n===== CAREER PREDICTION =====")

print("Số mẫu test:", len(y_test))
print("Số dự đoán:", len(y_pred))

print("\n10 kết quả đầu tiên:")

results = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred
})

print(results.head(10))

print("Train model thành công!")
print("Số class:", len(model.classes_))

print("\nCác class model có thể dự đoán:")
for career in model.classes_:
    print("-", career)
# ==============================
# CONFUSION MATRIX
# ==============================

labels = model.classes_

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)

cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels
)

print("\n===== CONFUSION MATRIX =====")
print(cm_df)


# ==============================
# CLASSIFICATION REPORT
# ==============================

print("\n===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_test,
        y_pred,
        labels=labels,
        zero_division=0
    )
)
# ==============================
# SAVE MODEL
# ==============================

joblib.dump(
    model,
    "models/career_classifier.joblib"
)

joblib.dump(
    tfidf,
    "models/tfidf_vectorizer.joblib"
)

print("\n===== SAVE MODEL =====")
print("Đã lưu Logistic Regression model.")
print("Đã lưu TF-IDF Vectorizer.")
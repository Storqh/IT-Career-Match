import joblib

from text_preprocessing import preprocess_text


# ==============================
# LOAD MODEL
# ==============================

model = joblib.load(
    "models/career_classifier.joblib"
)

tfidf = joblib.load(
    "models/tfidf_vectorizer.joblib"
)


test_profiles = [
    """
    Java Spring Boot developer with experience building
    REST APIs, SQL databases, backend services and microservices.
    """,

    """
    DevOps engineer experienced with Docker, Kubernetes,
    Jenkins, CI/CD pipelines, AWS and cloud infrastructure.
    """,

    """
    Cybersecurity specialist with experience in network security,
    penetration testing, vulnerability assessment,
    incident response and security monitoring.
    """
]

for i, cv_text in enumerate(test_profiles, start=1):

    cleaned_text = preprocess_text(cv_text)

    cv_vector = tfidf.transform(
        [cleaned_text]
    )

    prediction = model.predict(
        cv_vector
    )[0]

    print(f"\n===== TEST {i} =====")
    print("CV:", cleaned_text)
    print("Nghề dự đoán:", prediction)
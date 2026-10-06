import joblib
from ai.skill_gap import analyze_skill_gap
from ai.explanation import generate_explanation
from sklearn.metrics.pairwise import cosine_similarity
from ai.text_preprocessing import preprocess_text
from database.database import get_connection

# Load TF-IDF đã train ở Sprint 3
tfidf = joblib.load(
    "models/tfidf_vectorizer.joblib"
)
career_model = joblib.load(
    "models/career_classifier.joblib"
)


def vectorize_cv(cv_text):

    # Tiền xử lý CV
    cleaned_text = preprocess_text(cv_text)

    # Chuyển CV thành TF-IDF vector
    cv_vector = tfidf.transform(
        [cleaned_text]
    )

    return cv_vector
def vectorize_job(job_title, job_description):

    # Gộp title và description
    job_text = f"{job_title} {job_description}"

    # Tiền xử lý
    cleaned_text = preprocess_text(job_text)

    # Vector hóa bằng TF-IDF đã train
    job_vector = tfidf.transform(
        [cleaned_text]
    )

    return job_vector
def calculate_similarity(cv_vector, job_vector):

    similarity = cosine_similarity(
        cv_vector,
        job_vector
    )[0][0]

    return similarity
def get_all_jobs():

    connection = get_connection()

    jobs = connection.execute(
        """
        SELECT job_id, title, description,
               company, location, job_type, category
        FROM jobs
        """
    ).fetchall()

    connection.close()

    return jobs
def predict_career(cv_text):

    cleaned_text = preprocess_text(cv_text)

    cv_vector = tfidf.transform(
        [cleaned_text]
    )

    prediction = career_model.predict(
        cv_vector
    )[0]

    return prediction
def recommend_jobs(cv_text, top_k=5):

    # Vector hóa CV
    cv_vector = vectorize_cv(cv_text)
    predicted_career = predict_career(cv_text)
    # Lấy tất cả Job
    jobs = get_all_jobs()

    recommendations = []

    for job in jobs:

        # Vector hóa Job
        job_vector = vectorize_job(
            job["title"],
            job["description"]
        )

        # Tính Cosine Similarity
        similarity = calculate_similarity(
            cv_vector,
            job_vector
        )
        match_score = calculate_match_score(
            similarity,
            predicted_career,
            job["category"]
        )
        job_text = f"{job['title']} {job['description']}"

        skill_gap = analyze_skill_gap(
            cv_text,
            job_text
        )

        explanation = generate_explanation(
            predicted_career,
            job["category"],
            skill_gap["matched_skills"],
            skill_gap["missing_skills"]
        )
        recommendations.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "company": job["company"],
            "category": job["category"],
            "similarity": similarity,
            "match_score": match_score,
            "matched_skills": skill_gap["matched_skills"],
            "missing_skills": skill_gap["missing_skills"],

            "explanation": explanation
        })

    # Sắp xếp công việc theo độ tương đồng giảm dần
    recommendations.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return recommendations[:top_k]
def calculate_match_score(
    similarity,
    predicted_career,
    job_category
):

    # 70% từ Cosine Similarity
    similarity_score = similarity * 70

    # 30% từ Career Category
    career_score = 0

    if predicted_career == job_category:
        career_score = 30

    match_score = (
        similarity_score
        + career_score
    )

    return round(match_score, 2)
if __name__ == "__main__":

    test_cv = """
    Python developer with experience in machine learning,
    pandas, numpy, scikit-learn, TensorFlow,
    data analysis, SQL and predictive models.
    """

    recommendations = recommend_jobs(
        test_cv,
        top_k=5
    )

    predicted_career = predict_career(test_cv)

    print("===== TOP 5 RECOMMENDED JOBS =====")
    print("Career Prediction:", predicted_career)

    for rank, job in enumerate(recommendations, start=1):

        print(f"\n#{rank} - {job['title']}")
        print("Company:", job["company"])
        print("Category:", job["category"])
        print(
            f"Similarity: {job['similarity'] * 100:.2f}%"
        )
        print(
            f"Match Score: {job['match_score']}/100"
        )
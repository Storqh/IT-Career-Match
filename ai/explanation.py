def generate_explanation(
    predicted_career,
    job_category,
    matched_skills,
    missing_skills
):
    reasons = []

    if predicted_career == job_category:
        reasons.append(
            f"Công việc thuộc đúng nhóm nghề {predicted_career} "
            "được mô hình dự đoán từ CV."
        )
    else:
        reasons.append(
            f"Công việc thuộc nhóm {job_category}, trong khi CV "
            f"được dự đoán phù hợp nhất với {predicted_career}."
        )

    if matched_skills:
        reasons.append(
            "Các kỹ năng phù hợp: "
            + ", ".join(matched_skills)
            + "."
        )

    if missing_skills:
        reasons.append(
            "Các kỹ năng nên bổ sung: "
            + ", ".join(missing_skills)
            + "."
        )

    return " ".join(reasons)
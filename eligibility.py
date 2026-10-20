def check_condition(user_value, operator, criterion_value):
    """
    Compare a user's value with a scheme eligibility criterion.
    """

    if user_value is None:
        return False

    user_value = str(user_value).strip()
    criterion_value = str(criterion_value).strip()

    # Exact text comparison
    if operator == "=":
        return user_value.lower() == criterion_value.lower()

    # Numeric comparisons
    if operator in ["<=", ">=", "<", ">"]:
        try:
            user_number = float(user_value)
            criterion_number = float(criterion_value)

            if operator == "<=":
                return user_number <= criterion_number

            elif operator == ">=":
                return user_number >= criterion_number

            elif operator == "<":
                return user_number < criterion_number

            elif operator == ">":
                return user_number > criterion_number

        except (ValueError, TypeError):
            return False

    # Multiple allowed values
    if operator == "IN":
        allowed_values = [
            value.strip().lower()
            for value in criterion_value.split(",")
        ]

        return user_value.lower() in allowed_values

    return False


def calculate_eligibility(user, criteria):
    """
    Calculate eligibility and match score for one scheme.

    Match Score =
    Satisfied Criteria / Total Criteria × 100
    """

    total_criteria = len(criteria)
    has_substantive_criteria = any(
        criterion["criterion_type"].strip().lower() != "occupation"
        for criterion in criteria
    )
    satisfied_criteria = 0
    satisfied_details = []
    failed_criteria = []
    missing_criteria = []

    # Map database criterion names to user table fields
    field_mapping = {
    "12th_percentage": "percentage_12th",
    "income": "annual_income",

    "occupation": "occupation",
    "category": "category",
    "domicile": "domicile",
    "course_stream": "course_stream",
    "age": "age",
    "gender": "gender",
    "location": "location",
    "education": "education",
    "admission_mode": "admission_mode",

    # Student fields
    "graduation_percentage": "graduation_percentage",
    "is_pg_student": "is_pg_student",
    "minority_status": "minority_status",
    "hostel_status": "hostel_status",

    # Farmer fields
    "farmer_id": "farmer_id",
    "land_holding": "land_holding",
    "land_unit": "land_unit",
    "land_ownership": "land_ownership",
    "irrigation_type": "irrigation_type",
    "crop_type": "crop_type",
    "farmer_category": "farmer_category",
    "tribal_status": "tribal_status",

    # Other fields
    "parent_occupation": "parent_occupation",
    "disability_status": "disability_status",
    "ex_serviceman_child": "ex_serviceman_child",
    "freedom_fighter_child": "freedom_fighter_child"
}

    criterion_labels = {
        "12th_percentage": "12th percentage",
        "income": "Annual income",
        "course_stream": "Course stream",
        "is_pg_student": "Postgraduate student",
        "minority_status": "Minority status",
        "hostel_status": "Hostel status",
        "farmer_id": "Farmer ID",
        "land_holding": "Land holding",
        "land_unit": "Land unit",
        "land_ownership": "Land ownership",
        "irrigation_type": "Irrigation type",
        "crop_type": "Crop type",
        "farmer_category": "Farmer category",
        "tribal_status": "Tribal status",
        "parent_occupation": "Parent occupation",
        "disability_status": "Disability status",
        "ex_serviceman_child": "Child of ex-serviceman",
        "freedom_fighter_child": "Child of freedom fighter",
    }
    operator_labels = {"=": "is", "IN": "is one of", "<=": "≤", ">=": "≥", "<": "<", ">": ">"}

    for criterion in criteria:

        criterion_type = criterion["criterion_type"]
        operator = criterion["operator"]
        criterion_value = criterion["criterion_value"]

        user_field = field_mapping.get(
            criterion_type,
            criterion_type
        )

        user_value = user.get(user_field)

        if user_value is None or not str(user_value).strip():
            label = criterion_labels.get(criterion_type, criterion_type.replace("_", " ").capitalize())
            missing_criteria.append(label)
            continue

        result = check_condition(
            user_value,
            operator,
            criterion_value
        )

        if result:
            satisfied_criteria += 1
            label = criterion_labels.get(criterion_type, criterion_type.replace("_", " ").capitalize())
            satisfied_details.append(
                f"{label} requirement met: {user_value}"
            )
        else:
            label = criterion_labels.get(criterion_type, criterion_type.replace("_", " ").capitalize())
            actual_value = user_value if user_value is not None and str(user_value).strip() else "Not provided"
            failed_criteria.append(
                f"{label}: {actual_value} (required {operator_labels.get(operator, operator)} {criterion_value})"
            )

    # Calculate score
    if total_criteria > 0:
        match_score = (
            satisfied_criteria / total_criteria
        ) * 100
    else:
        match_score = 0

    # Eligible only when all criteria are satisfied
    eligible = (
        total_criteria > 0
        and has_substantive_criteria
        and not missing_criteria
        and satisfied_criteria == total_criteria
    )

    return {
        "eligible": eligible,
        "match_score": round(match_score, 2),
        "satisfied": satisfied_criteria,
        "total": total_criteria,
        "has_substantive_criteria": has_substantive_criteria,
        "satisfied_criteria": satisfied_details,
        "missing_criteria": missing_criteria,
        "failed_criteria": failed_criteria
    }

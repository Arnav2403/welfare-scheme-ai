from flask import Flask, render_template, request
import mysql.connector
from eligibility import calculate_eligibility

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arnav!2025N",
    database="welfare_scheme_db"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/check/<int:user_id>")
def check_eligibility(user_id):

    cursor = db.cursor(dictionary=True)

    # Get user profile
    cursor.execute(
        "SELECT * FROM users WHERE user_id = %s",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.close()
        return "User not found"

    # --------------------------------------------------
    # FILTER SCHEMES BASED ON OCCUPATION
    # --------------------------------------------------

    occupation = user["occupation"].strip().lower()

    occupation_domain = {
        "student": "Education",
        "farmer": "Agriculture"
    }

    if occupation in occupation_domain:

        domain = occupation_domain[occupation]

        cursor.execute(
            """
            SELECT *
            FROM schemes
            WHERE domain = %s
            """,
            (domain,)
        )

    else:

        cursor.execute(
            "SELECT * FROM schemes"
        )

    schemes = cursor.fetchall()

    # --------------------------------------------------
    # CHECK ELIGIBILITY FOR EACH SCHEME
    # --------------------------------------------------

    results = []

    for scheme in schemes:

        cursor.execute(
            """
            SELECT *
            FROM eligibility_criteria
            WHERE scheme_id = %s
            """,
            (scheme["scheme_id"],)
        )

        criteria = cursor.fetchall()

        result = calculate_eligibility(
            user,
            criteria
        )

        results.append({

            "scheme_id": scheme["scheme_id"],

            "scheme_name": scheme["scheme_name"],

            "domain": scheme["domain"],

            "description": scheme["description"],

            "benefits": scheme["benefits"],

            "required_documents":
                scheme["required_documents"],

            "match_score":
                result["match_score"],

            "eligible":
                result["eligible"],

            "satisfied":
                result["satisfied"],

            "total":
                result["total"],

            "failed_criteria":
                result["failed_criteria"]

        })

    cursor.close()

    # Highest match score first
    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return render_template(
        "results.html",
        results=results,
        user=user
    )


@app.route("/recommend", methods=["POST"])
def recommend():

    # --------------------------------------------------
    # BASIC PROFILE INFORMATION
    # --------------------------------------------------

    name = request.form["name"]

    age = request.form["age"]

    gender = request.form["gender"]

    annual_income = request.form["annual_income"]

    occupation = request.form["occupation"]

    education = request.form["education"]

    location = request.form["location"]

    category = request.form["category"]

    domicile = request.form["domicile"]

    admission_mode = (
        request.form.get("admission_mode")
        or None
    )

    # --------------------------------------------------
    # ACADEMIC INFORMATION
    # --------------------------------------------------

    children_count = (
        request.form.get("children_count")
        or None
    )

    percentage_12th = (
        request.form.get("percentage_12th")
        or None
    )

    course_stream = (
        request.form.get("course_stream")
        or None
    )

    graduation_percentage = (
        request.form.get("graduation_percentage")
        or None
    )

    is_pg_student = (
        request.form.get("is_pg_student")
        or None
    )

    # --------------------------------------------------
    # ADDITIONAL INFORMATION
    # --------------------------------------------------

    minority_status = (
        request.form.get("minority_status")
        or None
    )

    hostel_status = (
        request.form.get("hostel_status")
        or None
    )

    parent_occupation = (
        request.form.get("parent_occupation")
        or None
    )

    disability_status = (
        request.form.get("disability_status")
        or None
    )

    ex_serviceman_child = (
        request.form.get("ex_serviceman_child")
        or None
    )

    freedom_fighter_child = (
        request.form.get("freedom_fighter_child")
        or None
    )

    # --------------------------------------------------
    # FARMER INFORMATION
    # --------------------------------------------------

    farmer_id = (
        request.form.get("farmer_id")
        or None
    )

    land_holding = (
        request.form.get("land_holding")
        or None
    )

    land_unit = (
        request.form.get("land_unit")
        or None
    )

    land_ownership = (
        request.form.get("land_ownership")
        or None
    )

    irrigation_type = (
        request.form.get("irrigation_type")
        or None
    )

    crop_type = (
        request.form.get("crop_type")
        or None
    )

    farmer_category = (
        request.form.get("farmer_category")
        or None
    )

    tribal_status = (
        request.form.get("tribal_status")
        or None
    )

    # --------------------------------------------------
    # INSERT USER PROFILE
    # --------------------------------------------------

    cursor = db.cursor()

    query = """
        INSERT INTO users
        (
            name,
            age,
            gender,
            annual_income,
            occupation,
            education,
            location,
            category,
            domicile,
            admission_mode,
            children_count,
            percentage_12th,
            course_stream,
            graduation_percentage,
            is_pg_student,
            minority_status,
            hostel_status,
            parent_occupation,
            disability_status,
            ex_serviceman_child,
            freedom_fighter_child,
            farmer_id,
            land_holding,
            land_unit,
            land_ownership,
            irrigation_type,
            crop_type,
            farmer_category,
            tribal_status
        )

        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    values = (

        name,
        age,
        gender,
        annual_income,
        occupation,
        education,
        location,
        category,
        domicile,
        admission_mode,

        children_count,
        percentage_12th,
        course_stream,
        graduation_percentage,
        is_pg_student,

        minority_status,
        hostel_status,
        parent_occupation,
        disability_status,
        ex_serviceman_child,
        freedom_fighter_child,

        farmer_id,
        land_holding,
        land_unit,
        land_ownership,
        irrigation_type,
        crop_type,
        farmer_category,
        tribal_status
    )

    cursor.execute(
        query,
        values
    )

    db.commit()

    user_id = cursor.lastrowid

    cursor.close()

    return redirect_to_check(user_id)


def redirect_to_check(user_id):

    return render_template(
        "redirect.html",
        user_id=user_id
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )
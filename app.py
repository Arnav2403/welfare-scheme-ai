from flask import Flask, render_template, request
import mysql.connector
from eligibility import calculate_eligibility, check_condition

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arnav!2025N",
    database="welfare_scheme_db"
)


def get_scheme_guidance(scheme_name, user):
    """Explain official requirements that the stored scheme rules do not cover."""
    name = scheme_name.lower()
    requirements = []

    if "pmrkvy - rainfed area development" in name:
        requirements = [
            ("Farmer ID", "farmer_id", "PRESENT", "", "A Farmer ID from AgriStack is mandatory."),
            ("Aadhaar-linked bank account", None, None, None, "The beneficiary's bank account must be linked to Aadhaar."),
            ("Integrated farming", None, None, None, "The beneficiary must be willing to adopt Integrated Farming System practices."),
            ("Project selection", None, None, None, "Support is delivered through selected village clusters and approved project components."),
        ]
    elif "government vidyaniketan scholarship" in name:
        requirements = [
            ("10th percentage", "percentage_10th", ">=", "60", "At least 60% in 10th standard."),
            ("School attended", "studied_vidyaniketan", "=", "Yes", "Passed 10th from a State Government Vidyaniketan."),
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a resident of Maharashtra."),
        ]
    elif "ekl avya scholarship" in name or "eklavya scholarship" in name:
        requirements = [
            ("Parent income", "annual_income", "<=", "75000", "Annual parental income must not exceed ₹75,000."),
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a Maharashtra resident."),
            ("Postgraduate admission", "is_pg_student", "=", "Yes", "Must be admitted to postgraduate study."),
            ("Graduation marks", None, None, None, "At least 60% for Arts, Commerce or Law, or 70% for Science."),
            ("Employment", None, None, None, "Full-time and part-time employment are not allowed."),
        ]
    elif "meritorious students possessing mathematics" in name:
        requirements = [
            ("12th marks", "percentage_12th", ">=", "60", "At least 60% in 12th standard Science."),
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a Maharashtra resident."),
            ("Main subject", None, None, None, "Must study Mathematics or Physics as a main subject."),
            ("Subject marks", None, None, None, "Mathematics and Physics marks must each be above 60%."),
        ]
    elif "government research adhichatra" in name:
        requirements = [
            ("Postgraduate qualification", "is_pg_student", "=", "Yes", "Applicant must be a postgraduate."),
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a Maharashtra resident."),
            ("Postgraduate marks", "graduation_percentage", ">=", "60", "At least 60% in postgraduate study."),
            ("Research institution", None, None, None, "Research must be at an institution listed by the scheme."),
        ]
    elif "state government daxshina adhichatra" in name:
        requirements = [
            ("Postgraduate study", "is_pg_student", "=", "Yes", "Scheme is for postgraduate students."),
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a Maharashtra resident."),
            ("Institution", None, None, None, "Must attend one of the government colleges or universities listed by the scheme."),
        ]
    elif "jawaharlal nehru university" in name:
        requirements = [
            ("Maharashtra residence", "domicile", "=", "Maharashtra", "Must be a Maharashtra resident."),
            ("JNU study", None, None, None, "Must be studying at Jawaharlal Nehru University."),
            ("Research fellowship", None, None, None, "Must be pursuing a Junior Research Fellowship."),
        ]
    elif "state minority scholarship part ii" in name:
        requirements = [
            ("Minority community", "minority_status", "=", "Yes", "Applicant must belong to a minority community."),
            ("Maharashtra domicile", "domicile", "=", "Maharashtra", "Must be domiciled in Maharashtra."),
            ("Annual income", "annual_income", "<=", "800000", "Annual income must not exceed ₹8,00,000."),
            ("Course", "course_stream", "IN", "Arts,Commerce,Science,Law", "Graduation or postgraduate study in an eligible course."),
        ]
    elif "minority communities pursuing higher and professional courses (dte)" in name:
        requirements = [
            ("Minority community", "minority_status", "=", "Yes", "Applicant must belong to a listed minority community."),
            ("Maharashtra domicile", "domicile", "=", "Maharashtra", "Must be domiciled in Maharashtra."),
            ("Family income", "annual_income", "<=", "800000", "Annual family income must not exceed ₹8,00,000."),
            ("Technical/professional course", None, None, None, "Must be admitted to an eligible technical or professional course."),
            ("SSC in Maharashtra", None, None, None, "Must have passed SSC in Maharashtra."),
        ]
    elif "assistance to meritorious students scholarship - senior level" in name:
        requirements = [
            ("Merit rank", None, None, None, "Senior-level applicants must rank among the top students in secondary and higher-secondary examinations."),
            ("Current study", None, None, None, "Applicant must be studying after 12th standard."),
        ]

    guidance = []
    for label, field, operator, value, description in requirements:
        actual = user.get(field) if field else None
        if field and actual is not None and str(actual).strip():
            met = True if operator == "PRESENT" else check_condition(actual, operator, value)
            outcome = "Satisfied" if met else "Not satisfied"
            detail = (
                f"Your profile includes {actual}."
                if operator == "PRESENT"
                else f"Your profile says {actual}; requirement: {operator} {value}."
            )
        else:
            outcome = "Not checked"
            detail = "This detail is not available in the profile."
        guidance.append({
            "label": label,
            "description": description,
            "outcome": outcome,
            "detail": detail,
        })
    return guidance


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/profile")
@app.route("/profile/<int:user_id>")
def profile(user_id=None):
    user = None
    if user_id:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
    return render_template("profile.html", user=user)


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

    profile_sections = [
        ("Personal Information", [
            ("name", "Name"), ("age", "Age"), ("gender", "Gender"),
            ("annual_income", "Annual income"), ("occupation", "Occupation"),
            ("education", "Education"), ("location", "Location"),
            ("category", "Category"), ("domicile", "Domicile"),
        ]),
        ("Academic Information", [
            ("admission_mode", "Admission mode"), ("children_count", "Children"),
            ("percentage_12th", "12th percentage"), ("course_stream", "Course stream"),
            ("graduation_percentage", "Graduation percentage"), ("is_pg_student", "Postgraduate student"),
        ]),
        ("Additional Information", [
            ("minority_status", "Minority status"), ("hostel_status", "Hostel status"),
            ("parent_occupation", "Parent occupation"), ("disability_status", "Disability status"),
            ("ex_serviceman_child", "Child of ex-serviceman"),
            ("freedom_fighter_child", "Child of freedom fighter"),
        ]),
        ("Farmer Information", [
            ("farmer_id", "Farmer ID"), ("land_holding", "Land holding"),
            ("land_unit", "Land unit"), ("land_ownership", "Land ownership"),
            ("irrigation_type", "Irrigation type"), ("crop_type", "Crop type"),
            ("farmer_category", "Farmer category"), ("tribal_status", "Tribal status"),
        ]),
    ]
    profile_sections = [
        {"title": title, "entries": [
            {"label": label, "value": user[key]}
            for key, label in fields
            if user.get(key) is not None and str(user.get(key)).strip()
        ]}
        for title, fields in profile_sections
    ]
    profile_sections = [section for section in profile_sections if section["entries"]]

    # --------------------------------------------------
    # FILTER SCHEMES BASED ON OCCUPATION
    # --------------------------------------------------

    occupation = (user.get("occupation") or "").strip().lower()

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

        # These seed records previously contained only an occupation check.
        # Restore the scheme's defining relationship requirement so it can be
        # evaluated from the profile instead of being treated as unconfigured.
        if not any(
            criterion["criterion_type"].strip().lower() != "occupation"
            for criterion in criteria
        ):
            scheme_name = scheme["scheme_name"].lower()
            if "children of ex-servicemen" in scheme_name:
                criteria.append({
                    "criterion_type": "ex_serviceman_child",
                    "operator": "=",
                    "criterion_value": "Yes",
                })
            elif "children of freedom fighters" in scheme_name:
                criteria.append({
                    "criterion_type": "freedom_fighter_child",
                    "operator": "=",
                    "criterion_value": "Yes",
                })

        result = calculate_eligibility(
            user,
            criteria
        )

        eligibility_guidance = get_scheme_guidance(scheme["scheme_name"], user)
        official_requirement_failed = any(
            item["outcome"] == "Not satisfied"
            for item in eligibility_guidance
        )
        eligible = result["eligible"] and not official_requirement_failed
        rankable = (
            result["has_substantive_criteria"]
            and not result["missing_criteria"]
            and not official_requirement_failed
        )
        if eligible:
            result_group = "eligible"
            result_group_label = "Eligible schemes"
            result_group_order = 0
            summary_reason = "Meets all configured criteria and known requirements checked from this profile."
        elif official_requirement_failed or (result["has_substantive_criteria"] and not result["missing_criteria"]):
            result_group = "not_eligible"
            result_group_label = "Not eligible for these schemes"
            result_group_order = 2
            failed_labels = [
                item["label"] for item in eligibility_guidance
                if item["outcome"] == "Not satisfied"
            ]
            if failed_labels:
                summary_reason = "Does not meet: " + ", ".join(failed_labels) + "."
            elif result["failed_criteria"]:
                summary_reason = "Does not meet: " + "; ".join(result["failed_criteria"]) + "."
            else:
                summary_reason = "One or more configured eligibility criteria are not satisfied."
        else:
            result_group = "needs_information"
            result_group_label = "More information needed"
            result_group_order = 1
            missing_details = result["missing_criteria"]
            summary_reason = (
                "Provide: " + ", ".join(missing_details) + "."
                if missing_details
                else "Some official eligibility requirements are not available in this profile or system rules."
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
                eligible,

            "official_requirement_failed":
                official_requirement_failed,

            "criteria_configured":
                result["has_substantive_criteria"],

            "missing_criteria":
                result["missing_criteria"],

            "rankable":
                rankable,

            "result_group": result_group,

            "result_group_label": result_group_label,

            "result_group_order": result_group_order,

            "summary_reason": summary_reason,

            "satisfied":
                result["satisfied"],

            "total":
                result["total"],

            "satisfied_criteria":
                result["satisfied_criteria"],

            "failed_criteria":
                result["failed_criteria"],

            "eligibility_guidance":
                eligibility_guidance

        })

    cursor.close()

    # Rank assessable schemes first. Incomplete scheme criteria stay at the end.
    results.sort(
        key=lambda x: (
            -x["result_group_order"],
            x["rankable"],
            x["match_score"],
            x["satisfied"],
        ),
        reverse=True
    )

    rank = 0
    for result in results:
        if result["rankable"]:
            rank += 1
            result["rank"] = rank
        else:
            result["rank"] = None

    return render_template(
        "results.html",
        results=results,
        user=user,
        profile_sections=profile_sections
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

    occupation = request.form.get("occupation") or None

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

    existing_user_id = request.form.get("user_id")
    if existing_user_id:
        try:
            existing_user_id = int(existing_user_id)
        except (ValueError, TypeError):
            existing_user_id = None

    cursor = db.cursor()

    if existing_user_id:
        update_query = """
            UPDATE users SET
                name = %s,
                age = %s,
                gender = %s,
                annual_income = %s,
                occupation = %s,
                education = %s,
                location = %s,
                category = %s,
                domicile = %s,
                admission_mode = %s,
                children_count = %s,
                percentage_12th = %s,
                course_stream = %s,
                graduation_percentage = %s,
                is_pg_student = %s,
                minority_status = %s,
                hostel_status = %s,
                parent_occupation = %s,
                disability_status = %s,
                ex_serviceman_child = %s,
                freedom_fighter_child = %s,
                farmer_id = %s,
                land_holding = %s,
                land_unit = %s,
                land_ownership = %s,
                irrigation_type = %s,
                crop_type = %s,
                farmer_category = %s,
                tribal_status = %s
            WHERE user_id = %s
        """
        cursor.execute(update_query, values + (existing_user_id,))
        db.commit()
        cursor.close()
        return redirect_to_check(existing_user_id)

    # --------------------------------------------------
    # INSERT USER PROFILE
    # --------------------------------------------------

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

    cursor.execute(query, values)
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

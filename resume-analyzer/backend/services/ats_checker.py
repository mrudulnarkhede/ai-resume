import re


# ---------------------------------------------------------
# Check email
# ---------------------------------------------------------

def check_email(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    found = re.search(
        pattern,
        text
    )

    return bool(found)


# ---------------------------------------------------------
# Check phone number
# ---------------------------------------------------------

def check_phone(text):

    pattern = r"(\+?\d[\d\s\-()]{8,}\d)"

    found = re.search(
        pattern,
        text
    )

    return bool(found)


# ---------------------------------------------------------
# Check common resume sections
# ---------------------------------------------------------

def check_sections(resume_data):

    section_checks = {}

    section_checks["skills"] = bool(
        resume_data.get("skills")
    )

    section_checks["education"] = bool(
        resume_data.get("education")
    )

    section_checks["experience"] = bool(
        resume_data.get("experience")
    )

    section_checks["projects"] = bool(
        resume_data.get("projects")
    )

    return section_checks


# ---------------------------------------------------------
# Check resume length
# ---------------------------------------------------------

def check_length(text):

    words = text.split()

    word_count = len(words)

    if word_count < 150:

        return {
            "status": "warning",
            "message":
                "Resume appears very short.",
            "word_count": word_count
        }

    if word_count > 1200:

        return {
            "status": "warning",
            "message":
                "Resume may be too long for an early-career candidate.",
            "word_count": word_count
        }

    return {
        "status": "good",
        "message":
            "Resume length looks reasonable.",
        "word_count": word_count
    }


# ---------------------------------------------------------
# Check bullet usage
# ---------------------------------------------------------

def check_bullets(text):

    lines = text.splitlines()

    bullet_lines = 0

    for line in lines:

        line = line.strip()

        if (
            line.startswith("•")
            or line.startswith("-")
            or line.startswith("*")
            or line.startswith("–")
        ):

            bullet_lines += 1

    if bullet_lines == 0:

        return {
            "status": "warning",
            "message":
                "No bullet points were detected.",
            "bullet_count": 0
        }

    return {
        "status": "good",
        "message":
            "Bullet points were detected.",
        "bullet_count": bullet_lines
    }


# ---------------------------------------------------------
# Check action words
# ---------------------------------------------------------

def check_action_words(text):

    action_words = [

        "developed",
        "designed",
        "built",
        "created",
        "implemented",
        "developed",
        "optimized",
        "improved",
        "automated",
        "analyzed",
        "managed",
        "engineered",
        "deployed",
        "tested",
        "integrated",
        "maintained",
        "configured"

    ]

    text_lower = text.lower()

    found_words = []

    for word in action_words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            text_lower
        ):

            found_words.append(word)

    return {
        "status":
            "good" if found_words else "warning",

        "message":
            (
                "Strong action-oriented language detected."
                if found_words
                else
                "Consider starting resume bullets with action verbs."
            ),

        "action_words":
            sorted(set(found_words))
    }


# ---------------------------------------------------------
# Check contact information
# ---------------------------------------------------------

def check_contact_information(text):

    email_found = check_email(text)

    phone_found = check_phone(text)

    if email_found and phone_found:

        status = "good"

    elif email_found or phone_found:

        status = "warning"

    else:

        status = "warning"

    return {

        "status": status,

        "email": email_found,

        "phone": phone_found
    }


# ---------------------------------------------------------
# Calculate ATS score
# ---------------------------------------------------------

def calculate_ats_score(checks):

    score = 0

    # Contact information
    contact = checks["contact"]

    if contact["email"]:
        score += 15

    if contact["phone"]:
        score += 10

    # Sections
    sections = checks["sections"]

    if sections["skills"]:
        score += 15

    if sections["education"]:
        score += 10

    if sections["experience"]:
        score += 10

    if sections["projects"]:
        score += 10

    # Length
    if checks["length"]["status"] == "good":
        score += 10

    # Bullets
    if checks["bullets"]["status"] == "good":
        score += 10

    # Action words
    if checks["action_words"]["status"] == "good":
        score += 10

    return score


# ---------------------------------------------------------
# Complete ATS analysis
# ---------------------------------------------------------

def analyze_ats(text, resume_data):

    checks = {

        "contact":
            check_contact_information(text),

        "sections":
            check_sections(resume_data),

        "length":
            check_length(text),

        "bullets":
            check_bullets(text),

        "action_words":
            check_action_words(text)
    }

    score = calculate_ats_score(
        checks
    )

    return {

        "score": score,

        "checks": checks
    }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_text = """
    John Doe

    john@example.com
    +91 9876543210

    SKILLS

    Python
    SQL
    Git

    EDUCATION

    B.Tech Information Technology

    PROJECTS

    • Built a Python application.
    • Developed a SQL database.

    EXPERIENCE

    • Implemented REST APIs.
    """

    sample_resume_data = {

        "skills": [
            "Python",
            "SQL",
            "Git"
        ],

        "education": [
            "B.Tech Information Technology"
        ],

        "projects": [
            "Built a Python application."
        ],

        "experience": [
            "Implemented REST APIs."
        ]
    }

    result = analyze_ats(
        sample_text,
        sample_resume_data
    )

    print("\nATS ANALYSIS")
    print("------------")

    print(
        "ATS Score:",
        result["score"],
        "%"
    )

    print("\nContact:")
    print(
        result["checks"]["contact"]
    )

    print("\nSections:")
    print(
        result["checks"]["sections"]
    )

    print("\nLength:")
    print(
        result["checks"]["length"]
    )

    print("\nBullets:")
    print(
        result["checks"]["bullets"]
    )

    print("\nAction Words:")
    print(
        result["checks"]["action_words"]
    )
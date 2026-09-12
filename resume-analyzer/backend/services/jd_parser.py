import re


# ---------------------------------------------------------
# Job Description Section Names
# ---------------------------------------------------------

JD_SECTION_NAMES = {

    "responsibilities": [
        "responsibilities",
        "job responsibilities",
        "roles and responsibilities",
        "what you'll do",
        "what you will do",
        "duties"
    ],

    "qualifications": [
        "qualifications",
        "requirements",
        "basic qualifications",
        "minimum qualifications",
        "required qualifications"
    ],

    "preferred": [
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "good to have",
        "preferred"
    ],

    "skills": [
        "skills",
        "technical skills",
        "required skills",
        "technologies",
        "technical requirements"
    ]
}


# ---------------------------------------------------------
# Clean Text Lines
# ---------------------------------------------------------

def clean_line(line):
    """
    Remove unnecessary spaces from a line.
    """

    return re.sub(r"\s+", " ", line).strip()


# ---------------------------------------------------------
# Detect JD Section
# ---------------------------------------------------------

def detect_jd_section(line):
    """
    Detect whether a line is a Job Description section heading.
    """

    normalized = line.lower().strip()

    # Remove :, -, or * from the end of the heading
    normalized = re.sub(r"[:\-\*]+$", "", normalized)

    for section, names in JD_SECTION_NAMES.items():

        if normalized in names:
            return section

    return None


# ---------------------------------------------------------
# Extract Job Title
# ---------------------------------------------------------

def extract_job_title(lines):
    """
    Try to identify the job title from the beginning
    of the job description.
    """

    ignored_phrases = [
        "job description",
        "job analysis",
        "location",
        "salary",
        "posted",
        "company",
        "department"
    ]

    for line in lines[:10]:

        line = clean_line(line)

        if not line:
            continue

        lower_line = line.lower()

        # Ignore common metadata
        if any(phrase in lower_line for phrase in ignored_phrases):
            continue

        # Ignore section headings
        if detect_jd_section(line):
            continue

        # Job titles are usually relatively short
        if 1 <= len(line.split()) <= 8:
            return line

    return ""


# ---------------------------------------------------------
# Extract Technical Skills
# ---------------------------------------------------------

def extract_skills(text):
    """
    Extract known technical skills from the JD.

    Uses regular expressions so that:
        C++  -> detected as C++
        C    -> NOT detected inside C++
    """

    known_skills = [

        # Programming languages
        "Python",
        "Java",
        "C++",
        "C#",
        "C",
        "JavaScript",
        "TypeScript",

        # Frontend
        "React",
        "Angular",
        "Vue",
        "HTML",
        "CSS",

        # Backend
        "Node.js",
        "Flask",
        "Django",

        # Databases
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",

        # Tools
        "Git",
        "GitHub",
        "Docker",
        "Kubernetes",

        # Cloud
        "AWS",
        "Azure",
        "GCP",

        # AI / Data
        "Machine Learning",
        "Deep Learning",
        "Data Science",

        # CS concepts
        "Data Structures",
        "Algorithms",

        # APIs
        "REST API",
        "REST APIs",

        # Operating systems
        "Linux"
    ]

    found_skills = []

    for skill in known_skills:

        # Create a safe pattern that prevents
        # C from matching inside C++
        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, text, re.IGNORECASE):

            found_skills.append(skill)

    return found_skills


# ---------------------------------------------------------
# Parse Job Description
# ---------------------------------------------------------

def parse_job_description(text):
    """
    Convert raw Job Description text into structured data.
    """

    lines = text.splitlines()

    sections = {
        "responsibilities": [],
        "qualifications": [],
        "preferred": [],
        "skills": []
    }

    current_section = None

    # ---------------------------------------------
    # Identify different sections
    # ---------------------------------------------

    for line in lines:

        line = clean_line(line)

        if not line:
            continue

        detected_section = detect_jd_section(line)

        if detected_section:

            current_section = detected_section
            continue

        if current_section:

            sections[current_section].append(line)

    # ---------------------------------------------
    # Extract all technical skills
    # ---------------------------------------------

    all_skills = extract_skills(text)

    # ---------------------------------------------
    # Extract preferred skills
    # only from the preferred section
    # ---------------------------------------------

    preferred_text = " ".join(sections["preferred"])

    preferred_skills = extract_skills(preferred_text)

    # ---------------------------------------------
    # Required skills
    #
    # Anything detected in the JD that is NOT
    # specifically inside the preferred section
    # is treated as required.
    # ---------------------------------------------

    required_skills = [
        skill
        for skill in all_skills
        if skill not in preferred_skills
    ]

    # ---------------------------------------------
    # Return structured JD
    # ---------------------------------------------

    return {
        "job_title": extract_job_title(lines),

        "required_skills": required_skills,

        "preferred_skills": preferred_skills,

        "responsibilities": sections["responsibilities"],

        "qualifications": sections["qualifications"]
    }


# ---------------------------------------------------------
# Test the parser directly
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_jd = """
    Software Engineer Intern

    Responsibilities

    Develop software applications using modern programming practices.
    Work with engineering teams to build reliable software.
    Write clean and maintainable code.
    Debug software issues and improve application performance.

    Requirements

    Strong programming skills in Python and C++.
    Knowledge of Data Structures and Algorithms.
    Experience with SQL and Git.
    Good problem solving skills.

    Preferred Qualifications

    Knowledge of Docker and AWS.
    Knowledge of REST APIs.
    """

    result = parse_job_description(sample_jd)

    print("\nJOB DESCRIPTION ANALYSIS")
    print("------------------------")

    print("\nJob Title:")
    print(result["job_title"])

    print("\nRequired Skills:")
    for skill in result["required_skills"]:
        print("-", skill)

    print("\nPreferred Skills:")
    for skill in result["preferred_skills"]:
        print("-", skill)

    print("\nResponsibilities:")
    for item in result["responsibilities"]:
        print("-", item)

    print("\nQualifications:")
    for item in result["qualifications"]:
        print("-", item)
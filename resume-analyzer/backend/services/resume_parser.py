import re


SECTION_NAMES = {
    "education": [
        "education",
        "academic background",
        "academics"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment"
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical expertise"
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses"
    ]
}


def clean_line(line):
    """Remove unnecessary spaces from a line."""
    return re.sub(r"\s+", " ", line).strip()


def detect_section(line):
    """Detect whether a line is a resume section heading."""

    normalized = line.lower().strip()

    # Remove : or - from the end
    normalized = re.sub(r"[:\-]+$", "", normalized)

    for section, names in SECTION_NAMES.items():

        if normalized in names:
            return section

    return None


def extract_name(lines):
    """
    Try to identify the candidate's name.
    Usually the name appears near the top of the resume.
    """

    for line in lines[:10]:

        line = clean_line(line)

        if not line:
            continue

        lower_line = line.lower()

        # Ignore contact information
        if any(keyword in lower_line for keyword in [
            "@",
            "linkedin",
            "github",
            "phone",
            "mobile",
            "email",
            "resume",
            "curriculum vitae"
        ]):
            continue

        # Ignore section headings
        if detect_section(line):
            continue

        words = line.split()

        # A person's name is usually 2–4 words
        if 2 <= len(words) <= 4:
            return line

    return ""


def extract_skills(skill_lines):
    """
    Convert the skills section into a list of individual skills.
    """

    skills = []

    for line in skill_lines:

        # Remove common category labels
        line = re.sub(
            r"^(programming|languages|web|database|frameworks|tools|technologies)\s*:\s*",
            "",
            line,
            flags=re.IGNORECASE
        )

        # Split skills using common separators
        parts = re.split(r"[,|•;/]", line)

        for part in parts:

            skill = part.strip()

            if skill:
                skills.append(skill)

    return skills


def parse_resume_sections(text):
    """
    Convert raw resume text into structured sections.
    """

    lines = text.splitlines()

    # Extract candidate name
    name = extract_name(lines)

    sections = {
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "achievements": [],
        "certifications": []
    }

    current_section = None

    for line in lines:

        line = clean_line(line)

        if not line:
            continue

        # Check whether this line is a section heading
        detected_section = detect_section(line)

        if detected_section:

            current_section = detected_section
            continue

        # Add content to the current section
        if current_section:

            sections[current_section].append(line)

    # Convert skills from lines into individual skills
    skills = extract_skills(sections["skills"])

    return {
        "name": name,
        "education": sections["education"],
        "experience": sections["experience"],
        "projects": sections["projects"],
        "skills": skills,
        "achievements": sections["achievements"],
        "certifications": sections["certifications"]
    }
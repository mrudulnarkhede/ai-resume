import os

from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Create Groq client
# ---------------------------------------------------------

api_key = os.getenv("GROQ_API_KEY")

client = None

if api_key:
    client = Groq(
        api_key=api_key
    )


# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

MODEL_NAME = "openai/gpt-oss-120b"


# ---------------------------------------------------------
# Generate AI resume analysis
# ---------------------------------------------------------

def generate_ai_analysis(
    resume_data,
    jd_data,
    overall_match,
    skill_coverage,
    recommendations
):

    if client is None:

        return {
            "success": False,
            "error":
                "GROQ_API_KEY is not configured."
        }


    # -----------------------------------------------------
    # Prepare resume information
    # -----------------------------------------------------

    resume_skills = resume_data.get(
        "skills",
        []
    )

    resume_experience = resume_data.get(
        "experience",
        []
    )

    resume_projects = resume_data.get(
        "projects",
        []
    )

    resume_education = resume_data.get(
        "education",
        []
    )


    # -----------------------------------------------------
    # Prepare JD information
    # -----------------------------------------------------

    required_skills = jd_data.get(
        "required_skills",
        []
    )

    preferred_skills = jd_data.get(
        "preferred_skills",
        []
    )

    responsibilities = jd_data.get(
        "responsibilities",
        []
    )

    qualifications = jd_data.get(
        "qualifications",
        []
    )


    # -----------------------------------------------------
    # Prepare recommendations
    # -----------------------------------------------------

    recommendation_text = "\n".join(
        [
            f"- {item.get('title', '')}: "
            f"{item.get('message', '')}"
            for item in recommendations
        ]
    )


    # -----------------------------------------------------
    # Build prompt
    # -----------------------------------------------------

    prompt = f"""
You are an expert resume reviewer and career assistant.

Analyze the candidate's resume against the provided
job description.

IMPORTANT RULES:

1. Do NOT invent experience.
2. Do NOT invent skills.
3. Do NOT invent projects.
4. Do NOT invent achievements.
5. Do NOT invent numbers or performance metrics.
6. Only use information provided in the resume data.
7. If information is missing, clearly say that it is missing.
8. Do not encourage the candidate to lie on their resume.
9. Keep recommendations practical for a student or early-career candidate.
10. Be concise and specific.

--------------------------------------------------
MATCH SCORE
--------------------------------------------------

Overall Match:
{overall_match}%

Required Skill Coverage:
{skill_coverage.get('required_coverage', 0)}%

Preferred Skill Coverage:
{skill_coverage.get('preferred_coverage', 0)}%

--------------------------------------------------
RESUME
--------------------------------------------------

Skills:
{resume_skills}

Experience:
{resume_experience}

Projects:
{resume_projects}

Education:
{resume_education}

--------------------------------------------------
JOB DESCRIPTION
--------------------------------------------------

Required Skills:
{required_skills}

Preferred Skills:
{preferred_skills}

Responsibilities:
{responsibilities}

Qualifications:
{qualifications}

--------------------------------------------------
RULE-BASED RECOMMENDATIONS
--------------------------------------------------

{recommendation_text}

--------------------------------------------------
TASK
--------------------------------------------------

Provide the following:

1. A short summary of the candidate's strengths.

2. A short summary of the candidate's weaknesses
   relative to this job.

3. The top 5 improvements the candidate should make.

4. Explain which missing skills are most important.

5. Give suggestions for improving existing resume
   bullets.

6. If a resume bullet could be improved, show:

   Current:
   [existing information]

   Suggested:
   [improved version]

7. Never add facts that are not present in the
   candidate's resume.

Return the answer using these headings:

STRENGTHS

WEAKNESSES

TOP IMPROVEMENTS

IMPORTANT MISSING SKILLS

BULLET IMPROVEMENTS
"""


    # -----------------------------------------------------
    # Call Groq
    # -----------------------------------------------------

    try:

        completion = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content":
                        "You are a precise and honest "
                        "resume analysis assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_completion_tokens=2000
        )


        response_text = (
            completion
            .choices[0]
            .message
            .content
        )


        return {
            "success": True,
            "analysis": response_text
        }


    except Exception as error:

     error_message = str(error)

     if "401" in error_message:

        user_message = (
            "Groq API authentication failed. "
            "Please check your GROQ_API_KEY."
        )

     elif "429" in error_message:

        user_message = (
            "Groq API rate limit reached. "
            "Please try again later."
        )

     elif "404" in error_message:

        user_message = (
            "The selected Groq model is unavailable."
        )

     else:

        user_message = (
            "AI analysis could not be completed."
        )

     return {
        "success": False,
        "error": user_message
    }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    test_resume = {

        "skills": [
            "Python",
            "SQL",
            "Git"
        ],

        "experience": [
            "Developed a Python application."
        ],

        "projects": [
            "Built a student management system."
        ],

        "education": [
            "B.Tech Information Technology"
        ]
    }


    test_jd = {

        "required_skills": [
            "Python",
            "C++",
            "SQL"
        ],

        "preferred_skills": [
            "Docker",
            "AWS"
        ],

        "responsibilities": [
            "Develop software applications.",
            "Debug software issues."
        ],

        "qualifications": [
            "Knowledge of Data Structures and Algorithms."
        ]
    }


    test_recommendations = [

        {
            "title":
                "Learn or demonstrate C++",

            "message":
                "C++ was not detected in the resume."
        },

        {
            "title":
                "Consider adding Docker",

            "message":
                "Docker is preferred for this role."
        }
    ]


    result = generate_ai_analysis(

        test_resume,

        test_jd,

        68.5,

        {
            "required_coverage": 66.67,
            "preferred_coverage": 0
        },

        test_recommendations
    )


    if result["success"]:

        print("\nAI ANALYSIS")
        print("-----------")

        print(
            result["analysis"]
        )

    else:

        print(
            "ERROR:",
            result["error"]
        )
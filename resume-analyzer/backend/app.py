from flask import Flask, request
from flask_cors import CORS

from services.pdf_parser import extract_text_from_pdf
from services.resume_parser import parse_resume_sections
from services.jd_parser import parse_job_description

from services.matcher import (
    match_requirements,
    match_skills,
    calculate_skill_coverage,
    calculate_overall_score,
    get_score_breakdown
)

from services.recommendations import (
    generate_recommendations,
    summarize_recommendations
)

from services.ai_service import generate_ai_analysis

from services.ats_checker import analyze_ats


app = Flask(__name__)

CORS(app)


# ---------------------------------------------------------
# Global error handler
# ---------------------------------------------------------

@app.errorhandler(Exception)
def handle_error(error):
    print("SERVER ERROR:", error)

    return {
        "error": "Something went wrong while analyzing your resume."
    }, 500


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Resume Analyzer API is running!"
    }


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


# ---------------------------------------------------------
# Parse Resume
# ---------------------------------------------------------

@app.post("/api/parse-resume")
def parse_resume():

    # Check whether resume was uploaded
    if "resume" not in request.files:
        return {
            "error": "No resume file uploaded."
        }, 400

    file = request.files["resume"]

    # Check filename
    if file.filename == "":
        return {
            "error": "No file selected."
        }, 400

    # Check extension
    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are supported."
        }, 400

    # Check MIME type
    if file.mimetype != "application/pdf":
        return {
            "error": "Please upload a valid PDF file."
        }, 400

    try:
        text = extract_text_from_pdf(file)

        sections = parse_resume_sections(text)

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    return {
        "filename": file.filename,
        "text": text,
        "sections": sections
    }


# ---------------------------------------------------------
# Analyze Job Description
# ---------------------------------------------------------

@app.post("/api/analyze-jd")
def analyze_jd():

    data = request.get_json()

    if not data:
        return {
            "error": "No data provided."
        }, 400

    job_description = data.get(
        "job_description",
        ""
    ).strip()

    if not job_description:
        return {
            "error": "Job description is required."
        }, 400

    if len(job_description) < 30:
        return {
            "error": "Job description is too short."
        }, 400

    result = parse_job_description(job_description)

    return result


# ---------------------------------------------------------
# Complete Analysis
# ---------------------------------------------------------

@app.post("/api/analyze")
def analyze():

    # -----------------------------------------------------
    # Resume validation
    # -----------------------------------------------------

    if "resume" not in request.files:
        return {
            "error": "Please upload a resume PDF."
        }, 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return {
            "error": "No resume file selected."
        }, 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are supported."
        }, 400

    if resume_file.mimetype != "application/pdf":
        return {
            "error": "Please upload a valid PDF file."
        }, 400

    # -----------------------------------------------------
    # Job description validation
    # -----------------------------------------------------

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if not job_description:
        return {
            "error": "Please enter a job description."
        }, 400

    if len(job_description) < 30:
        return {
            "error": (
                "Job description is too short. "
                "Please provide a complete job description."
            )
        }, 400

    # -----------------------------------------------------
    # Parse resume
    # -----------------------------------------------------

    try:
        resume_text = extract_text_from_pdf(resume_file)

        resume_data = parse_resume_sections(
            resume_text
        )

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    # -----------------------------------------------------
    # Basic resume validation
    # -----------------------------------------------------

    if len(resume_text.split()) < 30:
        return {
            "error": (
                "The resume contains too little readable "
                "text. Please upload a proper resume PDF."
            )
        }, 400

    # -----------------------------------------------------
    # ATS analysis
    # -----------------------------------------------------

    ats_result = analyze_ats(
        resume_text,
        resume_data
    )

    # -----------------------------------------------------
    # Parse JD
    # -----------------------------------------------------

    jd_data = parse_job_description(
        job_description
    )

    # -----------------------------------------------------
    # Resume items for semantic matching
    # -----------------------------------------------------

    resume_items = []

    resume_items.extend(
        resume_data.get(
            "skills",
            []
        )
    )

    resume_items.extend(
        resume_data.get(
            "education",
            []
        )
    )

    resume_items.extend(
        resume_data.get(
            "experience",
            []
        )
    )

    resume_items.extend(
        resume_data.get(
            "projects",
            []
        )
    )

    resume_items.extend(
        resume_data.get(
            "achievements",
            []
        )
    )

    resume_items.extend(
        resume_data.get(
            "certifications",
            []
        )
    )

    # Clean resume items
    resume_items = [
        item.strip()
        for item in resume_items
        if isinstance(item, str)
        and item.strip()
    ]

    # Remove duplicates
    resume_items = list(
        dict.fromkeys(resume_items)
    )

    # -----------------------------------------------------
    # Job requirements
    # -----------------------------------------------------

    requirements = []

    requirements.extend(
        jd_data.get(
            "required_skills",
            []
        )
    )

    requirements.extend(
        jd_data.get(
            "qualifications",
            []
        )
    )

    requirements.extend(
        jd_data.get(
            "responsibilities",
            []
        )
    )

    # Clean requirements
    requirements = [
        item.strip()
        for item in requirements
        if isinstance(item, str)
        and item.strip()
    ]

    # Remove duplicates
    requirements = list(
        dict.fromkeys(requirements)
    )

    # -----------------------------------------------------
    # Semantic matching
    # -----------------------------------------------------

    semantic_results = match_requirements(
        resume_items,
        requirements
    )

    # -----------------------------------------------------
    # Skill matching
    # -----------------------------------------------------

    skill_results = match_skills(
        resume_data.get(
            "skills",
            []
        ),
        jd_data.get(
            "required_skills",
            []
        ),
        jd_data.get(
            "preferred_skills",
            []
        )
    )

    # -----------------------------------------------------
    # Skill coverage
    # -----------------------------------------------------

    skill_coverage = calculate_skill_coverage(
        skill_results
    )

    # -----------------------------------------------------
    # Overall score
    # -----------------------------------------------------

    overall_score = calculate_overall_score(
        semantic_results,
        skill_coverage
    )

    # -----------------------------------------------------
    # Score breakdown
    # -----------------------------------------------------

    score_breakdown = get_score_breakdown(
        semantic_results,
        skill_coverage
    )

    # -----------------------------------------------------
    # Matched / missing required skills
    # -----------------------------------------------------

    matched_required_skills = [
        item
        for item in skill_results["required"]
        if item.get("matched", False)
    ]

    missing_required_skills = [
        item
        for item in skill_results["required"]
        if not item.get("matched", False)
    ]

    # -----------------------------------------------------
    # Matched / missing preferred skills
    # -----------------------------------------------------

    matched_preferred_skills = [
        item
        for item in skill_results["preferred"]
        if item.get("matched", False)
    ]

    missing_preferred_skills = [
        item
        for item in skill_results["preferred"]
        if not item.get("matched", False)
    ]

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    recommendations = generate_recommendations(
        missing_required_skills,
        missing_preferred_skills,
        semantic_results
    )

    recommendation_summary = summarize_recommendations(
        recommendations
    )

    # -----------------------------------------------------
    # AI analysis
    # -----------------------------------------------------

    ai_analysis = generate_ai_analysis(
        resume_data,
        jd_data,
        overall_score,
        skill_coverage,
        recommendations
    )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "resume": {
            "filename": resume_file.filename,
            "name": resume_data.get(
                "name",
                ""
            )
        },

        "job": {
            "title": jd_data.get(
                "job_title",
                ""
            )
        },

        "ats": ats_result,

        "required_skills": jd_data.get(
            "required_skills",
            []
        ),

        "preferred_skills": jd_data.get(
            "preferred_skills",
            []
        ),

        "matched_required_skills": matched_required_skills,

        "missing_required_skills": missing_required_skills,

        "matched_preferred_skills": matched_preferred_skills,

        "missing_preferred_skills": missing_preferred_skills,

        "skill_coverage": skill_coverage,

        "overall_match": overall_score,

        "score_breakdown": score_breakdown,

        "matches": semantic_results,

        "recommendations": recommendations,

        "recommendation_summary": recommendation_summary,

        "ai_analysis": ai_analysis
    }


# ---------------------------------------------------------
# Run server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
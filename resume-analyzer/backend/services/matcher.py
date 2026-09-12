import numpy as np


try:
    from services.embeddings import (
        generate_embeddings
    )
except ImportError:
    from embeddings import (
        generate_embeddings
    )


# =========================================================
# Skill aliases
# =========================================================

SKILL_ALIASES = {

    "rest api": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ],

    "javascript": [
        "javascript",
        "js"
    ],

    "typescript": [
        "typescript",
        "ts"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "data structures": [
        "data structures",
        "data structure"
    ],

    "algorithms": [
        "algorithms",
        "algorithm"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "postgres"
    ],

    "git": [
        "git",
        "github",
        "gitlab"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "docker": [
        "docker",
        "docker containers",
        "containerization"
    ],

    "python": [
        "python",
        "python3",
        "python 3"
    ],

    "cpp": [
        "c++",
        "cpp"
    ],

    "node.js": [
        "node.js",
        "nodejs",
        "node"
    ],

    "react": [
        "react",
        "react.js",
        "reactjs"
    ],

    "flask": [
        "flask"
    ],

    "django": [
        "django"
    ]

}


# =========================================================
# Normalize skill
# =========================================================

def normalize_skill(skill):

    if not skill:
        return ""

    value = skill.lower().strip()

    value = value.replace(
        "react.js",
        "react"
    )

    value = value.replace(
        "reactjs",
        "react"
    )

    value = value.replace(
        "nodejs",
        "node.js"
    )

    value = value.replace(
        "cpp",
        "c++"
    )

    for canonical, aliases in SKILL_ALIASES.items():

        if value in aliases:
            return canonical

    return value


# =========================================================
# Cosine similarity
# =========================================================

def cosine_similarity(
    vector_a,
    vector_b
):

    vector_a = np.array(
        vector_a
    )

    vector_b = np.array(
        vector_b
    )

    dot_product = np.dot(
        vector_a,
        vector_b
    )

    magnitude_a = np.linalg.norm(
        vector_a
    )

    magnitude_b = np.linalg.norm(
        vector_b
    )

    if (
        magnitude_a == 0
        or
        magnitude_b == 0
    ):

        return 0.0

    similarity = (
        dot_product
        /
        (
            magnitude_a
            *
            magnitude_b
        )
    )

    return float(
        similarity
    )


# =========================================================
# Semantic requirement matching
# =========================================================

def match_requirements(
    resume_items,
    requirements
):

    if (
        not resume_items
        or
        not requirements
    ):

        return []

    resume_embeddings = (
        generate_embeddings(
            resume_items
        )
    )

    requirement_embeddings = (
        generate_embeddings(
            requirements
        )
    )

    results = []

    for i, requirement in enumerate(
        requirements
    ):

        best_score = -1

        best_evidence = ""

        for j, resume_item in enumerate(
            resume_items
        ):

            score = cosine_similarity(

                requirement_embeddings[i],

                resume_embeddings[j]

            )

            if score > best_score:

                best_score = score

                best_evidence = resume_item

        percentage = round(

            max(
                0.0,
                best_score
            ) * 100,

            2

        )

        if percentage >= 75:

            match_level = "strong"

        elif percentage >= 50:

            match_level = "partial"

        else:

            match_level = "weak"

        results.append({

            "requirement":
                requirement,

            "similarity":
                round(
                    max(
                        0.0,
                        best_score
                    ),
                    4
                ),

            "match_percentage":
                percentage,

            "match_level":
                match_level,

            "evidence":
                best_evidence

        })

    return results


# =========================================================
# Semantic skill matching
# =========================================================

def semantic_skill_match(
    resume_skills,
    target_skill
):

    if not resume_skills:

        return {

            "matched": False,

            "score": 0.0,

            "evidence": ""

        }

    resume_embeddings = (
        generate_embeddings(
            resume_skills
        )
    )

    target_embedding = (
        generate_embeddings(
            [target_skill]
        )[0]
    )

    best_score = -1

    best_evidence = ""

    for index, embedding in enumerate(
        resume_embeddings
    ):

        score = cosine_similarity(

            target_embedding,

            embedding

        )

        if score > best_score:

            best_score = score

            best_evidence = (
                resume_skills[index]
            )

    # Conservative semantic threshold
    # to reduce false positives.

    matched = (
        best_score >= 0.65
    )

    return {

        "matched":
            matched,

        "score":
            round(
                max(
                    0.0,
                    best_score
                ),
                4
            ),

        "evidence":
            best_evidence

    }


# =========================================================
# Process one skill
# =========================================================

def process_skill(
    skill,
    normalized_resume,
    resume_skills
):

    normalized = normalize_skill(
        skill
    )

    # -----------------------------------------------------
    # Exact / alias match
    # -----------------------------------------------------

    if normalized in normalized_resume:

        return {

            "skill":
                skill,

            "matched":
                True,

            "match_type":
                "exact",

            "evidence":
                normalized_resume[
                    normalized
                ],

            "similarity":
                1.0

        }

    # -----------------------------------------------------
    # Semantic match
    # -----------------------------------------------------

    semantic_result = (
        semantic_skill_match(
            resume_skills,
            skill
        )
    )

    if semantic_result["matched"]:

        return {

            "skill":
                skill,

            "matched":
                True,

            "match_type":
                "semantic",

            "evidence":
                semantic_result[
                    "evidence"
                ],

            "similarity":
                semantic_result[
                    "score"
                ]

        }

    # -----------------------------------------------------
    # Missing
    # -----------------------------------------------------

    return {

        "skill":
            skill,

        "matched":
            False,

        "match_type":
            "missing",

        "evidence":
            semantic_result[
                "evidence"
            ],

        "similarity":
            semantic_result[
                "score"
            ]

    }


# =========================================================
# Skill matching
# =========================================================

def match_skills(
    resume_skills,
    required_skills,
    preferred_skills
):

    resume_skills = (
        resume_skills
        if resume_skills
        else []
    )

    required_skills = (
        required_skills
        if required_skills
        else []
    )

    preferred_skills = (
        preferred_skills
        if preferred_skills
        else []
    )

    # -----------------------------------------------------
    # Normalize resume skills
    # -----------------------------------------------------

    normalized_resume = {}

    for skill in resume_skills:

        normalized = normalize_skill(
            skill
        )

        if normalized:

            normalized_resume[
                normalized
            ] = skill

    # -----------------------------------------------------
    # Required skills
    # -----------------------------------------------------

    required_results = []

    for skill in required_skills:

        required_results.append(

            process_skill(
                skill,
                normalized_resume,
                resume_skills
            )

        )

    # -----------------------------------------------------
    # Preferred skills
    # -----------------------------------------------------

    preferred_results = []

    for skill in preferred_skills:

        preferred_results.append(

            process_skill(
                skill,
                normalized_resume,
                resume_skills
            )

        )

    return {

        "required":
            required_results,

        "preferred":
            preferred_results

    }


# =========================================================
# Skill coverage
# =========================================================

def calculate_skill_coverage(
    skill_results
):

    required = skill_results[
        "required"
    ]

    preferred = skill_results[
        "preferred"
    ]

    # -----------------------------------------------------
    # Calculate one category
    # -----------------------------------------------------

    def calculate_category(items):

        if not items:

            return 0.0

        total_score = 0.0

        for item in items:

            # Exact match
            if item["match_type"] == "exact":

                total_score += 1.0

            # Semantic match
            elif item["match_type"] == "semantic":

                total_score += min(
                    max(
                        item["similarity"],
                        0.0
                    ),
                    1.0
                )

            # Missing skill
            else:

                total_score += 0.0

        coverage = (
            total_score
            /
            len(items)
        ) * 100

        return round(
            coverage,
            2
        )

    required_coverage = (
        calculate_category(
            required
        )
    )

    preferred_coverage = (
        calculate_category(
            preferred
        )
    )

    return {

        "required_coverage":
            required_coverage,

        "preferred_coverage":
            preferred_coverage

    }


# =========================================================
# Semantic score
# =========================================================

def calculate_semantic_score(
    semantic_results
):

    if not semantic_results:

        return 0.0

    total = sum(

        max(
            0.0,
            min(
                result.get(
                    "similarity",
                    0.0
                ),
                1.0
            )
        )

        for result
        in semantic_results

    )

    average = (
        total
        /
        len(
            semantic_results
        )
    )

    return round(
        average * 100,
        2
    )


# =========================================================
# Score classification
# =========================================================

def classify_score(score):

    if score >= 80:

        return "Excellent Match"

    elif score >= 65:

        return "Strong Match"

    elif score >= 50:

        return "Moderate Match"

    elif score >= 35:

        return "Weak Match"

    else:

        return "Low Match"


# =========================================================
# Overall score
# =========================================================

def calculate_overall_score(
    semantic_results,
    skill_coverage
):

    required_score = (
        skill_coverage[
            "required_coverage"
        ]
    )

    preferred_score = (
        skill_coverage[
            "preferred_coverage"
        ]
    )

    semantic_score = (
        calculate_semantic_score(
            semantic_results
        )
    )

    # -----------------------------------------------------
    # Weighted scoring
    #
    # Required Skills      = 55%
    # Preferred Skills     = 15%
    # Semantic Relevance   = 30%
    # -----------------------------------------------------

    overall_score = (

        required_score * 0.55

        +

        preferred_score * 0.15

        +

        semantic_score * 0.30

    )

    overall_score = round(
        overall_score,
        2
    )

    return overall_score


# =========================================================
# Score breakdown
# =========================================================

def get_score_breakdown(
    semantic_results,
    skill_coverage
):

    required_score = (
        skill_coverage[
            "required_coverage"
        ]
    )

    preferred_score = (
        skill_coverage[
            "preferred_coverage"
        ]
    )

    semantic_score = (
        calculate_semantic_score(
            semantic_results
        )
    )

    required_contribution = (
        required_score * 0.55
    )

    preferred_contribution = (
        preferred_score * 0.15
    )

    semantic_contribution = (
        semantic_score * 0.30
    )

    final_score = (
        required_contribution
        +
        preferred_contribution
        +
        semantic_contribution
    )

    return {

        "required_skills": round(
            required_score,
            2
        ),

        "preferred_skills": round(
            preferred_score,
            2
        ),

        "semantic_relevance": round(
            semantic_score,
            2
        ),

        "required_weight": 55,

        "preferred_weight": 15,

        "semantic_weight": 30,

        "required_contribution": round(
            required_contribution,
            2
        ),

        "preferred_contribution": round(
            preferred_contribution,
            2
        ),

        "semantic_contribution": round(
            semantic_contribution,
            2
        ),

        "final_score": round(
            final_score,
            2
        ),

        "classification":
            classify_score(
                final_score
            )

    }


# =========================================================
# Direct test
# =========================================================

if __name__ == "__main__":

    resume_skills = [

        "Python",

        "SQL",

        "Git",

        "React",

        "Flask"

    ]

    required_skills = [

        "Python",

        "REST APIs",

        "SQL",

        "C++"

    ]

    preferred_skills = [

        "Docker",

        "AWS"

    ]

    print(
        "\nSMART SKILL MATCHING"
    )

    print(
        "--------------------"
    )

    results = match_skills(

        resume_skills,

        required_skills,

        preferred_skills

    )

    print(
        "\nRequired Skills:"
    )

    for item in results[
        "required"
    ]:

        print(

            item["skill"],

            "→",

            item["match_type"],

            "→",

            item["similarity"]

        )

    print(
        "\nPreferred Skills:"
    )

    for item in results[
        "preferred"
    ]:

        print(

            item["skill"],

            "→",

            item["match_type"],

            "→",

            item["similarity"]

        )

    coverage = (
        calculate_skill_coverage(
            results
        )
    )

    print(
        "\nCoverage:"
    )

    print(
        coverage
    )

    # -----------------------------------------------------
    # Semantic test
    # -----------------------------------------------------

    resume_items = [

        "Developed web applications using Python and Flask.",

        "Built REST APIs for backend services.",

        "Worked with SQL databases.",

        "Developed responsive React applications."

    ]

    requirements = [

        "Develop backend APIs",

        "Work with databases",

        "Build frontend applications"

    ]

    semantic_results = (
        match_requirements(
            resume_items,
            requirements
        )
    )

    print(
        "\nSemantic Results:"
    )

    for result in semantic_results:

        print(
            result
        )

    score = calculate_overall_score(

        semantic_results,

        coverage

    )

    print(
        "\nOverall Score:"
    )

    print(
        f"{score}%"
    )

    breakdown = get_score_breakdown(

        semantic_results,

        coverage

    )

    print(
        "\nScore Breakdown:"
    )

    print(
        breakdown
    )
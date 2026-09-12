def generate_recommendations(
    missing_required_skills,
    missing_preferred_skills,
    semantic_results
):

    recommendations = []


    # -----------------------------------------------------
    # Missing required skills
    # -----------------------------------------------------

    for item in missing_required_skills:

        skill = item["skill"]

        recommendations.append({

            "type":
                "missing_required_skill",

            "priority":
                "high",

            "title":
                f"Learn or demonstrate {skill}",

            "message":
                (
                    f"The job description requires "
                    f"{skill}, but strong evidence "
                    f"was not detected in your resume."
                ),

            "skill":
                skill,

            "similarity":
                item.get(
                    "similarity",
                    0
                ),

            "evidence":
                item.get(
                    "evidence",
                    ""
                )

        })


    # -----------------------------------------------------
    # Missing preferred skills
    # -----------------------------------------------------

    for item in missing_preferred_skills:

        skill = item["skill"]

        recommendations.append({

            "type":
                "missing_preferred_skill",

            "priority":
                "medium",

            "title":
                f"Consider adding {skill}",

            "message":
                (
                    f"{skill} is listed as a preferred "
                    f"skill for this role."
                ),

            "skill":
                skill,

            "similarity":
                item.get(
                    "similarity",
                    0
                ),

            "evidence":
                item.get(
                    "evidence",
                    ""
                )

        })


    # -----------------------------------------------------
    # Weak requirements
    # -----------------------------------------------------

    for result in semantic_results:

        if result["match_percentage"] < 50:

            recommendations.append({

                "type":
                    "weak_requirement",

                "priority":
                    "medium",

                "title":
                    "Improve resume evidence",

                "message":
                    (
                        "Your resume has weak semantic "
                        "evidence for this requirement."
                    ),

                "requirement":
                    result["requirement"],

                "evidence":
                    result["evidence"],

                "match_percentage":
                    result["match_percentage"]

            })


    # -----------------------------------------------------
    # Partial requirements
    # -----------------------------------------------------

    for result in semantic_results:

        if (

            result["match_percentage"] >= 50

            and

            result["match_percentage"] < 75

        ):

            recommendations.append({

                "type":
                    "partial_requirement",

                "priority":
                    "low",

                "title":
                    "Strengthen resume evidence",

                "message":
                    (
                        "Your resume contains related "
                        "evidence, but it could be stronger."
                    ),

                "requirement":
                    result["requirement"],

                "evidence":
                    result["evidence"],

                "match_percentage":
                    result["match_percentage"]

            })


    return recommendations


def summarize_recommendations(
    recommendations
):

    high_priority = [

        item

        for item in recommendations

        if item["priority"] == "high"

    ]


    medium_priority = [

        item

        for item in recommendations

        if item["priority"] == "medium"

    ]


    low_priority = [

        item

        for item in recommendations

        if item["priority"] == "low"

    ]


    return {

        "total":
            len(recommendations),

        "high_priority":
            len(high_priority),

        "medium_priority":
            len(medium_priority),

        "low_priority":
            len(low_priority)

    }


if __name__ == "__main__":

    missing_required = [

        {
            "skill":
                "C++",

            "similarity":
                0.35,

            "evidence":
                "Python programming"

        }

    ]


    missing_preferred = [

        {
            "skill":
                "AWS",

            "similarity":
                0.42,

            "evidence":
                "Docker project"

        }

    ]


    semantic_results = [

        {

            "requirement":
                "Experience developing scalable applications",

            "match_percentage":
                42,

            "evidence":
                "Built a Python application."

        }

    ]


    result = generate_recommendations(

        missing_required,

        missing_preferred,

        semantic_results

    )


    print(
        "\nRECOMMENDATIONS"
    )

    print(
        "---------------"
    )


    for item in result:

        print(
            "\n",
            item["priority"].upper()
        )

        print(
            item["title"]
        )

        print(
            item["message"]
        )
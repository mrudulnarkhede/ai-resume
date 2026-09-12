import { useState } from "react";


function Analyzer() {

  const [resume, setResume] = useState(null);

  const [jobDescription, setJobDescription] = useState("");

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  // =========================================================
  // Score Helpers
  // =========================================================

  const getScoreStatus = (score) => {

    if (score >= 80) {
      return {
        label: "Excellent",
        description: "Your resume is a very strong match for this role.",
        background: "#dcfce7",
        text: "#166534",
        border: "#86efac"
      };
    }

    if (score >= 65) {
      return {
        label: "Strong Match",
        description: "Your resume matches this role well.",
        background: "#dbeafe",
        text: "#1d4ed8",
        border: "#93c5fd"
      };
    }

    if (score >= 50) {
      return {
        label: "Moderate Match",
        description: "Your resume has a reasonable match but needs improvement.",
        background: "#fef3c7",
        text: "#92400e",
        border: "#fcd34d"
      };
    }

    if (score >= 35) {
      return {
        label: "Weak Match",
        description: "Several areas of your resume need improvement for this role.",
        background: "#ffedd5",
        text: "#9a3412",
        border: "#fdba74"
      };
    }

    return {
      label: "Low Match",
      description: "Your resume currently has limited alignment with this role.",
      background: "#fee2e2",
      text: "#991b1b",
      border: "#fca5a5"
    };
  };


  const getAtsStatus = (score) => {

    if (score >= 80) {
      return {
        label: "ATS Ready",
        description: "Your resume structure is well optimized.",
        background: "#dcfce7",
        text: "#166534",
        border: "#86efac"
      };
    }

    if (score >= 60) {
      return {
        label: "Mostly Ready",
        description: "Your resume is usable but has some structural improvements.",
        background: "#fef3c7",
        text: "#92400e",
        border: "#fcd34d"
      };
    }

    return {
      label: "Needs Improvement",
      description: "Your resume structure may cause ATS compatibility issues.",
      background: "#fee2e2",
      text: "#991b1b",
      border: "#fca5a5"
    };
  };


  const getScoreCircle = (score) => {

    const safeScore = Math.min(
      Math.max(Number(score) || 0, 0),
      100
    );

    return `conic-gradient(
      #2563eb ${safeScore * 3.6}deg,
      #e2e8f0 ${safeScore * 3.6}deg
    )`;
  };


  // =========================================================
  // AI Review Helpers
  // =========================================================

  const parseAIAnalysis = (analysis) => {

    if (!analysis) {
      return [];
    }

    const headingMap = {
      "STRENGTHS": {
        title: "Strengths",
        icon: "💪",
        type: "strengths"
      },
      "WEAKNESSES": {
        title: "Weaknesses",
        icon: "⚠️",
        type: "weaknesses"
      },
      "TOP IMPROVEMENTS": {
        title: "Top Improvements",
        icon: "🎯",
        type: "improvements"
      },
      "IMPORTANT MISSING SKILLS": {
        title: "Important Missing Skills",
        icon: "🛠️",
        type: "missing"
      },
      "BULLET IMPROVEMENTS": {
        title: "Bullet Improvements",
        icon: "✍️",
        type: "bullets"
      }
    };

    const sections = [];
    let currentSection = null;
    let insideBulletTable = false;
    let tableHeaderSkipped = false;

    const lines = String(analysis)
      .replace(/\r\n/g, "\n")
      .split("\n");

    lines.forEach((rawLine) => {

      let line = rawLine
        .replace(/<br\s*\/?>/gi, " ")
        .trim();

      if (!line) {
        return;
      }

      // Ignore Markdown code fences returned by the AI.
      if (/^```/.test(line)) {
        return;
      }

      const normalizedHeading = line
        .replace(/^#+\s*/, "")
        .replace(/^\*\*(.*?)\*\*$/, "$1")
        .replace(/^\*(.*?)\*$/, "$1")
        .replace(/:$/, "")
        .trim()
        .toUpperCase();

      if (headingMap[normalizedHeading]) {

        currentSection = {
          ...headingMap[normalizedHeading],
          items: []
        };

        sections.push(currentSection);

        insideBulletTable =
          normalizedHeading === "BULLET IMPROVEMENTS";

        tableHeaderSkipped = false;

        return;
      }

      if (!currentSection) {
        currentSection = {
          title: "AI Review",
          icon: "🤖",
          type: "general",
          items: []
        };

        sections.push(currentSection);
      }

      /*
       * Handle Markdown tables returned by the AI.
       *
       * Example:
       * | Current | Suggested |
       * |---|---|
       * | old bullet | improved bullet |
       */
      if (
        insideBulletTable &&
        line.startsWith("|") &&
        line.endsWith("|")
      ) {

        const cells = line
          .split("|")
          .slice(1, -1)
          .map((cell) =>
            cell
              .replace(/<br\s*\/?>/gi, " ")
              .replace(/\*\*/g, "")
              .trim()
          );

        if (
          cells.length >= 2 &&
          cells.every((cell) =>
            /^:?-{2,}:?$/.test(cell)
          )
        ) {
          return;
        }

        if (!tableHeaderSkipped) {
          const looksLikeHeader =
            cells.length >= 2 &&
            /current/i.test(cells[0]) &&
            /suggested|improved|recommendation/i.test(cells[1]);

          if (looksLikeHeader) {
            tableHeaderSkipped = true;
            return;
          }
        }

        if (cells.length >= 2) {

          currentSection.items.push({
            type: "table",
            current: cells[0],
            suggested: cells.slice(1).join(" | ")
          });

          return;
        }
      }

      let cleanLine = line
        .replace(/^\*\*(.*?)\*\*$/, "$1")
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .trim();

      const labelMatch = cleanLine.match(
        /^\*{0,2}(Current|Suggested|Improved|Recommendation)\s*:\*{0,2}$/i
      );

      const numberedMatch = cleanLine.match(
        /^\d+\.\s*(.*)$/
      );

      const bulletMatch = cleanLine.match(
        /^[-•*]\s+(.*)$/
      );

      if (labelMatch) {
        currentSection.items.push({
          type: "label",
          text: labelMatch[1]
        });
      } else if (numberedMatch) {
        currentSection.items.push({
          type: "number",
          text: numberedMatch[1].trim()
        });
      } else if (bulletMatch) {
        currentSection.items.push({
          type: "bullet",
          text: bulletMatch[1].trim()
        });
      } else {
        currentSection.items.push({
          type: "text",
          text: cleanLine
        });
      }

    });

    /*
     * Convert sequential Current / Suggested AI output into
     * side-by-side comparison cards.
     *
     * This supports AI responses such as:
     * Current:
     * - old bullet
     * Suggested:
     * - improved bullet
     *
     * even when the AI does not return a Markdown table.
     */
    sections.forEach((section) => {
      if (section.type !== "bullets") {
        return;
      }

      const convertedItems = [];
      let i = 0;

      while (i < section.items.length) {
        const item = section.items[i];

        if (
          item.type === "label" &&
          item.text.toLowerCase() === "current"
        ) {
          const currentItem = section.items[i + 1];

          let suggestedIndex = i + 2;

          while (
            suggestedIndex < section.items.length &&
            section.items[suggestedIndex].type === "label" &&
            section.items[suggestedIndex].text.toLowerCase() !== "suggested"
          ) {
            suggestedIndex++;
          }

          const suggestedLabel = section.items[suggestedIndex];

          if (
            currentItem &&
            currentItem.type !== "label" &&
            suggestedLabel &&
            suggestedLabel.type === "label" &&
            suggestedLabel.text.toLowerCase() === "suggested"
          ) {
            const suggestedItem = section.items[suggestedIndex + 1];

            if (suggestedItem && suggestedItem.type !== "label") {
              convertedItems.push({
                type: "table",
                current:
                  currentItem.text ||
                  currentItem.current ||
                  "",
                suggested:
                  suggestedItem.text ||
                  suggestedItem.suggested ||
                  ""
              });

              i = suggestedIndex + 2;
              continue;
            }
          }
        }

        /*
         * Keep already parsed Markdown-table rows unchanged.
         */
        convertedItems.push(item);
        i++;
      }

      section.items = convertedItems;
    });

    return sections;
  };


  const renderAIItemText = (text) => {

    const parts = String(text)
      .replace(/<br\s*\/?>/gi, " ")
      .split(/(\*\*.*?\*\*)/g);

    return parts.map((part, index) => {

      if (
        part.startsWith("**") &&
        part.endsWith("**")
      ) {
        return (
          <strong key={index}>
            {part.slice(2, -2)}
          </strong>
        );
      }

      return (
        <span key={index}>
          {part}
        </span>
      );

    });

  };


  // =========================================================
  // Analyze Resume
  // =========================================================

  const analyzeResume = async () => {

    if (!resume) {

      setError(
        "Please select a resume PDF."
      );

      return;
    }


    if (!jobDescription.trim()) {

      setError(
        "Please enter a job description."
      );

      return;
    }


    if (jobDescription.trim().length < 30) {

      setError(
        "Please enter a more complete job description."
      );

      return;
    }


    setLoading(true);

    setError("");

    setResult(null);


    try {

      const formData = new FormData();


      formData.append(
        "resume",
        resume
      );


      formData.append(
        "job_description",
        jobDescription
      );


      const response = await fetch(
        "http://127.0.0.1:5000/api/analyze",
        {
          method: "POST",
          body: formData
        }
      );


      let data;


      try {

        data = await response.json();

      } catch {

        throw new Error(
          "The server returned an invalid response."
        );

      }


      if (!response.ok) {

        throw new Error(
          data.error ||
          "Analysis failed."
        );

      }


      setResult(data);

    } catch (error) {

      console.error(
        "Analysis error:",
        error
      );


      setError(
        error.message ||
        "Something went wrong."
      );

    } finally {

      setLoading(false);

    }

  };


  // =========================================================
  // Render
  // =========================================================

  return (

    <div>

      {/* ================================================= */}
      {/* INPUT CARD */}
      {/* ================================================= */}

      <div className="input-card">

        <h2>
          Analyze Your Resume
        </h2>

        <p>
          Upload your resume and paste the job
          description to get an AI-powered analysis.
        </p>


        {/* Resume */}

        <div className="input-section">

          <h3>
            1. Upload Resume
          </h3>


          <input

            className="file-input"

            type="file"

            accept=".pdf"

            onChange={(event) => {

              const selectedFile =
                event.target.files[0];


              if (!selectedFile) {

                setResume(null);

                return;

              }


              if (
                selectedFile.type !==
                "application/pdf"
              ) {

                setResume(null);

                setError(
                  "Please select a PDF file."
                );

                return;

              }


              setResume(
                selectedFile
              );

              setError("");

            }}

          />


          {resume && (

            <p>

              📄 {resume.name}

            </p>

          )}

        </div>


        {/* Job Description */}

        <div className="input-section">

          <h3>
            2. Job Description
          </h3>


          <textarea

            placeholder={
              "Paste the job description here..."
            }

            value={jobDescription}

            onChange={(event) => {

              setJobDescription(
                event.target.value
              );

              setError("");

            }}

          />

        </div>


        {/* Analyze Button */}

        <button

          className="analyze-button"

          onClick={analyzeResume}

          disabled={loading}

        >

          {loading
            ? "Analyzing Resume..."
            : "Analyze Resume"}

        </button>


        {loading && (

          <div className="loading">

            🤖 AI is analyzing your resume...

            <br />

            This may take a few seconds.

          </div>

        )}


        {error && (

          <div className="error">

            ❌ {error}

          </div>

        )}

      </div>


      {/* ================================================= */}
      {/* RESULTS */}
      {/* ================================================= */}

      {result && (

        <div className="results">

          <h2 className="results-title">

            Analysis Results

          </h2>

          {/* ================================================= */}
          {/* CANDIDATE */}
          {/* ================================================= */}

          <div className="card dashboard-candidate">

            <h2>
              Candidate
            </h2>

            <p>

              <strong>
                Name:
              </strong>

              {" "}

              {result.resume.name ||
                "Name not detected"}

            </p>

            <p>

              <strong>
                Resume:
              </strong>

              {" "}

              {result.resume.filename}

            </p>

            <p>

              <strong>
                Target Job:
              </strong>

              {" "}

              {result.job.title ||
                "Job title not detected"}

            </p>

          </div>
          
          {/* ================================================= */}
          {/* PROFESSIONAL SCORE DASHBOARD */}
          {/* ================================================= */}

          <div className="score-grid">


            {/* Overall Match */}

            <div className="card score-card">

              <h2>
                Overall Match
              </h2>


              <div
                style={{
                  width: "150px",
                  height: "150px",
                  borderRadius: "50%",
                  background: getScoreCircle(
                    result.overall_match
                  ),
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "18px auto"
                }}
              >

                <div
                  style={{
                    width: "122px",
                    height: "122px",
                    borderRadius: "50%",
                    background: "white",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                >

                  <div
                    style={{
                      fontSize: "32px",
                      fontWeight: "800",
                      color: "#2563eb",
                      lineHeight: "1"
                    }}
                  >

                    {result.overall_match}%

                  </div>

                </div>

              </div>


              <div
                style={{
                  display: "inline-block",
                  padding: "6px 13px",
                  borderRadius: "999px",
                  background:
                    getScoreStatus(
                      result.overall_match
                    ).background,
                  color:
                    getScoreStatus(
                      result.overall_match
                    ).text,
                  border:
                    `1px solid ${
                      getScoreStatus(
                        result.overall_match
                      ).border
                    }`,
                  fontWeight: "700",
                  fontSize: "13px"
                }}
              >

                {result.score_breakdown?.classification ||
                  getScoreStatus(
                    result.overall_match
                  ).label}

              </div>


              <p
                style={{
                  maxWidth: "340px",
                  margin: "12px auto 0",
                  fontSize: "13px"
                }}
              >

                {getScoreStatus(
                  result.overall_match
                ).description}

              </p>


              <div className="score-label">

                Resume ↔ Job Match

              </div>

            </div>


            {/* ATS Readiness */}

            <div className="card score-card">

              <h2>
                ATS Readiness
              </h2>


              <div
                style={{
                  width: "150px",
                  height: "150px",
                  borderRadius: "50%",
                  background: `conic-gradient(
                    #7c3aed ${
                      Math.min(
                        Math.max(
                          Number(result.ats.score) || 0,
                          0
                        ),
                        100
                      ) * 3.6
                    }deg,
                    #e2e8f0 ${
                      Math.min(
                        Math.max(
                          Number(result.ats.score) || 0,
                          0
                        ),
                        100
                      ) * 3.6
                    }deg
                  )`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "18px auto"
                }}
              >

                <div
                  style={{
                    width: "122px",
                    height: "122px",
                    borderRadius: "50%",
                    background: "white",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                >

                  <div
                    style={{
                      fontSize: "32px",
                      fontWeight: "800",
                      color: "#7c3aed",
                      lineHeight: "1"
                    }}
                  >

                    {result.ats.score}%

                  </div>

                </div>

              </div>


              <div
                style={{
                  display: "inline-block",
                  padding: "6px 13px",
                  borderRadius: "999px",
                  background:
                    getAtsStatus(
                      result.ats.score
                    ).background,
                  color:
                    getAtsStatus(
                      result.ats.score
                    ).text,
                  border:
                    `1px solid ${
                      getAtsStatus(
                        result.ats.score
                      ).border
                    }`,
                  fontWeight: "700",
                  fontSize: "13px"
                }}
              >

                {getAtsStatus(
                  result.ats.score
                ).label}

              </div>


              <p
                style={{
                  maxWidth: "340px",
                  margin: "12px auto 0",
                  fontSize: "13px"
                }}
              >

                {getAtsStatus(
                  result.ats.score
                ).description}

              </p>


              <div className="score-label">

                Resume Structure

              </div>

            </div>


          </div>


          {/* ================================================= */}
          {/* SCORE BREAKDOWN */}
          {/* ================================================= */}

          {result.score_breakdown && (

            <div className="card dashboard-breakdown">

              <h2>
                📊 Match Score Breakdown
              </h2>

              <p>
                Your overall match score combines required
                skills, preferred skills, and semantic relevance
                to the job description.
              </p>


              <div className="score-breakdown">


                {/* Required Skills */}

                <div className="score-breakdown-row">

                  <div className="score-breakdown-header">

                    <strong>
                      Required Skills
                    </strong>

                    <span>
                      {result.score_breakdown.required_skills}%
                      {" "}
                      ({result.score_breakdown.required_weight}% weight)
                    </span>

                  </div>


                  <div className="score-breakdown-bar">

                    <div
                      className="score-breakdown-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            result.score_breakdown.required_skills,
                            0
                          ),
                          100
                        )}%`,
                        background: "#2563eb"
                      }}
                    />

                  </div>

                </div>


                {/* Preferred Skills */}

                <div className="score-breakdown-row">

                  <div className="score-breakdown-header">

                    <strong>
                      Preferred Skills
                    </strong>

                    <span>
                      {result.score_breakdown.preferred_skills}%
                      {" "}
                      ({result.score_breakdown.preferred_weight}% weight)
                    </span>

                  </div>


                  <div className="score-breakdown-bar">

                    <div
                      className="score-breakdown-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            result.score_breakdown.preferred_skills,
                            0
                          ),
                          100
                        )}%`,
                        background: "#7c3aed"
                      }}
                    />

                  </div>

                </div>


                {/* Semantic Relevance */}

                <div className="score-breakdown-row">

                  <div className="score-breakdown-header">

                    <strong>
                      Semantic Relevance
                    </strong>

                    <span>
                      {result.score_breakdown.semantic_relevance}%
                      {" "}
                      ({result.score_breakdown.semantic_weight}% weight)
                    </span>

                  </div>


                  <div className="score-breakdown-bar">

                    <div
                      className="score-breakdown-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(
                            result.score_breakdown.semantic_relevance,
                            0
                          ),
                          100
                        )}%`,
                        background: "#059669"
                      }}
                    />

                  </div>

                </div>


                {/* Final Score */}

                <div className="score-breakdown-final">

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "15px"
                    }}
                  >

                    <strong>
                      Final Match Score
                    </strong>

                    <strong
                      style={{
                        fontSize: "20px",
                        color: "#2563eb"
                      }}
                    >
                      {result.score_breakdown.final_score}%
                    </strong>

                  </div>


                  <p
                    style={{
                      marginBottom: 0,
                      marginTop: "8px"
                    }}
                  >

                    Classification:
                    {" "}

                    <strong>
                      {result.score_breakdown.classification}
                    </strong>

                  </p>

                </div>

              </div>

            </div>

          )}


        


          {/* ================================================= */}
          {/* SKILL ANALYSIS */}
          {/* ================================================= */}

          <div className="card dashboard-skills">

            <h2>
              Skill Analysis
            </h2>

            <p>
              Required Skill Coverage:
              {""}
              <strong>
                {result.skill_coverage.required_coverage}%
              </strong>
            </p>

            <p>
              Preferred Skill Coverage:
              {" "}
              <strong>
                {result.skill_coverage.preferred_coverage}%
              </strong>
            </p>


            {/* ------------------------------------------------- */}
            {/* MATCHED REQUIRED SKILLS */}
            {/* ------------------------------------------------- */}

            <h3>
              Matched Required Skills
            </h3>

            <div className="skill-grid">

              {result.matched_required_skills.length === 0 ? (

                <p>
                  No required skills matched.
                </p>

              ) : (

                result.matched_required_skills.map(
                  (item, index) => (

                    <div
                      key={`${item.skill}-${index}`}
                      style={{
                        background: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        borderRadius: "12px",
                        padding: "12px 14px",
                        minWidth: "220px",
                        flex: "1 1 220px"
                      }}
                    >

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: "10px"
                        }}
                      >

                        <strong
                          style={{
                            color: "#166534"
                          }}
                        >
                          ✓ {item.skill}
                        </strong>

                        <span
                          style={{
                            fontSize: "11px",
                            fontWeight: "700",
                            padding: "4px 7px",
                            borderRadius: "999px",
                            background:
                              item.match_type === "exact"
                                ? "#dcfce7"
                                : "#dbeafe",
                            color:
                              item.match_type === "exact"
                                ? "#166534"
                                : "#1d4ed8"
                          }}
                        >
                          {item.match_type === "exact"
                            ? "Exact Match"
                            : "Semantic Match"}
                        </span>

                      </div>


                      {item.match_type === "semantic" && (
                        <p
                          style={{
                            margin: "8px 0 0",
                            fontSize: "12px"
                          }}
                        >
                          <strong>
                            Similarity:
                          </strong>
                          {" "}
                          {Math.round(
                            (Number(item.similarity) || 0) * 100
                          )}%
                        </p>
                      )}


                      {item.evidence && (
                        <p
                          style={{
                            margin: "7px 0 0",
                            fontSize: "12px",
                            color: "#64748b"
                          }}
                        >
                          <strong>
                            Evidence:
                          </strong>
                          {" "}
                          {item.evidence}
                        </p>
                      )}

                    </div>

                  )
                )

              )}

            </div>


            {/* ------------------------------------------------- */}
            {/* MISSING REQUIRED SKILLS */}
            {/* ------------------------------------------------- */}

            <h3>
              Missing Required Skills
            </h3>

            <div className="skill-grid">

              {result.missing_required_skills.length === 0 ? (

                <p>
                  🎉 No required skills are missing.
                </p>

              ) : (

                result.missing_required_skills.map(
                  (item, index) => (

                    <div
                      key={`${item.skill}-${index}`}
                      style={{
                        background: "#fff7f7",
                        border: "1px solid #fecaca",
                        borderRadius: "12px",
                        padding: "12px 14px",
                        minWidth: "220px",
                        flex: "1 1 220px"
                      }}
                    >

                      <strong
                        style={{
                          color: "#991b1b"
                        }}
                      >
                        ✗ {item.skill}
                      </strong>


                      {item.evidence && (
                        <p
                          style={{
                            margin: "8px 0 0",
                            fontSize: "12px",
                            color: "#64748b"
                          }}
                        >
                          <strong>
                            Closest Resume Evidence:
                          </strong>
                          {" "}
                          {item.evidence}
                        </p>
                      )}


                      {item.similarity !== undefined &&
                        Number(item.similarity) > 0 && (
                          <p
                            style={{
                              margin: "6px 0 0",
                              fontSize: "11px",
                              color: "#94a3b8"
                            }}
                          >
                            Semantic similarity:
                            {" "}
                            {Math.round(
                              (Number(item.similarity) || 0) * 100
                            )}%
                            {" "}
                            <span>
                              (below match threshold)
                            </span>
                          </p>
                        )}

                    </div>

                  )
                )

              )}

            </div>


            {/* ------------------------------------------------- */}
            {/* MISSING PREFERRED SKILLS */}
            {/* ------------------------------------------------- */}

            <h3>
              Missing Preferred Skills
            </h3>

            <div className="skill-grid">

              {result.missing_preferred_skills.length === 0 ? (

                <p>
                  ✓ No preferred skills are missing.
                </p>

              ) : (

                result.missing_preferred_skills.map(
                  (item, index) => (

                    <div
                      key={`${item.skill}-${index}`}
                      style={{
                        background: "#fff7f7",
                        border: "1px solid #fecaca",
                        borderRadius: "12px",
                        padding: "12px 14px",
                        minWidth: "220px",
                        flex: "1 1 220px"
                      }}
                    >

                      <strong
                        style={{
                          color: "#991b1b"
                        }}
                      >
                        ✗ {item.skill}
                      </strong>


                      {item.evidence && (
                        <p
                          style={{
                            margin: "8px 0 0",
                            fontSize: "12px",
                            color: "#64748b"
                          }}
                        >
                          <strong>
                            Closest Resume Evidence:
                          </strong>
                          {" "}
                          {item.evidence}
                        </p>
                      )}


                      {item.similarity !== undefined &&
                        Number(item.similarity) > 0 && (
                          <p
                            style={{
                              margin: "6px 0 0",
                              fontSize: "11px",
                              color: "#94a3b8"
                            }}
                          >
                            Semantic similarity:
                            {" "}
                            {Math.round(
                              (Number(item.similarity) || 0) * 100
                            )}%
                            {" "}
                            <span>
                              (below match threshold)
                            </span>
                          </p>
                        )}

                    </div>

                  )
                )

              )}

            </div>

          </div>


          {/* ================================================= */}
          {/* ATS CHECKS */}
          {/* ================================================= */}

          <div className="card dashboard-ats">

            <h2>
              ATS Checks
            </h2>


            <div className="check-grid">


              <div
                className={
                  result.ats.checks.contact.email
                    ? "check check-good"
                    : "check check-bad"
                }
              >

                <strong>
                  Email
                </strong>

                <p>

                  {result.ats.checks.contact.email
                    ? "✓ Found"
                    : "✗ Missing"}

                </p>

              </div>


              <div
                className={
                  result.ats.checks.contact.phone
                    ? "check check-good"
                    : "check check-bad"
                }
              >

                <strong>
                  Phone
                </strong>

                <p>

                  {result.ats.checks.contact.phone
                    ? "✓ Found"
                    : "✗ Missing"}

                </p>

              </div>


              <div className="check">

                <strong>
                  Resume Length
                </strong>

                <p>

                  {result.ats.checks.length.message}

                </p>

                <small>

                  {result.ats.checks.length.word_count}
                  {" "}
                  words

                </small>

              </div>


              <div className="check">

                <strong>
                  Bullet Points
                </strong>

                <p>

                  {result.ats.checks.bullets.message}

                </p>

                <small>

                  {result.ats.checks.bullets.bullet_count}
                  {" "}
                  bullets

                </small>

              </div>


              <div className="check">

                <strong>
                  Action Words
                </strong>

                <p>

                  {result.ats.checks.action_words.message}

                </p>

              </div>


            </div>


            <h3>
              Resume Sections
            </h3>


            <div className="skill-grid">

              {Object.entries(
                result.ats.checks.sections
              ).map(

                ([section, exists]) => (

                  <span

                    className={
                      exists
                        ? "skill skill-matched"
                        : "skill skill-missing"
                    }

                    key={section}

                  >

                    {exists
                      ? "✓"
                      : "✗"}

                    {" "}

                    {section}

                  </span>

                )

              )}

            </div>

          </div>


          {/* ================================================= */}
          {/* AI REVIEW */}
          {/* ================================================= */}

          <div className="card dashboard-ai">

            <h2>
              🤖 AI Resume Review
            </h2>

            {result.ai_analysis &&
            result.ai_analysis.success ? (

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                  marginTop: "10px"
                }}
              >

                {parseAIAnalysis(
                  result.ai_analysis.analysis
                ).map(
                  (section, sectionIndex) => (

                    <div
                      key={`${section.type}-${sectionIndex}`}
                      style={{
                        background: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        borderRadius: "12px",
                        padding: "14px 16px",
                        textAlign: "left"
                      }}
                    >

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "9px",
                          marginBottom: "8px"
                        }}
                      >

                        <span
                          style={{
                            fontSize: "20px"
                          }}
                        >
                          {section.icon}
                        </span>

                        <h3
                          style={{
                            margin: 0,
                            fontSize: "17px",
                            color: "#0f172a"
                          }}
                        >
                          {section.title}
                        </h3>

                      </div>


                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "9px"
                        }}
                      >

                        {section.items.map(
                          (item, itemIndex) => {

                            if (item.type === "table") {
                              return (
                                <div
                                  key={itemIndex}
                                  style={{
                                    display: "grid",
                                    gridTemplateColumns:
                                      "minmax(0, 1fr) minmax(0, 1fr)",
                                    gap: "12px",
                                    padding: "8px 0",
                                    borderBottom:
                                      itemIndex === section.items.length - 1
                                        ? "none"
                                        : "1px solid #e2e8f0"
                                  }}
                                >

                                  <div
                                    style={{
                                      background: "#ffffff",
                                      border: "1px solid #e2e8f0",
                                      borderRadius: "10px",
                                      padding: "12px",
                                      minWidth: 0
                                    }}
                                  >

                                    <div
                                      style={{
                                        fontSize: "11px",
                                        fontWeight: "700",
                                        color: "#64748b",
                                        textTransform: "uppercase",
                                        marginBottom: "7px",
                                        letterSpacing: "0.04em"
                                      }}
                                    >
                                      Current
                                    </div>

                                    <div
                                      style={{
                                        lineHeight: "1.55",
                                        color: "#475569"
                                      }}
                                    >
                                      {renderAIItemText(item.current)}
                                    </div>

                                  </div>


                                  <div
                                    style={{
                                      background: "#f0fdf4",
                                      border: "1px solid #bbf7d0",
                                      borderRadius: "10px",
                                      padding: "12px",
                                      minWidth: 0
                                    }}
                                  >

                                    <div
                                      style={{
                                        fontSize: "11px",
                                        fontWeight: "700",
                                        color: "#166534",
                                        textTransform: "uppercase",
                                        marginBottom: "7px",
                                        letterSpacing: "0.04em"
                                      }}
                                    >
                                      Suggested
                                    </div>

                                    <div
                                      style={{
                                        lineHeight: "1.55",
                                        color: "#166534"
                                      }}
                                    >
                                      {renderAIItemText(item.suggested)}
                                    </div>

                                  </div>

                                </div>
                              );
                            }

                            if (item.type === "label") {
                              return (
                                <div
                                  key={itemIndex}
                                  style={{
                                    marginTop: itemIndex === 0 ? "2px" : "10px",
                                    marginBottom: "2px",
                                    padding: "5px 0",
                                    fontSize: "12px",
                                    fontWeight: "800",
                                    color:
                                      item.text.toLowerCase() === "suggested" ||
                                      item.text.toLowerCase() === "improved"
                                        ? "#166534"
                                        : "#475569",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.06em"
                                  }}
                                >
                                  {item.text}
                                </div>
                              );
                            }

                            if (item.type === "number") {
                              return (
                                <div
                                  key={itemIndex}
                                  style={{
                                    display: "flex",
                                    gap: "8px",
                                    alignItems: "flex-start",
                                    lineHeight: "1.5",
                                    color: "#334155"
                                  }}
                                >

                                  <span
                                    style={{
                                      minWidth: "24px",
                                      fontWeight: "700",
                                      color: "#2563eb"
                                    }}
                                  >
                                    {itemIndex + 1}.
                                  </span>

                                  <span>
                                    {renderAIItemText(
                                      item.text
                                    )}
                                  </span>

                                </div>
                              );
                            }

                            if (item.type === "bullet") {
                              return (
                                <div
                                  key={itemIndex}
                                  style={{
                                    display: "flex",
                                    gap: "10px",
                                    alignItems: "flex-start",
                                    lineHeight: "1.6",
                                    color: "#334155"
                                  }}
                                >

                                  <span
                                    style={{
                                      minWidth: "10px",
                                      marginTop: "7px",
                                      width: "6px",
                                      height: "6px",
                                      borderRadius: "50%",
                                      background: "#64748b"
                                    }}
                                  />

                                  <span>
                                    {renderAIItemText(
                                      item.text
                                    )}
                                  </span>

                                </div>
                              );
                            }

                            return (
                              <p
                                key={itemIndex}
                                style={{
                                  margin: 0,
                                  lineHeight: "1.55",
                                  color: "#334155",
                                  fontSize: "13px"
                                }}
                              >
                                {renderAIItemText(
                                  item.text
                                )}
                              </p>
                            );

                          }
                        )}

                      </div>

                    </div>

                  )
                )}

              </div>

            ) : (

              <div
                style={{
                  marginTop: "16px",
                  padding: "16px",
                  borderRadius: "12px",
                  background: "#f8fafc",
                  border: "1px solid #e2e8f0"
                }}
              >

                <p style={{ margin: 0 }}>

                  AI analysis is currently unavailable.

                  {" "}

                  {result.ai_analysis &&
                    result.ai_analysis.error}

                </p>

              </div>

            )}

          </div>


          {/* ================================================= */}
          {/* RECOMMENDATIONS */}
          {/* ================================================= */}

          <div className="card dashboard-recommendations">

            <h2>
              💡 Improvement Recommendations
            </h2>


            <p>

              {result.recommendation_summary.total}

              {" "}

              improvement opportunities found.

            </p>


            {result.recommendations.length === 0 ? (

              <p>
                🎉 No major improvements detected.
              </p>

            ) : (

              result.recommendations.map(

                (recommendation, index) => (

                  <div

                    key={index}

                    className={
                      `recommendation priority-${recommendation.priority}`
                    }

                  >

                    <h3>

                      {recommendation.title}

                    </h3>


                    <p>

                      <strong>
                        Priority:
                      </strong>

                      {" "}

                      {recommendation.priority}

                    </p>


                    <p>

                      {recommendation.message}

                    </p>


                    {recommendation.skill && (

                      <p>

                        <strong>
                          Skill:
                        </strong>

                        {" "}

                        {recommendation.skill}

                      </p>

                    )}


                    {recommendation.requirement && (

                      <p>

                        <strong>
                          Requirement:
                        </strong>

                        {" "}

                        {recommendation.requirement}

                      </p>

                    )}


                    {recommendation.evidence && (

                      <p>

                        <strong>
                          Current Evidence:
                        </strong>

                        {" "}

                        {recommendation.evidence}

                      </p>

                    )}

                  </div>

                )

              )

            )}

          </div>


          {/* ================================================= */}
          {/* REQUIREMENT MATCHES */}
          {/* ================================================= */}

          <div className="card dashboard-requirements">

            <h2>
              Requirement-by-Requirement Analysis
            </h2>


            {result.matches.length === 0 ? (

              <p>
                No requirements were detected for semantic matching.
              </p>

            ) : (

              result.matches.map(

                (match, index) => (

                  <div

                    className="requirement"

                    key={index}

                  >

                    <p>

                      <strong>
                        Requirement
                      </strong>

                    </p>


                    <p>

                      {match.requirement}

                    </p>


                    <p>

                      <span className="match-score">

                        Semantic Match:
                        {" "}
                        {match.match_percentage}%

                      </span>

                    </p>


                    <p>

                      <strong>
                        Match Level:
                      </strong>

                      {" "}

                      {match.match_level}

                    </p>


                    <p>

                      <strong>
                        Resume Evidence:
                      </strong>

                    </p>


                    <p>

                      {match.evidence}

                    </p>

                  </div>

                )

              )

            )}

          </div>

        </div>

      )}

    </div>

  );

}


export default Analyzer;
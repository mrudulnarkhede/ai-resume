import { useState } from "react";

function JDInput() {

  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeJD = async () => {

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/analyze-jd",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            job_description: jobDescription
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      setResult(data);

    } catch (error) {

      setError(error.message);

    } finally {

      setLoading(false);

    }
  };


  return (
    <div>

      <h2>Job Description</h2>

      <textarea
        rows="15"
        cols="70"
        placeholder="Paste the job description here..."
        value={jobDescription}
        onChange={(event) =>
          setJobDescription(event.target.value)
        }
      />

      <br />
      <br />

      <button onClick={analyzeJD}>
        {loading ? "Analyzing..." : "Analyze Job Description"}
      </button>

      {error && (
        <p>{error}</p>
      )}

      {result && (
        <div>

          <h2>Job Analysis</h2>

          <h3>
            Job Title
          </h3>

          <p>{result.job_title}</p>


          <h3>
            Skills
          </h3>

          <ul>
            {result.required_skills.map((skill) => (
              <li key={skill}>
                {skill}
              </li>
            ))}
          </ul>


          <h3>
            Responsibilities
          </h3>

          <ul>
            {result.responsibilities.map((item, index) => (
              <li key={index}>
                {item}
              </li>
            ))}
          </ul>


          <h3>
            Qualifications
          </h3>

          <ul>
            {result.qualifications.map((item, index) => (
              <li key={index}>
                {item}
              </li>
            ))}
          </ul>

        </div>
      )}

    </div>
  );
}

export default JDInput;
import { useState } from "react";

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile);
    setText("");
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF resume.");
      return;
    }

    const formData = new FormData();

    formData.append("resume", file);

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/parse-resume",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      setText(data.text);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload Your Resume</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
      />

      <br />
      <br />

      <button onClick={handleUpload}>
        {loading ? "Processing..." : "Upload & Analyze"}
      </button>

      {error && <p>{error}</p>}

      {file && (
        <p>
          Selected file: {file.name}
        </p>
      )}

      {text && (
        <div>
          <h2>Extracted Resume Text</h2>

          <pre>{text}</pre>
        </div>
      )}
    </div>
  );
}

export default ResumeUpload;
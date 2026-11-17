import "../assets/css/Report.css";

const Report = ({ report }) => {
  const score = report?.score ?? "N/A";
  const correct_answer = report?.correct_answer ?? "N/A"; // 0 এলেও ঠিকঠাক 0 দেখাবে
  const feedback = report?.improvment_area || [];

  return (
    <div className="report-container">
      <h1 className="report-header">Interview Report</h1>
      <div className="report-cards">
        <div className="report-card">
          <h3>Overall Score</h3>
          <div className="card-value">{score}</div>
        </div>
        <div className="report-card">
          <h3>Correct Answer</h3>
          <div className="card-value">{correct_answer}</div>
        </div>
      </div>
      <div className="feedback-section">
        <h3>Detailed Feedback</h3>
        <ul className="feedback-list">
          {Array.isArray(feedback) && feedback.length > 0 ? (
            feedback.map((point, index) => <li key={index}>{point}</li>)
          ) : (
            <li>No specific feedback available.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Report;
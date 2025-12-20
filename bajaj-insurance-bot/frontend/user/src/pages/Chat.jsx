import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { nodeApi } from "../api/nodeClient"; // NEW

export default function Chat() {
  const [policies, setPolicies] = useState([]);
  const [selection, setSelection] = useState({
    insurance_type: "",
    policy_name: "",
    policy_year: "",
  });
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // NEW: feedback state
  const [feedback, setFeedback] = useState("");
  const [lastQA, setLastQA] = useState(null); // { question, answer }

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get("/admin/policies", {
          params: { published: true },
        });
        const data = res.data;
        setPolicies(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error("Failed to load policies", e);
        setPolicies([]);
      }
    };
    load();
  }, []);

  const handleAsk = async () => {
    if (loading) return;
    if (!selection.insurance_type || !selection.policy_name || !selection.policy_year) {
      alert("Please select insurance type, policy name, and year.");
      return;
    }
    if (!question.trim()) return;

    setLoading(true);

    const body = {
      insurance_type: selection.insurance_type,
      policy_name: selection.policy_name,
      policy_year: selection.policy_year,
      questions: [question],
    };

    try {
      const res = await api.post("/user/query", body);
      const answer = res.data.answers[0];

      setMessages((prev) => [
        ...prev,
        { role: "user", text: question },
        { role: "bot", text: answer },
      ]);
      setLastQA({ question, answer });       // NEW: remember last Q&A
      setFeedback("");                      // clear old feedback
      setQuestion("");
    } catch (e) {
      console.error("Query failed", e);
      alert("Query failed – check console for details.");
    } finally {
      setLoading(false);
    }
  };

  // NEW: send feedback to Node service
  const handleSendFeedback = async () => {
    if (!feedback.trim()) return;
    if (!lastQA) {
      alert("Ask a question first.");
      return;
    }
    try {
      await nodeApi.post("/node/feedback", {
        comment: feedback,
        rating: 5,
        question: lastQA.question,
        answer: lastQA.answer,
      });
      alert("Thanks for your feedback!");
      setFeedback("");
    } catch (e) {
      console.error("Feedback failed", e);
      alert("Failed to send feedback.");
    }
  };

  const types = [...new Set(policies.map((p) => p.insurance_type))];
  const policiesForType = policies.filter(
    (p) => p.insurance_type === selection.insurance_type
  );
  const yearsForPolicy = policiesForType.filter(
    (p) => p.policy_name === selection.policy_name
  );

  return (
    <div style={{ padding: "1rem", maxWidth: 800, margin: "0 auto" }}>
      <h2>Bajaj Insurance Assistant</h2>

      <div style={{ marginBottom: "1rem" }}>
        <select
          value={selection.insurance_type}
          onChange={(e) =>
            setSelection((s) => ({
              ...s,
              insurance_type: e.target.value,
              policy_name: "",
              policy_year: "",
            }))
          }
        >
          <option value="">Select Insurance Type</option>
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        <select
          value={selection.policy_name}
          onChange={(e) =>
            setSelection((s) => ({
              ...s,
              policy_name: e.target.value,
              policy_year: "",
            }))
          }
        >
          <option value="">Select Policy</option>
          {policiesForType.map((p) => (
            <option key={p.id} value={p.policy_name}>
              {p.policy_name}
            </option>
          ))}
        </select>

        <select
          value={selection.policy_year}
          onChange={(e) =>
            setSelection((s) => ({ ...s, policy_year: e.target.value }))
          }
        >
          <option value="">Select Year</option>
          {yearsForPolicy.map((p) => (
            <option key={p.id} value={p.policy_year}>
              {p.policy_year}
            </option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <textarea
          rows={3}
          style={{ width: "100%" }}
          placeholder="Ask about coverage, waiting period, exclusions..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleAsk} disabled={!question.trim() || loading}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </div>

      <div
        style={{
          border: "1px solid #ccc",
          padding: "0.5rem",
          minHeight: "150px",
        }}
      >
        {messages.map((m, idx) => (
          <div key={idx} style={{ marginBottom: "0.5rem" }}>
            <strong>{m.role === "user" ? "You" : "Bot"}:</strong> {m.text}
          </div>
        ))}
      </div>

      {/* NEW: feedback box under chat */}
      <div style={{ marginTop: "1rem" }}>
        <h3>Feedback</h3>
        <textarea
          rows={2}
          style={{ width: "100%" }}
          placeholder="Was this answer helpful? Any suggestions?"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        <button
          type="button"
          onClick={handleSendFeedback}
          disabled={!feedback.trim()}
        >
          Send feedback
        </button>
      </div>
    </div>
  );
}

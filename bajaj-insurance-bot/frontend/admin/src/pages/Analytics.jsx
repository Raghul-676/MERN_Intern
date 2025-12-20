import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Analytics() {
  const [topQuestions, setTopQuestions] = useState([]);
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    const load = async () => {
      const tq = await api.get("/admin/analytics/top-questions");
      setTopQuestions(tq.data || []);
      const rq = await api.get("/admin/analytics/recent");
      setRecent(rq.data || []);
    };
    load();
  }, []);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Analytics</h2>

      <h3>Top Questions</h3>
      <table border="1" cellPadding="4">
        <thead>
          <tr>
            <th>Question</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          {topQuestions.map((q, i) => (
            <tr key={i}>
              <td>{q.question}</td>
              <td>{q.count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Recent Queries</h3>
      <table border="1" cellPadding="4">
        <thead>
          <tr>
            <th>Time</th>
            <th>Policy</th>
            <th>Question</th>
            <th>Answer</th>
          </tr>
        </thead>
        <tbody>
          {recent.map((r, i) => (
            <tr key={i}>
              <td>{new Date(r.created_at).toLocaleString()}</td>
              <td>{r.policy_name} ({r.policy_year})</td>
              <td>{r.question}</td>
              <td>{r.answer}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

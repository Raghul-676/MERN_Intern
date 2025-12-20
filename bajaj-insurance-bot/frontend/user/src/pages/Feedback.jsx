import React, { useState } from "react";
import { nodeApi } from "../api/nodeClient";

export default function Feedback() {
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);

  async function sendFeedback(data) {
    await nodeApi.post("/node/feedback", data);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    await sendFeedback({ comment, rating, question: "", answer: "" });
    setComment("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Your feedback"
      />
      <button type="submit">Send</button>
    </form>
  );
}

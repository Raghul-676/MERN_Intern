const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// connect to SAME MongoDB URL you use in FastAPI
mongoose.connect("mongodb://localhost:27017/bajaj_insurance");

const feedbackSchema = new mongoose.Schema({
  question: String,
  answer: String,
  comment: String,
  rating: Number,
  created_at: { type: Date, default: Date.now },
});

const Feedback = mongoose.model("Feedback", feedbackSchema);

// POST /node/feedback
app.post("/node/feedback", async (req, res) => {
  try {
    const fb = new Feedback(req.body);
    await fb.save();
    res.status(201).json(fb);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: "Failed to save feedback" });
  }
});

// GET /node/feedback
app.get("/node/feedback", async (req, res) => {
  try {
    const items = await Feedback.find().sort({ created_at: -1 }).limit(50);
    res.json(items);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: "Failed to load feedback" });
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Node service running on port ${PORT}`);
});

import os
import asyncio
from typing import List

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("GROQ_API_KEY from env:", GROQ_API_KEY[:5] if GROQ_API_KEY else None)


system_prompt = (
    "You are an AI assistant that helps users understand the coverage, benefits, "
    "exclusions, and conditions of their health insurance policy, using only the "
    "provided policy document context.\n\n"
    "Users will ask natural language questions about specific treatments, benefits, "
    "waiting periods, or policy terms.\n\n"
    "Respond with the shortest accurate answer possible, strictly based on the "
    "document. Do not rely on external knowledge or make assumptions.\n\n"
    "If coverage depends on conditions such as time limits or eligibility, state "
    "them briefly. If a term is defined, summarize the definition clearly.\n\n"
    "Your response must:\n"
    "- Be in fluent, formal English\n"
    "- Fit within a single sentence on one line\n"
    "- Be concise, direct, and policy-specific\n"
    "- Avoid lists, bullet points, or extra formatting\n"
    "- Never repeat the user's question or include disclaimers\n"
    "- Only say 'not mentioned' if there is truly no relevant info in the context"
)


async def query_groq(question: str, context: str, model: str = "llama-3.3-70b-versatile") -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }

    await asyncio.sleep(1.5)

    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code}\n{response.text}")

    answer = response.json()["choices"][0]["message"]["content"].strip()

    # enforce single sentence
    if "." in answer:
        answer = answer.split(".")[0].strip() + "."
    return answer


def build_context_from_chunks(results: List[dict]) -> str:
    return "\n\n".join([doc["content"] for doc in results])

from typing import List
from datetime import datetime
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db
from app.services.vector_store import (
    get_sentence_model,
    embed_chunks_and_build_faiss_index,
    retrieve_top_k_faiss,
)
from app.services.qa_engine import query_groq, build_context_from_chunks

router = APIRouter(prefix="/user", tags=["user"])


class UserQuery(BaseModel):
    insurance_type: str
    policy_name: str
    policy_year: str
    questions: List[str]


class UserQueryResponse(BaseModel):
    answers: List[str]


@router.post("/query", response_model=UserQueryResponse)
async def query_policy(payload: UserQuery, db=Depends(get_db)):
    policy = db.policies.find_one(
        {
            "insurance_type": payload.insurance_type,
            "policy_name": payload.policy_name,
            "policy_year": payload.policy_year,
            "published": True,
        }
    )
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found or unpublished")

    chunks = policy.get("chunks")
    if not chunks:
        raise HTTPException(status_code=500, detail="Policy chunks missing")

    model = get_sentence_model()
    _, index = embed_chunks_and_build_faiss_index(chunks, model)

    answers: List[str] = []

    for question in payload.questions:
        while True:
            try:
                top_chunks = retrieve_top_k_faiss(
                    question, chunks, index, model, top_k=5
                )
                context = build_context_from_chunks(top_chunks)
                answer = await query_groq(question, context)
                answers.append(answer.strip())
                break
            except Exception as e:
                msg = str(e)
                if "rate_limit_exceeded" in msg:
                    await asyncio.sleep(3)
                else:
                    raise HTTPException(
                        status_code=500, detail=f"Groq error: {msg}"
                    )

    # ---- Logging block: log each question/answer pair ----
    logs = []
    for q, a in zip(payload.questions, answers):
        logs.append(
            {
                "policy_id": str(policy["_id"]),
                "insurance_type": policy["insurance_type"],
                "policy_name": policy["policy_name"],
                "policy_year": policy["policy_year"],
                "question": q,
                "answer": a,
                "similarity": None,  # later: store FAISS similarity
                "created_at": datetime.utcnow(),
            }
        )

    if logs:
        db.queries.insert_many(logs)
    # ------------------------------------------------------

    return UserQueryResponse(answers=answers)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
import asyncio
import re

from sentence_transformers import SentenceTransformer

from app.services.pdf_processor import download_pdf_from_url, extract_text_chunks_with_metadata
from app.services.vector_store import embed_chunks_and_build_faiss_index, retrieve_top_k_faiss
from app.services.qa_engine import query_groq, build_context_from_chunks

router = APIRouter(tags=["bajaj-model"])


class RAGRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]


class RAGResponse(BaseModel):
    answers: List[str]


@router.post("/bajaj-model", response_model=RAGResponse)
async def bajaj_model_endpoint(request_data: RAGRequest):
    try:
        # 1) Download PDF
        pdf_file = download_pdf_from_url(str(request_data.documents))

        # 2) Build chunks and FAISS index (for now per request)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        chunks = extract_text_chunks_with_metadata(str(request_data.documents), pdf_file)
        _, index = embed_chunks_and_build_faiss_index(chunks, model)

        plain_answers: List[str] = []

        for question in request_data.questions:
            while True:
                try:
                    top_chunks = retrieve_top_k_faiss(question, chunks, index, model, top_k=5)
                    context = build_context_from_chunks(top_chunks)

                    answer = await query_groq(question, context)
                    clean_answer = answer.strip()
                    plain_answers.append(clean_answer)
                    break

                except Exception as e:
                    error_message = str(e)
                    if "rate_limit_exceeded" in error_message:
                        match = re.search(r"try again in ([0-9.]+)s", error_message)
                        if match:
                            delay = float(match.group(1)) + 0.5
                            await asyncio.sleep(delay)
                        else:
                            await asyncio.sleep(3)
                    else:
                        raise HTTPException(status_code=500, detail=f"Groq API error: {error_message}")

        return RAGResponse(answers=plain_answers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

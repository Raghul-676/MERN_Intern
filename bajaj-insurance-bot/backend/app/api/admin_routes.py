# backend/app/api/admin_routes.py
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from app.api.auth_routes import get_current_admin, CurrentUser

from app.api.deps import get_db
from app.services.pdf_processor import (
    download_pdf_from_url,
    extract_text_chunks_with_metadata,
)
from app.services.vector_store import (
    get_sentence_model,
    embed_chunks_and_build_faiss_index,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class PolicyCreate(BaseModel):
    insurance_type: str  # "Health", "Motor", "Travel"
    policy_name: str
    policy_year: str
    document_url: HttpUrl
    publish: bool = False


class PolicyOut(BaseModel):
    id: str
    insurance_type: str
    policy_name: str
    policy_year: str
    document_url: HttpUrl
    published: bool


@router.post("/policies", response_model=PolicyOut)
def create_policy(payload: PolicyCreate, db=Depends(get_db)):
    existing = db.policies.find_one(
        {
            "insurance_type": payload.insurance_type,
            "policy_name": payload.policy_name,
            "policy_year": payload.policy_year,
        }
    )
    if existing:
        raise HTTPException(status_code=400, detail="Policy version already exists")

    pdf_file = download_pdf_from_url(str(payload.document_url))
    chunks = extract_text_chunks_with_metadata(str(payload.document_url), pdf_file)

    model = get_sentence_model()
    embeddings, index = embed_chunks_and_build_faiss_index(chunks, model)

    now = datetime.utcnow()
    doc = {
        "insurance_type": payload.insurance_type,
        "policy_name": payload.policy_name,
        "policy_year": payload.policy_year,
        "document_url": str(payload.document_url),
        "published": payload.publish,
        "chunks": chunks,
        "created_at": now,
        "updated_at": now,
    }
    result = db.policies.insert_one(doc)

    return PolicyOut(
        id=str(result.inserted_id),
        insurance_type=payload.insurance_type,
        policy_name=payload.policy_name,
        policy_year=payload.policy_year,
        document_url=payload.document_url,
        published=payload.publish,
    )


class PublishUpdate(BaseModel):
    published: bool


@router.patch("/policies/{policy_id}", response_model=PolicyOut)
def update_publish_status(policy_id: str, body: PublishUpdate, db=Depends(get_db)):
    res = db.policies.find_one_and_update(
        {"_id": policy_id},
        {"$set": {"published": body.published, "updated_at": datetime.utcnow()}},
        return_document=True,
    )
    if not res:
        raise HTTPException(status_code=404, detail="Policy not found")

    return PolicyOut(
        id=str(res["_id"]),
        insurance_type=res["insurance_type"],
        policy_name=res["policy_name"],
        policy_year=res["policy_year"],
        document_url=res["document_url"],
        published=res["published"],
    )


@router.get("/policies", response_model=List[PolicyOut])
def list_policies(published: bool | None = None, db=Depends(get_db)):
    query = {}
    if published is not None:
        query["published"] = published
    docs = list(db.policies.find(query))
    return [
        PolicyOut(
            id=str(d["_id"]),
            insurance_type=d["insurance_type"],
            policy_name=d["policy_name"],
            policy_year=d["policy_year"],
            document_url=d["document_url"],
            published=d["published"],
        )
        for d in docs
    ]


# --------- Analytics endpoints (top questions & recent queries) ---------


@router.get("/analytics/top-questions")
def top_questions(limit: int = 10, db=Depends(get_db)) -> List[Dict]:
    pipeline = [
        {"$group": {"_id": "$question", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    results = list(db.queries.aggregate(pipeline))
    return [{"question": r["_id"], "count": r["count"]} for r in results]


@router.get("/analytics/recent")
def recent_queries(limit: int = 20, db=Depends(get_db)) -> List[Dict]:
    docs = list(db.queries.find().sort("created_at", -1).limit(limit))
    return [
        {
            "question": d.get("question"),
            "answer": d.get("answer"),
            "policy_name": d.get("policy_name"),
            "policy_year": d.get("policy_year"),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]


@router.post("/policies", response_model=PolicyOut)
def create_policy(
    payload: PolicyCreate,
    db=Depends(get_db),
    current_admin: CurrentUser = Depends(get_current_admin),  # NEW
):
    ...

from fastapi import APIRouter, Depends
from app.auth import verify_token

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/analyze-lead")
def analyze_lead(payload: dict, user=Depends(verify_token)):
    return {
        "user": user["uid"],
        "classification": "lead",
        "score": 0.87,
        "breadcrumbs": ["entry", "analysis", "scoring"]
    }

from modules.rag.engine import rag_query

@router.post("/rag-query")
def rag(payload: dict, user=Depends(verify_token)):
    answer = rag_query(payload["query"])
    return {
        "uid": user["uid"],
        "answer": answer,
        "confidence": 0.82
    }

@router.post("/rag-query")
def rag(payload: dict, user=Depends(verify_token)):
    session_id = payload.get("session_id", user["uid"])
    answer = rag_query(payload["query"], session_id)

    return {
        "uid": user["uid"],
        "session": session_id,
        "answer": answer
    }

@router.post("/lead")
def create_lead(payload: dict):
    lead = {
        "name": payload.get("name"),
        "email": payload.get("email"),
        "phone": payload.get("phone"),
        "source": "icarus-preventa"
    }

    from services.firestore import db
    db.collection("leads").add(lead)

    return {"status": "ok"}

@router.post("/send-survey")
def send_survey(payload: dict, user=Depends(verify_token)):
    from services.firestore import db
    from datetime import datetime
    db.collection("surveys").add({
        "session_id": payload.get("session_id", user["uid"]),
        "uid": user["uid"],
        "channel": "whatsapp",
        "metric": payload.get("metric", "diagnostico"),
        "status": "sent",
        "ts": datetime.utcnow()
    })
    # Aquí puedes llamar a n8n vía HTTP para disparar Twilio
    return {"status": "queued"}

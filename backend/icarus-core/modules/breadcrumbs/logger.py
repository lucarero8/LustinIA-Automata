from services.firestore import db
from datetime import datetime

def log_breadcrumb(session_id, module, step, payload):
    db.collection("breadcrumbs").add({
        "session_id": session_id,
        "module": module,
        "step": step,
        "payload": payload,
        "ts": datetime.utcnow()
    })

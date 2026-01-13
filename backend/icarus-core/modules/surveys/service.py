from services.firestore import db
from datetime import datetime

def save_survey(session_id, uid, channel, metric, answer, status="received"):
    db.collection("surveys").add({
        "session_id": session_id,
        "uid": uid,
        "channel": channel,
        "metric": metric,
        "answer": answer,
        "status": status,
        "ts": datetime.utcnow()
    })

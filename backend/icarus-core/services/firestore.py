# En backend/icarus-core/services/firestore.py
from google.cloud import firestore

# Asegúrate de que 'db' esté inicializado en alguna parte de este archivo
# db = firestore.Client() 

def save_conversation_state(customer_id: str, state: str, tactic_used: str):
    """Guarda el estado actual de la conversación para un usuario específico."""
    doc_ref = db.collection('conversations').document(customer_id)
    doc_ref.set({
        'state': state,
        'last_tactic': tactic_used,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

def get_conversation_state(customer_id: str):
    """Recupera el último estado conocido del usuario."""
    doc_ref = db.collection('conversations').document(customer_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        # Estado inicial si es la primera vez que interactúa
        return {'state': 'INITIAL', 'last_tactic': 'none'}


from services.embeddings import fake_embedding
from modules.breadcrumbs.logger import log_breadcrumb

KNOWLEDGE = [
    {"id": 1, "text": "Icarus es un sistema cognitivo modular"},
    {"id": 2, "text": "Lustin-IA integra CRM, ERP y RAG"},
]

def rag_query(query: str, session_id="anon"):
    log_breadcrumb(
        session_id=session_id,
        module="rag",
        step="query_received",
        payload={"query": query}
    )

    q_emb = fake_embedding(query)

    scored = []
    for doc in KNOWLEDGE:
        d_emb = fake_embedding(doc["text"])
        score = sum(a*b for a,b in zip(q_emb, d_emb))
        scored.append((score, doc["text"]))

    scored.sort(reverse=True)
    answer = scored[0][1]

    log_breadcrumb(
        session_id=session_id,
        module="rag",
        step="answer_generated",
        payload={"answer": answer}
    )

    return answer

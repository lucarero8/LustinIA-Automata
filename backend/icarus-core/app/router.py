from fastapi import APIRouter, Depends, HTTPException
from app.modules.rag.engine import RAGEngine
from app.services.firestore import get_customer_data
from app.modules.guardrails.abcd import ABCDGuardrail
from app.modules.breadcrumbs.logger import BreadcrumbLogger

router = APIRouter()

# Instanciamos componentes core
rag_engine = RAGEngine()
guardrail = ABCDGuardrail()
logger = BreadcrumbLogger()

@router.post("/v1/negotiate")
async def handle_negotiation(customer_id: str, user_message: str):
    # 1. BREADCRUMBS: Trazabilidad de la fase de la conversación
    logger.log_interaction(customer_id, user_message)

    # 2. DATA RETRIEVAL: ¿A quién le cobramos? (Desde firestore.py)
    customer_info = await get_customer_data(customer_id)
    if not customer_info:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 3. RAG: Recuperar técnica de negociación según el contexto
    # Aquí es donde el sistema lee tus "extractos de libros" o "técnicas propias"
    negotiation_tactic = rag_engine.search_tactic(
        query=user_message, 
        context="cobranza_temprana" if customer_info['days_overdue'] < 30 else "recuperacion_critica"
    )

    # 4. VERBAL REASONING ENGINE (Inner Thoughts)
    # No le pasamos el mensaje directo, le pedimos que "piense" primero
    reasoning_prompt = f"""
    CONTEXTO CLIENTE: {customer_info['status']} - Deuda: {customer_info['balance']}
    TÉCNICA RECOMENDADA: {negotiation_tactic}
    MENSAJE DEL CLIENTE: "{user_message}"
    
    TAREA: Analiza la objeción, aplica la técnica y define el ANCHOR POINT de esta respuesta.
    """
    
    # 5. GENERACIÓN DE RESPUESTA CON COGNITIVE GUARDRAILS (ABCD)
    # El motor de razonamiento procesa y el guardrail valida que no sea agresivo
    final_response = await rag_engine.generate_safe_response(
        prompt=reasoning_prompt,
        rules=guardrail.get_rules() # Protege contra insultos o promesas falsas
    )

    return {
        "status": "success",
        "customer": customer_id,
        "response": final_response,
        "tactic_used": negotiation_tactic,
        "next_step": "esperar_promesa_pago"
    }
# En backend/icarus-core/app/router.py

# ... (importaciones anteriores) ...
from app.services.firestore import get_conversation_state, save_conversation_state # Importamos las nuevas funciones

@router.post("/v1/negotiate")
async def handle_negotiation(customer_id: str, user_message: str):
    # 1. Recuperar el estado anterior
    conversation_data = get_conversation_state(customer_id)
    current_state = conversation_data['state']

    # 2. DECIDIR EL ANCHOR POINT Y EL SCRIPT BASADO EN EL ESTADO
    if current_state == 'INITIAL':
        # Usar el Script de Bienvenida
        script_prompt = "BIENVENIDO A LUSTIG-IA ANALISTA. [SCRIPT INICIAL COMPLETO DEL PROMPT]"
        next_state = 'INTERMEDIATE' # Mover al siguiente estado
        tactic = 'bienvenida_menu'

    elif current_state == 'INTERMEDIATE':
        # Usar el Script con Escasez y Precios
        script_prompt = "Quedan 17 licencias. [SCRIPT INTERMEDIO CON PRECIOS Y ESCASEZ]"
        next_state = 'FINAL' # Mover al siguiente estado
        tactic = 'escasez_anchor_point'

    elif current_state == 'FINAL':
        # Usar el Script de Cierre/Demo
        script_prompt = "Excelente decisión la demo. [SCRIPT FINAL CTA CIERRE]"
        next_state = 'CLOSED'
        tactic = 'cierre_demo'
        
    # 3. RAG/Razonamiento usar script_prompt como contexto
    # ... (Lógica de RAG y generación de respuesta aquí) ...
    final_response = "Respuesta generada usando el prompt basado en estado"

    # 4. GUARDAR el nuevo estado para la próxima interacción
    save_conversation_state(customer_id, next_state, tactic)

    return {
        # ... (respuesta) ...
        "current_state": current_state,
        "next_state": next_state
    }

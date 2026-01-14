# 🚀 ICARUSIAV2 - Advanced Sales AI System

Sistema de IA de ventas con capacidades cognitivas avanzadas, integración empresarial y API lista para producción.

## Estructura

```
ICARUSIAV2/
├── backend/      # FastAPI + módulos cognitivos/ventas/enterprise
├── config/       # Configuración (settings)
├── docs/         # Documentación
├── frontend/     # (placeholder) UI/Dashboard
└── tests/
```

## Arranque rápido

```bash
cd ICARUSIAV2/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

# 🚀 ICARUSIAV2 - Advanced Sales AI System

Sistema de IA de ventas de próxima generación con capacidades cognitivas avanzadas, integración empresarial y optimización máxima.

## 🏗️ Arquitectura

```
ICARUSIAV2/
├── backend/
│   ├── core/              # Núcleo cognitivo
│   ├── sales/             # Agente de ventas
│   └── enterprise/        # Integraciones empresariales
├── frontend/              # Dashboard y UI
├── config/               # Configuraciones
├── tests/                # Tests unitarios e integración
└── docs/                 # Documentación
```

## 🧠 Módulos Principales

### 🚀 En Desarrollo (Core)
- **Anchor Points**: Sistema de objetivos y metas contextuales
- **Verbal Reasoning Engine**: Motor de razonamiento verbal avanzado
- **Self-Refinement Loop**: Auto-mejora continua
- **Cognitive Guardrails (ABCD)**: Límites cognitivos y legales
- **Parallel Decoding**: Decodificación paralela para velocidad
- **Robust Coreference**: Resolución de referencias semánticas
- **Thread Rot Prevention**: Prevención de degradación de contexto
- **Active Classification**: Clasificación activa de leads e intenciones

### 📚 Knowledge System
- **Inner Thoughts Processing**: Procesamiento de pensamientos internos
- **Breadcrumbs Navigation**: Navegación por rastros de decisiones
- **Knowledge Graph Integration**: Integración con grafos de conocimiento
- **Memory Management System**: Sistema de gestión de memoria
- **Manual Refresh System**: Sistema de actualización manual controlada

### 📞 Sales Agent (IcarusIA)
- **Voice Synthesis (TTS)**: Síntesis de voz
- **Speech Recognition (STT)**: Reconocimiento de voz
- **Twilio Webhook Handler**: Manejo de webhooks de Twilio
- **WhatsApp Business API**: Integración con WhatsApp Business
- **Sales Script Engine**: Motor de scripts de ventas
- **Objection Handling AI**: IA para manejo de objeciones

### 🏢 Enterprise
- **CRM / ERP Integration**: Integración con sistemas CRM/ERP
- **WAIS Tests Framework**: Framework de tests WAIS
- **Multi-Agent Orchestration**: Orquestación multi-agente
- **Real-time Analytics Dashboard**: Dashboard de analytics en tiempo real
- **Feedback Learning Loop**: Loop de aprendizaje por feedback

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Configurar variables de entorno
cp config/.env.example config/.env

# Ejecutar servidor
cd backend
uvicorn main:app --reload
```

## 📦 Tecnologías

- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: OpenAI GPT-4, LangChain, Vector DBs
- **Voice**: Google Cloud TTS/STT, Twilio
- **Database**: Firestore, PostgreSQL
- **Frontend**: React, TypeScript
- **Deployment**: Docker, Cloud Run

## 🔧 Configuración

Ver `config/.env.example` para variables de entorno requeridas.

## 📖 Documentación

Ver `docs/` para documentación detallada de cada módulo.

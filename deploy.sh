#!/bin/bash
set -e

PROJECT_ID="lustinia"        # Tu Project ID real
REGION="us-central1"         # Región recomendada para México (puedes cambiar a southamerica-east1 si prefieres)

echo "🚀 Iniciando despliegue para proyecto $PROJECT_ID en región $REGION..."

# 1️⃣ Reglas de Firestore
echo "📂 Deploying Firestore rules..."
firebase deploy --only firestore:rules --project $PROJECT_ID

# 2️⃣ Índices de Firestore
echo "📂 Deploying Firestore indexes..."
firebase deploy --only firestore:indexes --project $PROJECT_ID

# 3️⃣ Hosting (frontend)
echo "🌐 Deploying Firebase Hosting..."
firebase deploy --only hosting --project $PROJECT_ID

# 4️⃣ Backend en Cloud Run
echo "⚙️ Building and deploying backend to Cloud Run..."
cd backend/icarus-core
gcloud builds submit --tag gcr.io/$PROJECT_ID/icarus-core
gcloud run deploy icarus-core \
  --image gcr.io/$PROJECT_ID/icarus-core \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID
cd ../../

echo "✅ Despliegue completo!"

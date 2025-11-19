#!/bin/bash

# Script pour exécuter les tests IAMService
# Usage: ./run_tests.sh

echo "================================================"
echo "🧪 Exécution des Tests IAMService"
echo "================================================"
echo ""

# Vérifier que pytest est installé
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest n'est pas installé"
    echo "Installation..."
    pip install pytest pytest-asyncio
fi

# Définir les variables d'environnement
export MONGO_URL=${MONGO_URL:-"mongodb://localhost:27017/"}

echo "📋 Configuration:"
echo "   MONGO_URL: $MONGO_URL"
echo ""

# Exécuter les tests
echo "🚀 Lancement des tests..."
echo ""

cd /app/auth-microservice

pytest tests/test_iam_service.py -v -s --tb=short

TEST_EXIT_CODE=$?

echo ""
echo "================================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ TOUS LES TESTS SONT PASSÉS"
else
    echo "❌ CERTAINS TESTS ONT ÉCHOUÉ"
fi

echo "================================================"

exit $TEST_EXIT_CODE

#!/bin/bash

# Script de déploiement Docker pour JLC
set -e

echo "🚀 Début du déploiement JLC..."

# Vérification des prérequis
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi

# Vérification du fichier .env
if [ ! -f ".env.prod" ]; then
    echo "❌ Fichier .env.prod manquant"
    echo "Copiez .env.prod.example vers .env.prod et configurez les variables"
    exit 1
fi

# Arrêt des conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Nettoyage des images obsolètes
echo "🧹 Nettoyage des images obsolètes..."
docker system prune -f

# Construction des images
echo "🔨 Construction des images..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache

# Démarrage des services
echo "▶️ Démarrage des services..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Attente que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 30

# Vérification de l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps

# Test de santé des services
echo "🏥 Test de santé des services..."

# Test API
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ API: OK"
else
    echo "❌ API: Échec"
fi

# Test Auth
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Auth: OK"
else
    echo "❌ Auth: Échec"
fi

# Test Frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: Échec"
fi

echo "🎉 Déploiement terminé!"
echo "📊 Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🔧 Gestion: docker-compose -f docker-compose.prod.yml [up|down|restart]"

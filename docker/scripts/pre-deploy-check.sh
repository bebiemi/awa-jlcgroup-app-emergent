#!/bin/bash

# Script de vérification pré-déploiement
set -e

echo "🔍 Vérification pré-déploiement JLC..."

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Vérification des prérequis système
echo "📋 Vérification des prérequis..."

# Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    check_result 0 "Docker installé (version: $DOCKER_VERSION)"
else
    check_result 1 "Docker non installé"
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    check_result 0 "Docker Compose installé (version: $COMPOSE_VERSION)"
else
    check_result 1 "Docker Compose non installé"
fi

# 2. Vérification des fichiers de configuration
echo "📁 Vérification des fichiers..."

# Fichier .env.prod
if [ -f ".env.prod" ]; then
    check_result 0 "Fichier .env.prod présent"
    
    # Vérification des variables critiques
    source .env.prod
    
    if [ -z "$MONGO_ROOT_PASSWORD" ]; then
        check_result 1 "MONGO_ROOT_PASSWORD non défini"
    else
        check_result 0 "MONGO_ROOT_PASSWORD défini"
    fi
    
    if [ -z "$JWT_SECRET" ]; then
        check_result 1 "JWT_SECRET non défini"
    else
        if [ ${#JWT_SECRET} -lt 32 ]; then
            warning "JWT_SECRET devrait faire au moins 32 caractères"
        fi
        check_result 0 "JWT_SECRET défini"
    fi
    
    if [ -z "$GOOGLE_CLIENT_ID" ]; then
        warning "GOOGLE_CLIENT_ID non défini (OAuth Google désactivé)"
    else
        check_result 0 "GOOGLE_CLIENT_ID défini"
    fi
    
else
    check_result 1 "Fichier .env.prod manquant"
fi

# Certificats SSL
if [ -d "nginx/ssl" ] && [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    check_result 0 "Certificats SSL présents"
    
    # Vérification de la validité du certificat
    if openssl x509 -in nginx/ssl/cert.pem -noout -checkend 86400 > /dev/null 2>&1; then
        check_result 0 "Certificat SSL valide"
    else
        warning "Certificat SSL expire dans moins de 24h"
    fi
else
    warning "Certificats SSL manquants (HTTPS désactivé)"
fi

# 3. Vérification de la configuration Docker
echo "🐳 Vérification de la configuration Docker..."

# Validation du docker-compose.yml
if docker-compose -f docker-compose.prod.yml --env-file .env.prod config > /dev/null 2>&1; then
    check_result 0 "Configuration Docker Compose valide"
else
    check_result 1 "Configuration Docker Compose invalide"
fi

# 4. Vérification des ressources système
echo "💻 Vérification des ressources système..."

# Espace disque
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    check_result 0 "Espace disque suffisant ($DISK_USAGE% utilisé)"
else
    warning "Espace disque faible ($DISK_USAGE% utilisé)"
fi

# Mémoire disponible
MEMORY_MB=$(free -m | awk 'NR==2{printf "%.0f", $7}')
if [ $MEMORY_MB -gt 1000 ]; then
    check_result 0 "Mémoire disponible suffisante (${MEMORY_MB}MB)"
else
    warning "Mémoire disponible faible (${MEMORY_MB}MB)"
fi

# 5. Vérification des ports
echo "🔌 Vérification des ports..."

PORTS=(80 443 8000 8001 27017)
for port in "${PORTS[@]}"; do
    if netstat -tuln | grep ":$port " > /dev/null 2>&1; then
        warning "Port $port déjà utilisé"
    else
        check_result 0 "Port $port disponible"
    fi
done

# 6. Test de connectivité réseau
echo "🌐 Test de connectivité..."

# Test de résolution DNS
if nslookup google.com > /dev/null 2>&1; then
    check_result 0 "Résolution DNS fonctionnelle"
else
    check_result 1 "Problème de résolution DNS"
fi

# Test de connectivité Internet
if curl -s --connect-timeout 5 https://google.com > /dev/null; then
    check_result 0 "Connectivité Internet OK"
else
    warning "Problème de connectivité Internet"
fi

# 7. Vérification des Dockerfiles
echo "📄 Vérification des Dockerfiles..."

DOCKERFILES=(
    "../apps/api/Dockerfile.prod"
    "../apps/web/Dockerfile.prod"
    "../auth-microservice/Dockerfile.prod"
)

for dockerfile in "${DOCKERFILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        check_result 0 "$(basename $dockerfile) présent"
    else
        check_result 1 "$(basename $dockerfile) manquant"
    fi
done

# 8. Vérification des dépendances
echo "📦 Vérification des dépendances..."

# Requirements Python
if [ -f "../apps/api/requirements.txt" ]; then
    check_result 0 "requirements.txt API présent"
else
    check_result 1 "requirements.txt API manquant"
fi

if [ -f "../auth-microservice/requirements.txt" ]; then
    check_result 0 "requirements.txt Auth présent"
else
    check_result 1 "requirements.txt Auth manquant"
fi

# Package.json Frontend
if [ -f "../apps/web/package.json" ]; then
    check_result 0 "package.json Frontend présent"
else
    check_result 1 "package.json Frontend manquant"
fi

# 9. Recommandations de sécurité
echo "🔒 Vérifications de sécurité..."

# Vérification des mots de passe par défaut
if grep -q "your-super-secret" .env.prod 2>/dev/null; then
    warning "Mots de passe par défaut détectés dans .env.prod"
fi

if grep -q "change-in-production" .env.prod 2>/dev/null; then
    warning "Valeurs de développement détectées dans .env.prod"
fi

# 10. Résumé final
echo ""
echo "📊 Résumé de la vérification:"
echo "================================"

if [ -f ".env.prod" ]; then
    source .env.prod
    echo "🌍 Environnement: ${ENVIRONMENT:-development}"
    echo "🔗 API URL: ${API_BASE_URL:-non défini}"
    echo "🔐 Auth URL: ${AUTH_SERVICE_URL:-non défini}"
    echo "📧 SMTP: ${SMTP_HOST:-non défini}"
fi

echo ""
echo "✅ Vérification pré-déploiement terminée avec succès!"
echo "🚀 Vous pouvez maintenant lancer le déploiement avec:"
echo "   ./scripts/deploy.sh"
echo ""
echo "📚 Pour plus d'informations, consultez:"
echo "   - DEPLOYMENT_GUIDE.md"
echo "   - DOCKER_COMMANDS.md"
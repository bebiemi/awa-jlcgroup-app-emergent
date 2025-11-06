#!/bin/bash

# Script de diagnostic pour vérifier la santé de l'application JLC
# Usage: ./check-health.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
     ___  __     _____   __   
    |__ | |   |   /    |__| |__|
    |   |____ |  /___  |  | |      
    
    JLC - Diagnostic de Santé
EOF
echo -e "${NC}"
echo ""

# Fonction pour tester un service
test_service() {
    local name=$1
    local url=$2
    local port=$3
    
    echo -n "  $name (port $port): "
    
    # Test de port
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo -e "${RED}❌ Port non utilisé${NC}"
        return 1
    fi
    
    # Test HTTP
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Port ouvert mais service ne répond pas${NC}"
        return 1
    fi
}

# Fonction pour tester MongoDB
test_mongodb() {
    echo -n "  MongoDB (port 27017): "
    
    if ! lsof -i :27017 > /dev/null 2>&1; then
        echo -e "${RED}❌ Non actif${NC}"
        return 1
    fi
    
    if command -v mongosh &> /dev/null; then
        if mongosh --quiet --eval "db.runCommand({ping: 1}).ok" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        fi
    elif command -v mongo &> /dev/null; then
        if mongo --quiet --eval "db.runCommand({ping: 1}).ok" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        fi
    fi
    
    echo -e "${YELLOW}⚠️  Actif mais ne répond pas${NC}"
    return 1
}

echo "🔍 Vérification des services..."
echo ""

# MongoDB
test_mongodb
MONGO_OK=$?

# Auth Service
test_service "Auth Service" "http://localhost:8000/health" 8000
AUTH_OK=$?

# Backend API
test_service "Backend API" "http://localhost:8001/health" 8001
BACKEND_OK=$?

# Frontend
test_service "Frontend" "http://localhost:3000" 3000
FRONTEND_OK=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier Supervisor
echo "📊 Statut Supervisor:"
echo ""
if command -v supervisorctl &> /dev/null; then
    sudo supervisorctl status
else
    echo -e "${YELLOW}⚠️  Supervisor non installé${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier les variables d'environnement
echo "🔧 Variables d'environnement:"
echo ""
if [ -f "/app/apps/web/.env" ]; then
    echo "  Frontend .env:"
    cat /app/apps/web/.env | sed 's/^/    /'
else
    echo -e "  ${RED}❌ Frontend .env manquant${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test de connexion complète
echo "🧪 Tests de connectivité:"
echo ""

# Test login
echo -n "  Test Login API: "
LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}' 2>&1)

if echo "$LOGIN_RESULT" | grep -q "access_token"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Échec${NC}"
    echo "    Réponse: $LOGIN_RESULT" | head -c 100
fi

echo ""

# Test base de données
echo -n "  Collections MongoDB: "
if [ $MONGO_OK -eq 0 ]; then
    COLLECTIONS=$(mongosh auth_db --quiet --eval "db.getCollectionNames().join(', ')" 2>/dev/null)
    if [ -n "$COLLECTIONS" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "    Collections: $COLLECTIONS"
    else
        echo -e "${YELLOW}⚠️  Base de données vide${NC}"
    fi
else
    echo -e "${RED}❌ MongoDB non accessible${NC}"
fi

echo ""

# Nombre d'utilisateurs
echo -n "  Utilisateurs dans la DB: "
if [ $MONGO_OK -eq 0 ]; then
    USER_COUNT=$(mongosh auth_db --quiet --eval "db.users.countDocuments()" 2>/dev/null)
    if [ -n "$USER_COUNT" ] && [ "$USER_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ $USER_COUNT utilisateur(s)${NC}"
    else
        echo -e "${YELLOW}⚠️  Aucun utilisateur${NC}"
        echo "    Créez un admin avec: ./create-admin.sh"
    fi
else
    echo -e "${RED}❌ Non vérifié${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Résumé
echo "📋 Résumé:"
echo ""

TOTAL=0
SUCCESS=0

if [ $MONGO_OK -eq 0 ]; then ((SUCCESS++)); fi
((TOTAL++))

if [ $AUTH_OK -eq 0 ]; then ((SUCCESS++)); fi
((TOTAL++))

if [ $BACKEND_OK -eq 0 ]; then ((SUCCESS++)); fi
((TOTAL++))

if [ $FRONTEND_OK -eq 0 ]; then ((SUCCESS++)); fi
((TOTAL++))

echo "  Services opérationnels: $SUCCESS/$TOTAL"
echo ""

if [ $SUCCESS -eq $TOTAL ]; then
    echo -e "${GREEN}✅ Tous les services fonctionnent correctement!${NC}"
    echo ""
    echo "  Accédez à l'application: http://localhost:3000"
    exit 0
else
    echo -e "${RED}❌ Certains services ont des problèmes${NC}"
    echo ""
    echo "  Actions suggérées:"
    
    if [ $MONGO_OK -ne 0 ]; then
        echo "    - Démarrer MongoDB: sudo systemctl start mongodb"
    fi
    
    if [ $AUTH_OK -ne 0 ] || [ $BACKEND_OK -ne 0 ] || [ $FRONTEND_OK -ne 0 ]; then
        echo "    - Redémarrer les services: sudo supervisorctl restart all"
        echo "    - Vérifier les logs: tail -f /var/log/supervisor/*.log"
    fi
    
    echo ""
    echo "  Pour plus d'aide, consultez: LOCAL_SETUP.md"
    exit 1
fi

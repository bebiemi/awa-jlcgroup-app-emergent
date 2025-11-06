#!/bin/bash

# Script pour résoudre les problèmes courants en développement local
# Usage: ./fix-local.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
     ___  __     _____   __   
    |__ | |   |   /    |__| |__|
    |   |____ |  /___  |  | |      
    
    JLC - Fix Local Issues
EOF
echo -e "${NC}"
echo ""

echo -e "${YELLOW}Ce script va:${NC}"
echo "  1. Vérifier les services"
echo "  2. Nettoyer les caches"
echo "  3. Redémarrer les services"
echo "  4. Tester la connectivité"
echo ""

read -p "Continuer? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Annulé"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Vérifier MongoDB
echo -e "${BLUE}1. Vérification MongoDB...${NC}"
if ! systemctl is-active --quiet mongodb; then
    echo -e "  ${YELLOW}MongoDB n'est pas actif, démarrage...${NC}"
    sudo systemctl start mongodb
    sleep 2
    if systemctl is-active --quiet mongodb; then
        echo -e "  ${GREEN}✓ MongoDB démarré${NC}"
    else
        echo -e "  ${RED}✗ Impossible de démarrer MongoDB${NC}"
        exit 1
    fi
else
    echo -e "  ${GREEN}✓ MongoDB actif${NC}"
fi

echo ""

# 2. Arrêter les services
echo -e "${BLUE}2. Arrêt des services...${NC}"
sudo supervisorctl stop all
echo -e "  ${GREEN}✓ Services arrêtés${NC}"

echo ""

# 3. Nettoyer les caches
echo -e "${BLUE}3. Nettoyage des caches...${NC}"

if [ -d "/app/apps/web/node_modules/.vite" ]; then
    rm -rf /app/apps/web/node_modules/.vite
    echo -e "  ${GREEN}✓ Cache Vite nettoyé${NC}"
fi

if [ -d "/app/apps/web/dist" ]; then
    rm -rf /app/apps/web/dist
    echo -e "  ${GREEN}✓ Dossier dist nettoyé${NC}"
fi

echo ""

# 4. Redémarrer les services
echo -e "${BLUE}4. Redémarrage des services...${NC}"
sudo supervisorctl start all
echo -e "  ${YELLOW}⏳ Attente du démarrage (15 secondes)...${NC}"
sleep 15

echo ""

# 5. Vérifier le statut
echo -e "${BLUE}5. Vérification du statut...${NC}"
sudo supervisorctl status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 6. Tests de connectivité
echo -e "${BLUE}6. Tests de connectivité...${NC}"

# Test MongoDB
echo -n "  MongoDB: "
if mongosh --quiet --eval "db.runCommand({ping: 1}).ok" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test Auth
echo -n "  Auth Service: "
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test Backend
echo -n "  Backend API: "
if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test Frontend
echo -n "  Frontend: "
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 7. Instructions finales
echo -e "${GREEN}✅ Services redémarrés!${NC}"
echo ""
echo -e "${YELLOW}Actions à faire dans votre navigateur:${NC}"
echo "  1. ${BLUE}Vider le cache:${NC} Ctrl + Shift + Delete"
echo "  2. ${BLUE}Tout supprimer:${NC} Images et fichiers en cache"
echo "  3. ${BLUE}Fermer tous les onglets${NC}"
echo "  4. ${BLUE}Rouvrir:${NC} http://localhost:3000"
echo "  5. ${BLUE}Hard reload:${NC} Ctrl + Shift + R"
echo ""
echo -e "${YELLOW}OU en navigation privée:${NC} Ctrl + Shift + N"
echo ""
echo -e "${BLUE}Pour un diagnostic complet:${NC} ./check-health.sh"
echo ""

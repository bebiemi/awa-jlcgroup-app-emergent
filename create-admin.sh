#!/bin/bash

# Script rapide pour créer un super admin
# Usage: ./create-admin.sh

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

JLC - Création Super Admin
EOF
echo -e "${NC}"

# Vérifier que nous sommes à la racine du projet
if [ ! -d "auth-microservice" ]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté depuis la racine du projet${NC}"
    echo -e "   Répertoire actuel: $(pwd)"
    exit 1
fi

echo -e "${GREEN}✓${NC} Répertoire correct"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 installé"

# Vérifier que MongoDB tourne
if ! pgrep -x mongod > /dev/null; then
    echo -e "${YELLOW}⚠${NC} MongoDB ne semble pas tourner"
    echo -e "   Démarrage de MongoDB..."
    
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mongodb
    elif [ -f "docker/docker-compose.yml" ]; then
        cd docker && docker-compose up -d mongodb && cd ..
    else
        echo -e "${RED}❌ Impossible de démarrer MongoDB${NC}"
        echo -e "   Veuillez démarrer MongoDB manuellement"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} MongoDB actif"
echo ""

# Aller dans le répertoire auth-microservice
cd auth-microservice

# Vérifier les dépendances Python
echo -e "${BLUE}Vérification des dépendances...${NC}"
if ! python3 -c "import motor, passlib" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Installation des dépendances manquantes..."
    pip3 install motor passlib python-dotenv bcrypt 2>/dev/null || {
        echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
        echo -e "   Essayez: pip3 install motor passlib python-dotenv bcrypt"
        exit 1
    }
fi

echo -e "${GREEN}✓${NC} Dépendances installées"
echo ""

# Exécuter le script Python
echo -e "${BLUE}Lancement du script de création...${NC}"
echo ""
python3 scripts/create_super_admin_fresh.py

echo ""
echo -e "${GREEN}✅ Terminé!${NC}"

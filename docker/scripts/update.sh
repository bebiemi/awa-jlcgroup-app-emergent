#!/bin/bash

# Script de mise à jour automatisée pour l'application JLC
set -e

# Configuration
BACKUP_DIR="./backups"
LOG_FILE="update.log"
ROLLBACK_ENABLED=true

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Fonction d'affichage avec couleurs
print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

# Fonction de nettoyage en cas d'erreur
cleanup_on_error() {
    print_error "Erreur détectée pendant la mise à jour"
    
    if [ "$ROLLBACK_ENABLED" = true ]; then
        print_step "Démarrage du rollback automatique..."
        
        # Arrêter les nouveaux conteneurs
        docker-compose -f docker-compose.prod.yml --env-file .env.prod down || true
        
        # Restaurer la version précédente
        if [ -n "$PREVIOUS_COMMIT" ]; then
            git checkout $PREVIOUS_COMMIT
            print_step "Code restauré à la version précédente"
        fi
        
        # Restaurer la base de données si une sauvegarde existe
        if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
            print_step "Restauration de la base de données..."
            ./scripts/restore.sh "$BACKUP_FILE"
        fi
        
        # Redémarrer avec l'ancienne version
        docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
        
        print_success "Rollback terminé"
    fi
    
    exit 1
}

# Trap pour gérer les erreurs
trap cleanup_on_error ERR

# Header
echo "🚀 Mise à jour de l'application JLC"
echo "===================================="
log "Starting update process"

# 1. Vérifications préliminaires
print_step "Vérifications préliminaires..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "Fichier docker-compose.prod.yml non trouvé. Êtes-vous dans le bon répertoire ?"
    exit 1
fi

# Vérifier que l'application fonctionne actuellement
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_error "L'application ne semble pas être en cours d'exécution"
    exit 1
fi

# Sauvegarder le commit actuel pour rollback
PREVIOUS_COMMIT=$(git rev-parse HEAD)
log "Current commit: $PREVIOUS_COMMIT"

print_success "Vérifications préliminaires terminées"

# 2. Sauvegarde préventive
print_step "Création d'une sauvegarde préventive..."

mkdir -p $BACKUP_DIR
BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/pre_update_backup_$BACKUP_TIMESTAMP.tar.gz"

# Sauvegarde de la base de données
if ./scripts/backup.sh; then
    # Renommer la dernière sauvegarde
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/jlc_backup_*.tar.gz | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        cp "$LATEST_BACKUP" "$BACKUP_FILE"
        print_success "Sauvegarde créée: $BACKUP_FILE"
    fi
else
    print_warning "Échec de la sauvegarde - continuer quand même ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
    ROLLBACK_ENABLED=false
fi

# 3. Récupération des mises à jour
print_step "Récupération des mises à jour du code..."

# Stash des modifications locales si nécessaire
if ! git diff-index --quiet HEAD --; then
    print_warning "Modifications locales détectées, sauvegarde temporaire..."
    git stash push -m "Auto-stash before update $(date)"
fi

# Récupération des dernières modifications
git fetch origin
CURRENT_BRANCH=$(git branch --show-current)
NEW_COMMITS=$(git rev-list HEAD..origin/$CURRENT_BRANCH --count)

if [ "$NEW_COMMITS" -eq 0 ]; then
    print_success "Aucune mise à jour disponible"
    exit 0
fi

print_step "Mise à jour du code ($NEW_COMMITS nouveaux commits)..."
git pull origin $CURRENT_BRANCH

print_success "Code mis à jour"

# 4. Vérification des changements
print_step "Analyse des changements..."

# Vérifier si les dépendances ont changé
DEPS_CHANGED=false

if git diff --name-only $PREVIOUS_COMMIT HEAD | grep -q "requirements.txt\|package.json\|yarn.lock"; then
    DEPS_CHANGED=true
    print_warning "Dépendances modifiées détectées"
fi

# Vérifier si les Dockerfiles ont changé
DOCKER_CHANGED=false
if git diff --name-only $PREVIOUS_COMMIT HEAD | grep -q "Dockerfile"; then
    DOCKER_CHANGED=true
    print_warning "Dockerfiles modifiés détectés"
fi

# 5. Tests de pré-déploiement
print_step "Exécution des tests de pré-déploiement..."

if [ -f "scripts/pre-deploy-check.sh" ]; then
    if ./scripts/pre-deploy-check.sh; then
        print_success "Tests de pré-déploiement réussis"
    else
        print_error "Échec des tests de pré-déploiement"
        exit 1
    fi
else
    print_warning "Script de pré-déploiement non trouvé"
fi

# 6. Mise à jour des services
print_step "Mise à jour des services Docker..."

# Stratégie de mise à jour basée sur les changements
if [ "$DOCKER_CHANGED" = true ] || [ "$DEPS_CHANGED" = true ]; then
    print_step "Reconstruction complète des images nécessaire..."
    
    # Arrêt progressif des services (frontend en premier)
    docker-compose -f docker-compose.prod.yml stop jlc-web
    docker-compose -f docker-compose.prod.yml stop jlc-api
    docker-compose -f docker-compose.prod.yml stop auth-microservice
    
    # Reconstruction des images
    docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache
    
    # Redémarrage des services
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
    
else
    print_step "Mise à jour sans reconstruction (code seulement)..."
    
    # Redémarrage en douceur
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --force-recreate
fi

# 7. Attente et vérification de la santé
print_step "Vérification de la santé des services..."

# Attendre que les services soient prêts
sleep 30

# Tests de santé
HEALTH_CHECKS_PASSED=0
TOTAL_HEALTH_CHECKS=3

# Test API
if curl -f -s http://localhost:8001/health > /dev/null; then
    print_success "API: Opérationnelle"
    HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
else
    print_error "API: Non opérationnelle"
fi

# Test Auth
if curl -f -s http://localhost:8000/health > /dev/null; then
    print_success "Auth: Opérationnelle"
    HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
else
    print_error "Auth: Non opérationnelle"
fi

# Test Frontend
if curl -f -s http://localhost:80 > /dev/null; then
    print_success "Frontend: Opérationnel"
    HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
else
    print_error "Frontend: Non opérationnel"
fi

# Vérification du taux de réussite
if [ $HEALTH_CHECKS_PASSED -eq $TOTAL_HEALTH_CHECKS ]; then
    print_success "Tous les services sont opérationnels"
elif [ $HEALTH_CHECKS_PASSED -gt 0 ]; then
    print_warning "$HEALTH_CHECKS_PASSED/$TOTAL_HEALTH_CHECKS services opérationnels"
    print_warning "Continuer malgré les échecs ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_error "Aucun service opérationnel - rollback nécessaire"
    exit 1
fi

# 8. Tests fonctionnels post-déploiement
print_step "Tests fonctionnels post-déploiement..."

# Test de base de l'API
API_TEST_RESULT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ "$API_TEST_RESULT" = "200" ]; then
    print_success "Test API: OK (HTTP $API_TEST_RESULT)"
else
    print_warning "Test API: Attention (HTTP $API_TEST_RESULT)"
fi

# Test de base de l'Auth
AUTH_TEST_RESULT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$AUTH_TEST_RESULT" = "200" ]; then
    print_success "Test Auth: OK (HTTP $AUTH_TEST_RESULT)"
else
    print_warning "Test Auth: Attention (HTTP $AUTH_TEST_RESULT)"
fi

# 9. Nettoyage
print_step "Nettoyage des ressources inutilisées..."

# Supprimer les anciennes images
docker image prune -f > /dev/null 2>&1

# Supprimer les conteneurs arrêtés
docker container prune -f > /dev/null 2>&1

print_success "Nettoyage terminé"

# 10. Résumé final
echo ""
echo "🎉 Mise à jour terminée avec succès !"
echo "====================================="
log "Update completed successfully"

echo ""
echo "📊 Résumé de la mise à jour:"
echo "• Commits appliqués: $NEW_COMMITS"
echo "• Services opérationnels: $HEALTH_CHECKS_PASSED/$TOTAL_HEALTH_CHECKS"
echo "• Sauvegarde disponible: $BACKUP_FILE"
echo "• Version précédente: $PREVIOUS_COMMIT"
echo ""

echo "🔍 Vérifications recommandées:"
echo "• Tester les fonctionnalités critiques"
echo "• Vérifier les logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "• Monitoring: ./scripts/monitor.sh"
echo ""

echo "🔄 En cas de problème:"
echo "• Rollback manuel: git checkout $PREVIOUS_COMMIT && ./scripts/deploy.sh"
echo "• Restauration DB: ./scripts/restore.sh $BACKUP_FILE"
echo ""

# Option pour lancer le monitoring automatiquement
echo "Lancer le monitoring maintenant ? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    ./scripts/monitor.sh
fi

log "Update process completed"
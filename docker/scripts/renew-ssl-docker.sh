#!/bin/bash

###############################################################################
# Script de Renouvellement SSL avec Certbot Containerisé
# Pour l'application JLC
###############################################################################

# Configuration
DOMAIN="votredomaine.com"  # MODIFIER AVEC VOTRE DOMAINE
APP_DIR="/opt/jlc-app"
LOG_FILE="/var/log/ssl-renewal-docker.log"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}" | tee -a "$LOG_FILE"
}

# Début du script
log "========================================="
log "Démarrage du renouvellement SSL (Docker)"
log "========================================="

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé"
    exit 1
fi

# Vérifier que docker compose est disponible
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose n'est pas disponible"
    exit 1
fi

# Aller dans le dossier docker
cd "$APP_DIR/docker" || {
    log_error "Impossible d'accéder à $APP_DIR/docker"
    exit 1
}

# Vérifier que les containers sont en cours d'exécution
if ! docker compose -f docker-compose.prod.yml ps | grep -q "nginx"; then
    log_error "Le container Nginx n'est pas en cours d'exécution"
    exit 1
fi

# Renouveler les certificats avec le container certbot
log "Tentative de renouvellement des certificats..."
if docker compose -f docker-compose.prod.yml run --rm certbot renew --quiet 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Renouvellement réussi ou non nécessaire"
else
    log_error "Échec du renouvellement"
    exit 1
fi

# Vérifier si de nouveaux certificats ont été générés
log "Vérification des certificats..."
docker compose -f docker-compose.prod.yml run --rm certbot certificates 2>&1 | tee -a "$LOG_FILE"

# Redémarrer Nginx pour recharger les certificats
log "Redémarrage du conteneur Nginx..."
if docker compose -f docker-compose.prod.yml restart nginx 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Nginx redémarré avec succès"
else
    log_error "Échec du redémarrage de Nginx"
    exit 1
fi

# Vérifier que Nginx est bien démarré
sleep 5
if docker ps | grep -q "jlc-nginx"; then
    log_success "Nginx fonctionne correctement"
else
    log_error "Nginx ne fonctionne pas correctement"
    exit 1
fi

# Test HTTPS
log "Test de la connexion HTTPS..."
if curl -sSf -o /dev/null "https://${DOMAIN}" 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Connexion HTTPS fonctionnelle"
else
    log_warning "Impossible de tester la connexion HTTPS"
fi

# Afficher les informations sur le certificat actuel
log "Informations sur le certificat actuel:"
echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | \
    openssl x509 -noout -dates 2>&1 | tee -a "$LOG_FILE"

# Calculer le nombre de jours avant expiration
EXPIRY_DATE=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

if [ -n "$EXPIRY_DATE" ]; then
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s 2>/dev/null)
    CURRENT_EPOCH=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        log_warning "Le certificat expire dans $DAYS_LEFT jours"
    else
        log_success "Le certificat expire dans $DAYS_LEFT jours"
    fi
fi

log "========================================="
log "Renouvellement SSL terminé avec succès"
log "========================================="

exit 0

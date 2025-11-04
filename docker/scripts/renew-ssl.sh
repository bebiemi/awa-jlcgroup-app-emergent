#!/bin/bash

###############################################################################
# Script de Renouvellement Automatique des Certificats SSL Let's Encrypt
# Pour l'application JLC
###############################################################################

# Configuration
DOMAIN="votredomaine.com"  # MODIFIER AVEC VOTRE DOMAINE
APP_DIR="/opt/jlc-app"
SSL_DIR="${APP_DIR}/docker/nginx/ssl"
LOG_FILE="/var/log/ssl-renewal.log"
LETSENCRYPT_DIR="/etc/letsencrypt/live/${DOMAIN}"

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
log "Démarrage du renouvellement SSL"
log "========================================="

# Vérifier que certbot est installé
if ! command -v certbot &> /dev/null; then
    log_error "Certbot n'est pas installé"
    exit 1
fi

# Vérifier que le dossier SSL existe
if [ ! -d "$SSL_DIR" ]; then
    log_error "Le dossier SSL n'existe pas: $SSL_DIR"
    exit 1
fi

# Vérifier les certificats existants
log "Vérification des certificats existants..."
certbot certificates 2>&1 | tee -a "$LOG_FILE"

# Tenter le renouvellement
log "Tentative de renouvellement des certificats..."
if certbot renew --quiet 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Renouvellement réussi ou non nécessaire"
else
    log_error "Échec du renouvellement"
    exit 1
fi

# Vérifier si de nouveaux certificats ont été générés
CERT_DATE=$(stat -c %Y "$LETSENCRYPT_DIR/fullchain.pem" 2>/dev/null || echo "0")
CURRENT_CERT_DATE=$(stat -c %Y "$SSL_DIR/cert.pem" 2>/dev/null || echo "0")

if [ "$CERT_DATE" -gt "$CURRENT_CERT_DATE" ]; then
    log "De nouveaux certificats ont été générés, copie en cours..."
    
    # Backup des anciens certificats
    if [ -f "$SSL_DIR/cert.pem" ]; then
        BACKUP_DIR="${SSL_DIR}/backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp "$SSL_DIR/cert.pem" "$BACKUP_DIR/" 2>/dev/null
        cp "$SSL_DIR/key.pem" "$BACKUP_DIR/" 2>/dev/null
        log "Backup des anciens certificats dans: $BACKUP_DIR"
    fi
    
    # Copier les nouveaux certificats
    if cp "$LETSENCRYPT_DIR/fullchain.pem" "$SSL_DIR/cert.pem" && \
       cp "$LETSENCRYPT_DIR/privkey.pem" "$SSL_DIR/key.pem"; then
        log_success "Nouveaux certificats copiés avec succès"
        
        # Corriger les permissions
        chmod 644 "$SSL_DIR/cert.pem"
        chmod 600 "$SSL_DIR/key.pem"
        log_success "Permissions des certificats corrigées"
        
        # Redémarrer Nginx dans Docker
        log "Redémarrage du conteneur Nginx..."
        cd "$APP_DIR/docker" || exit 1
        
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
        
    else
        log_error "Échec de la copie des certificats"
        exit 1
    fi
else
    log "Les certificats n'ont pas été renouvelés (pas encore nécessaire)"
fi

# Afficher les informations sur le certificat actuel
log "Informations sur le certificat actuel:"
echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | \
    openssl x509 -noout -dates 2>&1 | tee -a "$LOG_FILE"

# Calculer le nombre de jours avant expiration
EXPIRY_DATE=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

if [ -n "$EXPIRY_DATE" ]; then
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
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

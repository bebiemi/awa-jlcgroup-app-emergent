#!/bin/bash

###############################################################################
# Script d'Installation Automatique du Renouvellement SSL Let's Encrypt
# Pour l'application JLC
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   Installation Automatique du Renouvellement SSL             ║"
    echo "║   Let's Encrypt - Application JLC                            ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Vérifier si root
if [ "$EUID" -ne 0 ]; then 
    print_error "Ce script doit être exécuté en tant que root (sudo)"
    exit 1
fi

print_header

# Configuration interactive
print_info "Configuration du renouvellement SSL..."
echo ""

# Demander le domaine
read -p "Entrez votre nom de domaine principal (ex: example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    print_error "Le domaine ne peut pas être vide"
    exit 1
fi

# Demander le chemin de l'application
read -p "Chemin de l'application [/opt/jlc-app]: " APP_DIR
APP_DIR=${APP_DIR:-/opt/jlc-app}

# Demander l'email pour les notifications
read -p "Email pour les notifications (optionnel): " ADMIN_EMAIL

# Demander la fréquence
echo ""
print_info "Choisissez la fréquence de renouvellement:"
echo "1) Quotidien à 3h (Recommandé par Let's Encrypt)"
echo "2) Hebdomadaire (Dimanche à 3h)"
echo "3) Mensuel (1er du mois à 3h)"
read -p "Votre choix [1]: " FREQUENCY
FREQUENCY=${FREQUENCY:-1}

# Demander la méthode
echo ""
print_info "Choisissez la méthode d'automatisation:"
echo "1) Cron (Classique, compatible tous systèmes)"
echo "2) Systemd Timer (Moderne, recommandé pour Ubuntu/Debian)"
read -p "Votre choix [1]: " METHOD
METHOD=${METHOD:-1}

echo ""
print_info "Résumé de la configuration:"
echo "  - Domaine: $DOMAIN"
echo "  - Application: $APP_DIR"
echo "  - Email: ${ADMIN_EMAIL:-Non configuré}"
echo "  - Fréquence: $([ $FREQUENCY -eq 1 ] && echo 'Quotidien' || [ $FREQUENCY -eq 2 ] && echo 'Hebdomadaire' || echo 'Mensuel')"
echo "  - Méthode: $([ $METHOD -eq 1 ] && echo 'Cron' || echo 'Systemd Timer')"
echo ""
read -p "Continuer avec cette configuration? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    print_warning "Installation annulée"
    exit 0
fi

echo ""
print_info "Installation en cours..."

# 1. Vérifier que certbot est installé
print_info "Vérification de Certbot..."
if ! command -v certbot &> /dev/null; then
    print_warning "Certbot n'est pas installé. Installation..."
    apt update
    apt install -y certbot
    print_success "Certbot installé"
else
    print_success "Certbot déjà installé"
fi

# 2. Configurer le script de renouvellement
print_info "Configuration du script de renouvellement..."
SCRIPT_PATH="${APP_DIR}/docker/scripts/renew-ssl.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
    print_error "Le script renew-ssl.sh n'existe pas à: $SCRIPT_PATH"
    exit 1
fi

# Mettre à jour le domaine dans le script
sed -i "s|DOMAIN=\".*\"|DOMAIN=\"${DOMAIN}\"|g" "$SCRIPT_PATH"
sed -i "s|APP_DIR=\".*\"|APP_DIR=\"${APP_DIR}\"|g" "$SCRIPT_PATH"

# Ajouter l'email si fourni
if [ ! -z "$ADMIN_EMAIL" ]; then
    if ! grep -q "ADMIN_EMAIL=" "$SCRIPT_PATH"; then
        sed -i "/^DOMAIN=/a ADMIN_EMAIL=\"${ADMIN_EMAIL}\"" "$SCRIPT_PATH"
    else
        sed -i "s|ADMIN_EMAIL=\".*\"|ADMIN_EMAIL=\"${ADMIN_EMAIL}\"|g" "$SCRIPT_PATH"
    fi
fi

# Rendre le script exécutable
chmod +x "$SCRIPT_PATH"
print_success "Script configuré et rendu exécutable"

# 3. Tester le script
print_info "Test du script de renouvellement..."
if "$SCRIPT_PATH" > /tmp/ssl-test.log 2>&1; then
    print_success "Test du script réussi"
else
    print_warning "Le test a échoué. Consultez /tmp/ssl-test.log pour plus de détails"
fi

# 4. Configuration selon la méthode choisie
if [ $METHOD -eq 1 ]; then
    # Configuration Cron
    print_info "Configuration du Cron job..."
    
    # Déterminer la ligne cron selon la fréquence
    case $FREQUENCY in
        1)
            CRON_LINE="0 3 * * * $SCRIPT_PATH >> /var/log/ssl-renewal.log 2>&1"
            ;;
        2)
            CRON_LINE="0 3 * * 0 $SCRIPT_PATH >> /var/log/ssl-renewal.log 2>&1"
            ;;
        3)
            CRON_LINE="0 3 1 * * $SCRIPT_PATH >> /var/log/ssl-renewal.log 2>&1"
            ;;
    esac
    
    # Ajouter au crontab si pas déjà présent
    (crontab -l 2>/dev/null | grep -v "renew-ssl.sh"; echo "$CRON_LINE") | crontab -
    
    print_success "Cron job configuré"
    
    # Afficher la configuration
    echo ""
    print_info "Configuration Cron actuelle:"
    crontab -l | grep "renew-ssl.sh"
    
else
    # Configuration Systemd Timer
    print_info "Configuration du Systemd Timer..."
    
    # Créer le service
    cat > /etc/systemd/system/ssl-renewal.service << EOF
[Unit]
Description=Renouvellement SSL Let's Encrypt pour JLC
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=$SCRIPT_PATH
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Créer le timer
    case $FREQUENCY in
        1)
            ON_CALENDAR="daily"
            ;;
        2)
            ON_CALENDAR="weekly"
            ;;
        3)
            ON_CALENDAR="monthly"
            ;;
    esac
    
    cat > /etc/systemd/system/ssl-renewal.timer << EOF
[Unit]
Description=Timer pour le renouvellement SSL
Requires=ssl-renewal.service

[Timer]
OnCalendar=$ON_CALENDAR
OnCalendar=03:00
Persistent=true
RandomizedDelaySec=3600

[Install]
WantedBy=timers.target
EOF
    
    # Recharger systemd
    systemctl daemon-reload
    
    # Activer et démarrer le timer
    systemctl enable ssl-renewal.timer
    systemctl start ssl-renewal.timer
    
    print_success "Systemd Timer configuré et activé"
    
    # Afficher le statut
    echo ""
    print_info "Statut du timer:"
    systemctl status ssl-renewal.timer --no-pager
    echo ""
    print_info "Prochaine exécution:"
    systemctl list-timers ssl-renewal.timer --no-pager
fi

# 5. Créer un fichier de log si nécessaire
touch /var/log/ssl-renewal.log
chmod 644 /var/log/ssl-renewal.log

# 6. Créer un script de vérification rapide
print_info "Création du script de vérification..."
cat > "${APP_DIR}/docker/scripts/check-ssl.sh" << 'EOF'
#!/bin/bash

DOMAIN="DOMAIN_PLACEHOLDER"

echo "🔐 Statut SSL pour $DOMAIN"
echo "================================"

# Date d'expiration
EXPIRY=$(echo | openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN} 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
echo "📅 Expire le: $EXPIRY"

# Jours restants
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "⚠️  Jours restants: $DAYS_LEFT (Renouvellement urgent!)"
elif [ $DAYS_LEFT -lt 60 ]; then
    echo "🟡 Jours restants: $DAYS_LEFT (Renouvellement bientôt)"
else
    echo "✅ Jours restants: $DAYS_LEFT"
fi

echo ""
echo "📋 Derniers logs de renouvellement:"
tail -n 10 /var/log/ssl-renewal.log
EOF

sed -i "s|DOMAIN_PLACEHOLDER|$DOMAIN|g" "${APP_DIR}/docker/scripts/check-ssl.sh"
chmod +x "${APP_DIR}/docker/scripts/check-ssl.sh"
print_success "Script de vérification créé: check-ssl.sh"

# 7. Résumé final
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║            Installation Terminée avec Succès! ✓              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
print_info "📋 Résumé:"
echo "  ✓ Script de renouvellement configuré"
echo "  ✓ $([ $METHOD -eq 1 ] && echo 'Cron job' || echo 'Systemd timer') configuré"
echo "  ✓ Logs disponibles dans: /var/log/ssl-renewal.log"
echo "  ✓ Script de vérification créé"

echo ""
print_info "🔧 Commandes utiles:"
echo ""
echo "  # Vérifier le statut SSL"
echo "  ${APP_DIR}/docker/scripts/check-ssl.sh"
echo ""
echo "  # Tester le renouvellement manuellement"
echo "  sudo ${SCRIPT_PATH}"
echo ""
echo "  # Voir les logs"
echo "  tail -f /var/log/ssl-renewal.log"
echo ""

if [ $METHOD -eq 1 ]; then
    echo "  # Voir les tâches cron"
    echo "  sudo crontab -l"
else
    echo "  # Voir le statut du timer"
    echo "  sudo systemctl status ssl-renewal.timer"
    echo ""
    echo "  # Voir les logs systemd"
    echo "  sudo journalctl -u ssl-renewal.service -f"
fi

echo ""
print_info "📚 Documentation complète:"
echo "  ${APP_DIR}/docs/SSL_AUTO_RENEWAL_GUIDE.md"

echo ""
print_success "Le renouvellement automatique est maintenant configuré!"
print_info "Vos certificats SSL seront automatiquement renouvelés. 🎉"

exit 0

#!/bin/bash

# Script de monitoring pour l'application JLC
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
LOG_FILE="monitoring.log"

# Fonction d'affichage
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# Fonction de logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Header
clear
echo "🔍 JLC Application Monitoring Dashboard"
echo "========================================"
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. État des conteneurs
echo "📦 État des Conteneurs:"
echo "------------------------"

SERVICES=("jlc-mongodb-prod" "jlc-auth-prod" "jlc-api-prod" "jlc-web-prod" "jlc-nginx")

for service in "${SERVICES[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "^$service$"; then
        status=$(docker inspect --format='{{.State.Status}}' $service 2>/dev/null || echo "not found")
        if [ "$status" = "running" ]; then
            # Vérifier depuis combien de temps le conteneur tourne
            uptime=$(docker inspect --format='{{.State.StartedAt}}' $service | xargs -I {} date -d {} +%s)
            current_time=$(date +%s)
            uptime_seconds=$((current_time - uptime))
            uptime_hours=$((uptime_seconds / 3600))
            uptime_minutes=$(((uptime_seconds % 3600) / 60))
            
            print_status "OK" "$service: Running (${uptime_hours}h ${uptime_minutes}m)"
            log_message "$service: Running (${uptime_hours}h ${uptime_minutes}m)"
        else
            print_status "ERROR" "$service: $status"
            log_message "$service: $status"
        fi
    else
        print_status "ERROR" "$service: Not found"
        log_message "$service: Not found"
    fi
done

echo ""

# 2. Health Checks
echo "🏥 Health Checks:"
echo "------------------"

# API Health Check
if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
    response=$(curl -s http://localhost:8001/health)
    print_status "OK" "API Health Check: $response"
    log_message "API Health Check: OK"
else
    print_status "ERROR" "API Health Check: Failed"
    log_message "API Health Check: Failed"
fi

# Auth Health Check
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/health)
    print_status "OK" "Auth Health Check: $response"
    log_message "Auth Health Check: OK"
else
    print_status "ERROR" "Auth Health Check: Failed"
    log_message "Auth Health Check: Failed"
fi

# Frontend Check
if curl -f -s http://localhost:80 > /dev/null 2>&1; then
    print_status "OK" "Frontend: Accessible"
    log_message "Frontend: Accessible"
else
    print_status "ERROR" "Frontend: Not accessible"
    log_message "Frontend: Not accessible"
fi

# MongoDB Check
if docker exec jlc-mongodb-prod mongo --eval "db.adminCommand('ismaster')" > /dev/null 2>&1; then
    print_status "OK" "MongoDB: Connected"
    log_message "MongoDB: Connected"
else
    print_status "ERROR" "MongoDB: Connection failed"
    log_message "MongoDB: Connection failed"
fi

echo ""

# 3. Utilisation des ressources
echo "💻 Utilisation des Ressources:"
echo "-------------------------------"

# CPU et Mémoire par conteneur
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | while read line; do
    if [[ $line == *"jlc-"* ]]; then
        container=$(echo $line | awk '{print $1}')
        cpu=$(echo $line | awk '{print $2}' | sed 's/%//')
        mem_usage=$(echo $line | awk '{print $3}')
        mem_perc=$(echo $line | awk '{print $4}' | sed 's/%//')
        
        # Alertes basées sur l'utilisation
        if (( $(echo "$cpu > 80" | bc -l) )); then
            print_status "WARNING" "$container: CPU ${cpu}% (High)"
        elif (( $(echo "$cpu > 50" | bc -l) )); then
            print_status "WARNING" "$container: CPU ${cpu}% (Medium)"
        else
            print_status "OK" "$container: CPU ${cpu}%"
        fi
        
        if (( $(echo "$mem_perc > 80" | bc -l) )); then
            print_status "WARNING" "$container: Memory ${mem_usage} (${mem_perc}% - High)"
        else
            print_status "OK" "$container: Memory ${mem_usage} (${mem_perc}%)"
        fi
        
        log_message "$container: CPU ${cpu}%, Memory ${mem_perc}%"
    fi
done

echo ""

# 4. Espace disque
echo "💾 Espace Disque:"
echo "------------------"

# Espace disque général
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
disk_available=$(df -h / | awk 'NR==2 {print $4}')

if [ $disk_usage -gt 90 ]; then
    print_status "ERROR" "Espace disque: ${disk_usage}% utilisé (${disk_available} disponible)"
elif [ $disk_usage -gt 80 ]; then
    print_status "WARNING" "Espace disque: ${disk_usage}% utilisé (${disk_available} disponible)"
else
    print_status "OK" "Espace disque: ${disk_usage}% utilisé (${disk_available} disponible)"
fi

# Volumes Docker
echo ""
echo "📁 Volumes Docker:"
docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep docker_ | while read line; do
    volume_name=$(echo $line | awk '{print $1}')
    volume_size=$(docker system df -v | grep $volume_name | awk '{print $3}' || echo "N/A")
    print_status "INFO" "Volume $volume_name: $volume_size"
done

echo ""

# 5. Logs récents (erreurs)
echo "📋 Erreurs Récentes (dernières 10 minutes):"
echo "---------------------------------------------"

# Recherche d'erreurs dans les logs
error_count=0
since_time=$(date -d '10 minutes ago' '+%Y-%m-%dT%H:%M:%S')

for service in "${SERVICES[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "^$service$"; then
        errors=$(docker logs $service --since="$since_time" 2>&1 | grep -i "error\|exception\|failed\|critical" | wc -l)
        if [ $errors -gt 0 ]; then
            print_status "WARNING" "$service: $errors erreurs détectées"
            error_count=$((error_count + errors))
            
            # Afficher les 3 dernières erreurs
            echo "   Dernières erreurs:"
            docker logs $service --since="$since_time" 2>&1 | grep -i "error\|exception\|failed\|critical" | tail -3 | while read error_line; do
                echo "   └─ $error_line"
            done
        else
            print_status "OK" "$service: Aucune erreur récente"
        fi
    fi
done

if [ $error_count -eq 0 ]; then
    print_status "OK" "Aucune erreur détectée dans les 10 dernières minutes"
fi

log_message "Total errors in last 10 minutes: $error_count"

echo ""

# 6. Connectivité réseau
echo "🌐 Connectivité Réseau:"
echo "------------------------"

# Test de connectivité entre services
if docker exec jlc-api-prod ping -c 1 mongodb > /dev/null 2>&1; then
    print_status "OK" "API → MongoDB: Connected"
else
    print_status "ERROR" "API → MongoDB: Connection failed"
fi

if docker exec jlc-api-prod ping -c 1 auth-microservice > /dev/null 2>&1; then
    print_status "OK" "API → Auth: Connected"
else
    print_status "ERROR" "API → Auth: Connection failed"
fi

echo ""

# 7. Sauvegardes
echo "💾 État des Sauvegardes:"
echo "-------------------------"

if [ -d "backups" ]; then
    latest_backup=$(ls -t backups/*.tar.gz 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        backup_date=$(stat -c %y "$latest_backup" | cut -d' ' -f1)
        backup_size=$(du -h "$latest_backup" | cut -f1)
        
        # Vérifier si la sauvegarde est récente (moins de 24h)
        backup_timestamp=$(stat -c %Y "$latest_backup")
        current_timestamp=$(date +%s)
        hours_since_backup=$(( (current_timestamp - backup_timestamp) / 3600 ))
        
        if [ $hours_since_backup -lt 24 ]; then
            print_status "OK" "Dernière sauvegarde: $backup_date ($backup_size) - il y a ${hours_since_backup}h"
        else
            print_status "WARNING" "Dernière sauvegarde: $backup_date ($backup_size) - il y a ${hours_since_backup}h (ancienne)"
        fi
    else
        print_status "WARNING" "Aucune sauvegarde trouvée"
    fi
else
    print_status "WARNING" "Dossier de sauvegarde non trouvé"
fi

echo ""

# 8. Certificats SSL
echo "🔒 Certificats SSL:"
echo "--------------------"

if [ -f "nginx/ssl/cert.pem" ]; then
    # Vérifier la date d'expiration
    expiry_date=$(openssl x509 -in nginx/ssl/cert.pem -noout -enddate | cut -d= -f2)
    expiry_timestamp=$(date -d "$expiry_date" +%s)
    current_timestamp=$(date +%s)
    days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    if [ $days_until_expiry -lt 7 ]; then
        print_status "ERROR" "Certificat SSL expire dans $days_until_expiry jours"
    elif [ $days_until_expiry -lt 30 ]; then
        print_status "WARNING" "Certificat SSL expire dans $days_until_expiry jours"
    else
        print_status "OK" "Certificat SSL valide ($days_until_expiry jours restants)"
    fi
else
    print_status "INFO" "Certificats SSL non configurés"
fi

echo ""

# 9. Résumé et recommandations
echo "📊 Résumé:"
echo "----------"

# Calculer le score de santé global
total_checks=20
failed_checks=$(grep -c "ERROR" $LOG_FILE 2>/dev/null || echo 0)
warning_checks=$(grep -c "WARNING" $LOG_FILE 2>/dev/null || echo 0)

health_score=$(( (total_checks - failed_checks - warning_checks) * 100 / total_checks ))

if [ $health_score -ge 90 ]; then
    print_status "OK" "Score de santé global: ${health_score}% - Excellent"
elif [ $health_score -ge 70 ]; then
    print_status "WARNING" "Score de santé global: ${health_score}% - Bon"
else
    print_status "ERROR" "Score de santé global: ${health_score}% - Attention requise"
fi

echo ""
echo "📈 Actions recommandées:"
if [ $failed_checks -gt 0 ]; then
    echo "   • Résoudre les $failed_checks erreurs critiques"
fi
if [ $warning_checks -gt 0 ]; then
    echo "   • Examiner les $warning_checks avertissements"
fi
if [ $error_count -gt 10 ]; then
    echo "   • Analyser les logs pour les erreurs fréquentes"
fi

echo ""
echo "🔄 Prochaine vérification recommandée dans 15 minutes"
echo "📝 Log complet disponible dans: $LOG_FILE"
echo ""

# Option pour monitoring continu
if [ "$1" = "--continuous" ]; then
    echo "🔄 Mode monitoring continu activé (Ctrl+C pour arrêter)"
    while true; do
        sleep 900  # 15 minutes
        echo ""
        echo "🔄 Nouvelle vérification - $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=================================================="
        $0  # Relancer le script
    done
fi
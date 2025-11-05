#!/bin/bash

# Script de démarrage Docker pour JLC Application
# Usage: ./docker-start.sh [dev|prod]

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Vérifier que Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        echo "  Installation: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose n'est pas installé."
        echo "  Installation: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker et Docker Compose sont installés"
}

# Vérifier que Docker daemon tourne
check_docker_daemon() {
    if ! docker info &> /dev/null; then
        print_error "Le Docker daemon ne tourne pas. Veuillez le démarrer."
        exit 1
    fi
    print_success "Docker daemon actif"
}

# Fonction pour démarrer en mode développement
start_dev() {
    print_info "Démarrage de l'environnement de développement..."
    
    cd docker
    
    # Vérifier si des containers tournent déjà
    if docker-compose ps | grep -q "Up"; then
        print_warning "Des services sont déjà en cours d'exécution"
        read -p "Voulez-vous les redémarrer? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down
        else
            print_info "Utilisation des services existants"
            docker-compose ps
            show_urls
            exit 0
        fi
    fi
    
    # Démarrer les services
    print_info "Construction et démarrage des services..."
    docker-compose up -d --build
    
    # Attendre que les services soient prêts
    print_info "Attente du démarrage des services..."
    sleep 10
    
    # Vérifier le statut
    print_success "Services démarrés!"
    echo
    docker-compose ps
    echo
    
    show_urls
    
    print_info "Pour voir les logs: docker-compose logs -f"
    print_info "Pour arrêter: docker-compose down"
}

# Fonction pour démarrer en mode production
start_prod() {
    print_info "Démarrage de l'environnement de production..."
    
    cd docker
    
    # Vérifier que .env existe
    if [ ! -f .env ]; then
        print_error "Fichier .env manquant!"
        print_info "Création du fichier .env depuis .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Veuillez éditer le fichier docker/.env avec vos valeurs de production"
            print_info "Ensuite relancez: ./docker-start.sh prod"
            exit 1
        else
            print_error "Fichier .env.example manquant!"
            exit 1
        fi
    fi
    
    # Avertissement production
    print_warning "⚠️  ATTENTION: Démarrage en mode PRODUCTION"
    read -p "Êtes-vous sûr? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Annulé"
        exit 0
    fi
    
    # Démarrer les services
    print_info "Construction et démarrage des services de production..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Attendre que les services soient prêts
    print_info "Attente du démarrage des services..."
    sleep 15
    
    # Vérifier le statut
    print_success "Services de production démarrés!"
    echo
    docker-compose -f docker-compose.prod.yml ps
    echo
    
    print_success "Application disponible sur:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8001"
    echo "  - Auth: http://localhost:8000"
    echo "  - Nginx: http://localhost (si configuré)"
    
    print_info "Pour voir les logs: docker-compose -f docker-compose.prod.yml logs -f"
    print_info "Pour arrêter: docker-compose -f docker-compose.prod.yml down"
}

# Afficher les URLs des services
show_urls() {
    print_success "Services disponibles:"
    echo "  - 🌐 Frontend:      http://localhost:5173"
    echo "  - 🔌 API Backend:   http://localhost:8001"
    echo "  - 🔐 Auth Service:  http://localhost:8000"
    echo "  - 📧 Mailhog:       http://localhost:8025"
    echo "  - 🗄️  Mongo Express: http://localhost:8081 (admin/admin)"
    echo "  - 🍃 MongoDB:       mongodb://localhost:27017"
    echo "  - 🔴 Redis:         redis://localhost:6379"
}

# Afficher l'aide
show_help() {
    cat << EOF
Usage: ./docker-start.sh [COMMAND]

Commandes:
  dev     Démarrer l'environnement de développement (par défaut)
  prod    Démarrer l'environnement de production
  stop    Arrêter tous les services
  clean   Arrêter et nettoyer tous les volumes
  logs    Afficher les logs
  status  Afficher le statut des services
  help    Afficher cette aide

Exemples:
  ./docker-start.sh           # Démarre en mode dev
  ./docker-start.sh dev       # Démarre en mode dev
  ./docker-start.sh prod      # Démarre en mode prod
  ./docker-start.sh stop      # Arrête les services
  ./docker-start.sh logs      # Affiche les logs

Pour plus d'informations, consultez DOCKER_GUIDE.md
EOF
}

# Arrêter les services
stop_services() {
    print_info "Arrêt des services..."
    cd docker
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        print_success "Services de développement arrêtés"
    fi
    if docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml down
        print_success "Services de production arrêtés"
    fi
}

# Nettoyer
clean_services() {
    print_warning "⚠️  Cette action va supprimer tous les volumes (perte de données)"
    read -p "Êtes-vous sûr? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Annulé"
        exit 0
    fi
    
    print_info "Nettoyage..."
    cd docker
    docker-compose down -v
    docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
    print_success "Nettoyage terminé"
}

# Afficher les logs
show_logs() {
    cd docker
    if docker-compose ps | grep -q "Up"; then
        docker-compose logs -f
    else
        print_error "Aucun service en cours d'exécution"
        exit 1
    fi
}

# Afficher le statut
show_status() {
    cd docker
    print_info "Statut des services de développement:"
    docker-compose ps
    echo
    print_info "Statut des services de production:"
    docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Aucun service de production actif"
}

# Main
main() {
    # Banner
    echo -e "${BLUE}"
    cat << "EOF"
     ___  __     _____   __   
    |__ | |   |   /    |__| |__|
    |   |____ |  /___  |  | |      
    
    JLC Application - Docker Manager
EOF
    echo -e "${NC}"
    
    # Vérifications
    check_docker
    check_docker_daemon
    echo
    
    # Commande
    COMMAND="${1:-dev}"
    
    case "$COMMAND" in
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        stop)
            stop_services
            ;;
        clean)
            clean_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Commande inconnue: $COMMAND"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Exécuter
main "$@"

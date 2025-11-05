.PHONY: help dev prod build up down logs clean restart status

# Couleurs pour les messages
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m # No Color

help: ## Afficher l'aide
	@echo "$(GREEN)JLC Application - Commandes Docker$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# === Développement ===

dev: ## Démarrer l'environnement de développement
	@echo "$(GREEN)Démarrage de l'environnement de développement...$(NC)"
	cd docker && docker-compose up -d
	@echo "$(GREEN)✓ Services démarrés$(NC)"
	@echo ""
	@echo "Services disponibles:"
	@echo "  - Frontend:      http://localhost:5173"
	@echo "  - API:           http://localhost:8001"
	@echo "  - Auth:          http://localhost:8000"
	@echo "  - Mailhog:       http://localhost:8025"
	@echo "  - Mongo Express: http://localhost:8081"

dev-build: ## Reconstruire et démarrer l'environnement de développement
	@echo "$(GREEN)Reconstruction et démarrage...$(NC)"
	cd docker && docker-compose up -d --build

dev-logs: ## Afficher les logs de développement
	cd docker && docker-compose logs -f

dev-down: ## Arrêter l'environnement de développement
	@echo "$(YELLOW)Arrêt de l'environnement de développement...$(NC)"
	cd docker && docker-compose down

dev-clean: ## Arrêter et supprimer les volumes de développement
	@echo "$(RED)Nettoyage complet de l'environnement de développement...$(NC)"
	cd docker && docker-compose down -v
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# === Production ===

prod: ## Démarrer l'environnement de production
	@echo "$(GREEN)Démarrage de l'environnement de production...$(NC)"
	cd docker && docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Services de production démarrés$(NC)"

prod-build: ## Reconstruire et démarrer l'environnement de production
	@echo "$(GREEN)Reconstruction et démarrage de la production...$(NC)"
	cd docker && docker-compose -f docker-compose.prod.yml up -d --build

prod-logs: ## Afficher les logs de production
	cd docker && docker-compose -f docker-compose.prod.yml logs -f

prod-down: ## Arrêter l'environnement de production
	@echo "$(YELLOW)Arrêt de l'environnement de production...$(NC)"
	cd docker && docker-compose -f docker-compose.prod.yml down

prod-clean: ## Arrêter et supprimer les volumes de production (ATTENTION!)
	@echo "$(RED)⚠️  ATTENTION: Cette commande va supprimer tous les volumes de production!$(NC)"
	@read -p "Êtes-vous sûr? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	cd docker && docker-compose -f docker-compose.prod.yml down -v
	@echo "$(GREEN)✓ Nettoyage de production terminé$(NC)"

# === Services spécifiques ===

restart-frontend: ## Redémarrer le service frontend
	@echo "$(YELLOW)Redémarrage du frontend...$(NC)"
	cd docker && docker-compose restart jlc-web
	@echo "$(GREEN)✓ Frontend redémarré$(NC)"

restart-api: ## Redémarrer le service API
	@echo "$(YELLOW)Redémarrage de l'API...$(NC)"
	cd docker && docker-compose restart jlc-api
	@echo "$(GREEN)✓ API redémarrée$(NC)"

restart-auth: ## Redémarrer le service Auth
	@echo "$(YELLOW)Redémarrage du service Auth...$(NC)"
	cd docker && docker-compose restart auth-microservice
	@echo "$(GREEN)✓ Service Auth redémarré$(NC)"

# === Logs par service ===

logs-frontend: ## Afficher les logs du frontend
	cd docker && docker-compose logs -f jlc-web

logs-api: ## Afficher les logs de l'API
	cd docker && docker-compose logs -f jlc-api

logs-auth: ## Afficher les logs du service Auth
	cd docker && docker-compose logs -f auth-microservice

logs-mongo: ## Afficher les logs de MongoDB
	cd docker && docker-compose logs -f mongodb

# === Statut ===

status: ## Afficher le statut de tous les services
	@echo "$(GREEN)Statut des services:$(NC)"
	cd docker && docker-compose ps

status-prod: ## Afficher le statut des services de production
	@echo "$(GREEN)Statut des services de production:$(NC)"
	cd docker && docker-compose -f docker-compose.prod.yml ps

# === Shell ===

shell-frontend: ## Ouvrir un shell dans le container frontend
	cd docker && docker-compose exec jlc-web sh

shell-api: ## Ouvrir un shell dans le container API
	cd docker && docker-compose exec jlc-api bash

shell-auth: ## Ouvrir un shell dans le container Auth
	cd docker && docker-compose exec auth-microservice bash

shell-mongo: ## Ouvrir un shell MongoDB
	cd docker && docker-compose exec mongodb mongosh

# === Backup & Restore ===

backup-mongo: ## Créer un backup de MongoDB
	@echo "$(GREEN)Création du backup MongoDB...$(NC)"
	mkdir -p ./backups
	cd docker && docker-compose exec -T mongodb mongodump --out=/data/backup/$$(date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Backup créé$(NC)"

restore-mongo: ## Restaurer un backup MongoDB (BACKUP_DATE=YYYYMMDD_HHMMSS)
	@if [ -z "$(BACKUP_DATE)" ]; then \
		echo "$(RED)Erreur: spécifiez la date du backup avec BACKUP_DATE=YYYYMMDD_HHMMSS$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restauration du backup $(BACKUP_DATE)...$(NC)"
	cd docker && docker-compose exec -T mongodb mongorestore /data/backup/$(BACKUP_DATE)
	@echo "$(GREEN)✓ Backup restauré$(NC)"

# === Maintenance ===

prune: ## Nettoyer les images et volumes Docker inutilisés
	@echo "$(YELLOW)Nettoyage des ressources Docker inutilisées...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

prune-all: ## Nettoyer TOUTES les ressources Docker (ATTENTION!)
	@echo "$(RED)⚠️  ATTENTION: Cette commande va supprimer toutes les ressources Docker inutilisées!$(NC)"
	@read -p "Êtes-vous sûr? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker system prune -a --volumes -f
	@echo "$(GREEN)✓ Nettoyage complet terminé$(NC)"

# === Tests ===

test: ## Lancer les tests (à implémenter)
	@echo "$(YELLOW)Tests à implémenter$(NC)"

# === CI/CD ===

ci-build: ## Build pour CI/CD
	@echo "$(GREEN)Build CI/CD...$(NC)"
	cd docker && docker-compose -f docker-compose.prod.yml build --no-cache

ci-test: ## Tests pour CI/CD
	@echo "$(GREEN)Tests CI/CD...$(NC)"
	# Commandes de tests ici

# === Documentation ===

docs: ## Ouvrir la documentation
	@echo "$(GREEN)Documentation disponible dans:$(NC)"
	@echo "  - /docs"
	@echo "  - /docker/README.md"

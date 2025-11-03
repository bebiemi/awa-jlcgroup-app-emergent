# Commandes Docker Essentielles - JLC App

## 🚀 Démarrage Rapide

### Développement
```bash
# Démarrage en mode développement
docker-compose up -d

# Avec rebuild des images
docker-compose up -d --build

# Suivi des logs
docker-compose logs -f
```

### Production
```bash
# Démarrage en production
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Avec rebuild
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## 📊 Monitoring

### État des Services
```bash
# Voir tous les conteneurs
docker-compose ps

# Voir l'utilisation des ressources
docker stats

# Health check manuel
docker-compose exec jlc-api curl http://localhost:8001/health
docker-compose exec auth-microservice curl http://localhost:8000/health
```

### Logs
```bash
# Tous les logs
docker-compose logs

# Logs d'un service spécifique
docker-compose logs jlc-api
docker-compose logs auth-microservice
docker-compose logs mongodb

# Suivi en temps réel
docker-compose logs -f jlc-api

# Dernières 100 lignes
docker-compose logs --tail=100 jlc-api
```

## 🔧 Gestion des Services

### Redémarrage
```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart jlc-api
docker-compose restart mongodb
```

### Arrêt et Nettoyage
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Arrêter et supprimer les images
docker-compose down --rmi all
```

## 🗄️ Base de Données

### Accès MongoDB
```bash
# Connexion à MongoDB
docker-compose exec mongodb mongo

# Avec authentification (production)
docker-compose exec mongodb mongo -u admin -p

# Backup de la base
docker-compose exec mongodb mongodump --db jlc_db --out /tmp/backup
docker cp $(docker-compose ps -q mongodb):/tmp/backup ./backup

# Restore de la base
docker cp ./backup $(docker-compose ps -q mongodb):/tmp/
docker-compose exec mongodb mongorestore --db jlc_db --drop /tmp/backup/jlc_db
```

### Mongo Express (Interface Web)
```bash
# Accéder à l'interface web MongoDB
# http://localhost:8081
# Utilisateur: admin / Mot de passe: admin
```

## 🐛 Débogage

### Accès aux Conteneurs
```bash
# Shell dans le conteneur API
docker-compose exec jlc-api /bin/bash

# Shell dans le conteneur Auth
docker-compose exec auth-microservice /bin/bash

# Shell dans MongoDB
docker-compose exec mongodb /bin/bash

# Shell dans le frontend
docker-compose exec jlc-web /bin/sh
```

### Inspection des Images
```bash
# Lister les images
docker images

# Inspecter une image
docker inspect jlc-api

# Historique d'une image
docker history jlc-api
```

### Réseau
```bash
# Lister les réseaux
docker network ls

# Inspecter le réseau de l'application
docker network inspect docker_jlc-network

# Tester la connectivité entre services
docker-compose exec jlc-api ping mongodb
docker-compose exec jlc-api ping auth-microservice
```

## 🔄 Mise à Jour

### Rebuild d'un Service Spécifique
```bash
# Rebuild et redémarrage de l'API
docker-compose up -d --build jlc-api

# Rebuild et redémarrage de l'Auth
docker-compose up -d --build auth-microservice

# Rebuild et redémarrage du Frontend
docker-compose up -d --build jlc-web
```

### Mise à Jour des Dépendances
```bash
# Rebuild sans cache
docker-compose build --no-cache jlc-api

# Pull des nouvelles images de base
docker-compose pull
```

## 📁 Gestion des Volumes

### Volumes de Données
```bash
# Lister les volumes
docker volume ls

# Inspecter un volume
docker volume inspect docker_mongodb_data
docker volume inspect docker_uploads

# Backup d'un volume
docker run --rm -v docker_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb_backup.tar.gz -C /data .

# Restore d'un volume
docker run --rm -v docker_mongodb_data:/data -v $(pwd):/backup alpine tar xzf /backup/mongodb_backup.tar.gz -C /data
```

## 🧹 Nettoyage

### Nettoyage Général
```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune

# Supprimer les volumes non utilisés
docker volume prune

# Nettoyage complet du système
docker system prune -a
```

### Nettoyage Spécifique au Projet
```bash
# Supprimer tous les conteneurs du projet
docker-compose down --rmi all -v

# Supprimer les volumes du projet
docker volume rm docker_mongodb_data docker_uploads
```

## 🔐 Sécurité

### Scan de Sécurité
```bash
# Scanner les vulnérabilités (si Docker Scout est installé)
docker scout cves jlc-api
docker scout cves auth-microservice
```

### Gestion des Secrets
```bash
# Vérifier les variables d'environnement
docker-compose config

# Voir les variables d'un conteneur
docker-compose exec jlc-api env | grep -E "(MONGO|JWT|GOOGLE)"
```

## 📈 Performance

### Monitoring des Ressources
```bash
# Utilisation CPU/Mémoire en temps réel
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Limiter les ressources d'un service
# (à ajouter dans docker-compose.yml)
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### Optimisation
```bash
# Voir la taille des images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Analyser les layers d'une image
docker history jlc-api --no-trunc
```

## 🚨 Dépannage d'Urgence

### Service qui ne Répond Plus
```bash
# Forcer l'arrêt d'un conteneur
docker kill $(docker-compose ps -q jlc-api)

# Redémarrer en mode debug
docker-compose up jlc-api

# Vérifier les ports
netstat -tulpn | grep :8001
```

### Problème de Connectivité
```bash
# Tester la connectivité réseau
docker-compose exec jlc-api nslookup mongodb
docker-compose exec jlc-api telnet mongodb 27017

# Recréer le réseau
docker-compose down
docker network rm docker_jlc-network
docker-compose up -d
```

### Corruption de Données
```bash
# Arrêter tous les services
docker-compose down

# Restaurer depuis la dernière sauvegarde
./scripts/restore.sh backups/jlc_backup_latest.tar.gz

# Redémarrer
docker-compose up -d
```

## 📝 Logs Avancés

### Configuration des Logs
```bash
# Configurer la rotation des logs (dans docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Analyse des Logs
```bash
# Filtrer les erreurs
docker-compose logs | grep ERROR

# Logs avec timestamp
docker-compose logs -t

# Exporter les logs
docker-compose logs > application.log
```

---

**💡 Conseil** : Créez des alias pour les commandes fréquentes :

```bash
# Ajouter à ~/.bashrc ou ~/.zshrc
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
```
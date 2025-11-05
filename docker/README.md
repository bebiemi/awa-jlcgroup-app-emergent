# JLC Docker Configuration

## Vue d'ensemble

Ce dossier contient toutes les configurations Docker pour déployer l'application JLC en développement et en production.

## Structure

```
docker/
├── docker-compose.yml          # Configuration développement
├── docker-compose.prod.yml     # Configuration production
├── .env.example                # Template de variables d'environnement
├── nginx/                      # Configuration Nginx (production)
└── mongo-init/                 # Scripts d'initialisation MongoDB
```

## Développement Local

### Prérequis
- Docker 20.10+
- Docker Compose 2.0+

### Démarrage rapide

```bash
# 1. Aller dans le dossier docker
cd docker

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier le statut
docker-compose ps

# 4. Voir les logs
docker-compose logs -f
```

### Services disponibles

- **Frontend (React + Vite)**: http://localhost:5173
- **API Backend**: http://localhost:8001
- **Auth Service**: http://localhost:8000
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **Mailhog**: http://localhost:8025
- **Mongo Express**: http://localhost:8081 (admin/admin)

### Commandes utiles

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Reconstruire les images
docker-compose build

# Reconstruire et redémarrer
docker-compose up -d --build

# Voir les logs d'un service spécifique
docker-compose logs -f jlc-web
docker-compose logs -f auth-microservice

# Exécuter une commande dans un container
docker-compose exec jlc-api bash
```

## Production

### Prérequis
- Docker 20.10+
- Docker Compose 2.0+
- Domaine configuré avec DNS
- Certificats SSL (Let's Encrypt recommandé)

### Configuration

1. **Créer le fichier .env**
```bash
cp .env.example .env
# Éditer .env avec vos valeurs de production
```

2. **Configurer MongoDB**
```bash
mkdir -p mongo-init
# Créer les scripts d'initialisation si nécessaire
```

3. **Configurer Nginx**
```bash
mkdir -p nginx/conf.d nginx/ssl
# Placer vos certificats SSL dans nginx/ssl/
```

### Déploiement

```bash
# 1. Builder les images
docker-compose -f docker-compose.prod.yml build

# 2. Démarrer en production
docker-compose -f docker-compose.prod.yml up -d

# 3. Vérifier la santé des services
docker-compose -f docker-compose.prod.yml ps
```

### Monitoring

```bash
# Voir les logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Vérifier l'utilisation des ressources
docker stats

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Backup MongoDB

```bash
# Créer un backup
docker-compose -f docker-compose.prod.yml exec mongodb mongodump \
  --username=$MONGO_ROOT_USERNAME \
  --password=$MONGO_ROOT_PASSWORD \
  --out=/data/backup/$(date +%Y%m%d)

# Restaurer un backup
docker-compose -f docker-compose.prod.yml exec mongodb mongorestore \
  --username=$MONGO_ROOT_USERNAME \
  --password=$MONGO_ROOT_PASSWORD \
  /data/backup/20231201
```

### Mise à jour

```bash
# 1. Pull les dernières modifications
git pull origin main

# 2. Rebuild les images
docker-compose -f docker-compose.prod.yml build

# 3. Redémarrer avec zero-downtime (si configuré)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build <service>
```

## Troubleshooting

### MongoDB ne démarre pas
```bash
# Vérifier les logs
docker-compose logs mongodb

# Vérifier les permissions du volume
docker volume inspect docker_mongodb_data
```

### Frontend ne se connecte pas au backend
```bash
# Vérifier les variables d'environnement
docker-compose exec jlc-web env | grep VITE

# Vérifier la connectivité réseau
docker-compose exec jlc-web ping jlc-api
```

### Redis connection error
```bash
# Tester la connexion Redis
docker-compose exec redis redis-cli ping

# Vérifier le mot de passe (production)
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping
```

## Sécurité

### Bonnes pratiques

1. **Ne jamais commit le fichier .env**
2. **Utiliser des mots de passe forts** (minimum 32 caractères)
3. **Activer HTTPS en production** avec certificats SSL valides
4. **Limiter les ports exposés** en production
5. **Configurer les backups automatiques**
6. **Mettre à jour régulièrement** les images Docker
7. **Utiliser un utilisateur non-root** dans les containers (déjà configuré)

## Support

Pour toute question ou problème:
1. Vérifier la documentation dans `/docs`
2. Consulter les logs: `docker-compose logs`
3. Contacter l'équipe technique

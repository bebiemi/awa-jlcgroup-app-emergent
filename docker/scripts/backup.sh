#!/bin/bash

# Script de sauvegarde MongoDB
set -e

BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="jlc_backup_$DATE"

echo "📦 Création de la sauvegarde: $BACKUP_NAME"

# Création du dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données principale
docker exec jlc-mongodb-prod mongodump --db jlc_db --out /tmp/backup
docker cp jlc-mongodb-prod:/tmp/backup $BACKUP_DIR/$BACKUP_NAME

# Sauvegarde de la base d'authentification
docker exec jlc-mongodb-prod mongodump --db auth_db --out /tmp/auth_backup
docker cp jlc-mongodb-prod:/tmp/auth_backup $BACKUP_DIR/${BACKUP_NAME}_auth

# Compression
tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $BACKUP_DIR $BACKUP_NAME ${BACKUP_NAME}_auth

# Nettoyage
rm -rf $BACKUP_DIR/$BACKUP_NAME $BACKUP_DIR/${BACKUP_NAME}_auth

echo "✅ Sauvegarde créée: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Nettoyage des anciennes sauvegardes (garde les 7 dernières)
find $BACKUP_DIR -name "jlc_backup_*.tar.gz" -type f -mtime +7 -delete

echo "🧹 Anciennes sauvegardes nettoyées"

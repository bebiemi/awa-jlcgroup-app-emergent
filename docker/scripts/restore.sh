#!/bin/bash

# Script de restauration MongoDB
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="./restore_temp"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Fichier de sauvegarde introuvable: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restauration depuis: $BACKUP_FILE"

# Extraction de la sauvegarde
mkdir -p $RESTORE_DIR
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Restauration de la base principale
if [ -d "$RESTORE_DIR/jlc_backup_*/jlc_db" ]; then
    echo "📥 Restauration de jlc_db..."
    docker cp $RESTORE_DIR/jlc_backup_*/jlc_db jlc-mongodb-prod:/tmp/
    docker exec jlc-mongodb-prod mongorestore --db jlc_db --drop /tmp/jlc_db
fi

# Restauration de la base d'authentification
if [ -d "$RESTORE_DIR/jlc_backup_*_auth/auth_db" ]; then
    echo "📥 Restauration de auth_db..."
    docker cp $RESTORE_DIR/jlc_backup_*_auth/auth_db jlc-mongodb-prod:/tmp/
    docker exec jlc-mongodb-prod mongorestore --db auth_db --drop /tmp/auth_db
fi

# Nettoyage
rm -rf $RESTORE_DIR

echo "✅ Restauration terminée"

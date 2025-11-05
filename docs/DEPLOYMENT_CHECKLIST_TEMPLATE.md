# ✅ Checklist de Déploiement - [ENVIRONNEMENT]

**Date**: _______________  
**Environnement**: [ ] Dev  [ ] Staging  [ ] Production  
**Version**: _______________  
**Déployé par**: _______________  
**Reviewé par**: _______________

---

## 📋 Pré-Déploiement

### Code & Tests
- [ ] Tous les tests unitaires passent (`pytest`)
- [ ] Tests d'intégration passent
- [ ] Tests frontend passent (`npm test`)
- [ ] Pull request approuvée (min 1 reviewer)
- [ ] Pas de conflits de merge
- [ ] Code lint passé (backend + frontend)

### Documentation
- [ ] README mis à jour si nécessaire
- [ ] CHANGELOG.md mis à jour avec nouvelles features/fixes
- [ ] Documentation API mise à jour (si changements)
- [ ] Documentation utilisateur mise à jour (si UI changes)

### Configuration
- [ ] Secrets configurés pour l'environnement cible
- [ ] Variables d'environnement vérifiées
- [ ] Fichiers de configuration validés (YAML)
- [ ] Test de configuration exécuté (`python scripts/test_config.py`)

### Base de Données
- [ ] Migrations préparées (si nécessaire)
- [ ] Scripts de migration testés sur copie de BD
- [ ] Backup de la base de données effectué
- [ ] Plan de rollback BD préparé

### Infrastructure
- [ ] Serveurs disponibles et accessibles
- [ ] Espace disque suffisant (min 20% libre)
- [ ] Certificats SSL valides (prod uniquement)
- [ ] DNS configurés correctement
- [ ] Firewall rules vérifiées

### Communication
- [ ] Équipe DevOps informée
- [ ] Équipe QA informée (staging/prod)
- [ ] Fenêtre de maintenance annoncée (prod uniquement)
- [ ] Status page mise à jour (prod uniquement)

---

## 🚀 Déploiement

### 1. Préparation

- [ ] Connexion au serveur établie
  ```bash
  ssh user@server.jlc-platform.com
  ```

- [ ] Vérification de l'environnement
  ```bash
  echo $APP_ENV
  # Doit afficher: dev / staging / prod
  ```

- [ ] Version Git vérifiée
  ```bash
  cd /app && git log -1
  ```

### 2. Backup (Staging/Prod uniquement)

- [ ] Backup MongoDB effectué
  ```bash
  mongodump --uri="${MONGO_URL}" --out=/backups/$(date +%Y%m%d_%H%M%S)
  ```

- [ ] Backup fichiers uploadés
  ```bash
  tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz /app/uploads
  ```

- [ ] Emplacement backup noté: _______________

### 3. Code

- [ ] Code pullé depuis Git
  ```bash
  git pull origin main
  # ou
  git checkout <tag-version>
  ```

- [ ] Commit hash noté: _______________

### 4. Dépendances

- [ ] Dépendances backend installées
  ```bash
  cd /app/auth-microservice
  pip install -r requirements.txt
  ```

- [ ] Dépendances frontend installées
  ```bash
  cd /app/apps/web
  yarn install
  ```

### 5. Configuration

- [ ] Secrets déchiffrés (dev/staging)
  ```bash
  python scripts/encrypt_env.py decrypt .env.encrypted .env
  ```

- [ ] Configuration testée
  ```bash
  python scripts/test_config.py
  ```

- [ ] Résultat test config: [ ] ✅ Tous passés  [ ] ❌ Échecs

### 6. Base de Données

- [ ] Migrations exécutées (si applicable)
  ```bash
  # Ajouter commande migration ici
  ```

- [ ] Données de référence mises à jour (si nécessaire)
  ```bash
  python scripts/seed_mission_references.py
  python scripts/seed_additional_references.py
  ```

### 7. Services

#### Option A: Supervisor (Dev/Staging)

- [ ] Services redémarrés
  ```bash
  sudo supervisorctl restart all
  ```

- [ ] Status vérifié
  ```bash
  sudo supervisorctl status
  ```

#### Option B: Docker (Production)

- [ ] Images buildées
  ```bash
  docker-compose -f docker-compose.prod.yml build
  ```

- [ ] Services redéployés
  ```bash
  docker-compose -f docker-compose.prod.yml up -d --no-deps --build auth-microservice
  ```

- [ ] Status vérifié
  ```bash
  docker-compose -f docker-compose.prod.yml ps
  ```

### 8. Temps d'attente

- [ ] Attente démarrage services (30 secondes)
  ```bash
  sleep 30
  ```

---

## ✅ Post-Déploiement

### Tests de Santé

- [ ] Backend health check
  ```bash
  curl https://[ENV]-api.jlc-platform.com/health
  ```
  - Statut: [ ] 200 OK  [ ] Erreur
  - Environnement retourné: _______________

- [ ] Frontend accessible
  ```bash
  curl -I https://[ENV].jlc-platform.com
  ```
  - Statut: [ ] 200 OK  [ ] Erreur

- [ ] OAuth configuré
  ```bash
  curl https://[ENV]-api.jlc-platform.com/api/auth/google/status
  ```
  - Résultat: [ ] configured: true  [ ] Erreur

### Tests Fonctionnels

- [ ] Login admin fonctionne
  - Username: admin
  - Résultat: [ ] ✅ OK  [ ] ❌ Échec

- [ ] API missions accessible
  ```bash
  curl -H "Authorization: Bearer $TOKEN" \
       https://[ENV]-api.jlc-platform.com/api/missions
  ```
  - Résultat: [ ] ✅ OK  [ ] ❌ Échec

- [ ] Upload document fonctionne (test manuel)
  - Résultat: [ ] ✅ OK  [ ] ❌ Échec

- [ ] Notifications email (si activées)
  - Résultat: [ ] ✅ OK  [ ] ❌ Échec  [ ] N/A

### Logs

- [ ] Logs backend vérifiés (pas d'erreur critique)
  ```bash
  tail -n 100 /var/log/supervisor/jlc-backend-*.log
  # ou
  docker-compose logs --tail=100 auth-microservice
  ```
  - Résultat: [ ] ✅ Pas d'erreur  [ ] ⚠️ Warnings  [ ] ❌ Erreurs

- [ ] Logs frontend vérifiés
  - Résultat: [ ] ✅ OK  [ ] ❌ Erreurs

### Métriques

- [ ] CPU normal (< 70%)
  ```bash
  top -bn1 | grep "Cpu(s)"
  ```
  - CPU: _______________

- [ ] RAM normale (< 80%)
  ```bash
  free -h
  ```
  - RAM utilisée: _______________

- [ ] Connexions MongoDB normales
  ```bash
  mongosh $MONGO_URL --eval "db.serverStatus().connections"
  ```
  - Connexions: _______________

- [ ] Temps de réponse API (< 500ms)
  ```bash
  curl -w "@curl-format.txt" -o /dev/null -s https://[ENV]-api.jlc-platform.com/health
  ```
  - Temps: _______________

### Monitoring

- [ ] Dashboard monitoring accessible
- [ ] Alertes configurées (prod uniquement)
- [ ] Logs centralisés actifs (CloudWatch/ELK)
- [ ] Pas d'alerte déclenchée

---

## 📊 Validation Finale

### Tests de Régression (Staging/Prod)

- [ ] Parcours utilisateur principal testé
- [ ] Création de mission testée
- [ ] Candidature à une mission testée
- [ ] Gestion utilisateurs testée (admin)
- [ ] Workflow complet testé

### Performance

- [ ] Temps de chargement page < 3s
- [ ] Temps de réponse API < 500ms
- [ ] Pas de memory leak détecté

### Sécurité

- [ ] HTTPS activé et fonctionnel
- [ ] Headers de sécurité présents
- [ ] Tokens JWT valides
- [ ] Rate limiting actif

---

## 🎯 Décision de Déploiement

### Tous les tests passent?

- [ ] ✅ OUI - Déploiement validé
- [ ] ❌ NON - Rollback nécessaire

### Si NON, procéder au Rollback:

- [ ] Rollback exécuté
  ```bash
  # Supervisor
  git checkout <previous-commit>
  sudo supervisorctl restart all
  
  # Docker
  docker-compose down
  git checkout <previous-commit>
  docker-compose up -d --build
  ```

- [ ] Services rétablis
- [ ] Health check OK après rollback

---

## 📝 Post-Déploiement (30 minutes après)

### Monitoring Continu

- [ ] Logs surveillés (pas de nouvelles erreurs)
- [ ] Métriques stables
- [ ] Pas de plainte utilisateur
- [ ] Équipe technique en veille

### Communication

- [ ] Équipe informée du succès
- [ ] Status page mise à jour (prod)
- [ ] Documentation interne mise à jour

---

## 📋 Rapport de Déploiement

### Résumé

**Statut final**: [ ] ✅ Succès  [ ] ⚠️ Succès avec warnings  [ ] ❌ Échec

**Durée totale**: _______________

**Problèmes rencontrés**:
- _______________
- _______________

**Actions correctives**:
- _______________
- _______________

### Métriques

- **Downtime**: _______________ (0 si zero-downtime)
- **Taux de réussite tests**: _______________
- **Temps de réponse moyen**: _______________

### Améliorations pour prochain déploiement

1. _______________
2. _______________
3. _______________

---

## 🔗 Références

- [Deployment Overview](/app/docs/DEPLOYMENT_OVERVIEW.md)
- [Dev Guide](/app/docs/DEPLOYMENT_DEV_GUIDE.md)
- [Prod Guide](/app/docs/DEPLOYMENT_PROD_GUIDE.md)
- [Quick Reference](/app/docs/DEPLOYMENT_QUICK_REFERENCE.md)

---

## ✍️ Signatures

**Déployé par**: _______________  
**Date**: _______________  
**Signature**: _______________

**Validé par**: _______________  
**Date**: _______________  
**Signature**: _______________

---

**Notes additionnelles**:

_______________
_______________
_______________

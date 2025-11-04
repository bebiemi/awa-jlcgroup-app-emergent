# 🔄 Guide Complet - Renouvellement Automatique Let's Encrypt

## 📋 Durée de Validité des Certificats

Les certificats **Let's Encrypt** ont une durée de validité de **90 jours**.

**Recommandations** :
- ✅ Renouvellement automatique tous les **30 jours** avant expiration
- ✅ Let's Encrypt recommande de renouveler à partir de **60 jours**
- ✅ Notre solution : renouvellement le **1er de chaque mois** (tous les 30 jours)

---

## 🚀 Installation Rapide du Renouvellement Automatique

### Option 1 : Script d'Installation Automatique (Recommandé)

Exécutez simplement cette commande :

```bash
cd /opt/jlc-app/docker/scripts
chmod +x setup-ssl-renewal.sh
./setup-ssl-renewal.sh
```

Le script fait tout automatiquement ! ✨

---

## 🔧 Installation Manuelle (Étape par Étape)

### Étape 1 : Préparer le Script de Renouvellement

```bash
# Aller dans le dossier scripts
cd /opt/jlc-app/docker/scripts

# Éditer le script de renouvellement
nano renew-ssl.sh
```

**Modifiez la ligne 9** avec votre domaine :
```bash
DOMAIN="votredomaine.com"  # Remplacez par votre vrai domaine
```

**Modifiez la ligne 10** si votre app est ailleurs :
```bash
APP_DIR="/opt/jlc-app"  # Chemin vers votre application
```

**Sauvegardez** : `Ctrl+X`, puis `Y`, puis `Enter`

### Étape 2 : Rendre le Script Exécutable

```bash
chmod +x renew-ssl.sh
```

### Étape 3 : Tester le Script Manuellement

```bash
# Test à sec (simulation)
sudo /opt/jlc-app/docker/scripts/renew-ssl.sh --dry-run

# Test réel
sudo /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Résultat attendu** :
```
[2025-01-20 15:30:00] =========================================
[2025-01-20 15:30:00] Démarrage du renouvellement SSL
[2025-01-20 15:30:00] =========================================
[2025-01-20 15:30:01] ✓ Renouvellement réussi ou non nécessaire
[2025-01-20 15:30:02] ✓ Le certificat expire dans 85 jours
[2025-01-20 15:30:03] =========================================
[2025-01-20 15:30:03] Renouvellement SSL terminé avec succès
[2025-01-20 15:30:03] =========================================
```

### Étape 4 : Configurer le Cron Job

```bash
# Ouvrir l'éditeur crontab
sudo crontab -e
```

**Ajoutez cette ligne à la fin du fichier** :

```bash
# Renouvellement SSL Let's Encrypt - Tous les 1er du mois à 3h du matin
0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1
```

**Explication** :
- `0 3 1 * *` : Minute 0, Heure 3, Jour 1 du mois, Tous les mois, Tous les jours de la semaine
- `/opt/jlc-app/docker/scripts/renew-ssl.sh` : Chemin du script
- `>> /var/log/ssl-renewal.log 2>&1` : Log la sortie

**Sauvegardez** : `Ctrl+X`, puis `Y`, puis `Enter`

### Étape 5 : Vérifier le Cron

```bash
# Lister les tâches cron actives
sudo crontab -l

# Vérifier que le service cron est actif
sudo systemctl status cron
```

---

## 📅 Alternatives de Configuration Cron

### Option A : Renouvellement Hebdomadaire (Plus Sûr)

```bash
# Tous les dimanches à 3h du matin
0 3 * * 0 /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Option B : Renouvellement Bi-mensuel

```bash
# Le 1er et le 15 de chaque mois à 3h
0 3 1,15 * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Option C : Renouvellement Mensuel (Recommandé)

```bash
# Le 1er de chaque mois à 3h
0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Option D : Renouvellement Quotidien (Let's Encrypt Recommandé)

```bash
# Tous les jours à 3h (Certbot ne renouvelle que si nécessaire)
0 3 * * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

---

## ⏰ Alternative : Systemd Timer (Plus Moderne)

### Avantages de Systemd Timer
- ✅ Plus fiable que cron
- ✅ Logs intégrés avec journalctl
- ✅ Gestion des dépendances
- ✅ Retry automatique en cas d'échec

### Installation

#### 1. Créer le Service

```bash
sudo nano /etc/systemd/system/ssl-renewal.service
```

**Contenu** :
```ini
[Unit]
Description=Renouvellement SSL Let's Encrypt pour JLC
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=/opt/jlc-app/docker/scripts/renew-ssl.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 2. Créer le Timer

```bash
sudo nano /etc/systemd/system/ssl-renewal.timer
```

**Contenu** :
```ini
[Unit]
Description=Timer pour le renouvellement SSL mensuel
Requires=ssl-renewal.service

[Timer]
# Exécuter le 1er de chaque mois à 3h du matin
OnCalendar=monthly
# OU pour un renouvellement quotidien (recommandé Let's Encrypt)
# OnCalendar=daily
# OnCalendar=03:00

# Si le système était éteint, rattraper l'exécution manquée
Persistent=true

# Ajouter un délai aléatoire de 0-1h pour éviter la surcharge des serveurs Let's Encrypt
RandomizedDelaySec=3600

[Install]
WantedBy=timers.target
```

#### 3. Activer et Démarrer

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le timer (démarrage automatique au boot)
sudo systemctl enable ssl-renewal.timer

# Démarrer le timer
sudo systemctl start ssl-renewal.timer

# Vérifier le statut
sudo systemctl status ssl-renewal.timer

# Voir quand sera la prochaine exécution
sudo systemctl list-timers ssl-renewal.timer
```

#### 4. Tester Manuellement

```bash
# Lancer le service manuellement (test)
sudo systemctl start ssl-renewal.service

# Voir les logs
sudo journalctl -u ssl-renewal.service -f
```

#### 5. Commandes Utiles

```bash
# Voir tous les timers
sudo systemctl list-timers

# Arrêter le timer
sudo systemctl stop ssl-renewal.timer

# Désactiver le timer
sudo systemctl disable ssl-renewal.timer

# Voir les logs du service
sudo journalctl -u ssl-renewal.service --since today

# Voir les logs du timer
sudo journalctl -u ssl-renewal.timer
```

---

## 📧 Ajouter des Notifications par Email

Pour être notifié en cas de problème ou de réussite.

### Méthode 1 : Via le Script (Simple)

Modifiez le script `renew-ssl.sh` :

```bash
nano /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Ajoutez ces fonctions au début** (après les variables) :

```bash
# Email de notification
ADMIN_EMAIL="votre-email@example.com"

# Fonction d'envoi d'email
send_email() {
    local subject="$1"
    local body="$2"
    
    if command -v mail &> /dev/null; then
        echo "$body" | mail -s "$subject" "$ADMIN_EMAIL"
    elif command -v sendmail &> /dev/null; then
        echo -e "Subject: $subject\n\n$body" | sendmail "$ADMIN_EMAIL"
    fi
}
```

**À la fin du script, ajoutez** :

```bash
# Notification de succès
send_email "✅ SSL Renewal Success - ${DOMAIN}" \
"Le renouvellement SSL a réussi.
Domaine: ${DOMAIN}
Date: $(date)
Expire dans: $DAYS_LEFT jours"
```

**En cas d'erreur, modifiez les sections exit 1 pour envoyer un email** :

```bash
send_email "❌ SSL Renewal Failed - ${DOMAIN}" \
"Le renouvellement SSL a échoué.
Domaine: ${DOMAIN}
Date: $(date)
Erreur: [description de l'erreur]"
exit 1
```

### Méthode 2 : Via Cron (Email intégré)

Cron envoie automatiquement un email en cas de sortie sur stdout/stderr.

**Configurez d'abord l'email** :

```bash
sudo crontab -e
```

**Ajoutez au début** :

```bash
MAILTO=votre-email@example.com

# Puis votre cron job habituel
0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Méthode 3 : Monitoring Externe (Healthchecks.io)

Service gratuit qui surveille vos cron jobs.

#### 1. Créer un Compte

- Allez sur https://healthchecks.io
- Créez un compte gratuit
- Créez une nouvelle "check" pour "SSL Renewal"
- Copiez l'URL de ping

#### 2. Modifier le Script

```bash
nano /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Ajoutez au début** :

```bash
HEALTHCHECK_URL="https://hc-ping.com/votre-uuid-unique"
```

**À la fin du script (en cas de succès)** :

```bash
# Ping healthchecks.io en cas de succès
curl -fsS -m 10 --retry 3 "$HEALTHCHECK_URL" > /dev/null
```

**En cas d'échec** :

```bash
# Ping avec /fail en cas d'erreur
curl -fsS -m 10 --retry 3 "${HEALTHCHECK_URL}/fail" > /dev/null
```

**Healthchecks.io vous enverra alors un email** si le script :
- N'a pas été exécuté
- A échoué
- Est en retard

---

## 📊 Monitoring et Logs

### Voir les Logs de Renouvellement

```bash
# Logs complets
cat /var/log/ssl-renewal.log

# Dernières 50 lignes
tail -n 50 /var/log/ssl-renewal.log

# Suivre en temps réel
tail -f /var/log/ssl-renewal.log

# Logs avec systemd
sudo journalctl -u ssl-renewal.service -f
```

### Vérifier la Date d'Expiration

```bash
# Voir la date d'expiration du certificat actuel
echo | openssl s_client -connect votredomaine.com:443 -servername votredomaine.com 2>/dev/null | openssl x509 -noout -dates

# Calculer les jours restants
EXPIRY=$(echo | openssl s_client -connect votredomaine.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
echo "Jours avant expiration: $DAYS_LEFT"
```

### Dashboard de Surveillance

Créez un simple script de vérification :

```bash
nano /opt/jlc-app/docker/scripts/check-ssl-status.sh
```

**Contenu** :

```bash
#!/bin/bash

DOMAIN="votredomaine.com"

echo "🔐 Statut SSL pour $DOMAIN"
echo "================================"

# Certificat actuel
EXPIRY=$(echo | openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN} 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
echo "📅 Expire le: $EXPIRY"

# Jours restants
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "⚠️  Jours restants: $DAYS_LEFT (Renouvellement urgent!)"
elif [ $DAYS_LEFT -lt 60 ]; then
    echo "🟡 Jours restants: $DAYS_LEFT (Renouvellement bientôt)"
else
    echo "✅ Jours restants: $DAYS_LEFT"
fi

# Certificats Let's Encrypt
echo ""
echo "📋 Certificats Let's Encrypt:"
sudo certbot certificates 2>/dev/null | grep -A 3 "$DOMAIN"

# Prochaine exécution cron
echo ""
echo "⏰ Prochaine exécution du cron:"
sudo crontab -l | grep renew-ssl.sh

# OU avec systemd
echo ""
echo "⏰ Prochaine exécution systemd:"
sudo systemctl list-timers ssl-renewal.timer --no-pager
```

**Rendre exécutable et lancer** :

```bash
chmod +x /opt/jlc-app/docker/scripts/check-ssl-status.sh
./check-ssl-status.sh
```

---

## 🧪 Tester le Renouvellement

### Test 1 : Dry Run (Simulation)

```bash
sudo certbot renew --dry-run
```

Simule le renouvellement sans rien modifier.

### Test 2 : Forcer le Renouvellement

```bash
# Forcer le renouvellement même si pas nécessaire
sudo certbot renew --force-renewal

# Puis copier et redémarrer
sudo /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Test 3 : Test du Cron

```bash
# Exécuter la commande cron manuellement
sudo /opt/jlc-app/docker/scripts/renew-ssl.sh

# Vérifier les logs
cat /var/log/ssl-renewal.log
```

---

## ⚠️ Gestion des Erreurs Courantes

### Erreur : "Port 80 occupé pendant le renouvellement"

**Problème** : Nginx utilise le port 80, empêchant le renouvellement standalone.

**Solution** : Utilisez le plugin webroot (déjà configuré dans nginx-letsencrypt.conf)

```bash
sudo certbot renew --webroot -w /opt/jlc-app/docker/nginx/webroot
```

### Erreur : "Certificat ne s'est pas renouvelé"

**Vérifications** :

```bash
# 1. Vérifier si le renouvellement est nécessaire
sudo certbot certificates

# 2. Vérifier les logs certbot
sudo cat /var/log/letsencrypt/letsencrypt.log

# 3. Forcer le renouvellement
sudo certbot renew --force-renewal
```

### Erreur : "Docker n'a pas redémarré"

**Vérification** :

```bash
# Vérifier que Docker fonctionne
docker ps

# Redémarrer manuellement
cd /opt/jlc-app/docker
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 📋 Checklist de Configuration

- [ ] Script renew-ssl.sh créé et configuré avec votre domaine
- [ ] Script rendu exécutable (`chmod +x`)
- [ ] Test manuel du script réussi
- [ ] Cron job configuré OU Systemd timer configuré
- [ ] Email de notification configuré (optionnel)
- [ ] Logs de renouvellement fonctionnels
- [ ] Monitoring externe configuré (optionnel - Healthchecks.io)
- [ ] Test dry-run réussi (`certbot renew --dry-run`)
- [ ] Documentation lue et comprise

---

## 🎯 Recommandations Finales

### Fréquence Optimale

**Let's Encrypt recommande** : Renouvellement quotidien

```bash
# Cron quotidien à 3h du matin
0 3 * * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Certbot est intelligent** : Il ne renouvelle que si le certificat expire dans moins de 30 jours.

### Backup des Certificats

Le script fait automatiquement un backup, mais vous pouvez aussi :

```bash
# Backup manuel
sudo tar -czf /opt/jlc-app/docker/backups/ssl-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt/

# Restauration si nécessaire
sudo tar -xzf /opt/jlc-app/docker/backups/ssl-backup-YYYYMMDD.tar.gz -C /
```

### Alertes Proactives

Configurez un monitoring qui vous alerte :
- **30 jours avant expiration** : Warning
- **15 jours avant expiration** : Critique
- **Échec de renouvellement** : Urgent

---

## 📞 Support

**En cas de problème** :

1. Vérifiez les logs : `/var/log/ssl-renewal.log`
2. Testez manuellement : `sudo /opt/jlc-app/docker/scripts/renew-ssl.sh`
3. Vérifiez certbot : `sudo certbot renew --dry-run`
4. Consultez la documentation Let's Encrypt : https://letsencrypt.org/docs/

---

## ✅ Résumé Ultra-Rapide

```bash
# 1. Configurer le script
sudo nano /opt/jlc-app/docker/scripts/renew-ssl.sh
# Modifier DOMAIN="votredomaine.com"

# 2. Rendre exécutable
chmod +x /opt/jlc-app/docker/scripts/renew-ssl.sh

# 3. Configurer cron
sudo crontab -e
# Ajouter: 0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh

# 4. Vérifier
sudo crontab -l
```

**C'est tout ! Vos certificats se renouvelleront automatiquement tous les mois. 🎉**

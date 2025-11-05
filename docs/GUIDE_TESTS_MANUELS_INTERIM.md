# Guide de Tests Manuels - Système Intérimaire

## 🎯 Objectif
Tester l'ensemble des fonctionnalités intérimaire implémentées avec données de test complètes.

---

## 📋 Prérequis

### Données de Test Créées ✅
- **Utilisateur**: `jeandupont`
- **Password**: `JeanDupont2025!`
- **Email**: `jean.dupont@jlc.com`
- **Rôle**: Intérimaire
- **Profil**: 85% complet

### Missions & Candidatures ✅
1. **GABON TELECOM** - Assistant Administratif
   - Statut: `contract_signed` (MISSION ACTIVE)
   - Fin dans **10 jours** (alerte J-14 activée!)
   - Libreville

2. **CASINO GABON** - Caissier Principal
   - Statut: `review` (en analyse)
   - Début dans 20 jours
   - Port-Gentil

3. **TOTAL GABON** - Secrétaire de Direction
   - Statut: `interviewed` (entretien passé)
   - Début dans 35 jours
   - Franceville

4. **BGFIBank** - Magasinier
   - Statut: `contract_signed` (mission TERMINÉE)
   - Terminée il y a 5 jours
   - Libreville

### Références Système ✅
- 6 workflow_steps ajoutés
- 12 jours fériés Gabon 2025 configurés
- 14 application_statuses existants

---

## 🧪 Scénarios de Test

### Test 1: Connexion Intérimaire
**Étapes**:
1. Aller sur http://localhost:3000
2. Cliquer sur "Connexion"
3. Entrer:
   - Username: `jeandupont`
   - Password: `JeanDupont2025!`
4. Cliquer "Se connecter"

**Résultat attendu**:
- ✅ Redirection vers `/interimaire` (dashboard)

---

### Test 2: Dashboard - Badge Statut Mission
**URL**: `/interimaire`

**Vérifications**:
- ✅ Badge **"🏢 En mission"** (vert) affiché en haut à droite
- ✅ Carte "Mission actuelle" visible avec:
  - Titre: "Assistant Administratif - Libreville"
  - Entreprise: "GABON TELECOM"
  - Localisation: "Libreville, Estuaire"

**Screenshot**: Badge doit être vert et visible

---

### Test 3: Dashboard - Alerte J-14
**URL**: `/interimaire`

**Vérifications**:
- ✅ Alerte orange affichée sous l'en-tête
- ✅ Texte contient:
  - "⚠️ Fin de mission approchante"
  - "se termine dans **10 jours**"
  - Date de fin affichée
  - "💡 C'est le moment de consulter..."
- ✅ Bouton "Voir les offres disponibles" présent et fonctionnel

**Action**:
- Cliquer sur "Voir les offres disponibles"
- Doit rediriger vers `/offres`

---

### Test 4: Dashboard - Complétude Profil
**URL**: `/interimaire`

**Vérifications**:
- ✅ Section "Complétude du profil" visible
- ✅ Barre de progression affiche **85%**
- ✅ Liste des champs complétés avec ✅
- ✅ Champs manquants listés (si < 100%)
- ✅ Bouton "Compléter mon profil" présent

**Action**:
- Vérifier que la barre est verte
- Si < 100%, vérifier que les champs manquants sont listés

---

### Test 5: Dashboard - Navigation Tuiles
**URL**: `/interimaire`

**Tuiles à tester**:

#### Tuile "Offres de Missions"
- ✅ Icône 📄 visible
- ✅ Titre: "Offres de Missions"
- ✅ Sous-titre: "Consulter les missions disponibles"
- ⚠️ **Alerte orange**: "Candidatures bloquées (mission en cours)"
- ✅ Clic → redirige vers `/offres`

#### Tuile "Mes Candidatures"
- ✅ Icône ✅ visible
- ✅ Titre: "Mes Candidatures"
- ✅ Sous-titre: "Suivre l'état de mes candidatures"
- ✅ Clic → redirige vers `/mes-candidatures`

#### Tuile "Mon Profil"
- ✅ Icône 👤 visible
- ✅ Titre: "Mon Profil"
- ✅ Sous-titre: "Mettre à jour mes informations"
- ✅ Clic → redirige vers `/profile`

---

### Test 6: Page Mes Candidatures - Stats
**URL**: `/mes-candidatures`

**Vérifications**:
- ✅ 4 cartes stats affichées:
  - **Total**: 4
  - **En cours**: 2 (review + interviewed)
  - **Acceptées**: 2 (contract_signed)
  - **Refusées**: 0

**Screenshot**: Cartes avec couleurs appropriées

---

### Test 7: Mes Candidatures - Alerte Mission Active
**URL**: `/mes-candidatures`

**Vérifications**:
- ✅ Alerte bleue en haut de page
- ✅ Icône 🏢
- ✅ Texte: "Mission en cours"
- ✅ Mention de "Assistant Administratif - Libreville"
- ✅ Message: "candidatures possibles 5 jours ouvrés avant fin"

---

### Test 8: Mes Candidatures - Regroupement par Statut
**URL**: `/mes-candidatures`

**Sections à vérifier**:

#### 📋 Candidatures en cours (2)
- ✅ Section affichée
- ✅ 2 cartes:
  1. **CASINO GABON** - Caissier
     - Badge bleu "En analyse"
     - **Nom masqué**: "Mission en cours de sélection" ⚠️
  2. **TOTAL GABON** - Secrétaire
     - Badge indigo "Entretien"
     - **Nom masqué**: "Mission en cours de sélection" ⚠️

#### ✅ Candidatures acceptées (2)
- ✅ Section affichée
- ✅ 2 cartes:
  1. **GABON TELECOM** - Assistant Administratif
     - Badge vert "Contrat signé"
     - **Nom visible** ✅
  2. **BGFIBank** - Magasinier
     - Badge vert "Contrat signé"
     - **Nom visible** ✅

#### ❌ Candidatures refusées (0)
- ✅ Section non affichée (aucune candidature refusée)

---

### Test 9: Mes Candidatures - Timeline de Progression
**URL**: `/mes-candidatures`

**Étapes**:
1. Cliquer sur "Voir les détails" sur la carte **CASINO GABON**

**Vérifications Timeline**:
- ✅ 6 étapes affichées horizontalement:
  1. 📝 Candidature envoyée (✅ vert)
  2. 🔍 Analyse / Pré-sélection (🔵 actuel - vert avec ring)
  3. 🤝 Entretien (⏳ gris)
  4. 📤 Transmission au client (⏳ gris)
  5. 📋 Validation contrat (⏳ gris)
  6. 🎯 Démarrage mission (⏳ gris)

- ✅ Ligne de connexion verte entre étapes 1-2
- ✅ Lignes grises pour étapes futures
- ✅ Étape actuelle avec ring coloré

**Actions**:
2. Tester sur **TOTAL GABON** (statut: interviewed)
   - Étapes 1, 2, 3 doivent être vertes
   - Étape 3 avec ring (actuelle)
   - Étapes 4-6 grises

3. Cliquer "Masquer les détails" pour replier

---

### Test 10: Mes Candidatures - Nom Mission Masqué
**URL**: `/mes-candidatures`

**Vérifications critiques**:

#### Candidatures NON signées (review, interviewed)
- ✅ Titre affiché: **"Mission en cours de sélection"**
- ❌ NOM RÉEL MISSION PAS VISIBLE
- ✅ Entreprise visible: "CASINO GABON", "TOTAL GABON"

#### Candidatures signées (contract_signed)
- ✅ Titre affiché: **Nom réel de la mission**
- ✅ "Assistant Administratif - Libreville"
- ✅ "Magasinier - Libreville"

**Test visuel**: Comparer les titres entre les différentes cartes

---

### Test 11: Page Profil - Champs Manquants
**URL**: `/profile`

**Vérifications**:
- ✅ Prénom: "Jean" affiché
- ✅ Nom: "Dupont" affiché
- ✅ Date de naissance: "15/06/1995" affichée
- ✅ Lieu de naissance: "Libreville" affiché
- ✅ Barre de progression: 85%

**Actions**:
1. Compléter un champ manquant (ex: ajouter une langue)
2. Sauvegarder
3. Retourner au dashboard
4. Vérifier que la progression s'est mise à jour

---

### Test 12: Navigation - Icône Home
**URL**: N'importe quelle page

**Vérifications**:
- ✅ Icône 🏠 dans la barre de navigation
- ✅ Clic → redirige vers `/interimaire` (pas `/`)
- ✅ Fonctionne depuis toutes les pages

---

### Test 13: Blocage Candidature
**URL**: `/offres` (page des offres)

**Vérifications**:
- ✅ Liste des missions affichée
- ✅ Sur chaque mission, bouton "Postuler"
- ⚠️ **Bouton désactivé ou alerte** si mission active
- ✅ Tooltip/message expliquant le blocage

**Note**: Ce test nécessite la page offres fonctionnelle

---

## 📊 Checklist Validation Complète

### Dashboard (/interimaire)
- [ ] Badge statut visible (En mission / En recherche)
- [ ] Carte mission active affichée (si applicable)
- [ ] Alerte J-14 visible (si < 14 jours)
- [ ] Complétude profil temps réel (85%)
- [ ] Tuiles navigation fonctionnelles (3/3)
- [ ] Alerte blocage candidature sur tuile offres

### Mes Candidatures (/mes-candidatures)
- [ ] Stats rapides (4 cartes)
- [ ] Alerte mission active en haut
- [ ] Regroupement par statut (en cours, acceptées, refusées)
- [ ] Nom mission masqué (review, interviewed)
- [ ] Nom mission visible (contract_signed)
- [ ] Timeline 6 étapes fonctionnelle
- [ ] Toggle détails fonctionne
- [ ] Badges de statut corrects

### Profil (/profile)
- [ ] Prénom/Nom affichés
- [ ] Date naissance affichée
- [ ] Lieu naissance affiché
- [ ] Icône home → /interimaire
- [ ] Barre progression mise à jour

### Général
- [ ] Navigation entre pages fluide
- [ ] Aucune valeur en dur visible
- [ ] Toutes les données viennent du backend
- [ ] Messages en français correct
- [ ] Design responsive

---

## 🐛 Bugs Connus / À Vérifier

1. **Login API**: Problème d'authentification avec curl (à investiguer)
   - Workaround: Utiliser interface web pour login

2. **Dates ISO**: Vérifier format affichage dates (FR vs EN)

3. **Timeline mobile**: Tester responsive sur petit écran

4. **Cache Redux**: Vérifier que les données se rafraîchissent correctement

---

## 📸 Screenshots Attendus

### 1. Dashboard avec alerte
![Dashboard](./screenshots/dashboard_alerte_j14.png)
- Badge "En mission" vert
- Carte mission active
- Alerte orange J-14
- Tuiles navigation

### 2. Mes Candidatures
![Candidatures](./screenshots/mes_candidatures.png)
- Stats en haut
- Sections par statut
- Nom masqué pour review/interviewed

### 3. Timeline détaillée
![Timeline](./screenshots/timeline_progression.png)
- 6 étapes
- Étape actuelle avec ring
- Connexions vertes/grises

---

## ✅ Critères de Succès

**Fonctionnalités critiques MUST WORK**:
1. ✅ Badge statut mission s'affiche correctement
2. ✅ Alerte J-14 apparaît quand < 14 jours
3. ✅ Nom mission masqué avant contract_signed
4. ✅ Timeline affiche progression correcte
5. ✅ Navigation tuiles fonctionne
6. ✅ Complétude profil temps réel

**Tests réussis si**:
- 100% des vérifications passent
- Aucune erreur console JavaScript
- Aucune valeur "undefined" ou "null" affichée
- Design cohérent et professionnel

---

## 🚀 Après les Tests

### Si tout fonctionne ✅
1. Documenter avec screenshots
2. Marquer comme "TESTED & VALIDATED"
3. Passer à la production

### Si bugs trouvés 🐛
1. Noter le bug précisément (screenshot + console logs)
2. Identifier le composant concerné
3. Corriger et re-tester

---

## 📞 Support

**Logs à consulter en cas de problème**:
```bash
# Backend
tail -f /var/log/supervisor/auth-microservice.err.log

# Frontend (console navigateur)
F12 → Console → Chercher erreurs rouges
```

**Vérifier données backend**:
```bash
# Connexion MongoDB
mongo jlc_db

# Vérifier user
db.users.findOne({username: "jeandupont"})

# Vérifier candidatures
db.mission_applications.find({interim_id: "USER_ID"}).pretty()

# Vérifier missions
db.missions.find({company_name: "GABON TELECOM"}).pretty()
```

---

**Version**: 1.0  
**Date**: 5 novembre 2025  
**Testeur**: _____________  
**Status**: ⏳ À tester

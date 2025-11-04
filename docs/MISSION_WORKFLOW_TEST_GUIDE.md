# Guide de Test - Workflow Complet de Gestion des Missions

## 📋 Vue d'ensemble

Ce guide vous permet de tester l'ensemble du processus "Candidat Mise à dispo" depuis la création d'une mission jusqu'à la signature du contrat.

---

## 👥 Comptes de Test Disponibles

### 1. **Compte Administrateur** ✅ Déjà créé
- **Username**: `admin`
- **Password**: `awana2025`
- **Rôle**: Admin
- **Accès**: Toutes les fonctionnalités
- **Dashboard**: `/admin`

### 2. **Compte Intérimaire** ✅ Déjà créé
- **Username**: `paf`
- **Password**: `AZERTY123456!!nbvcxw`
- **Rôle**: Interim
- **Accès**: Consultation offres, candidatures
- **Dashboard**: `/interimaire`

### 3. **Compte Entreprise** (À créer)
- **Email**: `entreprise.test@jlcgroup.com`
- **Username**: `entreprise_test`
- **Password**: `Entreprise2025!`
- **Rôle**: Company
- **Accès**: Création missions, gestion candidatures
- **Dashboard**: `/entreprise`

### 4. **Compte Commercial** (À créer)
- **Email**: `commercial.test@jlcgroup.com`
- **Username**: `commercial_test`
- **Password**: `Commercial2025!`
- **Rôle**: Commercial
- **Accès**: Gestion complète des missions
- **Dashboard**: `/admin` ou section spécifique

---

## 🔧 Création des Comptes de Test

### Étape 1: Créer le compte Entreprise

1. **Connectez-vous en tant qu'Admin** (admin/awana2025)
2. **Naviguez vers**: `/admin/users/new`
3. **Remplissez le formulaire**:
   - Email: `entreprise.test@jlcgroup.com`
   - Username: `entreprise_test`
   - Nom complet: `Entreprise Test SARL`
   - Password: `Entreprise2025!` (ou laissez générer automatiquement)
   - Rôles: ☑ `company`
   - Groupes: (optionnel)
   - Envoyer invitation: ☐ (décocher pour test)
4. **Cliquez sur**: "Créer l'utilisateur"

### Étape 2: Créer le compte Commercial

1. **Toujours connecté en tant qu'Admin**
2. **Naviguez vers**: `/admin/users/new`
3. **Remplissez le formulaire**:
   - Email: `commercial.test@jlcgroup.com`
   - Username: `commercial_test`
   - Nom complet: `Commercial Test`
   - Password: `Commercial2025!`
   - Rôles: ☑ `commercial` ☑ `admin` (pour accès complet)
   - Groupes: (optionnel)
   - Envoyer invitation: ☐
4. **Cliquez sur**: "Créer l'utilisateur"

### Étape 3: Créer un deuxième Intérimaire (optionnel)

1. **Toujours connecté en tant qu'Admin**
2. **Naviguez vers**: `/admin/users/new`
3. **Remplissez le formulaire**:
   - Email: `interim2.test@jlcgroup.com`
   - Username: `interim_test2`
   - Nom complet: `Jean Candidat`
   - Password: `Interim2025!`
   - Rôles: ☑ `interim`
4. **Cliquez sur**: "Créer l'utilisateur"

---

## 🧪 Scénarios de Test

### 📝 SCÉNARIO 1: Création et Publication de Mission

**Acteur**: Entreprise ou Admin/Commercial

#### Étapes:

1. **Connexion**
   - Déconnectez-vous du compte admin
   - Connectez-vous avec: `entreprise_test / Entreprise2025!`
   - Ou utilisez: `admin / awana2025`

2. **Navigation vers Missions**
   - Sidebar → Section "PROCESSUS"
   - Cliquez sur "Missions" ou "Mes Missions"
   - URL: `/missions`

3. **Créer une Nouvelle Mission**
   - Cliquez sur le bouton "➕ Nouvelle Mission"
   - URL: `/missions/create`

4. **Remplir le Formulaire**
   - **Titre**: `Développeur Full Stack JavaScript`
   - **Description**: 
     ```
     Nous recherchons un développeur Full Stack pour rejoindre notre équipe.
     
     Missions principales:
     - Développement frontend (React)
     - Développement backend (Node.js)
     - Intégration d'APIs
     - Tests et déploiement
     ```
   - **Type de poste**: `Developpeur`
   - **Localisation**: Sélectionnez une ville (ex: Libreville)
   - **Type de contrat**: `CDD` (Contrat à Durée Déterminée)
   - **Salaire Min**: `500000`
   - **Salaire Max**: `800000`
   - **Date de début**: (Date future, ex: dans 2 semaines)
   - **Date de fin**: (3-6 mois après la date de début)
   - **Compétences requises**: 
     ```
     - JavaScript, React, Node.js
     - MongoDB, REST API
     - Git, Docker
     ```
   - **Statut**: `Publiée` (pour la rendre visible aux intérimaires)

5. **Valider la Création**
   - Cliquez sur "Créer la Mission"
   - Vérifiez le message de succès
   - Vous devriez être redirigé vers la liste des missions

6. **Vérifications**
   - ✓ La mission apparaît dans la liste
   - ✓ Le statut est "Publiée"
   - ✓ Les statistiques sont mises à jour (Total: +1, Publiées: +1)

---

### 🔍 SCÉNARIO 2: Consultation des Offres (Intérimaire)

**Acteur**: Intérimaire

#### Étapes:

1. **Déconnexion et Reconnexion**
   - Déconnectez-vous du compte entreprise/admin
   - Connectez-vous avec: `paf / AZERTY123456!!nbvcxw`

2. **Navigation vers les Offres**
   - Sidebar → Section "MISSIONS"
   - Cliquez sur "Offres disponibles"
   - URL: `/offres`

3. **Consulter les Offres**
   - ✓ La mission "Développeur Full Stack JavaScript" est visible
   - ✓ Les informations principales sont affichées (titre, localisation, salaire)

4. **Voir les Détails**
   - Cliquez sur "Voir" ou sur la carte de la mission
   - URL: `/offres/{mission_id}`

5. **Vérifications**
   - ✓ Toutes les informations de la mission sont affichées
   - ✓ Description complète visible
   - ✓ Compétences requises listées
   - ✓ Bouton "Postuler" est présent

---

### 📤 SCÉNARIO 3: Candidature à une Mission

**Acteur**: Intérimaire (toujours connecté)

#### Étapes:

1. **Sur la page de détail de la mission**
   - Cliquez sur le bouton "Postuler à cette mission"
   - URL: `/offres/{mission_id}/postuler`

2. **Remplir le Formulaire de Candidature**
   - **Lettre de motivation**:
     ```
     Madame, Monsieur,

     Je me permets de postuler au poste de Développeur Full Stack JavaScript.
     
     Avec 3 ans d'expérience en développement web, je maîtrise les technologies 
     React et Node.js. J'ai travaillé sur plusieurs projets similaires et je suis 
     motivé à rejoindre votre équipe.
     
     Je reste à votre disposition pour un entretien.
     
     Cordialement,
     PAF
     ```
   - **CV** (optionnel): Uploader un fichier PDF si le champ existe
   - **Disponibilité**: Confirmer la disponibilité

3. **Soumettre la Candidature**
   - Cliquez sur "Envoyer ma candidature"
   - Vérifiez le message de confirmation

4. **Accéder à "Mes Candidatures"**
   - Sidebar → "Mes Candidatures"
   - URL: `/mes-candidatures`

5. **Vérifications**
   - ✓ La candidature apparaît dans la liste
   - ✓ Statut: "En attente" ou "Soumise"
   - ✓ Date de candidature affichée
   - ✓ Nom de la mission visible

---

### 📊 SCÉNARIO 4: Gestion des Candidatures (Entreprise/Admin)

**Acteur**: Entreprise ou Admin

#### Étapes:

1. **Déconnexion et Reconnexion**
   - Déconnectez-vous du compte intérimaire
   - Reconnectez-vous avec: `entreprise_test / Entreprise2025!`
   - Ou: `admin / awana2025`

2. **Navigation vers les Missions**
   - Sidebar → "PROCESSUS" → "Missions"
   - URL: `/missions`

3. **Voir les Candidatures**
   - Trouvez la mission "Développeur Full Stack JavaScript"
   - Cliquez sur "Voir" ou sur la mission
   - Dans la page de détails, section "Candidatures"
   - Ou URL directe: `/missions/{mission_id}/candidatures`

4. **Consulter la Candidature**
   - ✓ La candidature de "paf" est visible
   - ✓ Statut: "En attente"
   - ✓ Lettre de motivation affichée

5. **Actions sur la Candidature**
   - **Pré-sélectionner**: Cliquez sur "Pré-sélectionner"
     - Statut passe à "Présélectionnée"
   - **Planifier un Entretien**: Cliquez sur "Planifier entretien"
     - Remplir date et heure
     - Ajouter notes (optionnel)
     - Statut passe à "Entretien planifié"

6. **Vérifications**
   - ✓ Le statut de la candidature est mis à jour
   - ✓ L'intérimaire peut voir le changement de statut dans "Mes Candidatures"
   - ✓ Les statistiques de la mission sont à jour

---

### ✅ SCÉNARIO 5: Sélection du Candidat

**Acteur**: Entreprise ou Admin

#### Étapes:

1. **Sur la page de gestion des candidatures**
   - Après l'entretien (réel ou simulé)
   - Trouvez la candidature de "paf"

2. **Accepter la Candidature**
   - Cliquez sur "Accepter" ou "Embaucher"
   - Confirmez l'action
   - Statut passe à "Acceptée" ou "Embauchée"

3. **Vérifications**
   - ✓ Statut mis à jour
   - ✓ Notification à l'intérimaire (si système de notification actif)
   - ✓ Mission passe en statut "En cours"

---

### 📄 SCÉNARIO 6: Upload Documents (Visite Médicale)

**Acteur**: Admin ou Commercial (optionnellement Intérimaire)

#### Étapes:

1. **Navigation vers la Candidature**
   - Trouvez la candidature acceptée
   - Section "Documents"

2. **Upload du Certificat Médical**
   - Cliquez sur "Upload Visite Médicale"
   - Sélectionnez un fichier PDF (certificat médical)
   - Ajoutez des notes: "Apte au poste - Certificat du Dr. XYZ"
   - Validez l'upload

3. **Vérifications**
   - ✓ Document uploadé avec succès
   - ✓ Nom du fichier affiché
   - ✓ Date d'upload visible
   - ✓ Statut du processus avance

---

### 📝 SCÉNARIO 7: Upload Contrat et Finalisation

**Acteur**: Admin ou Commercial

#### Étapes:

1. **Upload du Contrat**
   - Dans la même section documents
   - Cliquez sur "Upload Contrat"
   - Sélectionnez le contrat signé (PDF)
   - Ajoutez des notes: "Contrat CDD 6 mois signé"
   - Validez

2. **Finaliser la Mission**
   - Si toutes les étapes sont complètes
   - Cliquez sur "Finaliser" ou "Valider"
   - Statut de la mission passe à "Terminée" ou "Contrat signé"

3. **Vérifications**
   - ✓ Contrat uploadé
   - ✓ Mission finalisée
   - ✓ Statistiques mises à jour
   - ✓ L'intérimaire peut voir le statut final

---

## 🔄 Workflow Complet - Vue d'ensemble

```
1. [ENTREPRISE/ADMIN] Crée une mission → Statut: "Publiée"
                ↓
2. [INTÉRIMAIRE] Voit l'offre dans /offres
                ↓
3. [INTÉRIMAIRE] Postule à la mission → Candidature: "En attente"
                ↓
4. [ENTREPRISE/ADMIN] Consulte les candidatures
                ↓
5. [ENTREPRISE/ADMIN] Pré-sélectionne → Candidature: "Présélectionnée"
                ↓
6. [ENTREPRISE/ADMIN] Planifie entretien → Candidature: "Entretien planifié"
                ↓
7. [ENTREPRISE/ADMIN] Accepte candidat → Candidature: "Acceptée"
                ↓
8. [ADMIN] Upload visite médicale → Document ajouté
                ↓
9. [ADMIN] Upload contrat signé → Document ajouté
                ↓
10. [ADMIN] Finalise → Mission: "Terminée", Candidature: "Embauchée"
```

---

## 🐛 Points à Tester / Vérifier

### Fonctionnalités Générales
- [ ] Authentification pour chaque type de compte
- [ ] Navigation dans le sidebar adaptée au rôle
- [ ] Redirections appropriées après actions
- [ ] Messages de succès/erreur clairs

### Missions
- [ ] Création de mission avec tous les champs
- [ ] Édition de mission existante
- [ ] Annulation de mission
- [ ] Recherche et filtres dans la liste des missions
- [ ] Statistiques correctes (total, publiées, en cours, candidatures)

### Candidatures
- [ ] Soumission de candidature
- [ ] Affichage dans "Mes Candidatures"
- [ ] Changements de statut visibles
- [ ] Gestion multi-candidatures pour une mission

### Documents
- [ ] Upload de fichiers PDF
- [ ] Affichage des documents uploadés
- [ ] Téléchargement des documents
- [ ] Validation des types de fichiers

### Notifications (si implémentées)
- [ ] Notification à la candidature
- [ ] Notification à l'acceptation
- [ ] Notification aux changements de statut

---

## 📌 URLs de Référence Rapide

| Rôle | Page | URL |
|------|------|-----|
| Admin | Dashboard | `/admin` |
| Admin | Gestion Missions | `/missions` |
| Admin | Créer Mission | `/missions/create` |
| Admin | Candidatures | `/missions/{id}/candidatures` |
| Entreprise | Dashboard | `/entreprise` |
| Entreprise | Mes Missions | `/missions` |
| Intérimaire | Dashboard | `/interimaire` |
| Intérimaire | Offres | `/offres` |
| Intérimaire | Détail Offre | `/offres/{id}` |
| Intérimaire | Postuler | `/offres/{id}/postuler` |
| Intérimaire | Mes Candidatures | `/mes-candidatures` |

---

## 🔒 Troubleshooting

### Problème: "401 Unauthorized"
- **Solution**: Reconnectez-vous avec les bons identifiants
- Vérifiez que l'utilisateur a le bon rôle
- Videz le cache du navigateur (Ctrl+Shift+R)

### Problème: "404 Not Found"
- **Solution**: Vérifiez l'URL
- Assurez-vous que l'endpoint backend existe
- Redémarrez le backend si nécessaire

### Problème: Page blanche ou erreur
- **Solution**: Ouvrez la console (F12)
- Vérifiez les erreurs JavaScript
- Vérifiez les erreurs réseau dans l'onglet Network

### Problème: Mission non visible dans /offres
- **Solution**: Vérifiez que le statut est "Publiée"
- Reconnectez-vous en tant qu'intérimaire
- Rafraîchissez la page

---

## 💡 Conseils de Test

1. **Testez dans l'ordre**: Suivez le workflow naturel du processus
2. **Utilisez plusieurs onglets**: Ouvrez un onglet par rôle pour tester les interactions
3. **Vérifiez les deux côtés**: Après une action, vérifiez l'impact pour l'autre acteur
4. **Prenez des notes**: Notez les bugs ou comportements inattendus
5. **Testez les cas limites**: 
   - Candidater plusieurs fois à la même mission
   - Modifier une mission avec des candidatures
   - Annuler une mission en cours

---

## 📸 Captures d'écran Recommandées

Pour documenter vos tests, prenez des captures d'écran de :
- Page de liste des missions (admin)
- Page des offres (intérimaire)
- Formulaire de candidature rempli
- Liste des candidatures (admin)
- Mes candidatures (intérimaire)
- Upload de documents

---

## ✅ Checklist Finale

Avant de considérer le système prêt pour production :

- [ ] Tous les rôles peuvent se connecter
- [ ] Tous les scénarios fonctionnent de bout en bout
- [ ] Les documents s'uploadent correctement
- [ ] Les statuts se mettent à jour en temps réel
- [ ] Aucune erreur dans la console
- [ ] Les redirections fonctionnent
- [ ] Les messages sont en français et clairs
- [ ] La navigation est intuitive
- [ ] Les performances sont acceptables

---

**Bonne chance avec vos tests ! 🚀**

Pour toute question ou problème rencontré, référez-vous à la documentation complète dans `/app/docs/`.

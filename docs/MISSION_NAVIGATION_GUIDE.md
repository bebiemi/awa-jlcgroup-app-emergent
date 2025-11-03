# Guide de Navigation - Système de Gestion des Missions

## Vue d'ensemble
Le système de gestion des missions (Candidat Mise à dispo) permet de gérer le cycle complet des missions d'intérim, depuis la création jusqu'à la signature du contrat.

## Navigation par Rôle

### 🔐 Pour les Administrateurs et Commerciaux

#### Accès Principal
Dans la barre latérale gauche, cherchez la section **"PROCESSUS"** et cliquez sur **"Missions"**.

**Chemin**: `Sidebar` → `PROCESSUS` → `Missions` → `/missions`

#### Pages Disponibles

1. **Gestion des Missions** (`/missions`)
   - Vue d'ensemble de toutes les missions
   - Statistiques: Total missions, Publiées, En cours, Candidatures
   - Recherche et filtrage par statut
   - Actions: Créer, Voir, Éditer, Annuler une mission
   - **Bouton principal**: `+ Nouvelle Mission` (en haut à droite)

2. **Créer une Mission** (`/missions/create`)
   - Accessible via le bouton "Nouvelle Mission" sur la page de gestion
   - Formulaire pour créer une nouvelle mission d'intérim
   - Champs: Titre, Description, Localisation, Type de contrat, etc.

3. **Détails d'une Mission** (`/missions/:id`)
   - Accessible en cliquant sur "Voir" depuis la liste des missions
   - Informations complètes de la mission
   - Liste des candidatures reçues
   - Actions: Éditer, Gérer les candidatures

4. **Éditer une Mission** (`/missions/:id/edit`)
   - Accessible depuis la page de détails ou liste des missions
   - Modification des informations de la mission

5. **Gestion des Candidatures** (`/candidatures`)
   - Vue d'ensemble de toutes les candidatures reçues
   - Filtres par mission, statut, candidat
   - Actions: Accepter, Refuser, Planifier entretien

---

### 👷 Pour les Intérimaires

#### Accès Principal
Dans la barre latérale gauche, section **"MISSIONS"**, vous avez deux options:

**Chemin 1**: `Sidebar` → `MISSIONS` → `Offres disponibles` → `/offres`
**Chemin 2**: `Sidebar` → `MISSIONS` → `Mes Candidatures` → `/mes-candidatures`

#### Pages Disponibles

1. **Offres Disponibles** (`/offres`)
   - Liste de toutes les missions publiées et disponibles
   - Recherche par mot-clé, localisation, type de contrat
   - Filtres: Localisation, Salaire, Type de contrat
   - **Action principale**: Voir les détails et postuler

2. **Détails d'une Offre** (`/offres/:id`)
   - Informations complètes sur la mission
   - Détails du poste, localisation, salaire, compétences requises
   - **Bouton principal**: `Postuler à cette mission`

3. **Postuler à une Mission** (`/offres/:id/apply`)
   - Formulaire de candidature
   - Lettre de motivation
   - Upload de CV (si nécessaire)
   - Confirmation de disponibilité

4. **Mes Candidatures** (`/mes-candidatures`)
   - Historique de toutes vos candidatures
   - Statuts: En attente, Acceptée, Refusée, Entretien planifié
   - Suivi du processus de recrutement
   - Notifications sur les changements de statut

---

### 🏢 Pour les Entreprises

#### Accès Principal
Dans la barre latérale gauche, section **"PROCESSUS"**, cliquez sur **"Mes Missions"**.

**Chemin**: `Sidebar` → `PROCESSUS` → `Mes Missions` → `/missions`

#### Pages Disponibles
(Similaires aux administrateurs, mais limitées aux missions de leur entreprise)

1. **Mes Missions** (`/missions`)
   - Vue de vos missions uniquement
   - Créer et gérer vos besoins en intérim

2. **Gestion des Candidatures**
   - Voir les candidatures pour vos missions
   - Sélectionner les candidats pour entretien
   - Valider le choix final

---

## Workflow Complet du Processus

### 1️⃣ Création de Mission (Admin/Commercial/Entreprise)
**Navigation**: Sidebar → PROCESSUS → Missions → Bouton "Nouvelle Mission"
- Remplir le formulaire de mission
- Publier la mission

### 2️⃣ Publication d'Offre
**Status**: La mission apparaît dans `/offres` pour les intérimaires
- Visible par tous les intérimaires
- Recherche et filtrage disponibles

### 3️⃣ Candidature (Intérimaire)
**Navigation**: Sidebar → MISSIONS → Offres disponibles → Sélectionner une offre → Postuler
- Remplir le formulaire de candidature
- Soumettre la candidature

### 4️⃣ Suivi de Candidature (Intérimaire)
**Navigation**: Sidebar → MISSIONS → Mes Candidatures
- Voir le statut de chaque candidature
- Notifications de changement de statut

### 5️⃣ Gestion des Candidatures (Admin/Commercial/Entreprise)
**Navigation**: Sidebar → PROCESSUS → Missions → Voir une mission → Candidatures
- Examiner les candidatures reçues
- Pré-sélectionner les candidats
- Planifier les entretiens

### 6️⃣ Entretiens et Sélection
- Conduire les entretiens
- Sélectionner le candidat final
- Notifier le candidat

### 7️⃣ Visite Médicale
- Upload du certificat médical
- Validation de l'aptitude

### 8️⃣ Signature du Contrat
- Génération du contrat
- Upload du contrat signé
- Validation finale

---

## Astuces de Navigation

### 🎯 Accès Rapide
- **Logo JLC** (en haut de la sidebar): Retour au tableau de bord principal
- **Icône Briefcase** 💼: Indique les pages liées aux missions
- **Badge de notifications** 🔔: Nouvelles candidatures ou changements de statut

### 🔍 Recherche et Filtres
- Utilisez la barre de recherche pour trouver rapidement une mission
- Les filtres par statut permettent de trier les missions (Brouillon, Publiée, En cours, Terminée, Annulée)

### 📱 Navigation Mobile
- Menu hamburger pour afficher/masquer la sidebar
- Navigation tactile optimisée

---

## FAQ Navigation

**Q: Je ne vois pas le menu "Missions" dans ma sidebar**
**R**: Vérifiez votre rôle utilisateur. Les missions sont accessibles aux rôles: Admin, Commercial, Entreprise, et Intérimaire. Reconnectez-vous si nécessaire.

**Q: La page `/missions` affiche "404 Not Found"**
**R**: Assurez-vous d'être connecté avec un compte ayant les permissions appropriées.

**Q: Comment accéder aux candidatures en tant qu'Admin?**
**R**: Sidebar → PROCESSUS → Missions → Cliquez sur une mission → Section "Candidatures"

**Q: Puis-je voir les missions d'autres entreprises?**
**R**: Non (sauf Admin/Commercial). Les entreprises voient uniquement leurs propres missions.

**Q: Comment suivre l'état de ma candidature?**
**R**: Intérimaires: Sidebar → MISSIONS → Mes Candidatures

---

## URLs de Référence Rapide

### Administrateurs/Commerciaux
- Gestion missions: `http://localhost:3000/missions`
- Créer mission: `http://localhost:3000/missions/create`
- Candidatures: `http://localhost:3000/candidatures`

### Intérimaires
- Offres disponibles: `http://localhost:3000/offres`
- Mes candidatures: `http://localhost:3000/mes-candidatures`

### Entreprises
- Mes missions: `http://localhost:3000/missions`

---

## Support
Pour toute question ou problème de navigation, contactez l'équipe support JLC Group.

**Contact**: support@jlcgroup.com  
**Documentation**: `/docs/`

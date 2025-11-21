# 📋 Améliorations Module Entreprises - Roadmap

**Date :** 21 novembre 2025  
**Module :** `/features/entreprises/`  
**Statut :** ✅ Config enrichie appliquée

---

## ✅ Déjà Implémenté

### 1. Architecture Config-Driven
- ✅ Structure standard respectée
- ✅ Config enrichie avec permissions IAM détaillées
- ✅ Actions transverses (relatedActions) définies
- ✅ Filtres enrichis configurés
- ✅ Pagination configurée (pageSize: 20, serverSide: true)

### 2. Config Actuelle (entreprises.config.ts)
```typescript
permissions: {
  view: "entreprises.read.all",
  create: "company.create",
  edit: "company.edit",
  delete: "company.delete",
  related: {
    needs: "besoins.read.own",
    missions: "missions.read.own",
    validation: "entreprises.validate",
    documents: "documents.read.own",
  }
}

relatedActions: [
  { label: "Voir les besoins", to: (id) => `/admin/besoins?entreprise=${id}` },
  { label: "Voir les missions", to: (id) => `/admin/missions?entreprise=${id}` },
  { label: "Valider cette entreprise", to: (id) => `/admin/validations/entreprise/${id}` },
  { label: "Documents de l'entreprise", to: (id) => `/admin/documents?entreprise=${id}` }
]

filters: {
  status: ["active", "inactive", "pending", "blocked"],
  localisation: { enabled: true, type: "select", source: "references.countries" },
  secteur: { enabled: true, type: "select", source: "references.secteurs" },
  date_creation: { enabled: true, type: "daterange" },
}
```

---

## 🔧 Améliorations Prioritaires (P1)

### 1. Gestion des Statuts Avancée
**Objectif :** Permettre l'activation/désactivation directe depuis le tableau

**Actions :**
- [ ] Créer `ToggleStatusModal.tsx`
- [ ] Ajouter bouton d'activation/désactivation rapide dans les actions
- [ ] Implémenter `useUpdateEntrepriseStatusMutation`
- [ ] Ajouter confirmation avant changement de statut

**Bénéfice :** Gain de temps pour les administrateurs (éviter d'ouvrir la modale d'édition)

---

### 2. Filtres Enrichis Fonctionnels
**Objectif :** Rendre les filtres configurés dans la config opérationnels

**Actions :**
- [ ] Implémenter le filtre "Localisation" (pays)
  - Récupérer la liste depuis `references.countries` API
  - Ajouter le dropdown dans la page
- [ ] Implémenter le filtre "Secteur d'activité"
  - Récupérer la liste depuis `references.secteurs` API
  - Ajouter le dropdown dans la page
- [ ] Implémenter le filtre "Date de création" (daterange)
  - Ajouter un composant DateRangePicker
  - Filtrer les résultats côté serveur
- [ ] Ajouter filtre "Type d'entreprise" (si pertinent)

**Bénéfice :** Faciliter la recherche quand JLC aura 200+ entreprises

---

### 3. Actions Transverses (Multi-Modules)
**Objectif :** Permettre la navigation entre modules depuis la page Entreprises

**Actions :**
- [ ] Créer un composant `RelatedActionsDropdown.tsx`
- [ ] Ajouter un menu dropdown dans les actions de chaque ligne
- [ ] Implémenter la navigation vers :
  - [ ] `/admin/besoins?entreprise=${id}` (avec permission `besoins.read.own`)
  - [ ] `/admin/missions?entreprise=${id}` (avec permission `missions.read.own`)
  - [ ] `/admin/validations/entreprise/${id}` (avec permission `entreprises.validate`)
  - [ ] `/admin/documents?entreprise=${id}` (avec permission `documents.read.own`)
- [ ] Vérifier les permissions IAM avant d'afficher chaque action

**Bénéfice :** Navigation fluide entre modules, gain de productivité

**Exemple d'UI :**
```
Actions : [👁️ Voir] [✏️ Modifier] [🗑️ Supprimer] [⋯ Plus d'actions ▼]
                                                     ↓
                                        - Voir les besoins
                                        - Voir les missions
                                        - Valider l'entreprise
                                        - Documents
```

---

## 🎨 Améliorations UX/UI (P2)

### 4. Tri et Export Avancés
**Actions :**
- [ ] Ajouter tri par "Date de création" (ascendant/descendant)
- [ ] Ajouter tri par "Nombre de besoins" (computed field)
- [ ] Ajouter tri par "Nombre de missions actives" (computed field)
- [ ] Implémenter export CSV avec filtres appliqués
  - Bouton "Exporter la sélection en CSV"
  - Permission : `entreprises.export`

**Bénéfice :** Utilisé par les commerciaux pour reporting

---

### 5. Avatars et Couleurs Automatiques
**Actions :**
- [ ] Créer un système de génération d'avatars avec couleurs cohérentes
  - Basé sur le hash du nom de l'entreprise
  - Palette de couleurs prédéfinie (8-10 couleurs)
- [ ] Ajouter icône de type d'entreprise (si applicable)

**Bénéfice :** Meilleure reconnaissance visuelle

---

### 6. Computed Fields (Champs Calculés)
**Objectif :** Afficher des informations agrégées sans surcharger l'API

**Actions :**
- [ ] Ajouter colonne "Besoins actifs" (compte des besoins en cours)
- [ ] Ajouter colonne "Missions en cours" (compte des missions actives)
- [ ] Ajouter colonne "Dernier contact" (date de dernière activité)
- [ ] Ajouter indicateur "Documents manquants" (🔴 si incomplet)

**Implémentation :**
- Option 1 : Computed côté backend (optimal)
- Option 2 : Computed côté frontend (si backend limité)

**Bénéfice :** Vue d'ensemble rapide de l'état de chaque entreprise

---

## 🔗 Intégrations Multi-Modules (P1)

### 7. Dashboard Entreprise
**Objectif :** Page de détail complète pour une entreprise

**Actions :**
- [ ] Créer `/features/entreprises/pages/EntrepriseDetailPage.tsx`
- [ ] Sections à inclure :
  - Informations générales (éditable)
  - Liste des utilisateurs de l'entreprise
  - Liste des besoins (avec statuts)
  - Liste des missions (avec statuts)
  - Documents déposés
  - Historique des validations
  - Timeline d'activité
- [ ] Route : `/admin/entreprises/:id`

**Bénéfice :** Vue 360° de l'entreprise

---

### 8. Workflow de Rattachement
**Objectif :** Gérer le transfert/rattachement d'entreprises

**Actions :**
- [ ] Créer `TransferEntrepriseModal.tsx`
- [ ] Permettre le rattachement à un groupe
- [ ] Permettre le transfert entre commerciaux
- [ ] Historique des transferts

**Bénéfice :** Gestion flexible des clients

---

## 📊 Analytics et Reporting (P3)

### 9. Vue Analytics
**Actions :**
- [ ] Ajouter dashboard analytics pour les entreprises
  - Nombre total d'entreprises
  - Répartition par statut
  - Répartition par secteur
  - Répartition géographique
  - Tendance de croissance (graphique)
- [ ] Export PDF du rapport

**Bénéfice :** Aide à la décision pour la direction

---

## 🧪 Tests et Qualité (P2)

### 10. Tests Automatisés
**Actions :**
- [ ] Tests unitaires pour `entreprises.config.ts`
- [ ] Tests d'intégration pour `EntreprisesPage.tsx`
- [ ] Tests E2E pour les workflows complets
  - Création d'entreprise
  - Modification
  - Changement de statut
  - Navigation vers modules liés
- [ ] Tests de permissions IAM

---

## 📈 Performance et Scalabilité (P3)

### 11. Optimisations
**Actions :**
- [ ] Implémenter pagination côté serveur (déjà configuré : `serverSide: true`)
- [ ] Ajouter infinite scroll ou "Load More"
- [ ] Implémenter cache intelligent pour les listes
- [ ] Lazy loading des computed fields
- [ ] Indexation backend optimisée pour les recherches

**Bénéfice :** Performance maintenue avec 1000+ entreprises

---

## 🔒 Sécurité et Audit (P2)

### 12. Audit Trail
**Actions :**
- [ ] Logger toutes les modifications d'entreprises
- [ ] Afficher historique des modifications dans la page détail
- [ ] Qui a créé/modifié/désactivé une entreprise
- [ ] Traçabilité complète

---

## 📝 Checklist d'Implémentation

### Phase 1 (Court terme - 1-2 semaines)
- [ ] Actions transverses fonctionnelles
- [ ] Filtres enrichis opérationnels
- [ ] Export CSV basique

### Phase 2 (Moyen terme - 3-4 semaines)
- [ ] Dashboard entreprise détaillé
- [ ] Computed fields
- [ ] Gestion avancée des statuts

### Phase 3 (Long terme - 2-3 mois)
- [ ] Analytics et reporting
- [ ] Workflow de rattachement
- [ ] Tests automatisés complets

---

## 🎯 Conclusion

Le module Entreprises est **fonctionnel et structuré correctement**. Les améliorations ci-dessus permettront de :
- Gérer efficacement une grande quantité d'entreprises
- Faciliter la navigation inter-modules
- Améliorer la productivité des commerciaux et administrateurs
- Préparer l'intégration avec Besoins, Missions, Validations

**Priorité actuelle :** Continuer la migration des autres modules (Besoins, Missions, Validations) avant de revenir sur ces améliorations.

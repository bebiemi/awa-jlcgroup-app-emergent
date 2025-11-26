# 📘 Exploitation du profil `agency_country`

## 🎯 Objectif
Assurer la prise en compte du nouveau profil d'agence multi-pays (`agency_country`) et documenter les opérations nécessaires pour l'activer côté base de données, permissions et bundles.

## 🌐 Contexte fonctionnel
- Les utilisateurs avec le rôle `agency` sont routés vers la collection MongoDB `agency_country_profiles` avec le `profile_type` `agency_country`.
- Un profil est créé automatiquement à la première requête `/profiles/me` avec les champs par défaut :
  - `user_id`
  - `document_ids: []`
  - `profile_completed: False`
  - `country: "GABON"` (Libreville par défaut)
  - `updated_at`
- La configuration de base expose le type dans `profiles.types.agency_country` (voir `auth-microservice/config/base.yaml`).

## 🗄️ Préparation base de données
### 1) Vérifier la configuration
- Confirmer que `profiles.types` contient `agency_country`.
- Confirmer que le rôle applicatif attendu est `security.roles.agency`.

### 2) Créer un utilisateur agence (exemple Mongo Shell)
```javascript
// Dans la collection users
const userId = "user_agency_gabon";
db.users.insertOne({
  id: userId,
  email: "agency-lbv@example.com",
  roles: ["agency"],
  status: "active",
  full_name: "Agence JLC Libreville",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});
```

### 3) Générer le profil agence-pays
Deux options :
1. Appeler l'API `GET /profiles/me` avec un token du compte ci-dessus (un document sera créé automatiquement).
2. Ou insérer manuellement :
```javascript
db.agency_country_profiles.insertOne({
  user_id: userId,
  country: "GABON", // remplacer par CAMEROUN, CONGO, etc. selon le déploiement
  document_ids: [],
  profile_completed: false,
  updated_at: new Date().toISOString(),
});
```

## 🔐 Permissions et bundles
### 1) Permissions minimales (collection `permissions`)
Utiliser le format `ressource.action[.scope]` déjà en place. Exemple :
```javascript
const perms = [
  {
    id: "perm_agency_country_read",
    code: "agency.country.read",
    name: "Lecture profil agence pays",
    description: "Consulter les informations d'une agence pays",
    resource: "agency_country",
    action: "read",
    scope: "own",
    category: "agency",
    created_at: new Date().toISOString(),
  },
  {
    id: "perm_agency_country_update",
    code: "agency.country.update",
    name: "Mise à jour profil agence pays",
    description: "Modifier les informations d'une agence pays",
    resource: "agency_country",
    action: "update",
    scope: "own",
    category: "agency",
    created_at: new Date().toISOString(),
  },
];
db.permissions.insertMany(perms);
```

### 2) Bundle dédié (collection `capability_bundles`)
Assembler les permissions dans un bundle réutilisable :
```javascript
db.capability_bundles.insertOne({
  id: "bundle_agency_country_core",
  code: "agency_country.core",
  name: "Noyau profil agence pays",
  description: "Bundle de base pour la gestion des agences pays",
  category: "business",
  permission_ids: ["perm_agency_country_read", "perm_agency_country_update"],
  tags: ["agency", "country"],
  is_system: false,
  created_at: new Date().toISOString(),
});
```

### 3) Profil IAM (collection `profiles`)
Créer le profil métier et lier le bundle :
```javascript
db.profiles.insertOne({
  id: "profile_agency_country",
  code: "agency_country",
  name: "Agence JLC (pays)",
  description: "Profil pour les agences JLC par pays",
  category: "business",
  permission_ids: [],
  capability_bundle_ids: ["bundle_agency_country_core"],
  is_protected: false,
  is_system_role: false,
  created_at: new Date().toISOString(),
});
```

## ✅ Checklist de recette
- [ ] Un utilisateur avec `roles: ["agency"]` obtient `{ "profile_type": "agency_country" }` via `GET /profiles/me`.
- [ ] Le document par défaut contient `country: "GABON"` (ou la valeur renseignée manuellement).
- [ ] Les permissions ci-dessus sont présentes et attribuées via le bundle `agency_country.core`.
- [ ] Les tests `pytest auth-microservice/tests/test_profile_routes.py` passent localement.

## 🌍 Ouverture multi-pays
Pour ajouter un nouveau pays :
1. Créer le compte utilisateur avec `roles: ["agency"]`.
2. Insérer/mettre à jour le document dans `agency_country_profiles` avec `country` défini (ex. `"CONGO"`).
3. Optionnel : créer des bundles/permissions spécifiques par pays en utilisant le préfixe `agency_country.<pays>` si une granularité différente est requise.

# ⚠️ ORDRE DES ROUTERS - RÈGLE CRITIQUE

## Problème Rencontré

**Date** : 15 Novembre 2025  
**Symptôme** : 404 sur `/api/profiles/me` pour utilisateurs admin  
**Cause** : Ordre incorrect de montage des routers dans FastAPI

---

## Règle d'Or FastAPI

**FastAPI matche les routes dans l'ordre où elles sont montées.**

La première route qui correspond à l'URL est utilisée. Les routes suivantes avec le même pattern sont ignorées.

---

## Ordre CORRECT (server.py)

```python
# ⚠️ ORDRE CRITIQUE - NE PAS MODIFIER

# 1️⃣ PROXIES EN PREMIER (routes spécifiques vers microservices)
app.include_router(auth_proxy_routes.router, prefix="/api/auth")
app.include_router(auth_endpoints_proxy.router, prefix="/api")  # Includes /profiles/me
app.include_router(iam_proxy_routes.router, prefix="/api/iam")
app.include_router(config_proxy_routes.router, prefix="/api/config")
app.include_router(security_proxy_routes.router, prefix="/api")
app.include_router(besoins_proxy_routes.router, prefix="/api/besoins")
app.include_router(entreprises_proxy_routes.router, prefix="/api/entreprises")

# 2️⃣ ROUTES LOCALES EN DERNIER (logique backend spécifique)
app.include_router(profile_routes.router, prefix="/api")  # Local profiles (jlc_db)
app.include_router(validation_routes.router, prefix="/api")
app.include_router(notification_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
```

---

## Pourquoi cet ordre ?

### Exemple du problème

**Ordre INCORRECT (❌)** :
```python
# Monté en PREMIER - matche /api/profiles/me
app.include_router(profile_routes.router, prefix="/api")  # Local, jlc_db

# Monté en SECOND - ne sera JAMAIS utilisé pour /profiles/me
app.include_router(auth_endpoints_proxy.router, prefix="/api")  # Proxy, auth_db
```

**Résultat** :
- Requête : `GET /api/profiles/me`
- FastAPI trouve d'abord `profile_routes` qui a une route `/profiles/me`
- Utilise la route locale (jlc_db)
- Admin n'a pas de profil dans jlc_db → **404 Not Found**
- Le proxy vers auth-microservice n'est jamais appelé

---

**Ordre CORRECT (✅)** :
```python
# Monté en PREMIER - intercepte /api/profiles/me
app.include_router(auth_endpoints_proxy.router, prefix="/api")  # Proxy vers auth_db

# Monté en SECOND - utilisé uniquement si proxy ne matche pas
app.include_router(profile_routes.router, prefix="/api")  # Fallback local
```

**Résultat** :
- Requête : `GET /api/profiles/me`
- FastAPI trouve d'abord `auth_endpoints_proxy` qui a une route `/profiles/me`
- Proxy vers auth-microservice (auth_db)
- Admin a son profil dans auth_db → **200 OK**

---

## Impact des Erreurs d'Ordre

### Symptômes typiques

1. **404 Not Found** : Route existe mais n'est jamais appelée
2. **Wrong database** : Route locale query mauvaise DB
3. **Wrong response format** : Route locale vs proxy retournent formats différents
4. **Permission errors** : Route locale vs proxy ont différentes vérifications

### Cas réels

| Endpoint | Si local AVANT proxy | Si proxy AVANT local |
|----------|---------------------|---------------------|
| `/api/profiles/me` | ❌ 404 (jlc_db vide) | ✅ 200 (auth_db OK) |
| `/api/users/me` | ❌ Wrong format | ✅ Correct format |
| `/api/auth/login` | ❌ Not found | ✅ Works |

---

## Checklist Ajout Nouveau Router

Lors de l'ajout d'un nouveau router dans `server.py` :

### Questions à se poser

1. **Ce router est-il un proxy ?**
   - OUI → Monter AVANT les routes locales
   - NON → Monter APRÈS les proxies

2. **Le prefix/path existe déjà ?**
   - OUI → Vérifier l'ordre (proxy en premier)
   - NON → Libre de choisir la position

3. **Le router gère-t-il des sous-ressources ?**
   - Exemple : `/api/users/{id}` vs `/api/users/me`
   - Plus spécifique en PREMIER

### Pattern de test

```python
# Après ajout router, TOUJOURS tester :
# 1. Endpoint direct
curl http://localhost:8001/api/mon-endpoint

# 2. Vérifier logs pour voir quelle route matche
# Regarder dans /var/log/supervisor/backend.*.log

# 3. Tester variations
curl http://localhost:8001/api/mon-endpoint/me
curl http://localhost:8001/api/mon-endpoint/123
```

---

## FastAPI Documentation Officielle

**Route Ordering** :
> Routes are matched in the order they are defined. If you have two routes that could match the same path, the first one will be used.

Source : https://fastapi.tiangolo.com/tutorial/path-params/#order-matters

---

## Historique des Incidents

| Date | Endpoint | Problème | Solution |
|------|----------|----------|----------|
| 15/11/2025 | `/api/profiles/me` | 404 pour admin | Réordonné : proxy avant local |
| - | - | - | - |

---

## Code Actuel (Référence)

Voir `/app/apps/api/server.py` lignes 82-100 pour l'ordre actuel correct.

**Commentaire dans le code** :
```python
# ⚠️ IMPORTANT: Proxy routes MUST be mounted BEFORE local routes to avoid conflicts
```

---

## En Résumé

### ✅ À FAIRE
- Monter proxies AVANT routes locales
- Documenter raison de l'ordre si non-évident
- Tester après changement d'ordre
- Vérifier logs pour voir quelle route matche

### ❌ À ÉVITER
- Modifier l'ordre sans raison
- Monter routes locales avant proxies avec même prefix
- Ignorer les warnings dans les commentaires
- Supposer que "ça marchera"

---

**⚠️ RÈGLE D'OR** : En cas de doute, toujours mettre les **PROXIES EN PREMIER** !

---

**Version** : 1.0  
**Dernière mise à jour** : 15 Novembre 2025  
**Status** : ⚠️ CRITIQUE - À RESPECTER ABSOLUMENT

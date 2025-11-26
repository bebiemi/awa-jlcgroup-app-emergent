# Contrat API mobile v1

Ce contrat décrit la surface stable destinée aux clients mobiles. Tous les appels passent par `/api/v1` et respectent une sémantique commune pour la pagination, le tri, le filtrage et les codes d'erreur.

## Principes généraux
- **Versionnement** : le préfixe `/api/v1` est figé pour les applications mobiles. Une nouvelle version sera introduite via un nouveau préfixe (`/api/v2`) sans rupture.
- **Rate limiting** :  `RATE_LIMIT_REQUESTS_PER_MINUTE` (par défaut `60`) sur une fenêtre de `RATE_LIMIT_WINDOW_SECONDS` (par défaut `60`) avec un éventuel backend Redis (`REDIS_URL`). Les réponses retournent `X-RateLimit-*` et une erreur normalisée `429` avec `error.code=RATE_LIMIT_EXCEEDED`.
- **Timeouts côté client API** : tous les proxies utilisent des timeouts homogènes (`API_CLIENT_TIMEOUT_SECONDS`, `API_CLIENT_CONNECT_TIMEOUT_SECONDS`). En cas d'échec upstream :
  - `504` avec `error.code=UPSTREAM_TIMEOUT`
  - `503` avec `error.code=UPSTREAM_UNAVAILABLE`
- **Offline-first** : toutes les réponses JSON incluent `meta.updated_at` (UTC, ISO8601) pour permettre la synchronisation locale. Les erreurs incluent `error.code`, `error.message`, `meta.updated_at` et éventuellement `meta.retry_after`.

## Paramètres de pagination/tri/filtrage
- `page` (défaut: `1`, min `1`)
- `page_size` (défaut: `20`, max `100`)
- `sort` (ex: `sort=created_at:desc`)
- `filter` (clé/valeur sérialisée ou répétable selon ressource)

Traduction backend : `limit = page_size`, `skip = (page-1)*page_size`. Les métadonnées retournent `meta.pagination = {page, page_size}` pour faciliter le cache local.

## Endpoints v1
| Méthode | Endpoint | Description | Notes |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/login` | Connexion utilisateur | Forward vers `/api/auth/login` |
| POST | `/api/v1/auth/refresh` | Rafraîchir le token | Forward vers `/api/auth/refresh` |
| GET | `/api/v1/profiles/me` | Profil courant | Forward vers `/api/profiles/me` |
| GET | `/api/v1/entreprises` | Liste paginée des entreprises | `page`, `page_size`, `sort`, `filter` |
| GET | `/api/v1/besoins` | Liste paginée des besoins | `page`, `page_size`, `sort`, `filter` |

## Codes d'erreur normalisés
- `RATE_LIMIT_EXCEEDED` (`429`) : trop de requêtes, inclut `meta.retry_after`.
- `UPSTREAM_TIMEOUT` (`504`) : dépassement du délai sur le service auth.
- `UPSTREAM_UNAVAILABLE` (`503`) : service auth indisponible.
- `SERVICE_UNAVAILABLE` (`503`) : indisponibilité générique (fallback cache ou réseau down).

## Champs de synchronisation
- `meta.updated_at` est toujours présent sur les réponses JSON.
- Les endpoints paginés exposent `meta.pagination` pour aider à la consolidation locale.
- Les clients peuvent persister le payload et les métadonnées pour un mode offline-first sans ambiguïté.

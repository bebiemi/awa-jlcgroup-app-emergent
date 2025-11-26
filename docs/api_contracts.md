# API Contracts et résilience

Cette note documente les conventions appliquées aux routes proxy publiques et d’authentification exposées par `apps/api`.

## Normalisation des routes proxy

* Toutes les routes proxy utilisent désormais un helper commun (`src/presentation/routes/proxy_helpers.py`) pour :
  * épurer les en-têtes sensibles (`Host`, `Connection`, `X-Forwarded-*`) avant de joindre le service amont ;
  * propager systématiquement les timeouts configurés et les exceptions HTTPX sous forme d’erreurs normalisées ;
  * enrichir les réponses JSON avec `meta.updated_at` afin de faciliter les scénarios offline-first.
* Les proxys `auth`, `auth-api`, `besoins`, `entreprises`, `documents/support`, `email-verification` sont alignés sur cette même logique.

## Gestion des erreurs (offline-first)

* Les erreurs amont sont renvoyées via `normalized_error` avec un objet `error` (`code`, `message`) et un champ `meta.updated_at` ISO8601.
* Les timeouts remontent `UPSTREAM_TIMEOUT` (504) et les indisponibilités réseau `UPSTREAM_UNAVAILABLE` (503).
* Les réponses JSON issues des services amont sont enrichies d’un `meta.updated_at` pour permettre la mise en cache côté client lorsque l’appareil est hors ligne.

## Rate limiting et en-têtes de quota

* Le middleware global ajoute les en-têtes standard :
  * `X-RateLimit-Limit`
  * `X-RateLimit-Window`
  * `X-RateLimit-Reset`
* En cas de dépassement, l’API renvoie `RATE_LIMIT_EXCEEDED` (429) avec `meta.retry_after` et `meta.updated_at`.

## Cache applicatif / Redis

* Un cache applicatif (`ResponseCache`) est initialisé au démarrage et se base sur Redis lorsqu’il est disponible (fallback mémoire sinon).
* Les requêtes `GET` pour les routes publiques `besoins`, `entreprises`, `support` et `entreprises/form-config` peuvent être servies depuis ce cache.
* La clé de cache inclut l’URL, les paramètres de requête et une empreinte du jeton `Authorization` le cas échéant, afin d’éviter toute fuite inter-utilisateur.
* Le TTL par défaut est piloté par la variable d’environnement `RESPONSE_CACHE_TTL_SECONDS`.

## Timeouts

* Tous les appels sortants utilisent `get_async_client` avec des timeouts configurables (`API_CLIENT_TIMEOUT_SECONDS`, `API_CLIENT_CONNECT_TIMEOUT_SECONDS`).
* Les proxys d’email vérification, documents/support et auth utilisent également ce client partagé pour garantir un comportement homogène.

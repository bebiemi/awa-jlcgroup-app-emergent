# Guide d'exécution : audit des valeurs en dur

Ce guide explique comment lancer localement l'audit des valeurs en dur et comment il est intégré à la CI.

## Utilisation locale

```bash
python scripts/audit_hardcoded_values.py \
  --root-dir . \
  --markdown-output audit_reports/AUDIT_VALEURS_EN_DUR.md \
  --stats-output audit_reports/stats.json \
  --max-occurrences 2040
```

Options principales :

- `--root-dir` : racine du dépôt à scanner (par défaut la racine du projet).
- `--markdown-output` : emplacement du rapport Markdown généré.
- `--stats-output` : chemin vers un fichier JSON contenant le nombre total et le détail par sévérité (utile pour les comparaisons CI).
- `--max-occurrences` : seuil maximal d'occurrences autorisées. Le script retourne un code de sortie 1 si le seuil est dépassé.
  Peut aussi être fourni via la variable d'environnement `AUDIT_MAX_OCCURRENCES`.

## Intégration CI

Le workflow GitHub Actions `.github/workflows/audit-hardcoded-values.yml` exécute le script sur chaque push vers `main` et sur les pull requests. Il :

1. Génère le rapport dans `audit_reports/AUDIT_VALEURS_EN_DUR.md` (avec `audit_reports/stats.json` pour les statistiques).
2. Publie ce rapport en tant qu'artifact nommé `audit-hardcoded-values-report`.
3. Compare automatiquement le nombre d'occurrences avec la branche cible de la PR via les statistiques générées et échoue si le delta dépasse `AUDIT_NEW_OCCURRENCES_THRESHOLD` (par défaut `0`, ajustable dans le workflow ou via une variable d'environnement).
4. Continue de faire échouer l'exécution si le seuil absolu `AUDIT_MAX_OCCURRENCES` (par défaut `2040`) est dépassé.

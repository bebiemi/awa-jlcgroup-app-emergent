# Guide d'exécution : audit des valeurs en dur

Ce guide explique comment lancer localement l'audit des valeurs en dur et comment il est intégré à la CI.

## Utilisation locale

```bash
python scripts/audit_hardcoded_values.py \
  --root-dir . \
  --markdown-output docs/AUDIT_VALEURS_EN_DUR.md \
  --max-occurrences 2040
```

Options principales :

- `--root-dir` : racine du dépôt à scanner (par défaut la racine du projet).
- `--markdown-output` : emplacement du rapport Markdown généré.
- `--max-occurrences` : seuil maximal d'occurrences autorisées. Le script retourne un code de sortie 1 si le seuil est dépassé. Peut aussi être fourni via la variable d'environnement `AUDIT_MAX_OCCURRENCES`.

## Intégration CI

Le workflow GitHub Actions `.github/workflows/audit-hardcoded-values.yml` exécute le script sur chaque push vers `main` et sur les pull requests. Il :

1. Génère le rapport dans `audit_reports/AUDIT_VALEURS_EN_DUR.md`.
2. Publie ce rapport en tant qu'artifact nommé `audit-hardcoded-values-report`.
3. Échoue si le nombre d'occurrences dépasse le seuil `AUDIT_MAX_OCCURRENCES` (valeur par défaut : `2040`, ajustable dans le workflow ou via une variable d'environnement au fil de la remédiation).

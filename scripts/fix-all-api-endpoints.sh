#!/bin/bash

# Script de migration automatique des endpoints API
# Corrige tous les fichiers pour respecter le standard /api/<service>/<resource>

set -e

echo "🚀 Migration des endpoints API vers le standard unifié"
echo "========================================================"
echo ""

cd /app/apps/web/src

# Étape 1: Corriger tous les createBaseQueryWithAuth
echo "📝 Étape 1: Correction des createBaseQueryWithAuth..."
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i \
  -e "s/createBaseQueryWithAuth(['\"][^)]*['\"])/createBaseQueryWithAuth()/g" \
  -e "s/createBaseQueryWithAuth('')/createBaseQueryWithAuth()/g" \
  -e "s/createBaseQueryWithAuth(undefined)/createBaseQueryWithAuth()/g" \
  {} \;

echo "✅ createBaseQueryWithAuth corrigés"
echo ""

# Étape 2: Liste des patterns à remplacer (chemins qui doivent être relatifs)
echo "📝 Étape 2: Normalisation des chemins d'endpoints..."

# Pour les fichiers API qui utilisent fetchBaseQuery directement
find ./features -name "*Api.ts" -o -name "*api.ts" | while read -r file; do
  # Vérifier si le fichier utilise fetchBaseQuery avec baseUrl: '/api'
  if grep -q "baseUrl: '/api'" "$file" 2>/dev/null; then
    echo "  📄 Traitement: $file"
    
    # Supprimer /api des query/url dans ce fichier
    sed -i \
      -e "s|query: () => '/api/\([^']*\)'|query: () => '/\1'|g" \
      -e "s|url: '/api/\([^']*\)'|url: '/\1'|g" \
      -e "s|return '/api/\([^']*\)'|return '/\1'|g" \
      -e "s|return \`/api/\([^\`]*\)\`|return \`/\1\`|g" \
      "$file"
  fi
done

echo "✅ Endpoints normalisés"
echo ""

# Étape 3: Vérification des duplications restantes
echo "🔍 Étape 3: Vérification des duplications /api/api/..."
duplicates=$(grep -r "/api/api/" . --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)

if [ "$duplicates" -gt 0 ]; then
  echo "⚠️  $duplicates duplications détectées :"
  grep -rn "/api/api/" . --include="*.ts" --include="*.tsx" 2>/dev/null | head -10
  echo ""
  echo "Correction manuelle requise pour ces cas"
else
  echo "✅ Aucune duplication détectée"
fi

echo ""

# Étape 4: Rapport final
echo "📊 Rapport final"
echo "================"
echo ""

# Compter les fichiers modifiés
total_api_files=$(find ./features -name "*Api.ts" -o -name "*api.ts" | wc -l)
echo "✅ $total_api_files fichiers API traités"

# Vérifier les baseQuery corrects
correct_basequery=$(grep -r "createBaseQueryWithAuth()" . --include="*.ts" | wc -l)
echo "✅ $correct_basequery createBaseQueryWithAuth() corrects"

# Endpoints potentiellement non conformes
non_conformes=$(grep -r "'/\(auth\|iam\|users\|profiles\)/" . --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "'/api/" | grep -v "//" | grep -v "path=" | wc -l)
echo "⚠️  $non_conformes endpoints potentiellement non conformes (nécessitent vérification)"

echo ""
echo "🎉 Migration terminée !"
echo ""
echo "Prochaines étapes:"
echo "  1. Exécuter: npm run lint"
echo "  2. Exécuter: npm run test:api-endpoints"
echo "  3. Tester l'application manuellement"
echo "  4. Commit les changements"

#!/usr/bin/env python3
"""
Script spécifique pour corriger ValidationsPage.tsx
"""
import re

def fix_validations_page():
    """Corriger ValidationsPage.tsx"""
    file_path = "/app/apps/web/src/features/admin/pages/ValidationsPage.tsx"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns de remplacement spécifiques
    replacements = [
        # Comparaisons status
        (r"v\.status === 'pending'", "v.status === validationStatusesConfig.pending"),
        (r"validation\.status === 'pending'", "validation.status === validationStatusesConfig.pending"),
        (r"status === 'pending'", "status === validationStatusesConfig.pending"),
        (r"status === 'approved'", "status === validationStatusesConfig.approved"),
        (r"status === 'rejected'", "status === validationStatusesConfig.rejected"),
        
        # Comparaisons validation_type
        (r"validation_type === 'interim'", "validation_type === validationTypesConfig.interim"),
        (r"validation_type === 'company'", "validation_type === validationTypesConfig.company"),
        (r"validation_type === 'collaborator'", "validation_type === validationTypesConfig.collaborator"),
        (r"validation\.validation_type === 'interim'", "validation.validation_type === validationTypesConfig.interim"),
        (r"validation\.validation_type === 'company'", "validation.validation_type === validationTypesConfig.company"),
        (r"validation\.validation_type === 'collaborator'", "validation.validation_type === validationTypesConfig.collaborator"),
        (r"selectedValidation\?\.validation_type === 'interim'", "selectedValidation?.validation_type === validationTypesConfig.interim"),
        (r"selectedValidation\?\.validation_type === 'company'", "selectedValidation?.validation_type === validationTypesConfig.company"),
        (r"selectedValidation\?\.validation_type === 'collaborator'", "selectedValidation?.validation_type === validationTypesConfig.collaborator"),
    ]
    
    # Appliquer les remplacements
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Sauvegarder si modifié
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Compter les changements
        changes = sum(1 for p, r in replacements if re.search(p, original_content))
        print(f"✅ {changes} corrections appliquées à ValidationsPage.tsx")
    else:
        print("ℹ️  Aucune correction nécessaire")

if __name__ == "__main__":
    fix_validations_page()

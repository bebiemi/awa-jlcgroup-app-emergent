#!/usr/bin/env python3
"""
Script pour corriger les fichiers frontend critiques restants
"""
import re
from pathlib import Path

def fix_file(file_path: Path, replacements: dict) -> int:
    """Appliquer des remplacements à un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        fixes = 0
        
        for pattern, replacement in replacements.items():
            matches = len(re.findall(pattern, content))
            if matches > 0:
                content = re.sub(pattern, replacement, content)
                fixes += matches
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes
        
        return 0
    except Exception as e:
        print(f"  ⚠️  Erreur: {e}")
        return 0

def main():
    """Corriger les fichiers frontend critiques"""
    print("🔧 Correction des fichiers frontend critiques\n")
    
    base_path = Path("/app/apps/web/src")
    
    files_to_fix = {
        "features/auth/pages/RegisterPage.tsx": {
            r"value=\"interim\"": "value={roles.interim}",
            r"value=\"company\"": "value={roles.company}",
            r"value=\"agency\"": "value={roles.agency}",
            r"'interim'": "roles.interim",
            r"'company'": "roles.company",
            r"'agency'": "roles.agency",
        },
        "features/auth/pages/RoleSelectionPage.tsx": {
            r"onClick=\{\(\) => selectRole\('interim'\)\}": "onClick={() => selectRole(roles.interim)}",
            r"onClick=\{\(\) => selectRole\('company'\)\}": "onClick={() => selectRole(roles.company)}",
            r"onClick=\{\(\) => selectRole\('agency'\)\}": "onClick={() => selectRole(roles.agency)}",
            r"selectRole\('interim'\)": "selectRole(roles.interim)",
            r"selectRole\('company'\)": "selectRole(roles.company)",
            r"selectRole\('agency'\)": "selectRole(roles.agency)",
        },
        "components/Sidebar.tsx": {
            r"user\?\.roles\.includes\('admin'\)": "user?.roles.includes(roles.admin)",
            r"user\?\.roles\.includes\('super_admin'\)": "user?.roles.includes(roles.super_admin)",
            r"user\?\.roles\.includes\('company'\)": "user?.roles.includes(roles.company)",
            r"user\?\.roles\.includes\('interim'\)": "user?.roles.includes(roles.interim)",
            r"user\?\.roles\.includes\('commercial'\)": "user?.roles.includes(roles.commercial)",
            r"user\?\.roles\.includes\('agency'\)": "user?.roles.includes(roles.agency)",
            r"user\.roles\.includes\('admin'\)": "user.roles.includes(roles.admin)",
            r"user\.roles\.includes\('super_admin'\)": "user.roles.includes(roles.super_admin)",
            r"user\.roles\.includes\('company'\)": "user.roles.includes(roles.company)",
            r"user\.roles\.includes\('interim'\)": "user.roles.includes(roles.interim)",
        }
    }
    
    # Imports à ajouter
    imports_needed = {
        "features/auth/pages/RegisterPage.tsx": "import { useRoles } from '@/hooks/useAppConfig'",
        "features/auth/pages/RoleSelectionPage.tsx": "import { useRoles } from '@/hooks/useAppConfig'",
        "components/Sidebar.tsx": "import { useRoles } from '@/hooks/useAppConfig'",
    }
    
    # Hook call à ajouter
    hook_calls = {
        "features/auth/pages/RegisterPage.tsx": "  const roles = useRoles()\n",
        "features/auth/pages/RoleSelectionPage.tsx": "  const roles = useRoles()\n",
        "components/Sidebar.tsx": "  const roles = useRoles()\n",
    }
    
    total_fixes = 0
    
    for rel_path, replacements in files_to_fix.items():
        file_path = base_path / rel_path
        
        if not file_path.exists():
            print(f"❌ {rel_path} - Fichier introuvable")
            continue
        
        print(f"📄 {rel_path}")
        
        # Appliquer les remplacements
        fixes = fix_file(file_path, replacements)
        
        if fixes > 0:
            # Ajouter l'import si nécessaire
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import_line = imports_needed.get(rel_path)
            if import_line and import_line not in content:
                # Trouver la dernière ligne d'import
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                
                lines.insert(insert_index, import_line)
                content = '\n'.join(lines)
            
            # Ajouter le hook call si nécessaire
            hook_call = hook_calls.get(rel_path)
            if hook_call and 'const roles = useRoles()' not in content:
                # Trouver la première ligne de fonction component
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'export default function' in line or 'function' in line and '{' in line:
                        # Insérer après la ligne de déclaration de fonction
                        insert_index = i + 1
                        lines.insert(insert_index, hook_call)
                        content = '\n'.join(lines)
                        break
            
            # Sauvegarder
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ {fixes} corrections appliquées")
            total_fixes += fixes
        else:
            print(f"  ℹ️  Aucune correction nécessaire")
    
    print(f"\n✅ Total: {total_fixes} corrections appliquées")

if __name__ == "__main__":
    main()

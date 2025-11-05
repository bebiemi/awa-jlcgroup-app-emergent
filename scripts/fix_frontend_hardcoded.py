#!/usr/bin/env python3
"""
Script pour corriger les valeurs en dur dans le frontend
"""
import re
from pathlib import Path
from typing import List, Tuple

class FrontendFixer:
    """Correcteur pour le frontend React/TypeScript"""
    
    def __init__(self):
        self.root_dir = Path("/app/apps/web/src")
        self.fixes_applied = 0
        
        # Patterns de remplacement pour TypeScript/React
        self.replacements = {
            # Rôles dans comparaisons
            r"'admin'(?!')": "roles.admin",
            r"'super_admin'(?!')": "roles.super_admin",
            r"'company'(?!')": "roles.company",
            r"'interim'(?!')": "roles.interim",
            r"'commercial'(?!')": "roles.commercial",
            r"'agency'(?!')": "roles.agency",
            r"'validator'(?!')": "roles.validator",
            
            # Arrays de rôles
            r"\['admin', 'super_admin'\]": "[roles.admin, roles.super_admin]",
            r"\['admin', 'super_admin', 'commercial'\]": "[roles.admin, roles.super_admin, roles.commercial]",
            
            # Statuts
            r"'active'(?!')": "userStatuses.active",
            r"'pending'(?!')": "userStatuses.pending",
            r"'suspended'(?!')": "userStatuses.suspended",
        }
    
    def should_skip_line(self, line: str) -> bool:
        """Lignes à ignorer"""
        skip_patterns = [
            r'^\s*//',  # Commentaires
            r'^\s*/\*',  # Commentaires multilignes
            r'console\.',  # Console logs
            r'label\s*=',  # Labels UI
            r'title\s*=',  # Titres
            r'placeholder\s*=',  # Placeholders
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def needs_hook_import(self, content: str, hook_name: str) -> bool:
        """Vérifie si le hook doit être importé"""
        return hook_name not in content and "roles." in content or "userStatuses." in content
    
    def fix_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Corriger un fichier"""
        changes = []
        fixes_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            lines = content.split('\n')
            
            # Appliquer les remplacements
            new_lines = []
            for line_num, line in enumerate(lines, 1):
                if self.should_skip_line(line):
                    new_lines.append(line)
                    continue
                
                original_line = line
                for pattern, replacement in self.replacements.items():
                    matches = list(re.finditer(pattern, line))
                    if matches:
                        line = re.sub(pattern, replacement, line)
                        if line != original_line:
                            fixes_count += 1
                            changes.append(f"Line {line_num}: Replaced value")
                            original_line = line
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            # Ajouter l'import du hook si nécessaire
            if fixes_count > 0 and self.needs_hook_import(original_content, 'useAppConfig'):
                # Trouver où insérer l'import
                import_pattern = r"import .+ from ['\"]"
                matches = list(re.finditer(import_pattern, content))
                
                if matches:
                    # Insérer après le dernier import
                    last_import = matches[-1]
                    insert_pos = content.find('\n', last_import.end())
                    
                    new_import = "\nimport { useRoles, useUserStatuses, useAppConfig } from '@/hooks/useAppConfig'"
                    content = content[:insert_pos] + new_import + content[insert_pos:]
                    changes.append("Added hook import")
            
            # Sauvegarder si modifié
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return fixes_count, changes
        
        except Exception as e:
            print(f"⚠️  Erreur: {e}")
            return 0, []
    
    def fix_frontend(self):
        """Corriger les fichiers frontend"""
        print("🔧 Correction du frontend (TypeScript/React)...")
        
        # Fichiers prioritaires
        priority_files = [
            "App.tsx",
            "features/admin/pages/ValidationsPage.tsx",
            "features/auth/pages/RegisterPage.tsx",
            "features/auth/pages/RoleSelectionPage.tsx",
            "components/Sidebar.tsx",
        ]
        
        for rel_path in priority_files:
            file_path = self.root_dir / rel_path
            if file_path.exists():
                print(f"\n  📄 {rel_path}")
                fixes, changes = self.fix_file(file_path)
                self.fixes_applied += fixes
                if fixes > 0:
                    print(f"    ✅ {fixes} corrections")
                else:
                    print(f"    ℹ️  Aucune correction")
    
    def run(self):
        """Exécuter"""
        print("🚀 Correction des valeurs en dur - Frontend\n")
        self.fix_frontend()
        print(f"\n✅ Total: {self.fixes_applied} corrections appliquées")

if __name__ == "__main__":
    fixer = FrontendFixer()
    fixer.run()

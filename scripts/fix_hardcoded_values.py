#!/usr/bin/env python3
"""
Script automatisé pour corriger les valeurs en dur
Remplace les valeurs hardcodées par des appels à config
"""
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

class HardcodedValuesFixer:
    """Correcteur automatisé de valeurs en dur"""
    
    def __init__(self, root_dir: str = "/app"):
        self.root_dir = Path(root_dir)
        self.fixes_applied = 0
        
        # Mappings de remplacement - Ordre important !
        self.replacements = {
            # Listes de rôles (à traiter en premier pour éviter les remplacements partiels)
            r'\["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"\]': 'cfg.get_all_roles()',
            r'\["admin", "super_admin", "commercial"\]': 'cfg.get_validator_roles()',
            r'\["admin", "super_admin", "company", "commercial"\]': 'cfg.get_mission_permission_roles("create")',
            r'\["admin", "super_admin"\]': '[cfg.get_admin_role(), cfg.get_super_admin_role()]',
            
            # Listes de statuts
            r'\["active", "pending", "suspended", "deleted", "blocked"\]': 'cfg.get_all_user_statuses()',
            r'\["active", "pending", "suspended", "deleted"\]': 'cfg.get_all_user_statuses()',
            
            # Rôles individuels dans les comparaisons "in"
            r'"admin"\s+in\s+user_roles': 'cfg.get_admin_role() in user_roles',
            r'"super_admin"\s+in\s+user_roles': 'cfg.get_super_admin_role() in user_roles',
            r'"company"\s+in\s+user_roles': 'cfg.get_company_role() in user_roles',
            r'"interim"\s+in\s+user_roles': 'cfg.get_interim_role() in user_roles',
            r'"commercial"\s+in\s+user_roles': 'cfg.get_commercial_role() in user_roles',
            r'"agency"\s+in\s+user_roles': 'cfg.get_agency_role() in user_roles',
            
            # Rôles individuels (si pas déjà remplacés)
            r'"admin"(?!\s*:)(?!\.)': 'cfg.get_admin_role()',
            r'"super_admin"(?!\s*:)(?!\.)': 'cfg.get_super_admin_role()',
            r'"company"(?!\s*:)(?!\.)': 'cfg.get_company_role()',
            r'"interim"(?!\s*:)(?!\.)': 'cfg.get_interim_role()',
            r'"commercial"(?!\s*:)(?!\.)': 'cfg.get_commercial_role()',
            r'"agency"(?!\s*:)(?!\.)': 'cfg.get_agency_role()',
            r'"validator"(?!\s*:)(?!\.)': 'cfg.get_validator_role()',
            
            # Statuts utilisateur dans comparaisons
            r'== "active"': '== cfg.get_active_status()',
            r'!= "active"': '!= cfg.get_active_status()',
            r'== "pending"': '== cfg.get_pending_status()',
            r'!= "pending"': '!= cfg.get_pending_status()',
            r'== "suspended"': '== cfg.get_suspended_status()',
            r'!= "suspended"': '!= cfg.get_suspended_status()',
            r'== "deleted"': '== cfg.get_deleted_status()',
            
            # Statuts dans accès direct (status: "pending")
            r'"status":\s*"pending"': '"status": cfg.get_pending_status()',
            r'"status":\s*"active"': '"status": cfg.get_active_status()',
            
            # Types de validation
            r'"validation_type":\s*"interim"': '"validation_type": cfg.get_validation_type("interim")',
            r'"validation_type":\s*"company"': '"validation_type": cfg.get_validation_type("company")',
        }
    
    def should_skip_line(self, line: str) -> bool:
        """Détermine si une ligne doit être ignorée"""
        skip_patterns = [
            r'^\s*#',  # Commentaires
            r'^\s*"""',  # Docstrings
            r'^\s*\'\'\'',  # Docstrings
            r'print\(',  # Prints
            r'logger\.',  # Logs
            r'log\(',  # Logs
            r'detail\s*=\s*"',  # Messages d'erreur (on les garde pour l'instant)
            r'description\s*=\s*"',  # Descriptions
            r'message\s*=\s*"',  # Messages
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def fix_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Corriger un fichier"""
        changes = []
        fixes_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            lines = content.split('\n')
            
            # Vérifier si le fichier importe déjà cfg
            has_cfg_import = 'from awana_auth.utils.config_helpers import cfg' in content
            
            # Appliquer les remplacements ligne par ligne pour plus de contrôle
            new_lines = []
            for line_num, line in enumerate(lines, 1):
                if self.should_skip_line(line):
                    new_lines.append(line)
                    continue
                
                original_line = line
                for pattern, replacement in self.replacements.items():
                    if re.search(pattern, line):
                        line = re.sub(pattern, replacement, line)
                        if line != original_line:
                            fixes_count += 1
                            changes.append(f"Line {line_num}: {original_line.strip()} → {line.strip()}")
                            original_line = line
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            # Si des changements ont été faits et que cfg n'est pas importé, ajouter l'import
            if fixes_count > 0 and not has_cfg_import and file_path.suffix == '.py':
                # Trouver où insérer l'import
                lines = content.split('\n')
                insert_index = 0
                
                # Chercher la dernière ligne d'import
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                
                # Insérer l'import
                lines.insert(insert_index, 'from awana_auth.utils.config_helpers import cfg')
                content = '\n'.join(lines)
                changes.append(f"Added import: from awana_auth.utils.config_helpers import cfg")
            
            # Sauvegarder si des changements ont été faits
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return fixes_count, changes
        
        except Exception as e:
            print(f"⚠️  Erreur lors de la correction de {file_path}: {e}")
            return 0, []
    
    def fix_backend(self):
        """Corriger le backend Python"""
        print("🔧 Correction du backend (Python)...")
        backend_dir = self.root_dir / "auth-microservice"
        
        # Fichiers critiques à corriger en priorité
        priority_files = [
            "awana_auth_routes.py",
            "mission_routes.py",
            "validation_routes.py",
            "profile_routes.py",
            "google_auth_routes.py",
            "security_routes.py",
            "mfa_routes.py",
            "document_routes.py",
            "location_routes.py",
        ]
        
        total_files = 0
        for filename in priority_files:
            file_path = backend_dir / filename
            if file_path.exists():
                total_files += 1
                print(f"\n  📄 {filename}")
                fixes, changes = self.fix_file(file_path)
                self.fixes_applied += fixes
                if fixes > 0:
                    print(f"    ✅ {fixes} corrections appliquées")
                    # Afficher quelques exemples
                    for change in changes[:3]:
                        print(f"       {change}")
                    if len(changes) > 3:
                        print(f"       ... et {len(changes) - 3} autres")
                else:
                    print(f"    ℹ️  Aucune correction nécessaire")
        
        print(f"\n  📊 Total: {total_files} fichiers traités")
    
    def generate_report(self) -> str:
        """Générer un rapport de correction"""
        return f"""
🎯 RAPPORT DE CORRECTION AUTOMATIQUE
{'='*60}
Total de corrections appliquées: {self.fixes_applied}

✅ Les valeurs en dur critiques ont été remplacées par des appels à cfg.*
✅ Les imports nécessaires ont été ajoutés automatiquement

📋 Prochaines étapes:
1. Tester les corrections avec: python scripts/test_config.py
2. Redémarrer les services: sudo supervisorctl restart all
3. Vérifier les logs pour détecter d'éventuelles erreurs
4. Lancer l'audit à nouveau: python scripts/audit_hardcoded_values.py
"""
    
    def run(self):
        """Exécuter la correction"""
        print("🚀 Démarrage de la correction automatique des valeurs en dur...")
        print("")
        
        self.fix_backend()
        
        print("")
        print(self.generate_report())


def main():
    """Point d'entrée principal"""
    fixer = HardcodedValuesFixer()
    fixer.run()


if __name__ == "__main__":
    main()

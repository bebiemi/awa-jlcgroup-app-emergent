#!/usr/bin/env python3
"""
Script d'audit complet pour identifier toutes les valeurs en dur dans le codebase
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class HardcodedValue:
    """Représente une valeur en dur trouvée"""
    file_path: str
    line_number: int
    line_content: str
    value: str
    category: str
    severity: str  # critical, high, medium, low
    context: str

class HardcodedValuesAuditor:
    """Auditeur de valeurs en dur"""
    
    def __init__(self, root_dir: str = "/app"):
        self.root_dir = Path(root_dir)
        self.findings: List[HardcodedValue] = []
        
        # Patterns à rechercher
        self.patterns = {
            # Rôles
            'roles': [
                r'["\']admin["\']',
                r'["\']super_admin["\']',
                r'["\']company["\']',
                r'["\']interim["\']',
                r'["\']agency["\']',
                r'["\']commercial["\']',
                r'["\']validator["\']',
            ],
            
            # Statuts utilisateur
            'user_status': [
                r'["\']active["\']',
                r'["\']pending["\']',
                r'["\']suspended["\']',
                r'["\']deleted["\']',
                r'["\']blocked["\']',
            ],
            
            # Statuts mission
            'mission_status': [
                r'["\']draft["\']',
                r'["\']published["\']',
                r'["\']closed["\']',
                r'["\']cancelled["\']',
                r'["\']archived["\']',
            ],
            
            # Statuts application
            'application_status': [
                r'["\']submitted["\']',
                r'["\']review["\']',
                r'["\']interview_scheduled["\']',
                r'["\']interviewed["\']',
                r'["\']selected["\']',
                r'["\']rejected["\']',
                r'["\']medical_pending["\']',
                r'["\']medical_completed["\']',
                r'["\']contract_pending["\']',
                r'["\']contract_signed["\']',
            ],
            
            # Types de validation
            'validation_types': [
                r'["\']interim["\']',
                r'["\']company["\']',
                r'["\']collaborator["\']',
            ],
            
            # Types de document
            'document_types': [
                r'["\']cv["\']',
                r'["\']medical_certificate["\']',
                r'["\']contract["\']',
                r'["\']identity_document["\']',
            ],
            
            # Types de contrat
            'contract_types': [
                r'["\']cdi["\']',
                r'["\']cdd["\']',
                r'["\']interim["\']',
                r'["\']freelance["\']',
            ],
            
            # Délais (en jours)
            'delays_days': [
                r'delay.*=\s*\d+',
                r'days\s*=\s*\d+',
                r'expire.*\d+',
            ],
            
            # Limites numériques
            'numeric_limits': [
                r'max_.*=\s*\d+',
                r'min_.*=\s*\d+',
                r'limit\s*=\s*\d+',
            ],
            
            # Messages et libellés
            'messages': [
                r'message\s*=\s*["\'].+["\']',
                r'detail\s*=\s*["\'].+["\']',
                r'description\s*=\s*["\'].+["\']',
            ],
        }
        
        # Patterns à exclure (false positives)
        self.exclude_patterns = [
            r'#.*',  # Commentaires
            r'""".*"""',  # Docstrings
            r"'''.*'''",  # Docstrings
            r'log\(',  # Logs
            r'print\(',  # Prints
            r'test_',  # Fichiers de test
        ]
    
    def should_skip_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être ignoré"""
        skip_dirs = {
            '__pycache__', 'node_modules', '.git', 'dist', 'build',
            'venv', '.venv', 'coverage', '.pytest_cache', 'migrations'
        }
        skip_files = {
            'test_', 'spec.', '.test.', '.spec.',
            'audit_hardcoded_values.py',  # Ce script lui-même
        }
        
        # Vérifier les répertoires
        for part in file_path.parts:
            if part in skip_dirs:
                return True
        
        # Vérifier les noms de fichiers
        for pattern in skip_files:
            if pattern in file_path.name:
                return True
        
        return False
    
    def is_excluded_line(self, line: str) -> bool:
        """Détermine si une ligne doit être exclue"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def scan_file(self, file_path: Path):
        """Scanner un fichier pour les valeurs en dur"""
        if self.should_skip_file(file_path):
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                # Ignorer les lignes exclues
                if self.is_excluded_line(line):
                    continue
                
                # Chercher chaque pattern
                for category, patterns in self.patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Déterminer la sévérité
                            severity = self.determine_severity(category, line)
                            
                            self.findings.append(HardcodedValue(
                                file_path=str(file_path.relative_to(self.root_dir)),
                                line_number=line_num,
                                line_content=line.strip(),
                                value=match.group(),
                                category=category,
                                severity=severity,
                                context=self.extract_context(lines, line_num)
                            ))
        
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {file_path}: {e}")
    
    def determine_severity(self, category: str, line: str) -> str:
        """Détermine la sévérité d'une valeur en dur"""
        # Critique: rôles, statuts de workflow, permissions
        if category in ['roles', 'application_status', 'validation_types']:
            return 'critical'
        
        # Haute: statuts utilisateur, statuts mission
        if category in ['user_status', 'mission_status']:
            return 'high'
        
        # Moyenne: types de document, contrats, délais
        if category in ['document_types', 'contract_types', 'delays_days']:
            return 'medium'
        
        # Basse: limites numériques, messages
        if category in ['numeric_limits', 'messages']:
            return 'low'
        
        return 'medium'
    
    def extract_context(self, lines: List[str], line_num: int, context_lines: int = 2) -> str:
        """Extrait le contexte autour d'une ligne"""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        context = lines[start:end]
        return '\n'.join([f"{start + i + 1}: {l.rstrip()}" for i, l in enumerate(context)])
    
    def scan_directory(self, directory: Path, extensions: Set[str]):
        """Scanner un répertoire récursivement"""
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                self.scan_file(file_path)
    
    def scan_backend(self):
        """Scanner le backend Python"""
        print("🔍 Scanning backend (Python)...")
        backend_dir = self.root_dir / "auth-microservice"
        if backend_dir.exists():
            self.scan_directory(backend_dir, {'.py'})
    
    def scan_frontend(self):
        """Scanner le frontend TypeScript/React"""
        print("🔍 Scanning frontend (TypeScript/React)...")
        frontend_dir = self.root_dir / "apps" / "web" / "src"
        if frontend_dir.exists():
            self.scan_directory(frontend_dir, {'.ts', '.tsx', '.js', '.jsx'})
    
    def generate_report(self) -> str:
        """Générer un rapport d'audit"""
        if not self.findings:
            return "✅ Aucune valeur en dur trouvée!"
        
        # Grouper par sévérité
        by_severity = defaultdict(list)
        for finding in self.findings:
            by_severity[finding.severity].append(finding)
        
        # Grouper par catégorie
        by_category = defaultdict(list)
        for finding in self.findings:
            by_category[finding.category].append(finding)
        
        # Grouper par fichier
        by_file = defaultdict(list)
        for finding in self.findings:
            by_file[finding.file_path].append(finding)
        
        report = []
        report.append("=" * 80)
        report.append("🔍 RAPPORT D'AUDIT - VALEURS EN DUR")
        report.append("=" * 80)
        report.append("")
        
        # Résumé
        report.append("📊 RÉSUMÉ")
        report.append("-" * 80)
        report.append(f"Total de valeurs en dur trouvées: {len(self.findings)}")
        report.append("")
        report.append("Par sévérité:")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                report.append(f"  {emoji} {severity.upper()}: {count}")
        report.append("")
        
        report.append("Par catégorie:")
        for category, findings in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            report.append(f"  • {category}: {len(findings)}")
        report.append("")
        
        report.append("Par fichier (top 10):")
        sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for file_path, findings in sorted_files:
            report.append(f"  • {file_path}: {len(findings)}")
        report.append("")
        report.append("")
        
        # Détails par sévérité
        for severity in ['critical', 'high', 'medium', 'low']:
            findings_list = by_severity[severity]
            if not findings_list:
                continue
            
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
            report.append(f"{emoji} SÉVÉRITÉ: {severity.upper()} ({len(findings_list)} occurrences)")
            report.append("=" * 80)
            report.append("")
            
            # Grouper par fichier pour cette sévérité
            by_file_severity = defaultdict(list)
            for finding in findings_list:
                by_file_severity[finding.file_path].append(finding)
            
            for file_path, file_findings in sorted(by_file_severity.items()):
                report.append(f"📄 {file_path}")
                report.append("-" * 80)
                
                for finding in file_findings:
                    report.append(f"  Ligne {finding.line_number} | [{finding.category}]")
                    report.append(f"  Code: {finding.line_content}")
                    report.append(f"  Valeur: {finding.value}")
                    report.append("")
                
                report.append("")
        
        return '\n'.join(report)
    
    def generate_markdown_report(self) -> str:
        """Générer un rapport au format Markdown"""
        if not self.findings:
            return "# ✅ Audit des Valeurs en Dur\n\nAucune valeur en dur trouvée!"
        
        # Grouper par sévérité
        by_severity = defaultdict(list)
        for finding in self.findings:
            by_severity[finding.severity].append(finding)
        
        # Grouper par catégorie
        by_category = defaultdict(list)
        for finding in self.findings:
            by_category[finding.category].append(finding)
        
        # Grouper par fichier
        by_file = defaultdict(list)
        for finding in self.findings:
            by_file[finding.file_path].append(finding)
        
        md = []
        md.append("# 🔍 Audit des Valeurs en Dur - Rapport Complet")
        md.append("")
        md.append(f"**Date**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        md.append("---")
        md.append("")
        
        # Résumé exécutif
        md.append("## 📊 Résumé Exécutif")
        md.append("")
        md.append(f"**Total de valeurs en dur trouvées**: {len(self.findings)}")
        md.append("")
        
        md.append("### Par Sévérité")
        md.append("")
        md.append("| Sévérité | Nombre | Pourcentage |")
        md.append("|----------|--------|-------------|")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                pct = (count / len(self.findings)) * 100
                md.append(f"| {emoji} {severity.upper()} | {count} | {pct:.1f}% |")
        md.append("")
        
        md.append("### Par Catégorie")
        md.append("")
        md.append("| Catégorie | Nombre |")
        md.append("|-----------|--------|")
        for category, findings in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            md.append(f"| {category} | {len(findings)} |")
        md.append("")
        
        md.append("### Top 15 Fichiers")
        md.append("")
        md.append("| Fichier | Nombre de valeurs en dur |")
        md.append("|---------|--------------------------|")
        sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:15]
        for file_path, findings in sorted_files:
            md.append(f"| `{file_path}` | {len(findings)} |")
        md.append("")
        md.append("---")
        md.append("")
        
        # Détails par sévérité
        for severity in ['critical', 'high', 'medium', 'low']:
            findings_list = by_severity[severity]
            if not findings_list:
                continue
            
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
            md.append(f"## {emoji} Sévérité: {severity.upper()}")
            md.append("")
            md.append(f"**Total**: {len(findings_list)} occurrences")
            md.append("")
            
            # Grouper par fichier
            by_file_severity = defaultdict(list)
            for finding in findings_list:
                by_file_severity[finding.file_path].append(finding)
            
            for file_path, file_findings in sorted(by_file_severity.items()):
                md.append(f"### 📄 `{file_path}`")
                md.append("")
                
                for i, finding in enumerate(file_findings, 1):
                    md.append(f"**{i}. Ligne {finding.line_number}** | Catégorie: `{finding.category}`")
                    md.append("")
                    md.append("```")
                    md.append(finding.line_content)
                    md.append("```")
                    md.append("")
                    md.append(f"**Valeur en dur**: `{finding.value}`")
                    md.append("")
                
                md.append("")
        
        md.append("---")
        md.append("")
        
        # Recommandations
        md.append("## 💡 Recommandations")
        md.append("")
        md.append("### Priorités de Correction")
        md.append("")
        md.append("1. **🔴 CRITIQUE** - À corriger immédiatement")
        md.append("   - Rôles et permissions")
        md.append("   - Statuts de workflow")
        md.append("   - Types de validation")
        md.append("")
        md.append("2. **🟠 HAUTE** - À corriger dans les 7 jours")
        md.append("   - Statuts utilisateur")
        md.append("   - Statuts mission")
        md.append("")
        md.append("3. **🟡 MOYENNE** - À corriger dans les 14 jours")
        md.append("   - Types de document")
        md.append("   - Types de contrat")
        md.append("   - Délais configurables")
        md.append("")
        md.append("4. **🟢 BASSE** - À corriger progressivement")
        md.append("   - Limites numériques")
        md.append("   - Messages et libellés")
        md.append("")
        
        md.append("### Actions Recommandées")
        md.append("")
        md.append("1. Ajouter les valeurs dans les fichiers de configuration YAML appropriés")
        md.append("2. Remplacer chaque valeur en dur par `config.get(\"path.to.value\")`")
        md.append("3. Ajouter validation pour les valeurs critiques")
        md.append("4. Tester après chaque remplacement")
        md.append("")
        
        return '\n'.join(md)
    
    def run_audit(self):
        """Exécuter l'audit complet"""
        print("🚀 Démarrage de l'audit des valeurs en dur...")
        print("")
        
        self.scan_backend()
        self.scan_frontend()
        
        print("")
        print(f"✅ Audit terminé: {len(self.findings)} valeurs en dur trouvées")
        print("")


def main():
    """Point d'entrée principal"""
    auditor = HardcodedValuesAuditor()
    auditor.run_audit()
    
    # Générer le rapport texte
    report = auditor.generate_report()
    print(report)
    
    # Sauvegarder le rapport Markdown
    md_report = auditor.generate_markdown_report()
    output_file = Path("/app/docs/AUDIT_VALEURS_EN_DUR.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"📄 Rapport détaillé sauvegardé: {output_file}")
    print("")
    
    # Statistiques finales
    by_severity = defaultdict(int)
    for finding in auditor.findings:
        by_severity[finding.severity] += 1
    
    print("=" * 80)
    print("📊 STATISTIQUES FINALES")
    print("=" * 80)
    print(f"🔴 CRITIQUE: {by_severity['critical']}")
    print(f"🟠 HAUTE: {by_severity['high']}")
    print(f"🟡 MOYENNE: {by_severity['medium']}")
    print(f"🟢 BASSE: {by_severity['low']}")
    print(f"📊 TOTAL: {len(auditor.findings)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

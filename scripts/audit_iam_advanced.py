#!/usr/bin/env python3
"""
AUDIT IAM EXPERT - Analyse Approfondie de la Sécurité et Cohérence IAM
Analyse complète des endpoints avec vérification du modèle IAM centralisé
"""
import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from collections import defaultdict

class IAMExpertAuditor:
    def __init__(self):
        self.endpoints = []
        self.permissions_db = {}
        self.profiles_db = {}
        self.bundles_db = {}
        self.issues = []
        self.hardcoded_perms = []
        
        # Patterns de détection
        self.ROUTE_PATTERN = r'@(\w+)\.(get|post|put|patch|delete|head|options)\s*\(\s*["\']([^"\']+)["\']'
        self.PERMISSION_PATTERNS = {
            'single': r'require_permission\s*\(\s*["\']([^"\']+)["\']',
            'any': r'require_any_permission\s*\(\s*\[([^\]]+)\]',
            'all': r'require_all_permissions\s*\(\s*\[([^\]]+)\]',
            'scope': r'scope\s*=\s*["\']([^"\']+)["\']'
        }
        self.HARDCODE_PATTERN = r'["\'][\w]+\.[\w]+["\']'
        
    async def load_iam_data(self):
        """Charge toutes les données IAM depuis MongoDB"""
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.auth_db
        
        # Permissions
        perms = await db.permissions.find({}, {"_id": 0}).to_list(1000)
        self.permissions_db = {p['code']: p for p in perms}
        print(f"✅ Loaded {len(self.permissions_db)} permissions")
        
        # Profils
        profiles = await db.profiles.find({}, {"_id": 0}).to_list(100)
        self.profiles_db = {p['code']: p for p in profiles}
        print(f"✅ Loaded {len(self.profiles_db)} profiles")
        
        # Bundles
        bundles = await db.permission_bundles.find({}, {"_id": 0}).to_list(100)
        bundles.extend(await db.capability_bundles.find({}, {"_id": 0}).to_list(100))
        self.bundles_db = {b.get('code', b.get('id')): b for b in bundles}
        print(f"✅ Loaded {len(self.bundles_db)} bundles")
    
    def extract_endpoint_details(self, filepath: str) -> List[Dict]:
        """Extrait les détails complets des endpoints"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            endpoints = []
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                route_match = re.search(self.ROUTE_PATTERN, line)
                if route_match:
                    router_name = route_match.group(1)
                    method = route_match.group(2).upper()
                    path = route_match.group(3)
                    
                    # Extraire les détails de la fonction (20 lignes suivantes)
                    func_block = '\n'.join(lines[i:min(i+30, len(lines))])
                    
                    endpoint = {
                        'file': os.path.basename(filepath),
                        'path': path,
                        'method': method,
                        'router': router_name,
                        'line': i + 1,
                        'function': self.extract_function_name(func_block),
                        'params': self.extract_params(func_block),
                        'iam': self.analyze_iam_implementation(func_block),
                        'body_schema': self.extract_body_schema(func_block),
                        'query_params': self.extract_query_params(func_block),
                        'response_model': self.extract_response_model(func_block)
                    }
                    
                    endpoints.append(endpoint)
            
            return endpoints
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return []
    
    def extract_function_name(self, func_block: str) -> str:
        """Extrait le nom de la fonction"""
        match = re.search(r'async\s+def\s+(\w+)|def\s+(\w+)', func_block)
        return match.group(1) or match.group(2) if match else 'unknown'
    
    def extract_params(self, func_block: str) -> List[str]:
        """Extrait les paramètres de la fonction"""
        params = []
        # Chercher les path parameters
        path_params = re.findall(r'\{(\w+)\}', func_block)
        params.extend([f"path:{p}" for p in path_params])
        
        # Chercher les query parameters
        query_params = re.findall(r'(\w+)\s*:\s*Optional\[', func_block)
        params.extend([f"query:{p}" for p in query_params])
        
        return params
    
    def extract_body_schema(self, func_block: str) -> Optional[str]:
        """Extrait le schéma du body"""
        match = re.search(r'(\w+)\s*:\s*(\w+Model|\w+Schema|\w+Request)', func_block)
        return match.group(2) if match else None
    
    def extract_query_params(self, func_block: str) -> List[str]:
        """Extrait les query parameters"""
        params = re.findall(r'Query\s*\(.*?description\s*=\s*["\']([^"\']+)', func_block)
        return params
    
    def extract_response_model(self, func_block: str) -> Optional[str]:
        """Extrait le response_model"""
        match = re.search(r'response_model\s*=\s*(\w+)', func_block)
        return match.group(1) if match else None
    
    def analyze_iam_implementation(self, func_block: str) -> Dict:
        """Analyse l'implémentation IAM complète"""
        iam = {
            'type': 'none',
            'permissions': [],
            'scope': None,
            'auth_required': False,
            'hardcoded': False,
            'policy': None,
            'role_check': None
        }
        
        # Vérifier require_permission
        single_match = re.search(self.PERMISSION_PATTERNS['single'], func_block)
        if single_match:
            perm = single_match.group(1)
            iam['type'] = 'single_permission'
            iam['permissions'] = [perm]
            iam['auth_required'] = True
            
            # Vérifier si hardcodé (permission en dur dans le code)
            if not self.is_permission_from_config(perm):
                iam['hardcoded'] = True
        
        # Vérifier require_any_permission
        any_match = re.search(self.PERMISSION_PATTERNS['any'], func_block)
        if any_match:
            perms_str = any_match.group(1)
            perms = [p.strip().strip('"').strip("'") for p in perms_str.split(',')]
            iam['type'] = 'any_permission'
            iam['permissions'] = perms
            iam['auth_required'] = True
        
        # Vérifier require_all_permissions
        all_match = re.search(self.PERMISSION_PATTERNS['all'], func_block)
        if all_match:
            perms_str = all_match.group(1)
            perms = [p.strip().strip('"').strip("'") for p in perms_str.split(',')]
            iam['type'] = 'all_permissions'
            iam['permissions'] = perms
            iam['auth_required'] = True
        
        # Vérifier scope
        scope_match = re.search(self.PERMISSION_PATTERNS['scope'], func_block)
        if scope_match:
            iam['scope'] = scope_match.group(1)
        
        # Vérifier get_current_user
        if 'get_current_user' in func_block or 'Depends(get_current_user)' in func_block:
            if iam['type'] == 'none':
                iam['type'] = 'auth_only'
            iam['auth_required'] = True
        
        # Vérifier policies
        policy_match = re.search(r'@policy\s*\(\s*["\']([^"\']+)', func_block)
        if policy_match:
            iam['policy'] = policy_match.group(1)
        
        # Vérifier role checks
        role_match = re.search(r'if\s+["\'](\w+)["\'].*in.*roles', func_block)
        if role_match:
            iam['role_check'] = role_match.group(1)
        
        return iam
    
    def is_permission_from_config(self, perm: str) -> bool:
        """Vérifie si une permission vient du config IAM"""
        return perm in self.permissions_db
    
    def categorize_endpoint(self, endpoint: Dict) -> str:
        """Catégorise un endpoint par type de ressource"""
        path = endpoint['path'].lower()
        
        categories = {
            'users': r'/users|/auth/users|/{user_id}',
            'admin': r'/admin',
            'iam': r'/iam/',
            'profiles': r'/profiles',
            'missions': r'/missions',
            'entreprises': r'/entreprises',
            'besoins': r'/besoins',
            'documents': r'/documents',
            'emails': r'/email',
            'config': r'/config',
            'validation': r'/validation',
            'audit': r'/audit'
        }
        
        for category, pattern in categories.items():
            if re.search(pattern, path):
                return category
        
        return 'other'
    
    def suggest_permission(self, endpoint: Dict) -> Dict:
        """Suggère la permission appropriée avec scope"""
        path = endpoint['path']
        method = endpoint['method']
        category = self.categorize_endpoint(endpoint)
        
        # Mapping des méthodes HTTP aux actions
        action_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'edit',
            'DELETE': 'delete'
        }
        
        base_action = action_map.get(method, 'manage')
        
        # Déterminer le scope approprié
        scope = 'all'
        if '{user_id}' in path or '{id}' in path:
            # Routes avec ID peuvent être 'own' ou 'all' selon le contexte
            if 'admin' in path:
                scope = 'all'
            else:
                scope = 'own'  # Ou 'all' selon les besoins
        
        # Construire la permission suggérée
        if category == 'other':
            resource = path.split('/')[1] if '/' in path else 'unknown'
        else:
            resource = category
        
        suggested_perm = f"{resource}.{base_action}"
        
        # Vérifier si elle existe déjà
        if suggested_perm in self.permissions_db:
            perm_data = self.permissions_db[suggested_perm]
            return {
                'permission': suggested_perm,
                'scope': perm_data.get('scope', scope),
                'exists': True,
                'category': perm_data.get('category', resource)
            }
        
        # Chercher des permissions similaires
        similar = self.find_similar_permission(resource, base_action)
        if similar:
            return {
                'permission': similar['code'],
                'scope': similar.get('scope', scope),
                'exists': True,
                'category': similar.get('category', resource),
                'alternative': suggested_perm
            }
        
        # Suggérer une nouvelle permission
        return {
            'permission': suggested_perm,
            'scope': scope,
            'exists': False,
            'category': resource,
            'action': 'CREATE_NEW'
        }
    
    def find_similar_permission(self, resource: str, action: str) -> Optional[Dict]:
        """Trouve une permission similaire"""
        for perm_code, perm_data in self.permissions_db.items():
            if resource in perm_code and action in perm_code:
                return perm_data
        return None
    
    def audit_endpoint(self, endpoint: Dict) -> List[Dict]:
        """Effectue un audit complet d'un endpoint"""
        issues = []
        iam = endpoint['iam']
        path = endpoint['path']
        method = endpoint['method']
        category = self.categorize_endpoint(endpoint)
        
        # Vérifier si l'endpoint est critique
        is_critical = self.is_critical_endpoint(endpoint)
        
        # Issue 1: Endpoint critique non protégé
        if is_critical and iam['type'] == 'none':
            suggestion = self.suggest_permission(endpoint)
            issues.append({
                'severity': 'BLOQUANT',
                'type': 'NO_PROTECTION',
                'endpoint': f"{method} {path}",
                'file': endpoint['file'],
                'line': endpoint['line'],
                'current': 'Aucune protection IAM',
                'expected': f"require_permission('{suggestion['permission']}')",
                'scope_expected': suggestion['scope'],
                'action': f"Ajouter: Depends(require_permission('{suggestion['permission']}', scope='{suggestion['scope']}'))",
                'justification': 'Endpoint critique exposé sans protection',
                'impact': 'SÉCURITÉ - Accès non autorisé possible'
            })
        
        # Issue 2: Permission hardcodée
        if iam['hardcoded']:
            issues.append({
                'severity': 'IMPORTANT',
                'type': 'HARDCODED_PERMISSION',
                'endpoint': f"{method} {path}",
                'file': endpoint['file'],
                'current': f"Permission hardcodée: {iam['permissions']}",
                'expected': 'Permission depuis config IAM',
                'action': f"Créer permission dans iam_config.yaml et relancer init_iam_from_config.py",
                'justification': 'Violation du modèle IAM centralisé',
                'impact': 'MAINTENANCE - Duplication et incohérence'
            })
        
        # Issue 3: Permission inexistante
        for perm in iam['permissions']:
            if perm not in self.permissions_db:
                issues.append({
                    'severity': 'IMPORTANT',
                    'type': 'MISSING_PERMISSION',
                    'endpoint': f"{method} {path}",
                    'file': endpoint['file'],
                    'current': f"Permission référencée mais absente: {perm}",
                    'expected': f"Permission {perm} dans config IAM",
                    'action': f"Ajouter dans /app/config/iam_config.yaml:\n  - code: {perm}\n    name: '...'",
                    'justification': 'Permission référencée mais non définie',
                    'impact': 'BUG - Erreur 500 possible'
                })
        
        # Issue 4: Scope manquant
        if iam['permissions'] and not iam['scope']:
            suggestion = self.suggest_permission(endpoint)
            issues.append({
                'severity': 'MINEUR',
                'type': 'MISSING_SCOPE',
                'endpoint': f"{method} {path}",
                'file': endpoint['file'],
                'current': f"Permission sans scope: {iam['permissions']}",
                'expected': f"scope='{suggestion['scope']}'",
                'action': f"Ajouter: scope='{suggestion['scope']}'",
                'justification': 'Le scope permet de filtrer les données (own/all/company)',
                'impact': 'SÉCURITÉ - Données potentiellement exposées'
            })
        
        # Issue 5: Auth-only sur route de modification
        if method in ['POST', 'PUT', 'PATCH', 'DELETE'] and iam['type'] == 'auth_only':
            suggestion = self.suggest_permission(endpoint)
            issues.append({
                'severity': 'IMPORTANT',
                'type': 'AUTH_ONLY_MODIFICATION',
                'endpoint': f"{method} {path}",
                'file': endpoint['file'],
                'current': 'Authentification seulement (get_current_user)',
                'expected': f"require_permission('{suggestion['permission']}')",
                'action': f"Remplacer get_current_user par require_permission('{suggestion['permission']}')",
                'justification': 'Routes de modification doivent avoir permissions granulaires',
                'impact': 'SECURITE - Controle acces insuffisant'
            })
        
        # Issue 6: Vérification de rôle hardcodée
        if iam['role_check']:
            issues.append({
                'severity': 'IMPORTANT',
                'type': 'HARDCODED_ROLE_CHECK',
                'endpoint': f"{method} {path}",
                'file': endpoint['file'],
                'current': f"Vérification de rôle hardcodée: {iam['role_check']}",
                'expected': 'Utiliser le système de permissions IAM',
                'action': 'Remplacer if role in roles par require_permission',
                'justification': 'Les rôles doivent passer par les permissions IAM',
                'impact': 'ARCHITECTURE - Contournement du modèle IAM'
            })
        
        return issues
    
    def is_critical_endpoint(self, endpoint: Dict) -> bool:
        """Détermine si un endpoint est critique"""
        path = endpoint['path'].lower()
        method = endpoint['method']
        
        critical_patterns = [
            (r'/admin', True),
            (r'/users/.*/password', True),
            (r'/users/.*/profiles', True),
            (r'/users/.*/archive', True),
            (r'/iam/', True),
            (r'/permissions', True),
            (r'/roles', True),
            (r'delete', method == 'DELETE'),
        ]
        
        return any(re.search(pattern, path) if match_all else False 
                   for pattern, match_all in critical_patterns)
    
    def is_public_endpoint(self, endpoint: Dict) -> bool:
        """Détermine si un endpoint peut être public"""
        path = endpoint['path'].lower()
        public_patterns = [
            r'^/health',
            r'^/version',
            r'^/docs',
            r'^/openapi',
            r'^/auth/login',
            r'^/auth/register',
            r'^/auth/forgot-password',
        ]
        return any(re.match(pattern, path) for pattern in public_patterns)
    
    async def run_audit(self):
        """Lance l'audit IAM expert complet"""
        print("=" * 100)
        print("AUDIT IAM EXPERT - ANALYSE APPROFONDIE".center(100))
        print("=" * 100)
        print()
        
        # Charger les données IAM
        await self.load_iam_data()
        print()
        
        # Trouver tous les fichiers de routes
        route_files = []
        auth_path = Path('/app/auth-microservice')
        route_files.extend(auth_path.glob('*routes*.py'))
        
        api_path = Path('/app/apps/api')
        if api_path.exists():
            route_files.extend(api_path.glob('**/*route*.py'))
            route_files.extend(api_path.glob('**/server.py'))
        
        print(f"📁 Analyzing {len(route_files)} route files...")
        print()
        
        # Analyser chaque fichier
        for filepath in route_files:
            endpoints = self.extract_endpoint_details(str(filepath))
            self.endpoints.extend(endpoints)
        
        print(f"✅ Found {len(self.endpoints)} endpoints")
        print()
        
        # Auditer chaque endpoint
        print("🔍 Performing IAM audit...")
        all_issues = []
        for endpoint in self.endpoints:
            issues = self.audit_endpoint(endpoint)
            all_issues.extend(issues)
        
        print(f"✅ Audit complete!")
        print()
        
        # Générer le rapport
        self.generate_comprehensive_report(all_issues)
        
        print(f"\n{'=' * 100}")
        print(f"📊 RÉSULTATS")
        print(f"{'=' * 100}")
        print(f"Total endpoints: {len(self.endpoints)}")
        print(f"Total issues: {len(all_issues)}")
        
        by_severity = defaultdict(int)
        for issue in all_issues:
            by_severity[issue['severity']] += 1
        
        print(f"\nPar sévérité:")
        print(f"  🔴 BLOQUANT: {by_severity['BLOQUANT']}")
        print(f"  🟠 IMPORTANT: {by_severity['IMPORTANT']}")
        print(f"  🟡 MINEUR: {by_severity['MINEUR']}")
        
        print(f"\n📄 Rapports générés:")
        print(f"  - /app/docs/IAM_AUDIT_EXPERT_REPORT.md")
        print(f"  - /app/docs/IAM_CORRECTIONS_IMMEDIATE.md")
        print(f"  - /app/docs/IAM_ENDPOINT_MATRIX.json")
    
    def generate_comprehensive_report(self, issues: List[Dict]):
        """Génère le rapport complet"""
        
        # Rapport principal Markdown
        report = []
        report.append("# 🔒 AUDIT IAM EXPERT - Rapport Complet\n\n")
        report.append(f"**Date:** {asyncio.get_event_loop().time()}\n")
        report.append(f"**Endpoints analysés:** {len(self.endpoints)}\n")
        report.append(f"**Issues détectés:** {len(issues)}\n\n")
        
        # Statistiques
        report.append("## 📊 Vue d'Ensemble\n\n")
        
        protected = sum(1 for e in self.endpoints if e['iam']['type'] not in ['none', 'auth_only'])
        auth_only = sum(1 for e in self.endpoints if e['iam']['type'] == 'auth_only')
        unprotected = sum(1 for e in self.endpoints if e['iam']['type'] == 'none')
        
        report.append(f"### Protection IAM\n")
        report.append(f"- ✅ Endpoints avec permissions IAM: {protected} ({protected/len(self.endpoints)*100:.1f}%)\n")
        report.append(f"- ⚠️  Endpoints avec auth seulement: {auth_only} ({auth_only/len(self.endpoints)*100:.1f}%)\n")
        report.append(f"- ❌ Endpoints non protégés: {unprotected} ({unprotected/len(self.endpoints)*100:.1f}%)\n\n")
        
        # Issues par catégorie
        by_type = defaultdict(list)
        for issue in issues:
            by_type[issue['type']].append(issue)
        
        report.append("### Issues par Type\n\n")
        for issue_type, type_issues in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            report.append(f"- **{issue_type}**: {len(type_issues)}\n")
        report.append("\n")
        
        # Issues BLOQUANTS
        bloquants = [i for i in issues if i['severity'] == 'BLOQUANT']
        if bloquants:
            report.append("## 🔴 ISSUES BLOQUANTS (Action Immédiate Requise)\n\n")
            for issue in bloquants[:20]:
                report.append(f"### {issue['endpoint']}\n")
                report.append(f"**Fichier:** `{issue['file']}` (ligne {issue.get('line', '?')})\n\n")
                report.append(f"**Type:** {issue['type']}\n\n")
                report.append(f"**État actuel:** {issue['current']}\n\n")
                report.append(f"**Attendu:** {issue['expected']}\n\n")
                if 'scope_expected' in issue:
                    report.append(f"**Scope attendu:** `{issue['scope_expected']}`\n\n")
                report.append(f"**Action:**\n```python\n{issue['action']}\n```\n\n")
                report.append(f"**Justification:** {issue['justification']}\n\n")
                report.append(f"**Impact:** {issue['impact']}\n\n")
                report.append("---\n\n")
        
        # Issues IMPORTANTS
        importants = [i for i in issues if i['severity'] == 'IMPORTANT']
        if importants:
            report.append("## 🟠 ISSUES IMPORTANTS\n\n")
            for issue in importants[:30]:
                report.append(f"### {issue['endpoint']}\n")
                report.append(f"**Type:** {issue['type']} | **Fichier:** `{issue['file']}`\n\n")
                report.append(f"**Problème:** {issue['current']}\n\n")
                report.append(f"**Action:** {issue['action']}\n\n")
                report.append("---\n\n")
        
        # Matrice complète des endpoints
        report.append("## 📋 Matrice Complète des Endpoints\n\n")
        report.append("| Endpoint | Méthode | Protection | Permissions | Scope | Criticité | Issue |\n")
        report.append("|----------|---------|------------|-------------|-------|-----------|-------|\n")
        
        # Grouper les endpoints par issues
        endpoints_with_issues = {}
        for issue in issues:
            endpoint_key = issue['endpoint']
            if endpoint_key not in endpoints_with_issues:
                endpoints_with_issues[endpoint_key] = []
            endpoints_with_issues[endpoint_key].append(issue)
        
        # Trier par sévérité
        for endpoint_key, endpoint_issues in sorted(
            endpoints_with_issues.items(),
            key=lambda x: {'BLOQUANT': 3, 'IMPORTANT': 2, 'MINEUR': 1}.get(
                max(i['severity'] for i in x[1]), 0
            ),
            reverse=True
        )[:100]:
            method, path = endpoint_key.split(' ', 1)
            endpoint = next((e for e in self.endpoints if e['path'] == path and e['method'] == method), None)
            
            if endpoint:
                iam = endpoint['iam']
                protection = iam['type']
                perms = ', '.join(iam['permissions']) if iam['permissions'] else '-'
                scope = iam['scope'] or '-'
                severity = max(endpoint_issues, key=lambda x: {'BLOQUANT': 3, 'IMPORTANT': 2, 'MINEUR': 1}.get(x['severity'], 0))['severity']
                severity_icon = {'BLOQUANT': '🔴', 'IMPORTANT': '🟠', 'MINEUR': '🟡'}.get(severity, '⚪')
                issue_types = ', '.join(set(i['type'] for i in endpoint_issues))
                
                report.append(f"| `{path}` | {method} | {protection} | {perms} | {scope} | {severity_icon} {severity} | {issue_types} |\n")
        
        # Sauvegarder le rapport
        report_path = '/app/docs/IAM_AUDIT_EXPERT_REPORT.md'
        os.makedirs('/app/docs', exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(''.join(report))
        
        # Générer le fichier de corrections immédiates
        self.generate_immediate_actions(bloquants + importants[:10])
        
        # Générer la matrice JSON pour traitement automatique
        self.generate_endpoint_matrix()
    
    def generate_immediate_actions(self, critical_issues: List[Dict]):
        """Génère le fichier d'actions immédiates"""
        actions = []
        actions.append("# 🚨 ACTIONS IMMÉDIATES - Corrections IAM Obligatoires\n\n")
        actions.append("**PRIORITÉ: CRITIQUE**\n\n")
        actions.append("Ces corrections doivent être appliquées IMMÉDIATEMENT pour éliminer les bugs de permissions.\n\n")
        
        # Grouper par fichier
        by_file = defaultdict(list)
        for issue in critical_issues:
            by_file[issue['file']].append(issue)
        
        actions.append("## 📝 Corrections par Fichier\n\n")
        
        for filepath, file_issues in sorted(by_file.items()):
            actions.append(f"### {filepath}\n\n")
            
            for issue in file_issues:
                actions.append(f"#### {issue['endpoint']}\n")
                actions.append(f"**Ligne:** {issue.get('line', '?')}\n\n")
                actions.append(f"**Action:**\n```python\n{issue['action']}\n```\n\n")
                actions.append(f"**Impact si non corrigé:** {issue['impact']}\n\n")
                actions.append("---\n\n")
        
        # Commandes à exécuter
        actions.append("## 🛠️ Commandes à Exécuter\n\n")
        actions.append("Après avoir appliqué les corrections:\n\n")
        actions.append("```bash\n")
        actions.append("# 1. Relancer l'init IAM pour créer les permissions manquantes\n")
        actions.append("python3 /app/scripts/init_iam_from_config.py\n\n")
        actions.append("# 2. Redémarrer les services\n")
        actions.append("sudo supervisorctl restart auth-microservice backend\n\n")
        actions.append("# 3. Re-lancer l'audit pour vérifier\n")
        actions.append("python3 /app/scripts/audit_iam_advanced.py\n")
        actions.append("```\n")
        
        # Sauvegarder
        actions_path = '/app/docs/IAM_CORRECTIONS_IMMEDIATE.md'
        with open(actions_path, 'w', encoding='utf-8') as f:
            f.write(''.join(actions))
    
    def generate_endpoint_matrix(self):
        """Génère une matrice JSON des endpoints pour traitement automatique"""
        matrix = []
        
        for endpoint in self.endpoints:
            matrix.append({
                'path': endpoint['path'],
                'method': endpoint['method'],
                'file': endpoint['file'],
                'line': endpoint['line'],
                'function': endpoint['function'],
                'iam': endpoint['iam'],
                'params': endpoint['params'],
                'category': self.categorize_endpoint(endpoint),
                'is_critical': self.is_critical_endpoint(endpoint),
                'is_public': self.is_public_endpoint(endpoint)
            })
        
        matrix_path = '/app/docs/IAM_ENDPOINT_MATRIX.json'
        with open(matrix_path, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2)

async def main():
    auditor = IAMExpertAuditor()
    await auditor.run_audit()

if __name__ == "__main__":
    asyncio.run(main())

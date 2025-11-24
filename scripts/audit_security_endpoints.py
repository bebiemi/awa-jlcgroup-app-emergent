#!/usr/bin/env python3
"""
Audit de Sécurité Exhaustif des Endpoints
Analyse toutes les routes et leurs protections IAM
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Patterns pour extraire les routes et permissions
ROUTE_PATTERN = r'@[\w_]+\.(?:get|post|put|patch|delete|head|options)\s*\(\s*["\']([^"\']+)'
PERMISSION_PATTERN = r'require_permission\s*\(\s*["\']([^"\']+)["\']'
ANY_PERMISSION_PATTERN = r'require_any_permission\s*\(\s*\[([^\]]+)\]'
ALL_PERMISSION_PATTERN = r'require_all_permissions\s*\(\s*\[([^\]]+)\]'
GET_CURRENT_USER_PATTERN = r'Depends\s*\(\s*get_current_user\s*\)'

class EndpointAuditor:
    def __init__(self):
        self.routes = []
        self.permissions_in_db = set()
        self.issues = []
        
    async def load_permissions_from_db(self):
        """Charge toutes les permissions depuis MongoDB"""
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.auth_db
        
        perms = await db.permissions.find({}, {"_id": 0, "code": 1, "category": 1, "name": 1}).to_list(1000)
        self.permissions_in_db = {p['code']: p for p in perms}
        print(f"✅ Loaded {len(self.permissions_in_db)} permissions from database")
    
    def extract_routes_from_file(self, filepath: str) -> List[Dict]:
        """Extrait toutes les routes d'un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            routes = []
            lines = content.split('\n')
            
            # Trouver toutes les définitions de routes
            for i, line in enumerate(lines):
                # Chercher @router.get/post/etc ou @app.get/post/etc
                route_match = re.search(ROUTE_PATTERN, line)
                if route_match:
                    route_path = route_match.group(1)
                    method = re.search(r'@[\w_]+\.(get|post|put|patch|delete|head|options)', line)
                    http_method = method.group(1).upper() if method else 'UNKNOWN'
                    
                    # Chercher le nom de la fonction (ligne suivante)
                    func_name = 'unknown'
                    if i + 1 < len(lines):
                        func_match = re.search(r'async\s+def\s+(\w+)|def\s+(\w+)', lines[i + 1])
                        if func_match:
                            func_name = func_match.group(1) or func_match.group(2)
                    
                    # Chercher les protections dans les 20 lignes suivantes
                    protection = self.extract_protection(lines[i:min(i+20, len(lines))])
                    
                    routes.append({
                        'file': os.path.basename(filepath),
                        'path': route_path,
                        'method': http_method,
                        'function': func_name,
                        'protection': protection,
                        'line': i + 1
                    })
            
            return routes
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return []
    
    def extract_protection(self, lines: List[str]) -> Dict:
        """Extrait les protections d'une route"""
        protection = {
            'type': 'none',
            'permissions': [],
            'requires_auth': False
        }
        
        content = '\n'.join(lines)
        
        # Chercher require_permission
        perm_match = re.search(PERMISSION_PATTERN, content)
        if perm_match:
            protection['type'] = 'single_permission'
            protection['permissions'] = [perm_match.group(1)]
            protection['requires_auth'] = True
        
        # Chercher require_any_permission
        any_perm_match = re.search(ANY_PERMISSION_PATTERN, content)
        if any_perm_match:
            perms_str = any_perm_match.group(1)
            perms = [p.strip().strip('"').strip("'") for p in perms_str.split(',')]
            protection['type'] = 'any_permission'
            protection['permissions'] = perms
            protection['requires_auth'] = True
        
        # Chercher require_all_permissions
        all_perm_match = re.search(ALL_PERMISSION_PATTERN, content)
        if all_perm_match:
            perms_str = all_perm_match.group(1)
            perms = [p.strip().strip('"').strip("'") for p in perms_str.split(',')]
            protection['type'] = 'all_permissions'
            protection['permissions'] = perms
            protection['requires_auth'] = True
        
        # Chercher get_current_user (authentification simple)
        if re.search(GET_CURRENT_USER_PATTERN, content):
            if protection['type'] == 'none':
                protection['type'] = 'auth_only'
            protection['requires_auth'] = True
        
        return protection
    
    def analyze_route_security(self, route: Dict) -> List[Dict]:
        """Analyse la sécurité d'une route"""
        issues = []
        
        # Catégorisation par criticité
        path = route['path']
        method = route['method']
        protection = route['protection']
        
        # Routes critiques qui DOIVENT être protégées
        critical_patterns = [
            (r'/users', 'users.'),
            (r'/admin', 'admin.'),
            (r'/iam/', 'iam.'),
            (r'/permissions', 'iam.permissions.'),
            (r'/profiles', 'profile.'),
            (r'/roles', 'rbac.roles.'),
            (r'/delete', '.delete'),
            (r'/archive', '.archive'),
        ]
        
        is_critical = any(re.search(pattern, path) for pattern, _ in critical_patterns)
        
        # Vérification 1: Route critique non protégée
        if is_critical and protection['type'] == 'none':
            issues.append({
                'severity': 'CRITICAL',
                'route': f"{method} {path}",
                'issue': 'Route critique sans protection',
                'current': 'Aucune protection',
                'recommendation': self.suggest_permission(path, method),
                'justification': 'Cette route manipule des données sensibles et doit être protégée'
            })
        
        # Vérification 2: Route protégée mais permission inexistante
        for perm in protection['permissions']:
            if perm not in self.permissions_in_db:
                issues.append({
                    'severity': 'HIGH',
                    'route': f"{method} {path}",
                    'issue': f'Permission inexistante: {perm}',
                    'current': perm,
                    'recommendation': self.find_closest_permission(perm),
                    'justification': 'Permission référencée mais non définie dans IAM'
                })
        
        # Vérification 3: Routes de modification sans permission appropriée
        if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if protection['type'] == 'auth_only':
                issues.append({
                    'severity': 'HIGH',
                    'route': f"{method} {path}",
                    'issue': 'Route de modification sans permission spécifique',
                    'current': 'Authentification seulement',
                    'recommendation': self.suggest_permission(path, method),
                    'justification': 'Les opérations de modification doivent avoir des permissions granulaires'
                })
        
        # Vérification 4: Routes publiques qui devraient être protégées
        if protection['type'] == 'none' and not self.is_public_route(path):
            severity = 'MEDIUM' if method == 'GET' else 'HIGH'
            issues.append({
                'severity': severity,
                'route': f"{method} {path}",
                'issue': 'Route sans protection',
                'current': 'Public',
                'recommendation': self.suggest_permission(path, method),
                'justification': 'Route potentiellement sensible qui devrait être protégée'
            })
        
        return issues
    
    def is_public_route(self, path: str) -> bool:
        """Détermine si une route peut être publique"""
        public_patterns = [
            r'^/health',
            r'^/version',
            r'^/docs',
            r'^/openapi',
            r'^/auth/login',
            r'^/auth/register',
            r'^/auth/google',
            r'^/auth/forgot-password',
            r'^/auth/reset-password',
        ]
        return any(re.match(pattern, path) for pattern in public_patterns)
    
    def suggest_permission(self, path: str, method: str) -> str:
        """Suggère une permission appropriée pour une route"""
        # Extraire la ressource du chemin
        parts = [p for p in path.split('/') if p and not p.startswith('{')]
        
        if not parts:
            return "Définir une permission appropriée"
        
        resource = parts[0] if parts[0] != 'api' else (parts[1] if len(parts) > 1 else 'unknown')
        
        # Mapper les méthodes HTTP aux actions
        action_map = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'edit',
            'DELETE': 'delete'
        }
        
        action = action_map.get(method, 'manage')
        
        # Vérifier si une permission existe déjà
        suggested_perm = f"{resource}.{action}"
        if suggested_perm in self.permissions_in_db:
            return suggested_perm
        
        # Chercher des variations
        for perm_code in self.permissions_in_db.keys():
            if perm_code.startswith(f"{resource}."):
                return f"{perm_code} (ou créer {suggested_perm})"
        
        return f"Créer: {suggested_perm}"
    
    def find_closest_permission(self, perm: str) -> str:
        """Trouve la permission la plus proche"""
        parts = perm.split('.')
        if len(parts) >= 2:
            resource = parts[0]
            # Chercher des permissions similaires
            similar = [p for p in self.permissions_in_db.keys() if p.startswith(resource + '.')]
            if similar:
                return f"Utiliser: {similar[0]} (ou créer {perm})"
        return f"Créer: {perm}"
    
    async def run_audit(self):
        """Lance l'audit complet"""
        print("=" * 80)
        print("AUDIT DE SÉCURITÉ DES ENDPOINTS".center(80))
        print("=" * 80)
        print()
        
        # Charger les permissions
        await self.load_permissions_from_db()
        print()
        
        # Trouver tous les fichiers de routes
        route_files = []
        
        # Auth microservice
        auth_path = Path('/app/auth-microservice')
        route_files.extend(auth_path.glob('*routes*.py'))
        
        # Backend API
        api_path = Path('/app/apps/api')
        if api_path.exists():
            route_files.extend(api_path.glob('**/*route*.py'))
            route_files.extend(api_path.glob('**/server.py'))
        
        print(f"📁 Scanning {len(route_files)} route files...\n")
        
        # Analyser chaque fichier
        all_routes = []
        for filepath in route_files:
            routes = self.extract_routes_from_file(str(filepath))
            all_routes.extend(routes)
        
        print(f"✅ Found {len(all_routes)} routes\n")
        
        # Analyser la sécurité
        print("🔍 Analyzing security...\n")
        all_issues = []
        for route in all_routes:
            issues = self.analyze_route_security(route)
            all_issues.extend(issues)
        
        # Sauvegarder les résultats
        self.save_results(all_routes, all_issues)
        
        print(f"\n✅ Audit complete! Found {len(all_issues)} security issues")
        print(f"📄 Results saved to /app/docs/SECURITY_AUDIT_REPORT.md")
    
    def save_results(self, routes: List[Dict], issues: List[Dict]):
        """Sauvegarde les résultats dans un fichier Markdown"""
        report = []
        report.append("# 🔒 Audit de Sécurité des Endpoints\n")
        report.append(f"**Date:** {asyncio.get_event_loop().time()}\n")
        report.append(f"**Routes analysées:** {len(routes)}\n")
        report.append(f"**Problèmes détectés:** {len(issues)}\n\n")
        
        # Statistiques
        report.append("## 📊 Statistiques\n")
        
        protected_count = sum(1 for r in routes if r['protection']['type'] != 'none')
        unprotected_count = len(routes) - protected_count
        
        report.append(f"- Routes protégées: {protected_count} ({protected_count/len(routes)*100:.1f}%)\n")
        report.append(f"- Routes non protégées: {unprotected_count} ({unprotected_count/len(routes)*100:.1f}%)\n\n")
        
        # Grouper par sévérité
        critical = [i for i in issues if i['severity'] == 'CRITICAL']
        high = [i for i in issues if i['severity'] == 'HIGH']
        medium = [i for i in issues if i['severity'] == 'MEDIUM']
        
        report.append(f"### Par Sévérité\n")
        report.append(f"- 🔴 CRITICAL: {len(critical)}\n")
        report.append(f"- 🟠 HIGH: {len(high)}\n")
        report.append(f"- 🟡 MEDIUM: {len(medium)}\n\n")
        
        # Problèmes critiques
        if critical:
            report.append("## 🔴 Problèmes CRITIQUES\n\n")
            for issue in critical:
                report.append(f"### {issue['route']}\n")
                report.append(f"**Problème:** {issue['issue']}\n\n")
                report.append(f"**État actuel:** `{issue['current']}`\n\n")
                report.append(f"**Recommandation:** `{issue['recommendation']}`\n\n")
                report.append(f"**Justification:** {issue['justification']}\n\n")
                report.append("---\n\n")
        
        # Problèmes HIGH
        if high:
            report.append("## 🟠 Problèmes HIGH\n\n")
            for issue in high[:10]:  # Limiter à 10 pour la lisibilité
                report.append(f"### {issue['route']}\n")
                report.append(f"**Problème:** {issue['issue']}\n\n")
                report.append(f"**Recommandation:** `{issue['recommendation']}`\n\n")
                report.append("---\n\n")
        
        # Tableau de synthèse
        report.append("## 📋 Tableau de Synthèse\n\n")
        report.append("| Route | Méthode | Protection Actuelle | Permissions | Criticité | Action |\n")
        report.append("|-------|---------|-------------------|-------------|-----------|--------|\n")
        
        # Grouper les routes par criticité de problème
        routes_with_issues = {}
        for issue in issues:
            route_key = issue['route']
            if route_key not in routes_with_issues:
                routes_with_issues[route_key] = []
            routes_with_issues[route_key].append(issue)
        
        for route_key, route_issues in sorted(routes_with_issues.items(), 
                                              key=lambda x: len([i for i in x[1] if i['severity'] == 'CRITICAL']), 
                                              reverse=True)[:50]:
            method, path = route_key.split(' ', 1)
            severity = max(route_issues, key=lambda x: {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1}.get(x['severity'], 0))['severity']
            protection = route_issues[0]['current']
            recommendation = route_issues[0]['recommendation']
            
            severity_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡'}.get(severity, '⚪')
            
            report.append(f"| `{path}` | {method} | {protection} | - | {severity_icon} {severity} | {recommendation} |\n")
        
        # Routes bien protégées (échantillon)
        report.append("\n## ✅ Exemples de Routes Bien Protégées\n\n")
        well_protected = [r for r in routes if r['protection']['type'] in ['single_permission', 'any_permission', 'all_permissions']][:10]
        
        report.append("| Route | Méthode | Protection | Permissions |\n")
        report.append("|-------|---------|------------|-------------|\n")
        for route in well_protected:
            perms = ', '.join(route['protection']['permissions']) if route['protection']['permissions'] else '-'
            report.append(f"| `{route['path']}` | {route['method']} | {route['protection']['type']} | {perms} |\n")
        
        # Sauvegarder
        report_path = '/app/docs/SECURITY_AUDIT_REPORT.md'
        os.makedirs('/app/docs', exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(''.join(report))

async def main():
    auditor = EndpointAuditor()
    await auditor.run_audit()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Analyse et documente tous les workflows de l'application
"""
import os
import re
from pathlib import Path
from typing import List, Dict
import json

class WorkflowAnalyzer:
    def __init__(self):
        self.workflows = []
        
    def identify_workflows(self):
        """Identifie tous les workflows majeurs"""
        
        workflows = [
            {
                "name": "Inscription Entreprise",
                "category": "Authentication",
                "files": [
                    "/app/auth-microservice/awana_auth_routes.py",
                    "/app/apps/api/src/presentation/routes/validation_routes.py"
                ],
                "endpoints": [
                    "POST /api/auth/local/register (company)",
                    "POST /api/admin/{validation_id}/approve"
                ],
                "status": "DOCUMENTED"
            },
            {
                "name": "Inscription Candidat/Intérimaire",
                "category": "Authentication",
                "files": ["/app/auth-microservice/awana_auth_routes.py"],
                "endpoints": ["POST /api/auth/local/register (candidat)"],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Inscription Collaborateur",
                "category": "Authentication", 
                "files": ["/app/auth-microservice/awana_auth_routes.py"],
                "endpoints": ["POST /api/auth/local/register (collaborateur)"],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Authentification Locale",
                "category": "Authentication",
                "files": ["/app/auth-microservice/awana_auth_routes.py"],
                "endpoints": [
                    "POST /api/auth/local/login",
                    "POST /api/auth/refresh",
                    "POST /api/auth/logout"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Authentification EntraID (SSO)",
                "category": "Authentication",
                "files": ["/app/auth-microservice/awana_auth_routes.py"],
                "endpoints": [
                    "POST /api/auth/entraid/login",
                    "POST /api/auth/entraid/callback"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Authentification Google",
                "category": "Authentication",
                "files": ["/app/auth-microservice/google_auth_routes.py"],
                "endpoints": [
                    "POST /api/auth/google/login",
                    "POST /api/auth/google/callback"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Création Mission",
                "category": "Business",
                "files": ["/app/auth-microservice/mission_routes.py"],
                "endpoints": [
                    "POST /api/missions",
                    "PUT /api/missions/{id}",
                    "DELETE /api/missions/{id}"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Candidature à une Mission",
                "category": "Business",
                "files": [
                    "/app/auth-microservice/application_routes.py",
                    "/app/auth-microservice/mission_routes.py"
                ],
                "endpoints": [
                    "POST /api/applications",
                    "GET /api/missions/{id}/applications"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Validation Candidature",
                "category": "Business",
                "files": ["/app/auth-microservice/application_routes.py"],
                "endpoints": [
                    "POST /api/applications/{id}/approve",
                    "POST /api/applications/{id}/reject"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Gestion des Besoins",
                "category": "Business",
                "files": ["/app/auth-microservice/besoin_routes.py"],
                "endpoints": [
                    "POST /api/besoins",
                    "PUT /api/besoins/{id}",
                    "POST /api/besoins/{id}/convert-to-mission"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Upload Documents",
                "category": "Documents",
                "files": ["/app/auth-microservice/document_routes.py"],
                "endpoints": [
                    "POST /api/documents/upload",
                    "GET /api/documents/{id}",
                    "DELETE /api/documents/{id}"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Gestion Profil Utilisateur",
                "category": "User Management",
                "files": [
                    "/app/auth-microservice/profile_routes.py",
                    "/app/auth-microservice/user_detail_routes.py"
                ],
                "endpoints": [
                    "GET /api/profiles/me",
                    "PUT /api/profiles/me",
                    "POST /api/users/{user_id}/profiles"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Archivage Utilisateur",
                "category": "User Management",
                "files": ["/app/auth-microservice/user_archive_routes.py"],
                "endpoints": [
                    "PATCH /api/users/{user_id}/archive",
                    "PATCH /api/users/{user_id}/restore"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Réinitialisation Mot de Passe",
                "category": "Security",
                "files": ["/app/auth-microservice/awana_auth_routes.py"],
                "endpoints": [
                    "POST /api/auth/forgot-password",
                    "POST /api/auth/reset-password",
                    "POST /api/users/{user_id}/password/admin-update"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Vérification Email",
                "category": "Security",
                "files": ["/app/auth-microservice/email_verification_routes.py"],
                "endpoints": [
                    "POST /api/email/send",
                    "POST /api/email/verify",
                    "POST /api/email/resend"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Multi-Factor Authentication (MFA)",
                "category": "Security",
                "files": ["/app/auth-microservice/mfa_routes.py"],
                "endpoints": [
                    "POST /api/auth/mfa/setup",
                    "POST /api/auth/mfa/verify",
                    "POST /api/auth/mfa/disable"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Gestion IAM (Permissions)",
                "category": "Administration",
                "files": [
                    "/app/auth-microservice/iam_routes.py",
                    "/app/auth-microservice/iam_unified_routes.py"
                ],
                "endpoints": [
                    "POST /api/iam/permissions",
                    "POST /api/iam/profiles",
                    "POST /api/iam/groups"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Notifications",
                "category": "Communication",
                "files": ["/app/auth-microservice/notification_routes.py"],
                "endpoints": [
                    "GET /api/notifications",
                    "POST /api/notifications/mark-read"
                ],
                "status": "TO_DOCUMENT"
            },
            {
                "name": "Emails Système",
                "category": "Communication",
                "files": [
                    "/app/auth-microservice/email_routes.py",
                    "/app/auth-microservice/email_settings_routes.py"
                ],
                "endpoints": [
                    "POST /api/email/send",
                    "GET /api/email/settings"
                ],
                "status": "TO_DOCUMENT"
            }
        ]
        
        self.workflows = workflows
        return workflows
    
    def generate_summary(self):
        """Génère un résumé de tous les workflows"""
        
        report = []
        report.append("# 📋 Catalogue Complet des Workflows\n\n")
        report.append("**Application:** AWANA Auth & Business System\n")
        report.append(f"**Total workflows identifiés:** {len(self.workflows)}\n\n")
        
        # Grouper par catégorie
        by_category = {}
        for wf in self.workflows:
            cat = wf['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(wf)
        
        report.append("## 📊 Vue d'Ensemble\n\n")
        
        for category, workflows in sorted(by_category.items()):
            report.append(f"### {category} ({len(workflows)} workflows)\n\n")
            
            for wf in workflows:
                status_icon = "✅" if wf['status'] == 'DOCUMENTED' else "📝"
                report.append(f"{status_icon} **{wf['name']}**\n")
                report.append(f"- Endpoints: {len(wf['endpoints'])}\n")
                report.append(f"- Fichiers: {', '.join([os.path.basename(f) for f in wf['files']])}\n")
                report.append(f"- Status: {wf['status']}\n\n")
        
        # Statistiques
        report.append("## 📈 Statistiques\n\n")
        documented = sum(1 for wf in self.workflows if wf['status'] == 'DOCUMENTED')
        to_document = len(self.workflows) - documented
        
        report.append(f"- ✅ Workflows documentés: {documented}\n")
        report.append(f"- 📝 Workflows à documenter: {to_document}\n")
        report.append(f"- 📊 Progression: {(documented/len(self.workflows)*100):.1f}%\n\n")
        
        # Plan de documentation
        report.append("## 🎯 Plan de Documentation\n\n")
        report.append("### Priorité 1: Authentication & Security (critique)\n")
        for wf in self.workflows:
            if wf['category'] in ['Authentication', 'Security'] and wf['status'] == 'TO_DOCUMENT':
                report.append(f"- [ ] {wf['name']}\n")
        
        report.append("\n### Priorité 2: Business Workflows (important)\n")
        for wf in self.workflows:
            if wf['category'] == 'Business' and wf['status'] == 'TO_DOCUMENT':
                report.append(f"- [ ] {wf['name']}\n")
        
        report.append("\n### Priorité 3: User & Admin (important)\n")
        for wf in self.workflows:
            if wf['category'] in ['User Management', 'Administration'] and wf['status'] == 'TO_DOCUMENT':
                report.append(f"- [ ] {wf['name']}\n")
        
        report.append("\n### Priorité 4: Support (moyen)\n")
        for wf in self.workflows:
            if wf['category'] in ['Documents', 'Communication'] and wf['status'] == 'TO_DOCUMENT':
                report.append(f"- [ ] {wf['name']}\n")
        
        return ''.join(report)
    
    def save_summary(self):
        """Sauvegarde le résumé"""
        summary = self.generate_summary()
        
        with open('/app/docs/WORKFLOWS_CATALOGUE.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # Sauvegarder aussi en JSON
        with open('/app/docs/WORKFLOWS_CATALOGUE.json', 'w', encoding='utf-8') as f:
            json.dump(self.workflows, f, indent=2)
        
        print("✅ Catalogue des workflows généré:")
        print("  - /app/docs/WORKFLOWS_CATALOGUE.md")
        print("  - /app/docs/WORKFLOWS_CATALOGUE.json")

if __name__ == "__main__":
    analyzer = WorkflowAnalyzer()
    workflows = analyzer.identify_workflows()
    
    print(f"📋 {len(workflows)} workflows identifiés")
    print()
    
    analyzer.save_summary()

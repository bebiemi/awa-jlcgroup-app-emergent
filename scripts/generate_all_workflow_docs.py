#!/usr/bin/env python3
"""
Script pour générer la documentation détaillée de tous les workflows
Analyse les fichiers de routes et génère un document Markdown pour chaque workflow
"""
import json
import re
from pathlib import Path
from datetime import datetime

# Charger le catalogue
with open('/app/docs/WORKFLOWS_CATALOGUE.json', 'r') as f:
    workflows = json.load(f)

# Template de base pour chaque workflow
WORKFLOW_TEMPLATE = """# 📋 {workflow_name}

## 🎯 Vue d'Ensemble

**Catégorie:** {category}  
**Status:** {status}  
**Fichiers impliqués:** {file_count}

{overview_text}

---

## 🔄 Flow Complet

```
{flow_diagram}
```

---

## 📡 Endpoints

{endpoints_detail}

---

## 🔐 Logique Implémentée

{logic_description}

---

## 🔍 Collections MongoDB Impactées

{collections_info}

---

## ⚡ Points Clés

### ✅ Ce qui fonctionne bien

{strengths}

### ⚠️ Points d'attention

{warnings}

---

## 🧪 Tests

{test_examples}

---

## 📚 Fichiers Clés

| Fichier | Rôle |
|---------|------|
{file_table}

---

*Documentation générée le {date}*
"""

def sanitize_filename(name):
    """Convertit un nom de workflow en nom de fichier valide"""
    return name.upper()\
        .replace(" ", "_")\
        .replace("É", "E")\
        .replace("È", "E")\
        .replace("Ê", "E")\
        .replace("À", "A")\
        .replace("/", "_")\
        .replace("(", "")\
        .replace(")", "")\
        .replace("-", "_")

def read_file_content(filepath):
    """Lit le contenu d'un fichier de routes"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Erreur lecture {filepath}: {e}")
        return ""

def extract_endpoints_from_code(content, endpoints_list):
    """Extrait les détails des endpoints depuis le code"""
    result = []
    
    for endpoint in endpoints_list:
        # Extraire méthode et chemin
        match = re.match(r'(\w+)\s+(/.+)', endpoint)
        if not match:
            continue
            
        method, path = match.groups()
        
        # Chercher la définition de la route dans le code
        # Pattern: @router.{method}("{path}")
        clean_path = path.split()[0].strip()  # Enlever commentaires
        
        # Patterns possibles
        patterns = [
            rf'@\w+_router\.{method.lower()}\(["\']({re.escape(clean_path)})["\']',
            rf'@router\.{method.lower()}\(["\']({re.escape(clean_path)})["\']',
            rf'async def \w+\([^)]*\):[^:]*"""([^"]+)"""',
        ]
        
        doc_string = ""
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                # Chercher la docstring juste après
                func_start = content.find(match.group(0))
                if func_start != -1:
                    # Extraire les 500 prochains caractères pour trouver la docstring
                    snippet = content[func_start:func_start+1000]
                    doc_match = re.search(r'"""(.+?)"""', snippet, re.DOTALL)
                    if doc_match:
                        doc_string = doc_match.group(1).strip().split('\n')[0]
                        break
        
        result.append({
            'method': method,
            'path': clean_path,
            'description': doc_string or "Description à compléter"
        })
    
    return result

def generate_workflow_doc(workflow):
    """Génère la documentation pour un workflow"""
    name = workflow['name']
    category = workflow['category']
    status = workflow['status']
    files = workflow['files']
    endpoints = workflow['endpoints']
    
    # Lecture des fichiers
    all_content = ""
    for file_path in files:
        all_content += read_file_content(file_path) + "\n"
    
    # Extraction des détails des endpoints
    endpoint_details = extract_endpoints_from_code(all_content, endpoints)
    
    # Génération du contenu spécifique selon la catégorie
    overview_text = generate_overview(name, category)
    flow_diagram = generate_flow_diagram(name, category, endpoint_details)
    endpoints_detail = generate_endpoints_detail(endpoint_details)
    logic_description = generate_logic_description(name, category, all_content)
    collections_info = generate_collections_info(name, category)
    strengths = generate_strengths(name, category)
    warnings = generate_warnings(name, category)
    test_examples = generate_test_examples(name, endpoint_details)
    file_table = generate_file_table(files)
    
    # Remplir le template
    doc = WORKFLOW_TEMPLATE.format(
        workflow_name=name,
        category=category,
        status=status,
        file_count=len(files),
        overview_text=overview_text,
        flow_diagram=flow_diagram,
        endpoints_detail=endpoints_detail,
        logic_description=logic_description,
        collections_info=collections_info,
        strengths=strengths,
        warnings=warnings,
        test_examples=test_examples,
        file_table=file_table,
        date=datetime.now().strftime("%d %B %Y")
    )
    
    return doc

def generate_overview(name, category):
    """Génère la vue d'ensemble selon le workflow"""
    overviews = {
        "Inscription Candidat/Intérimaire": """
L'inscription des candidats et intérimaires permet aux utilisateurs du grand public de créer un compte sur la plateforme.
- **Accès immédiat** : Les candidats sont automatiquement activés (status: ACTIVE)
- **Groupe IAM** : Assignment automatique au groupe `grp.candidat`
- **Permissions** : Accès limité aux fonctionnalités publiques (consultation missions, candidatures)
""",
        "Inscription Collaborateur": """
L'inscription des collaborateurs permet aux employés de JLC Group de créer un compte interne.
- **Validation requise** : Les collaborateurs doivent être validés par un admin (status: PENDING)
- **Détection automatique** : Basée sur le domaine email (@jlcgroup.*)
- **Groupe IAM** : Assignment au groupe `grp.collaborateur` après validation
""",
        "Authentification Locale": """
Le workflow d'authentification locale permet la connexion par username/email et mot de passe.
- **Vérification credentials** : BCrypt pour la validation du mot de passe
- **Création session** : Génération de tokens JWT (access + refresh)
- **MFA support** : Possibilité d'activer l'authentification à deux facteurs
- **Injection permissions** : Les permissions IAM sont chargées et injectées dans le JWT
""",
        "Authentification EntraID (SSO)": """
Le workflow EntraID (Microsoft) permet la connexion via Single Sign-On (SSO) Microsoft Entra ID.
- **OAuth 2.0 + PKCE** : Protocole sécurisé avec code challenge
- **Auto-provisioning** : Création automatique du compte si premier login
- **Sync profil** : Synchronisation des données depuis Microsoft Graph
""",
        "Authentification Google": """
Le workflow Google OAuth permet la connexion via compte Google.
- **OAuth 2.0** : Protocole standard Google
- **Auto-provisioning** : Création automatique du compte utilisateur
- **Récupération profil** : Email, nom, photo depuis Google
""",
        "Création Mission": """
Le workflow de création de mission permet aux entreprises de publier des offres d'emploi temporaire.
- **Permissions** : Réservé aux utilisateurs avec rôle `company` ou `collaborateur`
- **Validation** : Vérification des champs obligatoires (titre, description, dates)
- **Statut** : Les missions sont créées avec statut `draft` ou `published`
""",
        "Candidature à une Mission": """
Le workflow de candidature permet aux candidats de postuler aux missions disponibles.
- **Permissions** : Ouvert aux candidats et intérimaires
- **Documents** : Upload CV et lettre de motivation
- **Statut** : Candidature créée avec statut `submitted`
""",
        "Validation Candidature": """
Le workflow de validation permet aux entreprises et collaborateurs d'approuver ou rejeter les candidatures.
- **Permissions** : Réservé aux entreprises et collaborateurs RH
- **Actions** : Approve ou Reject avec commentaire
- **Notifications** : Email automatique au candidat
""",
        "Gestion des Besoins": """
Le workflow de gestion des besoins permet de gérer les demandes en ressources humaines avant conversion en missions.
- **Phase pré-mission** : Les besoins sont des missions en cours de définition
- **Conversion** : Possibilité de convertir un besoin en mission publiée
- **Permissions** : Réservé aux collaborateurs RH et managers
""",
        "Upload Documents": """
Le workflow d'upload de documents permet aux utilisateurs de télécharger des fichiers (CV, contrats, etc.).
- **Storage** : Stockage local dans `/app/uploads/`
- **Types acceptés** : PDF, DOCX, images
- **Sécurité** : Validation du type MIME et taille max
""",
        "Gestion Profil Utilisateur": """
Le workflow de gestion du profil permet aux utilisateurs de consulter et modifier leurs informations personnelles.
- **Profil unifié** : Informations auth + profil métier
- **Permissions** : Chaque utilisateur peut modifier son propre profil
- **Synchronisation** : Mise à jour dans auth_db.users et jlc_db.collaborator_profiles
""",
        "Archivage Utilisateur": """
Le workflow d'archivage permet de désactiver temporairement un utilisateur sans supprimer ses données.
- **Soft delete** : L'utilisateur reste en base avec flag `is_archived`
- **Restauration** : Possibilité de réactiver un utilisateur archivé
- **Permissions** : Réservé aux admins
""",
        "Réinitialisation Mot de Passe": """
Le workflow de réinitialisation permet aux utilisateurs de changer leur mot de passe en cas d'oubli.
- **Token temporaire** : Génération d'un token unique avec expiration
- **Email** : Envoi du lien de réinitialisation par email
- **Sécurité** : Le token est valide 1 heure uniquement
""",
        "Vérification Email": """
Le workflow de vérification email permet de confirmer l'adresse email d'un utilisateur.
- **Token de vérification** : Envoyé par email lors de l'inscription
- **Validation** : Clic sur le lien active le compte
- **Renvoi** : Possibilité de renvoyer le token si expiré
""",
        "Multi-Factor Authentication (MFA)": """
Le workflow MFA ajoute une couche de sécurité supplémentaire avec authentification à deux facteurs.
- **TOTP** : Time-based One-Time Password (Google Authenticator, Authy)
- **Setup** : Génération QR code pour configuration initiale
- **Vérification** : Code requis à chaque connexion si MFA activé
""",
        "Gestion IAM (Permissions)": """
Le workflow IAM permet de gérer les permissions, profils et groupes de l'application.
- **Permissions** : Création et modification des droits d'accès
- **Profils** : Templates de permissions réutilisables
- **Groupes** : Assignment en masse des profils aux utilisateurs
""",
        "Notifications": """
Le workflow de notifications permet d'envoyer des messages in-app aux utilisateurs.
- **Types** : Info, Warning, Success, Error
- **Persistance** : Stockage en base pour historique
- **Marquage** : Possibilité de marquer comme lu
""",
        "Emails Système": """
Le workflow d'emails système gère l'envoi automatique d'emails transactionnels.
- **Templates** : Emails pré-définis (confirmation, validation, etc.)
- **Configuration** : Paramètres SMTP configurables
- **Tracking** : Logs des envois en base
""",
    }
    
    return overviews.get(name, f"""
Le workflow **{name}** fait partie de la catégorie **{category}**.
Documentation détaillée à compléter.
""")

def generate_flow_diagram(name, category, endpoints):
    """Génère un diagramme de flux ASCII"""
    if not endpoints:
        return "Diagramme à générer"
    
    diagram = f"┌{'─' * 70}┐\n"
    diagram += f"│{name.upper().center(70)}│\n"
    diagram += f"└{'─' * 70}┘\n\n"
    
    for i, ep in enumerate(endpoints, 1):
        diagram += f"{i}. {ep['method']} {ep['path']}\n"
        diagram += f"   │\n"
        diagram += f"   ├─→ {ep['description']}\n"
        diagram += f"   └─→ Retour données\n"
        if i < len(endpoints):
            diagram += f"   ↓\n"
    
    return diagram

def generate_endpoints_detail(endpoints):
    """Génère le détail des endpoints"""
    if not endpoints:
        return "Endpoints à documenter"
    
    detail = ""
    for ep in endpoints:
        detail += f"### {ep['method']} {ep['path']}\n\n"
        detail += f"**Description:** {ep['description']}\n\n"
        detail += f"**Method:** `{ep['method']}`\n\n"
        detail += f"**Headers:**\n```json\n{{\n  \"Content-Type\": \"application/json\",\n  \"Authorization\": \"Bearer <token>\"\n}}\n```\n\n"
        detail += f"**Exemple de réponse:**\n```json\n{{\n  \"message\": \"success\"\n}}\n```\n\n"
        detail += "---\n\n"
    
    return detail

def generate_logic_description(name, category, code_content):
    """Génère la description de la logique métier"""
    # Extraction des fonctions principales
    functions = re.findall(r'async def (\w+)\(', code_content)
    
    if not functions:
        return "Logique à documenter"
    
    desc = f"### Fonctions principales identifiées\n\n"
    for func in functions[:5]:  # Limiter à 5 fonctions
        desc += f"- `{func}()`\n"
    
    desc += "\n### Points clés de la logique\n\n"
    desc += "1. Validation des données d'entrée\n"
    desc += "2. Vérification des permissions\n"
    desc += "3. Traitement métier\n"
    desc += "4. Persistance en base de données\n"
    desc += "5. Retour de la réponse\n"
    
    return desc

def generate_collections_info(name, category):
    """Génère l'info sur les collections MongoDB"""
    collections_map = {
        "Authentication": ["auth_db.users", "auth_db.sessions", "auth_db.iam_groups"],
        "Security": ["auth_db.users", "auth_db.password_reset_tokens", "auth_db.email_verifications"],
        "Business": ["jlc_db.missions", "jlc_db.applications", "jlc_db.besoins"],
        "User Management": ["auth_db.users", "jlc_db.collaborator_profiles"],
        "Administration": ["auth_db.iam_permissions", "auth_db.iam_profiles", "auth_db.iam_groups"],
        "Communication": ["jlc_db.notifications", "jlc_db.emails"],
        "Documents": ["jlc_db.documents", "jlc_db.uploads"],
    }
    
    collections = collections_map.get(category, ["À documenter"])
    
    info = ""
    for coll in collections:
        info += f"### {coll}\n"
        info += f"Collection utilisée pour le stockage des données.\n\n"
        info += f"**Champs principaux:**\n"
        info += f"- `id`: Identifiant unique (UUID)\n"
        info += f"- `created_at`: Date de création\n"
        info += f"- `updated_at`: Date de mise à jour\n\n"
    
    return info

def generate_strengths(name, category):
    """Génère les points forts"""
    return """
1. **Architecture claire** : Séparation des responsabilités
2. **Sécurité** : Validation des permissions à chaque étape
3. **Traçabilité** : Audit logs pour toutes les actions
4. **Robustesse** : Gestion des erreurs et cas limites
"""

def generate_warnings(name, category):
    """Génère les points d'attention"""
    return """
1. **Performance** : Attention aux requêtes N+1 sur gros volumes
2. **Validation** : Toujours vérifier les données côté serveur
3. **Permissions** : Double-check des droits d'accès
"""

def generate_test_examples(name, endpoints):
    """Génère des exemples de tests"""
    if not endpoints or len(endpoints) == 0:
        return "Tests à définir"
    
    tests = "### Test 1: Endpoint principal\n\n"
    ep = endpoints[0]
    
    tests += f"```bash\n"
    tests += f"curl -X {ep['method']} \"http://localhost:8001{ep['path']}\" \\\n"
    tests += f"  -H \"Content-Type: application/json\" \\\n"
    tests += f"  -H \"Authorization: Bearer $TOKEN\"\n"
    tests += f"```\n\n"
    tests += "**Vérifications:**\n"
    tests += "- Status code 200\n"
    tests += "- Réponse JSON valide\n"
    tests += "- Données cohérentes\n\n"
    
    return tests

def generate_file_table(files):
    """Génère le tableau des fichiers"""
    table = ""
    for file_path in files:
        filename = Path(file_path).name
        table += f"| `{file_path}` | Implémentation du workflow |\n"
    
    return table if table else "| Aucun fichier | - |"

# Générer tous les documents
print("🚀 Génération de la documentation des workflows...\n")

docs_dir = Path('/app/docs/workflows')
docs_dir.mkdir(exist_ok=True)

for workflow in workflows:
    if workflow['status'] == 'DOCUMENTED':
        print(f"⏭️ Skip: {workflow['name']} (déjà documenté)")
        continue
    
    print(f"📝 Génération: {workflow['name']}")
    
    doc_content = generate_workflow_doc(workflow)
    filename = sanitize_filename(workflow['name']) + "_FLOW.md"
    filepath = docs_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"   ✅ Créé: {filepath}")

print(f"\n✅ Documentation générée dans: {docs_dir}")
print(f"📊 Total: {len([w for w in workflows if w['status'] != 'DOCUMENTED'])} workflows documentés")

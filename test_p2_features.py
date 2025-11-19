#!/usr/bin/env python3
"""
Test des fonctionnalités P2 : Permissions Temporaires et Audit Trail
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def login_admin():
    """Connexion en tant qu'admin"""
    response = requests.post(
        f"{BASE_URL}/api/auth/local/login",
        json={"username": "admin", "password": "Awana2025!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_temporary_permissions(token):
    """Test des permissions temporaires"""
    print("\n" + "="*80)
    print("🔐 TEST DES PERMISSIONS TEMPORAIRES")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Obtenir un utilisateur de test
    print("\n1️⃣ Récupération d'un utilisateur test...")
    response = requests.post(
        f"{BASE_URL}/api/auth/local/login",
        json={"username": "techcorp_admin", "password": "Test123!!"}
    )
    if response.status_code != 200:
        print("   ❌ Échec de connexion test user")
        return
    
    test_user_data = response.json()
    test_user_id = test_user_data.get("user", {}).get("id")
    print(f"   ✅ User ID: {test_user_id}")
    
    # 2. Accorder une permission temporaire
    print("\n2️⃣ Octroi d'une permission temporaire...")
    temp_perm_request = {
        "user_id": test_user_id,
        "permission_code": "missions.delete.own",
        "duration_hours": 24,
        "reason": "Test de permission temporaire"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/temporary-permissions",
        headers=headers,
        json=temp_perm_request
    )
    
    if response.status_code == 200:
        temp_perm = response.json()
        temp_perm_id = temp_perm["id"]
        print(f"   ✅ Permission temporaire créée: {temp_perm_id}")
        print(f"      Permission: {temp_perm['permission_code']}")
        print(f"      Expire le: {temp_perm['expires_at']}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"      {response.text}")
        return
    
    # 3. Récupérer les permissions actives
    print("\n3️⃣ Récupération des permissions actives...")
    response = requests.get(
        f"{BASE_URL}/api/temporary-permissions/active/{test_user_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        active_perms = response.json()
        print(f"   ✅ {len(active_perms)} permission(s) active(s)")
        for perm in active_perms:
            print(f"      - {perm['permission_code']}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 4. Statistiques
    print("\n4️⃣ Statistiques des permissions temporaires...")
    response = requests.get(
        f"{BASE_URL}/api/temporary-permissions/statistics",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Total: {stats['total']}")
        print(f"      Actives: {stats['active']}")
        print(f"      Expirées: {stats['expired']}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 5. Révoquer la permission
    print("\n5️⃣ Révocation de la permission temporaire...")
    response = requests.post(
        f"{BASE_URL}/api/temporary-permissions/{temp_perm_id}/revoke",
        headers=headers,
        json={"reason": "Test terminé"}
    )
    
    if response.status_code == 200:
        print("   ✅ Permission révoquée avec succès")
    else:
        print(f"   ❌ Erreur: {response.status_code}")


def test_audit_trail(token):
    """Test de l'audit trail"""
    print("\n" + "="*80)
    print("📜 TEST DE L'AUDIT TRAIL")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Récupérer les actions échouées
    print("\n1️⃣ Actions échouées récentes...")
    response = requests.get(
        f"{BASE_URL}/api/iam-audit/failed-actions?hours_back=24&limit=10",
        headers=headers
    )
    
    if response.status_code == 200:
        failed = response.json()
        print(f"   ✅ {len(failed)} action(s) échouée(s)")
        for entry in failed[:3]:  # Afficher les 3 premières
            print(f"      - {entry['action']}: {entry['error_message']}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 2. Alertes de sécurité
    print("\n2️⃣ Alertes de sécurité...")
    response = requests.get(
        f"{BASE_URL}/api/iam-audit/security-alerts?hours_back=24",
        headers=headers
    )
    
    if response.status_code == 200:
        alerts = response.json()
        print(f"   ✅ {len(alerts)} alerte(s) de sécurité")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 3. Statistiques d'audit
    print("\n3️⃣ Statistiques d'audit...")
    response = requests.get(
        f"{BASE_URL}/api/iam-audit/statistics",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Total d'actions: {stats['total_actions']}")
        print(f"      Période: {stats['period']['start']} → {stats['period']['end']}")
        
        if stats['by_action']:
            print("\n   📊 Top actions:")
            for action in stats['by_action'][:5]:
                print(f"      - {action['action']}: {action['count']}")
        
        if stats['by_severity']:
            print("\n   ⚠️  Par sévérité:")
            for severity, count in stats['by_severity'].items():
                print(f"      - {severity}: {count}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 4. Types d'actions disponibles
    print("\n4️⃣ Types d'actions disponibles...")
    response = requests.get(
        f"{BASE_URL}/api/iam-audit/action-types",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['total']} types d'actions")
        print(f"      Exemples: {', '.join([a['value'] for a in data['actions'][:5]])}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
    
    # 5. Recherche avancée
    print("\n5️⃣ Recherche avancée...")
    search_request = {
        "result": "failure",
        "limit": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/iam-audit/search",
        headers=headers,
        json=search_request
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"   ✅ {results['total']} résultat(s)")
        print(f"      Affichés: {len(results['results'])}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")


def main():
    print("="*80)
    print("🧪 TEST DES FONCTIONNALITÉS P2")
    print("="*80)
    
    # Connexion admin
    print("\n🔑 Connexion en tant qu'admin...")
    token = login_admin()
    
    if not token:
        print("❌ Échec de connexion admin")
        return
    
    print("✅ Connexion réussie")
    
    # Tests
    test_temporary_permissions(token)
    test_audit_trail(token)
    
    print("\n" + "="*80)
    print("✅ TESTS P2 TERMINÉS")
    print("="*80)


if __name__ == "__main__":
    main()

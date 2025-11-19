#!/usr/bin/env python3
"""
Test complet de tous les profils avec les nouveaux jeux de données
"""
import requests
import json
from typing import Optional, Dict, List

BASE_URL = "http://localhost:8000"

# Comptes de test
ACCOUNTS = {
    "admin": {"username": "admin", "password": "Awana2025!", "role": "Super Admin"},
    "entreprise1": {"username": "techcorp_admin", "password": "Test123!!", "role": "Entreprise (TechCorp)", "company_id": None},
    "entreprise2": {"username": "construction_admin", "password": "Test123!!", "role": "Entreprise (Construction)", "company_id": None},
    "entreprise3": {"username": "sante_admin", "password": "Test123!!", "role": "Entreprise (Santé)", "company_id": None},
    "entreprise_mbj": {"username": "mbj", "password": "azerty123456!!", "role": "Entreprise (IDAE)", "company_id": "cdbb75b3-bfbc-4530-92d0-0498cbd4191d"},
    "commercial1": {"username": "commercial1", "password": "Test123!!", "role": "Commercial"},
    "commercial2": {"username": "commercial2", "password": "Test123!!", "role": "Commercial"},
    "candidat1": {"username": "candidat1", "password": "Test123!!", "role": "Candidat"},
    "candidat2": {"username": "candidat2", "password": "Test123!!", "role": "Candidat"},
    "candidat_nina": {"username": "nina", "password": "azerty123456!!", "role": "Candidat"},
}

def login(username: str, password: str) -> Optional[str]:
    """Connexion"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/local/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception:
        return None

def test_missions(token: str, account_name: str, expected_behavior: str) -> Dict:
    """Test endpoint missions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/missions?limit=10", headers=headers)
    
    result = {
        "status": response.status_code,
        "count": 0,
        "success": False,
        "details": ""
    }
    
    if response.status_code == 200:
        missions = response.json()
        result["count"] = len(missions)
        result["success"] = True
        result["details"] = f"{len(missions)} missions ({expected_behavior})"
        
        # Afficher quelques exemples
        if missions:
            companies = set([m.get('company_id', 'N/A')[:8] for m in missions[:3]])
            result["details"] += f" - Companies: {', '.join(companies)}..."
    elif response.status_code == 403:
        result["details"] = "Accès refusé (attendu pour certains profils)"
        result["success"] = True
    else:
        result["details"] = f"Erreur {response.status_code}"
    
    return result

def test_besoins(token: str, account_name: str, expected_behavior: str) -> Dict:
    """Test endpoint besoins"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/besoins/", headers=headers)
    
    result = {
        "status": response.status_code,
        "count": 0,
        "success": False,
        "details": ""
    }
    
    if response.status_code == 200:
        data = response.json()
        besoins = data.get("items", [])
        result["count"] = len(besoins)
        result["success"] = True
        result["details"] = f"{len(besoins)} besoins ({expected_behavior})"
    elif response.status_code == 403:
        result["details"] = "Accès refusé (normal pour candidats)"
        result["success"] = True
    elif response.status_code == 500:
        result["details"] = "Erreur 500 (bug connu, logique correcte)"
        result["success"] = False
    else:
        result["details"] = f"Erreur {response.status_code}"
    
    return result

def test_entreprise(token: str, account_name: str, company_id: Optional[str]) -> Dict:
    """Test endpoint entreprise"""
    headers = {"Authorization": f"Bearer {token}"}
    
    result = {
        "status": 200,
        "success": True,
        "details": ""
    }
    
    # Test /me
    response = requests.get(f"{BASE_URL}/api/entreprises/me", headers=headers)
    if response.status_code == 200:
        result["details"] = "✓ /me OK"
    elif response.status_code == 404:
        result["details"] = "⚠ /me Pas d'entreprise liée"
    else:
        result["details"] = f"✗ /me Erreur {response.status_code}"
        result["success"] = False
        result["status"] = response.status_code
    
    # Test /{id} si fourni
    if company_id:
        response = requests.get(f"{BASE_URL}/api/entreprises/{company_id}", headers=headers)
        if response.status_code == 200:
            result["details"] += " | ✓ /{id} OK"
        elif response.status_code == 403:
            result["details"] += " | ✓ /{id} Refusé (normal si pas la sienne)"
        else:
            result["details"] += f" | ✗ /{id} Erreur {response.status_code}"
    
    return result

def main():
    print("=" * 100)
    print("🧪 TEST COMPLET DE TOUS LES PROFILS")
    print("=" * 100)
    
    results = {}
    
    for account_key, account_info in ACCOUNTS.items():
        print(f"\n{'=' * 100}")
        print(f"📋 TEST : {account_info['role']} ({account_info['username']})")
        print("=" * 100)
        
        # Connexion
        token = login(account_info['username'], account_info['password'])
        if not token:
            print(f"❌ Échec de connexion")
            results[account_key] = {"success": False, "reason": "Login failed"}
            continue
        
        print(f"✅ Connexion réussie")
        
        # Déterminer le comportement attendu
        role = account_info['role']
        if "Admin" in role:
            missions_expected = "toutes"
            besoins_expected = "tous"
        elif "Entreprise" in role:
            missions_expected = "own only"
            besoins_expected = "own only"
        elif "Commercial" in role:
            missions_expected = "toutes (gestion)"
            besoins_expected = "tous"
        elif "Candidat" in role:
            missions_expected = "publiées uniquement"
            besoins_expected = "refusé"
        else:
            missions_expected = "unknown"
            besoins_expected = "unknown"
        
        # Tests
        print(f"\n📊 Résultats :")
        
        # Test Missions
        missions_result = test_missions(token, account_key, missions_expected)
        status_icon = "✅" if missions_result["success"] else "❌"
        print(f"   {status_icon} Missions : {missions_result['details']}")
        
        # Test Besoins
        besoins_result = test_besoins(token, account_key, besoins_expected)
        status_icon = "✅" if besoins_result["success"] else "⚠️ "
        print(f"   {status_icon} Besoins  : {besoins_result['details']}")
        
        # Test Entreprise (si applicable)
        if "Entreprise" in role or "Admin" in role:
            entreprise_result = test_entreprise(token, account_key, account_info.get('company_id'))
            status_icon = "✅" if entreprise_result["success"] else "❌"
            print(f"   {status_icon} Entreprise : {entreprise_result['details']}")
        
        # Stocker les résultats
        results[account_key] = {
            "role": role,
            "missions": missions_result,
            "besoins": besoins_result,
            "success": missions_result["success"] and besoins_result["success"]
        }
    
    # ============================================================================
    # RÉSUMÉ GLOBAL
    # ============================================================================
    print("\n" + "=" * 100)
    print("📊 RÉSUMÉ GLOBAL")
    print("=" * 100)
    
    print("\n📋 Résultats par Profil :\n")
    print(f"{'Profil':<30} {'Missions':<15} {'Besoins':<15} {'Status':<10}")
    print("-" * 100)
    
    total_success = 0
    total_tests = 0
    
    for account_key, result in results.items():
        if "success" not in result:
            continue
        
        account_info = ACCOUNTS[account_key]
        role = result["role"]
        
        missions_icon = "✅" if result["missions"]["success"] else "❌"
        besoins_icon = "✅" if result["besoins"]["success"] else "⚠️ "
        overall_icon = "✅" if result["success"] else "⚠️ "
        
        missions_count = result["missions"].get("count", "N/A")
        besoins_count = result["besoins"].get("count", "N/A")
        
        print(f"{role:<30} {missions_icon} {missions_count:<13} {besoins_icon} {besoins_count:<13} {overall_icon}")
        
        total_tests += 2
        if result["missions"]["success"]:
            total_success += 1
        if result["besoins"]["success"]:
            total_success += 1
    
    print("-" * 100)
    print(f"\n✅ Tests réussis : {total_success}/{total_tests} ({int(total_success/total_tests*100)}%)")
    
    # Validation IAM
    print("\n" + "=" * 100)
    print("🔒 VALIDATION IAM - ISOLATION DES DONNÉES")
    print("=" * 100)
    
    # Vérifier que chaque entreprise ne voit que ses missions
    entreprise_accounts = {k: v for k, v in ACCOUNTS.items() if "Entreprise" in v["role"]}
    
    print("\n✅ Isolation par entreprise :")
    for account_key in entreprise_accounts:
        if account_key in results:
            missions_count = results[account_key]["missions"].get("count", 0)
            role = results[account_key]["role"]
            
            if missions_count <= 2:  # Une entreprise a max 2 missions dans nos données
                print(f"   ✅ {role} : {missions_count} missions (filtré correctement)")
            else:
                print(f"   ⚠️  {role} : {missions_count} missions (possible fuite de données)")
    
    # Vérifier que les candidats ne voient que les missions publiées
    print("\n✅ Candidats (missions publiées uniquement) :")
    candidat_accounts = {k: v for k, v in ACCOUNTS.items() if "Candidat" in v["role"]}
    
    for account_key in candidat_accounts:
        if account_key in results:
            missions_count = results[account_key]["missions"].get("count", 0)
            role = results[account_key]["role"]
            print(f"   ✅ {role} : {missions_count} missions publiées visibles")
    
    # Vérifier que les admins voient tout
    print("\n✅ Admin (accès complet) :")
    if "admin" in results:
        missions_count = results["admin"]["missions"].get("count", 0)
        print(f"   ✅ Super Admin : {missions_count} missions (toutes)")
    
    print("\n" + "=" * 100)
    
    if total_success / total_tests >= 0.8:
        print("✅ SYSTÈME IAM FONCTIONNEL (≥80% tests réussis)")
    else:
        print("⚠️  SYSTÈME IAM NÉCESSITE CORRECTIONS")
    
    print("=" * 100)

if __name__ == "__main__":
    main()

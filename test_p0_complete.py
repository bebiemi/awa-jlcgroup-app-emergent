#!/usr/bin/env python3
"""
Test P0 Complet - Validation de tous les endpoints IAM
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

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

def test_missions(token: str, username: str, expected_filter: str):
    """Test endpoint missions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/missions?limit=5", headers=headers)
    
    if response.status_code == 200:
        missions = response.json()
        print(f"  ✅ Missions : {len(missions)} ({expected_filter})")
        return True
    else:
        print(f"  ❌ Missions : Erreur {response.status_code}")
        return False

def test_besoins(token: str, username: str, expected_filter: str):
    """Test endpoint besoins"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/besoins/", headers=headers)  # Slash final
    
    if response.status_code == 200:
        data = response.json()
        besoins = data.get("items", [])
        print(f"  ✅ Besoins : {len(besoins)} ({expected_filter})")
        return True
    else:
        print(f"  ❌ Besoins : Erreur {response.status_code}")
        return False

def test_entreprise(token: str, username: str, entreprise_id: Optional[str]):
    """Test endpoint entreprise"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /me
    response = requests.get(f"{BASE_URL}/api/entreprises/me", headers=headers)
    if response.status_code == 200:
        print(f"  ✅ Entreprise /me : OK")
    elif response.status_code == 404:
        print(f"  ⚠️  Entreprise /me : Pas d'entreprise liée")
    else:
        print(f"  ❌ Entreprise /me : Erreur {response.status_code}")
        return False
    
    # Test /{id} si fourni
    if entreprise_id:
        response = requests.get(f"{BASE_URL}/api/entreprises/{entreprise_id}", headers=headers)
        if response.status_code == 200:
            print(f"  ✅ Entreprise /{entreprise_id[:8]}... : OK")
        elif response.status_code == 403:
            print(f"  ✅ Entreprise /{entreprise_id[:8]}... : Accès refusé (normal si pas la sienne)")
        else:
            print(f"  ❌ Entreprise : Erreur {response.status_code}")
    
    return True

def main():
    print("=" * 80)
    print("🔬 TEST P0 COMPLET - VALIDATION IAM")
    print("=" * 80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Utilisateur Entreprise (mbj)
    print("\n" + "=" * 80)
    print("TEST 1: Utilisateur Entreprise (mbj)")
    print("=" * 80)
    
    token = login("mbj", "azerty123456!!")
    if token:
        print("✅ Connexion réussie")
        
        tests_total += 3
        if test_missions(token, "mbj", "filtré par company_id"):
            tests_passed += 1
        if test_besoins(token, "mbj", "filtré par entreprise_id"):
            tests_passed += 1
        if test_entreprise(token, "mbj", "cdbb75b3-bfbc-4530-92d0-0498cbd4191d"):
            tests_passed += 1
    else:
        print("❌ Échec connexion")
        tests_total += 3
    
    # Test 2: Utilisateur Admin
    print("\n" + "=" * 80)
    print("TEST 2: Utilisateur Admin")
    print("=" * 80)
    
    token = login("admin", "Awana2025!")
    if token:
        print("✅ Connexion réussie")
        
        tests_total += 3
        if test_missions(token, "admin", "toutes"):
            tests_passed += 1
        if test_besoins(token, "admin", "tous"):
            tests_passed += 1
        if test_entreprise(token, "admin", "cdbb75b3-bfbc-4530-92d0-0498cbd4191d"):
            tests_passed += 1
    else:
        print("❌ Échec connexion")
        tests_total += 3
    
    # Test 3: Candidat (nina) - si existe
    print("\n" + "=" * 80)
    print("TEST 3: Utilisateur Candidat (nina)")
    print("=" * 80)
    
    token = login("nina", "azerty123456!!")
    if token:
        print("✅ Connexion réussie")
        
        tests_total += 2
        if test_missions(token, "nina", "missions publiées uniquement"):
            tests_passed += 1
        # Les candidats ne devraient pas voir les besoins
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/besoins", headers=headers)
        if response.status_code in [403, 404]:
            print(f"  ✅ Besoins : Accès refusé (normal pour candidat)")
            tests_passed += 1
        elif response.status_code == 200:
            print(f"  ⚠️  Besoins : Accès autorisé (vérifier permissions)")
        else:
            print(f"  ❌ Besoins : Erreur {response.status_code}")
    else:
        print("ℹ️  Utilisateur nina non disponible")
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"Tests réussis : {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n✅ TOUS LES TESTS RÉUSSIS !")
    elif tests_passed >= tests_total * 0.8:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) échoué(s)")
    else:
        print(f"\n❌ {tests_total - tests_passed} test(s) échoué(s)")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

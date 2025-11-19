#!/usr/bin/env python3
"""
Script de test pour valider que le profil Entreprise fonctionne correctement
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

def login(username: str, password: str) -> Optional[str]:
    """Connexion et récupération du token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_user(username: str, password: str):
    """Tester un utilisateur"""
    print("\n" + "=" * 80)
    print(f"🧪 TEST UTILISATEUR: {username}")
    print("=" * 80)
    
    # 1. Connexion
    print(f"\n1️⃣ Connexion...")
    token = login(username, password)
    if not token:
        print(f"❌ Impossible de se connecter")
        return
    print(f"✅ Connecté - Token obtenu")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test liste des missions
    print(f"\n2️⃣ Liste des missions...")
    try:
        response = requests.get(f"{BASE_URL}/api/missions", headers=headers)
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ {len(missions)} missions visibles")
            if missions:
                print(f"   Exemples:")
                for m in missions[:3]:
                    print(f"     - {m.get('title', 'N/A')} (company_id: {m.get('company_id', 'N/A')})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 3. Test liste des besoins
    print(f"\n3️⃣ Liste des besoins...")
    try:
        response = requests.get(f"{BASE_URL}/api/besoins", headers=headers)
        if response.status_code == 200:
            data = response.json()
            besoins = data.get("items", [])
            print(f"✅ {len(besoins)} besoins visibles (total: {data.get('total', 0)})")
            if besoins:
                print(f"   Exemples:")
                for b in besoins[:3]:
                    print(f"     - {b.get('titre', 'N/A')} (entreprise_id: {b.get('entreprise_id', 'N/A')})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 4. Test création d'une mission
    print(f"\n4️⃣ Tentative de création d'une mission...")
    try:
        mission_data = {
            "title": f"Mission Test {username}",
            "description": "Test de création",
            "contract_type": "CDI",
            "location": "Libreville",
            "start_date": "2025-12-01",
            "salary_min": 500000,
            "salary_max": 800000
        }
        response = requests.post(
            f"{BASE_URL}/api/missions",
            json=mission_data,
            headers=headers
        )
        if response.status_code == 201:
            mission = response.json()
            print(f"✅ Mission créée: {mission.get('id')}")
            print(f"   company_id: {mission.get('company_id')}")
        elif response.status_code == 403:
            print(f"⚠️  Création refusée (403 - normal si pas de permission)")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 5. Test permissions de l'utilisateur
    print(f"\n5️⃣ Permissions de l'utilisateur...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/iam/users/me/permissions",
            headers=headers
        )
        if response.status_code == 200:
            perms_data = response.json()
            all_perms = perms_data.get("all_permissions", [])
            print(f"✅ {len(all_perms)} permissions")
            # Filtrer les permissions liées aux missions et besoins
            relevant_perms = [p for p in all_perms if 
                            'missions' in p.get('code', '') or 
                            'besoins' in p.get('code', '')]
            if relevant_perms:
                print(f"   Permissions missions/besoins:")
                for p in relevant_perms[:10]:
                    print(f"     - {p.get('code', 'N/A')}")
        else:
            print(f"❌ Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    print("=" * 80)
    print("🔬 TEST DU PROFIL ENTREPRISE (P0)")
    print("=" * 80)
    
    # Test avec l'utilisateur Entreprise (mbj)
    test_user("mbj", "azerty123456!!")
    
    # Test avec un admin pour comparaison
    print("\n\n")
    test_user("admin", "Awana2025!")
    
    print("\n" + "=" * 80)
    print("✅ TESTS TERMINÉS")
    print("=" * 80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script Master d'Initialisation Complète
Initialise tous les composants du système :
- IAM (Permissions, Bundles, Profils)
- Référentiels
- Feature Flags
- Configurations App

Usage:
  python3 init_all.py              # Initialisation complète
  python3 init_all.py --iam-only   # IAM seulement
  python3 init_all.py --skip-iam   # Sans IAM
"""
import asyncio
import sys
import subprocess
from pathlib import Path
import argparse

SCRIPTS_DIR = Path(__file__).parent


def run_script(script_name, args=None):
    """Exécute un script Python"""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Script non trouvé: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}")
        print(e.stderr)
        return False


async def init_all(iam_only=False, skip_iam=False, skip_referentials=False, skip_flags=False, skip_configs=False):
    """Initialise tous les composants"""
    
    print("=" * 80)
    print("🚀 INITIALISATION COMPLÈTE DU SYSTÈME")
    print("=" * 80)
    print()
    
    success_count = 0
    total_count = 0
    
    components = []
    
    if not skip_iam and not iam_only:
        components.append(("IAM (Permissions, Bundles, Profils)", "init_iam_from_config.py", []))
    
    if iam_only:
        components.append(("IAM (Permissions, Bundles, Profils)", "init_iam_from_config.py", []))
    
    if not skip_referentials and not iam_only:
        components.append(("Référentiels", "init_referentials.py", []))
    
    if not skip_flags and not iam_only:
        components.append(("Feature Flags", "init_feature_flags.py", []))
    
    if not skip_configs and not iam_only:
        components.append(("Configurations App", "ensure_app_configs.py", []))
    
    total_count = len(components)
    
    for i, (name, script, args) in enumerate(components, 1):
        print(f"\n{'=' * 80}")
        print(f"📦 [{i}/{total_count}] Initialisation : {name}")
        print(f"{'=' * 80}\n")
        
        if run_script(script, args):
            success_count += 1
            print(f"\n✅ {name} : Succès")
        else:
            print(f"\n❌ {name} : Échec")
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE L'INITIALISATION")
    print("=" * 80)
    print(f"\nComposants initialisés : {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n✅ INITIALISATION COMPLÈTE RÉUSSIE !")
        print("\n🎉 Le système est prêt à être utilisé.")
    else:
        print(f"\n⚠️  {total_count - success_count} composant(s) en échec")
        print("Consultez les logs ci-dessus pour plus de détails.")
    
    print("\n💡 Vérifications recommandées:")
    print("   1. Connexion : http://localhost:3000/login")
    print("   2. Vérifier utilisateurs : python3 verify_and_align_users.py")
    print("   3. Tester API : curl http://localhost:8001/api/referentials/user_statuses")
    print("\n" + "=" * 80)
    
    return success_count == total_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialisation complète du système"
    )
    parser.add_argument(
        "--iam-only",
        action="store_true",
        help="Initialiser IAM seulement"
    )
    parser.add_argument(
        "--skip-iam",
        action="store_true",
        help="Sauter l'initialisation IAM"
    )
    parser.add_argument(
        "--skip-referentials",
        action="store_true",
        help="Sauter les référentiels"
    )
    parser.add_argument(
        "--skip-flags",
        action="store_true",
        help="Sauter les feature flags"
    )
    parser.add_argument(
        "--skip-configs",
        action="store_true",
        help="Sauter les configurations app"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(init_all(
        iam_only=args.iam_only,
        skip_iam=args.skip_iam,
        skip_referentials=args.skip_referentials,
        skip_flags=args.skip_flags,
        skip_configs=args.skip_configs
    ))
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Utilitaire pour chiffrer/déchiffrer les fichiers .env
Usage:
    python scripts/encrypt_env.py encrypt .env .env.encrypted
    python scripts/encrypt_env.py decrypt .env.encrypted .env
    python scripts/encrypt_env.py generate-key
"""
import sys
import argparse
from pathlib import Path
from cryptography.fernet import Fernet


def generate_key(key_file: str = ".env.key"):
    """Générer une nouvelle clé de chiffrement"""
    key = Fernet.generate_key()
    
    with open(key_file, 'wb') as f:
        f.write(key)
    
    print(f"✅ Clé générée et sauvegardée dans: {key_file}")
    print(f"⚠️  IMPORTANT: Gardez cette clé en sécurité et ne la commitez JAMAIS dans git!")
    print(f"   Ajoutez '{key_file}' à .gitignore")


def encrypt_file(input_file: str, output_file: str, key_file: str = ".env.key"):
    """Chiffrer un fichier .env"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    key_path = Path(key_file)
    
    if not input_path.exists():
        print(f"❌ Fichier source non trouvé: {input_file}")
        sys.exit(1)
    
    if not key_path.exists():
        print(f"❌ Clé de chiffrement non trouvée: {key_file}")
        print(f"   Générez-en une avec: python {sys.argv[0]} generate-key")
        sys.exit(1)
    
    # Lire la clé
    with open(key_path, 'rb') as f:
        key = f.read()
    
    fernet = Fernet(key)
    
    # Lire le fichier source
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Chiffrer
    encrypted_data = fernet.encrypt(data)
    
    # Écrire le fichier chiffré
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"✅ Fichier chiffré: {input_file} → {output_file}")
    print(f"   Vous pouvez maintenant commiter {output_file} dans git")
    print(f"   ⚠️  N'oubliez pas d'ajouter {input_file} et {key_file} à .gitignore")


def decrypt_file(input_file: str, output_file: str, key_file: str = ".env.key"):
    """Déchiffrer un fichier .env.encrypted"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    key_path = Path(key_file)
    
    if not input_path.exists():
        print(f"❌ Fichier chiffré non trouvé: {input_file}")
        sys.exit(1)
    
    if not key_path.exists():
        print(f"❌ Clé de déchiffrement non trouvée: {key_file}")
        print(f"   Demandez la clé à votre administrateur système")
        sys.exit(1)
    
    # Lire la clé
    with open(key_path, 'rb') as f:
        key = f.read()
    
    fernet = Fernet(key)
    
    # Lire le fichier chiffré
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    
    try:
        # Déchiffrer
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Écrire le fichier déchiffré
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        print(f"✅ Fichier déchiffré: {input_file} → {output_file}")
    except Exception as e:
        print(f"❌ Erreur lors du déchiffrement: {e}")
        print(f"   Vérifiez que vous utilisez la bonne clé")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Chiffrer/déchiffrer les fichiers .env",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Générer une clé de chiffrement
  python scripts/encrypt_env.py generate-key
  
  # Chiffrer un fichier .env
  python scripts/encrypt_env.py encrypt .env .env.encrypted
  
  # Déchiffrer un fichier .env.encrypted
  python scripts/encrypt_env.py decrypt .env.encrypted .env
  
  # Utiliser une clé personnalisée
  python scripts/encrypt_env.py encrypt .env .env.encrypted --key-file my.key
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Generate key
    parser_gen = subparsers.add_parser('generate-key', help='Générer une nouvelle clé')
    parser_gen.add_argument('--key-file', default='.env.key', help='Fichier de clé (défaut: .env.key)')
    
    # Encrypt
    parser_enc = subparsers.add_parser('encrypt', help='Chiffrer un fichier')
    parser_enc.add_argument('input', help='Fichier source (.env)')
    parser_enc.add_argument('output', help='Fichier de sortie (.env.encrypted)')
    parser_enc.add_argument('--key-file', default='.env.key', help='Fichier de clé (défaut: .env.key)')
    
    # Decrypt
    parser_dec = subparsers.add_parser('decrypt', help='Déchiffrer un fichier')
    parser_dec.add_argument('input', help='Fichier chiffré (.env.encrypted)')
    parser_dec.add_argument('output', help='Fichier de sortie (.env)')
    parser_dec.add_argument('--key-file', default='.env.key', help='Fichier de clé (défaut: .env.key)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'generate-key':
        generate_key(args.key_file)
    elif args.command == 'encrypt':
        encrypt_file(args.input, args.output, args.key_file)
    elif args.command == 'decrypt':
        decrypt_file(args.input, args.output, args.key_file)


if __name__ == '__main__':
    main()

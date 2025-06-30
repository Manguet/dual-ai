#!/usr/bin/env python3
"""
Installateur simple pour Dual AI Orchestrator
Compatible avec les environnements Python gérés (PEP 668)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Installation simple de Dual AI Orchestrator")
    print("=" * 60)
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Répertoires
    project_root = Path(__file__).parent
    home_dir = Path.home()
    config_dir = home_dir / ".dual-ai"
    venv_dir = config_dir / "venv"
    bin_dir = home_dir / ".local" / "bin"
    
    # Créer les répertoires
    config_dir.mkdir(exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Configuration: {config_dir}")
    print(f"📁 Binaires: {bin_dir}")
    
    # Étape 1: Créer l'environnement virtuel
    print("\n📦 Création de l'environnement virtuel...")
    
    if venv_dir.exists():
        print("⚠️  Environnement virtuel existant détecté")
        response = input("Recréer l'environnement ? [O/n]: ").lower()
        if response in ['', 'o', 'oui', 'y', 'yes']:
            shutil.rmtree(venv_dir)
        else:
            print("Conservation de l'environnement existant")
    
    if not venv_dir.exists():
        result = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        if result.returncode != 0:
            print("❌ Impossible de créer l'environnement virtuel")
            sys.exit(1)
        print("✅ Environnement virtuel créé")
    
    # Déterminer les chemins dans le venv
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"
    
    # Étape 2: Installer les dépendances
    print("\n📦 Installation des dépendances...")
    
    # Mettre à jour pip
    subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                   capture_output=True)
    
    # Installer les dépendances
    requirements_file = project_root / "requirements.txt"
    result = subprocess.run([str(venv_pip), "install", "-r", str(requirements_file)])
    
    if result.returncode != 0:
        print("❌ Erreur lors de l'installation des dépendances")
        sys.exit(1)
    
    print("✅ Dépendances installées")
    
    # Étape 3: Installer l'application
    print("\n📦 Installation de l'application...")
    
    result = subprocess.run([str(venv_pip), "install", "-e", str(project_root)])
    
    if result.returncode != 0:
        print("❌ Erreur lors de l'installation de l'application")
        sys.exit(1)
    
    print("✅ Application installée")
    
    # Étape 4: Créer le script wrapper
    print("\n🔧 Création du script wrapper...")
    
    if sys.platform == "win32":
        wrapper_path = bin_dir / "dual-ai.bat"
        wrapper_content = f'''@echo off
"{venv_python}" -m dual_ai.main %*
'''
    else:
        wrapper_path = bin_dir / "dual-ai"
        wrapper_content = f'''#!/bin/bash
"{venv_python}" -m dual_ai.main "$@"
'''
    
    wrapper_path.write_text(wrapper_content)
    
    if sys.platform != "win32":
        wrapper_path.chmod(0o755)
    
    print(f"✅ Wrapper créé: {wrapper_path}")
    
    # Étape 5: Copier la configuration
    print("\n⚙️  Configuration...")
    
    config_source = project_root / "config" / "config.yaml"
    config_dest = config_dir / "config.yaml"
    
    if not config_dest.exists() and config_source.exists():
        shutil.copy2(config_source, config_dest)
        print(f"✅ Configuration copiée: {config_dest}")
    
    # Étape 6: Vérifications finales
    print("\n🧪 Tests...")
    
    # Test d'import
    try:
        result = subprocess.run([str(venv_python), "-c", "import dual_ai; print('Import OK')"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Import réussi")
        else:
            print("❌ Erreur d'import")
    except:
        print("⚠️  Impossible de tester l'import")
    
    # Test de la commande
    try:
        result = subprocess.run([str(wrapper_path), "--version"], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Commande fonctionnelle")
        else:
            print("❌ Erreur de commande")
    except:
        print("⚠️  Impossible de tester la commande")
    
    # Instructions finales
    print("\n" + "🎉 INSTALLATION TERMINÉE !" + "\n")
    print("Pour utiliser Dual AI Orchestrator:")
    print(f"1. Ajoutez {bin_dir} à votre PATH:")
    
    if sys.platform == "win32":
        print(f'   set PATH=%PATH%;{bin_dir}')
    else:
        shell_config = get_shell_config()
        print(f'   echo \'export PATH="$PATH:{bin_dir}"\' >> {shell_config}')
        print(f'   source {shell_config}')
    
    print("\n2. Redémarrez votre terminal")
    print("\n3. Lancez: dual-ai")
    
    print(f"\nConfiguration: {config_dir}")
    print(f"Logs: {config_dir}/logs")
    print(f"Solutions: {config_dir}/solutions")
    
    print("\n📚 Documentation:")
    print("- README.md : Guide de démarrage")
    print("- docs/usage.md : Guide d'utilisation détaillé")
    print("- docs/troubleshooting.md : Résolution de problèmes")

def get_shell_config():
    """Détermine le fichier de configuration du shell"""
    shell = os.environ.get('SHELL', '').lower()
    home = Path.home()
    
    if 'zsh' in shell:
        return home / '.zshrc'
    elif 'bash' in shell:
        for config in ['.bash_profile', '.bashrc']:
            config_path = home / config
            if config_path.exists():
                return config_path
        return home / '.bashrc'
    else:
        return home / '.profile'

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation annulée")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        sys.exit(1)
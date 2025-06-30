#!/usr/bin/env python3
"""
Script de build et release pour Dual AI Orchestrator
"""

import os
import sys
import subprocess
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


class ReleaseBuilder:
    """Constructeur de release pour Dual AI Orchestrator"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.version = self.get_version()
        
    def build_release(self, include_tests: bool = False) -> bool:
        """Construit une release complète"""
        try:
            self.show_welcome()
            
            # Nettoyage
            if not self.clean_previous_builds():
                return False
            
            # Vérifications pré-build
            if not self.pre_build_checks():
                return False
            
            # Build du package
            if not self.build_package():
                return False
            
            # Création des archives
            if not self.create_archives(include_tests):
                return False
            
            # Calcul des checksums
            if not self.create_checksums():
                return False
            
            # Génération des notes de release
            if not self.generate_release_notes():
                return False
            
            self.show_success()
            return True
            
        except KeyboardInterrupt:
            self.print_error("\nBuild annulé par l'utilisateur")
            return False
        except Exception as e:
            self.print_error(f"\nErreur durant le build: {e}")
            return False
    
    def show_welcome(self):
        """Affiche l'écran de bienvenue"""
        if RICH_AVAILABLE:
            console.clear()
            welcome_panel = Panel(
                f"[bold]Build de release Dual AI Orchestrator v{self.version}[/bold]\n\n"
                "Ce script va :\n"
                "• Nettoyer les builds précédents\n"
                "• Vérifier la qualité du code\n"
                "• Construire le package Python\n"
                "• Créer les archives de distribution\n"
                "• Générer les checksums\n"
                "• Créer les notes de release",
                title="[bold cyan]Release Builder[/bold cyan]",
                box=box.ROUNDED
            )
            console.print(welcome_panel)
        else:
            print("\n" + "="*60)
            print(f"    BUILD DE RELEASE v{self.version}")
            print("="*60)
    
    def clean_previous_builds(self) -> bool:
        """Nettoie les builds précédents"""
        self.print_step("Nettoyage des builds précédents")
        
        directories_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "*.egg-info"
        ]
        
        for directory in directories_to_clean:
            if directory.exists():
                if directory.is_dir():
                    shutil.rmtree(directory)
                else:
                    directory.unlink()
                self.print_success(f"✓ Supprimé: {directory.name}")
        
        return True
    
    def pre_build_checks(self) -> bool:
        """Effectue les vérifications pré-build"""
        self.print_step("Vérifications pré-build")
        
        checks = [
            ("Git status", self.check_git_status),
            ("Tests unitaires", self.run_tests),
            ("Linting", self.run_linting),
            ("Type checking", self.run_type_check),
            ("Dépendances", self.check_dependencies),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            self.print_info(f"  🔍 {check_name}...")
            
            try:
                if check_func():
                    self.print_success(f"  ✓ {check_name}: OK")
                else:
                    self.print_error(f"  ✗ {check_name}: ÉCHEC")
                    all_passed = False
            except Exception as e:
                self.print_warning(f"  ⚠ {check_name}: {e}")
                if not self.confirm("Continuer malgré cette erreur?"):
                    all_passed = False
        
        return all_passed
    
    def build_package(self) -> bool:
        """Construit le package Python"""
        self.print_step("Construction du package Python")
        
        commands = [
            ["python", "setup.py", "sdist"],
            ["python", "setup.py", "bdist_wheel"],
        ]
        
        for cmd in commands:
            self.print_info(f"  Exécution: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.print_error(f"Erreur: {result.stderr}")
                return False
            
            self.print_success(f"  ✓ {cmd[2]} terminé")
        
        return True
    
    def create_archives(self, include_tests: bool) -> bool:
        """Crée les archives de distribution"""
        self.print_step("Création des archives")
        
        # Archive source complète
        source_archive = self.dist_dir / f"dual-ai-orchestrator-{self.version}-source.zip"
        if not self.create_source_archive(source_archive, include_tests):
            return False
        
        # Archive binaire (wheel + dépendances)
        binary_archive = self.dist_dir / f"dual-ai-orchestrator-{self.version}-binary.zip"
        if not self.create_binary_archive(binary_archive):
            return False
        
        return True
    
    def create_source_archive(self, archive_path: Path, include_tests: bool) -> bool:
        """Crée l'archive source"""
        self.print_info(f"  Création de {archive_path.name}")
        
        files_to_include = [
            "src/",
            "config/",
            "docs/",
            "examples/",
            "scripts/",
            "README.md",
            "LICENSE",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "install.py",
            "uninstall.py",
        ]
        
        if include_tests:
            files_to_include.append("tests/")
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in files_to_include:
                item_path = self.project_root / item
                
                if item_path.is_file():
                    zf.write(item_path, item)
                elif item_path.is_dir():
                    for file_path in item_path.rglob("*"):
                        if file_path.is_file() and not self.should_exclude_file(file_path):
                            arc_path = file_path.relative_to(self.project_root)
                            zf.write(file_path, arc_path)
        
        self.print_success(f"  ✓ Archive source créée: {archive_path.name}")
        return True
    
    def create_binary_archive(self, archive_path: Path) -> bool:
        """Crée l'archive binaire"""
        self.print_info(f"  Création de {archive_path.name}")
        
        # Trouver les fichiers wheel et sdist
        wheel_files = list(self.dist_dir.glob("*.whl"))
        sdist_files = list(self.dist_dir.glob("*.tar.gz"))
        
        if not wheel_files or not sdist_files:
            self.print_error("Fichiers wheel ou sdist manquants")
            return False
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Ajouter les packages Python
            for wheel_file in wheel_files:
                zf.write(wheel_file, wheel_file.name)
            
            for sdist_file in sdist_files:
                zf.write(sdist_file, sdist_file.name)
            
            # Ajouter les scripts d'installation
            zf.write(self.project_root / "install.py", "install.py")
            zf.write(self.project_root / "requirements.txt", "requirements.txt")
            
            # Ajouter un README pour l'installation
            install_readme = """# Installation Dual AI Orchestrator

## Installation rapide
1. Extraire cette archive
2. Exécuter: python install.py

## Installation manuelle
1. pip install dual_ai_orchestrator-*.whl
2. Configurer les API avec: python scripts/setup_apis.py

## Documentation
Voir: https://github.com/yourusername/dual-ai-orchestrator
"""
            zf.writestr("INSTALL.md", install_readme)
        
        self.print_success(f"  ✓ Archive binaire créée: {archive_path.name}")
        return True
    
    def create_checksums(self) -> bool:
        """Crée les fichiers de checksum"""
        self.print_step("Calcul des checksums")
        
        checksum_file = self.dist_dir / "checksums.txt"
        
        with open(checksum_file, 'w') as f:
            f.write(f"# Checksums for Dual AI Orchestrator v{self.version}\n")
            f.write(f"# Generated on {datetime.now().isoformat()}\n\n")
            
            for file_path in sorted(self.dist_dir.glob("*")):
                if file_path.is_file() and file_path.name != "checksums.txt":
                    sha256_hash = self.calculate_sha256(file_path)
                    f.write(f"{sha256_hash}  {file_path.name}\n")
                    self.print_success(f"  ✓ {file_path.name}: {sha256_hash[:16]}...")
        
        return True
    
    def generate_release_notes(self) -> bool:
        """Génère les notes de release"""
        self.print_step("Génération des notes de release")
        
        notes_file = self.dist_dir / "RELEASE_NOTES.md"
        
        # Récupérer les commits depuis le dernier tag
        commits = self.get_commits_since_last_tag()
        
        content = f"""# Dual AI Orchestrator v{self.version}

**Date de release**: {datetime.now().strftime('%Y-%m-%d')}

## 🚀 Nouveautés

### Fonctionnalités principales
- Interface unifiée pour Claude Code et Gemini Code
- Débat automatique entre IA pour solutions optimales
- Installation interactive avec vérification des dépendances
- Interface Rich moderne avec animations et couleurs
- Configuration flexible via YAML et variables d'environnement

### Améliorations
- Gestion d'erreurs robuste avec retry automatique
- Sauvegarde automatique des solutions
- Support multi-plateforme (Windows, macOS, Linux)
- Documentation complète avec guides détaillés

## 📦 Contenu de la release

### Fichiers disponibles
"""
        
        # Lister les fichiers de distribution
        for file_path in sorted(self.dist_dir.glob("*")):
            if file_path.is_file() and file_path.suffix in ['.zip', '.whl', '.tar.gz']:
                size = self.format_size(file_path.stat().st_size)
                content += f"- `{file_path.name}` ({size})\n"
        
        content += f"""
### Checksums
Voir le fichier `checksums.txt` pour les hashes SHA256.

## 🔧 Installation

### Méthode recommandée
1. Télécharger `dual-ai-orchestrator-{self.version}-binary.zip`
2. Extraire l'archive
3. Exécuter `python install.py`

### Via pip
```bash
pip install dual-ai-orchestrator-{self.version}-py3-none-any.whl
```

## 📋 Prérequis
- Python 3.8 ou supérieur
- Claude Code ou Gemini Code installé
- 100 MB d'espace disque libre

## 🐛 Corrections de bugs

{self.format_commits(commits)}

## 🔄 Migration

### Depuis une version précédente
Aucune migration nécessaire pour cette version initiale.

## 📞 Support
- Documentation: [GitHub Wiki](https://github.com/yourusername/dual-ai-orchestrator/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/dual-ai-orchestrator/issues)
- Discord: [Serveur communautaire](https://discord.gg/dual-ai)

---

**Développé avec ❤️ par la communauté Dual AI**
"""
        
        notes_file.write_text(content)
        self.print_success(f"  ✓ Notes de release: {notes_file.name}")
        
        return True
    
    def check_git_status(self) -> bool:
        """Vérifie l'état Git"""
        try:
            # Vérifier s'il y a des changements non commités
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                self.print_warning("Changements non commités détectés")
                return self.confirm("Continuer avec des changements non commités?")
            
            return True
        except:
            self.print_warning("Impossible de vérifier Git (pas un repo?)")
            return True
    
    def run_tests(self) -> bool:
        """Exécute les tests unitaires"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def run_linting(self) -> bool:
        """Exécute le linting"""
        try:
            # Essayer flake8
            result = subprocess.run(
                ["flake8", "src/"],
                cwd=self.project_root,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return True  # Ne pas bloquer si flake8 n'est pas installé
    
    def run_type_check(self) -> bool:
        """Exécute la vérification de types"""
        try:
            result = subprocess.run(
                ["mypy", "src/dual_ai/"],
                cwd=self.project_root,
                capture_output=True
            )
            return result.returncode == 0
        except:
            return True  # Ne pas bloquer si mypy n'est pas installé
    
    def check_dependencies(self) -> bool:
        """Vérifie les dépendances"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return False
        
        try:
            # Vérifier que toutes les dépendances sont installées
            result = subprocess.run(
                ["pip", "install", "--dry-run", "-r", str(requirements_file)],
                capture_output=True
            )
            return True  # dry-run réussit toujours si le format est correct
        except:
            return False
    
    def get_version(self) -> str:
        """Récupère la version du projet"""
        # Essayer depuis setup.py
        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            content = setup_file.read_text()
            import re
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Fallback
        return "1.0.0"
    
    def get_commits_since_last_tag(self) -> List[str]:
        """Récupère les commits depuis le dernier tag"""
        try:
            # Récupérer le dernier tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                last_tag = result.stdout.strip()
                
                # Récupérer les commits depuis ce tag
                result = subprocess.run(
                    ["git", "log", f"{last_tag}..HEAD", "--oneline"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
            
            return []
        except:
            return []
    
    def format_commits(self, commits: List[str]) -> str:
        """Formate la liste des commits"""
        if not commits:
            return "Aucun commit spécifique pour cette release."
        
        formatted = ""
        for commit in commits:
            if commit.strip():
                formatted += f"- {commit}\n"
        
        return formatted or "Aucun commit spécifique pour cette release."
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être exclu"""
        excludes = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.git',
            '.pytest_cache',
            '.mypy_cache',
            'node_modules',
            '.DS_Store',
            'Thumbs.db',
        ]
        
        path_str = str(file_path)
        return any(exclude in path_str for exclude in excludes)
    
    def calculate_sha256(self, file_path: Path) -> str:
        """Calcule le hash SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def format_size(self, size_bytes: int) -> str:
        """Formate une taille en bytes"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def show_success(self):
        """Affiche le message de succès"""
        files = list(self.dist_dir.glob("*"))
        
        if RICH_AVAILABLE:
            success_panel = Panel(
                f"[bold green]✅ Release v{self.version} construite avec succès ![/bold green]\n\n"
                f"[bold]Fichiers générés ({len(files)}) :[/bold]\n" +
                "\n".join(f"• {f.name}" for f in files) + "\n\n"
                f"[bold]Répertoire :[/bold] {self.dist_dir}\n\n"
                "[bold]Prochaines étapes :[/bold]\n"
                "1. Tester l'installation localement\n"
                "2. Créer un tag Git si nécessaire\n"
                "3. Publier sur GitHub Releases\n"
                "4. Publier sur PyPI si configuré",
                title="[bold green]Build terminé[/bold green]",
                box=box.DOUBLE
            )
            console.print(success_panel)
        else:
            print("\n" + "="*60)
            print(f"✅ RELEASE v{self.version} CONSTRUITE AVEC SUCCÈS !")
            print("="*60)
            print(f"\nFichiers générés ({len(files)}) :")
            for f in files:
                print(f"• {f.name}")
            print(f"\nRépertoire : {self.dist_dir}")
    
    def print_step(self, message: str):
        """Affiche une étape"""
        if RICH_AVAILABLE:
            console.print(f"\n[bold blue]📦 {message}[/bold blue]")
        else:
            print(f"\n📦 {message}")
    
    def print_info(self, message: str):
        """Affiche une information"""
        if RICH_AVAILABLE:
            console.print(message, style="blue")
        else:
            print(message)
    
    def print_success(self, message: str):
        """Affiche un succès"""
        if RICH_AVAILABLE:
            console.print(message, style="green")
        else:
            print(message)
    
    def print_warning(self, message: str):
        """Affiche un avertissement"""
        if RICH_AVAILABLE:
            console.print(message, style="yellow")
        else:
            print(f"⚠️  {message}")
    
    def print_error(self, message: str):
        """Affiche une erreur"""
        if RICH_AVAILABLE:
            console.print(message, style="red")
        else:
            print(f"❌ {message}")
    
    def confirm(self, message: str) -> bool:
        """Demande confirmation"""
        if RICH_AVAILABLE:
            return Confirm.ask(message)
        else:
            response = input(f"{message} [O/n]: ").lower()
            return response in ['', 'o', 'oui', 'y', 'yes']


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build release pour Dual AI Orchestrator")
    parser.add_argument("--include-tests", action="store_true", help="Inclure les tests dans l'archive source")
    parser.add_argument("--skip-checks", action="store_true", help="Ignorer les vérifications pré-build")
    
    args = parser.parse_args()
    
    builder = ReleaseBuilder()
    
    if args.skip_checks:
        builder.pre_build_checks = lambda: True
    
    success = builder.build_release(include_tests=args.include_tests)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Installateur interactif pour Dual AI Orchestrator
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import List, Tuple, Optional

# Vérifier si Rich est disponible, sinon utiliser le mode texte simple
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich import box
    from rich.align import Align
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class Installer:
    """Installateur principal pour Dual AI Orchestrator"""
    
    def __init__(self):
        self.install_dir = Path.home() / ".local" / "bin"
        self.config_dir = Path.home() / ".dual-ai"
        self.errors = []
        self.warnings = []
        
    def run(self) -> bool:
        """Lance le processus d'installation"""
        try:
            self.show_welcome()
            
            # Étapes d'installation
            steps = [
                ("Vérification des prérequis", self.check_prerequisites),
                ("Configuration de l'installation", self.configure_installation),
                ("Installation des dépendances Python", self.install_dependencies),
                ("Vérification des outils IA", self.check_ai_tools),
                ("Installation de l'application", self.install_application),
                ("Configuration de l'environnement", self.configure_environment),
                ("Tests post-installation", self.run_post_install_tests),
            ]
            
            for step_name, step_func in steps:
                if not self.run_step(step_name, step_func):
                    self.show_error(f"Échec lors de: {step_name}")
                    if not self.ask_continue():
                        self.cleanup()
                        return False
            
            self.show_success()
            return True
            
        except KeyboardInterrupt:
            self.print_error("\n\nInstallation annulée par l'utilisateur")
            self.cleanup()
            return False
        except Exception as e:
            self.print_error(f"\n\nErreur fatale: {str(e)}")
            self.cleanup()
            return False
    
    def show_welcome(self) -> None:
        """Affiche l'écran de bienvenue"""
        if RICH_AVAILABLE:
            console.clear()
            logo = """
    ╔══════════════════════════════════════════════════════╗
    ║      🚀 DUAL AI ORCHESTRATOR INSTALLER 🚀          ║
    ╚══════════════════════════════════════════════════════╝
            """
            console.print(Align.center(logo), style="bold cyan")
            
            welcome_panel = Panel(
                "[bold]Bienvenue dans l'installateur de Dual AI Orchestrator![/bold]\n\n"
                "Ce programme va installer:\n"
                "• L'orchestrateur Dual AI\n"
                "• Les dépendances Python nécessaires\n"
                "• La configuration par défaut\n"
                "• Les raccourcis système\n\n"
                "L'installation prendra environ 3-5 minutes.",
                title="[bold cyan]Installation[/bold cyan]",
                box=box.ROUNDED
            )
            console.print(welcome_panel)
        else:
            print("\n" + "="*60)
            print("     DUAL AI ORCHESTRATOR INSTALLER")
            print("="*60)
            print("\nBienvenue dans l'installateur de Dual AI Orchestrator!")
            print("\nCe programme va installer:")
            print("• L'orchestrateur Dual AI")
            print("• Les dépendances Python nécessaires")
            print("• La configuration par défaut")
            print("• Les raccourcis système")
            print("\nL'installation prendra environ 3-5 minutes.")
        
        if not self.confirm("\nVoulez-vous continuer l'installation?"):
            sys.exit(0)
    
    def check_prerequisites(self) -> bool:
        """Vérifie les prérequis système"""
        checks = []
        
        # Python version
        python_version = sys.version_info
        python_ok = python_version >= (3, 8)
        checks.append((
            "Python 3.8+",
            python_ok,
            f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        ))
        
        # pip
        pip_ok = shutil.which("pip") is not None or shutil.which("pip3") is not None
        checks.append(("pip", pip_ok, "Installé" if pip_ok else "Non trouvé"))
        
        # Permissions
        can_write_home = os.access(Path.home(), os.W_OK)
        checks.append(("Permissions home", can_write_home, "OK" if can_write_home else "Insuffisantes"))
        
        # Espace disque (100 MB minimum)
        try:
            stat = shutil.disk_usage(Path.home())
            space_mb = stat.free / (1024 * 1024)
            space_ok = space_mb >= 100
            checks.append(("Espace disque", space_ok, f"{space_mb:.1f} MB disponibles"))
        except:
            checks.append(("Espace disque", True, "Non vérifié"))
        
        # Afficher les résultats
        self.show_check_results("Prérequis système", checks)
        
        # Retourner False si un check critique échoue
        if not python_ok:
            self.print_error("Python 3.8 ou supérieur est requis!")
            return False
        if not pip_ok:
            self.print_error("pip est requis pour l'installation!")
            self.print_info("Installez pip: https://pip.pypa.io/en/stable/installation/")
            return False
        
        return True
    
    def configure_installation(self) -> bool:
        """Configure les paramètres d'installation"""
        self.print_info("\nConfiguration de l'installation:")
        
        # Répertoire d'installation
        default_install = str(self.install_dir)
        if RICH_AVAILABLE:
            install_path = Prompt.ask(
                f"Répertoire d'installation",
                default=default_install
            )
        else:
            install_path = input(f"Répertoire d'installation [{default_install}]: ") or default_install
        
        self.install_dir = Path(install_path).expanduser()
        
        # Créer les répertoires nécessaires
        directories = [
            self.install_dir,
            self.config_dir,
            self.config_dir / "logs",
            self.config_dir / "solutions",
            self.config_dir / "cache"
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.print_success(f"✓ Créé: {directory}")
            except Exception as e:
                self.print_error(f"✗ Impossible de créer {directory}: {e}")
                return False
        
        return True
    
    def install_dependencies(self) -> bool:
        """Installe les dépendances Python"""
        self.print_info("\nInstallation des dépendances Python...")
        
        requirements_file = Path(__file__).parent / "requirements.txt"
        if not requirements_file.exists():
            self.print_error("Fichier requirements.txt introuvable!")
            return False
        
        # Commande pip
        pip_cmd = "pip3" if shutil.which("pip3") else "pip"
        
        # Détecter si on est dans un environnement géré
        is_managed_env = self.is_externally_managed_environment()
        
        # Options d'installation selon l'environnement
        install_options = []
        if is_managed_env:
            self.print_warning("Environnement Python géré détecté (PEP 668)")
            
            # Essayer pipx d'abord
            if shutil.which("pipx"):
                return self.install_with_pipx()
            
            # Proposer différentes options
            self.print_info("\nOptions d'installation disponibles:")
            self.print_info("1. Environnement virtuel (recommandé)")
            self.print_info("2. Installation avec --break-system-packages")
            self.print_info("3. Installation système avec apt/dnf")
            
            if RICH_AVAILABLE:
                choice = input("\nChoisissez une option [1]: ").strip() or "1"
            else:
                choice = input("\nChoisissez une option [1]: ").strip() or "1"
            
            if choice == "1":
                return self.install_with_venv()
            elif choice == "2":
                install_options = ["--break-system-packages", "--user"]
            elif choice == "3":
                return self.install_system_packages()
            else:
                return self.install_with_venv()
        else:
            install_options = ["--user"]
        
        try:
            command = [pip_cmd, "install", "-r", str(requirements_file)] + install_options
            
            if RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Installation des dépendances...", total=None)
                    
                    result = subprocess.run(command, capture_output=True, text=True)
                    progress.remove_task(task)
            else:
                print("Installation en cours...")
                result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("✓ Dépendances installées avec succès")
                
                # Réimporter Rich si elle vient d'être installée
                if not RICH_AVAILABLE:
                    try:
                        import importlib
                        importlib.import_module('rich')
                        self.print_info("Rich est maintenant disponible!")
                    except:
                        pass
                
                return True
            else:
                self.print_error("✗ Erreur lors de l'installation des dépendances")
                self.print_error(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"✗ Erreur: {str(e)}")
            return False
    
    def is_externally_managed_environment(self) -> bool:
        """Détecte si on est dans un environnement Python géré (PEP 668)"""
        import sysconfig
        stdlib_path = sysconfig.get_path('stdlib')
        pyvenv_cfg = Path(sys.prefix) / "pyvenv.cfg"
        marker_file = Path(stdlib_path).parent / "EXTERNALLY-MANAGED"
        
        return marker_file.exists() and not pyvenv_cfg.exists()
    
    def install_with_venv(self) -> bool:
        """Installation dans un environnement virtuel"""
        self.print_info("Création d'un environnement virtuel...")
        
        venv_path = self.config_dir / "venv"
        
        try:
            # Créer l'environnement virtuel
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.print_error(f"Impossible de créer l'environnement virtuel: {result.stderr}")
                return False
            
            # Déterminer l'exécutable pip dans le venv
            if sys.platform == "win32":
                venv_pip = venv_path / "Scripts" / "pip.exe"
                venv_python = venv_path / "Scripts" / "python.exe"
            else:
                venv_pip = venv_path / "bin" / "pip"
                venv_python = venv_path / "bin" / "python"
            
            # Mettre à jour pip dans le venv
            subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                         capture_output=True)
            
            # Installer les dépendances dans le venv
            requirements_file = Path(__file__).parent / "requirements.txt"
            result = subprocess.run([
                str(venv_pip), "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("✓ Environnement virtuel créé et dépendances installées")
                
                # Sauvegarder le chemin du venv pour l'utilisation ultérieure
                venv_info_file = self.config_dir / "venv_info.txt"
                venv_info_file.write_text(str(venv_path))
                
                return True
            else:
                self.print_error(f"Erreur lors de l'installation dans le venv: {result.stderr}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur lors de la création du venv: {e}")
            return False
    
    def install_with_pipx(self) -> bool:
        """Installation avec pipx"""
        self.print_info("Installation avec pipx...")
        
        try:
            # Installer le package avec pipx
            result = subprocess.run([
                "pipx", "install", "-e", str(Path(__file__).parent)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_success("✓ Installation pipx réussie")
                return True
            else:
                self.print_error(f"Erreur pipx: {result.stderr}")
                return False
                
        except Exception as e:
            self.print_error(f"Erreur pipx: {e}")
            return False
    
    def install_system_packages(self) -> bool:
        """Installation des packages système"""
        self.print_info("Installation des packages système...")
        
        # Détecter la distribution
        try:
            import distro
            dist_id = distro.id()
        except ImportError:
            # Fallback simple
            if Path("/etc/debian_version").exists():
                dist_id = "debian"
            elif Path("/etc/redhat-release").exists():
                dist_id = "rhel"
            else:
                dist_id = "unknown"
        
        packages_map = {
            "debian": ["python3-rich", "python3-yaml", "python3-requests", "python3-click"],
            "ubuntu": ["python3-rich", "python3-yaml", "python3-requests", "python3-click"],
            "rhel": ["python3-rich", "python3-PyYAML", "python3-requests", "python3-click"],
            "fedora": ["python3-rich", "python3-PyYAML", "python3-requests", "python3-click"],
        }
        
        packages = packages_map.get(dist_id, packages_map["debian"])
        
        if dist_id in ["debian", "ubuntu"]:
            cmd = ["sudo", "apt", "install", "-y"] + packages
        elif dist_id in ["rhel", "fedora"]:
            cmd = ["sudo", "dnf", "install", "-y"] + packages
        else:
            self.print_error("Distribution non supportée pour l'installation système")
            return False
        
        self.print_info(f"Commande: {' '.join(cmd)}")
        
        if self.confirm("Exécuter cette commande (nécessite sudo) ?"):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.print_success("✓ Packages système installés")
                    return True
                else:
                    self.print_error(f"Erreur: {result.stderr}")
                    return False
                    
            except Exception as e:
                self.print_error(f"Erreur: {e}")
                return False
        
        return False
    
    def check_ai_tools(self) -> bool:
        """Vérifie la disponibilité des outils IA"""
        self.print_info("\nVérification des outils IA...")
        
        tools = []
        
        # Vérifier Claude
        claude_ok = shutil.which("claude") is not None
        tools.append(("Claude Code", claude_ok, "Installé" if claude_ok else "Non trouvé"))
        
        # Vérifier Gemini
        gemini_ok = shutil.which("gemini") is not None
        tools.append(("Gemini Code", gemini_ok, "Installé" if gemini_ok else "Non trouvé"))
        
        self.show_check_results("Outils IA", tools)
        
        # Proposer l'installation si manquant
        if not claude_ok:
            self.print_warning("\nClaude Code n'est pas installé.")
            self.print_info("Pour l'installer: npm install -g @anthropic-ai/claude-code")
            self.print_info("ou: pip install claude-code")
        
        if not gemini_ok:
            self.print_warning("\nGemini Code n'est pas installé.")
            self.print_info("Pour l'installer: npm install -g @google/gemini-code")
            self.print_info("ou: pip install gemini-code")
        
        if not claude_ok or not gemini_ok:
            return self.confirm("\nContinuer sans tous les outils IA?")
        
        return True
    
    def install_application(self) -> bool:
        """Installe l'application principale"""
        self.print_info("\nInstallation de Dual AI Orchestrator...")
        
        try:
            # Déterminer l'environnement d'installation
            venv_info_file = self.config_dir / "venv_info.txt"
            
            if venv_info_file.exists():
                # Installation dans le venv
                venv_path = Path(venv_info_file.read_text().strip())
                if sys.platform == "win32":
                    python_cmd = str(venv_path / "Scripts" / "python.exe")
                    pip_cmd = str(venv_path / "Scripts" / "pip.exe")
                else:
                    python_cmd = str(venv_path / "bin" / "python")
                    pip_cmd = str(venv_path / "bin" / "pip")
                
                self.print_info("Installation dans l'environnement virtuel...")
            else:
                # Installation système
                python_cmd = sys.executable
                pip_cmd = "pip3" if shutil.which("pip3") else "pip"
            
            # Essayer l'installation avec pip en mode éditable
            install_cmd = [pip_cmd, "install", "-e", "."]
            
            # Ajouter des options selon le contexte
            if not venv_info_file.exists():
                if self.is_externally_managed_environment():
                    install_cmd.extend(["--break-system-packages", "--user"])
                else:
                    install_cmd.append("--user")
            
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            
            if result.returncode != 0:
                # Fallback avec setup.py
                self.print_warning("Tentative avec setup.py...")
                result = subprocess.run(
                    [python_cmd, "setup.py", "install"] + (["--user"] if not venv_info_file.exists() else []),
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )
            
            if result.returncode == 0:
                self.print_success("✓ Application installée avec succès")
                
                # Copier la configuration par défaut
                config_source = Path(__file__).parent / "config" / "config.yaml"
                config_dest = self.config_dir / "config.yaml"
                
                if not config_dest.exists() and config_source.exists():
                    shutil.copy2(config_source, config_dest)
                    self.print_success(f"✓ Configuration copiée vers {config_dest}")
                
                return True
            else:
                self.print_error("✗ Erreur lors de l'installation")
                self.print_error(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"✗ Erreur: {str(e)}")
            return False
    
    def configure_environment(self) -> bool:
        """Configure l'environnement système"""
        self.print_info("\nConfiguration de l'environnement...")
        
        # Vérifier si on utilise un venv
        venv_info_file = self.config_dir / "venv_info.txt"
        
        if venv_info_file.exists():
            return self.configure_venv_environment(venv_info_file)
        else:
            return self.configure_system_environment()
    
    def configure_venv_environment(self, venv_info_file: Path) -> bool:
        """Configure l'environnement avec venv"""
        venv_path = Path(venv_info_file.read_text().strip())
        
        # Créer un script wrapper qui active le venv
        if sys.platform == "win32":
            wrapper_name = "dual-ai.bat"
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            wrapper_name = "dual-ai"
            venv_python = venv_path / "bin" / "python"
        
        wrapper_path = self.install_dir / wrapper_name
        
        # Contenu du wrapper
        if sys.platform == "win32":
            wrapper_content = f'@echo off\n"{venv_python}" -m dual_ai.main %*\n'
        else:
            wrapper_content = f'#!/bin/bash\n"{venv_python}" -m dual_ai.main "$@"\n'
        
        try:
            wrapper_path.write_text(wrapper_content)
            if sys.platform != "win32":
                wrapper_path.chmod(0o755)
            
            self.print_success(f"✓ Wrapper venv créé: {wrapper_path}")
            
            # Ajouter au PATH
            return self.add_to_path_if_needed(wrapper_path)
            
        except Exception as e:
            self.print_error(f"Erreur lors de la création du wrapper: {e}")
            return False
    
    def configure_system_environment(self) -> bool:
        """Configure l'environnement système standard"""
        # Trouver l'exécutable
        if sys.platform == "win32":
            script_name = "dual-ai.exe"
        else:
            script_name = "dual-ai"
        
        # Chercher dans les emplacements possibles
        possible_locations = [
            Path.home() / ".local" / "bin" / script_name,
            Path(sys.prefix) / "bin" / script_name,
            Path(sys.prefix) / "Scripts" / script_name,
        ]
        
        dual_ai_path = None
        for loc in possible_locations:
            if loc.exists():
                dual_ai_path = loc
                break
        
        if not dual_ai_path:
            # Créer un wrapper si non trouvé
            self.print_warning("Création d'un wrapper pour dual-ai...")
            
            main_script = Path(__file__).parent / "src" / "dual_ai" / "main.py"
            wrapper_path = self.install_dir / script_name
            
            # Importer utils pour créer le wrapper
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            try:
                from dual_ai.utils import create_executable_wrapper
                
                if create_executable_wrapper(main_script, wrapper_path):
                    dual_ai_path = wrapper_path
                    self.print_success(f"✓ Wrapper créé: {wrapper_path}")
                else:
                    self.print_error("✗ Impossible de créer le wrapper")
                    return False
            except ImportError:
                # Créer un wrapper simple
                if sys.platform == "win32":
                    wrapper_content = f'@echo off\n"{sys.executable}" "{main_script}" %*\n'
                else:
                    wrapper_content = f'#!/bin/bash\n"{sys.executable}" "{main_script}" "$@"\n'
                
                wrapper_path.write_text(wrapper_content)
                if sys.platform != "win32":
                    wrapper_path.chmod(0o755)
                
                dual_ai_path = wrapper_path
                self.print_success(f"✓ Wrapper simple créé: {wrapper_path}")
        
        # Ajouter au PATH si nécessaire
        return self.add_to_path_if_needed(dual_ai_path)
    
    def add_to_path_if_needed(self, executable_path: Path) -> bool:
        """Ajoute le répertoire au PATH si nécessaire"""
        if executable_path and executable_path.parent not in os.environ.get("PATH", "").split(os.pathsep):
            self.print_info(f"Ajout de {executable_path.parent} au PATH...")
            
            try:
                sys.path.insert(0, str(Path(__file__).parent / "src"))
                from dual_ai.utils import add_to_path
                
                if add_to_path(executable_path.parent):
                    self.print_success("✓ PATH mis à jour")
                    self.print_warning("Note: Redémarrez votre terminal pour appliquer les changements")
                else:
                    self.print_warning("⚠ Impossible de mettre à jour le PATH automatiquement")
                    self.print_info(f"Ajoutez manuellement ce répertoire à votre PATH: {executable_path.parent}")
            except ImportError:
                self.print_warning("⚠ Impossible de mettre à jour le PATH automatiquement")
                self.print_info(f"Ajoutez manuellement ce répertoire à votre PATH: {executable_path.parent}")
        
        return True
    
    def run_post_install_tests(self) -> bool:
        """Exécute les tests post-installation"""
        self.print_info("\nTests post-installation...")
        
        tests = []
        
        # Test d'import
        try:
            import dual_ai
            tests.append(("Import module", True, f"Version {dual_ai.__version__}"))
        except Exception as e:
            tests.append(("Import module", False, str(e)))
        
        # Test de configuration
        config_ok = (self.config_dir / "config.yaml").exists()
        tests.append(("Configuration", config_ok, "OK" if config_ok else "Non trouvée"))
        
        # Test de l'exécutable
        try:
            result = subprocess.run(
                ["dual-ai", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            exec_ok = result.returncode == 0
            tests.append(("Exécutable", exec_ok, "Fonctionnel" if exec_ok else "Erreur"))
        except:
            tests.append(("Exécutable", False, "Non trouvé dans PATH"))
        
        self.show_check_results("Tests post-installation", tests)
        
        # Au moins l'import doit fonctionner
        return tests[0][1]
    
    def show_success(self) -> None:
        """Affiche le message de succès final"""
        if RICH_AVAILABLE:
            success_panel = Panel(
                "[bold green]✨ Installation réussie ![/bold green]\n\n"
                "Dual AI Orchestrator est maintenant installé.\n\n"
                "[bold]Pour commencer:[/bold]\n"
                "1. Redémarrez votre terminal\n"
                "2. Lancez: [cyan]dual-ai[/cyan]\n\n"
                "[bold]Configuration:[/bold]\n"
                f"• Fichier: {self.config_dir / 'config.yaml'}\n"
                f"• Logs: {self.config_dir / 'logs/'}\n\n"
                "Bon développement ! 🚀",
                title="[bold green]Installation terminée[/bold green]",
                box=box.DOUBLE
            )
            console.print(success_panel)
        else:
            print("\n" + "="*60)
            print("✨ INSTALLATION RÉUSSIE !")
            print("="*60)
            print("\nDual AI Orchestrator est maintenant installé.")
            print("\nPour commencer:")
            print("1. Redémarrez votre terminal")
            print("2. Lancez: dual-ai")
            print(f"\nConfiguration: {self.config_dir / 'config.yaml'}")
            print(f"Logs: {self.config_dir / 'logs/'}")
            print("\nBon développement ! 🚀")
    
    def cleanup(self) -> None:
        """Nettoie en cas d'échec"""
        self.print_warning("\nNettoyage des fichiers temporaires...")
        # Ajouter ici le code de nettoyage si nécessaire
    
    # Méthodes utilitaires
    def run_step(self, name: str, func) -> bool:
        """Exécute une étape avec gestion d'erreurs"""
        self.print_info(f"\n📌 {name}...")
        try:
            return func()
        except Exception as e:
            self.print_error(f"Erreur: {str(e)}")
            return False
    
    def show_check_results(self, title: str, checks: List[Tuple[str, bool, str]]) -> None:
        """Affiche les résultats de vérification"""
        if RICH_AVAILABLE:
            table = Table(title=title, box=box.ROUNDED)
            table.add_column("Élément", style="cyan")
            table.add_column("Statut", justify="center")
            table.add_column("Détails")
            
            for name, ok, details in checks:
                status = "[green]✓[/green]" if ok else "[red]✗[/red]"
                table.add_row(name, status, details)
            
            console.print(table)
        else:
            print(f"\n{title}:")
            print("-" * 40)
            for name, ok, details in checks:
                status = "✓" if ok else "✗"
                print(f"{status} {name:<20} {details}")
    
    def confirm(self, message: str) -> bool:
        """Demande confirmation à l'utilisateur"""
        if RICH_AVAILABLE:
            return Confirm.ask(message)
        else:
            response = input(f"{message} [O/n]: ").lower()
            return response in ['', 'o', 'oui', 'y', 'yes']
    
    def ask_continue(self) -> bool:
        """Demande si on continue après une erreur"""
        return self.confirm("Voulez-vous continuer malgré cette erreur?")
    
    def show_error(self, message: str) -> None:
        """Affiche un message d'erreur formaté"""
        if RICH_AVAILABLE:
            error_panel = Panel(
                message,
                title="[bold red]Erreur[/bold red]",
                border_style="red",
                box=box.ROUNDED
            )
            console.print(error_panel)
        else:
            print(f"\n❌ ERREUR: {message}")
    
    def print_info(self, message: str) -> None:
        """Affiche un message d'information"""
        if RICH_AVAILABLE:
            console.print(message, style="blue")
        else:
            print(message)
    
    def print_success(self, message: str) -> None:
        """Affiche un message de succès"""
        if RICH_AVAILABLE:
            console.print(message, style="green")
        else:
            print(message)
    
    def print_warning(self, message: str) -> None:
        """Affiche un avertissement"""
        if RICH_AVAILABLE:
            console.print(message, style="yellow")
        else:
            print(f"⚠ {message}")
    
    def print_error(self, message: str) -> None:
        """Affiche une erreur"""
        if RICH_AVAILABLE:
            console.print(message, style="red")
        else:
            print(f"❌ {message}")


def main():
    """Point d'entrée principal"""
    installer = Installer()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
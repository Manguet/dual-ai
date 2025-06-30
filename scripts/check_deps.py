#!/usr/bin/env python3
"""
Vérificateur de dépendances pour Dual AI Orchestrator
"""

import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import List, Tuple, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


class DependencyChecker:
    """Vérificateur complet des dépendances"""
    
    def __init__(self):
        self.results = []
        self.warnings = []
        self.errors = []
    
    def check_all(self) -> bool:
        """Vérifie toutes les dépendances"""
        checks = [
            ("Système", self.check_system),
            ("Python", self.check_python),
            ("Modules Python", self.check_python_modules),
            ("Outils IA", self.check_ai_tools),
            ("Réseau", self.check_network),
            ("Permissions", self.check_permissions),
            ("Espace disque", self.check_disk_space),
        ]
        
        all_ok = True
        
        for category, check_func in checks:
            self.print_section(category)
            try:
                if not check_func():
                    all_ok = False
            except Exception as e:
                self.print_error(f"Erreur lors de la vérification {category}: {e}")
                all_ok = False
        
        self.show_summary()
        return all_ok
    
    def check_system(self) -> bool:
        """Vérifie les informations système"""
        system_info = {
            "OS": platform.system(),
            "Version": platform.version(),
            "Architecture": platform.machine(),
            "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
        
        if RICH_AVAILABLE:
            table = Table(title="Informations système")
            table.add_column("Élément", style="cyan")
            table.add_column("Valeur")
            
            for key, value in system_info.items():
                table.add_row(key, value)
            
            console.print(table)
        else:
            print("Informations système:")
            for key, value in system_info.items():
                print(f"  {key}: {value}")
        
        return True
    
    def check_python(self) -> bool:
        """Vérifie Python et pip"""
        checks = []
        
        # Version Python
        python_version = sys.version_info
        python_ok = python_version >= (3, 8)
        checks.append((
            "Python 3.8+",
            python_ok,
            f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "Mettre à jour Python" if not python_ok else ""
        ))
        
        # pip
        pip_cmd = self.find_pip()
        pip_ok = pip_cmd is not None
        checks.append((
            "pip",
            pip_ok,
            pip_cmd or "Non trouvé",
            "Installer pip" if not pip_ok else ""
        ))
        
        # pip version
        if pip_ok:
            try:
                result = subprocess.run(
                    [pip_cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                pip_version = result.stdout.strip() if result.returncode == 0 else "Erreur"
            except:
                pip_version = "Timeout"
            
            checks.append((
                "Version pip",
                True,
                pip_version,
                ""
            ))
        
        self.show_checks_table("Python", checks)
        return all(check[1] for check in checks[:2])  # Python et pip requis
    
    def check_python_modules(self) -> bool:
        """Vérifie les modules Python requis"""
        required_modules = [
            ("rich", "Interface utilisateur moderne"),
            ("yaml", "Configuration YAML"),
            ("requests", "Requêtes HTTP"),
            ("click", "Interface ligne de commande"),
            ("colorama", "Couleurs terminal"),
        ]
        
        checks = []
        
        for module_name, description in required_modules:
            try:
                if module_name == "yaml":
                    import yaml
                else:
                    __import__(module_name)
                
                # Récupérer la version si possible
                try:
                    module = sys.modules[module_name]
                    version = getattr(module, '__version__', 'N/A')
                except:
                    version = "Installé"
                
                checks.append((
                    f"{module_name}",
                    True,
                    version,
                    ""
                ))
            except ImportError:
                checks.append((
                    f"{module_name}",
                    False,
                    "Non installé",
                    f"pip install {module_name}"
                ))
        
        self.show_checks_table("Modules Python", checks)
        return all(check[1] for check in checks)
    
    def check_ai_tools(self) -> bool:
        """Vérifie les outils IA"""
        tools = [
            ("claude", "Claude Code"),
            ("gemini", "Gemini Code"),
        ]
        
        checks = []
        
        for command, name in tools:
            if shutil.which(command):
                # Essayer d'obtenir la version
                try:
                    result = subprocess.run(
                        [command, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    version = result.stdout.strip() if result.returncode == 0 else "Installé"
                except:
                    version = "Installé"
                
                checks.append((
                    name,
                    True,
                    version,
                    ""
                ))
            else:
                install_cmd = f"npm install -g @anthropic-ai/{command}-code" if command == "claude" else f"npm install -g @google/{command}-code"
                checks.append((
                    name,
                    False,
                    "Non trouvé",
                    install_cmd
                ))
        
        self.show_checks_table("Outils IA", checks)
        
        # Au moins un outil doit être disponible
        available_tools = sum(1 for check in checks if check[1])
        if available_tools == 0:
            self.warnings.append("Aucun outil IA trouvé. L'application ne pourra pas fonctionner.")
            return False
        elif available_tools == 1:
            self.warnings.append("Un seul outil IA trouvé. Fonctionnalité limitée.")
        
        return True
    
    def check_network(self) -> bool:
        """Vérifie la connectivité réseau"""
        hosts_to_check = [
            ("anthropic.com", "API Claude"),
            ("google.com", "API Gemini"),
            ("pypi.org", "Repository Python"),
        ]
        
        checks = []
        
        for host, description in hosts_to_check:
            try:
                import socket
                socket.create_connection((host, 443), timeout=5)
                checks.append((
                    f"{description} ({host})",
                    True,
                    "Accessible",
                    ""
                ))
            except Exception as e:
                checks.append((
                    f"{description} ({host})",
                    False,
                    f"Erreur: {type(e).__name__}",
                    "Vérifier la connexion réseau"
                ))
        
        self.show_checks_table("Connectivité réseau", checks)
        return any(check[1] for check in checks)  # Au moins une connexion
    
    def check_permissions(self) -> bool:
        """Vérifie les permissions"""
        paths_to_check = [
            (Path.home(), "Répertoire home"),
            (Path.home() / ".dual-ai", "Répertoire config"),
            (Path.home() / ".local" / "bin", "Répertoire bin"),
        ]
        
        checks = []
        
        for path, description in paths_to_check:
            try:
                # Tester création/écriture
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    created = True
                else:
                    created = False
                
                # Tester écriture
                test_file = path / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                
                status = "OK (créé)" if created else "OK"
                checks.append((
                    description,
                    True,
                    status,
                    ""
                ))
            except Exception as e:
                checks.append((
                    description,
                    False,
                    f"Erreur: {type(e).__name__}",
                    "Vérifier les permissions"
                ))
        
        self.show_checks_table("Permissions", checks)
        return all(check[1] for check in checks)
    
    def check_disk_space(self) -> bool:
        """Vérifie l'espace disque"""
        try:
            stat = shutil.disk_usage(Path.home())
            free_mb = stat.free / (1024 * 1024)
            free_gb = free_mb / 1024
            
            required_mb = 100  # 100 MB minimum
            space_ok = free_mb >= required_mb
            
            if free_gb >= 1:
                size_str = f"{free_gb:.1f} GB"
            else:
                size_str = f"{free_mb:.1f} MB"
            
            checks = [(
                "Espace libre",
                space_ok,
                size_str,
                "Libérer de l'espace disque" if not space_ok else ""
            )]
            
            self.show_checks_table("Espace disque", checks)
            return space_ok
            
        except Exception as e:
            self.print_error(f"Impossible de vérifier l'espace disque: {e}")
            return True  # Ne pas bloquer pour cette erreur
    
    def find_pip(self) -> Optional[str]:
        """Trouve la commande pip disponible"""
        for cmd in ["pip3", "pip"]:
            if shutil.which(cmd):
                return cmd
        return None
    
    def show_checks_table(self, title: str, checks: List[Tuple[str, bool, str, str]]):
        """Affiche un tableau de vérifications"""
        if RICH_AVAILABLE:
            table = Table(title=title, box=box.ROUNDED)
            table.add_column("Élément", style="cyan")
            table.add_column("Statut", justify="center")
            table.add_column("Détails")
            table.add_column("Action recommandée")
            
            for name, ok, details, action in checks:
                status = "[green]✓[/green]" if ok else "[red]✗[/red]"
                action_str = action if action else "[dim]Aucune[/dim]"
                table.add_row(name, status, details, action_str)
            
            console.print(table)
        else:
            print(f"\n{title}:")
            print("-" * 60)
            for name, ok, details, action in checks:
                status = "✓" if ok else "✗"
                print(f"{status} {name:<25} {details}")
                if action:
                    print(f"    → {action}")
    
    def show_summary(self):
        """Affiche le résumé final"""
        if RICH_AVAILABLE:
            if self.errors:
                error_panel = Panel(
                    "\n".join(self.errors),
                    title="[bold red]Erreurs critiques[/bold red]",
                    border_style="red"
                )
                console.print(error_panel)
            
            if self.warnings:
                warning_panel = Panel(
                    "\n".join(self.warnings),
                    title="[bold yellow]Avertissements[/bold yellow]",
                    border_style="yellow"
                )
                console.print(warning_panel)
            
            if not self.errors and not self.warnings:
                success_panel = Panel(
                    "Toutes les dépendances sont satisfaites !",
                    title="[bold green]Succès[/bold green]",
                    border_style="green"
                )
                console.print(success_panel)
        else:
            if self.errors:
                print("\nERREURS CRITIQUES:")
                for error in self.errors:
                    print(f"  ❌ {error}")
            
            if self.warnings:
                print("\nAVERTISSEMENTS:")
                for warning in self.warnings:
                    print(f"  ⚠️  {warning}")
            
            if not self.errors and not self.warnings:
                print("\n✅ Toutes les dépendances sont satisfaites !")
    
    def print_section(self, title: str):
        """Affiche le titre d'une section"""
        if RICH_AVAILABLE:
            console.print(f"\n[bold blue]🔍 {title}[/bold blue]")
        else:
            print(f"\n🔍 {title}")
            print("=" * 40)
    
    def print_error(self, message: str):
        """Affiche une erreur"""
        self.errors.append(message)
        if RICH_AVAILABLE:
            console.print(f"[red]❌ {message}[/red]")
        else:
            print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Affiche un avertissement"""
        self.warnings.append(message)
        if RICH_AVAILABLE:
            console.print(f"[yellow]⚠️  {message}[/yellow]")
        else:
            print(f"⚠️  {message}")


def main():
    """Point d'entrée principal"""
    if RICH_AVAILABLE:
        console.print("\n[bold cyan]🔍 Vérificateur de dépendances Dual AI Orchestrator[/bold cyan]\n")
    else:
        print("\n🔍 Vérificateur de dépendances Dual AI Orchestrator\n")
        print("=" * 60)
    
    checker = DependencyChecker()
    success = checker.check_all()
    
    print(f"\n{'✅ Vérification terminée avec succès !' if success else '❌ Problèmes détectés.'}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
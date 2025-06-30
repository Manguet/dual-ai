#!/usr/bin/env python3
"""
Désinstallateur pour Dual AI Orchestrator
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


class Uninstaller:
    """Désinstallateur pour Dual AI Orchestrator"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".dual-ai"
        self.install_dirs = [
            Path.home() / ".local" / "bin",
            Path(sys.prefix) / "bin",
            Path(sys.prefix) / "Scripts",
        ]
        self.items_to_remove = []
        
    def run(self) -> bool:
        """Lance le processus de désinstallation"""
        try:
            self.show_welcome()
            
            # Rechercher les éléments installés
            self.find_installed_items()
            
            if not self.items_to_remove:
                self.print_info("Aucune installation de Dual AI Orchestrator trouvée.")
                return True
            
            # Afficher ce qui sera supprimé
            self.show_items_to_remove()
            
            # Demander confirmation
            if not self.confirm("\nVoulez-vous procéder à la désinstallation?"):
                self.print_info("Désinstallation annulée.")
                return False
            
            # Désinstaller
            self.uninstall_package()
            self.remove_files()
            self.cleanup_environment()
            
            self.show_success()
            return True
            
        except KeyboardInterrupt:
            self.print_error("\n\nDésinstallation annulée par l'utilisateur")
            return False
        except Exception as e:
            self.print_error(f"\n\nErreur: {str(e)}")
            return False
    
    def show_welcome(self) -> None:
        """Affiche l'écran de bienvenue"""
        if RICH_AVAILABLE:
            console.clear()
            welcome_panel = Panel(
                "[bold red]Désinstallateur Dual AI Orchestrator[/bold red]\n\n"
                "Ce programme va supprimer:\n"
                "• L'application Dual AI Orchestrator\n"
                "• Les fichiers de configuration\n"
                "• Les logs et données en cache\n\n"
                "[yellow]Attention:[/yellow] Cette action est irréversible!",
                title="[bold red]Désinstallation[/bold red]",
                box=box.ROUNDED
            )
            console.print(welcome_panel)
        else:
            print("\n" + "="*60)
            print("     DÉSINSTALLATEUR DUAL AI ORCHESTRATOR")
            print("="*60)
            print("\nCe programme va supprimer:")
            print("• L'application Dual AI Orchestrator")
            print("• Les fichiers de configuration")
            print("• Les logs et données en cache")
            print("\nAttention: Cette action est irréversible!")
    
    def find_installed_items(self) -> None:
        """Recherche les éléments installés"""
        self.print_info("\nRecherche des éléments installés...")
        
        # Configuration et données
        if self.config_dir.exists():
            self.items_to_remove.append(("Répertoire de configuration", self.config_dir))
        
        # Exécutables
        for install_dir in self.install_dirs:
            for name in ["dual-ai", "dual-ai.bat", "dual-ai.exe"]:
                exe_path = install_dir / name
                if exe_path.exists():
                    self.items_to_remove.append(("Exécutable", exe_path))
        
        # Package Python
        try:
            import dual_ai
            self.items_to_remove.append(("Package Python", "dual-ai-orchestrator"))
        except ImportError:
            pass
    
    def show_items_to_remove(self) -> None:
        """Affiche les éléments qui seront supprimés"""
        if RICH_AVAILABLE:
            table = Table(title="Éléments à supprimer", box=box.ROUNDED)
            table.add_column("Type", style="cyan")
            table.add_column("Emplacement")
            
            for item_type, item_path in self.items_to_remove:
                table.add_row(item_type, str(item_path))
            
            console.print(table)
        else:
            print("\nÉléments à supprimer:")
            print("-" * 60)
            for item_type, item_path in self.items_to_remove:
                print(f"• {item_type}: {item_path}")
    
    def uninstall_package(self) -> None:
        """Désinstalle le package Python"""
        self.print_info("\nDésinstallation du package Python...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "dual-ai-orchestrator", "-y"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.print_success("✓ Package Python désinstallé")
            else:
                self.print_warning("⚠ Package Python non trouvé ou déjà désinstallé")
        except Exception as e:
            self.print_error(f"Erreur lors de la désinstallation: {e}")
    
    def remove_files(self) -> None:
        """Supprime les fichiers et répertoires"""
        self.print_info("\nSuppression des fichiers...")
        
        for item_type, item_path in self.items_to_remove:
            if item_type == "Package Python":
                continue  # Déjà traité
            
            try:
                if isinstance(item_path, Path):
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                        self.print_success(f"✓ Supprimé: {item_path}")
                    elif item_path.exists():
                        item_path.unlink()
                        self.print_success(f"✓ Supprimé: {item_path}")
            except Exception as e:
                self.print_error(f"✗ Impossible de supprimer {item_path}: {e}")
    
    def cleanup_environment(self) -> None:
        """Nettoie l'environnement système"""
        self.print_info("\nNettoyage de l'environnement...")
        
        # Note sur le PATH
        self.print_warning(
            "\nNote: Le PATH système n'a pas été modifié automatiquement.\n"
            "Si vous aviez ajouté dual-ai au PATH, pensez à le retirer manuellement."
        )
    
    def show_success(self) -> None:
        """Affiche le message de succès"""
        if RICH_AVAILABLE:
            success_panel = Panel(
                "[bold green]✓ Désinstallation terminée[/bold green]\n\n"
                "Dual AI Orchestrator a été complètement supprimé.\n\n"
                "Merci d'avoir utilisé notre application!",
                title="[bold green]Succès[/bold green]",
                box=box.DOUBLE
            )
            console.print(success_panel)
        else:
            print("\n" + "="*60)
            print("✓ DÉSINSTALLATION TERMINÉE")
            print("="*60)
            print("\nDual AI Orchestrator a été complètement supprimé.")
            print("\nMerci d'avoir utilisé notre application!")
    
    # Méthodes utilitaires
    def confirm(self, message: str) -> bool:
        """Demande confirmation"""
        if RICH_AVAILABLE:
            return Confirm.ask(message)
        else:
            response = input(f"{message} [O/n]: ").lower()
            return response in ['', 'o', 'oui', 'y', 'yes']
    
    def print_info(self, message: str) -> None:
        """Affiche une information"""
        if RICH_AVAILABLE:
            console.print(message, style="blue")
        else:
            print(message)
    
    def print_success(self, message: str) -> None:
        """Affiche un succès"""
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
    uninstaller = Uninstaller()
    success = uninstaller.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
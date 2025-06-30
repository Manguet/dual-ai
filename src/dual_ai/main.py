#!/usr/bin/env python3
"""
Point d'entrée principal pour Dual AI Orchestrator
"""

import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .interface import DualAIInterface
from .config import Config
from .utils import check_dependencies, setup_logging

console = Console()


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Chemin vers un fichier de configuration personnalisé",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Active le mode debug avec logs détaillés",
)
@click.version_option(version="1.0.0", prog_name="Dual AI Orchestrator")
def main(config: Optional[Path] = None, debug: bool = False) -> None:
    """
    Dual AI Orchestrator - Interface unifiée pour Claude Code et Gemini Code
    
    Lance une session interactive où Claude et Gemini collaborent pour
    trouver les meilleures solutions à vos problèmes de développement.
    """
    try:
        # Configuration du logging
        setup_logging(debug=debug)
        
        # Chargement de la configuration
        config_obj = Config(config_path=config)
        if debug:
            config_obj.set("app.debug", True)
        
        # Vérification des dépendances
        missing_deps = check_dependencies()
        if missing_deps:
            console.print(
                f"[red]Erreur:[/red] Dépendances manquantes: {', '.join(missing_deps)}",
                style="bold red"
            )
            console.print("\nInstallez les dépendances manquantes:")
            if "claude" in missing_deps:
                console.print("  • Claude Code: npm install -g @anthropic-ai/claude-code")
            if "gemini" in missing_deps:
                console.print("  • Gemini Code: npm install -g @google/gemini-code")
            sys.exit(1)
        
        # Lancement de l'interface
        interface = DualAIInterface(config=config_obj)
        interface.run()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Session interrompue par l'utilisateur[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erreur fatale:[/red] {str(e)}", style="bold red")
        if debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
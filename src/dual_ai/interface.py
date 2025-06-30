"""
Interface utilisateur Rich pour Dual AI Orchestrator
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich import box

from .orchestrator import DualAIOrchestrator
from .config import Config


class DualAIInterface:
    """Interface utilisateur moderne avec Rich"""
    
    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.orchestrator = DualAIOrchestrator(config)
        self.session_count = 0
        self.history: List[Tuple[str, str]] = []
        
    def run(self) -> None:
        """Lance la session interactive"""
        self.show_welcome()
        
        while True:
            try:
                # Affichage du prompt numéroté
                self.session_count += 1
                prompt = f"[bold cyan]#{self.session_count:02d} ›[/bold cyan] "
                
                # Récupération de la demande utilisateur
                user_input = Prompt.ask(prompt, console=self.console)
                
                if not user_input.strip():
                    continue
                    
                # Commandes spéciales
                if user_input.lower() in ["exit", "quit", "q"]:
                    self.show_goodbye()
                    break
                elif user_input.lower() in ["help", "h", "?"]:
                    self.show_help()
                    continue
                elif user_input.lower() == "clear":
                    self.console.clear()
                    self.show_header()
                    continue
                elif user_input.lower() == "history":
                    self.show_history()
                    continue
                
                # Traitement de la demande
                self.process_request(user_input)
                
            except KeyboardInterrupt:
                # Gestion gracieuse de Ctrl+C
                self.console.print("\n[yellow]Commande annulée[/yellow]")
                continue
            except Exception as e:
                self.console.print(f"\n[red]Erreur:[/red] {str(e)}")
                if self.config.get("app.debug"):
                    self.console.print_exception()
    
    def show_welcome(self) -> None:
        """Affiche l'écran de bienvenue"""
        self.console.clear()
        
        # Logo ASCII art
        logo = """
    ╔══════════════════════════════════════════════════════╗
    ║         🤖 DUAL AI ORCHESTRATOR v1.0.0 🤖           ║
    ╚══════════════════════════════════════════════════════╝
        """
        
        self.console.print(Align.center(logo), style="bold cyan")
        self.console.print()
        
        # Affichage du header avec statut
        self.show_header()
        
        # Instructions
        welcome_text = Panel(
            "[bold]Bienvenue dans Dual AI Orchestrator ![/bold]\n\n"
            "• Tapez votre demande pour lancer une collaboration IA\n"
            "• [cyan]help[/cyan] pour afficher l'aide\n"
            "• [cyan]exit[/cyan] pour quitter\n"
            "• [cyan]clear[/cyan] pour effacer l'écran",
            title="[bold cyan]Instructions[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(welcome_text)
        self.console.print()
    
    def show_header(self) -> None:
        """Affiche le header avec statut des IA"""
        # Vérification du statut des IA
        claude_status = "✓ Ready" if self.orchestrator.check_ai_available("claude") else "✗ Not found"
        gemini_status = "✓ Ready" if self.orchestrator.check_ai_available("gemini") else "✗ Not found"
        
        # Création du header
        header_content = (
            f"🤖 Claude: [{self._get_status_color(claude_status)}]{claude_status}[/]    "
            f"🤖 Gemini: [{self._get_status_color(gemini_status)}]{gemini_status}[/]    "
            f"📁 {os.getcwd()}"
        )
        
        header = Panel(
            header_content,
            title="[bold]Dual AI Orchestrator v1.0.0[/bold]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
        
        self.console.print(header)
        self.console.print()
    
    def show_help(self) -> None:
        """Affiche l'aide"""
        help_table = Table(title="Commandes disponibles", box=box.ROUNDED)
        help_table.add_column("Commande", style="cyan", no_wrap=True)
        help_table.add_column("Description")
        
        help_table.add_row("help, h, ?", "Affiche cette aide")
        help_table.add_row("exit, quit, q", "Quitte l'application")
        help_table.add_row("clear", "Efface l'écran")
        help_table.add_row("history", "Affiche l'historique de la session")
        help_table.add_row("[texte]", "Envoie une demande aux IA")
        
        self.console.print(help_table)
        self.console.print()
    
    def show_history(self) -> None:
        """Affiche l'historique de la session"""
        if not self.history:
            self.console.print("[yellow]Aucun historique pour cette session[/yellow]")
            return
        
        history_table = Table(title="Historique de session", box=box.ROUNDED)
        history_table.add_column("#", style="cyan", width=4)
        history_table.add_column("Demande", style="white")
        history_table.add_column("Implémenté par", style="green", width=15)
        
        for i, (request, implementer) in enumerate(self.history, 1):
            history_table.add_row(str(i), request[:50] + "..." if len(request) > 50 else request, implementer)
        
        self.console.print(history_table)
        self.console.print()
    
    def process_request(self, user_input: str) -> None:
        """Traite une demande utilisateur"""
        try:
            # Phase 1: Structuration par Claude
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("🔄 Claude structure votre demande...", total=None)
                structured_request = self.orchestrator.structure_request(user_input)
                progress.remove_task(task)
            
            # Affichage de la demande structurée
            self.console.print(
                Panel(
                    structured_request,
                    title="[bold cyan]Demande structurée[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED
                )
            )
            
            # Phase 2: Débat entre les IA
            self.console.print("\n[bold yellow]💭 Débat en cours entre les IA...[/bold yellow]\n")
            
            debate_results = []
            consensus_reached = False
            
            for round_num in range(1, self.config.get("ui.max_debate_rounds", 3) + 1):
                # Proposition de Claude
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    task = progress.add_task(f"Round {round_num}: Claude propose...", total=None)
                    claude_response = self.orchestrator.get_claude_proposal(
                        structured_request, 
                        debate_results
                    )
                    progress.remove_task(task)
                
                # Affichage de la proposition Claude
                self.console.print(
                    Panel(
                        claude_response,
                        title=f"[bold cyan]Claude - Round {round_num}[/bold cyan]",
                        border_style="cyan",
                        box=box.ROUNDED
                    )
                )
                
                # Réponse de Gemini
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    task = progress.add_task(f"Round {round_num}: Gemini analyse...", total=None)
                    gemini_response = self.orchestrator.get_gemini_response(
                        claude_response,
                        structured_request
                    )
                    progress.remove_task(task)
                
                # Affichage de la réponse Gemini
                self.console.print(
                    Panel(
                        gemini_response,
                        title=f"[bold red]Gemini - Round {round_num}[/bold red]",
                        border_style="red",
                        box=box.ROUNDED
                    )
                )
                
                # Stockage du round
                debate_results.append({
                    "round": round_num,
                    "claude": claude_response,
                    "gemini": gemini_response
                })
                
                # Vérification du consensus
                if self.orchestrator.detect_consensus(gemini_response):
                    consensus_reached = True
                    self.console.print(
                        "\n[bold green]✅ Consensus atteint ![/bold green]\n"
                    )
                    break
            
            if not consensus_reached:
                self.console.print(
                    "\n[bold yellow]⚠️  Consensus non atteint après "
                    f"{self.config.get('ui.max_debate_rounds', 3)} rounds[/bold yellow]\n"
                )
            
            # Phase 3: Choix de l'implémenteur
            choice_table = Table(title="Quelle IA doit implémenter la solution ?", box=box.ROUNDED)
            choice_table.add_column("Option", style="cyan", width=10)
            choice_table.add_column("IA", style="bold")
            choice_table.add_column("Description")
            
            choice_table.add_row("1", "Claude", "IA d'Anthropic - Excellence en code propre")
            choice_table.add_row("2", "Gemini", "IA de Google - Innovation et performance")
            
            self.console.print(choice_table)
            
            choice = IntPrompt.ask(
                "\n[bold cyan]Choix[/bold cyan]",
                choices=["1", "2"],
                console=self.console
            )
            
            implementer = "claude" if choice == 1 else "gemini"
            
            # Phase 4: Implémentation
            self.console.print(f"\n[bold green]🚀 {implementer.capitalize()} implémente la solution...[/bold green]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Implémentation en cours...", total=None)
                
                # Préparation du contexte final
                final_context = self._prepare_final_context(debate_results, consensus_reached)
                
                # Implémentation
                result = self.orchestrator.implement_solution(
                    implementer,
                    structured_request,
                    final_context
                )
                
                progress.remove_task(task)
            
            # Affichage du résultat
            self.console.print(
                Panel(
                    result,
                    title=f"[bold green]Solution implémentée par {implementer.capitalize()}[/bold green]",
                    border_style="green",
                    box=box.DOUBLE
                )
            )
            
            # Ajout à l'historique
            self.history.append((user_input, implementer.capitalize()))
            
            # Sauvegarde optionnelle
            if self.config.get("ui.auto_save_solutions", True):
                self._save_solution(user_input, result, implementer)
            
        except Exception as e:
            self.console.print(f"\n[red]Erreur lors du traitement:[/red] {str(e)}")
            if self.config.get("app.debug"):
                self.console.print_exception()
    
    def show_goodbye(self) -> None:
        """Affiche le message d'au revoir"""
        goodbye = Panel(
            "[bold cyan]Merci d'avoir utilisé Dual AI Orchestrator ![/bold cyan]\n\n"
            f"Sessions complétées: {self.session_count}\n"
            "À bientôt ! 👋",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print("\n")
        self.console.print(goodbye)
        self.console.print("\n")
    
    def _get_status_color(self, status: str) -> str:
        """Retourne la couleur en fonction du statut"""
        return "green" if "Ready" in status else "red"
    
    def _prepare_final_context(self, debate_results: List[dict], consensus: bool) -> str:
        """Prépare le contexte final pour l'implémentation"""
        context = f"Consensus atteint: {'Oui' if consensus else 'Non'}\n\n"
        context += "Résumé du débat:\n"
        
        for result in debate_results:
            context += f"\nRound {result['round']}:\n"
            context += f"- Claude: {result['claude'][:200]}...\n"
            context += f"- Gemini: {result['gemini'][:200]}...\n"
        
        return context
    
    def _save_solution(self, request: str, solution: str, implementer: str) -> None:
        """Sauvegarde la solution dans un fichier"""
        try:
            solutions_dir = Path(self.config.get("paths.solutions_dir", "~/.dual-ai/solutions")).expanduser()
            solutions_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solution_{timestamp}_{implementer}.md"
            filepath = solutions_dir / filename
            
            content = f"# Solution Dual AI\n\n"
            content += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**Implémenté par**: {implementer.capitalize()}\n\n"
            content += f"## Demande\n\n{request}\n\n"
            content += f"## Solution\n\n{solution}\n"
            
            filepath.write_text(content, encoding="utf-8")
            
        except Exception as e:
            if self.config.get("app.debug"):
                self.console.print(f"[yellow]Avertissement: Impossible de sauvegarder la solution: {e}[/yellow]")
#!/usr/bin/env python3
"""
Assistant de configuration des clés API pour Dual AI Orchestrator
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


class APISetup:
    """Assistant de configuration des API"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".dual-ai"
        self.env_file = self.config_dir / ".env"
        self.secrets_dir = self.config_dir / "secrets"
        
    def run(self):
        """Lance l'assistant de configuration"""
        self.show_welcome()
        
        if not self.confirm("Voulez-vous configurer les clés API ?"):
            return
        
        # Créer les répertoires nécessaires
        self.ensure_directories()
        
        # Configuration des API
        apis_config = {}
        
        # Claude API
        if self.confirm("\nConfigurer Claude API ?"):
            claude_key = self.setup_claude_api()
            if claude_key:
                apis_config['claude'] = claude_key
        
        # Gemini API
        if self.confirm("\nConfigurer Gemini API ?"):
            gemini_key = self.setup_gemini_api()
            if gemini_key:
                apis_config['gemini'] = gemini_key
        
        # Choisir la méthode de stockage
        storage_method = self.choose_storage_method()
        
        # Sauvegarder la configuration
        self.save_configuration(apis_config, storage_method)
        
        self.show_success()
    
    def show_welcome(self):
        """Affiche l'écran de bienvenue"""
        if RICH_AVAILABLE:
            console.clear()
            welcome_panel = Panel(
                "[bold]Assistant de configuration des clés API[/bold]\n\n"
                "Cet assistant vous aide à configurer les clés API pour :\n"
                "• Claude Code (Anthropic)\n"
                "• Gemini Code (Google)\n\n"
                "[yellow]Important :[/yellow] Vos clés seront stockées localement et\n"
                "ne seront jamais transmises à des tiers.",
                title="[bold cyan]Configuration API[/bold cyan]",
                box=box.ROUNDED
            )
            console.print(welcome_panel)
        else:
            print("\n" + "="*60)
            print("    ASSISTANT DE CONFIGURATION DES CLÉS API")
            print("="*60)
            print("\nCet assistant vous aide à configurer les clés API pour :")
            print("• Claude Code (Anthropic)")
            print("• Gemini Code (Google)")
            print("\nImportant : Vos clés seront stockées localement.")
    
    def setup_claude_api(self) -> Optional[str]:
        """Configure l'API Claude"""
        self.print_info("\n📋 Configuration Claude API")
        
        if RICH_AVAILABLE:
            info_panel = Panel(
                "Pour utiliser Claude Code, vous avez besoin d'une clé API Anthropic.\n\n"
                "[bold]Comment obtenir une clé :[/bold]\n"
                "1. Allez sur https://console.anthropic.com\n"
                "2. Créez un compte ou connectez-vous\n"
                "3. Allez dans 'API Keys'\n"
                "4. Créez une nouvelle clé\n\n"
                "[yellow]Format :[/yellow] sk-ant-api03-...",
                title="[cyan]Claude API[/cyan]",
                box=box.ROUNDED
            )
            console.print(info_panel)
        else:
            print("\nPour utiliser Claude Code, vous avez besoin d'une clé API Anthropic.")
            print("\nComment obtenir une clé :")
            print("1. Allez sur https://console.anthropic.com")
            print("2. Créez un compte ou connectez-vous")
            print("3. Allez dans 'API Keys'")
            print("4. Créez une nouvelle clé")
            print("\nFormat : sk-ant-api03-...")
        
        # Vérifier si une clé existe déjà
        existing_key = self.get_existing_api_key("ANTHROPIC_API_KEY")
        if existing_key:
            masked_key = existing_key[:15] + "..." + existing_key[-4:]
            if self.confirm(f"\nClé existante trouvée ({masked_key}). Garder ?"):
                return existing_key
        
        # Demander une nouvelle clé
        while True:
            if RICH_AVAILABLE:
                api_key = Prompt.ask(
                    "\n[cyan]Entrez votre clé API Claude[/cyan]",
                    password=True
                )
            else:
                api_key = input("\nEntrez votre clé API Claude (masquée): ")
            
            if not api_key:
                if self.confirm("Ignorer la configuration Claude ?"):
                    return None
                continue
            
            # Validation basique
            if not api_key.startswith("sk-ant-api"):
                self.print_warning("Format de clé invalide. Les clés Claude commencent par 'sk-ant-api'")
                if not self.confirm("Continuer quand même ?"):
                    continue
            
            # Test de la clé (optionnel)
            if self.confirm("Tester la clé API ?"):
                if self.test_claude_api(api_key):
                    self.print_success("✅ Clé API Claude valide !")
                    return api_key
                else:
                    self.print_error("❌ Clé API Claude invalide ou problème de réseau")
                    if not self.confirm("Utiliser quand même cette clé ?"):
                        continue
            
            return api_key
    
    def setup_gemini_api(self) -> Optional[str]:
        """Configure l'API Gemini"""
        self.print_info("\n📋 Configuration Gemini API")
        
        if RICH_AVAILABLE:
            info_panel = Panel(
                "Pour utiliser Gemini Code, vous avez besoin d'une clé API Google.\n\n"
                "[bold]Comment obtenir une clé :[/bold]\n"
                "1. Allez sur https://makersuite.google.com/app/apikey\n"
                "2. Connectez-vous avec votre compte Google\n"
                "3. Cliquez sur 'Create API Key'\n"
                "4. Copiez la clé générée\n\n"
                "[yellow]Format :[/yellow] AIza...",
                title="[red]Gemini API[/red]",
                box=box.ROUNDED
            )
            console.print(info_panel)
        else:
            print("\nPour utiliser Gemini Code, vous avez besoin d'une clé API Google.")
            print("\nComment obtenir une clé :")
            print("1. Allez sur https://makersuite.google.com/app/apikey")
            print("2. Connectez-vous avec votre compte Google")
            print("3. Cliquez sur 'Create API Key'")
            print("4. Copiez la clé générée")
            print("\nFormat : AIza...")
        
        # Vérifier si une clé existe déjà
        existing_key = self.get_existing_api_key("GOOGLE_API_KEY")
        if existing_key:
            masked_key = existing_key[:10] + "..." + existing_key[-4:]
            if self.confirm(f"\nClé existante trouvée ({masked_key}). Garder ?"):
                return existing_key
        
        # Demander une nouvelle clé
        while True:
            if RICH_AVAILABLE:
                api_key = Prompt.ask(
                    "\n[red]Entrez votre clé API Gemini[/red]",
                    password=True
                )
            else:
                api_key = input("\nEntrez votre clé API Gemini (masquée): ")
            
            if not api_key:
                if self.confirm("Ignorer la configuration Gemini ?"):
                    return None
                continue
            
            # Validation basique
            if not api_key.startswith("AIza"):
                self.print_warning("Format de clé invalide. Les clés Google commencent par 'AIza'")
                if not self.confirm("Continuer quand même ?"):
                    continue
            
            # Test de la clé (optionnel)
            if self.confirm("Tester la clé API ?"):
                if self.test_gemini_api(api_key):
                    self.print_success("✅ Clé API Gemini valide !")
                    return api_key
                else:
                    self.print_error("❌ Clé API Gemini invalide ou problème de réseau")
                    if not self.confirm("Utiliser quand même cette clé ?"):
                        continue
            
            return api_key
    
    def choose_storage_method(self) -> str:
        """Choisit la méthode de stockage"""
        if RICH_AVAILABLE:
            console.print("\n[bold]Méthode de stockage des clés :[/bold]")
            console.print("1. Variables d'environnement (fichier .env)")
            console.print("2. Fichiers séparés sécurisés")
            console.print("3. Variables d'environnement système")
            
            choice = Prompt.ask(
                "\nChoisissez une méthode",
                choices=["1", "2", "3"],
                default="1"
            )
        else:
            print("\nMéthode de stockage des clés :")
            print("1. Variables d'environnement (fichier .env)")
            print("2. Fichiers séparés sécurisés")
            print("3. Variables d'environnement système")
            
            choice = input("\nChoisissez une méthode [1]: ") or "1"
        
        method_map = {
            "1": "env_file",
            "2": "separate_files",
            "3": "system_env"
        }
        
        return method_map.get(choice, "env_file")
    
    def save_configuration(self, apis_config: Dict[str, str], method: str):
        """Sauvegarde la configuration"""
        self.print_info(f"\n💾 Sauvegarde avec la méthode : {method}")
        
        if method == "env_file":
            self.save_to_env_file(apis_config)
        elif method == "separate_files":
            self.save_to_separate_files(apis_config)
        elif method == "system_env":
            self.save_to_system_env(apis_config)
    
    def save_to_env_file(self, apis_config: Dict[str, str]):
        """Sauvegarde dans un fichier .env"""
        env_content = ""
        
        if self.env_file.exists():
            # Lire le contenu existant
            existing_content = self.env_file.read_text()
            lines = existing_content.split('\n')
            
            # Supprimer les anciennes clés
            filtered_lines = []
            for line in lines:
                if not any(line.startswith(f"{key}_API_KEY=") for key in ["ANTHROPIC", "GOOGLE"]):
                    filtered_lines.append(line)
            
            env_content = '\n'.join(filtered_lines).strip()
            if env_content:
                env_content += '\n'
        
        # Ajouter les nouvelles clés
        if "claude" in apis_config:
            env_content += f"ANTHROPIC_API_KEY={apis_config['claude']}\n"
        
        if "gemini" in apis_config:
            env_content += f"GOOGLE_API_KEY={apis_config['gemini']}\n"
        
        # Sauvegarder
        self.env_file.write_text(env_content)
        self.env_file.chmod(0o600)  # Permissions restrictives
        
        self.print_success(f"✅ Configuration sauvegardée dans {self.env_file}")
    
    def save_to_separate_files(self, apis_config: Dict[str, str]):
        """Sauvegarde dans des fichiers séparés"""
        for api_name, api_key in apis_config.items():
            key_file = self.secrets_dir / f"{api_name}.key"
            key_file.write_text(api_key)
            key_file.chmod(0o600)
            
            self.print_success(f"✅ Clé {api_name} sauvegardée dans {key_file}")
        
        # Créer un fichier d'instructions
        instructions = self.secrets_dir / "README.txt"
        instructions.write_text("""
Configuration des clés API Dual AI Orchestrator

Les clés sont stockées dans des fichiers séparés pour plus de sécurité.

Pour utiliser ces clés, ajoutez à votre configuration ~/.dual-ai/config.yaml :

ai:
  claude:
    env:
      ANTHROPIC_API_KEY: "file:~/.dual-ai/secrets/claude.key"
  gemini:
    env:
      GOOGLE_API_KEY: "file:~/.dual-ai/secrets/gemini.key"

IMPORTANT : Ces fichiers contiennent vos clés API privées.
Ne les partagez jamais et gardez-les sécurisés.
""")
    
    def save_to_system_env(self, apis_config: Dict[str, str]):
        """Instructions pour les variables d'environnement système"""
        if RICH_AVAILABLE:
            instructions = "Ajoutez ces lignes à votre fichier de configuration shell :\n\n"
        else:
            instructions = "\nAjoutez ces lignes à votre fichier de configuration shell :\n"
        
        shell_file = self.get_shell_config_file()
        
        for api_name, api_key in apis_config.items():
            var_name = "ANTHROPIC_API_KEY" if api_name == "claude" else "GOOGLE_API_KEY"
            instructions += f"export {var_name}=\"{api_key}\"\n"
        
        instructions += f"\nFichier suggéré : {shell_file}\n"
        instructions += "Puis redémarrez votre terminal ou exécutez : source " + str(shell_file)
        
        if RICH_AVAILABLE:
            console.print(Panel(instructions, title="[bold]Instructions[/bold]"))
        else:
            print(instructions)
    
    def test_claude_api(self, api_key: str) -> bool:
        """Test la clé API Claude"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Test simple avec l'API Anthropic
            response = requests.get(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                timeout=10
            )
            
            # 200 ou 400 (bad request) indiquent que l'auth fonctionne
            return response.status_code in [200, 400]
            
        except Exception:
            return False
    
    def test_gemini_api(self, api_key: str) -> bool:
        """Test la clé API Gemini"""
        try:
            import requests
            
            # Test avec l'API Google AI
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            
            response = requests.get(url, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_existing_api_key(self, var_name: str) -> Optional[str]:
        """Récupère une clé API existante"""
        # Vérifier les variables d'environnement
        env_key = os.environ.get(var_name)
        if env_key:
            return env_key
        
        # Vérifier le fichier .env
        if self.env_file.exists():
            content = self.env_file.read_text()
            for line in content.split('\n'):
                if line.startswith(f"{var_name}="):
                    return line.split('=', 1)[1].strip()
        
        return None
    
    def get_shell_config_file(self) -> Path:
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
    
    def ensure_directories(self):
        """Crée les répertoires nécessaires"""
        self.config_dir.mkdir(exist_ok=True)
        self.secrets_dir.mkdir(exist_ok=True)
        
        # Permissions restrictives
        self.config_dir.chmod(0o700)
        self.secrets_dir.chmod(0o700)
    
    def show_success(self):
        """Affiche le message de succès"""
        if RICH_AVAILABLE:
            success_panel = Panel(
                "[bold green]✅ Configuration terminée ![/bold green]\n\n"
                "Vos clés API sont maintenant configurées.\n\n"
                "[bold]Prochaines étapes :[/bold]\n"
                "1. Redémarrez votre terminal si nécessaire\n"
                "2. Lancez : [cyan]dual-ai[/cyan]\n"
                "3. Testez avec une demande simple\n\n"
                "[yellow]Sécurité :[/yellow] Gardez vos clés privées et ne les partagez jamais.",
                title="[bold green]Succès[/bold green]",
                box=box.DOUBLE
            )
            console.print(success_panel)
        else:
            print("\n" + "="*60)
            print("✅ CONFIGURATION TERMINÉE !")
            print("="*60)
            print("\nVos clés API sont maintenant configurées.")
            print("\nProchaines étapes :")
            print("1. Redémarrez votre terminal si nécessaire")
            print("2. Lancez : dual-ai")
            print("3. Testez avec une demande simple")
            print("\nSécurité : Gardez vos clés privées et ne les partagez jamais.")
    
    def confirm(self, message: str) -> bool:
        """Demande confirmation"""
        if RICH_AVAILABLE:
            return Confirm.ask(message)
        else:
            response = input(f"{message} [O/n]: ").lower()
            return response in ['', 'o', 'oui', 'y', 'yes']
    
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


def main():
    """Point d'entrée principal"""
    setup = APISetup()
    setup.run()


if __name__ == "__main__":
    main()
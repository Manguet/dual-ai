"""
Wrapper unifié pour Claude Code et Gemini Code
"""

import subprocess
import shutil
import time
import logging
from typing import Optional, Tuple
from pathlib import Path

from .config import Config


class AIWrapper:
    """Interface uniforme pour interagir avec Claude et Gemini"""
    
    def __init__(self, ai_type: str, config: Config):
        self.ai_type = ai_type
        self.config = config
        self.logger = logging.getLogger(f"AIWrapper.{ai_type}")
        
        # Configuration spécifique à l'IA
        self.command = self.config.get(f"ai.{ai_type}.command", ai_type)
        self.timeout = self.config.get(f"ai.{ai_type}.timeout", 120)
        self.enabled = self.config.get(f"ai.{ai_type}.enabled", True)
        self.args = self.config.get(f"ai.{ai_type}.args", [])
        
        # Tentatives de retry
        self.max_retries = 3
        self.retry_delay = 2
    
    def is_available(self) -> bool:
        """Vérifie si l'outil IA est disponible"""
        if not self.enabled:
            return False
        
        try:
            # Vérifier si la commande existe
            return shutil.which(self.command) is not None
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de {self.ai_type}: {e}")
            return False
    
    def get_version(self) -> str:
        """Récupère la version de l'outil"""
        try:
            result = subprocess.run(
                [self.command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Version inconnue"
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de la version: {e}")
            return "Erreur"
    
    def execute(self, prompt: str, context: str = "", timeout: Optional[int] = None) -> str:
        """Exécute une commande IA avec gestion d'erreurs et retry"""
        if not self.is_available():
            raise RuntimeError(f"{self.ai_type} n'est pas disponible")
        
        actual_timeout = timeout or self.timeout
        
        for attempt in range(self.max_retries):
            try:
                # Préparation du prompt complet
                full_prompt = self._prepare_prompt(prompt, context)
                
                # Préparation de la commande
                command = [self.command] + self.args
                
                # Exécution de la commande
                self.logger.info(f"Exécution de {self.ai_type} (tentative {attempt + 1}/{self.max_retries})")
                
                result = subprocess.run(
                    command,
                    input=full_prompt,
                    capture_output=True,
                    text=True,
                    timeout=actual_timeout,
                    env=self._get_env()
                )
                
                
                # Vérification du résultat
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
                        return self._clean_output(output)
                    else:
                        raise ValueError("Réponse vide de l'IA")
                else:
                    error_msg = result.stderr or "Erreur inconnue"
                    raise RuntimeError(f"Erreur {self.ai_type}: {error_msg}")
                
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout pour {self.ai_type} (tentative {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise TimeoutError(f"{self.ai_type} n'a pas répondu dans le délai de {actual_timeout}s")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'exécution: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
        
        raise RuntimeError(f"Échec après {self.max_retries} tentatives")
    
    def _prepare_prompt(self, prompt: str, context: str) -> str:
        """Prépare le prompt complet avec contexte"""
        if context:
            return f"{context}\n\n{prompt}"
        return prompt
    
    def _save_temp_prompt(self, prompt: str) -> Path:
        """Sauvegarde un prompt dans un fichier temporaire"""
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        temp_file = temp_dir / f"dual_ai_{self.ai_type}_{int(time.time())}.txt"
        temp_file.write_text(prompt, encoding="utf-8")
        return temp_file
    
    def _get_env(self) -> dict:
        """Retourne les variables d'environnement pour l'exécution"""
        import os
        env = os.environ.copy()
        
        # Ajouter des variables spécifiques si nécessaire
        if self.config.get("app.debug"):
            env["DEBUG"] = "1"
        
        return env
    
    def _clean_output(self, output: str) -> str:
        """Nettoie la sortie de l'IA"""
        # Supprimer les caractères de contrôle ANSI
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Supprimer les lignes vides en excès
        lines = output.split('\n')
        cleaned_lines = []
        empty_count = 0
        
        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
                empty_count = 0
            elif empty_count < 1:
                cleaned_lines.append(line)
                empty_count += 1
        
        return '\n'.join(cleaned_lines).strip()
"""
Gestion de la configuration pour Dual AI Orchestrator
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional, Dict


class Config:
    """Gestionnaire de configuration avec support YAML et variables d'environnement"""
    
    DEFAULT_CONFIG = {
        "app": {
            "name": "Dual AI Orchestrator",
            "version": "1.0.0",
            "debug": False
        },
        "ai": {
            "claude": {
                "command": "claude",
                "timeout": 120,
                "enabled": True
            },
            "gemini": {
                "command": "gemini",
                "timeout": 120,
                "enabled": True
            }
        },
        "ui": {
            "theme": "modern",
            "show_spinners": True,
            "max_debate_rounds": 3,
            "auto_save_solutions": True
        },
        "logging": {
            "level": "INFO",
            "file": "~/.dual-ai/logs/app.log",
            "max_size": "10MB",
            "backup_count": 5
        },
        "paths": {
            "config_dir": "~/.dual-ai",
            "solutions_dir": "~/.dual-ai/solutions",
            "cache_dir": "~/.dual-ai/cache"
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = self._load_config()
        self._apply_env_overrides()
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier ou utilise les defaults"""
        config = self.DEFAULT_CONFIG.copy()
        
        # Chemins de configuration possibles
        config_paths = []
        
        if self.config_path:
            config_paths.append(self.config_path)
        
        # Configurations par défaut
        config_paths.extend([
            Path("config/config.yaml"),
            Path.home() / ".dual-ai" / "config.yaml",
            Path("/etc/dual-ai/config.yaml")
        ])
        
        # Charger la première configuration trouvée
        for path in config_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = yaml.safe_load(f) or {}
                        config = self._deep_merge(config, user_config)
                        break
                except Exception as e:
                    print(f"Erreur lors du chargement de {path}: {e}")
        
        return config
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Fusion profonde de deux dictionnaires"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self) -> None:
        """Applique les overrides depuis les variables d'environnement"""
        env_mappings = {
            "DUAL_AI_DEBUG": ("app.debug", self._parse_bool),
            "DUAL_AI_CLAUDE_COMMAND": ("ai.claude.command", str),
            "DUAL_AI_GEMINI_COMMAND": ("ai.gemini.command", str),
            "DUAL_AI_CLAUDE_TIMEOUT": ("ai.claude.timeout", int),
            "DUAL_AI_GEMINI_TIMEOUT": ("ai.gemini.timeout", int),
            "DUAL_AI_MAX_ROUNDS": ("ui.max_debate_rounds", int),
            "DUAL_AI_LOG_LEVEL": ("logging.level", str),
        }
        
        for env_var, (config_path, parser) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    self.set(config_path, parser(value))
                except Exception:
                    pass
    
    def get(self, path: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration par chemin pointé"""
        keys = path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[Path] = None) -> None:
        """Sauvegarde la configuration dans un fichier"""
        save_path = path or self.config_path
        
        if not save_path:
            save_path = Path.home() / ".dual-ai" / "config.yaml"
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=True)
    
    def validate(self) -> bool:
        """Valide la configuration"""
        required_keys = [
            "app.name",
            "app.version",
            "ai.claude.command",
            "ai.gemini.command"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                return False
        
        return True
    
    @staticmethod
    def _parse_bool(value: str) -> bool:
        """Parse une chaîne en booléen"""
        return value.lower() in ('true', '1', 'yes', 'on')
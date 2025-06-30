"""
Utilitaires divers pour Dual AI Orchestrator
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def check_dependencies() -> List[str]:
    """Vérifie les dépendances manquantes"""
    missing = []
    
    # Vérifier Claude
    if not shutil.which("claude"):
        missing.append("claude")
    
    # Vérifier Gemini
    if not shutil.which("gemini"):
        missing.append("gemini")
    
    return missing


def setup_logging(debug: bool = False) -> None:
    """Configure le système de logging"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Format de log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuration du logger root
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Créer le répertoire de logs si nécessaire
    log_dir = Path.home() / ".dual-ai" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Ajouter un handler fichier si en mode debug
    if debug:
        log_file = log_dir / f"dual_ai_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)


def get_system_info() -> dict:
    """Récupère les informations système"""
    import platform
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "hostname": platform.node()
    }


def ensure_directories() -> None:
    """Crée les répertoires nécessaires"""
    directories = [
        Path.home() / ".dual-ai",
        Path.home() / ".dual-ai" / "logs",
        Path.home() / ".dual-ai" / "solutions",
        Path.home() / ".dual-ai" / "cache"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def format_size(bytes: int) -> str:
    """Formate une taille en bytes en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def check_disk_space(required_mb: int = 100) -> bool:
    """Vérifie l'espace disque disponible"""
    import shutil
    
    try:
        home = Path.home()
        stat = shutil.disk_usage(home)
        available_mb = stat.free / (1024 * 1024)
        return available_mb >= required_mb
    except Exception:
        return True  # En cas d'erreur, on continue


def is_admin() -> bool:
    """Vérifie si le script est exécuté avec des privilèges admin"""
    try:
        if sys.platform == "win32":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except Exception:
        return False


def get_shell_config_file() -> Optional[Path]:
    """Détermine le fichier de configuration du shell"""
    shell = os.environ.get('SHELL', '').lower()
    home = Path.home()
    
    if 'zsh' in shell:
        return home / '.zshrc'
    elif 'bash' in shell:
        # Vérifier dans l'ordre de priorité
        for config in ['.bash_profile', '.bashrc', '.profile']:
            config_path = home / config
            if config_path.exists():
                return config_path
        return home / '.bashrc'  # Par défaut
    elif 'fish' in shell:
        return home / '.config' / 'fish' / 'config.fish'
    else:
        return home / '.profile'  # Fallback générique


def add_to_path(directory: Path) -> bool:
    """Ajoute un répertoire au PATH de manière permanente"""
    try:
        if sys.platform == "win32":
            # Windows: Modifier la variable d'environnement système
            import winreg
            
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_ALL_ACCESS
            ) as key:
                current_path = winreg.QueryValueEx(key, "PATH")[0]
                
                if str(directory) not in current_path:
                    new_path = f"{current_path};{directory}"
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    
                    # Notifier Windows du changement
                    import win32api
                    import win32con
                    win32api.SendMessage(
                        win32con.HWND_BROADCAST,
                        win32con.WM_SETTINGCHANGE,
                        0,
                        "Environment"
                    )
            return True
        else:
            # Unix-like: Ajouter au fichier de configuration du shell
            config_file = get_shell_config_file()
            if not config_file:
                return False
            
            export_line = f'\nexport PATH="$PATH:{directory}"\n'
            
            # Vérifier si déjà présent
            if config_file.exists():
                content = config_file.read_text()
                if str(directory) in content:
                    return True
            
            # Ajouter au fichier
            with open(config_file, 'a') as f:
                f.write(export_line)
            
            return True
            
    except Exception as e:
        logging.error(f"Erreur lors de l'ajout au PATH: {e}")
        return False


def create_executable_wrapper(target: Path, destination: Path) -> bool:
    """Crée un wrapper exécutable pour le script Python"""
    try:
        if sys.platform == "win32":
            # Créer un .bat pour Windows
            wrapper_content = f'@echo off\n"{sys.executable}" "{target}" %*\n'
            wrapper_path = destination.with_suffix('.bat')
        else:
            # Créer un script shell pour Unix
            wrapper_content = f'#!/bin/sh\n"{sys.executable}" "{target}" "$@"\n'
            wrapper_path = destination
        
        wrapper_path.write_text(wrapper_content)
        
        # Rendre exécutable sur Unix
        if sys.platform != "win32":
            os.chmod(wrapper_path, 0o755)
        
        return True
        
    except Exception as e:
        logging.error(f"Erreur lors de la création du wrapper: {e}")
        return False
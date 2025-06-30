"""
Dual AI Orchestrator - Un orchestrateur intelligent pour Claude Code et Gemini Code
"""

__version__ = "1.0.0"
__author__ = "Dual AI Contributors"
__email__ = "contact@dual-ai.dev"
__license__ = "MIT"

from .main import main
from .orchestrator import DualAIOrchestrator
from .interface import DualAIInterface

__all__ = ["main", "DualAIOrchestrator", "DualAIInterface"]
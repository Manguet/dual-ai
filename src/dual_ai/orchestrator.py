"""
Orchestrateur principal pour la collaboration entre Claude et Gemini
"""

import re
from typing import List, Dict, Optional, Tuple

from .ai_wrapper import AIWrapper
from .config import Config


class DualAIOrchestrator:
    """Gère la collaboration entre Claude et Gemini"""
    
    CONSENSUS_KEYWORDS = [
        "consensus", "d'accord", "agree", "parfait", 
        "excellent", "je suis d'accord", "c'est une bonne approche",
        "CONSENSUS", "AGREE", "PARFAIT", "D'ACCORD"
    ]
    
    OBJECTION_KEYWORDS = [
        "mais", "cependant", "toutefois", "néanmoins",
        "je suggère", "alternative", "plutôt", "instead"
    ]
    
    def __init__(self, config: Config):
        self.config = config
        self.claude = AIWrapper("claude", config)
        self.gemini = AIWrapper("gemini", config)
        
    def check_ai_available(self, ai_type: str) -> bool:
        """Vérifie si une IA est disponible"""
        if ai_type == "claude":
            return self.claude.is_available()
        elif ai_type == "gemini":
            return self.gemini.is_available()
        return False
    
    def structure_request(self, user_request: str) -> str:
        """Claude structure la demande utilisateur"""
        prompt = f"""Tu es un assistant expert en analyse de demandes. 
Analyse et structure cette demande utilisateur de manière claire et précise:

Demande: {user_request}

Fournis une analyse structurée avec:
1. Objectif principal
2. Contraintes techniques éventuelles
3. Critères de succès
4. Technologies suggérées (si applicable)

Sois concis et précis."""

        try:
            return self.claude.execute(prompt)
        except Exception as e:
            # Fallback: retourner la demande originale structurée basiquement
            return f"Objectif: {user_request}\nContraintes: Aucune spécifiée\nCritères: Solution fonctionnelle"
    
    def get_claude_proposal(self, structured_request: str, previous_rounds: List[Dict]) -> str:
        """Claude propose une solution"""
        context = self._build_context(previous_rounds)
        
        prompt = f"""Tu es Claude, un expert en développement. 
Voici une demande structurée:

{structured_request}

{context}

Propose une solution technique détaillée. 
Sois spécifique sur l'implémentation, l'architecture et les bonnes pratiques.
Si c'est un nouveau round, tiens compte des retours de Gemini."""

        return self.claude.execute(prompt)
    
    def get_gemini_response(self, claude_proposal: str, structured_request: str) -> str:
        """Gemini analyse et répond à la proposition de Claude"""
        prompt = f"""Tu es Gemini, un expert en développement. 
Voici la demande originale:

{structured_request}

Claude propose cette solution:

{claude_proposal}

Analyse cette proposition:
1. Points forts
2. Points d'amélioration potentiels
3. Alternatives ou optimisations

Si tu es d'accord avec l'approche, indique clairement "CONSENSUS" ou "D'ACCORD".
Sinon, propose des améliorations constructives."""

        return self.gemini.execute(prompt)
    
    def detect_consensus(self, gemini_response: str) -> bool:
        """Détecte si un consensus a été atteint"""
        response_lower = gemini_response.lower()
        
        # Vérifier les mots-clés de consensus
        consensus_found = any(keyword.lower() in response_lower for keyword in self.CONSENSUS_KEYWORDS)
        
        # Vérifier l'absence d'objections majeures
        objections_found = sum(1 for keyword in self.OBJECTION_KEYWORDS if keyword.lower() in response_lower)
        
        # Analyse plus sophistiquée si nécessaire
        if consensus_found and objections_found < 2:
            return True
        
        # Vérifier des patterns spécifiques
        consensus_patterns = [
            r"je.*suis.*d'accord",
            r"c'est.*parfait",
            r"excellente.*approche",
            r"solution.*valide"
        ]
        
        for pattern in consensus_patterns:
            if re.search(pattern, response_lower):
                return True
        
        return False
    
    def implement_solution(self, implementer: str, structured_request: str, context: str) -> str:
        """L'IA choisie implémente la solution finale"""
        prompt = f"""Tu es {implementer.capitalize()}, choisi pour implémenter la solution finale.

Demande originale:
{structured_request}

Contexte du débat:
{context}

Implémente maintenant la solution complète avec:
1. Code complet et fonctionnel
2. Documentation inline
3. Instructions d'utilisation
4. Tests si applicable

Fournis une implémentation production-ready."""

        if implementer == "claude":
            return self.claude.execute(prompt, timeout=180)  # Plus de temps pour l'implémentation
        else:
            return self.gemini.execute(prompt, timeout=180)
    
    def _build_context(self, previous_rounds: List[Dict]) -> str:
        """Construit le contexte des rounds précédents"""
        if not previous_rounds:
            return "C'est le premier round de discussion."
        
        context = "Rounds précédents:\n\n"
        for round_data in previous_rounds[-2:]:  # Garder seulement les 2 derniers rounds
            context += f"Round {round_data['round']}:\n"
            context += f"- Ta proposition: {round_data['claude'][:300]}...\n"
            context += f"- Retour de Gemini: {round_data['gemini'][:300]}...\n\n"
        
        return context
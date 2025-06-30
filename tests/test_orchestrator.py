"""
Tests pour l'orchestrateur IA
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from dual_ai.orchestrator import DualAIOrchestrator
from dual_ai.config import Config


class TestDualAIOrchestrator:
    """Tests pour DualAIOrchestrator"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuration mock pour les tests"""
        config = Mock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "ai.claude.timeout": 120,
            "ai.gemini.timeout": 120,
            "ui.max_debate_rounds": 3
        }.get(key, default)
        return config
    
    @pytest.fixture
    def orchestrator(self, mock_config):
        """Instance d'orchestrateur pour les tests"""
        with patch('dual_ai.orchestrator.AIWrapper'):
            return DualAIOrchestrator(mock_config)
    
    def test_init(self, mock_config):
        """Test de l'initialisation"""
        with patch('dual_ai.orchestrator.AIWrapper') as mock_wrapper:
            orchestrator = DualAIOrchestrator(mock_config)
            
            assert orchestrator.config == mock_config
            assert mock_wrapper.call_count == 2  # Claude + Gemini
            
            # Vérifier les appels de création des wrappers
            calls = mock_wrapper.call_args_list
            assert calls[0][0] == ("claude", mock_config)
            assert calls[1][0] == ("gemini", mock_config)
    
    def test_check_ai_available_claude(self, orchestrator):
        """Test de vérification de disponibilité Claude"""
        orchestrator.claude.is_available.return_value = True
        
        assert orchestrator.check_ai_available("claude") is True
        orchestrator.claude.is_available.assert_called_once()
    
    def test_check_ai_available_gemini(self, orchestrator):
        """Test de vérification de disponibilité Gemini"""
        orchestrator.gemini.is_available.return_value = False
        
        assert orchestrator.check_ai_available("gemini") is False
        orchestrator.gemini.is_available.assert_called_once()
    
    def test_check_ai_available_invalid(self, orchestrator):
        """Test avec une IA invalide"""
        assert orchestrator.check_ai_available("invalid") is False
    
    def test_structure_request_success(self, orchestrator):
        """Test de structuration de demande réussie"""
        test_request = "Crée une fonction Python"
        expected_response = "Objectif: Créer une fonction Python\nContraintes: Aucune"
        
        orchestrator.claude.execute.return_value = expected_response
        
        result = orchestrator.structure_request(test_request)
        
        assert result == expected_response
        orchestrator.claude.execute.assert_called_once()
        
        # Vérifier que le prompt contient la demande
        call_args = orchestrator.claude.execute.call_args[0][0]
        assert test_request in call_args
    
    def test_structure_request_fallback(self, orchestrator):
        """Test de fallback en cas d'erreur"""
        test_request = "Crée une fonction Python"
        orchestrator.claude.execute.side_effect = Exception("Network error")
        
        result = orchestrator.structure_request(test_request)
        
        assert "Objectif: " + test_request in result
        assert "Contraintes: Aucune spécifiée" in result
    
    def test_get_claude_proposal(self, orchestrator):
        """Test de proposition Claude"""
        structured_request = "Objectif: Créer une API"
        previous_rounds = []
        expected_response = "Je propose d'utiliser FastAPI..."
        
        orchestrator.claude.execute.return_value = expected_response
        
        result = orchestrator.get_claude_proposal(structured_request, previous_rounds)
        
        assert result == expected_response
        orchestrator.claude.execute.assert_called_once()
        
        # Vérifier le prompt
        call_args = orchestrator.claude.execute.call_args[0][0]
        assert structured_request in call_args
    
    def test_get_gemini_response(self, orchestrator):
        """Test de réponse Gemini"""
        claude_proposal = "Je propose FastAPI"
        structured_request = "Objectif: Créer une API"
        expected_response = "D'ACCORD avec FastAPI, excellente approche"
        
        orchestrator.gemini.execute.return_value = expected_response
        
        result = orchestrator.get_gemini_response(claude_proposal, structured_request)
        
        assert result == expected_response
        orchestrator.gemini.execute.assert_called_once()
        
        # Vérifier le prompt
        call_args = orchestrator.gemini.execute.call_args[0][0]
        assert claude_proposal in call_args
        assert structured_request in call_args
    
    def test_detect_consensus_positive(self, orchestrator):
        """Test de détection de consensus positif"""
        test_cases = [
            "CONSENSUS - cette approche est parfaite",
            "Je suis d'accord avec cette solution",
            "D'ACCORD, excellente approche",
            "C'est une parfaite solution"
        ]
        
        for response in test_cases:
            assert orchestrator.detect_consensus(response) is True
    
    def test_detect_consensus_negative(self, orchestrator):
        """Test de détection de consensus négatif"""
        test_cases = [
            "Mais je pense qu'on pourrait améliorer...",
            "Cependant, il faudrait plutôt utiliser...",
            "Je suggère une alternative différente",
            "Cette approche a des problèmes"
        ]
        
        for response in test_cases:
            assert orchestrator.detect_consensus(response) is False
    
    def test_detect_consensus_mixed(self, orchestrator):
        """Test de détection avec réponse mixte"""
        response = "D'ACCORD avec l'approche générale, mais je suggère quelques améliorations"
        # Devrait être False car il y a des objections malgré l'accord
        assert orchestrator.detect_consensus(response) is False
    
    def test_implement_solution_claude(self, orchestrator):
        """Test d'implémentation par Claude"""
        structured_request = "Objectif: API REST"
        context = "Consensus atteint"
        expected_code = "from fastapi import FastAPI\napp = FastAPI()"
        
        orchestrator.claude.execute.return_value = expected_code
        
        result = orchestrator.implement_solution("claude", structured_request, context)
        
        assert result == expected_code
        orchestrator.claude.execute.assert_called_once_with(
            unittest.mock.ANY, timeout=180
        )
    
    def test_implement_solution_gemini(self, orchestrator):
        """Test d'implémentation par Gemini"""
        structured_request = "Objectif: API REST"
        context = "Consensus atteint"
        expected_code = "import express\nconst app = express()"
        
        orchestrator.gemini.execute.return_value = expected_code
        
        result = orchestrator.implement_solution("gemini", structured_request, context)
        
        assert result == expected_code
        orchestrator.gemini.execute.assert_called_once_with(
            unittest.mock.ANY, timeout=180
        )
    
    def test_build_context_empty(self, orchestrator):
        """Test de construction de contexte vide"""
        context = orchestrator._build_context([])
        assert "C'est le premier round de discussion" in context
    
    def test_build_context_with_rounds(self, orchestrator):
        """Test de construction de contexte avec rounds"""
        previous_rounds = [
            {
                "round": 1,
                "claude": "Ma première proposition est d'utiliser FastAPI car...",
                "gemini": "D'accord mais il faut considérer la scalabilité..."
            },
            {
                "round": 2,
                "claude": "Bonne remarque, ajoutons Redis pour le cache...",
                "gemini": "Parfait, CONSENSUS sur cette approche"
            }
        ]
        
        context = orchestrator._build_context(previous_rounds)
        
        assert "Rounds précédents:" in context
        assert "Round 1:" in context
        assert "Round 2:" in context
        assert "FastAPI" in context
        assert "Redis" in context
    
    def test_build_context_limit_rounds(self, orchestrator):
        """Test de limitation des rounds dans le contexte"""
        # Créer 5 rounds mais seuls les 2 derniers devraient être inclus
        previous_rounds = [
            {"round": i, "claude": f"Claude round {i}", "gemini": f"Gemini round {i}"}
            for i in range(1, 6)
        ]
        
        context = orchestrator._build_context(previous_rounds)
        
        # Vérifier que seuls les rounds 4 et 5 sont inclus
        assert "Round 4:" in context
        assert "Round 5:" in context
        assert "Round 1:" not in context
        assert "Round 2:" not in context


class TestDualAIOrchestratorIntegration:
    """Tests d'intégration pour l'orchestrateur"""
    
    @pytest.fixture
    def real_config(self, tmp_path):
        """Configuration réelle pour tests d'intégration"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
ai:
  claude:
    command: "echo"
    timeout: 5
  gemini:
    command: "echo"
    timeout: 5
""")
        return Config(config_file)
    
    def test_full_workflow_simulation(self, real_config):
        """Test simulé d'un workflow complet"""
        with patch('dual_ai.orchestrator.AIWrapper') as mock_wrapper:
            # Configuration des mocks
            mock_claude = Mock()
            mock_gemini = Mock()
            mock_wrapper.side_effect = [mock_claude, mock_gemini]
            
            # Réponses simulées
            mock_claude.execute.side_effect = [
                "Objectif structuré: Créer une API REST",  # structure_request
                "Je propose FastAPI avec SQLAlchemy",      # get_claude_proposal
                "Code final: from fastapi import FastAPI"  # implement_solution
            ]
            mock_gemini.execute.return_value = "D'ACCORD, excellente approche FastAPI"
            
            orchestrator = DualAIOrchestrator(real_config)
            
            # Simulation du workflow
            structured = orchestrator.structure_request("Crée une API")
            proposal = orchestrator.get_claude_proposal(structured, [])
            gemini_response = orchestrator.get_gemini_response(proposal, structured)
            consensus = orchestrator.detect_consensus(gemini_response)
            
            assert consensus is True
            
            if consensus:
                final_code = orchestrator.implement_solution("claude", structured, "Consensus atteint")
                assert "FastAPI" in final_code


# Import nécessaire pour les tests avec timeout
import unittest.mock
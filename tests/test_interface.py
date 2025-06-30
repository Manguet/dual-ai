"""
Tests pour l'interface utilisateur
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from dual_ai.interface import DualAIInterface
from dual_ai.config import Config


class TestDualAIInterface:
    """Tests pour DualAIInterface"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuration mock pour les tests"""
        config = Mock(spec=Config)
        config.get.return_value = True
        return config
    
    @pytest.fixture
    def interface(self, mock_config):
        """Instance d'interface pour les tests"""
        with patch('dual_ai.interface.DualAIOrchestrator'):
            return DualAIInterface(mock_config)
    
    def test_init(self, mock_config):
        """Test de l'initialisation"""
        with patch('dual_ai.interface.DualAIOrchestrator') as mock_orchestrator:
            interface = DualAIInterface(mock_config)
            
            assert interface.config == mock_config
            assert interface.session_count == 0
            assert interface.history == []
            mock_orchestrator.assert_called_once_with(mock_config)
    
    @patch('dual_ai.interface.Console')
    def test_show_welcome(self, mock_console_class, interface):
        """Test de l'affichage de bienvenue"""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        interface.console = mock_console
        
        interface.show_welcome()
        
        # Vérifier que clear() et print() ont été appelés
        mock_console.clear.assert_called_once()
        assert mock_console.print.call_count >= 2
    
    def test_get_status_color(self, interface):
        """Test de la fonction de couleur de statut"""
        assert interface._get_status_color("✓ Ready") == "green"
        assert interface._get_status_color("✗ Not found") == "red"
    
    @patch('dual_ai.interface.Path')
    def test_save_solution(self, mock_path, interface):
        """Test de la sauvegarde de solution"""
        mock_path.home.return_value = Path("/home/user")
        mock_solutions_dir = Mock()
        mock_path.return_value.expanduser.return_value = mock_solutions_dir
        
        interface._save_solution("Test request", "Test solution", "claude")
        
        mock_solutions_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_prepare_final_context(self, interface):
        """Test de préparation du contexte final"""
        debate_results = [
            {
                "round": 1,
                "claude": "Claude's proposal",
                "gemini": "Gemini's response"
            }
        ]
        
        context = interface._prepare_final_context(debate_results, True)
        
        assert "Consensus atteint: Oui" in context
        assert "Round 1:" in context
        assert "Claude's proposal" in context
    
    @patch('dual_ai.interface.Prompt')
    def test_process_request_exit(self, mock_prompt, interface):
        """Test de la commande exit"""
        # Ce test nécessiterait une refactorisation de process_request
        # pour être plus testable (séparer la logique de commandes)
        pass
    
    @patch('dual_ai.interface.Console')
    def test_show_help(self, mock_console_class, interface):
        """Test de l'affichage de l'aide"""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        interface.console = mock_console
        
        interface.show_help()
        
        mock_console.print.assert_called()
    
    def test_show_history_empty(self, interface):
        """Test de l'affichage d'historique vide"""
        with patch.object(interface, 'console') as mock_console:
            interface.show_history()
            mock_console.print.assert_called_with("[yellow]Aucun historique pour cette session[/yellow]")
    
    def test_show_history_with_data(self, interface):
        """Test de l'affichage d'historique avec données"""
        interface.history = [
            ("Test request 1", "Claude"),
            ("Test request 2", "Gemini")
        ]
        
        with patch.object(interface, 'console') as mock_console:
            interface.show_history()
            mock_console.print.assert_called()


class TestDualAIInterfaceIntegration:
    """Tests d'intégration pour l'interface"""
    
    @pytest.fixture
    def real_config(self, tmp_path):
        """Configuration réelle pour les tests d'intégration"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
app:
  debug: true
ai:
  claude:
    command: "echo"
    timeout: 5
  gemini:
    command: "echo"
    timeout: 5
ui:
  max_debate_rounds: 2
""")
        return Config(config_file)
    
    @patch('dual_ai.interface.DualAIOrchestrator')
    def test_interface_creation(self, mock_orchestrator, real_config):
        """Test de création d'interface avec vraie config"""
        interface = DualAIInterface(real_config)
        
        assert interface.config == real_config
        mock_orchestrator.assert_called_once_with(real_config)
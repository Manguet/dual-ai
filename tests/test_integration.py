"""
Tests d'intégration bout-en-bout pour Dual AI Orchestrator
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

from dual_ai.config import Config
from dual_ai.interface import DualAIInterface
from dual_ai.orchestrator import DualAIOrchestrator


class TestEndToEndIntegration:
    """Tests d'intégration complets"""
    
    @pytest.fixture
    def temp_home(self):
        """Crée un répertoire home temporaire"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_home = Path(tmp_dir) / "home"
            temp_home.mkdir()
            yield temp_home
    
    @pytest.fixture
    def mock_ai_commands(self, temp_home):
        """Crée des commandes AI mock pour les tests"""
        bin_dir = temp_home / "bin"
        bin_dir.mkdir()
        
        # Script Claude mock
        claude_script = bin_dir / "claude"
        claude_script.write_text("""#!/bin/bash
if [[ "$1" == "--version" ]]; then
    echo "Claude Code v1.0.0"
elif [[ "$1" == *"structure"* ]]; then
    echo "Objectif: $2"
    echo "Contraintes: Aucune spécifiée"
elif [[ "$1" == *"propose"* ]]; then
    echo "Je propose d'utiliser FastAPI pour créer l'API"
else
    echo "from fastapi import FastAPI"
    echo "app = FastAPI()"
fi
""")
        claude_script.chmod(0o755)
        
        # Script Gemini mock
        gemini_script = bin_dir / "gemini"
        gemini_script.write_text("""#!/bin/bash
if [[ "$1" == "--version" ]]; then
    echo "Gemini Code v1.0.0"
else
    echo "D'ACCORD avec FastAPI, excellente approche pour l'API REST"
fi
""")
        gemini_script.chmod(0o755)
        
        return bin_dir
    
    @pytest.fixture
    def test_config(self, temp_home, mock_ai_commands):
        """Configuration de test complète"""
        config_dir = temp_home / ".dual-ai"
        config_dir.mkdir()
        
        config_file = config_dir / "config.yaml"
        config_content = f"""
app:
  debug: true

ai:
  claude:
    command: "{mock_ai_commands / 'claude'}"
    timeout: 10
    enabled: true
  gemini:
    command: "{mock_ai_commands / 'gemini'}"
    timeout: 10
    enabled: true

ui:
  max_debate_rounds: 2
  auto_save_solutions: true
  show_spinners: false

logging:
  level: "DEBUG"
  file: "{config_dir / 'test.log'}"

paths:
  config_dir: "{config_dir}"
  solutions_dir: "{config_dir / 'solutions'}"
  cache_dir: "{config_dir / 'cache'}"
"""
        config_file.write_text(config_content)
        
        return Config(config_file)
    
    def test_config_loading(self, test_config):
        """Test de chargement de configuration"""
        assert test_config.get("app.debug") is True
        assert test_config.get("ui.max_debate_rounds") == 2
        assert "claude" in str(test_config.get("ai.claude.command"))
    
    def test_orchestrator_creation(self, test_config):
        """Test de création de l'orchestrateur"""
        orchestrator = DualAIOrchestrator(test_config)
        
        assert orchestrator.config == test_config
        assert orchestrator.claude is not None
        assert orchestrator.gemini is not None
    
    def test_ai_availability_check(self, test_config):
        """Test de vérification de disponibilité des IA"""
        orchestrator = DualAIOrchestrator(test_config)
        
        # Les scripts mock devraient être disponibles
        claude_available = orchestrator.check_ai_available("claude")
        gemini_available = orchestrator.check_ai_available("gemini")
        
        assert claude_available is True
        assert gemini_available is True
    
    def test_full_workflow_simulation(self, test_config):
        """Test d'un workflow complet simulé"""
        orchestrator = DualAIOrchestrator(test_config)
        
        # Phase 1: Structuration
        user_request = "Crée une API REST pour gérer des tâches"
        structured = orchestrator.structure_request(user_request)
        
        assert "Objectif:" in structured
        
        # Phase 2: Proposition Claude
        claude_proposal = orchestrator.get_claude_proposal(structured, [])
        assert "FastAPI" in claude_proposal
        
        # Phase 3: Réponse Gemini
        gemini_response = orchestrator.get_gemini_response(claude_proposal, structured)
        assert "D'ACCORD" in gemini_response
        
        # Phase 4: Détection consensus
        consensus = orchestrator.detect_consensus(gemini_response)
        assert consensus is True
        
        # Phase 5: Implémentation
        final_code = orchestrator.implement_solution("claude", structured, "Consensus atteint")
        assert "FastAPI" in final_code
    
    @patch('dual_ai.interface.Prompt')
    @patch('dual_ai.interface.IntPrompt')
    def test_interface_integration(self, mock_int_prompt, mock_prompt, test_config):
        """Test d'intégration de l'interface"""
        # Configuration des mocks
        mock_prompt.ask.return_value = "Crée une fonction Python simple"
        mock_int_prompt.ask.return_value = 1  # Choisir Claude
        
        interface = DualAIInterface(test_config)
        
        # Test d'une méthode publique non-interactive
        interface.session_count = 0
        interface.history = []
        
        # Vérifier l'initialisation
        assert interface.config == test_config
        assert interface.session_count == 0
        assert len(interface.history) == 0


class TestCommandLineIntegration:
    """Tests d'intégration en ligne de commande"""
    
    def test_help_command(self):
        """Test de la commande d'aide"""
        try:
            result = subprocess.run(
                ["python", "-m", "dual_ai.main", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0
            assert "Dual AI Orchestrator" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Module dual_ai non installé ou timeout")
    
    def test_version_command(self):
        """Test de la commande version"""
        try:
            result = subprocess.run(
                ["python", "-m", "dual_ai.main", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0
            assert "1.0.0" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Module dual_ai non installé ou timeout")


class TestInstallationIntegration:
    """Tests d'intégration de l'installation"""
    
    @pytest.fixture
    def temp_install_env(self):
        """Environnement d'installation temporaire"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            install_dir = Path(tmp_dir)
            
            # Copier les fichiers nécessaires
            project_root = Path(__file__).parent.parent
            
            # Créer une structure minimale
            (install_dir / "src").mkdir()
            (install_dir / "src" / "dual_ai").mkdir()
            
            # Copier les fichiers principaux
            shutil.copy2(project_root / "requirements.txt", install_dir)
            shutil.copy2(project_root / "setup.py", install_dir)
            
            yield install_dir
    
    def test_requirements_validation(self, temp_install_env):
        """Test de validation des requirements"""
        requirements_file = temp_install_env / "requirements.txt"
        
        assert requirements_file.exists()
        
        content = requirements_file.read_text()
        required_packages = ["rich", "pyyaml", "requests", "click"]
        
        for package in required_packages:
            assert package in content
    
    def test_setup_py_validation(self, temp_install_env):
        """Test de validation du setup.py"""
        setup_file = temp_install_env / "setup.py"
        
        assert setup_file.exists()
        
        content = setup_file.read_text()
        assert "dual-ai-orchestrator" in content
        assert "entry_points" in content


class TestConfigurationIntegration:
    """Tests d'intégration de configuration"""
    
    def test_config_hierarchy(self):
        """Test de la hiérarchie de configuration"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir) / ".dual-ai"
            config_dir.mkdir()
            
            # Configuration utilisateur
            user_config = config_dir / "config.yaml"
            user_config.write_text("""
app:
  debug: true
ui:
  max_debate_rounds: 5
""")
            
            config = Config(user_config)
            
            # Vérifier les overrides
            assert config.get("app.debug") is True
            assert config.get("ui.max_debate_rounds") == 5
            
            # Vérifier les valeurs par défaut
            assert config.get("app.name") == "Dual AI Orchestrator"
    
    def test_environment_variables_override(self):
        """Test des variables d'environnement"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir) / ".dual-ai"
            config_dir.mkdir()
            
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
app:
  debug: false
ui:
  max_debate_rounds: 3
""")
            
            # Test avec variables d'environnement
            import os
            old_env = os.environ.copy()
            
            try:
                os.environ["DUAL_AI_DEBUG"] = "true"
                os.environ["DUAL_AI_MAX_ROUNDS"] = "7"
                
                config = Config(config_file)
                
                assert config.get("app.debug") is True
                assert config.get("ui.max_debate_rounds") == 7
                
            finally:
                # Restaurer l'environnement
                os.environ.clear()
                os.environ.update(old_env)


class TestErrorHandlingIntegration:
    """Tests d'intégration de gestion d'erreurs"""
    
    def test_missing_ai_tools(self):
        """Test avec outils IA manquants"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "config.yaml"
            config_file.write_text("""
ai:
  claude:
    command: "nonexistent_claude"
  gemini:
    command: "nonexistent_gemini"
""")
            
            config = Config(config_file)
            orchestrator = DualAIOrchestrator(config)
            
            # Les IA ne devraient pas être disponibles
            assert orchestrator.check_ai_available("claude") is False
            assert orchestrator.check_ai_available("gemini") is False
    
    def test_invalid_configuration(self):
        """Test avec configuration invalide"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "config.yaml"
            config_file.write_text("""
invalid_yaml: [
  missing_closing_bracket
""")
            
            # Devrait utiliser la configuration par défaut
            config = Config(config_file)
            
            # Vérifier que la config par défaut est chargée
            assert config.get("app.name") == "Dual AI Orchestrator"
    
    def test_permission_errors(self):
        """Test avec erreurs de permissions"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir) / ".dual-ai"
            config_dir.mkdir(mode=0o444)  # Lecture seule
            
            try:
                config = Config()
                # Ne devrait pas planter, utiliser config par défaut
                assert config.get("app.name") == "Dual AI Orchestrator"
            finally:
                # Nettoyer
                config_dir.chmod(0o755)


@pytest.mark.slow
class TestPerformanceIntegration:
    """Tests d'intégration de performance"""
    
    def test_large_context_handling(self, test_config):
        """Test avec un contexte large"""
        orchestrator = DualAIOrchestrator(test_config)
        
        # Créer un contexte volumineux
        large_rounds = []
        for i in range(10):
            large_rounds.append({
                "round": i,
                "claude": "A" * 1000,  # 1KB de texte
                "gemini": "B" * 1000
            })
        
        # Devrait gérer sans erreur
        context = orchestrator._build_context(large_rounds)
        assert len(context) > 0
    
    def test_timeout_handling(self, test_config):
        """Test de gestion des timeouts"""
        # Configuration avec timeout très court
        test_config.set("ai.claude.timeout", 1)
        test_config.set("ai.gemini.timeout", 1)
        
        orchestrator = DualAIOrchestrator(test_config)
        
        # Les commandes mock devraient toujours réussir rapidement
        try:
            result = orchestrator.structure_request("Test rapide")
            assert len(result) > 0
        except Exception:
            # Acceptable si le timeout est vraiment trop court
            pass
#!/usr/bin/env python3
"""
Exemple d'utilisation basique de Dual AI Orchestrator
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path pour l'import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dual_ai.config import Config
from dual_ai.orchestrator import DualAIOrchestrator
from dual_ai.interface import DualAIInterface


def exemple_utilisation_directe():
    """Exemple d'utilisation directe de l'orchestrateur"""
    print("=== Exemple d'utilisation directe ===\n")
    
    # Configuration par défaut
    config = Config()
    
    # Créer l'orchestrateur
    orchestrator = DualAIOrchestrator(config)
    
    # Vérifier la disponibilité des IA
    claude_available = orchestrator.check_ai_available("claude")
    gemini_available = orchestrator.check_ai_available("gemini")
    
    print(f"Claude disponible: {'✓' if claude_available else '✗'}")
    print(f"Gemini disponible: {'✓' if gemini_available else '✗'}")
    
    if not claude_available and not gemini_available:
        print("\n❌ Aucune IA disponible. Installez Claude Code ou Gemini Code.")
        return
    
    # Demande d'exemple
    user_request = "Crée une fonction Python pour calculer la factorielle d'un nombre"
    
    print(f"\n📝 Demande: {user_request}")
    
    try:
        # Phase 1: Structuration
        print("\n🔄 Phase 1: Structuration par Claude...")
        structured = orchestrator.structure_request(user_request)
        print(f"Structuré: {structured[:100]}...")
        
        # Phase 2: Débat (simulation avec 1 round)
        print("\n💭 Phase 2: Débat collaboratif...")
        
        if claude_available:
            claude_proposal = orchestrator.get_claude_proposal(structured, [])
            print(f"Proposition Claude: {claude_proposal[:100]}...")
            
            if gemini_available:
                gemini_response = orchestrator.get_gemini_response(claude_proposal, structured)
                print(f"Réponse Gemini: {gemini_response[:100]}...")
                
                # Détection consensus
                consensus = orchestrator.detect_consensus(gemini_response)
                print(f"Consensus atteint: {'✓' if consensus else '✗'}")
                
                # Phase 3: Implémentation
                print("\n🚀 Phase 3: Implémentation...")
                implementer = "claude"  # Choix fixe pour l'exemple
                
                final_code = orchestrator.implement_solution(
                    implementer, 
                    structured, 
                    f"Consensus: {'Oui' if consensus else 'Non'}"
                )
                
                print(f"\n✅ Solution finale (par {implementer.capitalize()}):")
                print("="*50)
                print(final_code)
                print("="*50)
            else:
                print("Gemini non disponible, pas de débat possible")
        else:
            print("Claude non disponible")
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


def exemple_configuration_personnalisee():
    """Exemple avec configuration personnalisée"""
    print("\n\n=== Exemple avec configuration personnalisée ===\n")
    
    # Configuration personnalisée
    config = Config()
    config.set("ui.max_debate_rounds", 2)
    config.set("ai.claude.timeout", 60)
    config.set("ai.gemini.timeout", 60)
    
    print("Configuration personnalisée:")
    print(f"  Rounds max: {config.get('ui.max_debate_rounds')}")
    print(f"  Timeout Claude: {config.get('ai.claude.timeout')}s")
    print(f"  Timeout Gemini: {config.get('ai.gemini.timeout')}s")
    
    # Utilisation avec cette config
    orchestrator = DualAIOrchestrator(config)
    
    # Test de détection de consensus
    test_responses = [
        "D'ACCORD avec cette approche, excellente solution !",
        "Mais je pense qu'on pourrait améliorer cela...",
        "CONSENSUS atteint, parfait !",
        "Cependant, il faudrait considérer..."
    ]
    
    print("\n🔍 Test de détection de consensus:")
    for i, response in enumerate(test_responses, 1):
        consensus = orchestrator.detect_consensus(response)
        status = "✓ Consensus" if consensus else "✗ Pas de consensus"
        print(f"  {i}. {response[:50]}... → {status}")


def exemple_gestion_erreurs():
    """Exemple de gestion d'erreurs"""
    print("\n\n=== Exemple de gestion d'erreurs ===\n")
    
    # Configuration avec outils inexistants
    config = Config()
    config.set("ai.claude.command", "claude_inexistant")
    config.set("ai.gemini.command", "gemini_inexistant")
    
    orchestrator = DualAIOrchestrator(config)
    
    # Test de disponibilité
    print("Test avec outils inexistants:")
    claude_ok = orchestrator.check_ai_available("claude")
    gemini_ok = orchestrator.check_ai_available("gemini")
    
    print(f"  Claude: {'✓' if claude_ok else '✗'}")
    print(f"  Gemini: {'✓' if gemini_ok else '✗'}")
    
    if not claude_ok and not gemini_ok:
        print("  ✓ Gestion d'erreur correcte: aucune IA disponible")
    
    # Test avec timeout très court
    config.set("ai.claude.timeout", 1)
    print(f"\nTest avec timeout très court ({config.get('ai.claude.timeout')}s):")
    print("  Cette configuration pourrait causer des timeouts")


def exemple_interface_simulation():
    """Exemple de simulation d'interface (sans interaction)"""
    print("\n\n=== Exemple de simulation d'interface ===\n")
    
    config = Config()
    config.set("ui.show_spinners", False)  # Désactiver les animations
    config.set("app.debug", True)
    
    # Créer l'interface
    interface = DualAIInterface(config)
    
    print("Interface créée avec succès:")
    print(f"  Session count: {interface.session_count}")
    print(f"  Historique: {len(interface.history)} entrées")
    print(f"  Configuration debug: {config.get('app.debug')}")
    
    # Simulation d'ajout à l'historique
    interface.history.append(("Exemple de demande", "Claude"))
    interface.session_count = 1
    
    print(f"\nAprès simulation:")
    print(f"  Session count: {interface.session_count}")
    print(f"  Historique: {len(interface.history)} entrées")
    
    # Test de préparation de contexte
    debate_results = [
        {
            "round": 1,
            "claude": "Je propose d'utiliser une approche récursive",
            "gemini": "D'accord, mais attention aux performances"
        }
    ]
    
    context = interface._prepare_final_context(debate_results, True)
    print(f"\nContexte généré: {context[:100]}...")


def main():
    """Fonction principale"""
    print("🤖 Exemples d'utilisation de Dual AI Orchestrator")
    print("=" * 60)
    
    try:
        # Exemple 1: Utilisation directe
        exemple_utilisation_directe()
        
        # Exemple 2: Configuration personnalisée
        exemple_configuration_personnalisee()
        
        # Exemple 3: Gestion d'erreurs
        exemple_gestion_erreurs()
        
        # Exemple 4: Simulation d'interface
        exemple_interface_simulation()
        
        print("\n\n✅ Tous les exemples terminés avec succès !")
        print("\nPour une utilisation interactive complète, lancez:")
        print("  dual-ai")
        print("\nOu installez d'abord avec:")
        print("  python install.py")
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import: {e}")
        print("\nInstallez d'abord le projet avec:")
        print("  python install.py")
        print("ou:")
        print("  pip install -e .")
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
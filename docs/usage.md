# Guide d'utilisation de Dual AI Orchestrator

## 🚀 Démarrage rapide

Lancez Dual AI Orchestrator dans votre terminal :

```bash
dual-ai
```

Vous verrez apparaître l'interface interactive avec un prompt numéroté :

```
╭─────────────────── Dual AI Orchestrator v1.0.0 ───────────────────╮
│ 🤖 Claude: ✓ Ready    🤖 Gemini: ✓ Ready    📁 /home/user/project │
╰────────────────────────────────────────────────────────────────────╯

#01 › _
```

## 💡 Exemples d'utilisation

### Exemple 1 : Création d'une fonction

```bash
#01 › Crée une fonction Python pour calculer les nombres premiers jusqu'à N
```

**Résultat :**
1. Claude structure votre demande
2. Claude propose une solution avec crible d'Ératosthène
3. Gemini analyse et propose des optimisations
4. Consensus atteint après 2 rounds
5. Vous choisissez qui implémente (Claude ou Gemini)

### Exemple 2 : API REST

```bash
#02 › Développe une API REST avec FastAPI pour gérer une liste de tâches avec CRUD complet
```

**Workflow automatique :**
- Claude structure : endpoints, modèles de données, validation
- Débat sur l'architecture (base de données, authentification)
- Consensus sur une solution avec SQLAlchemy et JWT
- Implémentation complète avec tests

### Exemple 3 : Optimisation de code

```bash
#03 › Optimise ce code Python pour améliorer les performances : [coller votre code]
```

**Collaboration :**
- Claude analyse les bottlenecks
- Gemini propose des alternatives (NumPy, multiprocessing)
- Débat sur les trade-offs performance/lisibilité
- Solution optimisée avec benchmarks

## 🎯 Types de demandes supportées

### Développement Web
- APIs REST et GraphQL
- Applications frontend (React, Vue, Angular)
- Backend (Express, Django, FastAPI)
- Bases de données et migrations

### Scripts et automatisation
- Scripts Bash/PowerShell
- Automatisation CI/CD
- Tâches DevOps
- Scripts de déploiement

### Analyse de données
- Scripts Python pour data science
- Visualisations avec matplotlib/plotly
- Analyse statistique
- Machine learning

### Architecture système
- Design patterns
- Architecture microservices
- Optimisation de performance
- Sécurité

## 📋 Commandes disponibles

### Commandes système

| Commande | Description |
|----------|-------------|
| `help`, `h`, `?` | Affiche l'aide |
| `exit`, `quit`, `q` | Quitte l'application |
| `clear` | Efface l'écran |
| `history` | Affiche l'historique de session |

### Options en ligne de commande

```bash
# Lancer avec configuration personnalisée
dual-ai --config /path/to/config.yaml

# Mode debug
dual-ai --debug

# Afficher la version
dual-ai --version

# Afficher l'aide
dual-ai --help
```

## 🎛️ Workflow détaillé

### Phase 1 : Structuration (Claude)
Claude analyse votre demande et la structure avec :
- Objectif principal
- Contraintes techniques
- Critères de succès
- Technologies suggérées

### Phase 2 : Débat collaboratif
Cycles de négociation (maximum 3-5 rounds) :
1. Claude propose une solution
2. Gemini analyse et donne son avis
3. Si consensus → fin du débat
4. Sinon → nouveau round avec les retours

### Phase 3 : Détection de consensus
Consensus automatique détecté par :
- Mots-clés : "CONSENSUS", "D'ACCORD", "PARFAIT"
- Absence d'objections majeures
- Analyse du sentiment positif

### Phase 4 : Implémentation
Vous choisissez quelle IA implémente :
- **Claude** : Code propre, documentation excellente
- **Gemini** : Innovations, optimisations performance

## 🎨 Interface utilisateur

### Éléments visuels

- **Header** : Statut des IA et répertoire courant
- **Prompts numérotés** : `#01 ›`, `#02 ›`, etc.
- **Panels colorés** : 
  - Cyan pour Claude
  - Rouge pour Gemini
  - Vert pour les solutions finales
- **Spinners animés** : Pendant les traitements
- **Tables de choix** : Pour sélectionner l'implémenteur

### Mode fallback
Si Rich n'est pas disponible, mode texte simple automatique.

## 💾 Sauvegarde et historique

### Sauvegarde automatique
Les solutions sont automatiquement sauvegardées dans :
```
~/.dual-ai/solutions/solution_YYYYMMDD_HHMMSS_implementer.md
```

### Format de sauvegarde
```markdown
# Solution Dual AI

**Date**: 2024-12-30 14:30:15
**Implémenté par**: Claude

## Demande

Crée une fonction Python pour calculer les nombres premiers

## Solution

[Code et documentation]
```

### Historique de session
Utilisez `history` pour voir toutes les demandes de la session courante.

## ⚙️ Configuration avancée

### Personnalisation du comportement

```yaml
# ~/.dual-ai/config.yaml
ui:
  max_debate_rounds: 5        # Plus de rounds de débat
  auto_save_solutions: false  # Désactiver la sauvegarde auto
  show_spinners: false        # Désactiver les animations

ai:
  claude:
    timeout: 180              # Plus de temps pour Claude
  gemini:
    enabled: false            # Désactiver Gemini temporairement
```

### Variables d'environnement

```bash
# Timeout personnalisés
export DUAL_AI_CLAUDE_TIMEOUT=300
export DUAL_AI_GEMINI_TIMEOUT=300

# Commandes personnalisées
export DUAL_AI_CLAUDE_COMMAND="claude --model=claude-3"
export DUAL_AI_GEMINI_COMMAND="gemini --temperature=0.7"

# Mode debug
export DUAL_AI_DEBUG=true
```

## 🚀 Conseils d'utilisation

### Rédigez des demandes claires
❌ **Mauvais :** "Fais un truc avec du Python"
✅ **Bon :** "Crée une classe Python pour gérer une cache LRU avec limite de taille"

### Spécifiez le contexte
```bash
#01 › Crée une API FastAPI pour un blog avec authentification JWT et base PostgreSQL
```

### Utilisez des exemples
```bash
#02 › Optimise cette fonction Python [coller le code] pour traiter des listes de 100k+ éléments
```

### Itérez sur les solutions
```bash
#03 › Améliore la solution précédente en ajoutant la gestion d'erreurs et des tests unitaires
```

## 🔍 Débogage

### Mode debug
```bash
dual-ai --debug
```

Active :
- Logs détaillés
- Sauvegarde des prompts
- Temps d'exécution
- Erreurs complètes

### Logs
Consultez les logs dans :
```
~/.dual-ai/logs/app.log
```

### Problèmes courants

**IA ne répond pas :**
- Vérifiez la connexion réseau
- Augmentez le timeout dans la config
- Redémarrez dual-ai

**Consensus non atteint :**
- Reformulez votre demande plus précisément
- Augmentez `max_debate_rounds`
- Utilisez le mode debug pour analyser

**Interface cassée :**
- Redimensionnez votre terminal
- Désactivez Rich : `export DUAL_AI_NO_RICH=1`

## 📊 Métriques et performance

### Temps de réponse typiques
- Structuration : 5-15 secondes  
- Round de débat : 10-30 secondes
- Implémentation : 20-60 secondes

### Optimisations
- Utilisez des demandes spécifiques
- Limitez le contexte aux éléments pertinents
- Configurez des timeouts appropriés

## 🤝 Bonnes pratiques

### Organisation du travail
1. **Démarrez simple** : Une demande par session
2. **Itérez** : Améliorez progressivement
3. **Testez** : Validez les solutions proposées
4. **Documentez** : Sauvegardez les bonnes solutions

### Collaboration efficace
- Laissez les IA débattre (n'interrompez pas)
- Choisissez l'implémenteur selon vos préférences
- Utilisez l'historique pour le contexte

### Maintenance
- Nettoyez régulièrement `~/.dual-ai/cache/`
- Sauvegardez vos configurations personnalisées
- Mettez à jour régulièrement

## 💡 Cas d'usage avancés

### Intégration dans des projets existants
```bash
cd mon-projet
dual-ai
#01 › Analyse ce projet et propose une architecture de tests automatisés
```

### Génération de documentation
```bash
#01 › Génère une documentation API complète pour ce code FastAPI [coller le code]
```

### Refactoring
```bash
#01 › Refactorise cette classe Python pour respecter les principes SOLID [coller le code]
```

### Code review automatisé
```bash
#01 › Fais un code review de cette pull request et identifie les problèmes potentiels
```

## 📚 Ressources supplémentaires

- [Configuration avancée](configuration.md)
- [Résolution de problèmes](troubleshooting.md)
- [API interne](api.md)
- [Exemples complets](../examples/)
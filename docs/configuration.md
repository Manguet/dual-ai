# Configuration avancée de Dual AI Orchestrator

## 📁 Emplacements des fichiers de configuration

### Priorité de chargement
1. Fichier spécifié par `--config`
2. `./config/config.yaml` (répertoire courant)
3. `~/.dual-ai/config.yaml` (utilisateur)
4. `/etc/dual-ai/config.yaml` (système)

### Structure des répertoires
```
~/.dual-ai/
├── config.yaml          # Configuration principale
├── logs/                 # Fichiers de logs
├── solutions/           # Solutions sauvegardées  
└── cache/               # Cache temporaire
```

## ⚙️ Structure de configuration

### Fichier de configuration complet

```yaml
# Configuration de l'application
app:
  name: "Dual AI Orchestrator"
  version: "1.0.0"
  debug: false

# Configuration des IA
ai:
  claude:
    command: "claude"
    timeout: 120
    enabled: true
    args: []
    env: {}
  gemini:
    command: "gemini"
    timeout: 120
    enabled: true
    args: []
    env: {}

# Interface utilisateur
ui:
  theme: "modern"
  show_spinners: true
  max_debate_rounds: 3
  auto_save_solutions: true
  prompt_style: "numbered"
  colors:
    claude: "cyan"
    gemini: "red"
    success: "green"
    error: "red"
    warning: "yellow"

# Logging
logging:
  level: "INFO"
  file: "~/.dual-ai/logs/app.log"
  max_size: "10MB"
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Chemins
paths:
  config_dir: "~/.dual-ai"
  solutions_dir: "~/.dual-ai/solutions"
  cache_dir: "~/.dual-ai/cache"
  temp_dir: "/tmp/dual-ai"

# Orchestration
orchestration:
  consensus_keywords:
    - "consensus"
    - "d'accord"
    - "agree"
    - "parfait"
  objection_keywords:
    - "mais"
    - "cependant"
    - "plutôt"
  context_length: 2000
  retry_attempts: 3
  retry_delay: 2

# Performance
performance:
  cache_enabled: true
  cache_ttl: 3600
  concurrent_requests: false
  request_delay: 1
```

## 🔧 Configuration par section

### Application (`app`)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `name` | string | "Dual AI Orchestrator" | Nom de l'application |
| `version` | string | "1.0.0" | Version |
| `debug` | boolean | false | Mode debug activé |

### IA (`ai`)

#### Configuration Claude
```yaml
ai:
  claude:
    command: "claude"           # Commande à exécuter
    timeout: 120               # Timeout en secondes
    enabled: true              # IA activée
    args: ["--model", "claude-3"]  # Arguments supplémentaires
    env:                       # Variables d'environnement
      ANTHROPIC_API_KEY: "sk-..."
```

#### Configuration Gemini
```yaml
ai:
  gemini:
    command: "gemini"
    timeout: 120
    enabled: true
    args: ["--temperature", "0.7"]
    env:
      GOOGLE_API_KEY: "AIza..."
```

### Interface utilisateur (`ui`)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `theme` | string | "modern" | Thème d'affichage |
| `show_spinners` | boolean | true | Afficher les animations |
| `max_debate_rounds` | integer | 3 | Rounds maximum de débat |
| `auto_save_solutions` | boolean | true | Sauvegarde automatique |
| `prompt_style` | string | "numbered" | Style du prompt |

#### Couleurs personnalisées
```yaml
ui:
  colors:
    claude: "blue"        # Couleur pour Claude
    gemini: "magenta"     # Couleur pour Gemini
    success: "bright_green"
    error: "bright_red"
    warning: "orange3"
```

### Logging (`logging`)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `level` | string | "INFO" | Niveau de logs (DEBUG, INFO, WARNING, ERROR) |
| `file` | string | "~/.dual-ai/logs/app.log" | Fichier de logs |
| `max_size` | string | "10MB" | Taille max avant rotation |
| `backup_count` | integer | 5 | Nombre de backups |
| `format` | string | Format des logs | Format Python logging |

### Chemins (`paths`)

```yaml
paths:
  config_dir: "~/.dual-ai"              # Répertoire de configuration
  solutions_dir: "~/.dual-ai/solutions" # Solutions sauvegardées
  cache_dir: "~/.dual-ai/cache"         # Cache
  temp_dir: "/tmp/dual-ai"              # Fichiers temporaires
```

### Orchestration (`orchestration`)

Configuration du débat entre IA :

```yaml
orchestration:
  consensus_keywords:       # Mots-clés de consensus
    - "consensus"
    - "d'accord"
    - "perfect"
  objection_keywords:       # Mots-clés d'objection
    - "but"
    - "however"
    - "instead"
  context_length: 2000      # Longueur max du contexte
  retry_attempts: 3         # Tentatives en cas d'erreur
  retry_delay: 2           # Délai entre tentatives (sec)
```

## 🌍 Variables d'environnement

### Variables principales

| Variable | Configuration | Description |
|----------|---------------|-------------|
| `DUAL_AI_DEBUG` | `app.debug` | Active le mode debug |
| `DUAL_AI_CONFIG` | - | Chemin vers fichier de config |
| `DUAL_AI_CLAUDE_COMMAND` | `ai.claude.command` | Commande Claude |
| `DUAL_AI_GEMINI_COMMAND` | `ai.gemini.command` | Commande Gemini |
| `DUAL_AI_CLAUDE_TIMEOUT` | `ai.claude.timeout` | Timeout Claude |
| `DUAL_AI_GEMINI_TIMEOUT` | `ai.gemini.timeout` | Timeout Gemini |
| `DUAL_AI_MAX_ROUNDS` | `ui.max_debate_rounds` | Rounds maximum |
| `DUAL_AI_LOG_LEVEL` | `logging.level` | Niveau de logs |
| `DUAL_AI_NO_RICH` | - | Désactive Rich |

### Exemples d'utilisation

```bash
# Configuration temporaire
export DUAL_AI_DEBUG=true
export DUAL_AI_MAX_ROUNDS=5
dual-ai

# Configuration permanente (ajout au .bashrc)
echo 'export DUAL_AI_CLAUDE_TIMEOUT=300' >> ~/.bashrc
```

## 📝 Configuration par profil

### Profils multiples

Créez différents profils pour différents contextes :

```bash
# Profil développement
dual-ai --config ~/.dual-ai/dev.yaml

# Profil production
dual-ai --config ~/.dual-ai/prod.yaml

# Profil test
dual-ai --config ~/.dual-ai/test.yaml
```

### Exemple de profil développement
```yaml
# dev.yaml
app:
  debug: true

ai:
  claude:
    timeout: 300
  gemini:
    timeout: 300

ui:
  max_debate_rounds: 5

logging:
  level: "DEBUG"
```

### Exemple de profil production
```yaml
# prod.yaml
app:
  debug: false

ai:
  claude:
    timeout: 60
  gemini:
    timeout: 60

ui:
  max_debate_rounds: 2
  show_spinners: false

logging:
  level: "WARNING"
```

## 🎯 Configurations spécialisées

### Configuration pour projets spécifiques

#### Développement Web
```yaml
ai:
  claude:
    args: ["--context", "web-development"]
  gemini:
    args: ["--domain", "frontend"]

ui:
  max_debate_rounds: 4

orchestration:
  context_length: 3000
```

#### Data Science
```yaml
ai:
  claude:
    args: ["--context", "data-science"]
    timeout: 180
  gemini:
    args: ["--domain", "analytics"]
    timeout: 180

ui:
  max_debate_rounds: 3
```

#### DevOps/Infrastructure
```yaml
ai:
  claude:
    args: ["--context", "devops"]
  gemini:
    args: ["--domain", "infrastructure"]

orchestration:
  consensus_keywords:
    - "consensus"
    - "approved"
    - "production-ready"
```

## 🔐 Configuration sécurisée

### Gestion des clés API

```yaml
ai:
  claude:
    env:
      ANTHROPIC_API_KEY_FILE: "/secure/path/claude.key"
  gemini:
    env:
      GOOGLE_API_KEY_FILE: "/secure/path/gemini.key"
```

### Fichiers séparés pour les secrets
```bash
# Créer un fichier de secrets
echo "sk-ant-api03-..." > ~/.dual-ai/secrets/claude.key
chmod 600 ~/.dual-ai/secrets/claude.key

# Référencer dans la config
ai:
  claude:
    env:
      ANTHROPIC_API_KEY: "file:~/.dual-ai/secrets/claude.key"
```

## 📊 Configuration de performance

### Optimisation pour gros projets
```yaml
performance:
  cache_enabled: true
  cache_ttl: 7200          # 2 heures
  concurrent_requests: true
  request_delay: 0.5

orchestration:
  context_length: 1500     # Réduire pour la vitesse
  retry_attempts: 2

ai:
  claude:
    timeout: 90
  gemini:
    timeout: 90
```

### Configuration réseau lent
```yaml
ai:
  claude:
    timeout: 300
    args: ["--stream", "false"]
  gemini:
    timeout: 300
    
performance:
  request_delay: 3
  retry_attempts: 5

ui:
  show_spinners: true      # Important pour feedback
```

## 🔧 Validation de configuration

### Commandes de validation

```bash
# Valider la configuration
dual-ai --validate-config

# Afficher la configuration chargée
dual-ai --show-config

# Tester la connexion aux IA
dual-ai --test-connection
```

### Validation manuelle

```python
from dual_ai.config import Config

config = Config("~/.dual-ai/config.yaml")
if config.validate():
    print("Configuration valide")
else:
    print("Configuration invalide")
```

## 🛠️ Configuration programmatique

### Modification dynamique

```python
from dual_ai.config import Config

config = Config()
config.set("ui.max_debate_rounds", 5)
config.set("ai.claude.timeout", 180)
config.save()
```

### Hook de configuration

```python
# ~/.dual-ai/hooks/config.py
def post_load_config(config):
    """Hook appelé après chargement de la config"""
    if config.get("app.debug"):
        config.set("logging.level", "DEBUG")
    return config
```

## 📋 Configuration par défaut complète

```yaml
app:
  name: "Dual AI Orchestrator"
  version: "1.0.0"
  debug: false

ai:
  claude:
    command: "claude"
    timeout: 120
    enabled: true
    args: []
    env: {}
  gemini:
    command: "gemini"
    timeout: 120
    enabled: true
    args: []
    env: {}

ui:
  theme: "modern"
  show_spinners: true
  max_debate_rounds: 3
  auto_save_solutions: true
  prompt_style: "numbered"
  colors:
    claude: "cyan"
    gemini: "red"
    success: "green"
    error: "red"
    warning: "yellow"

logging:
  level: "INFO"
  file: "~/.dual-ai/logs/app.log"
  max_size: "10MB"
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

paths:
  config_dir: "~/.dual-ai"
  solutions_dir: "~/.dual-ai/solutions"
  cache_dir: "~/.dual-ai/cache"
  temp_dir: "/tmp/dual-ai"

orchestration:
  consensus_keywords:
    - "consensus"
    - "d'accord"
    - "agree"
    - "parfait"
  objection_keywords:
    - "mais"
    - "cependant"
    - "plutôt"
  context_length: 2000
  retry_attempts: 3
  retry_delay: 2

performance:
  cache_enabled: true
  cache_ttl: 3600
  concurrent_requests: false
  request_delay: 1
```
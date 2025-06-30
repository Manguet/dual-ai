# Résolution de problèmes - Dual AI Orchestrator

## 🚨 Problèmes d'installation

### Python non trouvé ou version incorrecte

**Erreur :**
```
python: command not found
```
ou
```
Python 3.8+ is required, found 3.7
```

**Solutions :**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.8 python3.8-pip

# CentOS/RHEL
sudo yum install python38 python38-pip

# macOS
brew install python@3.8

# Windows
# Télécharger depuis python.org
```

### Problèmes de permissions

**Erreur :**
```
Permission denied: '/usr/local/bin/dual-ai'
```

**Solutions :**
```bash
# Installer en mode utilisateur
pip install --user dual-ai-orchestrator

# Ou créer le répertoire
mkdir -p ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"
```

### Dépendances manquantes

**Erreur :**
```
ModuleNotFoundError: No module named 'rich'
```

**Solutions :**
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --user --force-reinstall

# Ou installation manuelle
pip install rich pyyaml requests click colorama
```

## 🤖 Problèmes avec les outils IA

### Claude Code non trouvé

**Erreur :**
```
Claude Code not found. Please install it first.
```

**Solutions :**
```bash
# Via npm (méthode recommandée)
npm install -g @anthropic-ai/claude-code

# Via pip
pip install claude-code

# Vérifier l'installation
which claude
claude --version
```

### Gemini Code non trouvé

**Erreur :**
```
Gemini Code not found. Please install it first.
```

**Solutions :**
```bash
# Via npm
npm install -g @google/gemini-code

# Via pip  
pip install gemini-code

# Vérifier
which gemini
gemini --version
```

### Problèmes d'authentification IA

**Erreur :**
```
Authentication failed for Claude
```

**Solutions :**
```bash
# Configurer les clés API
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export GOOGLE_API_KEY="AIza..."

# Ou dans la configuration
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." >> ~/.dual-ai/.env
```

### Timeouts fréquents

**Erreur :**
```
Timeout: AI didn't respond within 120 seconds
```

**Solutions :**
```yaml
# ~/.dual-ai/config.yaml
ai:
  claude:
    timeout: 300  # 5 minutes
  gemini:
    timeout: 300
```

## 🖥️ Problèmes d'interface

### Interface Rich corrompue

**Erreur :**
Interface avec caractères étranges ou layout cassé.

**Solutions :**
```bash
# Redimensionner le terminal
# Ou désactiver Rich temporairement
export DUAL_AI_NO_RICH=1
dual-ai

# Vérifier la compatibilité du terminal
echo $TERM
# Doit être xterm-256color ou similaire
```

### Commande dual-ai non trouvée

**Erreur :**
```
dual-ai: command not found
```

**Solutions :**
```bash
# Vérifier le PATH
echo $PATH | grep -o ~/.local/bin

# Ajouter au PATH si nécessaire
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Ou créer un alias
echo 'alias dual-ai="python3 -m dual_ai"' >> ~/.bashrc
```

### Problèmes d'encodage

**Erreur :**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Solutions :**
```bash
# Configurer les locales
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Ubuntu/Debian
sudo locale-gen en_US.UTF-8
```

## ⚙️ Problèmes de configuration

### Fichier de configuration invalide

**Erreur :**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solutions :**
```bash
# Valider le YAML
python3 -c "import yaml; yaml.safe_load(open('~/.dual-ai/config.yaml'))"

# Utiliser la configuration par défaut
cp config/config.yaml ~/.dual-ai/config.yaml
```

### Variables d'environnement ignorées

**Problème :** Les variables DUAL_AI_* ne sont pas prises en compte.

**Solutions :**
```bash
# Vérifier qu'elles sont définies
env | grep DUAL_AI

# Exporter correctement
export DUAL_AI_DEBUG=true

# Permanent dans .bashrc
echo 'export DUAL_AI_DEBUG=true' >> ~/.bashrc
```

## 🔄 Problèmes de session

### Consensus jamais atteint

**Problème :** Les IA débattent indéfiniment sans consensus.

**Solutions :**
```yaml
# Augmenter le nombre de rounds
ui:
  max_debate_rounds: 5

# Ou reformuler la demande plus précisément
```

### Sessions lentes

**Problème :** Temps de réponse très longs.

**Solutions :**
```yaml
# Optimiser les timeouts
ai:
  claude:
    timeout: 90
  gemini:
    timeout: 90

# Réduire le contexte
orchestration:
  context_length: 1000
```

### Perte de contexte

**Problème :** L'IA oublie le contexte des rounds précédents.

**Solutions :**
```yaml
# Augmenter la longueur du contexte
orchestration:
  context_length: 3000
```

## 💾 Problèmes de fichiers

### Permissions sur ~/.dual-ai

**Erreur :**
```
Permission denied: ~/.dual-ai/config.yaml
```

**Solutions :**
```bash
# Corriger les permissions
chmod -R 755 ~/.dual-ai
chmod 644 ~/.dual-ai/config.yaml

# Recréer si nécessaire
rm -rf ~/.dual-ai
dual-ai  # Recréera automatiquement
```

### Espace disque insuffisant

**Erreur :**
```
No space left on device
```

**Solutions :**
```bash
# Nettoyer les logs
rm ~/.dual-ai/logs/*.log

# Nettoyer le cache
rm -rf ~/.dual-ai/cache/*

# Configurer la rotation des logs
logging:
  max_size: "5MB"
  backup_count: 2
```

### Fichiers corrompus

**Erreur :**
```
json.decoder.JSONDecodeError: Expecting value
```

**Solutions :**
```bash
# Sauvegarder les données importantes
cp -r ~/.dual-ai/solutions ~/dual-ai-backup

# Réinitialiser la configuration
rm ~/.dual-ai/config.yaml
dual-ai  # Régénérera la config par défaut
```

## 🌐 Problèmes réseau

### Connexion Internet lente/instable

**Solutions :**
```yaml
# Augmenter les timeouts
ai:
  claude:
    timeout: 300
  gemini:
    timeout: 300

# Ajouter des délais entre requêtes
performance:
  request_delay: 3
  retry_attempts: 5
```

### Proxy d'entreprise

**Configuration proxy :**
```bash
# Variables d'environnement
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# Ou dans la config IA
ai:
  claude:
    env:
      HTTP_PROXY: "http://proxy.company.com:8080"
  gemini:
    env:
      HTTP_PROXY: "http://proxy.company.com:8080"
```

## 🔍 Débogage avancé

### Activer les logs détaillés

```bash
# Mode debug complet
dual-ai --debug

# Ou via configuration
export DUAL_AI_DEBUG=true
export DUAL_AI_LOG_LEVEL=DEBUG
```

### Analyser les logs

```bash
# Logs en temps réel
tail -f ~/.dual-ai/logs/app.log

# Rechercher des erreurs
grep -i error ~/.dual-ai/logs/app.log

# Logs par date
grep "2024-12-30" ~/.dual-ai/logs/app.log
```

### Tests de connectivité

```bash
# Tester Claude
claude --version
claude "Hello world"

# Tester Gemini
gemini --version
gemini "Hello world"

# Test réseau
ping anthropic.com
ping google.com
```

## 🔧 Outils de diagnostic

### Script de diagnostic automatique

```bash
#!/bin/bash
# diagnostic.sh

echo "=== Diagnostic Dual AI Orchestrator ==="

echo "1. Version Python:"
python3 --version

echo "2. Modules Python:"
python3 -c "import dual_ai; print('dual_ai OK')" 2>/dev/null || echo "dual_ai ERREUR"
python3 -c "import rich; print('rich OK')" 2>/dev/null || echo "rich ERREUR"

echo "3. Outils IA:"
which claude && echo "Claude: OK" || echo "Claude: MANQUANT"
which gemini && echo "Gemini: OK" || echo "Gemini: MANQUANT"

echo "4. Configuration:"
ls -la ~/.dual-ai/ 2>/dev/null || echo "Répertoire config manquant"

echo "5. PATH:"
echo $PATH | grep -o ~/.local/bin && echo "PATH: OK" || echo "PATH: ~/.local/bin manquant"

echo "6. Permissions:"
[ -w ~/.dual-ai ] && echo "Permissions: OK" || echo "Permissions: ERREUR"
```

```bash
chmod +x diagnostic.sh
./diagnostic.sh
```

### Tests unitaires

```bash
# Installer les dépendances de test
pip install pytest pytest-cov

# Lancer les tests
cd dual-ai-orchestrator
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=dual_ai --cov-report=html
```

## 📞 Obtenir de l'aide

### Informations à fournir

Quand vous demandez de l'aide, fournissez :

1. **Version et environnement :**
   ```bash
   dual-ai --version
   python3 --version
   uname -a  # Linux/macOS
   # ou systeminfo sur Windows
   ```

2. **Logs d'erreur :**
   ```bash
   tail -50 ~/.dual-ai/logs/app.log
   ```

3. **Configuration :**
   ```bash
   cat ~/.dual-ai/config.yaml
   ```

4. **Étapes pour reproduire :**
   - Commandes exactes exécutées
   - Messages d'erreur complets
   - Comportement attendu vs observé

### Canaux de support

1. **GitHub Issues :** [https://github.com/yourusername/dual-ai-orchestrator/issues](https://github.com/yourusername/dual-ai-orchestrator/issues)
2. **Discord :** [https://discord.gg/dual-ai](https://discord.gg/dual-ai)
3. **Email :** support@dual-ai.dev

### Avant de contacter le support

- [ ] Vérifiez cette page de troubleshooting
- [ ] Recherchez dans les issues GitHub existantes
- [ ] Essayez en mode debug : `dual-ai --debug`
- [ ] Testez avec la configuration par défaut
- [ ] Vérifiez que tous les prérequis sont installés

## 🔄 Solutions rapides courantes

| Problème | Solution rapide |
|----------|----------------|
| `dual-ai: command not found` | `export PATH="$HOME/.local/bin:$PATH"` |
| Interface cassée | `export DUAL_AI_NO_RICH=1` |
| IA non trouvée | `npm install -g @anthropic-ai/claude-code` |
| Timeout | Augmenter `timeout` dans config.yaml |
| Consensus non atteint | Reformuler la demande plus précisément |
| Logs volumineux | `rm ~/.dual-ai/logs/*.log` |
| Config corrompue | `rm ~/.dual-ai/config.yaml && dual-ai` |
| Permissions | `chmod -R 755 ~/.dual-ai` |
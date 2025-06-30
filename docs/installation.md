# Guide d'installation de Dual AI Orchestrator

## 🚀 Installation rapide

La méthode la plus simple pour installer Dual AI Orchestrator est d'utiliser l'installateur interactif :

```bash
git clone https://github.com/yourusername/dual-ai-orchestrator
cd dual-ai-orchestrator
python install.py
```

L'installation prend environ 3-5 minutes et configure automatiquement votre environnement.

## 📋 Prérequis

### Prérequis système

- **Python 3.8 ou supérieur**
- **pip** (généralement inclus avec Python)
- **100 MB d'espace disque libre**
- Permissions d'écriture dans votre répertoire home

### Vérification des prérequis

```bash
# Vérifier Python
python --version
# ou
python3 --version

# Vérifier pip
pip --version
# ou
pip3 --version
```

### Outils IA requis

Dual AI Orchestrator nécessite au moins un des outils suivants :

#### Claude Code
```bash
# Via npm
npm install -g @anthropic-ai/claude-code

# Via pip
pip install claude-code
```

#### Gemini Code
```bash
# Via npm
npm install -g @google/gemini-code

# Via pip
pip install gemini-code
```

## 📦 Installation détaillée

### Méthode 1 : Installateur interactif (Recommandé)

1. **Télécharger le projet :**
   ```bash
   git clone https://github.com/yourusername/dual-ai-orchestrator
   cd dual-ai-orchestrator
   ```

2. **Lancer l'installateur :**
   ```bash
   python install.py
   ```

3. **Suivre les instructions :**
   L'installateur vous guidera à travers :
   - Vérification des prérequis
   - Configuration de l'installation
   - Installation des dépendances
   - Configuration de l'environnement

### Méthode 2 : Installation manuelle

1. **Cloner le repository :**
   ```bash
   git clone https://github.com/yourusername/dual-ai-orchestrator
   cd dual-ai-orchestrator
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt --user
   ```

3. **Installer l'application :**
   ```bash
   pip install -e . --user
   ```

4. **Créer la configuration :**
   ```bash
   mkdir -p ~/.dual-ai
   cp config/config.yaml ~/.dual-ai/config.yaml
   ```

### Méthode 3 : Via PyPI (Futur)

```bash
pip install dual-ai-orchestrator
```

## 🔧 Configuration

### Fichier de configuration

Le fichier de configuration principal se trouve dans `~/.dual-ai/config.yaml`.

Exemple de configuration :

```yaml
app:
  debug: false

ai:
  claude:
    command: "claude"
    timeout: 120
    enabled: true
  gemini:
    command: "gemini"
    timeout: 120
    enabled: true

ui:
  max_debate_rounds: 3
  auto_save_solutions: true
```

### Variables d'environnement

Vous pouvez également configurer via des variables d'environnement :

```bash
export DUAL_AI_DEBUG=true
export DUAL_AI_CLAUDE_COMMAND=claude
export DUAL_AI_GEMINI_COMMAND=gemini
export DUAL_AI_MAX_ROUNDS=5
```

## 🖥️ Installation par OS

### Ubuntu/Debian

```bash
# Installer Python et pip
sudo apt update
sudo apt install python3 python3-pip git

# Cloner et installer
git clone https://github.com/yourusername/dual-ai-orchestrator
cd dual-ai-orchestrator
python3 install.py
```

### CentOS/RHEL

```bash
# Installer Python et pip
sudo yum install python3 python3-pip git
# ou sur les versions récentes :
sudo dnf install python3 python3-pip git

# Cloner et installer
git clone https://github.com/yourusername/dual-ai-orchestrator
cd dual-ai-orchestrator
python3 install.py
```

### macOS

```bash
# Installer Homebrew si nécessaire
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Python
brew install python git

# Cloner et installer
git clone https://github.com/yourusername/dual-ai-orchestrator
cd dual-ai-orchestrator
python3 install.py
```

### Windows

1. **Installer Python :**
   - Télécharger depuis [python.org](https://python.org)
   - Cocher "Add Python to PATH"

2. **Installer Git :**
   - Télécharger depuis [git-scm.com](https://git-scm.com)

3. **Ouvrir PowerShell et installer :**
   ```powershell
   git clone https://github.com/yourusername/dual-ai-orchestrator
   cd dual-ai-orchestrator
   python install.py
   ```

## ✅ Vérification de l'installation

Après l'installation, vérifiez que tout fonctionne :

```bash
# Vérifier que la commande est disponible
dual-ai --version

# Tester l'importation Python
python -c "import dual_ai; print(dual_ai.__version__)"

# Vérifier la configuration
ls ~/.dual-ai/
```

## 🚨 Résolution de problèmes

### Erreur : "dual-ai command not found"

1. Vérifiez que le répertoire est dans votre PATH :
   ```bash
   echo $PATH | grep -o ~/.local/bin
   ```

2. Si absent, ajoutez-le :
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Erreur : "Permission denied"

```bash
# Donnez les permissions d'exécution
chmod +x ~/.local/bin/dual-ai
```

### Erreur : Module 'dual_ai' not found

```bash
# Réinstallez en mode développement
pip install -e . --user
```

### Problèmes avec Rich

Si Rich ne s'affiche pas correctement :

```bash
# Vérifiez votre terminal
echo $TERM

# Désactivez Rich si nécessaire
export DUAL_AI_NO_RICH=1
dual-ai
```

### Claude/Gemini non trouvés

1. Vérifiez l'installation :
   ```bash
   which claude
   which gemini
   ```

2. Installez les outils manquants :
   ```bash
   npm install -g @anthropic-ai/claude-code
   npm install -g @google/gemini-code
   ```

## 🔄 Mise à jour

Pour mettre à jour Dual AI Orchestrator :

```bash
cd dual-ai-orchestrator
git pull origin main
python install.py
```

## 🗑️ Désinstallation

Pour désinstaller complètement :

```bash
cd dual-ai-orchestrator
python uninstall.py
```

Ou manuellement :

```bash
pip uninstall dual-ai-orchestrator
rm -rf ~/.dual-ai
rm ~/.local/bin/dual-ai
```

## 🆘 Support

Si vous rencontrez des problèmes :

1. Consultez la [FAQ](troubleshooting.md)
2. Ouvrez une [issue sur GitHub](https://github.com/yourusername/dual-ai-orchestrator/issues)
3. Rejoignez notre [Discord](https://discord.gg/dual-ai)

## 📝 Installation pour le développement

Si vous voulez contribuer au projet :

```bash
# Fork et clone votre fork
git clone https://github.com/VOTRE-USERNAME/dual-ai-orchestrator
cd dual-ai-orchestrator

# Installer en mode développement
pip install -e ".[dev]" --user

# Installer les hooks pre-commit
pre-commit install

# Lancer les tests
pytest
```
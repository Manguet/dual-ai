# 🤖 Dual AI Orchestrator

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-80%25-yellowgreen)

Un orchestrateur intelligent qui unifie Claude Code et Gemini Code pour une collaboration optimale entre IA.

## ✨ Fonctionnalités

- 🎯 **Interface unifiée** : Une seule commande pour deux IA
- 🤝 **Débat collaboratif** : Les IA négocient pour trouver la meilleure solution
- 🚀 **Installation simple** : Installateur interactif en 3 minutes
- 🎨 **Interface moderne** : Rich UI avec animations et couleurs
- 🔧 **Configuration flexible** : YAML et variables d'environnement

## 📸 Démo

```bash
$ dual-ai
╭─────────────────── Dual AI Orchestrator v1.0.0 ───────────────────╮
│ 🤖 Claude: ✓ Ready    🤖 Gemini: ✓ Ready    📁 /home/user/project │
╰────────────────────────────────────────────────────────────────────╯

#01 › Crée une fonction Python pour calculer les nombres premiers

🔄 Claude structure votre demande...
💭 Débat en cours entre les IA...
✅ Consensus atteint après 2 rounds !

Quelle IA doit implémenter la solution ?
1. Claude
2. Gemini

Choix › _
```

## 🚀 Installation rapide

```bash
# 1. Cloner le repository
git clone https://github.com/Manguet/dual-ai
cd dual-ai-orchestrator

# 2. Lancer l'installateur interactif
python3 install_simple.py

# 3. C'est tout ! Lancez l'orchestrateur
dual-ai
```

## 📖 Documentation

- [Guide d'installation détaillé](docs/installation.md)
- [Guide d'utilisation](docs/usage.md)
- [Configuration avancée](docs/configuration.md)
- [Résolution de problèmes](docs/troubleshooting.md)

## 🛠️ Prérequis

- Python 3.8 ou supérieur
- Claude Code installé (`npm install -g @anthropic-ai/claude-code`)
- Gemini Code installé (`npm install -g @google/gemini-code`)

## 💡 Exemples d'utilisation

### Utilisation basique
```bash
$ dual-ai
#01 › Crée une API REST avec FastAPI pour gérer des tâches
```

### Avec configuration personnalisée
```bash
$ dual-ai --config ~/.my-config.yaml
```

### Mode debug
```bash
$ dual-ai --debug
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](CONTRIBUTING.md).

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

- 📧 Email : support@dual-ai.dev
- 💬 Discord : [Rejoindre le serveur](https://discord.gg/dual-ai)
- 🐛 Issues : [GitHub Issues](https://github.com/Manguet/dual-ai/issues)

---

Fait avec ❤️ par la communauté open source

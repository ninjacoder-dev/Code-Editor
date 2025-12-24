# Code Editor

Un éditeur de code multi-langage léger et extensible construit avec Python et Tkinter. Cet outil permet de rédiger, de compiler et d'exécuter divers langages de programmation, ainsi que de prévisualiser des projets web en temps réel.

## 🚀 Fonctionnalités

- **Interface Multi-onglets** : Gérez plusieurs fichiers simultanément grâce à un système d'onglets intuitif.
- **Coloration Syntaxique** : Support pour Python, C, C++, Java, C#, PHP et HTML via des expressions régulières.
- **Gestionnaire d'Exécution** : Lancez vos scripts et programmes directement depuis l'éditeur.
- **Aperçu Web Intégré** : Serveur statique et PHP intégré pour tester vos pages web instantanément.
- **Linter Python** : Vérification syntaxique en temps réel utilisant le module AST.
- **Configuration Personnalisée** : Définissez les chemins vers vos compilateurs (gcc, javac, etc.) via une interface dédiée.

## 📂 Structure du Projet

L'application est découpée en plusieurs modules spécialisés :

* `main.py` : Point d'entrée de l'application et gestion de l'interface utilisateur (UI).
* `editor_widget.py` : Composant de zone de texte avec numérotation de lignes et auto-indentation.
* `syntax_highlighter.py` : Moteur de coloration syntaxique.
* `execution_manager.py` : Gestion des processus de compilation et d'exécution.
* `web_preview.py` : Serveur local pour la prévisualisation HTML et PHP.
* `config_manager.py` : Gestion de la persistance des paramètres dans `config.json`.
* `linter_integration.py` : Analyseur de syntaxe pour Python.

## 🛠️ Prérequis

### Système
L'application utilise uniquement la bibliothèque standard de **Python 3.x**. Cependant, pour exécuter les différents langages, vous devez installer les outils suivants sur votre système :

* **C/C++** : GCC / G++ (MinGW sur Windows)
* **Java** : JDK (javac & java)
* **C#** : CSC (C# Compiler)
* **PHP** : Runtime PHP (pour le serveur de preview)

### Dépendance Linux (si applicable)
Si vous êtes sur Linux, assurez-vous que `tkinter` est installé :
```bash
sudo apt-get install python3-tk

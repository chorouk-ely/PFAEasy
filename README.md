# 🎓 Générateur Automatique de Rapport PFA

Générez, structurez et exportez votre mémoire académique (Projet de Fin d'Études ou d'Année) en quelques clics grâce à l'Intelligence Artificielle.

# Alors ce projet :

1- Un assistant IA qui génère :la structure et du contenu d’amorce

2-un générateur de mémoire prêt-à-compléter.

## 🚀 Fonctionnalités

- **Génération par IA** : Utilise le modèle **Llama 3 (via Groq)** pour rédiger les sections de votre rapport (Résumé, Introduction, Chapitres, Conclusion, etc.).
- **Édition Interactive** : Relisez et modifiez le contenu généré directement dans l'interface avant l'export.
- **Export Multi-format** :
  - **PDF Élégant** : Généré avec **ReportLab**, incluant une page de garde professionnelle et le logo de votre institution.
  - **Word (DOCX)** : Généré avec **python-docx**, entièrement modifiable pour les ajustements finaux.
- **Personnalisation** : Configurez votre nom, institution, entreprise d'accueil et encadrant.

## 🛠️ Installation

1. **Cloner le projet** :
   ```bash
   git clone <url-du-repo>
   cd prompting
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer l'environnement** :
   Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Groq :
   ```env
   GROQ_API_KEY=votre_cle_api_ici
   ```

## 📖 Utilisation

Lancez l'application Streamlit :
```bash
streamlit run app.py
```

1. **Accueil** : Cliquez sur "Démarrer la rédaction maintenant".
2. **Configuration** : Remplissez vos informations dans la barre latérale.
3. **Rédaction** : Saisissez le titre, le sujet et le plan de votre PFA, puis cliquez sur "Générer le texte".
4. **Édition** : Modifiez les textes générés si nécessaire.
5. **Export** : Cliquez sur "Générer les documents" pour télécharger votre rapport en PDF et Word.

## 🧰 Technologies utilisées

- **Python** : Langage principal.
- **Streamlit** : Interface utilisateur web.
- **Groq API (Llama 3)** : Moteur d'IA pour la génération de texte.
- **ReportLab** : Création de documents PDF.
- **python-docx** : Création de documents Word.
- **python-dotenv** : Gestion des variables d'environnement.

---
*Développé pour faciliter la rédaction académique.*
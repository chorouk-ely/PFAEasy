import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SECTIONS = [
    {
        "id": "resume_fr",
        "title": "Résumé en français",
        "prompt": "Génère le résumé en français du rapport.",
        "tooltip": "Un court paragraphe (150–250 mots) résumant l'objectif, la méthode et les principaux résultats du projet.",
        "min_words": 150
    },
    {
        "id": "resume_ar",
        "title": "Résumé en arabe",
        "prompt": "Génère le résumé en arabe du rapport. Assure-toi que la langue est correcte et professionnelle.",
        "tooltip": "ملخص قصير (150–250 كلمة) يصف هدف المشروع، المنهجية المتبعة، والنتائج الرئيسية باللغة العربية الفصحى.",
        "min_words": 150
    },
    {
        "id": "resume_en",
        "title": "Résumé en anglais",
        "prompt": "Génère l'abstract (résumé en anglais) du rapport. CETTE SECTION DOIT ÊTRE RÉDIGÉE INTÉGRALEMENT EN ANGLAIS (WRITE ENTIRELY IN ENGLISH).",
        "tooltip": "An abstract (150–250 words) summarizing the project's objective, methodology, and key results in English.",
        "min_words": 150
    },
    {
        "id": "remerciements",
        "title": "Remerciements",
        "prompt": "Génère une page de remerciements formelle pour un rapport de PFA.",
        "tooltip": "Remerciements formels adressés à l'encadrant, aux enseignants et à l'entreprise. Soyez sincère et professionnel (100–200 mots).",
        "min_words": 100
    },
    {
        "id": "intro_generale",
        "title": "Introduction générale",
        "prompt": "Génère l'introduction détaillée du rapport incluant le contexte.",
        "tooltip": "Présente le contexte général, la problématique, les objectifs du projet et le plan du rapport. Doit faire 300–500 mots.",
        "min_words": 300
    },
    {
        "id": "chapitre_1",
        "title": "Chapitre 1 : Présentation de l'entreprise",
        "prompt": "Génère le Chapitre 1 complet, portant sur la présentation de l'entreprise d'accueil.",
        "tooltip": "Décrit l'entreprise d'accueil : secteur, activités, organigramme, missions du stage. Attendu : 400–700 mots.",
        "min_words": 400
    },
    {
        "id": "chapitre_2",
        "title": "Chapitre 2 : Problématique, méthode et outils",
        "prompt": "Génère le Chapitre 2 complet, détaillant la problématique, la méthode de travail adoptée, et les outils utilisés.",
        "tooltip": "Analyse la problématique, justifie les choix méthodologiques (ex: Agile, Scrum) et présente l'environnement technologique. Attendu : 500–800 mots.",
        "min_words": 500
    },
    {
        "id": "chapitre_3",
        "title": "Chapitre 3 : Modélisation et réalisation",
        "prompt": "Génère le Chapitre 3 complet, détaillant la modélisation (diagrammes UML ou autres) et la réalisation (développement, architecture).",
        "tooltip": "Présente la conception (diagrammes UML, architecture) et la réalisation (interfaces, fonctionnalités développées). C'est le chapitre le plus important. Attendu : 700–1200 mots.",
        "min_words": 700
    },
    {
        "id": "conclusion",
        "title": "Conclusion générale",
        "prompt": "Génère la conclusion générale du rapport et les perspectives.",
        "tooltip": "Synthèse des travaux réalisés, bilan des objectifs atteints et ouverture sur des perspectives futures. Attendu : 200–400 mots.",
        "min_words": 200
    },
    {
        "id": "bibliographie",
        "title": "Bibliographie",
        "prompt": "Génère une bibliographie plausible basée sur les technologies et le sujet. Utilise le format APA. Uniquement les références.",
        "tooltip": "Liste des références bibliographiques en format APA. Incluez livres, articles, sites officiels et documentations techniques utilisées.",
        "min_words": 50
    }
]

def generate_section(context_inputs, section):
    # Retrieve api key directly from env or use the user provided one if passed, but it's handled globally here since we only have .env config based on the original structure.
    # However we will use Groq client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "votre_cle_api_groq":
        raise Exception("Veuillez configurer votre GROQ_API_KEY dans le fichier .env")

    client = Groq(api_key=api_key)

    # Context construction
    context_str = f"""
Informations sur le projet :
- Nom de l'étudiant : {context_inputs.get('student_name', '')}
- Titre du mémoire : {context_inputs.get('title', '')}
- Institution : {context_inputs.get('university', '')}
- Entreprise d'accueil : {context_inputs.get('company', '')}
- Spécialité : {context_inputs.get('specialty', '')}
- Sujet : {context_inputs.get('subject', '')}
- Problématique : {context_inputs.get('problematic', '')}
- Plan du mémoire : {context_inputs.get('plan', '')}
- Technologies utilisées : {context_inputs.get('techs', '')}
"""
    
    system_prompt = (
        "Tu es un expert en rédaction de mémoires universitaires (PFA). "
        "Ta tâche est de générer UNE section précise du rapport. "
        "NE GÉNÈRE QUE CE QUI EST DEMANDÉ. N'invente pas de détails contradictoires "
        "avec les informations fournies. Évite de générer le titre principal de la section. "
        "Formate le contenu en Markdown."
    )

    prompt = context_str + "\n\nDemande:\n" + section['prompt']

    # Append user custom instructions if provided
    custom_instruction = context_inputs.get('custom_instruction', '').strip()
    if custom_instruction:
        prompt += f"\n\nInstructions supplémentaires de l'utilisateur pour cette section:\n{custom_instruction}"


    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erreur API Groq: {e}.")


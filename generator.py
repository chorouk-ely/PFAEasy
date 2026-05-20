import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SECTIONS = [
    {
        "id": "resume_fr",
        "title": "Résumé en français",
        "prompt": "Génère le résumé en français du rapport."
    },
    {
        "id": "resume_ar",
        "title": "Résumé en arabe",
        "prompt": "Génère le résumé en arabe du rapport. Assure-toi que la langue est correcte et professionnelle."
    },
    {
        "id": "resume_en",
        "title": "Résumé en anglais",
        "prompt": "Génère l'abstract (résumé en anglais) du rapport."
    },
    {
        "id": "remerciements",
        "title": "Remerciements",
        "prompt": "Génère une page de remerciements formelle pour un rapport de PFA."
    },
    {
        "id": "intro_generale",
        "title": "Introduction générale",
        "prompt": "Génère l'introduction détaillée du rapport incluant le contexte."
    },
    {
        "id": "chapitre_1",
        "title": "Chapitre 1 : Présentation de l'entreprise",
        "prompt": "Génère le Chapitre 1 complet, portant sur la présentation de l'entreprise d'accueil."
    },
    {
        "id": "chapitre_2",
        "title": "Chapitre 2 : Problématique, méthode et outils",
        "prompt": "Génère le Chapitre 2 complet, détaillant la problématique, la méthode de travail adoptée, et les outils utilisés."
    },
    {
        "id": "chapitre_3",
        "title": "Chapitre 3 : Modélisation et réalisation",
        "prompt": "Génère le Chapitre 3 complet, détaillant la modélisation (diagrammes UML ou autres) et la réalisation (développement, architecture)."
    },
    {
        "id": "conclusion",
        "title": "Conclusion générale",
        "prompt": "Génère la conclusion générale du rapport et les perspectives."
    },
    {
        "id": "bibliographie",
        "title": "Bibliographie",
        "prompt": "Génère une bibliographie plausible basée sur les technologies et le sujet. Utilise le format APA. Uniquement les références."
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


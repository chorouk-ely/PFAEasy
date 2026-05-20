import streamlit as st
import os
import time
from dotenv import load_dotenv
from generator import SECTIONS, generate_section
from pdf_builder import create_pdf
from docx_builder import create_docx

load_dotenv()

st.set_page_config(page_title="Générateur de PFA", page_icon="🎓", layout="wide")

# Inject Custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("style.css")
except Exception:
    pass

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

def go_to_generator():
    st.session_state['page'] = 'generator'

if st.session_state['page'] == 'home':
    st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>🚀 Rédigez votre PFA avec l'IA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #94a3b8; font-weight: 300;'>Générez, structurez et exportez votre mémoire académique en quelques clics.</h3>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("💡 **Comment ça marche ?**\n\n1. Saisissez les informations de votre PFA (sujet, plan, technologies).\n2. Notre IA (modèle Llama 3) génère un contenu structuré et pertinent.\n3. Révisez le texte et exportez directement en **PDF élégant** avec page de garde ou en **Word modifiable**.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Démarrer la rédaction maintenant", type="primary", use_container_width=True, on_click=go_to_generator)

elif st.session_state['page'] == 'generator':
    st.title("🎓 Générateur Automatique de Rapport PFA")
    st.write("Générez et éditez votre rapport de PFA section par section avant l'export (PDF & Word).")

    # Initialize session state for sections
    if 'generated_sections' not in st.session_state:
        st.session_state['generated_sections'] = {}

    # --- SIDEBAR: Configuration ---
    st.sidebar.header("⚙️ Informations de l'Étudiant")
    student_name = st.sidebar.text_input("Nom et Prénom")
    university = st.sidebar.text_input("Institution (Université / École)")
    company = st.sidebar.text_input("Entreprise d'accueil")
    specialty = st.sidebar.text_input("Spécialité / Filière")
    supervisor = st.sidebar.text_input("Encadrant(e)")
    academic_year = st.sidebar.text_input("Année Universitaire", value="2023-2024")
    logo_file = st.sidebar.file_uploader("Logo de l'institution (PNG/JPG)", type=["png", "jpg", "jpeg"])

    st.sidebar.markdown("---")
    st.sidebar.header("📑 Sections à générer")
    # Map id to title
    section_options = {s['id']: s for s in SECTIONS}
    selected_ids = st.sidebar.multiselect(
        "Choisissez les sections",
        options=list(section_options.keys()),
        default=list(section_options.keys()),
        format_func=lambda x: section_options[x]['title']
    )

    # --- MAIN PAGE: Subject & Generation ---
    st.header("📝 Détails du Projet")
    title = st.text_input("Titre du mémoire :", placeholder="Ex: Développement d'une plateforme web pour la gestion...")
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_area("Sujet du projet :", height=150)
        problematic = st.text_area("Problématique :", height=150)
    with col2:
        plan = st.text_area("Plan du mémoire :", height=150, placeholder="Chapitre 1: ...\nChapitre 2: ...")
        techs = st.text_input("Technologies utilisées :", placeholder="Ex: Python, Streamlit, Groq, ReportLab")

    if st.button("🚀 1. Générer le texte (IA)", type="primary"):
        if not title.strip() or not subject.strip():
            st.warning("Veuillez entrer au moins le titre et le sujet du PFA.")
        elif not selected_ids:
            st.warning("Veuillez sélectionner au moins une section.")
        elif not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "votre_cle_api_groq":
            st.error("Veuillez configurer votre GROQ_API_KEY dans le fichier .env")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            context_inputs = {
                "student_name": student_name,
                "title": title,
                "university": university,
                "company": company,
                "specialty": specialty,
                "subject": subject,
                "problematic": problematic,
                "plan": plan,
                "techs": techs
            }
            
            # We only generate sections that are selected
            for i, sid in enumerate(selected_ids):
                section = section_options[sid]
                status_text.text(f"Rédaction de la section : {section['title']}...")
                try:
                    content = generate_section(context_inputs, section)
                    st.session_state['generated_sections'][sid] = content
                except Exception as e:
                    st.error(f"Erreur lors de la génération de {section['title']}: {str(e)}")
                    break
                    
                progress_bar.progress((i + 1) / len(selected_ids))
                
            status_text.success("Génération terminée ! Vous pouvez maintenant modifier le texte ci-dessous.")

    # --- MAIN PAGE: Interactive Editing ---
    if st.session_state['generated_sections']:
        st.markdown("---")
        st.markdown("### ✍️ 2. Édition des sections")
        st.info("Relisez et corrigez le contenu généré par l'IA avant d'exporter en PDF ou Word.")
        
        # Store edited content in a temporary dictionary
        edited_contents = {}
        
        for sid in selected_ids:
            if sid in st.session_state['generated_sections']:
                section_title = section_options[sid]['title']
                edited_contents[sid] = st.text_area(
                    label=section_title, 
                    value=st.session_state['generated_sections'][sid], 
                    height=300,
                    key=f"edit_{sid}"
                )
                
        # --- MAIN PAGE: PDF Export ---
        st.markdown("---")
        st.markdown("### 📄 3. Exportation")
        if st.button("💾 Générer les documents avec ces modifications"):
            status_text = st.empty()
            status_text.info("Assemblage et formatage des documents en cours...")
            
            # Handle logo save temporarily
            logo_path = None
            if logo_file:
                logo_path = f"temp_logo_{logo_file.name}"
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())

            output_pdf_path = "Rapport_PFA_Complet.pdf"
            output_docx_path = "Rapport_PFA_Complet.docx"
            try:
                # Generate PDF
                create_pdf(
                    title=title.strip(),
                    student_name=student_name,
                    university=university,
                    company=company,
                    specialty=specialty,
                    supervisor=supervisor,
                    academic_year=academic_year,
                    logo_path=logo_path,
                    sections_dict=edited_contents,
                    section_options=section_options,
                    selected_ids=selected_ids,
                    output_path=output_pdf_path
                )
                
                # Generate DOCX
                create_docx(
                    title=title.strip(),
                    student_name=student_name,
                    university=university,
                    company=company,
                    specialty=specialty,
                    supervisor=supervisor,
                    academic_year=academic_year,
                    logo_path=logo_path,
                    sections_dict=edited_contents,
                    section_options=section_options,
                    selected_ids=selected_ids,
                    output_path=output_docx_path
                )

                status_text.success("Rapports générés avec succès !")
                
                c1, c2 = st.columns(2)
                with c1:
                    with open(output_pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Télécharger le Rapport (PDF)",
                            data=pdf_file,
                            file_name="Rapport_PFA.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                with c2:
                    with open(output_docx_path, "rb") as docx_file:
                        st.download_button(
                            label="📥 Télécharger le Rapport (Word)",
                            data=docx_file,
                            file_name="Rapport_PFA.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
            except Exception as e:
                status_text.error(f"Erreur lors de la création : {str(e)}")
            finally:
                # Cleanup temp logo
                if logo_path and os.path.exists(logo_path):
                    os.remove(logo_path)


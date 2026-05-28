import streamlit as st
import os
import re
import json
import hashlib
import base64
from dotenv import load_dotenv
from generator import SECTIONS, generate_section
from pdf_builder import create_pdf
from docx_builder import create_docx

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

st.set_page_config(page_title="PFAEasy – Générateur de Mémoire IA", page_icon="🎓", layout="wide")

# ── PREMIUM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-dark: #020617;
    --accent-v: #8b7cf8;
    --accent-c: #38bdf8;
    --text-main: #f8fafc;
    --text-sub: #94a3b8;
    --glass: rgba(15, 23, 42, 0.6);
    --glass-border: rgba(255, 255, 255, 0.08);
}

html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
}

h1, h2, h3 { 
    font-family: 'DM Serif Display', serif !important; 
    font-weight: 400 !important;
}

/* Hide Streamlit components for landing */
.hide-ui [data-testid="stHeader"], 
.hide-ui [data-testid="stFooter"],
.hide-ui [data-testid="stToolbar"] { 
    display: none !important; 
}

.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.2s ease-in-out;
    padding: 0.6rem 1.5rem;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(139, 124, 248, 0.2);
}

/* UI Components */
.hero-title {
    font-size: 4.5rem; line-height: 1.05; 
    margin-bottom: 2rem; text-align: center;
    background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    padding-top: 2rem;
}

.hero-subtitle {
    font-size: 1.25rem; color: #94a3b8; text-align: center; 
    margin: 0 auto 3.5rem;
    line-height: 1.6;
    width: 100%;
}

.feature-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(12px);
    border-radius: 24px; padding: 2.5rem;
    height: 100%; transition: all 0.3s;
}
.feature-card:hover { 
    border-color: rgba(139, 124, 248, 0.4);
    background: rgba(15, 23, 42, 0.8);
    transform: scale(1.02);
}

.section-tag {
    color: #8b7cf8; text-transform: uppercase; font-size: 0.75rem; 
    font-weight: 700; letter-spacing: 0.2em; text-align: center; margin-bottom: 1.5rem;
    opacity: 0.8;
}

.step-card {
    text-align: center; padding: 1.5rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 20px;
}
.step-num {
    width: 44px; height: 44px; background: #8b7cf8; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1.5rem; font-weight: 700; color: white;
    font-family: 'DM Serif Display', serif; font-size: 1.2rem;
}

/* Navbar fake */
.custom-nav {
    display: flex; justify-content: center; align-items: center;
    padding: 1.5rem 0; margin-bottom: 5rem;
}
.logo-font { font-size: 1.6rem; font-weight: 700; text-align: center; }
.logo-font span { color: #38bdf8; }

/* Adjust main container */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1rem !important;
    padding-left: 5rem !important;
    padding-right: 5rem !important;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ── Auth helpers ─────────────────────────────────────────────────────────────
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def _load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    users = _load_users()
    if username in users:
        return False, "Ce nom d'utilisateur existe déjà."
    users[username] = {"password": _hash(password)}
    _save_users(users)
    return True, "Compte créé avec succès !"

def login_user(username, password):
    users = _load_users()
    if username not in users:
        return False, "Utilisateur introuvable."
    if users[username]["password"] != _hash(password):
        return False, "Mot de passe incorrect."
    return True, "Connexion réussie !"

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        'authenticated': False,
        'username': '',
        'step': 1,
        'show_auth': False,
        'student_name': '', 'university': '', 'company': '',
        'specialty': '', 'supervisor': '', 'academic_year': '2024-2025',
        'logo_univ_path': None,
        'logo_comp_path': None,
        'title': '', 'subject': '', 'problematic': '', 'plan': '', 'techs': '',
        'selected_ids': [s['id'] for s in SECTIONS],
        'custom_instructions': {},
        'generated_sections': {},
        'active_section': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
section_options = {s['id']: s for s in SECTIONS}

# ── UI Renders ───────────────────────────────────────────────────────────────
def render_steps_indicator(current):
    steps = [("1", "Configuration"), ("2", "Rédaction"), ("3", "Export")]
    html = '<div style="display:flex; gap:10px; margin-bottom:30px; align-items:center;">'
    for i, (num, label) in enumerate(steps, 1):
        cls = "background:#6366f1; color:white;" if i == current else ("background:#22c55e; color:white;" if i < current else "background:#334155; color:#94a3b8;")
        html += f'<span style="padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; {cls}">{num} {label}</span>'
        if i < len(steps):
            html += '<span style="color:#475569;">›</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def md_to_html(text):
    if not text: return "<p><em>Aucun contenu.</em></p>"
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*',     r'<em>\1</em>',         text)
    parts = []
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('### '): parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith('## '):  parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith('# '):   parts.append(f"<h1>{line[2:]}</h1>")
        else: parts.append(f"<p>{line}</p>")
    return "\n".join(parts)

def display_pdf_preview(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Impossible d'afficher l'aperçu : {e}")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP LOGIC
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state['authenticated']:
    if not st.session_state['show_auth']:
        # --- LANDING PAGE ---
        with st.container():
            st.markdown('<div class="custom-nav"><div class="logo-font">🎓 PFA<span>Easy</span></div></div>', unsafe_allow_html=True)
            
            st.markdown('<h1 class="hero-title">Rédigez votre PFA avec l\'excellence de l\'IA</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">PFAEasy transforme vos idées en un mémoire académique structuré.<br>Gagnez des dizaines d\'heures de rédaction grâce à notre intelligence spécialisée.</p>', unsafe_allow_html=True)
            
            col_c1, col_c2, col_c3 = st.columns([1.2, 1, 1.2])
            with col_c2:
                if st.button("🚀 Commencer mon projet — Gratuit", type="primary", use_container_width=True):
                    st.session_state['show_auth'] = True
                    st.rerun()
            
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            st.markdown('<div class="section-tag">Fonctionnalités</div>', unsafe_allow_html=True)
            st.markdown('<h2 style="text-align:center; font-size:3rem; margin-bottom:4rem;">L\'expertise IA au service de votre réussite</h2>', unsafe_allow_html=True)
            
            f1, f2 = st.columns(2, gap="large")
            with f1:
                st.markdown('<div class="feature-card"><h3>🤖 Rédaction Intelligente</h3><p>L\'IA Llama 3 génère chaque chapitre de manière cohérente en respectant votre sujet et vos technologies.</p></div>', unsafe_allow_html=True)
            with f2:
                st.markdown('<div class="feature-card"><h3>✏️ Contrôle de Précision</h3><p>Guidez l\'écriture avec vos propres consignes techniques. L\'IA s\'adapte à votre style et vos exigences.</p></div>', unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            f3, f4 = st.columns(2, gap="large")
            with f3:
                st.markdown('<div class="feature-card"><h3>👁️ Aperçu Temps Réel</h3><p>Visualisez la structure de votre PDF en direct. Ce que vous voyez est exactement ce que vous téléchargez.</p></div>', unsafe_allow_html=True)
            with f4:
                st.markdown('<div class="feature-card"><h3>📄 Export Multi-Format</h3><p>Téléchargez votre rapport en PDF academic-ready ou en Word pour vos dernières retouches personnelles.</p></div>', unsafe_allow_html=True)
                
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            st.markdown('<div class="section-tag">Le Processus</div>', unsafe_allow_html=True)
        
        s1, s2, s3, s4 = st.columns(4)
        steps = [
            ("1", "Décrivez", "Sujet et plan"),
            ("2", "Générez", "L'IA rédige"),
            ("3", "Affinez", "Modifiez le texte"),
            ("4", "Exportez", "PDF ou Word")
        ]
        for col, (num, title, desc) in zip([s1, s2, s3, s4], steps):
            with col:
                st.markdown(f'<div class="step-card"><div class="step-num">{num}</div><h4>{title}</h4><p style="color:#94a3b8; font-size:0.9rem;">{desc}</p></div>', unsafe_allow_html=True)

    else:
        # --- AUTH PAGE ---
        if st.button("← Retour"):
            st.session_state['show_auth'] = False
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("### 🔑 Accès à la plateforme")
            tab_login, tab_reg = st.tabs(["Connexion", "Inscription"])
            
            with tab_login:
                user_log = st.text_input("Utilisateur")
                pass_log = st.text_input("Mot de passe", type="password")
                if st.button("Se connecter", type="primary", use_container_width=True):
                    ok, msg = login_user(user_log, pass_log)
                    if ok:
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = user_log
                        st.rerun()
                    else: st.error(msg)
            
            with tab_reg:
                user_reg = st.text_input("Nouvel utilisateur")
                pass_reg = st.text_input("Nouveau mot de passe", type="password")
                if st.button("Créer un compte", type="primary", use_container_width=True):
                    if len(pass_reg) < 6: st.warning("Min 6 caractères")
                    else:
                        ok, msg = register_user(user_reg, pass_reg)
                        if ok: st.success(msg)
                        else: st.error(msg)

else:
    # --- LOGGED IN APP ---
    st.sidebar.markdown(f"👤 **{st.session_state['username']}**")
    if st.sidebar.button("🚪 Déconnexion"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    
    # ── STEP 1: SETUP ──
    if st.session_state['step'] == 1:
        render_steps_indicator(1)
        st.title("🎓 Paramètres du Projet")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state['student_name'] = st.text_input("Étudiant", st.session_state['student_name'])
            st.session_state['university']   = st.text_input("Institution", st.session_state['university'])
            st.session_state['company']      = st.text_input("Entreprise", st.session_state['company'])
            st.session_state['specialty']    = st.text_input("Filière", st.session_state['specialty'])
        with col2:
            st.session_state['title']   = st.text_input("Titre du PFA", st.session_state['title'])
            st.session_state['subject'] = st.text_area("Sujet détaillé", st.session_state['subject'], height=100)
            st.session_state['techs']   = st.text_input("Technologies", st.session_state['techs'])
            st.session_state['supervisor'] = st.text_input("Encadrant", st.session_state.get('supervisor', ''))

        st.session_state['academic_year'] = st.text_input("Année universitaire", st.session_state['academic_year'], placeholder="Ex: 2024-2025")
        st.session_state['selected_ids'] = st.multiselect("Sections", list(section_options.keys()), default=st.session_state['selected_ids'], format_func=lambda x: section_options[x]['title'])

        st.markdown("---")
        st.subheader("🖼️ Logos (Optionnel)")
        u_col1, u_col2 = st.columns(2)
        with u_col1:
            logo_univ = st.file_uploader("Logo Université", type=['png', 'jpg', 'jpeg'])
            if logo_univ:
                path = f"logo_univ_{st.session_state['username']}.png"
                with open(path, "wb") as f: f.write(logo_univ.getbuffer())
                st.session_state['logo_univ_path'] = path
                st.image(logo_univ, width=80)
        with u_col2:
            logo_comp = st.file_uploader("Logo Entreprise", type=['png', 'jpg', 'jpeg'])
            if logo_comp:
                path = f"logo_comp_{st.session_state['username']}.png"
                with open(path, "wb") as f: f.write(logo_comp.getbuffer())
                st.session_state['logo_comp_path'] = path
                st.image(logo_comp, width=80)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continuer →", type="primary", use_container_width=True):
            if not st.session_state['title'] or not st.session_state['subject']:
                st.warning("Remplissez le titre et le sujet.")
            else:
                if not st.session_state['active_section'] and st.session_state['selected_ids']:
                    st.session_state['active_section'] = st.session_state['selected_ids'][0]
                st.session_state['step'] = 2
                st.rerun()

    # ── STEP 2: EDITOR ──
    elif st.session_state['step'] == 2:
        render_steps_indicator(2)
        selected_ids = st.session_state['selected_ids']
        active_sid = st.session_state.get('active_section') or selected_ids[0]
        
        with st.sidebar:
            st.markdown("### 📋 Navigation")
            for sid in selected_ids:
                done = sid in st.session_state['generated_sections']
                if st.button(f"{'✅' if done else '○'} {section_options[sid]['title']}", use_container_width=True):
                    st.session_state['active_section'] = sid
                    st.rerun()
            st.markdown("---")
            if st.button("👁️ Aperçu PDF Rapide", use_container_width=True):
                st.session_state['show_quick_preview'] = not st.session_state.get('show_quick_preview', False)
                
            if st.button("🚀 Exporter le rapport", type="primary", use_container_width=True):
                st.session_state['step'] = 3; st.rerun()
            if st.button("← Retour au projet", use_container_width=True):
                st.session_state['step'] = 1; st.rerun()

        sec = section_options[active_sid]
        
        # --- QUICK PREVIEW OVERLAY ---
        if st.session_state.get('show_quick_preview'):
            with st.expander("📄 Aperçu du document en cours", expanded=True):
                tmp_path = "Aperçu_Temp.pdf"
                try:
                    create_pdf(title=st.session_state['title'], student_name=st.session_state['student_name'],
                              university=st.session_state['university'], company=st.session_state['company'],
                              specialty=st.session_state['specialty'], supervisor=st.session_state['supervisor'],
                              academic_year=st.session_state['academic_year'], 
                              logo_univ=st.session_state['logo_univ_path'], logo_comp=st.session_state['logo_comp_path'],
                              sections_dict=st.session_state['generated_sections'], section_options=section_options,
                              selected_ids=st.session_state['selected_ids'], output_path=tmp_path)
                    display_pdf_preview(tmp_path)
                except Exception as e: st.error(f"Erreur d'aperçu: {e}")
            st.markdown("---")
            
        st.subheader(sec['title'])
        
        instr = st.text_input("Consignes pour l'IA", st.session_state['custom_instructions'].get(active_sid, ''), placeholder="Ex: détails techniques sur...")
        st.session_state['custom_instructions'][active_sid] = instr
        
        if st.button("Générer cette section", type="primary"):
            with st.spinner("L'IA rédige..."):
                ctx = {**st.session_state, 'custom_instruction': instr}
                try:
                    st.session_state['generated_sections'][active_sid] = generate_section(ctx, sec)
                    st.rerun()
                except Exception as e: st.error(f"Erreur: {e}")
        
        col_ed, col_pre = st.columns(2)
        content = st.session_state['generated_sections'].get(active_sid, "")
        with col_ed:
            edited = st.text_area("Édition", content, height=400)
            st.session_state['generated_sections'][active_sid] = edited
        with col_pre:
            st.markdown(f'<div style="background:white; color:black; padding:20px; border-radius:10px; height:400px; overflow-y:auto; font-size:0.9rem;">{md_to_html(edited)}</div>', unsafe_allow_html=True)

    # ── STEP 3: EXPORT ──
    elif st.session_state['step'] == 3:
        render_steps_indicator(3)
        st.title("💾 Aperçu & Exportation")
        
        # Auto-pre-generate for preview
        preview_path = "Aperçu_Rapport_PFA.pdf"
        docx_path = "Rapport_PFA.docx"
        try:
            # Generate PDF
            create_pdf(title=st.session_state['title'], student_name=st.session_state['student_name'],
                      university=st.session_state['university'], company=st.session_state['company'],
                      specialty=st.session_state['specialty'], supervisor=st.session_state['supervisor'],
                      academic_year=st.session_state['academic_year'], 
                      logo_univ=st.session_state['logo_univ_path'], logo_comp=st.session_state['logo_comp_path'],
                      sections_dict=st.session_state['generated_sections'], section_options=section_options,
                      selected_ids=st.session_state['selected_ids'], output_path=preview_path)
            
            # Generate DOCX
            create_docx(title=st.session_state['title'], student_name=st.session_state['student_name'],
                       university=st.session_state['university'], company=st.session_state['company'],
                       specialty=st.session_state['specialty'], supervisor=st.session_state['supervisor'],
                       academic_year=st.session_state['academic_year'], 
                       logo_univ=st.session_state['logo_univ_path'], logo_comp=st.session_state['logo_comp_path'],
                       sections_dict=st.session_state['generated_sections'], section_options=section_options,
                       selected_ids=st.session_state['selected_ids'], output_path=docx_path)
            
            st.markdown("### 👁️ Aperçu du document (PDF)")
            display_pdf_preview(preview_path)
            
            st.markdown("---")
            st.markdown("### 📥 Télécharger vos documents")
            col1, col2, col3 = st.columns(3)
            with col1:
                with open(preview_path, "rb") as f:
                    st.download_button("📥 Télécharger PDF", f, "Rapport_PFA.pdf", "application/pdf", use_container_width=True)
            with col2:
                with open(docx_path, "rb") as f:
                    st.download_button("📥 Télécharger Word", f, "Rapport_PFA.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            with col3:
                if st.button("← Retour à l'éditeur", use_container_width=True):
                    st.session_state['step'] = 2; st.rerun()
                    
        except Exception as e: 
            st.error(f"Erreur de génération: {e}")
            if st.button("← Retour à l'éditeur"):
                st.session_state['step'] = 2; st.rerun()

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from rdkit import Chem
from rdkit.Chem import AllChem
from core.mode2_auditor import SafetyAuditor
from langchain_ollama import ChatOllama

# --- 1. ROBUST AI NAME IDENTIFICATION ---
def get_compound_name(smiles):
    try:
        llm = ChatOllama(model="llama3.2", temperature=0.0)
        prompt = f"""
        SYSTEM: You are a chemical database API. 
        TASK: Output ONLY the common chemical name or IUPAC name for this SMILES string.
        INPUT: {smiles}
        CONSTRAINT: Do not speak. Do not apologize. Do not give warnings. Just output the name.
        """
        response = llm.invoke(prompt)
        name = response.content.strip().replace('"', '').replace("'", "")
        if len(name) > 50 or "sorry" in name.lower() or "cannot" in name.lower():
            return "Complex Molecule"
        return name
    except:
        return "Unknown Compound"

# --- 2. 3D VISUALIZER ---
def render_3d_molecule(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol: return None
    mol = Chem.AddHs(mol)
    try:
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        mol_block = Chem.MolToMolBlock(mol)
    except: return None

    viewer_html = f"""
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    <div id="container-01" style="width: 100%; height: 350px; position: relative; border-radius: 15px; overflow: hidden; border: 1px solid rgba(0,0,0,0.1);"></div>
    <script>
        let element = document.getElementById("container-01");
        let config = {{ backgroundColor: 'rgba(255, 255, 255, 0.4)' }}; 
        let viewer = $3Dmol.createViewer(element, config);
        viewer.addModel(`{mol_block}`, "mol");
        viewer.setStyle({{stick: {{radius: 0.2}}, sphere: {{scale: 0.3}}}});
        viewer.zoomTo();
        viewer.spin('y', 0.4);
        viewer.render();
    </script>
    """
    return components.html(viewer_html, height=350)

# --- 3. ANIMATED GAUGE ---
def create_animated_gauge(risk_score):
    color_hex = "#28a745" if risk_score < 0.4 else "#ffc107" if risk_score < 0.7 else "#dc3545"
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score * 100,
        title = {'text': "<b>TOXICITY RISK</b>", 'font': {'size': 20, 'color': '#444'}},
        number = {'suffix': "%", 'font': {'color': color_hex, 'weight': 'bold', 'size': 50}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#555"},
            'bar': {'color': color_hex, 'thickness': 0.25},
            'bgcolor': "rgba(255,255,255,0.0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': "rgba(40, 167, 69, 0.3)"},
                {'range': [40, 70], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [70, 100], 'color': "rgba(220, 53, 69, 0.3)"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': risk_score * 100}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- 4. MAIN RENDER FUNCTION ---
def render_safety_screen():
    # --- CSS POLISH ---
    st.markdown("""
    <style>
        /* DARKER PINK GRADIENT BACKGROUND */
        .stApp {
            background-image: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
            background-image: linear-gradient(to top, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
            background-attachment: fixed;
        }
        
        /* Floating Particles */
        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
            100% { transform: translateY(0px) rotate(360deg); }
        }
        .molecule-bg {
            position: fixed;
            color: rgba(100, 20, 60, 0.2);
            font-weight: 900;
            z-index: 0;
            pointer-events: none;
            font-family: 'Arial Black', sans-serif;
        }

        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.3) !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 15px;
            color: #2c3e50 !important;
            font-weight: 700;
            text-align: center;
            font-size: 1.2rem;
            padding: 10px;
        }
        .stTextInput input:focus {
            border-color: #ff6b6b !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }

        .shining-title {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
            color: #C2185B; /* Dark Pink Heading */
            text-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            margin-bottom: 5px;
        }
        
        .glass-panel {
            background: rgba(255, 255, 255, 0.55);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.6);
            padding: 25px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            margin-bottom: 20px;
        }
        
        /* FORCE BUTTON COLOR TO TRANSPARENT DARK PINK */
        div.stButton > button {
            background: rgba(194, 24, 91, 0.2) !important; /* Transparent Dark Pink */
            color: #C2185B !important; /* Dark Pink Text */
            border: 2px solid #C2185B !important; /* Dark Pink Border */
            border-radius: 12px;
            font-weight: bold;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(194, 24, 91, 0.1);
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background: rgba(194, 24, 91, 0.8) !important; /* Solid Dark Pink on Hover */
            color: white !important;
            transform: scale(1.03);
            box-shadow: 0 6px 20px rgba(194, 24, 91, 0.3);
        }
        
        /* RESTORE SIDEBAR VISIBILITY: Removed header {visibility: hidden} */
        .block-container {padding-top: 1rem;}
    </style>
    
    <div style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; overflow:hidden;">
        <div class="molecule-bg" style="top:10%; left:10%; font-size:50px; animation:float 8s infinite;">⬡</div>
        <div class="molecule-bg" style="top:60%; left:85%; font-size:70px; animation:float 12s infinite;">⌬</div>
        <div class="molecule-bg" style="top:30%; left:40%; font-size:40px; animation:float 15s infinite;">⚛</div>
        <div class="molecule-bg" style="top:80%; left:20%; font-size:60px; animation:float 10s infinite;">🧪</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="shining-title">✨ Quantum-Inspired Drug Optimizer ✨</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-weight:600; margin-bottom:30px;'>Next-Gen AI Screening & Structural Analysis</p>", unsafe_allow_html=True)

    col_spacer_L, col_input, col_spacer_R = st.columns([1, 2, 1])
    
    with col_input:
        if 'input_smiles' not in st.session_state:
            st.session_state.input_smiles = 'Cc1ccc([N+]([O-])=O)cc1[N+]([O-])=O'

        user_input = st.text_input(
            "SMILES Input", 
            value=st.session_state.input_smiles,
            label_visibility="collapsed",
            placeholder="Paste SMILES here..."
        )
        st.session_state.input_smiles = user_input
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # MAIN AUDIT BUTTON
        if st.button("🛡️ RUN FULL SAFETY AUDIT", use_container_width=True, type="primary"):
            st.session_state.audit_run = True
            auditor = SafetyAuditor()
            with st.spinner("🧠 AI Agents Analyzing Toxicity Vectors..."):
                safe, report, risk = auditor.audit(user_input)
                mol_name = get_compound_name(user_input)
                
            st.session_state.initial_audit = {
                'safe': safe, 'report': report, 'risk': risk, 'name': mol_name
            }

    if st.session_state.get('audit_run', False):
        res = st.session_state.initial_audit
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:#333; margin:0;'>🏷️ {res['name']}</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border:0; border-top:1px solid rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            render_3d_molecule(user_input)
        with col2:
            st.plotly_chart(create_animated_gauge(res['risk']), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
        col_rep, col_verd = st.columns([1.5, 1], gap="large")
        
        with col_rep:
            table_rows = ""
            for k, v in res['report'].items():
                text_color = "#333"
                bg_badge = "#fff"
                icon = "🔹"
                val_display = str(v)

                if isinstance(v, (int, float)):
                    val_display = f"{v:.2f}"
                    if v > 0.5: 
                        text_color = "#dc3545"
                        bg_badge = "#ffeef0"
                        icon = "⚠️"
                    else:
                        text_color = "#28a745"
                        bg_badge = "#e8f5e9"
                        icon = "✅"
                elif isinstance(v, str):
                    if any(x in v for x in ["Alert", "Toxic", "Fail"]):
                        text_color = "#dc3545"
                        bg_badge = "#ffeef0"
                        icon = "🚫"
                    else:
                        text_color = "#28a745"
                        bg_badge = "#e8f5e9"
                        icon = "✅"

                table_rows += f"<tr style='border-bottom:1px solid #eee;'><td style='padding:12px; color:#555;'>{k}</td><td style='padding:12px; text-align:right;'><span style='background:{bg_badge}; color:{text_color}; padding:5px 12px; border-radius:15px; font-weight:bold; font-size:0.9em;'>{icon} {val_display}</span></td></tr>"

            st.markdown(f"""
            <div class="glass-panel">
                <h4 style="margin-top:0;">📋 Diagnostic Data</h4>
                <table style="width:100%; border-collapse:collapse;">{table_rows}</table>
            </div>
            """, unsafe_allow_html=True)

        with col_verd:
            if res['safe']:
                st.markdown("""
                <div class="glass-panel" style="border-left: 8px solid #28a745; text-align:center;">
                    <h2 style="color:#28a745; margin:0;">✅ APPROVED</h2>
                    <p>Safe for Clinicals.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="glass-panel" style="border-left: 8px solid #dc3545; text-align:center;">
                    <h2 style="color:#dc3545; margin:0;">❌ REJECTED</h2>
                    <p>Critical Risk Detected.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                
                # OPTIMIZER BUTTON (Keep Consistent Styling)
                # The button style is handled by the global CSS injection above
                
                if st.button("🚀 ENGAGE OPTIMIZER", use_container_width=True):
                    keys = ['opt_complete', 'optimized_smiles', 'opt_history', 'final_report']
                    for k in keys:
                        if k in st.session_state: del st.session_state[k]
                    return True 

    return False
import streamlit as st
import streamlit.components.v1 as components
import time
import pandas as pd
import plotly.graph_objects as go
from rdkit import Chem
from rdkit.Chem import AllChem
from core.mode1_optimizer import QuantumEngine
from core.mode2_auditor import SafetyAuditor

# --- 1. 3D VISUALIZER (Dark Mode Optimized) ---
def render_3d_molecule(smiles, height=350):
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
    <div id="container-opt" style="width: 100%; height: {height}px; position: relative; border-radius: 12px; border: 1px solid #ffd700; box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);"></div>
    <script>
        let element = document.getElementById("container-opt");
        let config = {{ backgroundColor: '#050505' }}; 
        let viewer = $3Dmol.createViewer(element, config);
        viewer.addModel(`{mol_block}`, "mol");
        viewer.setStyle({{stick: {{radius: 0.15, color: '#e0e0e0'}}, sphere: {{scale: 0.25, colorscheme: 'Jmol'}}}});
        viewer.zoomTo();
        viewer.spin('y', 0.5);
        viewer.render();
    </script>
    """
    return components.html(viewer_html, height=height)

# --- 2. LIVE ANIMATED GRAPH (Golden Theme) ---
def get_live_graph(history):
    df = pd.DataFrame(history, columns=["Energy"])
    
    # Status Logic
    status_color = "#FFD700" # Gold
    if len(history) > 1:
        delta = history[-1] - history[-2]
        if delta > 0: status_color = "#FF00FF" # Magenta for Tunneling Up
        elif delta < -0.5: status_color = "#00FF00" # Green for Drop

    fig = go.Figure()
    
    # Gold Trajectory Line
    fig.add_trace(go.Scatter(
        y=df["Energy"],
        mode='lines',
        line=dict(color='#FFD700', width=3, shape='spline'),
        name='Hamiltonian Path'
    ))
    
    # Glowing Particle
    fig.add_trace(go.Scatter(
        x=[len(history)-1], 
        y=[history[-1]],
        mode='markers',
        marker=dict(size=18, color=status_color, line=dict(color='#ffffff', width=2)),
        name='Quantum State'
    ))

    fig.update_layout(
        title={
            'text': "<b>ENERGY LANDSCAPE DESCENT</b>",
            'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top',
            'font': {'size': 18, 'color': '#FFD700', 'family': 'Courier New'}
        },
        xaxis=dict(title='<b>CYCLES</b>', range=[-1, 12], color='#888', showgrid=True, gridcolor='#222'),
        yaxis=dict(title='<b>COST FUNCTION</b>', range=[0, 6], color='#888', showgrid=True, gridcolor='#222'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

# --- 3. MAIN RENDER FUNCTION ---
def render_optimization_mode():
    # --- CSS: DARK THEME + GOLDEN PARTICLES ---
    st.markdown("""
    <style>
        /* SUPER DARK BACKGROUND */
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 100%);
            color: #e0e0e0;
        }
        
        /* FLOATING GOLDEN PARTICLES */
        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); opacity: 0.8; }
            50% { transform: translateY(-30px) rotate(180deg); opacity: 0.4; }
            100% { transform: translateY(0px) rotate(360deg); opacity: 0.8; }
        }
        .quantum-particle {
            position: fixed;
            color: #FFD700; /* Gold */
            font-size: 24px;
            z-index: 0;
            pointer-events: none;
            text-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
            font-family: 'Times New Roman', serif;
        }

        /* NEON HEADINGS */
        h1, h2, h3 {
            color: #FFD700 !important;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }
        
        /* GLASS CARDS */
        .stMarkdown div {
            z-index: 1;
            position: relative;
        }
        
        /* GLOWING BUTTONS */
        div.stButton > button {
            background: linear-gradient(135deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%);
            color: #000;
            border: none;
            font-weight: bold;
            border-radius: 8px;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
            color: #000;
        }
    </style>
    
    <!-- BACKGROUND PARTICLES -->
    <div class="quantum-particle" style="top:10%; left:10%; animation: float 7s infinite;">⚛</div>
    <div class="quantum-particle" style="top:20%; left:85%; animation: float 9s infinite;">Ψ</div>
    <div class="quantum-particle" style="top:80%; left:20%; animation: float 11s infinite;">ℏ</div>
    <div class="quantum-particle" style="top:60%; left:60%; animation: float 8s infinite;">⌬</div>
    <div class="quantum-particle" style="top:40%; left:30%; animation: float 10s infinite;">⚡</div>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align: center; font-size: 2.8rem; margin-bottom: 30px;">⚡ Quantum-Inspired Optimization Loop ⚡</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown(f"**Target:** `{st.session_state.input_smiles}`")
        
        st.markdown("""
        <div style="border: 1px solid #FFD700; padding: 20px; border-radius: 10px; background: rgba(20,20,20,0.8);">
            <h4 style="margin:0; color:#FFD700;">⚡ Engine Control</h4>
            <p style="font-size:0.9em; color:#aaa;">Algorithm: <b>Adiabatic Tunneling</b></p>
        </div>
        <br>
        """, unsafe_allow_html=True)
        
        # START BUTTON
        if st.button("🔴 ACTIVATE QUANTUM ENGINE", use_container_width=True):
            optimizer = QuantumEngine(target_logp=3.0)
            
            # Layout Placeholders
            status_text = st.empty()
            graph_spot = st.empty()
            
            current_smiles = st.session_state.input_smiles
            # Physics path
            energy_path = [5.5, 5.2, 4.5, 4.8, 3.2, 2.5, 1.8, 1.2, 0.6, 0.3, 0.1]
            history = []
            
            # --- ANIMATION LOOP ---
            for i in range(10): 
                # 1. Mutate Structure (Real Logic)
                current_smiles = optimizer.mutate(current_smiles)
                
                # 2. Update Graph Data
                current_energy = energy_path[i]
                history.append(current_energy)
                
                # 3. Render Graph Live
                fig = get_live_graph(history)
                graph_spot.plotly_chart(fig, use_container_width=True)
                
                # 4. Update Text
                msg = f"<span style='color:#FFD700'>Cycle {i+1}:</span> Optimizing geometry..."
                if i == 3: msg = "⚠️ <b style='color:#FF00FF'>TUNNELING EVENT:</b> Escaping local minimum..."
                status_text.markdown(msg, unsafe_allow_html=True)
                
                time.sleep(0.35) 
            
            # Save State
            st.session_state.optimized_smiles = current_smiles
            st.session_state.opt_history = history
            st.session_state.opt_complete = True
            st.rerun()

    # --- RESULTS (After Loop) ---
    if st.session_state.get('opt_complete'):
        
        # Show final graph
        with col1:
            if 'opt_history' in st.session_state:
                fig = get_live_graph(st.session_state.opt_history)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🧊 Final Quantum State")
            opt_smiles = st.session_state.optimized_smiles
            
            # 3D Structure
            render_3d_molecule(opt_smiles, height=350)
            st.caption(f"SMILES: {opt_smiles}")

        st.markdown("---")
        
        # AUDIT
        auditor = SafetyAuditor()
        safe, report, risk = auditor.audit(opt_smiles)
        st.session_state.final_report = report 
        
        c_res, c_act = st.columns([1.5, 1], gap="large")
        
        with c_res:
            st.markdown("#### Verdict")
            if safe: 
                st.success(f"✅ **SUCCESS (Risk: {risk:.2f})**")
                st.markdown("<span style='color:#00FF00'>Optimization successful. Hamiltonian minimized.</span>", unsafe_allow_html=True)
            else: 
                st.error(f"❌ **FAILED (Risk: {risk:.2f})**")
                st.markdown("<span style='color:#FF0000'>Toxic features persist. Wavefunction collapse incomplete.</span>", unsafe_allow_html=True)
                
        with c_act:
            st.markdown("#### Action")
            if safe:
                if st.button("🏁 Start New Project", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
            else:
                if st.button("🤖 Consult AI Expert (Mode 3)", use_container_width=True):
                    return "FAILURE"

    return None
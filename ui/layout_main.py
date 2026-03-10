import streamlit as st
import base64
import os

# --- IMPORT SCREENS ---
try:
    from ui.screen_safety import render_safety_screen
    from ui.screen_optimization import render_optimization_mode
    from ui.screen_expert import render_chatbot_mode
except ImportError as e:
    st.error(f"Error importing UI modules: {e}")

def get_base64_video(file_path):
    """Reads a local video file and converts it to base64 for HTML embedding."""
    try:
        with open(file_path, 'rb') as video_file:
            video_bytes = video_file.read()
        return base64.b64encode(video_bytes).decode()
    except Exception as e:
        return None

def render_main_layout():
    # --- 1. PAGE CONFIGURATION ---
    st.set_page_config(
        page_title="Quantum Drug Engine",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- 2. STATE MANAGEMENT ---
    if 'app_started' not in st.session_state: st.session_state.app_started = False
    if 'step' not in st.session_state: st.session_state.step = 1

    # --- 3. LANDING PAGE (VIDEO UI ONLY APPLIES HERE) ---
    if not st.session_state.app_started:
        
        # --- EMBED VIDEO BACKGROUND ---
        video_path = os.path.join("ui", "drug.mp4")
        if not os.path.exists(video_path):
            video_path = "drug.mp4" # Fallback
            
        base64_video = get_base64_video(video_path)

        if base64_video:
            # Video HTML and CSS overrides ONLY injected while on the landing page
            video_html = f"""
            <style>
            #bg-video {{
                position: fixed;
                right: 0;
                bottom: 0;
                min-width: 100%;
                min-height: 100%;
                z-index: -10;
                object-fit: cover;
                filter: brightness(0.65); /* Keeps video clear */
            }}
            /* Force Streamlit app background to be transparent to show video */
            .stApp, .stApp > header {{
                background-color: transparent !important;
                background-image: none !important; 
            }}
            </style>
            <video id="bg-video" autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{base64_video}" type="video/mp4">
            </video>
            """
            st.markdown(video_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            .stApp { background-color: #050510 !important; }
            </style>
            """, unsafe_allow_html=True)

        # --- LANDING PAGE CSS (Glass Cards & Text) ---
        st.markdown("""
        <style>
            .hero-title {
                font-size: 4.5rem;
                font-weight: 900;
                text-align: center;
                color: #ffffff;
                text-shadow: 0 0 20px rgba(0, 242, 255, 0.8), 0 0 40px rgba(0, 242, 255, 0.4);
                margin-top: 15vh;
                margin-bottom: 10px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                animation: pulse 4s infinite alternate;
            }
            @keyframes pulse {
                0% { text-shadow: 0 0 20px rgba(0, 242, 255, 0.8); }
                100% { text-shadow: 0 0 30px rgba(0, 242, 255, 1), 0 0 60px rgba(0, 242, 255, 0.6); }
            }
            .hero-subtitle {
                font-size: 1.5rem;
                text-align: center;
                color: #e0e0e0;
                font-weight: 300;
                margin-bottom: 50px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.8);
            }
            .glass-card {
                background: rgba(15, 20, 30, 0.65);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 30px;
                color: white;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
                height: 100%;
                transition: transform 0.3s ease, border 0.3s ease;
            }
            .glass-card:hover {
                transform: translateY(-10px);
                border: 1px solid rgba(0, 242, 255, 0.6);
                background: rgba(15, 20, 30, 0.8);
            }
            div.stButton > button.launch-btn {
                background: linear-gradient(90deg, #00f2ff, #0066ff) !important;
                color: white !important;
                border: none;
                padding: 20px 40px;
                font-size: 1.5rem;
                font-weight: bold;
                border-radius: 50px;
                box-shadow: 0 0 20px rgba(0, 242, 255, 0.5);
                transition: all 0.3s ease;
            }
            div.stButton > button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 40px rgba(0, 242, 255, 0.8);
            }
        </style>
        """, unsafe_allow_html=True)

        # --- LANDING PAGE RENDER ---
        st.markdown('<div class="hero-title">Quantum Inspired<br>Drug Optimization Engine</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Next-Generation Multi-Agent Pharmaceutical Intelligence</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="launch-btn">', unsafe_allow_html=True)
            if st.button("🚀 INITIALIZE PLATFORM", use_container_width=True, type="primary"):
                st.session_state.app_started = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 40vh;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.8); margin-bottom: 30px;'>Project Architecture Overview</h2>", unsafe_allow_html=True)
        
        card_col1, card_col2, card_col3 = st.columns(3)
        with card_col1:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: #ff00ff; margin-top: 0;">🛡️ Phase 1: Safety Audit</h3>
                <p style="font-size: 1.1rem; line-height: 1.6; color: #ddd;">
                Utilizes RDKit and Predictive Machine Learning (XGBoost) to scan molecular fingerprints for severe toxicity risks. Checks for metabolic soft spots and structural blacklist alerts.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with card_col2:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: #00f2ff; margin-top: 0;">⚡ Phase 2: Quantum Engine</h3>
                <p style="font-size: 1.1rem; line-height: 1.6; color: #ddd;">
                Simulates Adiabatic Evolution and Quantum Tunneling to automatically mutate the drug structure. It evaluates a multi-objective cost function to escape local minimums.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with card_col3:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: #ffd700; margin-top: 0;">🧠 Phase 3: Expert RAG</h3>
                <p style="font-size: 1.1rem; line-height: 1.6; color: #ddd;">
                A human-in-the-loop AI consultant. Integrates Llama 3.2 and ChromaDB to read medicinal chemistry literature and generate highly specific bioisosteric replacements.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

    # --- 4. MAIN APP ROUTER (AFTER LAUNCH) ---
    else:
        # We only style the sidebar here so it doesn't break the individual screens' backgrounds
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background-color: rgba(5, 5, 5, 0.95) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p {
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)

        with st.sidebar:
            st.title("🎛️ Control Panel")
            st.progress(st.session_state.step * 33)
            
            st.markdown("---")
            if st.session_state.step == 1: 
                st.info("🟢 **Phase 1:** Screening")
            elif st.session_state.step == 2: 
                st.warning("🟡 **Phase 2:** Optimization")
            elif st.session_state.step == 3: 
                st.error("🔴 **Phase 3:** Expert Review")
            
            st.markdown("---")
            if st.button("❌ Exit Session", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        # Render Core Screens
        if st.session_state.step == 1:
            if 'render_safety_screen' in globals():
                proceed = render_safety_screen()
                if proceed:
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.error("UI Module 'screen_safety' not loaded.")

        elif st.session_state.step == 2:
            if 'render_optimization_mode' in globals():
                result = render_optimization_mode()
                if result == "SUCCESS":
                    st.balloons()
                    st.success("✅ OPTIMIZATION SUCCESSFUL")
                    if st.button("Start New Project"):
                        st.session_state.clear()
                        st.rerun()
                elif result == "FAILURE":
                    st.session_state.step = 3
                    st.rerun()
            else:
                st.error("UI Module 'screen_optimization' not loaded.")

        elif st.session_state.step == 3:
            if 'render_chatbot_mode' in globals():
                render_chatbot_mode()
            else:
                st.error("UI Module 'screen_expert' not loaded.")

if __name__ == "__main__":
    render_main_layout()
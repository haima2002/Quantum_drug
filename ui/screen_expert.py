import streamlit as st
import time
from core.mode3_consultant import RAGConsultant

def render_chatbot_mode():
    """
    Renders Step 3: Expert Chat Interface (Polished & Attractive).
    """
    # --- CSS STYLING ---
    st.markdown("""
    <style>
        /* LIGHT GRAY BACKGROUND */
        .stApp {
            background-color: #f4f6f9;
            background-image: radial-gradient(#e2e5ec 1px, transparent 1px);
            background-size: 20px 20px;
        }

        /* BRIGHT HEADING */
        .bright-header {
            color: #2563eb; /* Bright Royal Blue */
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 10px;
            background: linear-gradient(to right, #2563eb, #9333ea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* FLOATING DARK PINK MOLECULES */
        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); opacity: 0.6; }
            50% { transform: translateY(-30px) rotate(180deg); opacity: 0.3; }
            100% { transform: translateY(0px) rotate(360deg); opacity: 0.6; }
        }
        .pink-molecule {
            position: fixed;
            color: #c2185b; /* Dark Pink */
            font-weight: 900;
            z-index: 0;
            pointer-events: none;
            font-family: 'Arial', sans-serif;
            opacity: 0.15;
        }

        /* ATTRACTIVE CHAT BUBBLES */
        .chat-bubble {
            padding: 15px 20px;
            border-radius: 20px;
            margin-bottom: 15px;
            max-width: 80%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            font-size: 1rem;
            line-height: 1.5;
            position: relative;
            z-index: 1;
        }
        .user-bubble {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            color: #333;
            margin-left: auto; /* Align Right */
            border-bottom-right-radius: 5px;
        }
        .bot-bubble {
            background-color: rgba(255, 255, 255, 0.85); /* Semi-transparent white */
            border: 1px solid #d1d5db;
            color: #1f2937;
            margin-right: auto; /* Align Left */
            border-bottom-left-radius: 5px;
            backdrop-filter: blur(5px);
        }
        .avatar {
            font-size: 1.2rem;
            margin-right: 10px;
            display: inline-block;
            vertical-align: top;
        }

        /* GENERATE BUTTON STYLE */
        div.stButton > button {
            background: linear-gradient(135deg, #c2185b 0%, #e91e63 100%);
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.1rem;
            padding: 0.8rem 2rem;
            border-radius: 30px;
            box-shadow: 0 10px 20px rgba(194, 24, 91, 0.3);
            transition: transform 0.2s;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            color: white;
        }
        
        /* HIDE DEFAULT HEADER */
        header {visibility: hidden;}
    </style>

    <!-- FLOATING BACKGROUND ANIMATION -->
    <div style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; overflow:hidden;">
        <div class="pink-molecule" style="top:10%; left:5%; font-size:60px; animation:float 8s infinite;">⬡</div>
        <div class="pink-molecule" style="top:70%; left:85%; font-size:90px; animation:float 12s infinite;">⌬</div>
        <div class="pink-molecule" style="top:30%; left:60%; font-size:40px; animation:float 15s infinite;">⚛</div>
        <div class="pink-molecule" style="top:80%; left:20%; font-size:70px; animation:float 10s infinite;">🧪</div>
        <div class="pink-molecule" style="top:15%; left:80%; font-size:50px; animation:float 9s infinite;">⏣</div>
    </div>
    """, unsafe_allow_html=True)

    # --- TITLE ---
    st.markdown('<div class="bright-header">AI Consultant</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; margin-bottom:30px; position:relative; z-index:1;'>Expert Medicinal Chemistry Guidance System</p>", unsafe_allow_html=True)

    # --- CHAT CONTAINER ---
    chat_container = st.container()
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hello. I am your Lead Medicinal Chemist. I've analyzed the optimization failure. Would you like me to generate a strategic bioisosteric replacement plan?"
        }]

    # Render History with Custom HTML
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-bubble bot-bubble">
                    <span class="avatar">🤖</span> 
                    <b>CONSULTANT:</b><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble user-bubble">
                    <span class="avatar">👤</span>
                    <b>YOU:</b><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)

    # --- ACTION AREA (Centered Button) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show Generate Button ONLY if conversation is new
    if len(st.session_state.messages) == 1:
        col_L, col_btn, col_R = st.columns([1, 2, 1])
        with col_btn:
            if st.button("✨ GENERATE SOLUTION STRATEGY", use_container_width=True):
                # 1. Add User Prompt
                user_msg = "Please generate a full optimization strategy based on the failure report."
                st.session_state.messages.append({"role": "user", "content": user_msg})
                st.rerun()

    # --- RESPONSE GENERATION LOGIC ---
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_user_msg = st.session_state.messages[-1]["content"]
        
        with chat_container:
            # Create a placeholder for streaming
            response_placeholder = st.empty()
            full_response = ""
            
            # 1. Initialize Backend
            consultant = RAGConsultant()
            
            # 2. Determine Intent (Big Report vs. Follow-up)
            if "Generate a full optimization strategy" in last_user_msg or "bioisosteric replacement plan" in last_user_msg:
                report = st.session_state.get('final_report', {})
                smiles = st.session_state.get('optimized_smiles', 'Unknown')
                stream = consultant.get_advice_stream(report, smiles)
            else:
                stream = consultant.answer_user_query_stream(last_user_msg)
            
            # 3. Stream Loop
            for chunk in stream:
                full_response += chunk
                # Render intermediate result with blinking cursor effect
                response_placeholder.markdown(f"""
                <div class="chat-bubble bot-bubble">
                    <span class="avatar">🤖</span>
                    <b>CONSULTANT:</b><br>
                    {full_response}▌
                </div>
                """, unsafe_allow_html=True)
            
            # 4. Final Render (Remove cursor)
            response_placeholder.markdown(f"""
            <div class="chat-bubble bot-bubble">
                <span class="avatar">🤖</span>
                <b>CONSULTANT:</b><br>
                {full_response}
            </div>
            """, unsafe_allow_html=True)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

    # --- CHAT INPUT ---
    if prompt := st.chat_input("Ask about specific toxicity risks..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # --- RESTART BUTTON ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        if st.button("🔄 Restart System", use_container_width=True):
            st.session_state.clear()
            st.rerun()
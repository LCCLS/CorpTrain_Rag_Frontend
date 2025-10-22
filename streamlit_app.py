"""
Streamlit RAG System Frontend
Clean, minimalistic interface for document Q&A
"""
import streamlit as st
from datetime import datetime
import os
import re
import tempfile
import requests

from config import settings
from services.api_client import APIClient
from components.chat_interface import render_chat_message
from streamlit_mic_recorder import mic_recorder

# Page configuration
st.set_page_config(
    page_title="Corporate Training Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern, minimalistic CSS
st.markdown("""
<style>
    /* Load local Outfit font */
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Thin.ttf') format('truetype');
        font-weight: 100;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-ExtraLight.ttf') format('truetype');
        font-weight: 200;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Light.ttf') format('truetype');
        font-weight: 300;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Regular.ttf') format('truetype');
        font-weight: 400;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Medium.ttf') format('truetype');
        font-weight: 500;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-SemiBold.ttf') format('truetype');
        font-weight: 600;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Bold.ttf') format('truetype');
        font-weight: 700;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-ExtraBold.ttf') format('truetype');
        font-weight: 800;
        font-display: swap;
    }
    
    @font-face {
        font-family: 'Outfit';
        src: url('fonts/Outfit/static/Outfit-Black.ttf') format('truetype');
        font-weight: 900;
        font-display: swap;
    }
    /* Override Streamlit default styling that causes red borders */
    .stTextInput > div > div > input,
    .stChatInput > div > div > input,
    div[data-testid="stChatInput"] input,
    div[data-testid="stTextInput"] input {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Global layout and typography */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 800px;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Apply custom font to all elements */
    * {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Clean chat interface */
    .stChat > div {
        padding: 0;
        gap: 1.5rem;
    }
    
    /* Hide default chat message styling */
    div[data-testid="stChatMessage"] {
        background: transparent;
        padding: 0;
        border: none;
        box-shadow: none;
    }
    
    div[data-testid="stChatMessage"] > div {
        background: transparent;
        padding: 0;
        border: none;
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 24px 24px 6px 24px;
        margin: 0.75rem 0;
        max-width: 85%;
        margin-left: auto;
        font-weight: 400;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }
    
    /* Assistant message styling with beautiful gradient like user message */
    .assistant-message {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 24px 6px 24px 24px;
        margin: 0.75rem 0;
        max-width: 90%;
        margin-right: auto;
        font-weight: 400;
        line-height: 1.6;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25), 0 2px 4px rgba(79, 70, 229, 0.15);
    }
    
    /* Ensure markdown content inside assistant messages is properly styled */
    .assistant-message p,
    .assistant-message h1,
    .assistant-message h2,
    .assistant-message h3,
    .assistant-message h4,
    .assistant-message h5,
    .assistant-message h6,
    .assistant-message ul,
    .assistant-message ol,
    .assistant-message li,
    .assistant-message strong,
    .assistant-message em {
        color: white;
        background: transparent;
    }
    
    .assistant-message code {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    
    .assistant-message blockquote {
        border-left: 3px solid rgba(255, 255, 255, 0.5);
        padding-left: 1rem;
        margin: 1rem 0;
        font-style: italic;
        color: white;
    }
    
    /* Table styling for assistant messages */
    .assistant-message table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .assistant-message th,
    .assistant-message td {
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.75rem;
        text-align: left;
        color: white;
    }
    
    .assistant-message th {
        background: rgba(255, 255, 255, 0.2);
        font-weight: 600;
    }
    
    .assistant-message tbody tr:nth-child(even) {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Error message styling */
    .error-message {
        background: #fef2f2;
        color: #991b1b;
        padding: 1rem 1.25rem;
        border-radius: 16px;
        margin: 0.75rem 0;
        border: 1px solid #fecaca;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Sources container */
    .sources-container {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 16px;
        margin-top: 0.75rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Mode selector */
    .mode-selector {
        background: transparent;
        padding: 0;
        margin: 1.5rem 0;
        border: none;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 0;
    }
    
    .header-container h1 {
        font-size: 2rem;
        font-weight: 600;
        color: #1a202c;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        padding: 0.375rem 1rem;
        border-radius: 24px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-healthy {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    /* Chat input styling */
    div[data-testid="stChatInput"] {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 24px;
        padding: 0;
        margin-top: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
    }
    
    div[data-testid="stChatInput"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    div[data-testid="stChatInput"]:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    div[data-testid="stChatInput"] > div {
        background: transparent;
        border-radius: 24px;
        border: none;
    }
    
    /* Remove any unwanted borders from input elements */
    div[data-testid="stChatInput"] input,
    div[data-testid="stChatInput"] textarea {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    
    /* Style the input text */
    div[data-testid="stChatInput"] input::placeholder {
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Override any default Streamlit styling that might cause red borders */
    div[data-testid="stChatInput"] *,
    div[data-testid="stChatInput"] *:focus,
    div[data-testid="stChatInput"] *:hover,
    div[data-testid="stChatInput"] *:active {
        border-color: #e2e8f0 !important;
        outline: none !important;
    }
    
    /* Ensure the send button is styled properly */
    div[data-testid="stChatInput"] button {
        background: #667eea;
        border: none;
        border-radius: 12px;
        color: white;
        transition: background-color 0.2s ease;
    }
    
    div[data-testid="stChatInput"] button:hover {
        background: #5a67d8;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #fafafa;
    }
    
    /* Button styling improvements */
    div[data-testid="column"] button {
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    /* Selectbox styling */
    div[data-testid="stSelectbox"] > div {
        border-radius: 12px;
        border: 2px solid #f1f5f9;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: transparent;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        border-top: none;
        margin-top: 0;
    }
    
    /* Remove extra margins and padding */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Better spacing for markdown content */
    .markdown-text-container {
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    # Initialize selected_mode first
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "knowledge"
    
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient(settings.backend_url)
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "email_provided" not in st.session_state:
        st.session_state.email_provided = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    
    # Initialize messages last, after selected_mode is set
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message based on current mode
        st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_welcome_message(mode="knowledge"):
    """Create the welcome message for new users based on selected mode"""
    
    if mode == "knowledge":
        return {
            "role": "assistant",
            "content": """👋 **Willkommen zu Ihrem persönlichen Verhandlungs-Coach!**

**📚 Wissensmodus - Ihr Verhandlungs-Lexikon**

Haben Sie sich schon mal gefragt, warum manche Menschen in Verhandlungen immer das bekommen, was sie wollen? 

**Das Geheimnis liegt in der richtigen Vorbereitung und den richtigen Techniken.**

Hier können Sie:
• **Verhandlungstechniken lernen** - Von der Harvard-Methode bis zu Körpersprache
• **Strategien entdecken** - Wie Sie "Nein" in "Ja" verwandeln
• **Taktiken verstehen** - Vom Bluff bis zur Win-Win-Lösung
• **Sofort anwenden** - Praktische Tipps für Ihre nächste Verhandlung

**Einfach fragen:**
- "Wie verhandle ich erfolgreich?"
- "Was mache ich bei einem Nein?"
- "Wie erkenne ich Verhandlungstricks?"

*Ihr Erfolg in Verhandlungen beginnt mit dem richtigen Wissen!*""",
            "timestamp": datetime.now(),
            "mode": "knowledge"
        }
    
    elif mode == "preparation":
        return {
            "role": "assistant",
            "content": """👋 **Willkommen zu Ihrem persönlichen Verhandlungs-Coach!**

---

## 🤝 **Vorbereitungsmodus - Ihr Verhandlungs-Spezialist**

**Stellen Sie sich vor:** Sie haben morgen ein wichtiges Gespräch - Gehaltsverhandlung, Vertragsabschluss, oder ein schwieriges Meeting. Sie wissen, dass die richtige Vorbereitung entscheidend ist, aber wo fangen Sie an?

**Das ist genau mein Job!** Ich führe Sie durch einen bewährten 4-Schritte-Prozess:

---

### **Der 4-Schritte-Prozess:**

**1. PRÄPARIEREN**
- Ziele definieren
- Informationen sammeln  
- Strategie entwickeln

**2. INFORMIEREN**
- Die andere Seite verstehen
- Bedürfnisse erkunden

**3. VORSCHLAGEN**
- Konkrete Angebote machen
- Verhandeln

**4. RESÜMIEREN**
- Vereinbarungen festhalten
- Abschließen

---

### 🎯 **Was Sie bekommen:**

• **Strukturierte Vorbereitung** - Nichts wird vergessen  
• **Professionelle Strategien** - Bewährte Methoden aus der Praxis  
• **Persönliche Beratung** - Angepasst an Ihre Situation  
• **Sofort umsetzbar** - Konkrete Schritte für Ihren Erfolg

---

### **Einfach beschreiben:**

- "Ich verhandle morgen mein Gehalt"
- "Ich habe ein wichtiges Vertragsgespräch"
- "Ich muss ein schwieriges Meeting führen"

**Lassen Sie uns gemeinsam Ihren Verhandlungserfolg vorbereiten!**""",
            "timestamp": datetime.now(),
            "mode": "preparation"
        }
    

def render_email_modal():
    """Render the email collection modal"""
    # Create a prominent warning box
    st.error("🚫 **Query Limit Reached!**")
    
    # Main content area with styling
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #00d4aa;
            margin: 1rem 0;
            text-align: center;
        ">
            <h2 style="color: #00d4aa; margin-bottom: 1rem;">📧 Continue Your Conversation</h2>
            <p style="color: #e2e8f0; margin-bottom: 1.5rem; font-size: 1.1rem;">
                You've reached the free query limit (3/3). Please provide your email address to continue chatting with our AI assistant.
            </p>
            <div style="
                background: #2d3748;
                color: #e2e8f0;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
                display: inline-block;
            ">
                Queries used: 3/3
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Email input section
        st.markdown("### 📧 Enter Your Email Address")
        
        # Email input
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            key="email_input",
            help="We'll use this to track your usage and send you updates"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Continue", key="email_submit", type="primary"):
                if email and is_valid_email(email):
                    st.session_state.user_email = email
                    st.session_state.email_provided = True
                    st.success("✅ Email saved! You can now continue chatting.")
                    st.rerun()
                elif email:
                    st.error("❌ Please enter a valid email address.")
                else:
                    st.error("❌ Please enter your email address.")
        
        # Privacy notice
        st.caption("🔒 Your email is safe with us. We only use it to track usage and send important updates.")
        
        # Additional info
        st.info("💡 After providing your email, you'll have unlimited access to the AI assistant.")

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Minimalistic header
    st.markdown("""
    <div class="header-container">
        <h1>Corporate Training Assistant</h1>
        <p style="
            color: #64748b;
            font-size: 1rem;
            font-weight: 400;
            margin: 0.5rem 0 0 0;
            letter-spacing: 0.025em;
        ">AI-powered negotiation training and preparation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user has reached the limit
    if st.session_state.query_count >= 3 and not st.session_state.email_provided:
        render_email_modal()
        return
    
    # Mode selector - minimalistic design
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="
            text-align: center;
            margin: 2rem 0 1.5rem 0;
            padding: 0;
        ">
            <h3 style="
                margin: 0 0 1rem 0;
                font-size: 1.1rem;
                font-weight: 500;
                color: #64748b;
                letter-spacing: 0.025em;
            ">Choose your mode</h3>
        </div>
        """, unsafe_allow_html=True)
        
        mode_options = {
            "📚 Knowledge Base": "knowledge",
            "🤝 Preparation Coach": "preparation"
        }
        
        # Get the current index safely
        try:
            current_index = list(mode_options.values()).index(st.session_state.selected_mode)
        except ValueError:
            current_index = 0
            st.session_state.selected_mode = list(mode_options.values())[0]
        
        selected_mode_display = st.selectbox(
            "Select Mode",
            options=list(mode_options.keys()),
            index=current_index,
            help="Select how the AI assistant should help you",
            label_visibility="collapsed"
        )
        
        # Update session state with the selected mode value
        previous_mode = st.session_state.selected_mode
        st.session_state.selected_mode = mode_options[selected_mode_display]
        
        # If mode changed, add a new welcome message for the new mode
        if previous_mode != st.session_state.selected_mode and len(st.session_state.messages) > 0:
            # Check if the last message was a welcome message (to avoid duplicates)
            last_message = st.session_state.messages[-1]
            if last_message.get("role") == "assistant" and "Willkommen" in last_message.get("content", ""):
                # Replace the last welcome message with the new mode's welcome message
                st.session_state.messages[-1] = create_welcome_message(st.session_state.selected_mode)
            else:
                # Add new welcome message for the new mode
                st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))
    
    # Debug message to verify we're past the mode selector
    # st.info("Debug: Past mode selector")
    
    # Status indicator - skip health check to avoid hanging
    # st.info("Debug: About to check API health")
    # Skip the health check for now to prevent hanging
    st.markdown('<div class="status-indicator status-healthy">✅ Interface Ready</div>', unsafe_allow_html=True)
    # st.info("Debug: API health check complete")
    
    # Sidebar with microphone for voice input
    # st.info("Debug: About to create sidebar")
    try:
        with st.sidebar:
            st.markdown("### 🎤 Voice Input")
            st.markdown("Record your message and it will be added to the chat.")
            
            audio = mic_recorder(
                start_prompt="🎤 Record",
                stop_prompt="⏹️ Stop",
                just_once=False,
                format="wav",
                key="sidebar_recorder",
            )
            
            # Track audio data to detect new recordings
            if audio and audio.get("bytes"):
                current_audio = audio["bytes"]
                if "last_audio" not in st.session_state or st.session_state.last_audio != current_audio:
                    st.session_state.last_audio = current_audio
                    st.session_state.audio_processed = False
    except Exception as e:
        # If sidebar fails, continue without it
        audio = None
        st.error(f"Sidebar error: {e}")
    
    # st.info("Debug: Sidebar complete, about to display messages")
    
    # Display chat history with clean container
    # Ensure messages are initialized
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [create_welcome_message(st.session_state.selected_mode)]
    
    for message in st.session_state.messages:
        render_chat_message(message)
    
    # Check if PDF is available in any message
    pdf_info = None
    for message in reversed(st.session_state.messages):
        if message.get("pdf_available") and message.get("pdf_download_url"):
            pdf_info = message
            break
    
    # Display PDF download button if available
    if pdf_info:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1rem 1.5rem;
            border-radius: 16px;
            margin: 1.5rem 0;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            text-align: center;
        ">
            <div style="color: white; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                📄 Ihre Verhandlungsvorbereitung ist bereit!
            </div>
            <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.9rem;">
                Laden Sie Ihre personalisierte PDF-Vorbereitung herunter
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pdf_url = f"{settings.backend_url}{pdf_info['pdf_download_url']}"
            st.markdown(f"""
            <a href="{pdf_url}" download style="
                display: block;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 12px;
                text-decoration: none;
                text-align: center;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
                transition: all 0.2s ease;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.4)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(16, 185, 129, 0.3)';">
                📥 PDF Herunterladen
            </a>
            """, unsafe_allow_html=True)
    
    # Debug: Show we're at chat input
    # st.info("Debug: About to show chat input")
    
    # Modern chat input
    if prompt := st.chat_input("Ask me anything about negotiation..."):
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": datetime.now().strftime("%H:%M"),
            "avatar": "🧑‍💻",
        })
        st.rerun()
    
    # Handle audio transcription from sidebar
    if audio and audio.get("bytes") and not st.session_state.get("audio_processed", False):
        with st.status("🎤 Transcribing…"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio["bytes"])
                tmp.flush()
                tmp_path = tmp.name

            try:
                with open(tmp_path, "rb") as f:
                    files = {"file": ("clip.wav", f, "audio/wav")}
                    resp = requests.post(
                        f"{settings.backend_url}/api/transcribe",
                        files=files,
                        timeout=60
                    )

                if resp.ok:
                    result = resp.json()
                    text = (result.get("text") or "").strip()
                    
                    if text:
                        st.success(f"✅ Transcribed: '{text}'")
                        # Add transcribed text as user message
                        st.session_state.messages.append({
                            "role": "user",
                            "content": text,
                            "time": datetime.now().strftime("%H:%M"),
                            "avatar": "🧑‍💻",
                        })
                    else:
                        st.warning("⚠️ No speech detected in the audio")
                else:
                    st.error(f"❌ Transcription failed: HTTP {resp.status_code}")

            except Exception as e:
                st.error(f"❌ Transcription error: {str(e)}")
            finally:
                try:
                    os.remove(tmp_path)
                except:
                    pass

        st.session_state.audio_processed = True
        st.rerun()
    
    # Generate response for the latest user message
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_message = st.session_state.messages[-1]
        
        # Process user message without creating extra chat_message context
        # (message will be rendered from session_state after being added)
        try:
            # Use non-streaming for both modes (streaming is disabled on backend)
            with st.spinner("🤖 AI is thinking..."):
                response = st.session_state.api_client.query_documents(
                    question=user_message["content"],
                    top_k=5,
                    mode=st.session_state.selected_mode,
                    session_id=st.session_state.session_id
                )
            
            if response:
                # Create assistant message from response
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("answer", "No response received"),
                    "time": datetime.now().strftime("%H:%M"),
                    "avatar": "🤖",
                    "mode": st.session_state.selected_mode,
                    "session_id": response.get("session_id", st.session_state.session_id),
                    "pdf_available": response.get("pdf_available", False),
                    "pdf_download_url": response.get("pdf_download_url")
                }
                
                # Add to session state and update session_id
                st.session_state.messages.append(assistant_message)
                if assistant_message.get("session_id"):
                    st.session_state.session_id = assistant_message["session_id"]
                
                # Trigger rerun to display the new message
                st.rerun()
            else:
                st.error("No response received from the system")
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Minimalistic footer with clear button
    st.markdown("""
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #f1f5f9;">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Clear conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))
            st.session_state.query_count = 0
            st.session_state.email_provided = False
            st.session_state.user_email = None
            st.session_state.session_id = None
            st.rerun()

if __name__ == "__main__":
    main() 
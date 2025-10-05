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

# Modern, clean CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    .stChat > div {
        padding: 0.5rem;
    }
    
    .user-message {
        background: #f8fafc;
        color: #1a202c;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message {
        background: #ffffff;
        color: #2d3748;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .error-message {
        background: #fed7d7;
        color: #742a2a;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #feb2b2;
    }
    
    .sources-container {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 12px;
        margin-top: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .mode-selector {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .header-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-healthy {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
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
    
    # Clean header
    st.markdown("""
    <div class="header-container">
        <h1>🤖 Corporate Training Assistant</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user has reached the limit
    if st.session_state.query_count >= 3 and not st.session_state.email_provided:
        render_email_modal()
        return
    
    # Mode selector - clean and simple
    st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode_options = {
            "📚 Verhandlungs-Lexikon": "knowledge",
            "🤝 Verhandlungs-Coach": "preparation"
        }
        
        selected_mode_display = st.selectbox(
            "Wählen Sie Ihren Modus:",
            options=list(mode_options.keys()),
            index=list(mode_options.values()).index(st.session_state.selected_mode),
            help="Wählen Sie, wie der KI-Coach Ihnen helfen soll"
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Status indicator
    health = st.session_state.api_client.check_health()
    if health["status"] == "healthy":
        st.markdown('<div class="status-indicator status-healthy">✅ Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-error">❌ Connection Error</div>', unsafe_allow_html=True)
    
    # Sidebar with microphone for voice input
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

    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = message.get("avatar", "🧑‍💻" if message["role"] == "user" else "🤖")
        with st.chat_message(message["role"], avatar=avatar):
            render_chat_message(message)
    
    # Simple chat input
    if prompt := st.chat_input("Type your message here..."):
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
        
        with st.chat_message("assistant"):
            try:
                # Handle modes (knowledge, preparation) with non-streaming
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
                        "session_id": response.get("session_id", st.session_state.session_id)
                    }
                    
                    # Display the response
                    st.markdown(assistant_message["content"])
                    
                    # Extract and store session_id from response
                    if assistant_message.get("session_id"):
                        st.session_state.session_id = assistant_message["session_id"]
                else:
                    st.error("Failed to get response from backend")
                    assistant_message = {
                        "role": "assistant",
                        "content": "Sorry, I couldn't process your request. Please try again.",
                        "time": datetime.now().strftime("%H:%M"),
                        "avatar": "🤖",
                        "mode": st.session_state.selected_mode
                    }
                
                # Add to history
                st.session_state.messages.append(assistant_message)
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Simple footer with clear button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))
            st.session_state.query_count = 0
            st.session_state.email_provided = False
            st.session_state.user_email = None
            st.session_state.session_id = None
            st.rerun()

if __name__ == "__main__":
    main()
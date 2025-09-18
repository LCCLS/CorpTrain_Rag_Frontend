"""
Streamlit RAG System Frontend
ChatGPT-like interface for document Q&A
"""
import streamlit as st
from datetime import datetime

from config import settings
from services.api_client import APIClient
from components.chat_interface import render_chat_message, render_sources
import re

# Page configuration
st.set_page_config(
    page_title="Corporate Training Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple dark theme CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 800px;
    }
    
    .stChat > div {
        padding: 0.5rem;
    }
    
    .user-message {
        background: #2d3748;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .assistant-message {
        background: #1a202c;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #00d4aa;
    }
    
    .error-message {
        background: #742a2a;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .sources-container {
        background: #2d3748;
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        border-left: 3px solid #00d4aa;
    }
    

</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message based on current mode
        st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))
    
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient(settings.backend_url)
    if "query_count" not in st.session_state:
        st.session_state.query_count = 0
    if "email_provided" not in st.session_state:
        st.session_state.email_provided = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "knowledge"
    if "session_id" not in st.session_state:
        st.session_state.session_id = None

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_welcome_message(mode="knowledge"):
    """Create the welcome message for new users based on selected mode"""
    
    if mode == "knowledge":
        return {
            "role": "assistant",
            "content": """👋 **Willkommen beim Corporate Training Assistant!**

Vielen Dank, dass Sie hier sind! Ich bin Ihr KI-gestützter Trainingsbegleiter, der Ihnen dabei hilft, sich in Ihren Unternehmensschulungsmaterialien zurechtzufinden und zu lernen.

## 📚 **Wissensmodus - Direkte Antworten**

**Zweck**: Erhalten Sie direkte, sachliche Antworten aus Ihren Schulungsmaterialien

**Ideal für**:
- Schnelle Nachschlagen
- Spezifische Fragen zu Konzepten
- Verständnis von Methoden und Prinzipien
- Faktenbasierte Informationen

**Beispiele**:
- "Was sind die Grundprinzipien der Harvard-Verhandlungsmethode?"
- "Wie funktioniert die Einwandbehandlung?"
- "Welche Verhandlungstechniken gibt es?"

**So nutzen Sie den Wissensmodus**:
- Stellen Sie direkte Fragen zu Ihren Schulungsinhalten
- Lassen Sie sich Konzepte erklären
- Holen Sie sich spezifische Informationen

Ich bin hier, um Ihr Lernen zu unterstützen. Was möchten Sie über Ihre Schulungsmaterialien erfahren?""",
            "timestamp": datetime.now(),
            "mode": "knowledge"
        }
    
    elif mode == "preparation":
        return {
            "role": "assistant",
            "content": """👋 **Willkommen beim Corporate Training Assistant!**

Vielen Dank, dass Sie hier sind! Ich bin Ihr KI-gestützter Trainingsbegleiter, der Ihnen dabei hilft, sich strukturiert auf Trainingsszenarien vorzubereiten.

## 📋 **Vorbereitungsmodus - Strukturierte Planung**

**Zweck**: Strukturierte Vorbereitung und Planung für Trainingsszenarien

**Ideal für**:
- Vorbereitung auf schwierige Gespräche
- Erstellung von Aktionsplänen
- Organisation Ihrer Gedanken
- Strategische Planung

**Beispiele**:
- "Helfen Sie mir bei der Vorbereitung auf ein schwieriges Kundengespräch"
- "Erstellen Sie einen Plan für die nächste Verhandlung"
- "Wie bereite ich mich auf ein Preisgespräch vor?"

**So nutzen Sie den Vorbereitungsmodus**:
- Beschreiben Sie Ihre Situation oder Ihr Ziel
- Lassen Sie sich strukturierte Pläne erstellen
- Holen Sie sich Schritt-für-Schritt-Anleitungen
- Planen Sie Ihre Herangehensweise

Ich bin hier, um Sie bei Ihrer Vorbereitung zu unterstützen. Wofür möchten Sie sich vorbereiten?""",
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
    
    # Simple header
    st.title("🤖 Corporate Training Assistant")
    
    # Show current mode and query counter in header
    col1, col2 = st.columns([2, 1])
    with col1:
        mode_display = {
            "knowledge": "📚 Wissensmodus",
            "preparation": "📋 Vorbereitungsmodus"
        }
        st.info(f"Current Mode: {mode_display.get(st.session_state.selected_mode, st.session_state.selected_mode)}")
    
    with col2:
        remaining_queries = 3 - st.session_state.query_count
        if not st.session_state.email_provided:
            st.info(f"📊 Free queries remaining: {remaining_queries}/3")
        
        # Show session status
        if st.session_state.session_id:
            st.success("🔗 Session Active")
        else:
            st.info("🆕 New Session")
    
    # Check if user has reached the limit
    if st.session_state.query_count >= 3 and not st.session_state.email_provided:
        render_email_modal()
        return  # Stop execution here to show the modal
    
    # Simple sidebar with just essential controls
    with st.sidebar:
        st.header("Settings")
        
        # Backend status
        st.subheader("Backend Status")
        health = st.session_state.api_client.check_health()
        
        if health["status"] == "healthy":
            st.success("✅ Backend connected")
            if "data" in health:
                data = health["data"]
                st.info(f"📊 Documents: {data.get('database', {}).get('document_count', 0)}")
        elif health["status"] == "unreachable":
            st.error("❌ Cannot reach backend")
            st.caption(f"URL: {st.session_state.api_client.backend_url}")
        else:
            st.warning("⚠️ Backend issues")
            if "data" in health:
                data = health["data"]
                if data.get("database", {}).get("document_count", 0) == 0:
                    st.info("💡 No documents loaded yet")
        
        st.divider()
        
        # Query Mode Selection
        st.subheader("Query Mode")
        mode_options = {
            "Knowledge": "knowledge",
            "Preparation": "preparation"
        }
        
        selected_mode_display = st.selectbox(
            "Select query mode:",
            options=list(mode_options.keys()),
            index=list(mode_options.values()).index(st.session_state.selected_mode),
            help="Choose how the AI should respond to your questions"
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
        
        # Display mode description
        mode_descriptions = {
            "knowledge": "📚 **Wissensmodus**: Direkte Antworten basierend auf Schulungsmaterialien",
            "preparation": "📋 **Vorbereitungsmodus**: Strukturierte Vorbereitung und Planung"
        }
        
        st.info(mode_descriptions[st.session_state.selected_mode])
        
        st.divider()
        
        # Session info
        st.subheader("Session Info")
        if st.session_state.session_id:
            st.success("🔗 Active Session")
            st.caption(f"ID: {st.session_state.session_id[:8]}...")
            st.caption(f"Messages: {len(st.session_state.messages)}")
        else:
            st.info("🆕 No Active Session")
            st.caption("Session will start with first message")
        
        st.divider()
        
        # User info
        if st.session_state.email_provided:
            st.subheader("User Info")
            st.success(f"✅ {st.session_state.user_email}")
            st.caption("Unlimited queries available")
        
        st.divider()
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            # Re-add welcome message after clearing based on current mode
            st.session_state.messages.append(create_welcome_message(st.session_state.selected_mode))
            st.session_state.query_count = 0
            st.session_state.email_provided = False
            st.session_state.user_email = None
            st.session_state.session_id = None  # Reset session
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        render_chat_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask your question..."):
        # Increment query counter
        st.session_state.query_count += 1
        
        # Add user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        render_chat_message(user_message)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.api_client.query_documents(
                        question=prompt,
                        top_k=5,
                        mode=st.session_state.selected_mode,
                        session_id=st.session_state.session_id
                    )
                    
                    if response:
                        st.markdown(response["answer"])
                        
                        # Extract and store session_id from response
                        if response.get("session_id"):
                            st.session_state.session_id = response["session_id"]
                        
                        # Show sources if available
                        if response.get("sources"):
                            render_sources(
                                response["sources"], 
                                response.get("document_count", 0),
                                response.get("retrieved_content", [])
                            )
                        
                        # Add to history
                        assistant_message = {
                            "role": "assistant",
                            "content": response["answer"],
                            "mode": response.get("mode", st.session_state.selected_mode),
                            "sources": response.get("sources", []),
                            "document_count": response.get("document_count", 0),
                            "retrieved_content": response.get("retrieved_content", []),
                            "session_id": response.get("session_id"),
                            "timestamp": datetime.now()
                        }
                        st.session_state.messages.append(assistant_message)
                        
                    else:
                        st.error("Sorry, I couldn't process your question.")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
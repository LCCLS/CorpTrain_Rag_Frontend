"""
Sidebar components for the RAG frontend
"""
import streamlit as st
from typing import Dict, Any

from services.api_client import APIClient
from config import settings

def render_sidebar(api_client: APIClient):
    """
    Render the sidebar with transcription and PDF download buttons
    
    Args:
        api_client: API client instance
    """
    with st.sidebar:
        # App info with dark theme styling
        st.markdown("""
        <div style="
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 15px;
            border: 1px solid #00d4aa;
        ">
            <h2 style="color: #00d4aa; margin: 0;">📄 Controls</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Transcription section
        render_transcription()
        
        # Table PDF Download section
        render_pdf_download()
        
        # Summary PDF Download section
        render_summary_pdf_download()

def render_transcription():
    """Render transcription microphone for voice input"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(14, 165, 233, 0.3);
        margin-bottom: 1rem;
        text-align: center;
    ">
        <h4 style="color: white; margin: 0 0 0.5rem 0;">🎤 Voice Input</h4>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; margin: 0;">
            Record your message and it will be added to the chat
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add mic_recorder component
    from streamlit_mic_recorder import mic_recorder
    
    audio = mic_recorder(
        start_prompt="🎤 Record",
        stop_prompt="⏹️ Stop",
        just_once=False,
        format="wav",
        key="sidebar_recorder",
    )
    
    # Store audio in session state for processing in main app
    st.session_state.sidebar_audio = audio

def render_summary_pdf_download():
    """Render Summary PDF download section if Summary PDF is available"""
    import requests
    
    # Check if we have an active session
    session_id = st.session_state.get("session_id")
    
    # Try to check if Summary PDF is available via backend
    summary_pdf_available = False
    summary_pdf_url = None
    
    if session_id:
        # Check messages for Summary PDF availability flags
        if "messages" in st.session_state:
            for message in reversed(st.session_state.messages):
                if message.get("summary_pdf_available") and message.get("summary_pdf_download_url"):
                    summary_pdf_available = True
                    summary_pdf_url = f"{settings.backend_url}{message['summary_pdf_download_url']}"
                    break
    
    if summary_pdf_available and summary_pdf_url:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(139, 92, 246, 0.3);
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">📋 Summary PDF Bereit!</h4>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; margin: 0;">
                Ihre Zusammenfassung ist fertig
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        st.markdown(f"""
        <a href="{summary_pdf_url}" download style="
            display: block;
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            text-align: center;
            font-weight: 600;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
            transition: all 0.2s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(139, 92, 246, 0.4)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(139, 92, 246, 0.3)';">
            📥 Summary PDF Herunterladen
        </a>
        """, unsafe_allow_html=True)

def render_pdf_download():
    """Render PDF download section if PDF is available"""
    import requests
    
    # Check if we have an active session
    session_id = st.session_state.get("session_id")
    
    # Try to check if PDF is available via backend
    pdf_available = False
    pdf_url = None
    
    if session_id:
        # Check messages for PDF availability flags
        if "messages" in st.session_state:
            for message in reversed(st.session_state.messages):
                if message.get("pdf_available") and message.get("pdf_download_url"):
                    pdf_available = True
                    pdf_url = f"{settings.backend_url}{message['pdf_download_url']}"
                    break
    
    if pdf_available and pdf_url:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">📄 PDF Bereit!</h4>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; margin: 0;">
                Ihre Vorbereitung ist fertig
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        st.markdown(f"""
        <a href="{pdf_url}" download style="
            display: block;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            text-align: center;
            font-weight: 600;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
            transition: all 0.2s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.4)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(16, 185, 129, 0.3)';">
            📥 PDF Herunterladen
        </a>
        """, unsafe_allow_html=True)

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
            <h2 style="color: #00d4aa; margin: 0;">📄 Downloads</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Table PDF Download section
        render_pdf_download()
        
        # Summary PDF Download section
        render_summary_pdf_download()

def render_transcription():
    """Render transcription button section"""
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
            Transcribe audio to text
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio file uploader
    audio_file = st.file_uploader(
        "Upload audio file",
        type=['wav', 'mp3', 'm4a', 'ogg'],
        help="Upload an audio file to transcribe",
        key="audio_transcription_uploader"
    )
    
    if audio_file:
        if st.button("📝 Transcribe", use_container_width=True):
            import requests
            import tempfile
            import os
            
            with st.spinner("🎤 Transcribing audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp:
                    tmp.write(audio_file.getvalue())
                    tmp.flush()
                    tmp_path = tmp.name
                
                try:
                    with open(tmp_path, "rb") as f:
                        files = {"file": (audio_file.name, f, f"audio/{audio_file.name.split('.')[-1]}")}
                        resp = requests.post(
                            f"{settings.backend_url}/api/transcribe",
                            files=files,
                            timeout=60
                        )
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        text = (result.get("text") or "").strip()
                        
                        if text:
                            # Add transcribed text to session state so it gets picked up
                            st.session_state.transcribed_text = text
                            st.success(f"✅ Transcribed: '{text}'")
                            st.rerun()
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

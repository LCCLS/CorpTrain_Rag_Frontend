"""
Chat interface components
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Generator
from utils.formatting import format_source_name
import time
import requests
from config import settings

def render_chat_message(message: Dict[str, Any]):
    """
    Render a single chat message
    
    Args:
        message: Message dict with role, content, etc.
    """
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
            
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            if message.get("error"):
                st.markdown(f'<div class="error-message">{message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                # Show mode indicator if available
                if message.get("mode"):
                    mode_display = {
                        "knowledge": "📚 Wissensmodus",
                        "preparation": "📋 Vorbereitungsmodus"
                    }
                    st.caption(f"Mode: {mode_display.get(message['mode'], message['mode'])}")
                
                st.markdown(message["content"])
                
                # Show PDF download button if available (preparation mode)
                if message.get("pdf_available") and message.get("pdf_download_url"):
                    render_pdf_download_button(
                        message.get("pdf_download_url"),
                        message.get("session_id", "preparation")
                    )
                
                # Show sources if available
                if message.get("sources"):
                    render_sources(
                        message["sources"], 
                        message.get("document_count", 0),
                        message.get("retrieved_content", [])
                    )

def render_sources(sources: List[str], document_count: int, retrieved_content: List[str] = None):
    """
    Render source citations and retrieved content
    
    Args:
        sources: List of source identifiers
        document_count: Number of documents used
        retrieved_content: List of retrieved text content (optional)
    """
    if sources:
        with st.expander(f"📚 Sources ({document_count} documents)", expanded=False):
            for i, source in enumerate(sources, 1):
                formatted_source = format_source_name(source)
                st.markdown(f"**{i}.** {formatted_source}")
                
                # Show retrieved content if available
                if retrieved_content and i <= len(retrieved_content):
                    content = retrieved_content[i-1]
                    # Truncate very long content for better readability
                    if len(content) > 500:
                        content = content[:500] + "..."
                    
                    with st.expander(f"📄 Content from {formatted_source}", expanded=False):
                        st.text(content)

def render_message_timestamp(timestamp: datetime):
    """
    Render message timestamp
    
    Args:
        timestamp: Message timestamp
    """
    formatted_time = timestamp.strftime("%H:%M")
    st.caption(f"🕐 {formatted_time}")

def render_streaming_message(stream_generator: Generator[Dict[str, Any], None, None], mode: str = "knowledge") -> Dict[str, Any]:
    """
    Render a streaming message with real-time updates
    
    Args:
        stream_generator: Generator yielding streaming data chunks
        mode: Query mode for display
        
    Returns:
        Final message dict with complete content and metadata
    """
    # Create a placeholder for the streaming message
    message_placeholder = st.empty()
    full_content = ""
    sources = []
    document_count = 0
    session_id = None
    
    # Show mode indicator
    if mode:
        mode_display = {
            "knowledge": "📚 Wissensmodus",
            "preparation": "📋 Vorbereitungsmodus"
        }
        st.caption(f"Mode: {mode_display.get(mode, mode)}")
    
    # Create a container for the streaming content
    with message_placeholder.container():
        content_placeholder = st.empty()
        
        # Process streaming chunks
        for chunk in stream_generator:
            if chunk.get("type") == "chunk":
                full_content += chunk.get("content", "")
                # Update the content in real-time
                content_placeholder.markdown(full_content)
                time.sleep(0.01)  # Small delay for better visual effect
                
            elif chunk.get("type") == "complete":
                # Extract metadata from completion signal
                session_id = chunk.get("session_id")
                sources = chunk.get("sources", [])
                document_count = chunk.get("document_count", 0)
                break
                
            elif chunk.get("type") == "error":
                # Handle errors
                error_content = chunk.get("content", "An error occurred")
                content_placeholder.markdown(f'<div class="error-message">{error_content}</div>', 
                                          unsafe_allow_html=True)
                return {
                    "role": "assistant",
                    "content": error_content,
                    "error": True,
                    "timestamp": datetime.now(),
                    "mode": mode
                }
    
    # Show sources if available
    if sources:
        render_sources(sources, document_count)
    
    # Return the complete message
    return {
        "role": "assistant",
        "content": full_content,
        "mode": mode,
        "sources": sources,
        "document_count": document_count,
        "session_id": session_id,
        "timestamp": datetime.now()
    }

def render_pdf_download_button(pdf_url: str, session_id: str):
    """
    Render PDF download button
    
    Args:
        pdf_url: URL path to download the PDF
        session_id: Session ID for the filename
    """
    st.markdown("---")
    
    # Create a nice container for the download section
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="color: white; margin: 0 0 0.5rem 0;">📄 Ihre Verhandlungstabelle ist bereit!</h3>
        <p style="color: #e2e8f0; margin: 0 0 1rem 0;">
            Laden Sie Ihre personalisierte Schnellreferenz-Karte herunter
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Download button
        if st.button(
            "📥 PDF Herunterladen",
            key=f"download_pdf_{session_id}",
            type="primary",
            use_container_width=True
        ):
            try:
                # Make request to download PDF
                download_url = f"{settings.backend_url}{pdf_url}"
                response = requests.get(download_url, timeout=30)
                
                if response.status_code == 200:
                    # Provide download link
                    st.download_button(
                        label="💾 Datei speichern",
                        data=response.content,
                        file_name=f"verhandlungsvorbereitung_{session_id}.pdf",
                        mime="application/pdf",
                        key=f"save_pdf_{session_id}",
                        use_container_width=True
                    )
                    st.success("✅ PDF bereit zum Speichern!")
                elif response.status_code == 404:
                    st.error("❌ PDF nicht gefunden. Bitte vervollständigen Sie zuerst die Vorbereitung.")
                else:
                    st.error(f"❌ Download fehlgeschlagen: HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("❌ Download-Zeitüberschreitung. Bitte versuchen Sie es erneut.")
            except Exception as e:
                st.error(f"❌ Fehler beim Download: {str(e)}")
    
    # Info about the PDF
    st.info("💡 Die PDF enthält: Verhandlungsthemen, Ziele, Walk-Away-Points, wichtige Fragen und Ihre Verhandlungsstrategie")

def clear_chat_history():
    """Clear all chat messages"""
    st.session_state.messages = []
    st.rerun()
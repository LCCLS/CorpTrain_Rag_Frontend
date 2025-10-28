"""
Chat interface components
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Generator
from utils.formatting import format_source_name
import time
import requests
import markdown
from config import settings

def render_chat_message(message: Dict[str, Any]):
    """
    Render a single chat message with modern minimalistic styling
    
    Args:
        message: Message dict with role, content, etc.
    """
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', 
                   unsafe_allow_html=True)
            
    elif message["role"] == "assistant":
        if message.get("error"):
            st.markdown(f'<div class="error-message">{message["content"]}</div>', 
                      unsafe_allow_html=True)
        else:
            # Show mode indicator if available with subtle styling
            if message.get("mode"):
                mode_display = {
                    "knowledge": "📚 Knowledge Mode",
                    "preparation": "📋 Preparation Mode"
                }
                mode_text = mode_display.get(message['mode'], message['mode'])
                st.markdown(f'<div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem; font-weight: 500;">{mode_text}</div>', 
                           unsafe_allow_html=True)
            
            # Main message content with clean styling - same pattern as user message
            # Convert markdown to HTML for proper rendering in styled div
            try:
                html_content = markdown.markdown(message["content"], extensions=['nl2br', 'tables', 'fenced_code'])
                st.markdown(f'<div class="assistant-message">{html_content}</div>', 
                           unsafe_allow_html=True)
            except ImportError:
                # Fallback if markdown library is not available
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', 
                           unsafe_allow_html=True)
            except Exception:
                # Fallback for any other errors
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', 
                           unsafe_allow_html=True)
            
            # PDF download buttons are now handled in the sidebar only
            
            # Show sources if available
            if message.get("sources"):
                render_sources(
                    message["sources"], 
                    message.get("document_count", 0),
                    message.get("retrieved_content", [])
                )

def render_sources(sources: List[str], document_count: int, retrieved_content: List[str] = None):
    """
    Render source citations and retrieved content with minimalistic design
    
    Args:
        sources: List of source identifiers
        document_count: Number of documents used
        retrieved_content: List of retrieved text content (optional)
    """
    if sources:
        # Clean source expander with minimalistic styling
        with st.expander(f"📚 Sources ({document_count})", expanded=False):
            for i, source in enumerate(sources, 1):
                formatted_source = format_source_name(source)
                st.markdown(f"""
                <div style="
                    padding: 0.75rem 0;
                    border-bottom: 1px solid #f1f5f9;
                    font-size: 0.9rem;
                    color: #475569;
                ">
                    <strong>{i}.</strong> {formatted_source}
                </div>
                """, unsafe_allow_html=True)
                
                # Show retrieved content if available
                if retrieved_content and i <= len(retrieved_content):
                    content = retrieved_content[i-1]
                    # Truncate very long content for better readability
                    if len(content) > 500:
                        content = content[:500] + "..."
                    
                    with st.expander(f"View content from {formatted_source}", expanded=False):
                        st.markdown(f"""
                        <div style="
                            font-size: 0.85rem;
                            line-height: 1.5;
                            color: #64748b;
                            background: #f8fafc;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 3px solid #e2e8f0;
                        ">
                            {content}
                        </div>
                        """, unsafe_allow_html=True)

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

def render_pdf_download_button(pdf_url: str, session_id: str, message_index: int = 0):
    """
    Render PDF download button
    
    Args:
        pdf_url: URL path to download the PDF
        session_id: Session ID for the filename
        message_index: Index of the message to make key unique
    """
    st.markdown("---")
    
    # Minimalistic download section
    st.markdown("""
    <div style="
        background: #f8fafc;
        padding: 1.25rem;
        border-radius: 16px;
        margin: 1rem 0;
        text-align: center;
        border: 1px solid #e2e8f0;
    ">
        <h3 style="
            color: #1e293b; 
            margin: 0 0 0.5rem 0; 
            font-size: 1.1rem;
            font-weight: 600;
        ">📄 Preparation summary ready</h3>
        <p style="
            color: #64748b; 
            margin: 0 0 1rem 0;
            font-size: 0.9rem;
        ">
            Download your personalized negotiation reference
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Download button
        if st.button(
            "Download PDF",
            key=f"download_pdf_{session_id}_{message_index}",
            type="primary",
            use_container_width=True
        ):
            try:
                # Make request to download PDF
                download_url = f"{settings.backend_url}{pdf_url}"
                response = requests.get(download_url, timeout=60)
                
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
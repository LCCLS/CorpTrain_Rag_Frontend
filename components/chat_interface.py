"""
Chat interface components
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from utils.formatting import format_source_name

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
                st.markdown(message["content"])
                
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

def clear_chat_history():
    """Clear all chat messages"""
    st.session_state.messages = []
    st.rerun()
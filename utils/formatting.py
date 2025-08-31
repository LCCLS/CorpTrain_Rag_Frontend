"""
Formatting utilities for the Streamlit frontend
Handles response formatting, text processing, and UI helpers
"""
import re
import html
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st

def format_answer_text(text: str) -> str:
    """
    Format answer text for better display in Streamlit
    
    Args:
        text: Raw answer text from backend
        
    Returns:
        Formatted text with proper markdown
    """
    if not text:
        return "No answer provided."
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text.strip())
    
    # Escape HTML entities
    text = html.unescape(text)
    
    # Format lists better
    text = re.sub(r'\n(\d+\.)', r'\n\n\1', text)  # Add space before numbered lists
    text = re.sub(r'\n(-|\*)', r'\n\n\1', text)   # Add space before bullet lists
    
    return text

def format_sources_display(sources: List[str], document_count: int) -> str:
    """
    Format sources for display in the UI
    
    Args:
        sources: List of source identifiers
        document_count: Number of documents used
        
    Returns:
        Formatted sources string
    """
    if not sources:
        return "No sources available"
    
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        # Clean up source names
        clean_source = format_source_name(source)
        formatted_sources.append(f"**{i}.** {clean_source}")
    
    return "\n".join(formatted_sources)

def format_source_name(source: str) -> str:
    """
    Format individual source names for better readability
    
    Args:
        source: Raw source identifier
        
    Returns:
        Cleaned and formatted source name
    """
    if not source:
        return "Unknown Source"
    
    # Remove file extensions (including .md)
    source = re.sub(r'\.(pdf|txt|docx|doc|md)$', '', source, flags=re.IGNORECASE)
    
    # Replace underscores and hyphens with spaces
    source = re.sub(r'[_-]', ' ', source)
    
    # Capitalize words
    source = ' '.join(word.capitalize() for word in source.split())
    
    # Handle common patterns
    source = re.sub(r'Document (\d+)', r'Document \1', source)
    source = re.sub(r'Chunk (\d+)', r'Section \1', source)
    
    return source

def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Message timestamp
        
    Returns:
        Formatted time string
    """
    now = datetime.now()
    time_diff = now - timestamp
    
    if time_diff.seconds < 60:
        return "Just now"
    elif time_diff.seconds < 3600:
        minutes = time_diff.seconds // 60
        return f"{minutes}m ago"
    elif time_diff.days == 0:
        return timestamp.strftime("%H:%M")
    else:
        return timestamp.strftime("%b %d, %H:%M")

def format_error_message(error_type: str, message: str) -> str:
    """
    Format error messages for user display
    
    Args:
        error_type: Type of error (connection, timeout, server, etc.)
        message: Error message
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        "connection": "🔌 **Connection Error**: Cannot reach the backend server. Please check your internet connection or contact support.",
        "timeout": "⏱️ **Timeout Error**: The request took too long. The server might be busy - please try again.",
        "server": "🖥️ **Server Error**: Something went wrong on the server. Please try again or contact support.",
        "validation": "⚠️ **Invalid Input**: Please check your question and try again.",
        "not_found": "🔍 **Not Found**: The requested resource was not found.",
        "unauthorized": "🔒 **Access Denied**: You don't have permission to access this resource."
    }
    
    base_message = error_messages.get(error_type, "❌ **Error**: Something went wrong.")
    
    if message:
        return f"{base_message}\n\n*Details: {message}*"
    
    return base_message

def format_query_stats(response: Dict[str, Any]) -> str:
    """
    Format query statistics for display
    
    Args:
        response: Backend response with stats
        
    Returns:
        Formatted stats string
    """
    stats = []
    
    if "document_count" in response:
        stats.append(f"📄 {response['document_count']} documents")
    
    if "sources" in response and response["sources"]:
        stats.append(f"🔗 {len(response['sources'])} sources")
    
    # Add processing time if available (future enhancement)
    if "processing_time" in response:
        stats.append(f"⚡ {response['processing_time']:.2f}s")
    
    return " • ".join(stats) if stats else ""

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncate text for preview purposes
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add "..." at the end
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rsplit(' ', 1)[0]  # Don't cut words
    return f"{truncated}..." if add_ellipsis else truncated

def highlight_keywords(text: str, keywords: List[str]) -> str:
    """
    Highlight keywords in text (for search results)
    
    Args:
        text: Text to highlight
        keywords: Keywords to highlight
        
    Returns:
        Text with highlighted keywords
    """
    if not keywords:
        return text
    
    for keyword in keywords:
        if keyword.strip():
            # Case-insensitive highlighting
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(f'**{keyword}**', text)
    
    return text

def format_chat_export(messages: List[Dict[str, Any]]) -> str:
    """
    Format chat history for export
    
    Args:
        messages: List of chat messages
        
    Returns:
        Formatted chat export string
    """
    if not messages:
        return "No chat history to export."
    
    export_lines = [
        "# Chat Export",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total messages: {len(messages)}",
        "\n---\n"
    ]
    
    for i, message in enumerate(messages, 1):
        timestamp = message.get("timestamp", datetime.now())
        role = message["role"].title()
        content = message["content"]
        
        export_lines.append(f"## Message {i} - {role}")
        export_lines.append(f"Time: {format_timestamp(timestamp)}")
        export_lines.append(f"\n{content}\n")
        
        if message.get("sources"):
            export_lines.append("**Sources:**")
            for j, source in enumerate(message["sources"], 1):
                export_lines.append(f"{j}. {format_source_name(source)}")
        
        export_lines.append("\n---\n")
    
    return "\n".join(export_lines)

def format_health_status(health_data: Dict[str, Any]) -> str:
    """
    Format health check data for display
    
    Args:
        health_data: Health check response
        
    Returns:
        Formatted health status
    """
    if health_data.get("status") == "healthy":
        lines = ["✅ **System Healthy**"]
        
        if "data" in health_data:
            data = health_data["data"]
            
            # Database info
            if "database" in data:
                db = data["database"]
                if db.get("document_count"):
                    lines.append(f"📊 Documents: {db['document_count']}")
                if db.get("collection_name"):
                    lines.append(f"🗂️ Collection: {db['collection_name']}")
            
            # Environment info
            if data.get("environment"):
                lines.append(f"🌍 Environment: {data['environment']}")
        
        return "\n".join(lines)
    
    else:
        error = health_data.get("error", "Unknown error")
        return f"❌ **System Unhealthy**\nError: {error}"

def create_message_container_style(role: str) -> str:
    """
    Create CSS style for message containers
    
    Args:
        role: Message role (user/assistant)
        
    Returns:
        CSS style string
    """
    if role == "user":
        return """
        <style>
        .user-message {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            border-left: 3px solid #2196f3;
        }
        </style>
        """
    else:
        return """
        <style>
        .assistant-message {
            background-color: #f5f5f5;
            padding: 1rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            border-left: 3px solid #4caf50;
        }
        </style>
        """

def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input for safety
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>\"\'&]', '', text)
    
    # Limit length
    text = text[:1000]  # Max 1000 characters
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text

def format_processing_indicator(stage: str) -> str:
    """
    Format processing stage indicators
    
    Args:
        stage: Current processing stage
        
    Returns:
        Formatted indicator text
    """
    indicators = {
        "connecting": "🔌 Connecting to backend...",
        "searching": "🔍 Searching through documents...",
        "processing": "⚙️ Processing your question...",
        "generating": "✨ Generating response...",
        "finalizing": "📝 Finalizing answer..."
    }
    
    return indicators.get(stage, f"⏳ {stage}...")
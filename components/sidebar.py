"""
Sidebar components for the RAG frontend
"""
import streamlit as st
from typing import Dict, Any

from services.api_client import APIClient
from config import settings

def render_sidebar(api_client: APIClient):
    """
    Render the sidebar with system status and controls
    
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
            <h2 style="color: #00d4aa; margin: 0;">🤖 Assistant Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # System status
        render_system_status(api_client)
        
        # PDF Download section
        render_pdf_download()
        
        # Query settings
        render_query_settings()
        
        # Chat controls
        render_chat_controls()
        
        # Help section
        render_help_section()

def render_system_status(api_client: APIClient):
    """Render system status section with dark theme"""
    st.markdown("""
    <div style="
        background: rgba(0, 212, 170, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        margin-bottom: 1rem;
    ">
        <h4 style="color: #00d4aa; margin: 0 0 1rem 0;">📡 System Status</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Check Backend Status", type="secondary"):
        with st.spinner("🔍 Checking backend..."):
            health_status = api_client.check_health()
            
            if health_status["status"] == "healthy":
                st.markdown("""
                <div style="
                    background: rgba(76, 175, 80, 0.2);
                    padding: 1rem;
                    border-radius: 10px;
                    border: 1px solid #4caf50;
                    color: #4caf50;
                    margin: 0.5rem 0;
                ">
                    ✅ <strong>Backend is running</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Show additional details if available
                if "data" in health_status:
                    data = health_status["data"]
                    doc_count = data.get('database', {}).get('document_count', 'Unknown')
                    environment = data.get('environment', 'Unknown')
                    
                    st.markdown(f"""
                    <div style="
                        background: rgba(38, 39, 48, 0.8);
                        padding: 0.75rem;
                        border-radius: 8px;
                        margin: 0.25rem 0;
                        color: #fafafa;
                    ">
                        📊 <strong>Documents:</strong> {doc_count}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="
                        background: rgba(38, 39, 48, 0.8);
                        padding: 0.75rem;
                        border-radius: 8px;
                        margin: 0.25rem 0;
                        color: #fafafa;
                    ">
                        🌍 <strong>Environment:</strong> {environment}
                    </div>
                    """, unsafe_allow_html=True)
                    
            elif health_status["status"] == "unreachable":
                st.markdown(f"""
                <div style="
                    background: rgba(244, 67, 54, 0.2);
                    padding: 1rem;
                    border-radius: 10px;
                    border: 1px solid #f44336;
                    color: #f44336;
                    margin: 0.5rem 0;
                ">
                    ❌ <strong>Cannot reach backend</strong><br>
                    <small>URL: {api_client.backend_url}</small>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                error = health_status.get('error', 'Unknown error')
                st.markdown(f"""
                <div style="
                    background: rgba(244, 67, 54, 0.2);
                    padding: 1rem;
                    border-radius: 10px;
                    border: 1px solid #f44336;
                    color: #f44336;
                    margin: 0.5rem 0;
                ">
                    ❌ <strong>Backend unhealthy:</strong> {error}
                </div>
                """, unsafe_allow_html=True)

def render_query_settings():
    """Render query configuration settings with dark theme"""
    st.markdown("""
    <div style="
        background: rgba(0, 212, 170, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        margin-bottom: 1rem;
    ">
        <h4 style="color: #00d4aa; margin: 0 0 1rem 0;">⚙️ Query Settings</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Number of documents to retrieve
    st.markdown("**📄 Documents to retrieve:**")
    top_k = st.slider(
        "",
        min_value=1,
        max_value=settings.max_top_k,
        value=settings.default_top_k,
        help="Number of relevant documents to use for generating answers",
        label_visibility="collapsed"
    )
    
    # Store in session state
    st.session_state["top_k"] = top_k
    
    # Show current setting
    st.markdown(f"""
    <div style="
        background: rgba(38, 39, 48, 0.8);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #fafafa;
        text-align: center;
    ">
        Currently retrieving <strong>{top_k}</strong> documents
    </div>
    """, unsafe_allow_html=True)
    
    # Backend URL configuration (for development)
    if st.checkbox("🔧 Advanced Settings"):
        st.markdown("**🌐 Backend URL:**")
        new_backend_url = st.text_input(
            "",
            value=settings.backend_url,
            help="URL of the RAG backend API",
            label_visibility="collapsed"
        )
        
        if new_backend_url != settings.backend_url:
            settings.backend_url = new_backend_url
            st.session_state.api_client = APIClient(new_backend_url)
            st.markdown("""
            <div style="
                background: rgba(76, 175, 80, 0.2);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 1px solid #4caf50;
                color: #4caf50;
                margin: 0.5rem 0;
                text-align: center;
            ">
                ✅ Backend URL updated!
            </div>
            """, unsafe_allow_html=True)

def render_chat_controls():
    """Render chat control buttons with dark theme"""
    st.markdown("""
    <div style="
        background: rgba(0, 212, 170, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        margin-bottom: 1rem;
    ">
        <h4 style="color: #00d4aa; margin: 0 0 1rem 0;">💬 Chat Controls</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear", type="secondary", help="Clear chat history"):
            st.session_state.messages = []
            st.markdown("""
            <div style="
                background: rgba(76, 175, 80, 0.2);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 1px solid #4caf50;
                color: #4caf50;
                margin: 0.5rem 0;
                text-align: center;
            ">
                ✅ Chat history cleared!
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
    
    with col2:
        if st.button("📤 Export", disabled=True, help="Export chat (coming soon)"):
            st.info("Export feature coming soon!")
    
    # Show chat stats
    message_count = len(st.session_state.get("messages", []))
    st.markdown(f"""
    <div style="
        background: rgba(38, 39, 48, 0.8);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #fafafa;
        text-align: center;
    ">
        💬 <strong>{message_count}</strong> messages in history
    </div>
    """, unsafe_allow_html=True)

def render_help_section():
    """Render help and examples section with dark theme"""
    st.markdown("""
    <div style="
        background: rgba(0, 212, 170, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 170, 0.3);
        margin-bottom: 1rem;
    ">
        <h4 style="color: #00d4aa; margin: 0 0 1rem 0;">💡 Help & Examples</h4>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("❓ How to use", expanded=False):
        st.markdown("""
        <div style="color: #fafafa;">
        <strong>How to ask questions:</strong>
        
        1. Type your question in the chat input
        2. Press Enter or click Send
        3. Wait for the AI to search and respond
        4. View sources by expanding the "Sources" section
        
        <strong>Example questions:</strong>
        - "What are the key safety procedures?"
        - "How do I handle customer complaints?"
        - "What is the company policy on remote work?"
        - "Explain the onboarding process"
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        <div style="color: #fafafa;">
        <strong>Common issues:</strong>
        
        - <strong>"Cannot connect to backend"</strong>: Check if backend is running
        - <strong>Slow responses</strong>: Try reducing documents to retrieve
        - <strong>No relevant answers</strong>: Your question might be outside the training materials
        - <strong>Error messages</strong>: Check the system status above
        
        <strong>Need help?</strong> Contact your system administrator.
        </div>
        """, unsafe_allow_html=True)
    
    # Current settings summary
    with st.expander("📊 Current Settings", expanded=False):
        current_settings = {
            "backend_url": settings.backend_url,
            "documents_per_query": st.session_state.get("top_k", settings.default_top_k),
            "request_timeout": f"{settings.request_timeout}s",
            "messages_in_history": len(st.session_state.get("messages", []))
        }
        
        st.markdown("""
        <div style="
            background: rgba(38, 39, 48, 0.8);
            padding: 1rem;
            border-radius: 8px;
            color: #fafafa;
        ">
        """, unsafe_allow_html=True)
        
        for key, value in current_settings.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_pdf_download():
    """Render PDF download section if PDF is available"""
    import requests
    
    # Check if we have an active session
    session_id = st.session_state.get("session_id")
    
    # Try to check if PDF is available via backend
    pdf_available = False
    pdf_url = None
    
    if session_id:
        try:
            # Quick check: try to access the PDF download endpoint
            pdf_check_url = f"{settings.backend_url}/api/pdf/download/{session_id}"
            response = requests.head(pdf_check_url, timeout=2)
            
            if response.status_code == 200:
                pdf_available = True
                pdf_url = pdf_check_url
        except:
            # If check fails, fall back to checking messages
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
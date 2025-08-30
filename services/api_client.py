"""
API client for communicating with the RAG backend
"""
import requests
import logging
from typing import Dict, Any, Optional
import streamlit as st

from config import settings

logger = logging.getLogger(__name__)

class APIClient:
    """Client for RAG backend API"""
    
    def __init__(self, backend_url: str):
        """
        Initialize API client
        
        Args:
            backend_url: URL of the RAG backend
        """
        self.backend_url = backend_url.rstrip('/')
        self.timeout = settings.request_timeout
        
    def check_health(self) -> Dict[str, Any]:
        """
        Check backend health status
        
        Returns:
            Dict with health status or error info
        """
        try:
            response = requests.get(
                f"{self.backend_url}/health",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "data": response.json()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "unreachable",
                "error": "Cannot connect to backend",
                "details": f"Failed to connect to {self.backend_url}"
            }
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": "Request timeout",
                "details": f"Request took longer than {self.timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "details": "Unexpected error during health check"
            }
    
    def query_documents(self, question: str, top_k: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Query the RAG system with a question
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve (optional)
            
        Returns:
            Response from backend or None if error
        """
        try:
            # Prepare request data
            request_data = {"question": question}
            if top_k is not None:
                request_data["top_k"] = top_k
            
            # Make API request
            response = requests.post(
                f"{self.backend_url}/api/query",
                json=request_data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed: HTTP {response.status_code} - {response.text}")
                st.error(f"Backend error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to backend")
            st.error("❌ Cannot connect to backend. Please check if the backend is running.")
            return None
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            st.error(f"⏱️ Request timeout ({self.timeout}s). The backend might be overloaded.")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
    
    def query_documents_get(self, question: str, top_k: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Query using GET method (alternative)
        
        Args:
            question: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            Response from backend or None if error
        """
        try:
            params = {"question": question}
            if top_k is not None:
                params["top_k"] = top_k
            
            response = requests.get(
                f"{self.backend_url}/api/query",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"GET Query failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"GET Query error: {e}")
            return None
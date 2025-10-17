"""
Frontend configuration
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv(".env")  # Try .env first
load_dotenv("local.env")  # Then local.env as override

class Settings:
    """Frontend configuration settings"""
    
    # Backend API configuration
    backend_url: str = os.getenv("BACKEND_URL", "https://corptrainrag-production-576c.up.railway.app")
    
    # UI settings
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    max_top_k: int = int(os.getenv("MAX_TOP_K", "20"))
    
    # Timeouts
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # App settings
    app_title: str = os.getenv("APP_TITLE", "Corporate Training Assistant")
    app_description: str = os.getenv(
        "APP_DESCRIPTION", 
        "Ask questions about your corporate training documents"
    )
    
    # Deployment settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    def get_backend_health_url(self) -> str:
        """Get backend health check URL"""
        return f"{self.backend_url.rstrip('/')}/health"
    
    def get_backend_query_url(self) -> str:
        """Get backend query URL"""
        return f"{self.backend_url.rstrip('/')}/api/query"

# Global settings instance
settings = Settings()
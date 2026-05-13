import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # LLM API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Security Settings
    MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", 2000))
    ENTROPY_THRESHOLD = float(os.getenv("ENTROPY_THRESHOLD", 4.5))
    
    # Detection Settings
    ENABLE_ENTROPY_CHECK = os.getenv("ENABLE_ENTROPY_CHECK", "true").lower() == "true"
    ENABLE_REGEX_CHECK = os.getenv("ENABLE_REGEX_CHECK", "true").lower() == "true"
    
    # Model Settings
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3-8b-8192")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

settings = Settings()
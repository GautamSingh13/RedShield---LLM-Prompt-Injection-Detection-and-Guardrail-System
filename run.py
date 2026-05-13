
import uvicorn
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def main():
    print("Starting RedShield AI Security System")
    print("=" * 40)
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Groq API Key: {'Configured' if settings.GROQ_API_KEY else 'Missing'}")
    print("=" * 40)
    
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

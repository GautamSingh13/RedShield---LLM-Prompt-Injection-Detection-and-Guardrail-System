from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from core.sanitization import analyze_prompt_safety
from config.settings import settings
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RedShield AI Security API",
    version="1.0.0",
    description="LLM Prompt Injection Detection and Guardrail System"
)

# Initialize Groq client
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
        logger.info("Groq client initialized successfully")
    else:
        client = None
        logger.warning("No Groq API key found - running in demo mode")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

class QueryRequest(BaseModel):
    input: str

class QueryResponse(BaseModel):
    response: str
    security_status: str
    sanitized: bool = False
    confidence: float = 0.0
    original_length: int = 0
    sanitized_length: int = 0
    timestamp: str

@app.post("/", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Main endpoint for processing user queries with security filtering."""
    timestamp = datetime.now().isoformat()
    user_input = request.input.strip()
    
    logger.info(f"Processing query: {user_input[:50]}...")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="Input cannot be empty")
    
    if len(user_input) > settings.MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Input too long. Maximum {settings.MAX_PROMPT_LENGTH} characters.")
    
    try:
        # Security analysis
        safety_analysis = analyze_prompt_safety(user_input)
        
        # Handle blocked content
        if not safety_analysis["is_safe"]:
            logger.warning("Blocked malicious input")
            return QueryResponse(
                response="Your input was blocked due to security concerns. Please rephrase your request safely.",
                security_status="BLOCKED",
                confidence=safety_analysis["confidence"],
                original_length=len(user_input),
                timestamp=timestamp
            )
        
        # Get sanitized input
        safe_input = safety_analysis["sanitized_text"]
        was_sanitized = safety_analysis["was_modified"]
        
        # Handle no LLM case
        if not client:
            response_text = f"[DEMO MODE] Your input: {safe_input}"
            if was_sanitized:
                response_text = f"[DEMO MODE] Your sanitized input: {safe_input}"
            
            return QueryResponse(
                response=response_text,
                security_status=safety_analysis["security_status"],
                sanitized=was_sanitized,
                confidence=safety_analysis["confidence"],
                original_length=len(user_input),
                sanitized_length=len(safe_input),
                timestamp=timestamp
            )
        
        # Generate LLM response
        try:
            llm_prompt = safe_input
            if was_sanitized:
                llm_prompt = f"Please respond helpfully to this request: {safe_input}"
            
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful and safe AI assistant."},
                    {"role": "user", "content": llm_prompt}
                ],
                model=settings.DEFAULT_MODEL,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            llm_response = completion.choices[0].message.content
            
            if was_sanitized:
                final_response = f"[Content was sanitized for safety]\n\n{llm_response}"
            else:
                final_response = llm_response
            
            logger.info("Generated LLM response successfully")
            
            return QueryResponse(
                response=final_response,
                security_status=safety_analysis["security_status"],
                sanitized=was_sanitized,
                confidence=safety_analysis["confidence"],
                original_length=len(user_input),
                sanitized_length=len(safe_input),
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            fallback_response = f"LLM service unavailable. Your safe input was: {safe_input}"
            
            return QueryResponse(
                response=fallback_response,
                security_status=safety_analysis["security_status"],
                sanitized=was_sanitized,
                confidence=safety_analysis["confidence"],
                original_length=len(user_input),
                sanitized_length=len(safe_input),
                timestamp=timestamp
            )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "groq_available": client is not None,
        "message": "RedShield AI Security API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


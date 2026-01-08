"""
FastAPI Backend: Career Guidance AI Agent
REST API for the career guidance system.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from career_agent.agent import CareerGuidanceAgent
import logging
import uuid
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fastapi_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Guidance AI API",
    description="Bilingual AI-powered career guidance for Indian 12th-grade students",
    version="1.0.0"
)

# CORS middleware
# Allow frontend from various origins
def validate_origin(origin: str) -> bool:
    """Validate that origin is a well-formed URL with scheme and host."""
    try:
        parsed = urlparse(origin.strip())
        # Require scheme to be http or https
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Invalid origin scheme: {origin} (scheme: {parsed.scheme})")
            return False
        # Require netloc (host) to be present
        if not parsed.netloc:
            logger.warning(f"Invalid origin: missing netloc: {origin}")
            return False
        # Forbid paths, queries, fragments, and params (origin must be scheme+host+optional port only)
        if parsed.path or parsed.params or parsed.query or parsed.fragment:
            logger.warning(f"Invalid origin: contains path/query/fragment: {origin}")
            return False
        # Validate hostname is non-empty
        if not parsed.hostname:
            logger.warning(f"Invalid origin: empty hostname: {origin}")
            return False
        return True
    except (ValueError, AttributeError) as e:
        logger.exception(f"Error parsing origin: {origin}")
        return False

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
is_production = os.getenv("ENV", "").lower() == "production" or os.getenv("PRODUCTION", "").lower() == "true"

if allowed_origins_env:
    # Parse and validate each origin
    raw_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    allowed_origins = []
    invalid_origins = []
    
    for origin in raw_origins:
        if validate_origin(origin):
            allowed_origins.append(origin.strip())
        else:
            invalid_origins.append(origin)
            logger.warning(f"Invalid origin in ALLOWED_ORIGINS, skipping: {origin}")
    
    if invalid_origins:
        logger.warning(f"Skipped {len(invalid_origins)} invalid origin(s) from ALLOWED_ORIGINS")
    
    # Production check: fail fast if no valid origins
    if is_production and not allowed_origins:
        error_msg = "PRODUCTION mode requires at least one valid origin in ALLOWED_ORIGINS. Please set ALLOWED_ORIGINS with valid URLs (e.g., https://yourdomain.com)."
        logger.error(error_msg)
        raise ValueError(error_msg)
else:
    # Default: Allow common local development origins
    if is_production:
        error_msg = "PRODUCTION mode requires ALLOWED_ORIGINS to be set. Please configure ALLOWED_ORIGINS environment variable with your production domain(s)."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    allowed_origins = [
        "https://shivamsonawane2003.github.io"
        "http://localhost:8501",
        "http://localhost:8502", 
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    logger.warning("ALLOWED_ORIGINS not set, falling back to localhost-only defaults. This is not suitable for production. Please set ALLOWED_ORIGINS environment variable.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store agent instances per session
agents = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = None  # Optional language preference: "en" or "mr"


class ChatResponse(BaseModel):
    response: str
    complete: bool
    session_id: str
    error: bool = False


class RestartRequest(BaseModel):
    session_id: str


class RestartResponse(BaseModel):
    success: bool
    message: str


def get_agent(session_id: str) -> CareerGuidanceAgent:
    """Get or create agent for session."""
    if session_id not in agents:
        logger.info(f"Creating new agent for session: {session_id}")
        agents[session_id] = CareerGuidanceAgent()
        logger.info(f"Agent created successfully for session: {session_id}")
    else:
        logger.debug(f"Retrieved existing agent for session: {session_id}")
    return agents[session_id]


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {
        "message": "Career Guidance AI API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": "career-guidance-agent"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages.
    Enforces one-question-at-a-time rule.
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"New session created: {session_id}")
        else:
            session_id = request.session_id
            logger.debug(f"Existing session: {session_id}")
        
        user_input = request.message.strip()
        logger.info(f"Processing message for session {session_id}: {user_input[:100]}...")
        
        if not user_input:
            logger.warning(f"Empty message received for session {session_id}")
            raise HTTPException(
                status_code=400,
                detail="Please provide a valid message."
            )
        
        agent = get_agent(session_id)
        logger.debug(f"Agent retrieved for session {session_id}, current phase: {agent.get_current_phase()}, current language: {agent.language}")
        
        # Set language preference if provided (MUST be before process_input)
        if request.language:
            agent.set_language(request.language)
            logger.info(f"Language preference set to: {request.language} for session {session_id} (was: {agent.language})")
        else:
            logger.debug(f"No language preference provided, using agent's current language: {agent.language}")
        
        response, is_complete = agent.process_input(user_input)
        logger.debug(f"Response generated in language: {agent.language}")
        logger.info(f"Response generated for session {session_id} (complete: {is_complete}, response length: {len(response)})")
        
        return ChatResponse(
            response=response,
            complete=is_complete,
            session_id=session_id,
            error=False
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred. Please try again."
        )


@app.post("/api/restart", response_model=RestartResponse)
async def restart(request: RestartRequest):
    """Reset conversation and start fresh."""
    try:
        session_id = request.session_id
        logger.info(f"Restart requested for session: {session_id}")
        
        if session_id in agents:
            agents[session_id].reset()
            logger.info(f"Agent reset for session: {session_id}")
        else:
            logger.warning(f"Restart requested for non-existent session: {session_id}")
        
        return RestartResponse(
            success=True,
            message="Conversation reset successfully."
        )
    
    except Exception as e:
        logger.error(f"Error in restart endpoint for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error resetting conversation."
        )


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)


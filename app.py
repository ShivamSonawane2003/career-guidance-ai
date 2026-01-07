"""
Streamlit Frontend: Career Guidance AI Agent
UI-only application that connects to FastAPI backend.
"""

import streamlit as st
import httpx
import os
import logging
from dotenv import load_dotenv

# Configuration - Support both Streamlit Cloud secrets and local .env
if hasattr(st, 'secrets') and 'API_BASE_URL' in st.secrets:
    # Streamlit Cloud deployment
    API_BASE_URL = st.secrets['API_BASE_URL']
else:
    # Local development
    load_dotenv()
    API_BASE_URL = os.getenv("API_BASE_URL", "https://career-guidance-ai-xo2g.onrender.com")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration - Use environment variables only
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
logger.info(f"Initialized Streamlit app with API_BASE_URL: {API_BASE_URL}")
>>>>>>> d376f0b (Initial commit: Career Guidance AI Agent)

# Page configuration
st.set_page_config(
    page_title="Career Guidance AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMarkdown {
        line-height: 1.8;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    logger.debug("Initializing session state")
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
        logger.debug("Session ID initialized to None")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        logger.info("Initializing new conversation - fetching welcome message")
        # Get welcome message
        try:
            with httpx.Client() as client:
                logger.debug(f"Sending initial 'hello' message to {API_BASE_URL}/api/chat")
                response = client.post(
                    f"{API_BASE_URL}/api/chat",
                    json={"message": "hello"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data.get("session_id")
                    logger.info(f"Received welcome message, session_id: {st.session_state.session_id}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["response"]
                    })
                else:
                    logger.warning(f"Backend returned status {response.status_code} for welcome message")
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to backend at {API_BASE_URL}: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Welcome! I'm your career guidance assistant. Please make sure the FastAPI backend is running."
            })
        except Exception as e:
            logger.error(f"Error initializing session: {e}", exc_info=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Welcome! I'm your career guidance assistant. Please make sure the FastAPI backend is running."
            })
    
    if 'complete' not in st.session_state:
        st.session_state.complete = False
        logger.debug("Conversation complete flag initialized to False")


def send_message(message: str) -> tuple:
    """Send message to FastAPI backend."""
    logger.info(f"Sending message to backend (session_id: {st.session_state.session_id}): {message[:50]}...")
    try:
        with httpx.Client() as client:
            logger.debug(f"POST request to {API_BASE_URL}/api/chat with message length: {len(message)}")
            response = client.post(
                f"{API_BASE_URL}/api/chat",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id
                },
                timeout=30.0
            )
            logger.debug(f"Received response with status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data.get("session_id")
                is_complete = data.get("complete", False)
                logger.info(f"Successfully received response (complete: {is_complete}, response length: {len(data.get('response', ''))})")
                return data["response"], is_complete, None
            else:
                logger.error(f"Backend returned error status {response.status_code}: {response.text}")
                return None, False, f"Error: {response.status_code}"
    
    except httpx.ConnectError as e:
        logger.error(f"Connection error to backend at {API_BASE_URL}: {e}")
        return None, False, "Cannot connect to backend. Please make sure FastAPI server is running on " + API_BASE_URL
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout: {e}")
        return None, False, "Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}", exc_info=True)
        return None, False, f"Error: {str(e)}"


def reset_conversation():
    """Reset the conversation via API."""
    logger.info(f"Resetting conversation (session_id: {st.session_state.session_id})")
    if st.session_state.session_id:
        try:
            with httpx.Client() as client:
                logger.debug(f"Sending restart request to {API_BASE_URL}/api/restart")
                response = client.post(
                    f"{API_BASE_URL}/api/restart",
                    json={"session_id": st.session_state.session_id},
                    timeout=10.0
                )
                if response.status_code == 200:
                    logger.info("Backend confirmed conversation reset")
                    # Get new welcome message
                    send_message("hello")
                else:
                    logger.warning(f"Backend restart returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}", exc_info=True)
            st.error(f"Error resetting: {e}")
    
    # Reset local state
    st.session_state.messages = []
    st.session_state.complete = False
    st.session_state.session_id = None
    logger.info("Local session state reset complete")
    initialize_session_state()


def main():
    """Main Streamlit application."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1> Career Guidance AI</h1>
            <p>Bilingual Assistant for Indian 12th Grade Students</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Controls")
        if st.button(" Restart Conversation", key="restart", use_container_width=True):
            reset_conversation()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This AI agent provides career guidance for 12th grade students in India.
        based on:
        - Your academic stream (PCM/PCB/Commerce/Arts/Vocational)
        - Your interests and aptitudes
        - Indian higher education pathways
        
        **Note**: This is first-level guidance only. 
        Please consult a certified career counselor for final decisions.
        """)
        
        st.markdown("---")
        st.markdown("### API Status")
        try:
            logger.debug(f"Checking backend health at {API_BASE_URL}/health")
            with httpx.Client() as client:
                response = client.get(f"{API_BASE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    st.success("Backend Connected")
                else:
                    st.error(" Backend Error")
        except:
            st.error(" Backend Offline")
=======
                    logger.debug("Backend health check passed")
                    st.success("✅ Backend Connected")
                else:
                    logger.warning(f"Backend health check returned status {response.status_code}")
                    st.error(" Backend Error")
        except httpx.ConnectError as e:
            logger.error(f"Backend health check failed - connection error: {e}")
            st.error(" Backend Offline")
            st.info(f"Expected at: {API_BASE_URL}")
        except Exception as e:
            logger.error(f"Backend health check failed - unexpected error: {e}", exc_info=True)
            st.error(" Backend Offline")
            st.info(f"Expected at: {API_BASE_URL}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input area
    if not st.session_state.complete:
        # User input using Streamlit's chat input
        if prompt := st.chat_input("Type your message here..."):
            logger.info(f"User input received: {prompt[:100]}...")
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Get agent response from API
            response, is_complete, error = send_message(prompt)
            
            if error:
                logger.error(f"Error in response: {error}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f" {error}"
                })
            elif response:
                logger.info(f"Response received (complete: {is_complete}, length: {len(response)})")
                st.session_state.complete = is_complete
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            else:
                logger.warning("No response and no error returned from send_message")
            
            # Rerun to update UI
            st.rerun()
    else:
        st.info(" Conversation complete! Use the Restart button in the sidebar to start a new conversation.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>
         This guidance is indicative only. Please confirm your decision with a certified human career counselor.
        </small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()


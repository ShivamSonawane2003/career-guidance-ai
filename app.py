"""
Streamlit Frontend: Career Guidance AI Agent
UI-only application that connects to FastAPI backend.
"""

import streamlit as st
import httpx
import os
from dotenv import load_dotenv

# Configuration - Support both Streamlit Cloud secrets and local .env
if hasattr(st, 'secrets') and 'API_BASE_URL' in st.secrets:
    # Streamlit Cloud deployment
    API_BASE_URL = st.secrets['API_BASE_URL']
else:
    # Local development
    load_dotenv()
    API_BASE_URL = os.getenv("API_BASE_URL", "https://career-guidance-ai-xo2g.onrender.com")

# Page configuration
st.set_page_config(
    page_title="Career Guidance AI",
    page_icon="🎓",
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
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Get welcome message
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{API_BASE_URL}/api/chat",
                    json={"message": "hello"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data.get("session_id")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["response"]
                    })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Welcome! I'm your career guidance assistant. Please make sure the FastAPI backend is running."
            })
    
    if 'complete' not in st.session_state:
        st.session_state.complete = False


def send_message(message: str) -> tuple:
    """Send message to FastAPI backend."""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{API_BASE_URL}/api/chat",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data.get("session_id")
                return data["response"], data["complete"], None
            else:
                return None, False, f"Error: {response.status_code}"
    
    except httpx.ConnectError:
        return None, False, "Cannot connect to backend. Please make sure FastAPI server is running on " + API_BASE_URL
    except Exception as e:
        return None, False, f"Error: {str(e)}"


def reset_conversation():
    """Reset the conversation via API."""
    if st.session_state.session_id:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{API_BASE_URL}/api/restart",
                    json={"session_id": st.session_state.session_id},
                    timeout=10.0
                )
                if response.status_code == 200:
                    # Get new welcome message
                    send_message("hello")
        except Exception as e:
            st.error(f"Error resetting: {e}")
    
    # Reset local state
    st.session_state.messages = []
    st.session_state.complete = False
    st.session_state.session_id = None
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
        if st.button("🔄 Restart Conversation", key="restart", use_container_width=True):
            reset_conversation()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This AI agent provides career guidance for 12th grade students in India.
        This AI agent provides career guidance based on:
        - Your academic stream (PCM/PCB/Commerce/Arts/Vocational)
        - Your interests and aptitudes
        - Indian higher education pathways
        
        **Note**: This is first-level guidance only. 
        Please consult a certified career counselor for final decisions.
        """)
        
        st.markdown("---")
        st.markdown("### API Status")
        try:
            with httpx.Client() as client:
                response = client.get(f"{API_BASE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    st.success("✅ Backend Connected")
                else:
                    st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")
            st.info(f"Expected at: {API_BASE_URL}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input area
    if not st.session_state.complete:
        # User input using Streamlit's chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Get agent response from API
            response, is_complete, error = send_message(prompt)
            
            if error:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ {error}"
                })
            elif response:
                st.session_state.complete = is_complete
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            
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


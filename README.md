# Career Guidance AI Agent

> An intelligent, bilingual career guidance system that helps Indian 12th-grade students discover the perfect career path based on their academic stream and interests.

# Demo Link of AI Agent 

## https://career-guidance-ai-12th-grad-student.streamlit.app/

---

## 📖 What is This Project? (Simple Explanation)

Imagine you're a 12th-grade student in India, confused about what career to choose after school. This project is like having a smart career counselor available 24/7 on your computer or phone!

**In the simplest terms:**
- You open a website
- The AI asks you questions about your favorite subjects, interests, and marks
- Based on your answers, it figures out which stream you're in (like Science, Commerce, Arts, etc.)
- Then it gives you 3 personalized career suggestions that match your stream
- Everything works in both English and Marathi!

**Think of it like this:**
- **Frontend (frontend/)**: The beautiful website you see and interact with (HTML/CSS/JavaScript)
- **Backend (main.py)**: The brain that processes your answers and generates recommendations
- **AI Agent (career_agent/)**: The smart counselor that asks questions and gives advice
- **Data (data.json)**: The database of all careers, questions, and information

---

## 🎯 How Does It Work? (Step by Step)

1. **You open the website** → The frontend (app.py) loads
2. **You select a language** → English or Marathi
3. **You answer questions** → "What are your favorite subjects?"
4. **Your answers go to the backend** → main.py receives them
5. **The AI agent processes** → agent.py figures out your stream
6. **Stream detection happens** → logic.py matches keywords to find your stream
7. **More questions are asked** → Stream-specific questions
8. **Career filtering** → logic.py finds careers matching your stream
9. **AI generates recommendations** → llm.py uses Gemini AI to personalize
10. **You get 3 career options** → Each with details about education, exams, skills

---

## 📁 Project Structure Explained

```
career_guidance_ai/
├── main.py                    # Backend server (API)
├── app.py                     # Streamlit frontend (legacy, optional)
├── frontend/                  # Modern HTML/CSS/JS frontend (NEW!)
│   ├── index.html            # Main HTML file
│   ├── style.css             # All styling
│   ├── script.js             # JavaScript logic
│   └── README.md             # Frontend documentation
├── career_agent/              # The "brain" folder
│   ├── __init__.py           # Makes it a Python package
│   ├── agent.py              # Main conversation manager
│   ├── logic.py              # Stream detection & career matching
│   ├── llm.py                # AI integration (Gemini/Ollama)
│   └── data.json             # All questions and career data
├── requirements.txt           # List of Python packages needed
├── .env                       # Your API keys (you create this)
├── DEPLOYMENT.md              # How to deploy online
└── README.md                  # This file!
```

---

## 📝 Detailed File-by-File Explanation

### 1. `main.py` - The Backend Server

**What it does:** This is the server that runs in the background. It receives requests from the frontend, processes them, and sends back responses.

**Think of it as:** A restaurant kitchen - you (frontend) place an order, the kitchen (backend) prepares it, and you get your food (response).

#### Line-by-Line Explanation:

```python
# Lines 1-4: Documentation comment explaining what this file does
"""
FastAPI Backend: Career Guidance AI Agent
REST API for the career guidance system.
"""

# Lines 6-14: Importing all necessary libraries
from fastapi import FastAPI, HTTPException          # FastAPI framework for creating API
from fastapi.middleware.cors import CORSMiddleware  # Allows frontend to talk to backend
from pydantic import BaseModel                      # For data validation
from typing import Optional                         # For type hints
import os                                           # For environment variables
from dotenv import load_dotenv                      # Loads .env file
from career_agent.agent import CareerGuidanceAgent  # Our main AI agent
import logging                                      # For logging errors/info
import uuid                                         # For creating unique session IDs

# Lines 16-25: Setting up logging (records what happens)
logging.basicConfig(
    level=logging.INFO,                             # Log level: INFO (shows important messages)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler('fastapi_backend.log'),  # Save logs to file
        logging.StreamHandler()                      # Also print to console
    ]
)
logger = logging.getLogger(__name__)                 # Create logger object

# Line 27: Load environment variables from .env file
load_dotenv()

# Lines 29-34: Create FastAPI application
app = FastAPI(
    title="Career Guidance AI API",                 # API title
    description="Bilingual AI-powered career guidance...",  # API description
    version="1.0.0"                                 # Version number
)

# Lines 36-49: CORS (Cross-Origin Resource Sharing) setup
# This allows the frontend (running on different port) to talk to backend
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",                              # Get from environment variable
    "http://localhost:8501,http://localhost:8502"   # Default: local development URLs
).split(",")                                        # Split by comma to get list

app.add_middleware(
    CORSMiddleware,                                 # Add CORS middleware
    allow_origins=allowed_origins,                  # Which websites can access
    allow_credentials=True,                         # Allow cookies/credentials
    allow_methods=["*"],                            # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                            # Allow all headers
)

# Lines 51-60: Data models (structures for requests/responses)
class ChatRequest(BaseModel):
    message: str                                    # User's message
    session_id: Optional[str] = None               # Session ID (optional)
    language: Optional[str] = None                 # Language preference (optional)

class ChatResponse(BaseModel):
    response: str                                   # AI's response
    complete: bool                                 # Is conversation complete?
    session_id: str                                # Session ID
    error: bool = False                            # Any error occurred?

# Lines 62-70: Store agent instances (one per user session)
agents = {}                                        # Dictionary: {session_id: agent_object}

def get_agent(session_id: str) -> CareerGuidanceAgent:
    """Get or create agent for session."""
    if session_id not in agents:                   # If new session
        agents[session_id] = CareerGuidanceAgent() # Create new agent
        logger.info(f"Created new agent for session: {session_id}")
    return agents[session_id]                      # Return agent

# Lines 72-78: Root endpoint (just shows API info)
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Career Guidance AI API",
        "version": "1.0.0",
        "status": "running"
    }

# Lines 80-85: Health check endpoint (checks if server is running)
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "career-guidance-agent"}

# Lines 87-150: Main chat endpoint (handles all conversations)
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages.
    Enforces one-question-at-a-time rule.
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            session_id = str(uuid.uuid4())          # Create unique ID
        else:
            session_id = request.session_id        # Use existing ID
        
        user_input = request.message.strip()       # Remove extra spaces
        
        # Get or create agent for this session
        agent = get_agent(session_id)
        
        # Set language preference if provided
        if request.language:
            agent.set_language(request.language)   # Set to Marathi or English
        
        # Process user input and get response
        response, is_complete = agent.process_input(user_input)
        
        # Return response
        return ChatResponse(
            response=response,
            complete=is_complete,
            session_id=session_id,
            error=False
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")

# Lines 152-170: Restart endpoint (resets conversation)
@app.post("/api/restart", response_model=RestartResponse)
async def restart(request: RestartRequest):
    """Reset conversation and start fresh."""
    session_id = request.session_id
    if session_id in agents:
        agents[session_id].reset()                  # Reset agent
        del agents[session_id]                     # Remove from memory
    return RestartResponse(success=True, message="Conversation reset")

# Lines 172-178: Run server when script is executed
if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))            # Get port from env or use 8000
    uvicorn.run(app, host='0.0.0.0', port=port)    # Start server
```

---

### 2. `frontend/` - The Modern Frontend (HTML/CSS/JavaScript)

**What it does:** This is the beautiful website you see. It handles the user interface, displays questions, and sends your answers to the backend. Built with plain HTML, CSS, and JavaScript - no heavy frameworks!

**Think of it as:** The restaurant dining room - where you sit, see the menu, place orders, and receive your food.

**Files:**
- `index.html`: The main HTML structure with sidebar and chat area
- `style.css`: All the beautiful styling and colors
- `script.js`: JavaScript that handles API calls, session management, and UI updates

**Note:** There's also `app.py` (Streamlit frontend) which is the legacy version. The new `frontend/` folder is the recommended modern frontend.

#### Key Sections Explained:

```python
# Lines 1-4: Documentation
"""
Streamlit Frontend: Career Guidance AI Agent
UI-only application that connects to FastAPI backend.
"""

# Lines 6-10: Import libraries
import streamlit as st          # Streamlit framework (creates web UI)
import httpx                    # HTTP client (sends requests to backend)
import os                       # Environment variables
import logging                  # Logging
from dotenv import load_dotenv  # Load .env file

# Lines 12-21: Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_app.log'),  # Save to file
        logging.StreamHandler()                     # Print to console
    ]
)

# Lines 23-29: Configuration
load_dotenv()                                       # Load .env file
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")  # Backend URL

# Lines 31-37: Page configuration
st.set_page_config(
    page_title="Career Guidance AI",                # Browser tab title
    page_icon="🎓",                                 # Browser tab icon
    layout="wide",                                  # Use full width
    initial_sidebar_state="collapsed"               # Sidebar starts collapsed
)

# Lines 39-54: Custom CSS styling
st.markdown("""<style>...</style>""", unsafe_allow_html=True)  # Add custom styles

# Lines 57-124: Initialize session state
def initialize_session_state():
    """
    Initialize session state variables.
    Session state = data that persists while you use the app
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None          # No session yet
    
    if 'language' not in st.session_state:
        st.session_state.language = "en"           # Default: English
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []              # Empty chat history
        # Send "hello" to get first question
        response = client.post(f"{API_BASE_URL}/api/chat", json={"message": "hello"})
        # Add welcome message to chat

# Lines 127-191: Send message to backend
def send_message(message: str, show_loader: bool = False) -> tuple:
    """
    Send message to FastAPI backend.
    
    Parameters:
    - message: What the user typed
    - show_loader: Show loading spinner (for recommendations)
    
    Returns:
    - (response_text, is_complete, error)
    """
    if show_loader:
        # Show spinner while waiting
        with st.spinner("Generating recommendations..."):
            response = client.post(...)            # Send request
            # Process response
    else:
        # Normal request without spinner
        response = client.post(...)                 # Send request
        # Process response
    
    return response_text, is_complete, error

# Lines 193-210: Reset conversation
def reset_conversation():
    """Reset the conversation via API."""
    # Send restart request to backend
    # Clear local messages
    # Re-initialize

# Lines 212-380: Main application
def main():
    """Main Streamlit application."""
    initialize_session_state()                      # Setup
    
    # Display header
    st.markdown("""<div class="main-header">...</div>""")
    
    # Sidebar with controls
    with st.sidebar:
        # Language switch buttons
        # Restart button
        # About section
        # API status
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):     # Show as chat bubble
            st.markdown(message["content"])         # Display text
    
    # Input area
    if prompt := st.chat_input("Type your message..."):
        # User typed something
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Detect if generating recommendations
        is_generating_recommendations = ...
        
        # Send to backend
        response, is_complete, error = send_message(prompt, show_loader=...)
        
        # Add response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()                                  # Refresh page

if __name__ == '__main__':
    main()                                          # Run app
```

---

### 3. `career_agent/agent.py` - The Conversation Manager

**What it does:** This is the "brain" that manages the entire conversation. It decides what question to ask next, processes your answers, and coordinates everything.

**Think of it as:** The head waiter who manages your entire dining experience - greets you, takes your order, coordinates with kitchen, serves food.

#### Key Sections Explained:

```python
# Lines 16-25: Conversation phases (like steps in a journey)
class CareerGuidanceAgent:
    PHASE_WELCOME = "welcome"                       # Step 1: Greeting
    PHASE_GENERAL_QUESTIONS = "general_questions"   # Step 2: Basic questions
    PHASE_STREAM_CONFIRMATION = "stream_confirmation"  # Step 3: Confirm stream
    PHASE_STREAM_QUESTIONS = "stream_questions"    # Step 4: Stream-specific questions
    PHASE_RECOMMENDATIONS = "recommendations"       # Step 5: Generate recommendations
    PHASE_COMPLETE = "complete"                    # Step 6: Done!

# Lines 27-40: Initialize agent
def __init__(self):
    self.profile = StudentProfile()                # Store student info
    self.stream_detector = StreamDetector()         # Detect stream
    self.recommender = CareerRecommender()         # Find careers
    self.llm = LLMProvider()                       # AI integration
    self.phase = self.PHASE_WELCOME                # Start at welcome
    self.current_question_index = 0                # First question
    self.language = "en"                           # Default: English
    self.language_manually_set = False             # Not manually set yet
    
    # Load questions and career data from JSON file
    data_file = os.path.join(os.path.dirname(__file__), "data.json")
    with open(data_file, "r", encoding="utf-8") as f:
        self.data = json.load(f)

# Lines 42-62: Get question text in correct language
def _get_question_text(self, question: Dict) -> str:
    """Get question text in current language."""
    if not question:
        return self._get_welcome_message()         # Fallback if no question
    
    # Choose language key
    key = "text_mr" if self.language == "mr" else "text_en"
    text = question.get(key, "")                   # Get text in that language
    
    # Fallback to English if Marathi not found
    if not text and self.language == "mr":
        text = question.get("text_en", "")
    
    return text

# Lines 64-71: Auto-detect language from user input
def _detect_language(self, text: str):
    """Detect and set language from first user input."""
    if self.language == "en":                      # Only detect once
        detected = self.stream_detector.detect_language(text)  # Detect
        self.language = detected                    # Set language
        self.profile.set_language(detected)         # Save to profile

# Lines 73-81: Manually set language (from UI button)
def set_language(self, language: str):
    """Manually set language preference."""
    if language in ["en", "mr"]:
        self.language = language
        self.profile.set_language(language)
        self.language_manually_set = True          # Mark as manually set

# Lines 83-88: Welcome message
def _get_welcome_message(self) -> str:
    """Get welcome message in current language."""
    if self.language == "mr":
        return "नमस्कार! मी तुमचा करिअर मार्गदर्शन सहाय्यक आहे..."
    else:
        return "Hello! I'm your career guidance assistant..."

# Lines 90-95: Get next general question
def _get_next_general_question(self) -> Optional[Dict]:
    """Get next general question."""
    questions = self.data["questions"]["general"]  # Get all general questions
    if self.current_question_index < len(questions):
        return questions[self.current_question_index]  # Return current question
    return None                                     # No more questions

# Lines 456-470: Process user input (MAIN FUNCTION)
def process_input(self, user_input: str) -> Tuple[str, bool]:
    """
    Process user input and return response.
    This is the MAIN function that handles everything!
    """
    user_input = user_input.strip()                # Remove spaces
    
    # PHASE 1: Welcome
    if self.phase == self.PHASE_WELCOME:
        # Detect language if not manually set
        if not self.language_manually_set:
            self._detect_language(user_input)
        
        # Move to next phase
        self.phase = self.PHASE_GENERAL_QUESTIONS
        self.current_question_index = 0
        
        # Get and return first question
        question = self._get_next_general_question()
        return self._get_question_text(question), False
    
    # PHASE 2: General Questions
    if self.phase == self.PHASE_GENERAL_QUESTIONS:
        # Save answer to profile
        question_id = self.data["questions"]["general"][self.current_question_index]["id"]
        self.profile.update(question_id, user_input)
        
        # Move to next question
        self.current_question_index += 1
        
        # Get next question
        next_question = self._get_next_general_question()
        if next_question:
            return self._get_question_text(next_question), False
        else:
            # All general questions done, detect stream
            self.phase = self.PHASE_STREAM_CONFIRMATION
            detected = self.stream_detector.detect_stream(...)
            # Ask to confirm stream
    
    # PHASE 3: Stream Confirmation
    if self.phase == self.PHASE_STREAM_CONFIRMATION:
        # User confirms or specifies stream
        # Move to stream-specific questions
    
    # PHASE 4: Stream Questions
    if self.phase == self.PHASE_STREAM_QUESTIONS:
        # Ask stream-specific questions
        # Save answers
    
    # PHASE 5: Generate Recommendations
    if self.phase == self.PHASE_RECOMMENDATIONS:
        recommendations = self._generate_recommendations()  # Generate 3 careers
        response = self._format_recommendations_response(recommendations)
        self.phase = self.PHASE_COMPLETE
        return response, True                        # Conversation complete!
```

---

### 4. `career_agent/logic.py` - Stream Detection & Career Matching

**What it does:** This file contains the "smart logic" - it detects which stream you're in and finds careers that match your stream.

**Think of it as:** The matchmaker who finds the perfect careers for you based on your stream.

#### Key Classes Explained:

```python
# Lines 15-40: StreamDetector class
class StreamDetector:
    """Detects student stream from academic inputs."""
    
    # Keywords for each stream (in English and Marathi)
    STREAM_KEYWORDS = {
        "PCM": {
            "en": ["physics", "chemistry", "mathematics", "engineering"],
            "mr": ["भौतिकशास्त्र", "रसायनशास्त्र", "गणित"]
        },
        "PCB": {
            "en": ["biology", "medical", "doctor", "neet"],
            "mr": ["जीवशास्त्र", "वैद्यकीय", "डॉक्टर"]
        },
        # ... more streams
    }
    
    # Lines 42-49: Detect language
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language from text."""
        try:
            lang = detect(text)                     # Use langdetect library
            return "mr" if lang == "mr" else "en"  # Return Marathi or English
        except:
            return "en"                             # Default: English
    
    # Lines 51-86: Detect stream
    @staticmethod
    def detect_stream(favourite_subjects, weak_subjects, interests) -> Optional[str]:
        """
        Detect stream from student inputs.
        Works by counting keyword matches!
        """
        # Combine all text
        text = f"{favourite_subjects} {weak_subjects} {interests}".lower()
        
        # Score each stream
        stream_scores = {stream: 0 for stream in STREAM_KEYWORDS.keys()}
        
        # Count matches for each stream
        for stream, keywords in STREAM_KEYWORDS.items():
            for lang in ["en", "mr"]:
                for keyword in keywords[lang]:
                    if keyword in text:             # Found keyword!
                        stream_scores[stream] += 1  # Add point
        
        # Find stream with highest score
        max_score = max(stream_scores.values())
        if max_score >= 2:                          # Need at least 2 matches
            detected_stream = max(stream_scores, key=stream_scores.get)
            return detected_stream
        return None                                 # Not sure, ask user

# Lines 130-229: CareerRecommender class
class CareerRecommender:
    """Generates stream-aligned career recommendations."""
    
    def filter_careers(self, stream: str, student_profile: Dict) -> List[Dict]:
        """
        Filter careers based on student profile.
        Returns exactly 3 careers!
        """
        # Get all careers for this stream
        careers = self.get_stream_careers(stream)
        
        # Score each career
        filtered = []
        for career in careers:
            score = 0
            
            # Match interests
            if "tech" in interests and "engineering" in career_name:
                score += 2
            
            # Match marks range
            if "80-90" in marks_range:
                score += 1
            
            # Match stream-specific aptitude
            if stream == "PCM" and math_aptitude == "high":
                score += 1.5
            
            filtered.append((career, score))        # Store with score
        
        # Sort by score (highest first)
        filtered.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3
        return [career for career, score in filtered[:3]]

# Lines 253-307: StudentProfile class
class StudentProfile:
    """Manages student profile data throughout the conversation."""
    
    def __init__(self):
        self.data = {
            "favourite_subjects": "",              # Empty initially
            "weak_subjects": "",
            "marks_range": "",
            "interests": "",
            "stream": None,                        # Not detected yet
            "stream_aptitude": {},                 # Stream-specific answers
            "language": "en"                       # Default language
        }
    
    def update(self, field: str, value: str):
        """Update a field in the profile."""
        if field in self.data:
            self.data[field] = value               # Save answer
    
    def set_stream(self, stream: str):
        """Set confirmed stream."""
        self.data["stream"] = stream              # Save stream
```

---

### 5. `career_agent/llm.py` - AI Integration

**What it does:** This file connects to Google's Gemini AI to generate personalized career recommendations. If Gemini fails, it falls back to Ollama.

**Think of it as:** The expert consultant who gives personalized advice using AI.

#### Key Sections Explained:

```python
# Lines 31-65: LLMProvider class
class LLMProvider:
    """Manages LLM interactions with automatic fallback."""
    
    def __init__(self):
        # Get API keys from environment
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        
        self.conversation_history = []            # Store chat history
        self.use_gemini = True                    # Try Gemini first
        self._initialize_gemini()                  # Setup Gemini
    
    def _initialize_gemini(self):
        """Initialize Gemini API if key is available."""
        if not self.gemini_api_key:
            self.use_gemini = False                # No key, use Ollama
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_llm = ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=self.gemini_api_key,
                temperature=0.7                    # Creativity level
            )
            self.use_gemini = True
        except:
            self.use_gemini = False               # Failed, use Ollama
    
    # Lines 159-176: Generate response (main function)
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response with automatic fallback.
        Tries Gemini first, falls back to Ollama if needed.
        """
        if self.use_gemini:
            try:
                return self._call_gemini(prompt, system_prompt)  # Try Gemini
            except:
                self.use_gemini = False           # Failed, switch to Ollama
                return self._call_ollama(prompt, system_prompt)  # Use Ollama
        else:
            return self._call_ollama(prompt, system_prompt)  # Use Ollama
```

---

### 6. `career_agent/data.json` - The Database

**What it does:** This JSON file contains ALL the questions and career information. It's like a big encyclopedia of careers and questions.

**Structure:**
```json
{
  "streams": {
    "PCM": {
      "name": "Science (PCM)",
      "subjects": ["Physics", "Chemistry", "Mathematics"],
      "careers": [
        {
          "name": "Engineering",
          "pathway": "JEE Main -> B.Tech -> M.Tech",
          "entrance_exams": ["JEE Main", "JEE Advanced"],
          "skills": ["Problem-solving", "Mathematical aptitude"],
          "risks": "High competition"
        }
      ]
    }
  },
  "questions": {
    "general": [
      {
        "id": "favourite_subjects",
        "text_en": "What are your favourite subjects?",
        "text_mr": "तुमचे आवडते विषय कोणते?"
      }
    ],
    "stream_specific": {
      "PCM": [
        {
          "id": "math_aptitude",
          "text_en": "How comfortable are you with mathematics?",
          "text_mr": "गणितासाठी तुम्ही किती सोयीस्कर आहात?"
        }
      ]
    }
  }
}
```

---

### 7. `career_agent/__init__.py` - Package Initializer

**What it does:** This file makes `career_agent` a Python package so we can import it.

**Content:** Just a comment (empty file is fine too)

---

### 8. `requirements.txt` - Dependencies List

**What it does:** Lists all Python packages needed to run this project.

**Key packages:**
- `streamlit` - For the frontend website
- `fastapi` - For the backend API
- `uvicorn` - Server to run FastAPI
- `httpx` - HTTP client for making requests
- `langchain` - AI conversation management
- `google-generativeai` - Gemini AI integration
- `python-dotenv` - Load .env file
- `langdetect` - Detect language from text

---

## 🔄 How Everything Works Together (Flow Diagram)

```
User opens website (app.py)
    ↓
User selects language (Marathi/English)
    ↓
User types answer
    ↓
app.py sends HTTP request to main.py
    ↓
main.py receives request
    ↓
main.py calls agent.process_input()
    ↓
agent.py processes answer
    ↓
logic.py detects stream / filters careers
    ↓
llm.py generates personalized recommendations (if needed)
    ↓
agent.py formats response
    ↓
main.py returns JSON response
    ↓
app.py displays response to user
    ↓
User sees next question or recommendations!
```

---

## 🎯 Key Features Explained Simply

### 1. **Bilingual Support**
- System detects if you type in Marathi or English
- All questions and responses switch to your language
- You can manually switch using sidebar buttons

### 2. **Stream Detection**
- System looks for keywords in your answers
- Example: If you say "physics, chemistry, math" → PCM stream
- Example: If you say "biology, medical" → PCB stream

### 3. **One Question at a Time**
- System waits for your answer before asking next question
- This makes it feel like a real conversation
- No overwhelming list of questions!

### 4. **Stream-Aligned Recommendations**
- **CRITICAL**: System NEVER suggests careers outside your stream
- Example: Arts student will NEVER get Engineering recommendation
- This is enforced by rule-based filtering

### 5. **Exactly 3 Recommendations**
- System always returns exactly 3 career options
- Each has: pathway, exams, skills, risks
- Personalized using Gemini AI

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### Step 2: Install Python

Make sure you have Python 3.8 or higher:
```bash
python --version
```

### Step 3: Setup the Project

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Add Your API Key

Create a file named `.env` in the project folder:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Step 5: Run the Application

**Terminal 1 - Start Backend:**
```bash
python main.py
```

**Terminal 2 - Start Frontend (Modern HTML/CSS/JS):**
```bash
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080` in your browser! 🎉

**Alternative - Streamlit Frontend (Legacy):**
```bash
streamlit run app.py
```
This opens at `http://localhost:8501`

---

## 📋 What Questions Will Be Asked?

### General Questions (Everyone)
1. What are your favorite subjects?
2. Which subjects do you find difficult?
3. What's your marks range?
4. What are your interests?

### Stream-Specific Questions

**For Science (PCM):**
- How comfortable are you with mathematics?
- Are you interested in engineering?

**For Science (PCB):**
- How interested are you in biology?
- Are you considering a medical career?

**For Commerce:**
- Are you interested in business?
- How comfortable are you with accounting?

**For Arts:**
- How creative are you?
- How strong are your communication skills?

**For Vocational:**
- What practical skills do you have?
- Are you interested in certifications?

---

## 🎓 Supported Streams

- **PCM** (Physics, Chemistry, Mathematics) → Engineering, Architecture, Data Science
- **PCB** (Physics, Chemistry, Biology) → Medical, Pharmacy, Biotechnology
- **Commerce** → CA, Business Administration, Finance
- **Arts** → Psychology, Law, Journalism
- **Vocational** → Skill-based careers, Technical trades

---

## 🛠️ Troubleshooting

### "Can't connect to backend"
- Make sure `main.py` is running in Terminal 1
- Check it says "Uvicorn running on http://0.0.0.0:8000"

### "API Key Error"
- Check your `.env` file exists
- Verify API key is correct (no extra spaces)

### "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## 🔒 Privacy & Safety

- **Your data stays private**: All conversations stored only in your session
- **No personal information collected**: Only academic interests
- **Disclaimer**: This is guidance, not professional counseling
- **Always verify**: Confirm decisions with certified human counselor

---

## 📚 Technical Details

**Technologies Used:**
- **FastAPI**: Modern Python web framework for backend
- **Streamlit**: Easy-to-use framework for frontend
- **LangChain**: AI conversation management
- **Google Gemini**: AI for generating recommendations
- **Rule-based filtering**: Ensures accuracy

---

## ⚠️ Important Notes

1. **This is guidance, not a decision**: Always consult a real career counselor
2. **Stream alignment is strict**: Never suggests careers outside your stream
3. **Exactly 3 recommendations**: Always 3 options, no more, no less
4. **One question at a time**: Waits for your answer before proceeding

---

## 📖 Deployment

Want to share this online? See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step guide to deploy on Streamlit Cloud.

---

## 🤝 Need Help?

- Check troubleshooting section above
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Check code comments for technical details
- Open an issue on GitHub if you find a bug

---

## 🎉 Ready to Start?

1. Follow Quick Start guide above
2. Start both terminals
3. Open your browser
4. Begin your career journey!

---

**Made for Indian students**

*Remember: Your career is a journey, not a destination. Take your time, explore your options, and always seek guidance from experienced professionals.*

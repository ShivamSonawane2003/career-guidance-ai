# Career Guidance AI Agent

A production-ready, bilingual (Marathi + English) AI-powered career guidance system for Indian 12th-grade students. This system provides accurate, stream-aligned career recommendations following Indian higher education pathways.

## 🎯 Key Features

- **FastAPI Backend + Streamlit Frontend**: Modern architecture with separated concerns
- **Bilingual Support**: Automatically detects and responds in Marathi or English
- **Stream Detection**: Identifies student's academic stream (PCM, PCB, Commerce, Arts, Vocational)
- **Stream-Aligned Recommendations**: NEVER suggests careers outside the student's stream
- **Structured Conversation**: Asks exactly one question at a time, waits for user input
- **Rule-Based Filtering**: Ensures accuracy with rule-based career filtering before LLM explanation
- **Dual LLM Support**: Primary (Gemini API) with automatic fallback to Ollama
- **Production-Grade**: Comprehensive error handling, testing, and validation
- **Proper Formatting**: Career recommendations displayed with clear line breaks and structure

## 📋 Prerequisites

- Python 3.8 or higher
- Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- (Optional) Ollama installed locally for fallback (if Gemini unavailable)

## 🚀 Quick Start

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
API_BASE_URL=http://localhost:8000
```

### 4. Run the Application

**Terminal 1 - Start Backend:**
```bash
python main.py
# OR
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
career_guidance_ai/
├── main.py                    # FastAPI backend (API server)
├── app.py                     # Streamlit frontend (UI only)
├── career_agent/              # Core agent package
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Main agent orchestration
│   ├── logic.py              # Stream detection & recommendations
│   ├── llm.py                # LLM provider (Gemini + Ollama)
│   └── data.json             # Career data and questions
├── test_agent.py              # Unit tests
├── test_conversation.py       # Integration tests
├── setup_check.py            # Setup verification script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── start_backend.bat/sh      # Backend startup scripts
├── start_frontend.bat/sh     # Frontend startup scripts
├── README.md                 # This file
└── QUICKSTART.md             # Quick start guide
```

## 📚 Code Documentation

### Backend Files

#### `main.py` - FastAPI Backend Server

**Purpose**: REST API server that handles all business logic and agent orchestration.

**Key Components**:
- **FastAPI App**: Main application instance with CORS middleware
- **Session Management**: Stores agent instances per session ID
- **API Endpoints**:
  - `GET /` - Root endpoint (API info)
  - `GET /health` - Health check
  - `POST /api/chat` - Handle chat messages
  - `POST /api/restart` - Reset conversation

**Key Functions**:
- `get_agent(session_id)`: Gets or creates agent instance for session
- `chat(request)`: Processes user messages, returns agent response
- `restart(request)`: Resets agent state for a session

**Data Models**:
- `ChatRequest`: Request model with message and optional session_id
- `ChatResponse`: Response model with response, complete flag, and session_id
- `RestartRequest/Response`: Models for restart endpoint

**How it works**:
1. Receives HTTP POST request with user message
2. Gets or creates agent instance for session
3. Calls `agent.process_input()` to get response
4. Returns JSON response with agent output

**Dependencies**: FastAPI, uvicorn, career_agent package

---

#### `app.py` - Streamlit Frontend

**Purpose**: User interface that communicates with FastAPI backend via HTTP.

**Key Components**:
- **Streamlit UI**: Chat interface with sidebar controls
- **Session State**: Manages conversation state and session ID
- **HTTP Client**: Uses httpx to communicate with backend

**Key Functions**:
- `initialize_session_state()`: Sets up Streamlit session state variables
- `send_message(message)`: Sends message to FastAPI backend via POST request
- `reset_conversation()`: Resets conversation via API call
- `main()`: Main Streamlit application function

**UI Components**:
- Header with gradient styling
- Sidebar with restart button and API status
- Chat message display using `st.chat_message()`
- Chat input using `st.chat_input()`
- Footer with disclaimer

**How it works**:
1. Initializes session state on first load
2. Gets welcome message from backend API
3. Displays chat messages in conversation format
4. On user input, sends POST request to `/api/chat`
5. Displays response and updates UI

**Configuration**:
- `API_BASE_URL`: Backend URL (default: http://localhost:8000)
- Set via environment variable or `.env` file

**Dependencies**: streamlit, httpx, dotenv

---

### Core Agent Package (`career_agent/`)

#### `career_agent/__init__.py`

**Purpose**: Python package initialization file.

**Content**: Empty file that makes `career_agent` a Python package, allowing imports like `from career_agent.agent import CareerGuidanceAgent`.

---

#### `career_agent/agent.py` - Main Agent Orchestration

**Purpose**: Orchestrates the entire conversation flow, manages phases, and coordinates all components.

**Key Classes**:
- **CareerGuidanceAgent**: Main agent class that manages conversation

**Conversation Phases**:
1. `PHASE_WELCOME`: Initial welcome message
2. `PHASE_GENERAL_QUESTIONS`: Asking general questions (subjects, marks, interests)
3. `PHASE_STREAM_CONFIRMATION`: Confirming detected stream
4. `PHASE_STREAM_QUESTIONS`: Asking stream-specific questions
5. `PHASE_RECOMMENDATIONS`: Generating and displaying recommendations
6. `PHASE_COMPLETE`: Conversation finished

**Key Methods**:
- `__init__()`: Initializes agent with profile, detector, recommender, and LLM
- `process_input(user_input)`: Main method that processes user input and returns response
- `_get_question_text(question)`: Gets question text in current language (Marathi/English)
- `_detect_language(text)`: Detects language from first user input
- `_get_welcome_message()`: Returns welcome message in current language
- `_get_next_general_question()`: Gets next question from general questions list
- `_get_stream_questions(stream)`: Gets stream-specific questions
- `_generate_stream_confirmation_prompt(detected_stream)`: Creates stream confirmation prompt
- `_generate_recommendations()`: Generates 3 career recommendations using rule-based filtering
- `_format_recommendations_response(recommendations)`: Formats recommendations with proper line breaks
- `reset()`: Resets all agent state to initial state

**State Management**:
- `self.profile`: StudentProfile instance storing all student data
- `self.phase`: Current conversation phase
- `self.current_question_index`: Index of current question
- `self.language`: Current language ("en" or "mr")
- `self.data`: Loaded questions and career data from JSON

**Critical Rules Enforced**:
- One question at a time (never asks multiple questions)
- Waits for user input before proceeding
- Never auto-fills or assumes data
- Validates stream alignment before recommendations

**Dependencies**: logic.py, llm.py, data.json

---

#### `career_agent/logic.py` - Core Business Logic

**Purpose**: Contains stream detection, validation, and career recommendation logic.

**Key Classes**:

1. **StreamDetector**:
   - Detects student's academic stream from inputs
   - Validates stream alignment for recommendations
   - Language detection

   **Key Methods**:
   - `detect_language(text)`: Detects Marathi or English
   - `detect_stream(favourite_subjects, weak_subjects, interests)`: Detects stream using keyword matching
   - `validate_stream_alignment(career_name, student_stream, career_data)`: CRITICAL - Prevents cross-stream recommendations

   **Stream Keywords**: Dictionary mapping stream codes to keywords in English and Marathi

2. **CareerRecommender**:
   - Filters and scores careers based on student profile
   - Returns exactly 3 stream-aligned careers
   - Formats recommendations with all required details

   **Key Methods**:
   - `__init__(data_file)`: Loads career data from JSON
   - `get_stream_careers(stream)`: Gets all careers for a stream
   - `filter_careers(stream, student_profile)`: Rule-based filtering with scoring
   - `format_recommendation(career, stream, language)`: Formats single career recommendation

   **Filtering Logic**:
   - Scores careers based on interests matching
   - Considers marks range
   - Matches stream-specific aptitudes
   - Ensures exactly 3 careers returned

3. **StudentProfile**:
   - Manages student data throughout conversation
   - Stores all collected information

   **Key Methods**:
   - `update(field, value)`: Updates a profile field
   - `set_stream(stream)`: Sets confirmed stream
   - `set_language(language)`: Sets conversation language
   - `get(field, default)`: Gets field value
   - `is_complete()`: Checks if profile has minimum required data
   - `reset()`: Resets profile to initial state
   - `to_dict()`: Returns profile as dictionary

**Data Structure**:
- Profile fields: favourite_subjects, weak_subjects, marks_range, interests, stream, stream_aptitude, personality_traits, budget_preference, language

**Dependencies**: langdetect, data.json

---

#### `career_agent/llm.py` - LLM Provider

**Purpose**: Manages LLM interactions with automatic fallback from Gemini to Ollama.

**Key Classes**:
- **LLMProvider**: Manages LLM with automatic fallback

**Key Methods**:
- `__init__()`: Initializes with API keys and model names from environment
- `_initialize_gemini()`: Sets up Gemini API if key available
- `_call_gemini(prompt, system_prompt)`: Calls Gemini API via LangChain
- `_call_ollama(prompt, system_prompt)`: Calls Ollama API as fallback
- `_convert_to_ollama_messages(messages)`: Converts LangChain messages to Ollama format
- `generate(prompt, system_prompt)`: Main method - tries Gemini, falls back to Ollama
- `clear_history()`: Clears conversation history
- `get_history()`: Returns conversation history

**Fallback Mechanism**:
1. Tries Gemini API first
2. On failure, automatically switches to Ollama
3. Maintains conversation history across fallback
4. Logs all fallback events

**Configuration** (from .env):
- `GEMINI_API_KEY`: Google Gemini API key
- `GEMINI_MODEL`: Model name (default: gemini-pro)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Ollama model name (default: llama2)

**Dependencies**: langchain, google-generativeai, ollama

---

#### `career_agent/data.json` - Career Data and Questions

**Purpose**: Contains all career information, questions, and stream data.

**Structure**:

1. **streams**: Object containing all 5 streams
   - Each stream has: name, subjects, careers array
   - Each career has: name, pathway, entrance_exams, skills, risks

2. **questions**: Object containing all questions
   - **general**: Array of 4 general questions (favourite_subjects, weak_subjects, marks_range, interests)
   - **stream_specific**: Object with questions for each stream
     - PCM: math_aptitude, engineering_interest
     - PCB: biology_interest, medical_interest
     - Commerce: business_interest, accounting_aptitude
     - Arts: creativity, communication
     - Vocational: practical_skills, certification_interest

**Question Format**:
- Each question has: `id`, `text_en`, `text_mr`

**Career Format**:
- `name`: Career name
- `pathway`: Education pathway (e.g., "JEE Main -> B.Tech -> M.Tech")
- `entrance_exams`: Array of exam names
- `skills`: Array of required skills
- `risks`: String describing risks/limitations

**Streams Covered**:
- PCM (Physics, Chemistry, Mathematics): Engineering, Architecture, Data Science
- PCB (Physics, Chemistry, Biology): Medical, Pharmacy, Biotechnology
- Commerce: CA, Business Administration, Finance & Banking
- Arts: Psychology, Law, Journalism
- Vocational: Skill-based certifications, Technical trades, Hospitality

**Note**: This file is the single source of truth for all career recommendations. To add new careers or modify pathways, edit this file.

---

### Test Files

#### `test_agent.py` - Unit Test Suite

**Purpose**: Comprehensive unit tests for all components.

**Test Classes**:

1. **TestStreamDetector**: Tests stream detection
   - `test_detect_pcm()`: Verifies PCM detection
   - `test_detect_pcb()`: Verifies PCB detection
   - `test_detect_commerce()`: Verifies Commerce detection
   - `test_detect_arts()`: Verifies Arts detection
   - `test_detect_vocational()`: Verifies Vocational detection
   - `test_validate_stream_alignment()`: CRITICAL - Tests no cross-stream recommendations

2. **TestCareerRecommender**: Tests recommendation engine
   - `test_get_stream_careers()`: Tests getting careers for stream
   - `test_filter_careers_pcm()`: Tests PCM filtering
   - `test_filter_careers_pcb()`: Tests PCB filtering
   - `test_filter_careers_commerce()`: Tests Commerce filtering
   - `test_exactly_three_careers()`: Ensures exactly 3 careers returned

3. **TestCareerGuidanceAgent**: Tests agent conversation flow
   - `test_welcome_phase()`: Tests welcome message
   - `test_one_question_at_a_time()`: CRITICAL - Ensures one question at a time
   - `test_pcm_conversation_flow()`: Full PCM conversation test
   - `test_pcb_conversation_flow()`: Full PCB conversation test
   - `test_commerce_conversation_flow()`: Full Commerce conversation test
   - `test_restart_functionality()`: Tests reset functionality
   - `test_empty_input_handling()`: Tests error handling
   - `test_invalid_stream_handling()`: Tests invalid input handling

4. **TestStreamAlignmentRules**: CRITICAL validation tests
   - `test_arts_no_engineering()`: Arts should NEVER recommend Engineering
   - `test_commerce_no_medical()`: Commerce should NEVER recommend Medical
   - `test_pcm_no_medical()`: PCM should NEVER recommend Medical without bridge
   - `test_pcb_no_core_engineering()`: PCB should NOT recommend core Engineering

**How to Run**:
```bash
python test_agent.py
```

**Expected Output**: All 23 tests should pass

---

#### `test_conversation.py` - Integration Tests

**Purpose**: Tests actual conversation flows to verify end-to-end accuracy.

**Test Functions**:
- `test_pcm_conversation()`: Simulates full PCM conversation and verifies recommendations
- `test_pcb_conversation()`: Simulates full PCB conversation and verifies recommendations
- `test_commerce_conversation()`: Simulates full Commerce conversation and verifies recommendations
- `test_arts_conversation()`: Simulates full Arts conversation and verifies recommendations

**What it Tests**:
- Correct stream detection
- Proper question flow
- Accurate recommendations
- No cross-stream recommendations
- Exactly 3 careers returned

**How to Run**:
```bash
python test_conversation.py
```

---

### Utility Files

#### `setup_check.py` - Setup Verification Script

**Purpose**: Verifies that the environment is properly set up.

**Functions**:
- `check_python_version()`: Verifies Python 3.8+
- `check_virtual_env()`: Checks if virtual environment is activated
- `check_dependencies()`: Verifies all required packages are installed
- `check_env_file()`: Checks if .env file exists and has API key
- `check_data_files()`: Verifies all required files exist

**How to Run**:
```bash
python setup_check.py
```

**Output**: Shows [OK] for passed checks, [X] for failed checks, [!] for warnings

---

#### `start_backend.bat` / `start_backend.sh` - Backend Startup Scripts

**Purpose**: Convenience scripts to start the FastAPI backend.

**Windows** (`start_backend.bat`):
```batch
python main.py
```

**Linux/Mac** (`start_backend.sh`):
```bash
python main.py
```

**Usage**: Double-click or run from terminal

---

#### `start_frontend.bat` / `start_frontend.sh` - Frontend Startup Scripts

**Purpose**: Convenience scripts to start the Streamlit frontend.

**Windows** (`start_frontend.bat`):
```batch
streamlit run app.py
```

**Linux/Mac** (`start_frontend.sh`):
```bash
streamlit run app.py
```

**Usage**: Double-click or run from terminal

---

### Configuration Files

#### `requirements.txt` - Python Dependencies

**Purpose**: Lists all required Python packages with versions.

**Key Dependencies**:
- `streamlit==1.31.0`: Frontend framework
- `fastapi==0.109.0`: Backend framework
- `uvicorn==0.27.0`: ASGI server for FastAPI
- `httpx==0.27.2`: HTTP client for frontend
- `langchain==0.1.20`: LLM orchestration
- `langchain-google-genai==1.0.3`: Gemini integration
- `google-generativeai==0.5.2`: Google AI SDK
- `ollama==0.3.1`: Ollama client
- `langdetect==1.0.9`: Language detection
- `python-dotenv==1.0.0`: Environment variable management
- `pydantic==2.9.2`: Data validation

**Installation**:
```bash
pip install -r requirements.txt
```

---

#### `.env.example` - Environment Variables Template

**Purpose**: Template showing required environment variables.

**Variables**:
- `GEMINI_API_KEY`: Your Gemini API key (required)
- `GEMINI_MODEL`: Model name (default: gemini-2.5-flash)
- `OLLAMA_BASE_URL`: Ollama server URL (optional)
- `OLLAMA_MODEL`: Ollama model name (optional)
- `PORT`: Backend port (default: 8000)
- `API_BASE_URL`: Backend URL for frontend (default: http://localhost:8000)

**Usage**: Copy to `.env` and fill in your values

---

## 🔄 How Files Interact

### Request Flow

```
User Input (Streamlit UI)
    ↓
app.py (send_message function)
    ↓ HTTP POST /api/chat
main.py (chat endpoint)
    ↓
CareerGuidanceAgent.process_input()
    ↓
StreamDetector.detect_stream()
    ↓
CareerRecommender.filter_careers()
    ↓
LLMProvider.generate() (if needed)
    ↓
Response formatted
    ↓
main.py returns JSON
    ↓
app.py displays response
```

### Component Dependencies

```
main.py
  └── career_agent.agent.CareerGuidanceAgent

app.py
  └── httpx (HTTP client)
      └── main.py (FastAPI backend)

career_agent/agent.py
  ├── career_agent.logic.StreamDetector
  ├── career_agent.logic.CareerRecommender
  ├── career_agent.logic.StudentProfile
  ├── career_agent.llm.LLMProvider
  └── career_agent/data.json

career_agent/logic.py
  └── career_agent/data.json

career_agent/llm.py
  ├── langchain (Gemini)
  └── ollama (Fallback)
```

## 🧪 Testing

### Run All Tests

```bash
# Unit tests
python test_agent.py

# Integration tests
python test_conversation.py
```

### Test Coverage

- ✅ Stream detection for all 5 streams
- ✅ Career filtering and recommendations
- ✅ Conversation flow for all streams
- ✅ Stream alignment validation (no cross-stream recommendations)
- ✅ One-question-at-a-time enforcement
- ✅ Error handling
- ✅ Restart functionality

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
API_BASE_URL=http://localhost:8000
PORT=8000
```

### API Configuration

- **Backend Port**: Set via `PORT` in `.env` (default: 8000)
- **Frontend Port**: Set via Streamlit CLI: `streamlit run app.py --server.port 8501`
- **API Base URL**: Set via `API_BASE_URL` in `.env`

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ⚠️ Critical Rules (Non-Negotiable)

1. **No Cross-Stream Recommendations**: 
   - Arts → Never suggests Engineering/Medical
   - Commerce → Never suggests Medical/Core Engineering
   - PCM → Never suggests Medical without bridge explanation
   - PCB → Never suggests Core Engineering

2. **One Question at a Time**: Agent waits for user input before proceeding

3. **Exactly 3 Careers**: Each recommendation returns exactly 3 options

4. **Indian Education Context**: All pathways follow Indian higher education system

## 🐛 Troubleshooting

### Backend Not Starting
- Check if port 8000 is available
- Verify `.env` file exists and has correct values
- Check Python version: `python --version` (needs 3.8+)

### Frontend Can't Connect
- Verify backend is running: `http://localhost:8000/health`
- Check `API_BASE_URL` in `.env`
- Check firewall settings

### Gemini API Errors
- Verify API key is correct
- Check API quota/limits
- System will automatically fallback to Ollama if configured

### Import Errors
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`
- Check Python path

## 🚀 Deployment

### Deployment Options

We provide deployment guides for multiple platforms:

1. **[DEPLOYMENT.md](DEPLOYMENT.md)**: Deploy to Streamlit Cloud with GitHub (Cloud-based, easiest)
2. **[DEPLOYMENT_UBUNTU.md](DEPLOYMENT_UBUNTU.md)**: Deploy on Ubuntu Server with Nginx (Self-hosted, full control)

### Quick Deployment (Streamlit Cloud)

**Quick Steps**:
1. Push code to GitHub
2. Deploy backend to Railway/Render/Heroku
3. Deploy frontend to Streamlit Cloud
4. Configure secrets and environment variables

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step guide.**

### Self-Hosted Deployment (Ubuntu + Nginx)

**Quick Steps**:
1. Setup Ubuntu server
2. Install dependencies (Python, Nginx)
3. Clone repository and setup virtual environment
4. Configure systemd services for backend and frontend
5. Configure Nginx as reverse proxy
6. Setup SSL certificates (optional)

**See [DEPLOYMENT_UBUNTU.md](DEPLOYMENT_UBUNTU.md) for complete step-by-step guide.**

## 📝 License

This project is built for educational purposes. Ensure compliance with Gemini API and Ollama usage terms.

## 🤝 Contributing

When contributing:
1. Run tests before submitting: `python test_agent.py`
2. Ensure no cross-stream recommendations
3. Maintain one-question-at-a-time rule
4. Update tests for new features

## 📖 Additional Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete guide for deploying to Streamlit Cloud with GitHub
- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide for local development

---

**⚠️ IMPORTANT DISCLAIMER**: This system provides indicative guidance only. Students must confirm their career decisions with certified human career counselors before making final choices.
